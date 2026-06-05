from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_validation_panel,
)


def test_boundary_benchmark_validation_panel_selects_stable_typed_fields() -> None:
    records = [
        _record(1, "seizure free for 6 month", "Seizure-free since 27 March 2024"),
        _record(2, "unknown", "Last seizure on 25 December 2023"),
        _record(3, "unknown", "Only with sleep deprivation"),
        _record(4, "seizure free for multiple month", "Seizures are currently non-epileptic"),
        _record(
            5,
            "1 cluster per month, multiple per cluster",
            "Monthly clusters; within-cluster count unclear",
        ),
        _record(6, "multiple per week", "Several episodes per week"),
    ]

    rows = boundary_benchmark_validation_panel.build_validation_panel_rows(records)
    summary = boundary_benchmark_validation_panel.summarize_validation_panel_rows(rows)

    assert summary["decision"] == "ready_for_boundary_renderer_validation_contract"
    assert summary["row_count"] == 6
    assert summary["boundary_rows"] == 4
    assert summary["renderer_rows"] == 2
    assert summary["exact_evidence_rows"] == 6
    assert summary["final_label_policy_connected"] is False
    assert {row["expected_boundary_state"] for row in rows} >= {
        "asserted_seizure_free_interval",
        "last_event_only",
        "conditional_or_trigger_only",
        "non_epileptic_current_events",
    }
    assert {row["expected_benchmark_format_rule_id"] for row in rows} >= {
        "none_boundary_state_only",
        "gan_cluster_multiple_per_cluster",
        "gan_vague_multiple_frequency",
    }


def test_boundary_benchmark_validation_panel_rows_omit_note_text() -> None:
    rows = boundary_benchmark_validation_panel.build_validation_panel_rows(
        [_record(1, "unknown", "Last seizure on 25 December 2023")]
    )

    assert rows[0]["source_note_text"] is None
    assert rows[0]["expected_evidence_substring"] == "Last seizure on 25 December 2023"
    assert rows[0]["split"] == "validation"
    assert rows[0]["split_manifest"] == "gan2026_split_v1"
    assert rows[0]["claim_boundary"] == "validation_development_only_no_holdout_use"
    assert rows[0]["final_label_policy_connected"] is False


def test_boundary_benchmark_validation_panel_caps_rows_per_slice() -> None:
    records = [
        _record(index, "seizure free for 6 month", f"Seizure-free since day {index}")
        for index in range(20)
    ]

    rows = boundary_benchmark_validation_panel.build_validation_panel_rows(
        records,
        max_rows_per_slice=3,
    )

    assert len(rows) == 3
    assert {row["slice_id"] for row in rows} == {"asserted_seizure_free_interval"}


def _record(source_row_index: int, gold_label: str, gold_reference: str) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "note_text": f"Clinical note. {gold_reference}. Medication unchanged.",
        "gold_label": gold_label,
        "gold_reference": gold_reference,
    }
