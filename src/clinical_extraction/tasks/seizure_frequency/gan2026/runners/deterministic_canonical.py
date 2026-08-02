"""Compatibility adapter for the canonical Gan rules orchestrator."""

from __future__ import annotations

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.rules import (
    run_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def run_item(item: GanRecord, config: PipelineConfiguration) -> PipelineResult[FinalExtraction]:
    """Preserve the historical public return shape while delegating stages."""

    return run_record(item, config).to_pipeline_result()
