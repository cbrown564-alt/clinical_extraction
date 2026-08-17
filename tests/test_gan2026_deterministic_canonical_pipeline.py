"""Stage-contract guard for the retained deterministic Gan pipeline."""

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runner import (
    Gan2026PipelineRunner,
    PipelineConfiguration,
)

_SAMPLE_SOURCE_ROW_INDICES = {11118, 12383, 5555, 13485, 11434}

pytestmark = pytest.mark.local_corpus


def test_deterministic_canonical_pipeline_exposes_the_retained_stage_diagnostics() -> None:
    records = [
        record
        for record in load_records_with_monthly_frequency()
        if record.source_row_index in _SAMPLE_SOURCE_ROW_INDICES
    ]
    assert len(records) == len(_SAMPLE_SOURCE_ROW_INDICES)

    canonical_runner = Gan2026PipelineRunner(
        PipelineConfiguration(architecture="deterministic_canonical_pipeline")
    )

    for record in records:
        staged = canonical_runner.run(record)

        assert staged.output.final_value
        assert staged.diagnostics.keys() == {
            "candidate_events",
            "normalized_events",
            "final_selection",
            "evidence_valid",
            "clinical_assessment",
        }
