from __future__ import annotations

import json
from types import SimpleNamespace

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    h1_hidden_family_slice_aggregates,
)


def test_h1_slice_aggregates_compute_family_gap_without_row_ids() -> None:
    summary = h1_hidden_family_slice_aggregates.build_h1_slice_aggregates(
        [_row(1, before=True, after=True, label="seizure free for 6 month")],
        [
            _row(2, before=True, after=False, label="seizure free for 6 month"),
            _row(3, before=True, after=True, label="1 per week"),
        ],
        validation_records={
            1: _record("No seizures since January.", "seizure free for 6 month")
        },
        test_records={
            2: _record("No seizures since January.", "seizure free for 6 month"),
            3: _record("Weekly focal seizures continue.", "1 per week"),
        },
    )

    families = {row["family"]: row for row in summary["family_gaps"]}

    assert families["seizure_free_duration"]["validation_rows"] == 1
    assert families["seizure_free_duration"]["test_rows"] == 1
    assert families["seizure_free_duration"]["validation_minus_test_gap"] == 1.0
    assert summary["locked_test_row_level_artifacts_written"] == 0
    assert "source_row_index" not in json.dumps(summary)


def test_h1_decision_marks_concentrated_family_gap_plausible() -> None:
    summary = h1_hidden_family_slice_aggregates.build_h1_slice_aggregates(
        [_row(1, before=True, after=True, label="unknown")],
        [_row(2, before=True, after=False, label="unknown")],
        validation_records={1: _record("Frequency is unknown.", "unknown")},
        test_records={2: _record("Frequency is unknown.", "unknown")},
    )

    assert summary["decision"] == "h1_plausible_gap_concentrates_in_top_family_slices"


def _row(
    source_row_index: int,
    *,
    before: bool,
    after: bool,
    label: str,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "baseline_label": label,
        "deterministic_correct": before,
        "gate_variants": {
            "selective_safety_floor_gate_v0": {
                "final_label": label,
                "purist_correct": after,
                "changed": before != after,
            }
        },
    }


def _record(note_text: str, gold_label: str) -> SimpleNamespace:
    return SimpleNamespace(note_text=note_text, gold_normalized_label=gold_label)
