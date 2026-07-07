"""Staged deterministic_canonical_pipeline single-item runner."""

from __future__ import annotations

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026 import (
    deterministic_canonical_stages as canonical_stages,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def run_item(item: GanRecord, config: PipelineConfiguration) -> PipelineResult[FinalExtraction]:
    """Run one record through the staged deterministic canonical pipeline."""
    raw_candidates, candidate_set, candidate_events = canonical_stages.extract_stage(
        item.note_text,
        source_row_index=item.source_row_index or 1,
        ablation_config=config.ablation_config,
        use_state_graph=config.use_state_graph_extract,
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
        "clinical_assessment": (clinical_assessment.model_dump() if clinical_assessment else None),
    }
    return PipelineResult(output=output, diagnostics=diagnostics)
