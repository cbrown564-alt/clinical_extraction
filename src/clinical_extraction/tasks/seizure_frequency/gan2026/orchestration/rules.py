"""Canonical Gan 2026 deterministic rules-only record orchestrator."""

from __future__ import annotations

from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026 import (
    deterministic_canonical_stages as canonical_stages,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.contracts import (
    GanRecordResult,
    GanStageEvent,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def run_record(item: GanRecord, config: PipelineConfiguration) -> GanRecordResult:
    """Run one Gan record through the selected deterministic stage order."""

    raw_candidates, candidate_set, candidate_events = canonical_stages.extract_stage(
        item.note_text,
        source_row_index=item.source_row_index or 1,
        ablation_config=config.ablation_config,
    )
    normalized_events = canonical_stages.normalize_stage(
        candidate_events,
        raw_candidates,
        ablation_config=config.ablation_config,
    )
    final_selection = canonical_stages.select_and_render_stage(
        candidate_events,
        normalized_events,
        ablation_config=config.ablation_config,
    )
    selected_index = int(final_selection.selected_event_ids[0].split("_")[1]) - 1
    output = FinalExtraction(
        final_value=final_selection.final_label,
        rationale=final_selection.rationale,
        evidence=final_selection.evidence,
    )

    disabled_switches = {
        group.value for group in RuleGroup if group not in config.ablation_config.enabled_groups
    } | set(config.ablation_config.disabled_rule_ids)
    evidence_valid, clinical_assessment = canonical_stages.evidence_trace_check_stage(
        item.note_text,
        final_selection=final_selection,
        candidate_set=candidate_set,
        selected_index=selected_index,
        disabled_ablation_switches=disabled_switches,
    )

    diagnostics = {
        "candidate_events": [event.model_dump(mode="json") for event in candidate_events],
        "normalized_events": [event.model_dump(mode="json") for event in normalized_events],
        "final_selection": final_selection.model_dump(mode="json"),
        "evidence_valid": evidence_valid,
        "clinical_assessment": (
            clinical_assessment.model_dump() if clinical_assessment else None
        ),
    }
    stage_events = (
        GanStageEvent(
            stage_id="gan.rules.extract",
            owner="deterministic",
            effect_class="clinical_meaning",
            input_value=item.note_text,
            output_value=[event.model_dump(mode="json") for event in candidate_events],
            changed=True,
            action="extract_candidates",
            rule_category="seizure_frequency",
        ),
        GanStageEvent(
            stage_id="gan.rules.normalize",
            owner="deterministic",
            effect_class="representation",
            input_value=[event.model_dump(mode="json") for event in candidate_events],
            output_value=[event.model_dump(mode="json") for event in normalized_events],
            changed=[event.model_dump(mode="json") for event in candidate_events]
            != [event.model_dump(mode="json") for event in normalized_events],
            action="normalize_candidates",
            rule_category="seizure_frequency",
        ),
        GanStageEvent(
            stage_id="gan.rules.select_and_render",
            owner="deterministic",
            effect_class="clinical_meaning",
            input_value=[event.model_dump(mode="json") for event in normalized_events],
            output_value=final_selection.model_dump(mode="json"),
            changed=True,
            action="select_current_event_and_render_label",
            rule_category="gan2026_specific",
        ),
        GanStageEvent(
            stage_id="gan.rules.evidence_trace_check",
            owner="deterministic",
            effect_class="validation_gate",
            input_value=final_selection.model_dump(mode="json"),
            output_value={"evidence_valid": evidence_valid},
            changed=not evidence_valid,
            action="validate_selected_evidence",
            rule_category="general",
        ),
        GanStageEvent(
            stage_id="gan.rules.score",
            owner="scorer",
            effect_class="benchmark_projection",
            input_value=output.model_dump(),
            output_value={},
            changed=False,
            action="defer_gold_comparison_to_scorer",
        ),
    )
    first_owner = next(
        (
            event.owner
            for event in stage_events
            if event.changed and event.effect_class == "clinical_meaning"
        ),
        None,
    )
    return GanRecordResult(
        output=output,
        diagnostics=diagnostics,
        stage_events=stage_events,
        deterministic_output=final_selection,
        first_prediction_changing_owner=first_owner,
        scorer_projection={"final_label": output.final_value, "evidence_valid": evidence_valid},
    )
