from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_seed_expansion_panel,
    structured_seed_projection_generator,
)


def test_projection_generator_adds_explicit_ownership_for_hard_rows() -> None:
    panel_rows = structured_seed_expansion_panel.build_seed_expansion_panel_rows()
    hard_row = next(row for row in panel_rows if row["seed_family"] == "cluster_completion")

    result = structured_seed_projection_generator.build_projection_generator_row(hard_row)

    assert result["generator_action"] == "emit_candidate"
    assert result["candidate_label"] == "1 cluster per month, 4 per cluster"
    assert result["clinical_event_owner"] == "typed_event_extractor"
    assert result["projection_owner"] == "cluster_projection_policy"
    assert result["projection_stage"] == "clinical_event_to_benchmark_label"
    assert result["projection_ownership_explicit"] is True
    assert result["source_note_text_present"] is False
    assert result["exact_evidence"] is True


def test_projection_generator_suppresses_control_without_losing_owner_schema() -> None:
    panel_rows = structured_seed_expansion_panel.build_seed_expansion_panel_rows()
    control_row = next(
        row
        for row in panel_rows
        if row["seed_family"] == "yearly_to_daily"
        and row["panel_role"] == "synthetic_control"
    )

    result = structured_seed_projection_generator.build_projection_generator_row(control_row)

    assert result["generator_action"] == "suppress_candidate"
    assert result["candidate_label"] is None
    assert result["clinical_event_owner"] == "typed_event_extractor"
    assert result["projection_owner"] == "rate_projection_policy"
    assert result["projection_ownership_explicit"] is True
    assert result["expected_action_matched"] is True


def test_projection_generator_summary_passes_synthetic_smoke() -> None:
    panel_rows = structured_seed_expansion_panel.build_seed_expansion_panel_rows()
    rows = structured_seed_projection_generator.build_projection_generator_rows(panel_rows)
    summary = structured_seed_projection_generator.summarize_projection_generator_rows(rows)

    assert summary["row_count"] == 180
    assert summary["hard_emit_rows"] == 90
    assert summary["control_suppressed_rows"] == 90
    assert summary["projection_ownership_explicit_rows"] == 180
    assert summary["source_note_text_rows"] == 0
    assert summary["synthetic_smoke_passed"] is True
    assert summary["decision"] == "promote_to_validation_projection_owner_panel"
