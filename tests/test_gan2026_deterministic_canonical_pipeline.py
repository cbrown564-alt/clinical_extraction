"""Equivalence guard for the `deterministic_canonical_pipeline` staging pass.

[[0013-stage-deterministic-canonical-config-before-generalizing-its-rules]]
requires the staging restructure (named Extract/Normalize/Select & Render/
Evidence Trace Check stages — see `deterministic_canonical_stages.py`) to
change no rules and no behavior. This test asserts that directly: the new
architecture must produce byte-identical `output`/`diagnostics` to the
existing `deterministic` architecture on the same records. Any future drift
here is a signal that a change leaked into the canonical branch unintentionally
(e.g. a Section 4 de-overfitting rewrite landing in the wrong place).
"""

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runner import (
    Gan2026PipelineRunner,
    PipelineConfiguration,
)

_SAMPLE_SOURCE_ROW_INDICES = {11118, 12383, 5555, 13485, 11434}


def test_deterministic_canonical_pipeline_matches_deterministic_output_and_diagnostics() -> None:
    records = [
        record
        for record in load_records_with_monthly_frequency()
        if record.source_row_index in _SAMPLE_SOURCE_ROW_INDICES
    ]
    assert len(records) == len(_SAMPLE_SOURCE_ROW_INDICES)

    deterministic_runner = Gan2026PipelineRunner(
        PipelineConfiguration(architecture="deterministic")
    )
    canonical_runner = Gan2026PipelineRunner(
        PipelineConfiguration(architecture="deterministic_canonical_pipeline")
    )

    for record in records:
        baseline = deterministic_runner.run(record)
        staged = canonical_runner.run(record)

        assert staged.output == baseline.output
        assert staged.diagnostics == baseline.diagnostics
        assert staged.diagnostics.keys() == {
            "candidate_events",
            "normalized_events",
            "final_selection",
            "evidence_valid",
            "clinical_assessment",
        }
