"""Focused tests for the optional state-graph extract seam (Wave 3 / C1)."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026 import (
    deterministic_canonical_stages as canonical_stages,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanRecord,
    load_records_with_monthly_frequency,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runner import (
    Gan2026PipelineRunner,
    PipelineConfiguration,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    build_state_graph,
    extract_stage as state_graph_extract_stage,
    project_graph_to_gan,
)

_SAMPLE_SOURCE_ROW_INDICES = {11118, 12383, 5555}


def test_extract_stage_default_matches_pipeline_v1_extraction() -> None:
    note = (
        "Clinic Date: 10 January 2024. "
        "Current frequency: two focal seizures per week."
    )
    baseline = canonical_stages.extract_stage(
        note,
        source_row_index=7,
        use_state_graph=False,
    )
    implicit_default = canonical_stages.extract_stage(
        note,
        source_row_index=7,
    )

    assert implicit_default == baseline
    assert all(
        candidate.source_type == "deterministic_candidate"
        for candidate in baseline[1].candidates
    )


def test_extract_stage_state_graph_materializes_state_graph_node_candidates() -> None:
    note = (
        "She has no tonic-clonic seizures for one year, "
        "but still has three focal impaired-awareness seizures per month."
    )

    raw_candidates, candidate_set, candidate_events = canonical_stages.extract_stage(
        note,
        source_row_index=42,
        use_state_graph=True,
    )

    assert len(raw_candidates) >= 2
    assert len(candidate_set.candidates) == len(raw_candidates)
    assert len(candidate_events) == len(raw_candidates)
    assert candidate_set.component_owner == "state_graph_extraction"
    assert all(
        candidate.source_type == "state_graph_node"
        for candidate in candidate_set.candidates
    )
    assert all(candidate.candidate_id.startswith("sg:42:") for candidate in candidate_set.candidates)
    frequency_candidates = [
        candidate for candidate in candidate_set.candidates if candidate.candidate_kind == "frequency_rate"
    ]
    assert frequency_candidates
    assert frequency_candidates[0].evidence_span.text == (
        "three focal impaired-awareness seizures per month"
    )


def test_state_graph_extract_stage_aligns_with_graph_projection() -> None:
    note = "Current frequency: two focal seizures per week."
    graph = build_state_graph(note, source_row_index=3)
    projection = project_graph_to_gan(graph)

    _, candidate_set, _ = state_graph_extract_stage(note, source_row_index=3)

    projected_labels = {
        candidate.frequency.source_phrase
        for candidate in candidate_set.candidates
        if candidate.candidate_kind == "frequency_rate" and candidate.frequency is not None
    }
    assert projection.evidence in projected_labels


def test_runner_default_unchanged_canonical_equivalence_on_sample_rows() -> None:
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


def test_runner_state_graph_extract_produces_distinct_candidate_set() -> None:
    note = (
        "She has no tonic-clonic seizures for one year, "
        "but still has three focal impaired-awareness seizures per month."
    )
    record = GanRecord(
        source_row_index=99,
        note_text=note,
        gold_label="3 per month",
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )

    default_runner = Gan2026PipelineRunner(
        PipelineConfiguration(architecture="deterministic_canonical_pipeline")
    )
    state_graph_runner = Gan2026PipelineRunner(
        PipelineConfiguration(
            architecture="deterministic_canonical_pipeline",
            use_state_graph_extract=True,
        )
    )

    default_result = default_runner.run(record)
    state_graph_result = state_graph_runner.run(record)

    default_events = default_result.diagnostics["candidate_events"]
    state_graph_events = state_graph_result.diagnostics["candidate_events"]
    assert len(state_graph_events) >= len(default_events)
