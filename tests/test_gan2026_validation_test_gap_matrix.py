from __future__ import annotations

import csv
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    validation_test_gap_matrix,
)


def test_gap_matrix_builds_score_layers_from_validation_component_csv(tmp_path: Path) -> None:
    matrix_csv = tmp_path / "component_matrix.csv"
    with matrix_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "candidate_version",
                "source_row_index",
                "split",
                "split_manifest",
                "gold_label",
                "final_action",
                "prediction_bearing",
                "prediction_label",
                "selected_evidence_exact",
                "selected_source_ids_exist",
                "deterministic_comparator_label",
                "deterministic_comparator_purist_correct",
                "final_purist_correct",
                "comparator_transition",
                "hidden_families",
                "first_failure_owner",
                "first_failure_reason",
                "router_action",
                "router_reason",
                "safety_floor_changed",
                "parse_issue_count",
                "evidence_issue_count",
                "schema_issue_count",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "candidate_version": "candidate_v0",
                "source_row_index": "42",
                "split": "validation",
                "split_manifest": "gan2026_split_v1",
                "gold_label": "1 per week",
                "final_action": "predict",
                "prediction_bearing": "True",
                "prediction_label": "1 per week",
                "selected_evidence_exact": "True",
                "selected_source_ids_exist": "True",
                "deterministic_comparator_label": "unknown",
                "deterministic_comparator_purist_correct": "False",
                "final_purist_correct": "True",
                "comparator_transition": "W_to_C",
                "hidden_families": "current_vs_historical;rate_bucket_or_denominator",
                "first_failure_owner": "projection",
                "first_failure_reason": "demo",
                "router_action": "predict",
                "router_reason": "plain_predictable_frequency",
                "safety_floor_changed": "False",
                "parse_issue_count": "0",
                "evidence_issue_count": "0",
                "schema_issue_count": "0",
            }
        )

    inventory = {
        "split_manifest": "gan2026_split_v1",
        "protocol": "protocol.md",
        "artifacts": [
            {
                "artifact_id": "component_matrix",
                "candidate_name": "candidate_v0",
                "pipeline_family": "hybrid",
                "distribution": "validation750",
                "paths": [matrix_csv.name],
                "artifact_role": "component_matrix_seed",
                "score_layers_available": ["deterministic_comparator", "final_policy"],
                "allowed_inspection": "validation_row_level_allowed",
                "hypothesis_ids": ["H2", "H4"],
            }
        ],
    }

    rows, metadata = validation_test_gap_matrix.build_gap_matrix(inventory, root=tmp_path)

    assert metadata["row_count"] == 2
    assert metadata["locked_test_row_level_artifacts_used"] == 0
    assert {row["score_layer"] for row in rows} == {
        "deterministic_comparator",
        "final_policy",
    }
    final_row = next(row for row in rows if row["score_layer"] == "final_policy")
    assert final_row["source_row_index"] == 42
    assert final_row["component_owner"] == "deterministic_adapter"
    assert final_row["hidden_families"] == [
        "current_vs_historical",
        "rate_bucket_or_denominator",
    ]
    assert final_row["wrong_to_correct"] is True
    assert final_row["correct_to_wrong"] is False
    assert final_row["evidence_exact"] is True
    assert final_row["inspection_policy"] == "validation_row_level_allowed"


def test_gap_matrix_refuses_locked_test_row_level_sources(tmp_path: Path) -> None:
    test_jsonl = tmp_path / "locked.jsonl"
    test_jsonl.write_text(json.dumps({"source_row_index": 1}) + "\n")
    inventory = {
        "split_manifest": "gan2026_split_v1",
        "protocol": "protocol.md",
        "artifacts": [
            {
                "artifact_id": "locked_rows",
                "candidate_name": "candidate_v0",
                "pipeline_family": "hybrid",
                "distribution": "locked_test450",
                "paths": [test_jsonl.name],
                "artifact_role": "test_rows",
                "score_layers_available": ["final_policy"],
                "allowed_inspection": "locked_test_aggregate_only",
                "hypothesis_ids": ["H2"],
            }
        ],
    }

    rows, metadata = validation_test_gap_matrix.build_gap_matrix(inventory, root=tmp_path)

    assert rows == []
    assert metadata["locked_test_row_level_artifacts_used"] == 0
    assert metadata["skipped_artifacts"][0]["reason"] == "locked_test_row_level_blocked"


def test_gap_matrix_skips_validation_csvs_without_component_matrix_role(tmp_path: Path) -> None:
    atlas_csv = tmp_path / "atlas.csv"
    atlas_csv.write_text("source_row_index,hidden_families\n1,current_vs_historical\n")
    inventory = {
        "split_manifest": "gan2026_split_v1",
        "protocol": "protocol.md",
        "artifacts": [
            {
                "artifact_id": "hidden_family_atlas",
                "candidate_name": "atlas",
                "pipeline_family": "analysis",
                "distribution": "validation750",
                "paths": [atlas_csv.name],
                "artifact_role": "hidden_family_and_first_failure_join",
                "score_layers_available": ["hidden_family"],
                "allowed_inspection": "validation_row_level_allowed",
                "hypothesis_ids": ["H1"],
            }
        ],
    }

    rows, metadata = validation_test_gap_matrix.build_gap_matrix(inventory, root=tmp_path)

    assert rows == []
    assert metadata["skipped_artifacts"][0]["reason"] == "unsupported_row_source_role"
