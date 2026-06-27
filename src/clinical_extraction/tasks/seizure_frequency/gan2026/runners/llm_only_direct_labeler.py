"""LLM-only direct labeler single-item runner."""

from __future__ import annotations

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.lm import configure_lm


def run_item(item: GanRecord, config: PipelineConfiguration) -> PipelineResult[FinalExtraction]:
    """Run one record through the LLM-only direct labeler architecture."""
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        llm_only_direct_labeler,
    )

    configure_lm(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        dspy_cache=config.dspy_cache,
    )

    prompt_input_json = llm_only_direct_labeler.build_prompt_input(item)
    program = llm_only_direct_labeler.DspyLlmOnlyDirectLabelerExtractor()
    prediction = program(prompt_input_json=prompt_input_json)
    raw_output = str(prediction.decision_json)

    decision, parse_errors = llm_only_direct_labeler.parse_decision_json(raw_output)

    output = FinalExtraction(
        final_value=decision.final_label if decision else "unknown",
        rationale=decision.rationale if decision else "extraction failed",
        evidence=decision.evidence if decision else "",
    )
    diagnostics = {
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "parse_errors": parse_errors,
        "decision_record": decision.model_dump() if decision else None,
    }
    return PipelineResult(output=output, diagnostics=diagnostics)
