"""Canonical rules-only ExECTv2 letter orchestrator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    mention_to_dict,
)
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.find_ledger import (
    DIAGNOSIS_COMPONENT_TOKEN,
    DIAGNOSIS_EXPANSION_SURFACE,
    DIAGNOSIS_HEADING_DECOMPOSITION,
    DIAGNOSIS_HIERARCHY_ANCESTOR,
    DIAGNOSIS_NESTED_SURFACE,
    DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
    DIAGNOSIS_UNRESTRICTED_SURFACE,
    DIRECT,
    INV_RESULT_VARIANT,
    RECALL_FIRST_CLASS_TAG,
    RX_RECALL_EXPANSION,
    SF_HEADING_STATE,
    SF_NAMED_TYPE,
    SF_SEIZURE_FREE,
    SF_STATE_VARIANT,
    FindCandidate,
    FindConfig,
    FindLedger,
    build_find_ledger,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    INVENTORY_WEAK_EPISODE_DROP,
    INVESTIGATION_RESULTLESS_DROP,
    KEEP_DX_HEADING_DECOMPOSITION,
    KEEP_INV_RESULT_VARIANT,
    KEEP_RX_RECALL_EXPANSION,
    KEEP_SF_STATE_VARIANT,
    RECALL_FIRST_UNSUPPORTED_DROP,
    RULES_ONLY_SELECT_RULE_IDS,
    SF_RATELESS_ANCHOR_DROP,
    SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
    apply_select_rules,
    flatten_family_select_plan,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured as structured,
)

from ..deterministic.all_entities.orchestrator import extract_deterministic_all9
from .contracts import ExectStageEvent

PRIMARY_COMPARISON_ENTITIES: tuple[str, ...] = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)


# Named encoders available to per-family encode sequences. Each encoder is a
# same-fact normalizer; it must never add or remove facts.
ENCODE_FORMAT_STACK = "encode.format_stack"


@dataclass(frozen=True)
class ThreeStageConfig:
    deferred_classes: frozenset[str] = frozenset()
    encode_families: frozenset[str] = frozenset({DIAGNOSIS.name})
    select_rule_ids: tuple[str, ...] = RULES_ONLY_SELECT_RULE_IDS
    find: FindConfig | None = None
    # Recall-first: classed producer candidates emitted as tagged direct
    # mentions. The Select gate (selection.recall_first_unsupported_drop)
    # owns their keep/drop decision.
    direct_classes: frozenset[str] = frozenset()
    # Per-family stage plans. When set, they take precedence over the flat
    # legacy fields above: family_encoders maps family -> ordered encoder
    # ids, family_select maps family (or cross_family) -> ordered Select
    # rule ids, validated and flattened by flatten_family_select_plan.
    # Tuples of pairs keep the frozen config hashable.
    family_encoders: tuple[tuple[str, tuple[str, ...]], ...] | None = None
    family_select: tuple[tuple[str, tuple[str, ...]], ...] | None = None

    def resolved_select_rule_ids(self) -> tuple[str, ...]:
        if self.family_select is not None:
            return flatten_family_select_plan(dict(self.family_select))
        return self.select_rule_ids

    def resolved_family_encoders(self) -> dict[str, tuple[str, ...]]:
        if self.family_encoders is not None:
            return dict(self.family_encoders)
        return {family: (ENCODE_FORMAT_STACK,) for family in self.encode_families}


# Frozen 2026-08-27 development candidate of the three-stage reconstruction
# protocol. Accepted on dev140 (inventory F1 0.8949 -> 0.9167, no
# comparator-exact regression). Any test60 replay requires its own
# predeclared aggregate-only protocol; do not change this configuration
# without a new development candidate.
ACCEPTED_THREE_STAGE_CONFIG = ThreeStageConfig(
    find=FindConfig(
        diagnosis_service_context_exclusion=True,
        diagnosis_secondary_to_retention=True,
        diagnosis_focal_onset_alias=True,
    ),
    select_rule_ids=(
        *RULES_ONLY_SELECT_RULE_IDS,
        SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
        INVENTORY_WEAK_EPISODE_DROP,
    ),
)

# Frozen 2026-08-27 recall-first restructure candidate (Phase C accepted).
# Find stage emits every recall-first candidate class as tagged direct
# mentions (dev140 find recall: Diagnosis 0.9666, SF 0.9212,
# Prescription 0.9854, Investigations 1.0). Select keeps only the four
# gated classes (heading decomposition, SF state variant, Rx recall
# expansion, Inv result variant; the last three conditional) and drops
# the rest. Accepted on dev140: select F1 0.9167 -> 0.9266, zero
# comparator-exact regressions, every keep isolated-positive and
# leave-one-out-negative. Do not change without a new development
# candidate under the recall-first restructure protocol.
RECALL_FIRST_THREE_STAGE_CONFIG = ThreeStageConfig(
    find=FindConfig(
        diagnosis_service_context_exclusion=True,
        diagnosis_secondary_to_retention=True,
        diagnosis_focal_onset_alias=True,
        sf_keep_unassociated_anchors=True,
        investigations_emit_resultless=True,
    ),
    select_rule_ids=(
        RECALL_FIRST_UNSUPPORTED_DROP,
        *RULES_ONLY_SELECT_RULE_IDS,
        SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
        INVENTORY_WEAK_EPISODE_DROP,
        SF_RATELESS_ANCHOR_DROP,
        INVESTIGATION_RESULTLESS_DROP,
        KEEP_DX_HEADING_DECOMPOSITION,
        KEEP_SF_STATE_VARIANT,
        KEEP_RX_RECALL_EXPANSION,
        KEEP_INV_RESULT_VARIANT,
    ),
    direct_classes=frozenset(
        {
            DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
            DIAGNOSIS_NESTED_SURFACE,
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
        }
    ),
)

# 2026-08-27 development candidate after Phase D: keep only the
# mechanisms whose aggregate-only family bands transferred (Rx recall
# expansion, SF state variant). Do not emit or keep heading
# decomposition or Investigations result variants. Frozen Phase C
# config above is unchanged. Not promoted; run_letter stays accepted.
TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG = ThreeStageConfig(
    find=FindConfig(
        diagnosis_service_context_exclusion=True,
        diagnosis_secondary_to_retention=True,
        diagnosis_focal_onset_alias=True,
    ),
    select_rule_ids=(
        RECALL_FIRST_UNSUPPORTED_DROP,
        *RULES_ONLY_SELECT_RULE_IDS,
        SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
        INVENTORY_WEAK_EPISODE_DROP,
        KEEP_SF_STATE_VARIANT,
        KEEP_RX_RECALL_EXPANSION,
    ),
    direct_classes=frozenset({RX_RECALL_EXPANSION, SF_STATE_VARIANT}),
)


@dataclass(frozen=True)
class RulesRecordResult:
    """All-nine deterministic prediction and its explicit four-family view."""

    prediction: PredictedLetter
    comparison_projection: PredictedLetter
    stage_events: tuple[ExectStageEvent, ...]

    @property
    def output(self) -> PredictedLetter:
        return self.prediction


def _mention_from_row(row: Mapping[str, Any]) -> PredictedMention:
    attributes = row.get("attributes") or {}
    if not isinstance(attributes, Mapping):
        attributes = {}
    return PredictedMention(
        entity=str(row.get("entity") or ""),
        text=str(row.get("text") or ""),
        attributes={str(key): str(value) for key, value in attributes.items()},
        evidence=str(row.get("evidence") or ""),
        component_owner=str(row.get("component_owner") or ""),
    )


def _candidate_to_source_row(candidate: FindCandidate) -> dict[str, Any]:
    row = dict(mention_to_dict(candidate.mention))
    row["candidate_class"] = candidate.candidate_class
    row["find_rule_id"] = candidate.rule_id
    return row


def _apply_format_stack_encoder(
    mentions: tuple[PredictedMention, ...],
    letter: ExectLetter,
) -> tuple[PredictedMention, ...]:
    encoded, _warnings = structured.apply_format_stack(
        mentions,
        letter.note_text,
        letter_id=letter.letter_id,
    )
    return tuple(encoded)


_ENCODER_REGISTRY: dict[str, Any] = {
    ENCODE_FORMAT_STACK: _apply_format_stack_encoder,
}


def _encode_four_family_direct_mentions(
    direct_four_family: tuple[PredictedMention, ...],
    letter: ExectLetter,
    family_encoders: Mapping[str, tuple[str, ...]],
) -> tuple[PredictedMention, ...]:
    def _bypasses_encode(mention: PredictedMention) -> bool:
        # Recall-first tagged candidates pass encode unchanged; their
        # keep/drop (and any encoding) is owned by Select-stage rules.
        if RECALL_FIRST_CLASS_TAG in mention.component_owner:
            return True
        encoder_ids = family_encoders.get(mention.entity) or ()
        return not encoder_ids

    unchanged = tuple(
        mention for mention in direct_four_family if _bypasses_encode(mention)
    )
    encoded_parts: list[PredictedMention] = []
    for entity in PRIMARY_COMPARISON_ENTITIES:
        encoder_ids = family_encoders.get(entity) or ()
        if not encoder_ids:
            continue
        family_mentions = tuple(
            mention
            for mention in direct_four_family
            if mention.entity == entity and not _bypasses_encode(mention)
        )
        if not family_mentions:
            continue
        for encoder_id in encoder_ids:
            encoder = _ENCODER_REGISTRY.get(encoder_id)
            if encoder is None:
                raise ValueError(f"unknown encoder id: {encoder_id!r}")
            family_mentions = encoder(family_mentions, letter)
        encoded_parts.extend(family_mentions)
    return (*unchanged, *encoded_parts)


def _four_family_source_rows(ledger: FindLedger) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in ledger.candidates:
        if (
            candidate.candidate_class == DIRECT
            and candidate.mention.entity in PRIMARY_COMPARISON_ENTITIES
        ):
            rows.append(_candidate_to_source_row(candidate))
    for candidate in ledger.deferred_candidates():
        rows.append(_candidate_to_source_row(candidate))
    return rows


def apply_rules_only_later_stages(
    letter: ExectLetter,
    prediction: PredictedLetter,
) -> PredictedLetter:
    """Encode then inventory-Select the four comparison families."""

    four = tuple(
        mention
        for mention in prediction.mentions
        if mention.entity in PRIMARY_COMPARISON_ENTITIES
    )
    other = tuple(
        mention
        for mention in prediction.mentions
        if mention.entity not in PRIMARY_COMPARISON_ENTITIES
    )
    diagnosis = tuple(mention for mention in four if mention.entity == DIAGNOSIS.name)
    unchanged = tuple(mention for mention in four if mention.entity != DIAGNOSIS.name)
    encoded_diagnosis, _warnings = structured.apply_format_stack(
        diagnosis,
        letter.note_text,
        letter_id=letter.letter_id,
    )
    encoded = (*unchanged, *encoded_diagnosis)
    source_rows = [mention_to_dict(mention) for mention in four]
    encoded_rows = [mention_to_dict(mention) for mention in encoded]
    selected, actions = apply_select_rules(
        encoded_rows,
        source_mentions=source_rows,
        note_text=letter.note_text,
        enabled_rule_ids=set(RULES_ONLY_SELECT_RULE_IDS),
    )
    selected_mentions = tuple(_mention_from_row(row) for row in selected)
    return prediction.model_copy(
        update={
            "mentions": (*other, *selected_mentions),
            "diagnostics": {
                **dict(prediction.diagnostics),
                "rules_only_later_stages": "encode_then_inventory_select",
                "select_action_count": len(actions),
            },
        }
    )


def project_primary_comparison(prediction: PredictedLetter) -> PredictedLetter:
    """Project all-nine extraction for the decision-0046 primary comparison."""

    return prediction.model_copy(
        update={
            "mentions": tuple(
                mention
                for mention in prediction.mentions
                if mention.entity in PRIMARY_COMPARISON_ENTITIES
            ),
            "diagnostics": {
                **dict(prediction.diagnostics),
                "comparison_projection": "clinical_headline",
                "comparison_entities": PRIMARY_COMPARISON_ENTITIES,
            },
        }
    )


def run_letter_retune_stack(
    letter: ExectLetter,
    *,
    include_diagnosis_resolution_candidate: bool = False,
    include_diagnosis_benchmark_residuals: bool = False,
) -> RulesRecordResult:
    """Pre-three-stage retune stack; development comparator only."""

    prediction = extract_deterministic_all9(
        letter,
        include_diagnosis_resolution_candidate=include_diagnosis_resolution_candidate,
        include_diagnosis_benchmark_residuals=include_diagnosis_benchmark_residuals,
    )
    prediction = apply_rules_only_later_stages(letter, prediction)
    comparison = project_primary_comparison(prediction)
    stage_events = build_stage_events(letter, prediction, comparison)
    return RulesRecordResult(
        prediction=prediction,
        comparison_projection=comparison,
        stage_events=stage_events,
    )


def run_letter(
    letter: ExectLetter,
    *,
    include_diagnosis_resolution_candidate: bool = False,
    include_diagnosis_benchmark_residuals: bool = False,
) -> RulesRecordResult:
    """Run the promoted rules-only three-stage program on one letter."""

    del include_diagnosis_resolution_candidate, include_diagnosis_benchmark_residuals
    return run_letter_three_stage(letter, ACCEPTED_THREE_STAGE_CONFIG)


@dataclass(frozen=True)
class ThreeStagePass:
    """One three-stage run with the four-family mentions at each stop."""

    ledger: FindLedger
    all9_prediction: PredictedLetter
    find_mentions: tuple[PredictedMention, ...]
    encode_mentions: tuple[PredictedMention, ...]
    select_mentions: tuple[PredictedMention, ...]
    select_action_count: int


@dataclass(frozen=True)
class ThreeStageStops:
    """Four-family mentions at the find, encode, and select stops."""

    find: tuple[PredictedMention, ...]
    encode: tuple[PredictedMention, ...]
    select: tuple[PredictedMention, ...]


def _run_three_stage_pass(
    letter: ExectLetter,
    config: ThreeStageConfig,
) -> ThreeStagePass:
    ledger, all9_prediction = build_find_ledger(
        letter,
        enabled_deferred_classes=config.deferred_classes,
        find=config.find,
        direct_classes=config.direct_classes,
    )
    direct_four_family = tuple(
        candidate.mention
        for candidate in ledger.candidates
        if (
            candidate.candidate_class == DIRECT
            or candidate.candidate_class in config.direct_classes
        )
        and candidate.mention.entity in PRIMARY_COMPARISON_ENTITIES
    )
    encoded_four_family = _encode_four_family_direct_mentions(
        direct_four_family,
        letter,
        config.resolved_family_encoders(),
    )
    source_rows = _four_family_source_rows(ledger)
    encoded_rows = [mention_to_dict(mention) for mention in encoded_four_family]
    selected, actions = apply_select_rules(
        encoded_rows,
        source_mentions=source_rows,
        note_text=letter.note_text,
        enabled_rule_ids=set(config.resolved_select_rule_ids()),
    )
    return ThreeStagePass(
        ledger=ledger,
        all9_prediction=all9_prediction,
        find_mentions=direct_four_family,
        encode_mentions=encoded_four_family,
        select_mentions=tuple(_mention_from_row(row) for row in selected),
        select_action_count=len(actions),
    )


def three_stage_stop_mentions(
    letter: ExectLetter,
    config: ThreeStageConfig | None = None,
) -> ThreeStageStops:
    """Read the four-family mentions at each stop of one three-stage run."""

    stage_pass = _run_three_stage_pass(letter, config or ThreeStageConfig())
    return ThreeStageStops(
        find=stage_pass.find_mentions,
        encode=stage_pass.encode_mentions,
        select=stage_pass.select_mentions,
    )


def run_letter_three_stage(
    letter: ExectLetter,
    config: ThreeStageConfig | None = None,
) -> RulesRecordResult:
    """Run find, encode, and select stages for rules-only reconstruction."""

    resolved_config = config or ThreeStageConfig()
    stage_pass = _run_three_stage_pass(letter, resolved_config)
    ledger = stage_pass.ledger
    all9_prediction = stage_pass.all9_prediction
    selected_mentions = stage_pass.select_mentions
    other = tuple(
        mention
        for mention in all9_prediction.mentions
        if mention.entity not in PRIMARY_COMPARISON_ENTITIES
    )
    prediction = all9_prediction.model_copy(
        update={
            "mentions": (*other, *selected_mentions),
            "diagnostics": {
                **dict(all9_prediction.diagnostics),
                "rules_only_program": "three_stage_reconstruction",
                "deferred_classes": sorted(resolved_config.deferred_classes),
                "encode_families": sorted(
                    family
                    for family, encoders in resolved_config.resolved_family_encoders().items()
                    if encoders
                ),
                "select_rule_ids": list(resolved_config.resolved_select_rule_ids()),
                "ledger_candidate_counts_by_class": dict(
                    ledger.diagnostics.get("candidate_counts_by_class", {})
                ),
                "select_action_count": stage_pass.select_action_count,
            },
        }
    )
    comparison = project_primary_comparison(prediction)
    stage_events = build_stage_events(letter, prediction, comparison)
    return RulesRecordResult(
        prediction=prediction,
        comparison_projection=comparison,
        stage_events=stage_events,
    )


def build_stage_events(
    letter: ExectLetter,
    prediction: PredictedLetter,
    comparison: PredictedLetter | None = None,
) -> tuple[ExectStageEvent, ...]:
    """Build the stable rules trace for a completed prediction."""

    comparison = comparison or project_primary_comparison(prediction)
    counts = dict(prediction.diagnostics.get("entity_counts", {}))
    return (
        ExectStageEvent(
            stage_id="exect.rules.extract_seizure_frequency",
            owner="deterministic",
            effect_class="clinical_meaning",
            input_value=letter.note_text,
            output_value=counts.get(SEIZURE_FREQUENCY.name, 0),
            changed=True,
            action="extract_seizure_frequency",
            rule_category="seizure_frequency",
        ),
        ExectStageEvent(
            stage_id="exect.rules.extract_entities",
            owner="deterministic",
            effect_class="clinical_meaning",
            input_value=letter.note_text,
            output_value=counts,
            changed=True,
            action="extract_all_nine_entities",
            rule_category="clinical_epilepsy",
        ),
        ExectStageEvent(
            stage_id="exect.rules.dedupe",
            owner="deterministic",
            effect_class="representation",
            input_value=sum(counts.values()),
            output_value=len(prediction.mentions),
            changed=sum(counts.values()) != len(prediction.mentions),
            action="deduplicate_mentions_in_stable_order",
            rule_category="general",
        ),
        ExectStageEvent(
            stage_id="exect.rules.score",
            owner="scorer",
            effect_class="benchmark_projection",
            input_value=len(prediction.mentions),
            output_value={
                "all_entities": len(prediction.mentions),
                "primary_comparison": len(comparison.mentions),
            },
            changed=False,
            action="defer_gold_comparison_to_scorer",
        ),
    )


def run_all9_on_letters(
    letters: Sequence[ExectLetter],
    *,
    include_diagnosis_resolution_candidate: bool = False,
    include_diagnosis_benchmark_residuals: bool = False,
) -> list[PredictedLetter]:
    """Compatibility batch adapter for the all-nine deterministic output."""

    return [
        run_letter(
            letter,
            include_diagnosis_resolution_candidate=include_diagnosis_resolution_candidate,
            include_diagnosis_benchmark_residuals=include_diagnosis_benchmark_residuals,
        ).prediction
        for letter in letters
    ]
