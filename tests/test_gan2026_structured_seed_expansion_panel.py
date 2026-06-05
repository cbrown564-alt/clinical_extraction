from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_seed_expansion_panel,
)


def test_seed_expansion_panel_has_balanced_hard_and_control_cases() -> None:
    rows = structured_seed_expansion_panel.build_seed_expansion_panel_rows()
    summary = structured_seed_expansion_panel.summarize_seed_expansion_panel(rows)

    assert len(rows) == 180
    assert summary["row_count"] == 180
    assert summary["hard_case_rows"] == 90
    assert summary["control_rows"] == 90
    assert summary["family_counts"] == {
        "cluster_completion": 60,
        "seizure_free_to_unknown": 60,
        "yearly_to_daily": 60,
    }
    assert summary["hard_family_counts"] == {
        "cluster_completion": 30,
        "seizure_free_to_unknown": 30,
        "yearly_to_daily": 30,
    }
    assert summary["decision"] == "ready_for_structured_generator_smoke"


def test_seed_expansion_panel_rows_preserve_exact_evidence_contract() -> None:
    rows = structured_seed_expansion_panel.build_seed_expansion_panel_rows()
    hard_rows = [row for row in rows if row["panel_role"] == "synthetic_hard"]
    control_rows = [row for row in rows if row["panel_role"] == "synthetic_control"]

    assert all(row["expected_evidence_substring"] in row["source_note_text"] for row in rows)
    assert all(row["expected_generator_action"] == "emit_candidate" for row in hard_rows)
    assert all(row["expected_generator_action"] == "suppress_candidate" for row in control_rows)
    assert all(row["split"] == "synthetic_hard_control" for row in rows)
    assert all(row["split_manifest"] == structured_seed_expansion_panel.PANEL_NAME for row in rows)
    assert all(row["claim_boundary"] == "synthetic_development_only_no_holdout_use" for row in rows)
