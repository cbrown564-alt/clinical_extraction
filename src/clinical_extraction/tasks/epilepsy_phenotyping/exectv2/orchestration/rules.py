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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.recognise_ledger import (
    DIRECT,
    RecogniseCandidate,
    RecogniseConfig,
    RecogniseLedger,
    build_recognise_ledger,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    INVENTORY_WEAK_EPISODE_DROP,
    RULES_ONLY_SELECT_RULE_IDS,
    SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
    apply_select_rules,
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


@dataclass(frozen=True)
class ThreeStageConfig:
    deferred_classes: frozenset[str] = frozenset()
    encode_families: frozenset[str] = frozenset({DIAGNOSIS.name})
    select_rule_ids: tuple[str, ...] = RULES_ONLY_SELECT_RULE_IDS
    recognise: RecogniseConfig | None = None


# Frozen 2026-08-27 development candidate of the three-stage reconstruction
# protocol. Accepted on dev140 (inventory F1 0.8949 -> 0.9167, no
# comparator-exact regression). Any test60 replay requires its own
# predeclared aggregate-only protocol; do not change this configuration
# without a new development candidate.
ACCEPTED_THREE_STAGE_CONFIG = ThreeStageConfig(
    recognise=RecogniseConfig(
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


def _candidate_to_source_row(candidate: RecogniseCandidate) -> dict[str, Any]:
    row = dict(mention_to_dict(candidate.mention))
    row["candidate_class"] = candidate.candidate_class
    row["recognise_rule_id"] = candidate.rule_id
    return row


def _encode_four_family_direct_mentions(
    direct_four_family: tuple[PredictedMention, ...],
    letter: ExectLetter,
    encode_families: frozenset[str],
) -> tuple[PredictedMention, ...]:
    unchanged = tuple(
        mention for mention in direct_four_family if mention.entity not in encode_families
    )
    encoded_parts: list[PredictedMention] = []
    for entity in PRIMARY_COMPARISON_ENTITIES:
        if entity not in encode_families:
            continue
        family_mentions = tuple(
            mention for mention in direct_four_family if mention.entity == entity
        )
        if not family_mentions:
            continue
        encoded, _warnings = structured.apply_format_stack(
            family_mentions,
            letter.note_text,
            letter_id=letter.letter_id,
        )
        encoded_parts.extend(encoded)
    return (*unchanged, *encoded_parts)


def _four_family_source_rows(ledger: RecogniseLedger) -> list[dict[str, Any]]:
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


def run_letter_three_stage(
    letter: ExectLetter,
    config: ThreeStageConfig | None = None,
) -> RulesRecordResult:
    """Run recognise, encode, and select stages for rules-only reconstruction."""

    resolved_config = config or ThreeStageConfig()

    ledger, all9_prediction = build_recognise_ledger(
        letter,
        enabled_deferred_classes=resolved_config.deferred_classes,
        recognise=resolved_config.recognise,
    )
    direct_four_family = tuple(
        candidate.mention
        for candidate in ledger.candidates
        if candidate.candidate_class == DIRECT
        and candidate.mention.entity in PRIMARY_COMPARISON_ENTITIES
    )
    encoded_four_family = _encode_four_family_direct_mentions(
        direct_four_family,
        letter,
        resolved_config.encode_families,
    )
    source_rows = _four_family_source_rows(ledger)
    encoded_rows = [mention_to_dict(mention) for mention in encoded_four_family]
    selected, actions = apply_select_rules(
        encoded_rows,
        source_mentions=source_rows,
        note_text=letter.note_text,
        enabled_rule_ids=set(resolved_config.select_rule_ids),
    )
    selected_mentions = tuple(_mention_from_row(row) for row in selected)
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
                "encode_families": sorted(resolved_config.encode_families),
                "select_rule_ids": list(resolved_config.select_rule_ids),
                "ledger_candidate_counts_by_class": dict(
                    ledger.diagnostics.get("candidate_counts_by_class", {})
                ),
                "select_action_count": len(actions),
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
