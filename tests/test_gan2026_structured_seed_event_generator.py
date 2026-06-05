from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_seed_event_generator,
    structured_seed_expansion_panel,
)


def test_seed_event_generator_emits_hard_case_candidates() -> None:
    rows = structured_seed_expansion_panel.build_seed_expansion_panel_rows()
    hard_row = next(row for row in rows if row["seed_family"] == "yearly_to_daily")

    result = structured_seed_event_generator.build_generator_row(hard_row)

    assert result["generator_action"] == "emit_candidate"
    assert result["candidate_label"] == "1 per day"
    assert result["candidate_event_kind"] == "frequency_rate"
    assert result["candidate_evidence"] == hard_row["expected_evidence_substring"]
    assert result["expected_action_matched"] is True
    assert result["exact_evidence"] is True


def test_seed_event_generator_suppresses_matched_controls() -> None:
    rows = structured_seed_expansion_panel.build_seed_expansion_panel_rows()
    control_row = next(
        row
        for row in rows
        if row["seed_family"] == "seizure_free_to_unknown"
        and row["panel_role"] == "synthetic_control"
    )

    result = structured_seed_event_generator.build_generator_row(control_row)

    assert result["generator_action"] == "suppress_candidate"
    assert result["candidate_label"] is None
    assert result["expected_action_matched"] is True
    assert result["exact_evidence"] is True


def test_seed_event_generator_summary_passes_synthetic_smoke() -> None:
    rows = structured_seed_expansion_panel.build_seed_expansion_panel_rows()
    generator_rows = structured_seed_event_generator.build_generator_rows(rows)
    summary = structured_seed_event_generator.summarize_generator_rows(generator_rows)

    assert summary["row_count"] == 180
    assert summary["hard_emit_rows"] == 90
    assert summary["control_suppressed_rows"] == 90
    assert summary["exact_evidence_rows"] == 180
    assert summary["synthetic_smoke_passed"] is True
    assert summary["decision"] == "promote_to_validation_hard_control_design"
