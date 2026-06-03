from __future__ import annotations

import csv
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    component_projection_panel,
)


def test_panel_propagates_atlas_family_and_infers_first_failure_owner(tmp_path: Path) -> None:
    rq2 = tmp_path / "rq2.jsonl"
    rq4 = tmp_path / "rq4.jsonl"
    atlas = tmp_path / "atlas.csv"
    slices = tmp_path / "slices.json"

    rq2.write_text(
        _jsonl(
            {
                "source_row_index": 10,
                "split": "validation",
                "candidate_name": "llm_heavy_selected_fact",
                "gold_label": "multiple per week",
                "candidate_label": "multiple times per week",
                "baseline_label": "unknown",
                "selected_evidence": "multiple times per week",
                "evidence_status": "exact",
                "source_id_status": "valid",
                "purist_correct": False,
                "wrong_to_correct": False,
                "correct_to_wrong": False,
                "operand_complete": True,
                "hidden_families": [],
            }
        ),
        encoding="utf-8",
    )
    rq4.write_text("", encoding="utf-8")
    _write_atlas(
        atlas,
        [
            {
                "source_row_index": 10,
                "hidden_families": "rate_bucket_or_denominator;benchmark_format_convention",
                "first_failure_owner": "projection",
                "first_failure_reason": "atlas projection owner",
            }
        ],
    )
    slices.write_text(_slice_manifest([10]), encoding="utf-8")

    rows, metadata = component_projection_panel.build_component_projection_panel(
        rq2_matrix_path=rq2,
        rq4_matrix_path=rq4,
        atlas_csv_path=atlas,
        hard_slice_manifest_path=slices,
    )

    assert rows[0]["hidden_families"] == [
        "rate_bucket_or_denominator",
        "benchmark_format_convention",
    ]
    assert rows[0]["first_failure_owner"] == "projection_rendering_policy"
    assert rows[0]["interpretation_policy"] == "projection_compatible_phrase"
    assert metadata["panel_row_count"] == 1
    assert metadata["predeclared_slices"]["projection_arbitration"]["row_count"] == 1


def test_panel_marks_gated_targets_and_regression_rows(tmp_path: Path) -> None:
    rq2 = tmp_path / "rq2.jsonl"
    rq4 = tmp_path / "rq4.jsonl"
    atlas = tmp_path / "atlas.csv"
    slices = tmp_path / "slices.json"
    rq2.write_text("", encoding="utf-8")
    rq4.write_text(
        _jsonl(
            {
                "source_row_index": 20,
                "surface": "target_duration_enriched",
                "component_name": "graph_gated_month_bucket_duration",
                "gold_label": "seizure free for multiple month",
                "candidate_label": "seizure free for multiple month",
                "baseline_label": "seizure free for multiple year",
                "projection_correct": True,
                "wrong_to_correct": True,
                "correct_to_wrong": False,
                "changed_from_baseline": True,
                "hidden_families": ["seizure_free_duration"],
            }
        )
        + _jsonl(
            {
                "source_row_index": 30,
                "surface": "regression_validation_hard_slice",
                "component_name": "graph_gated_month_bucket_duration",
                "gold_label": "4 per day",
                "candidate_label": "4 per day",
                "baseline_label": "4 per day",
                "projection_correct": True,
                "wrong_to_correct": False,
                "correct_to_wrong": False,
                "changed_from_baseline": False,
                "hidden_families": ["already_projection_correct"],
            }
        ),
        encoding="utf-8",
    )
    _write_atlas(atlas, [])
    slices.write_text(_slice_manifest([]), encoding="utf-8")

    rows, metadata = component_projection_panel.build_component_projection_panel(
        rq2_matrix_path=rq2,
        rq4_matrix_path=rq4,
        atlas_csv_path=atlas,
        hard_slice_manifest_path=slices,
    )

    by_row = {row["source_row_index"]: row for row in rows}
    assert by_row[20]["panel_role"] == "gated_projection_target"
    assert by_row[30]["panel_role"] == "gated_projection_regression"
    gate = metadata["gated_projection_panels"]["graph_gated_month_bucket_duration"]
    assert gate["target_rows"] == 1
    assert gate["regression_rows"] == 1
    assert gate["wrong_to_correct"] == 1
    assert gate["correct_to_wrong"] == 0


def _jsonl(row: dict) -> str:
    return json.dumps(row) + "\n"


def _write_atlas(path: Path, rows: list[dict]) -> None:
    fieldnames = [
        "source_row_index",
        "hidden_families",
        "first_failure_owner",
        "first_failure_reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _slice_manifest(members: list[int]) -> str:
    return json.dumps(
        {
            "slices": [
                {
                    "slice_name": "projection_arbitration",
                    "component_focus": "graph/final projection",
                    "membership_rule": "test rule",
                    "primary_metric": "test metric",
                    "members": [{"source_row_index": row} for row in members],
                }
            ]
        }
    )
