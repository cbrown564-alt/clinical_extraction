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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    RULES_ONLY_SELECT_RULE_IDS,
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


def run_letter(
    letter: ExectLetter,
    *,
    include_diagnosis_resolution_candidate: bool = False,
    include_diagnosis_benchmark_residuals: bool = False,
) -> RulesRecordResult:
    """Run all nine extractors once and materialize the separate four-family view."""

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
