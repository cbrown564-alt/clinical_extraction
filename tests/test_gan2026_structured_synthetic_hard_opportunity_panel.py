from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_synthetic_hard_opportunity_panel,
)


def test_synthetic_hard_opportunity_panel_has_balanced_projection_families() -> None:
    rows = structured_synthetic_hard_opportunity_panel.build_synthetic_panel_rows()
    summary = structured_synthetic_hard_opportunity_panel.summarize_synthetic_panel_rows(
        rows
    )

    assert summary["row_count"] == 240
    assert summary["hard_rows"] == 120
    assert summary["control_rows"] == 120
    assert summary["exact_evidence_rows"] == 240
    assert summary["family_counts"] == {
        "cluster_frequency": 60,
        "daily_frequency": 60,
        "other_frequency": 60,
        "unknown_frequency": 60,
    }
    assert summary["decision"] == "ready_for_structured_projection_generator_smoke"


def test_synthetic_hard_opportunity_rows_preserve_source_text_and_expected_actions() -> None:
    rows = structured_synthetic_hard_opportunity_panel.build_synthetic_panel_rows()
    hard_rows = [row for row in rows if row["panel_role"] == "synthetic_hard"]
    control_rows = [row for row in rows if row["panel_role"] == "synthetic_control"]

    assert all(row["expected_evidence_substring"] in row["source_note_text"] for row in rows)
    assert all(row["expected_generator_action"] == "emit_candidate" for row in hard_rows)
    assert all(row["expected_generator_action"] == "suppress_candidate" for row in control_rows)
    assert all(row["projection_ownership_explicit"] is True for row in rows)
    assert all(row["claim_boundary"] == "synthetic_development_only_no_holdout_use" for row in rows)
