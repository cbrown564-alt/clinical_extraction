"""CandidateSet hybrid (assessment + projection) single-item runner."""

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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_candidate_set_clinical_assessment_probe as assessment_probe,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.stages import (
    clinical_assessment_projection_render as projection_render,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.lm import configure_lm


def run_item(item: GanRecord, config: PipelineConfiguration) -> PipelineResult[FinalExtraction]:
    """Run one record through the CandidateSet hybrid architecture."""
    _raw_candidates, candidate_set, _candidate_events = canonical_stages.extract_stage(
        item.note_text,
        source_row_index=item.source_row_index or 1,
        ablation_config=config.ablation_config,
        use_state_graph=config.use_state_graph_extract,
    )

    configure_lm(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        dspy_cache=config.dspy_cache,
    )

    inputs = assessment_probe.build_assessment_inputs(item, candidate_set)
    program = assessment_probe.DspyCandidateSetClinicalAssessment()
    prediction = program(
        note_text=inputs["note_text"],
        source_row_index=inputs["source_row_index"],
        task_instructions=inputs["task_instructions"],
        policy_examples=inputs["policy_examples"],
        candidate_set=inputs["candidate_set"],
        output_contract=inputs["output_contract"],
    )

    draft = prediction.assessment_draft

    disabled_switches = {
        group.value
        for group in RuleGroup
        if group not in config.ablation_config.enabled_groups
    } | set(config.ablation_config.disabled_rule_ids)

    clinical_assessment, errors = assessment_probe.assemble_clinical_assessment(
        draft,
        candidate_set=candidate_set,
        disabled_ablation_switches=disabled_switches,
    )

    if clinical_assessment is None:
        raise ValueError(f"ClinicalAssessment assembly failed: {errors}")

    proj_decision, final_rendered_label = projection_render.project_and_render(
        clinical_assessment,
        candidate_set=candidate_set,
        disabled_ablation_switches=disabled_switches,
    )
    final_value = final_rendered_label.rendered_label or "unknown"
    rationale = clinical_assessment.assessment_summary or ""
    evidence = final_rendered_label.evidence or ""

    output = FinalExtraction(
        final_value=final_value,
        rationale=rationale,
        evidence=evidence,
    )

    diagnostics = {
        "candidate_set": candidate_set.model_dump(),
        "assessment_draft": draft.model_dump() if draft else None,
        "clinical_assessment": (
            clinical_assessment.model_dump() if clinical_assessment else None
        ),
        "projection_decision": proj_decision.model_dump() if proj_decision else None,
        "final_rendered_label": (
            final_rendered_label.model_dump() if final_rendered_label else None
        ),
    }
    return PipelineResult(output=output, diagnostics=diagnostics)
