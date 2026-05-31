from __future__ import annotations

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanRecord


class Gan2026PipelineV1:
    """Initial hybrid deterministic-DSPy seizure-frequency pipeline."""

    def run(self, item: GanRecord) -> PipelineResult[FinalExtraction]:
        raise NotImplementedError("V1 pipeline implementation starts after scoring parity.")

