"""Typed recall-first recognise ledger for rules-only reconstruction."""

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
    nested_ancestor_diagnosis_candidates,
    nondiagnostic_context_diagnosis_candidates,
)
from .all_entities.orchestrator import extract_deterministic_all9
from .pipeline import deferred_sf_candidates

DIRECT = "direct"
DIAGNOSIS_NESTED_ANCESTOR = "diagnosis_nested_ancestor"
DIAGNOSIS_NONDIAGNOSTIC_CONTEXT = "diagnosis_nondiagnostic_context"
SF_NAMED_TYPE = "sf_named_type"
SF_HEADING_STATE = "sf_heading_state"
SF_SEIZURE_FREE = "sf_seizure_free"

DEFERRED_CANDIDATE_CLASSES: tuple[str, ...] = (
    DIAGNOSIS_NESTED_ANCESTOR,
    DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
    SF_NAMED_TYPE,
    SF_HEADING_STATE,
    SF_SEIZURE_FREE,
)

_SF_DEFERRED_CLASSES: frozenset[str] = frozenset(
    {SF_NAMED_TYPE, SF_HEADING_STATE, SF_SEIZURE_FREE}
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
class RecogniseConfig:
    diagnosis_service_context_exclusion: bool = False
    diagnosis_secondary_to_retention: bool = False
    diagnosis_focal_onset_alias: bool = False


@dataclass(frozen=True)
class RecogniseCandidate:
    mention: PredictedMention
    candidate_class: str
    rule_id: str


@dataclass(frozen=True)
class RecogniseLedger:
    letter_id: str
    candidates: tuple[RecogniseCandidate, ...]
    diagnostics: Mapping[str, Any]

    def direct_mentions(self) -> tuple[PredictedMention, ...]:
        return tuple(
            candidate.mention
            for candidate in self.candidates
            if candidate.candidate_class == DIRECT
        )

    def deferred_candidates(self) -> tuple[RecogniseCandidate, ...]:
        return tuple(
            candidate
            for candidate in self.candidates
            if candidate.candidate_class in DEFERRED_CANDIDATE_CLASSES
        )


def build_recognise_ledger(
    letter: ExectLetter,
    *,
    enabled_deferred_classes: frozenset[str] = frozenset(),
    recognise: RecogniseConfig | None = None,
) -> tuple[RecogniseLedger, PredictedLetter]:
    resolved_recognise = recognise or RecogniseConfig()
    prediction = extract_deterministic_all9(
        letter,
        diagnosis_service_context_exclusion=resolved_recognise.diagnosis_service_context_exclusion,
        diagnosis_secondary_to_retention=resolved_recognise.diagnosis_secondary_to_retention,
        diagnosis_focal_onset_alias=resolved_recognise.diagnosis_focal_onset_alias,
    )
    candidates: list[RecogniseCandidate] = [
        RecogniseCandidate(
            mention=mention,
            candidate_class=DIRECT,
            rule_id="recognise.deterministic_all9",
        )
        for mention in prediction.mentions
    ]
    per_class_counts: dict[str, int] = {DIRECT: len(candidates)}

    if DIAGNOSIS_NESTED_ANCESTOR in enabled_deferred_classes:
        nested = nested_ancestor_diagnosis_candidates(letter.note_text)
        candidates.extend(nested)
        per_class_counts[DIAGNOSIS_NESTED_ANCESTOR] = len(nested)

    if DIAGNOSIS_NONDIAGNOSTIC_CONTEXT in enabled_deferred_classes:
        nondiagnostic = nondiagnostic_context_diagnosis_candidates(letter.note_text)
        candidates.extend(nondiagnostic)
        per_class_counts[DIAGNOSIS_NONDIAGNOSTIC_CONTEXT] = len(nondiagnostic)

    enabled_sf_classes = enabled_deferred_classes & _SF_DEFERRED_CLASSES
    if enabled_sf_classes:
        sf_deferred = deferred_sf_candidates(letter, enabled_sf_classes)
        candidates.extend(sf_deferred)
        for sf_class in enabled_sf_classes:
            per_class_counts[sf_class] = sum(
                1 for candidate in sf_deferred if candidate.candidate_class == sf_class
            )

    ledger = RecogniseLedger(
        letter_id=letter.letter_id,
        candidates=tuple(candidates),
        diagnostics={"candidate_counts_by_class": dict(per_class_counts)},
    )
    return ledger, prediction
