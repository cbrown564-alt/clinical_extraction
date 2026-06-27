"""Hybrid structured-events single-item runner."""

from __future__ import annotations

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.lm import configure_lm


def run_item(item: GanRecord, config: PipelineConfiguration) -> PipelineResult[FinalExtraction]:
    """Run one record through the hybrid structured-events architecture."""
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        hybrid_structured_events,
    )

    configure_lm(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        dspy_cache=config.dspy_cache,
    )

    prompt_input_json = hybrid_structured_events.build_prompt_input(item)
    program = hybrid_structured_events.DspyStructuredExtractor()
    prediction = program(prompt_input_json=prompt_input_json)
    raw_output = str(prediction.structured_json)

    extraction, normalized_events, parse_errors = hybrid_structured_events.parse_structured_json(
        raw_output,
        note_text=item.note_text,
        repair_config=hybrid_structured_events.StructuredRepairConfig(),
    )

    final_label = extraction.selection.final_label if extraction else "unknown"
    output = FinalExtraction(
        final_value=final_label,
        rationale=extraction.selection.rationale if extraction else "extraction failed",
        evidence=extraction.selection.evidence if extraction else "",
    )
    diagnostics = {
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "parse_errors": parse_errors,
        "structured_record": extraction.model_dump() if extraction else None,
        "normalized_events": [event.model_dump() for event in normalized_events],
    }
    return PipelineResult(output=output, diagnostics=diagnostics)
