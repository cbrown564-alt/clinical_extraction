"""Typed recall-first find ledger for rules-only reconstruction."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from .all_entities.diagnosis import (
    component_token_diagnosis_candidates,
    expansion_surface_diagnosis_candidates,
    heading_decomposition_diagnosis_candidates,
    hierarchy_ancestor_diagnosis_candidates,
    nested_ancestor_diagnosis_candidates,
    nested_surface_diagnosis_candidates,
    nondiagnostic_context_diagnosis_candidates,
    unrestricted_surface_diagnosis_candidates,
)
from .all_entities.investigations import result_variant_investigation_candidates
from .all_entities.orchestrator import extract_deterministic_all9
from .all_entities.prescription import recall_first_rx_candidates
from .pipeline import deferred_sf_candidates

DIRECT = "direct"
DIAGNOSIS_NESTED_ANCESTOR = "diagnosis_nested_ancestor"
DIAGNOSIS_NESTED_SURFACE = "diagnosis_nested_surface"
DIAGNOSIS_NONDIAGNOSTIC_CONTEXT = "diagnosis_nondiagnostic_context"
DIAGNOSIS_HEADING_DECOMPOSITION = "diagnosis_heading_decomposition"
DIAGNOSIS_UNRESTRICTED_SURFACE = "diagnosis_unrestricted_surface"
DIAGNOSIS_EXPANSION_SURFACE = "diagnosis_expansion_surface"
DIAGNOSIS_HIERARCHY_ANCESTOR = "diagnosis_hierarchy_ancestor"
DIAGNOSIS_COMPONENT_TOKEN = "diagnosis_component_token"
SF_NAMED_TYPE = "sf_named_type"
SF_HEADING_STATE = "sf_heading_state"
SF_SEIZURE_FREE = "sf_seizure_free"
SF_STATE_VARIANT = "sf_state_variant"
RX_RECALL_EXPANSION = "rx_recall_expansion"
INV_RESULT_VARIANT = "inv_result_variant"

DEFERRED_CANDIDATE_CLASSES: tuple[str, ...] = (
    DIAGNOSIS_NESTED_ANCESTOR,
    DIAGNOSIS_NESTED_SURFACE,
    DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
    DIAGNOSIS_HEADING_DECOMPOSITION,
    DIAGNOSIS_UNRESTRICTED_SURFACE,
    DIAGNOSIS_EXPANSION_SURFACE,
    DIAGNOSIS_HIERARCHY_ANCESTOR,
    DIAGNOSIS_COMPONENT_TOKEN,
    SF_NAMED_TYPE,
    SF_HEADING_STATE,
    SF_SEIZURE_FREE,
    SF_STATE_VARIANT,
    RX_RECALL_EXPANSION,
    INV_RESULT_VARIANT,
)

# Component-owner tag marking a mention emitted as a recall-first direct
# candidate from a classed producer. Select reads the tag to decide
# keep/drop; the class name follows the tag.
# Persisted replay fingerprints keep the historical recognise.* rule_id prefix.
RECALL_FIRST_CLASS_TAG = "+recognise_class:"


def recall_first_class_of(component_owner: str) -> str | None:
    """Return the recall-first candidate class tagged on a mention, if any."""

    _prefix, tag, suffix = component_owner.partition(RECALL_FIRST_CLASS_TAG)
    if not tag:
        return None
    return suffix.split("+", 1)[0]

_SF_DEFERRED_CLASSES: frozenset[str] = frozenset(
    {SF_NAMED_TYPE, SF_HEADING_STATE, SF_SEIZURE_FREE, SF_STATE_VARIANT}
)

PRIMARY_COMPARISON_ENTITIES: frozenset[str] = frozenset(
    {
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
        PRESCRIPTION.name,
        INVESTIGATIONS.name,
    }
)


@dataclass(frozen=True)
class FindConfig:
    diagnosis_service_context_exclusion: bool = False
    diagnosis_secondary_to_retention: bool = False
    diagnosis_focal_onset_alias: bool = False
    # Recall-first emission switches (2026-08-27 restructure). Each widens
    # the direct ledger; precision is recovered by a paired Select rule.
    sf_keep_unassociated_anchors: bool = False
    investigations_emit_resultless: bool = False


@dataclass(frozen=True)
class FindCandidate:
    mention: PredictedMention
    candidate_class: str
    rule_id: str


@dataclass(frozen=True)
class FindLedger:
    letter_id: str
    candidates: tuple[FindCandidate, ...]
    diagnostics: Mapping[str, Any]

    def direct_mentions(self) -> tuple[PredictedMention, ...]:
        return tuple(
            candidate.mention
            for candidate in self.candidates
            if candidate.candidate_class == DIRECT
        )

    def deferred_candidates(self) -> tuple[FindCandidate, ...]:
        return tuple(
            candidate
            for candidate in self.candidates
            if candidate.candidate_class in DEFERRED_CANDIDATE_CLASSES
        )


def _tag_direct(candidate: FindCandidate) -> FindCandidate:
    tagged_mention = candidate.mention.model_copy(
        update={
            "component_owner": (
                f"{candidate.mention.component_owner}"
                f"{RECALL_FIRST_CLASS_TAG}{candidate.candidate_class}"
            )
        }
    )
    return FindCandidate(
        mention=tagged_mention,
        candidate_class=candidate.candidate_class,
        rule_id=candidate.rule_id,
    )


def build_find_ledger(
    letter: ExectLetter,
    *,
    enabled_deferred_classes: frozenset[str] = frozenset(),
    find: FindConfig | None = None,
    direct_classes: frozenset[str] = frozenset(),
) -> tuple[FindLedger, PredictedLetter]:
    resolved_find = find or FindConfig()
    prediction = extract_deterministic_all9(
        letter,
        diagnosis_service_context_exclusion=resolved_find.diagnosis_service_context_exclusion,
        diagnosis_secondary_to_retention=resolved_find.diagnosis_secondary_to_retention,
        diagnosis_focal_onset_alias=resolved_find.diagnosis_focal_onset_alias,
        keep_unassociated_sf_anchors=resolved_find.sf_keep_unassociated_anchors,
        investigations_emit_resultless=resolved_find.investigations_emit_resultless,
    )
    candidates: list[FindCandidate] = [
        FindCandidate(
            mention=mention,
            candidate_class=DIRECT,
            rule_id="recognise.deterministic_all9",
        )
        for mention in prediction.mentions
    ]
    per_class_counts: dict[str, int] = {DIRECT: len(candidates)}
    producer_classes = enabled_deferred_classes | direct_classes

    def _add(produced: tuple[FindCandidate, ...], candidate_class: str) -> None:
        emitted = tuple(
            _tag_direct(candidate) if candidate_class in direct_classes else candidate
            for candidate in produced
        )
        candidates.extend(emitted)
        per_class_counts[candidate_class] = len(emitted)

    if DIAGNOSIS_NESTED_ANCESTOR in producer_classes:
        _add(
            nested_ancestor_diagnosis_candidates(letter.note_text),
            DIAGNOSIS_NESTED_ANCESTOR,
        )

    if DIAGNOSIS_NESTED_SURFACE in producer_classes:
        _add(
            nested_surface_diagnosis_candidates(letter.note_text),
            DIAGNOSIS_NESTED_SURFACE,
        )

    if DIAGNOSIS_HEADING_DECOMPOSITION in producer_classes:
        _add(
            heading_decomposition_diagnosis_candidates(letter.note_text),
            DIAGNOSIS_HEADING_DECOMPOSITION,
        )

    if DIAGNOSIS_NONDIAGNOSTIC_CONTEXT in producer_classes:
        _add(
            nondiagnostic_context_diagnosis_candidates(letter.note_text),
            DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
        )

    if DIAGNOSIS_UNRESTRICTED_SURFACE in producer_classes:
        _add(
            unrestricted_surface_diagnosis_candidates(letter.note_text),
            DIAGNOSIS_UNRESTRICTED_SURFACE,
        )

    if DIAGNOSIS_EXPANSION_SURFACE in producer_classes:
        _add(
            expansion_surface_diagnosis_candidates(letter.note_text),
            DIAGNOSIS_EXPANSION_SURFACE,
        )

    if DIAGNOSIS_HIERARCHY_ANCESTOR in producer_classes:
        _add(
            hierarchy_ancestor_diagnosis_candidates(letter.note_text),
            DIAGNOSIS_HIERARCHY_ANCESTOR,
        )

    if DIAGNOSIS_COMPONENT_TOKEN in producer_classes:
        _add(
            component_token_diagnosis_candidates(letter.note_text),
            DIAGNOSIS_COMPONENT_TOKEN,
        )

    if RX_RECALL_EXPANSION in producer_classes:
        _add(
            recall_first_rx_candidates(letter.note_text),
            RX_RECALL_EXPANSION,
        )

    if INV_RESULT_VARIANT in producer_classes:
        _add(
            result_variant_investigation_candidates(prediction.mentions),
            INV_RESULT_VARIANT,
        )

    enabled_sf_classes = producer_classes & _SF_DEFERRED_CLASSES
    if enabled_sf_classes:
        sf_deferred = deferred_sf_candidates(letter, enabled_sf_classes)
        for sf_class in enabled_sf_classes:
            _add(
                tuple(
                    candidate
                    for candidate in sf_deferred
                    if candidate.candidate_class == sf_class
                ),
                sf_class,
            )

    ledger = FindLedger(
        letter_id=letter.letter_id,
        candidates=tuple(candidates),
        diagnostics={"candidate_counts_by_class": dict(per_class_counts)},
    )
    return ledger, prediction
