from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_seed_validation_panel,
)


def test_seed_validation_panel_selects_hard_and_control_rows() -> None:
    current_rows = [
        _current_row(1, "seizure free for multiple year", "unknown", False),
        _current_row(2, "4 per year", "1 per day", False),
        _current_row(3, "1 per month", "1 cluster per month, multiple per cluster", False),
        _current_row(4, "seizure free for 6 month", "seizure free for 6 month", True),
        _current_row(5, "2 per year", "2 per year", True),
        _current_row(6, "1 per month", "1 per month", True),
    ]
    records = {
        index: _record(index, f"evidence {index}") for index in range(1, 7)
    }

    rows = structured_seed_validation_panel.build_validation_panel_rows(
        current_rows,
        records,
    )
    summary = structured_seed_validation_panel.summarize_validation_panel_rows(rows)

    assert summary["row_count"] == 6
    assert summary["hard_rows"] == 3
    assert summary["control_rows"] == 3
    assert summary["family_counts"] == {
        "cluster_completion": 2,
        "seizure_free_to_unknown": 2,
        "yearly_to_daily": 2,
    }
    assert summary["decision"] == "ready_for_validation_extractor_smoke"


def test_seed_validation_panel_rows_omit_note_text() -> None:
    current_rows = [_current_row(1, "4 per year", "1 per day", False)]
    records = {1: _record(1, "daily seizure evidence")}

    rows = structured_seed_validation_panel.build_validation_panel_rows(
        current_rows,
        records,
    )

    assert rows[0]["expected_evidence_substring"] == "daily seizure evidence"
    assert rows[0]["source_note_text"] is None
    assert rows[0]["expected_generator_action"] == "emit_candidate"
    assert rows[0]["claim_boundary"] == "validation_development_only_no_holdout_use"


def _current_row(
    source_row_index: int,
    current_label: str,
    gold_label: str,
    final_purist_correct: bool,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "final_label": current_label,
        "gold_label": gold_label,
        "final_purist_correct": final_purist_correct,
    }


def _record(source_row_index: int, evidence: str) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "note_text": f"Clinical note containing {evidence}.",
        "gold_reference": evidence,
    }
