from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_synthetic_hard_opportunity_panel,
    structured_synthetic_projection_generator,
)


def test_synthetic_projection_generator_emits_unknown_frequency_hard_row() -> None:
    panel_rows = structured_synthetic_hard_opportunity_panel.build_synthetic_panel_rows()
    hard_row = next(
        row
        for row in panel_rows
        if row["target_family"] == "unknown_frequency"
        and row["panel_role"] == "synthetic_hard"
    )

    result = structured_synthetic_projection_generator.build_projection_generator_row(
        hard_row
    )

    assert result["generator_action"] == "emit_candidate"
    assert result["candidate_label"] == "unknown"
    assert result["candidate_event_kind"] == "unknown_frequency"
    assert result["clinical_event_owner"] == "typed_boundary_classifier"
    assert result["projection_owner"] == "boundary_projection_policy"
    assert result["projection_ownership_explicit"] is True
    assert result["source_note_text_present"] is False
    assert result["exact_evidence"] is True


def test_synthetic_projection_generator_suppresses_matched_control() -> None:
    panel_rows = structured_synthetic_hard_opportunity_panel.build_synthetic_panel_rows()
    control_row = next(
        row
        for row in panel_rows
        if row["target_family"] == "daily_frequency"
        and row["panel_role"] == "synthetic_control"
    )

    result = structured_synthetic_projection_generator.build_projection_generator_row(
        control_row
    )

    assert result["generator_action"] == "suppress_candidate"
    assert result["candidate_label"] is None
    assert result["unsafe_candidate_label"] == "1 per day"
    assert result["projection_owner"] == "rate_projection_policy"
    assert result["projection_ownership_explicit"] is True
    assert result["expected_action_matched"] is True


def test_synthetic_projection_generator_summary_passes_smoke() -> None:
    panel_rows = structured_synthetic_hard_opportunity_panel.build_synthetic_panel_rows()
    rows = structured_synthetic_projection_generator.build_projection_generator_rows(
        panel_rows
    )
    summary = structured_synthetic_projection_generator.summarize_projection_generator_rows(
        rows
    )

    assert summary["row_count"] == 240
    assert summary["hard_emit_rows"] == 120
    assert summary["control_suppressed_rows"] == 120
    assert summary["exact_evidence_rows"] == 240
    assert summary["projection_ownership_explicit_rows"] == 240
    assert summary["source_note_text_rows"] == 0
    assert summary["synthetic_smoke_passed"] is True
    assert summary["decision"] == "synthetic_projection_generator_smoke_passed"
