"""Compatibility adapter for the canonical Gan LLM-only orchestrator."""

from __future__ import annotations

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.llm import (
    run_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def run_item(
    item: GanFrequencyRecord, config: PipelineConfiguration
) -> PipelineResult[FinalExtraction]:
    """Run one record through the canonical pipeline, retaining old return shape."""

    return run_record(item, config).to_pipeline_result()
