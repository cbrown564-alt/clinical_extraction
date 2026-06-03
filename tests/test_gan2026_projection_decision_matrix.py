from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    projection_decision_matrix,
)


def test_projection_matrix_extracts_saved_same_row_projection_components(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "rq2.jsonl"
    arbitration_path = tmp_path / "arbitration.jsonl"
    duration_path = tmp_path / "duration.jsonl"
    evidence_path.write_text(
        _jsonl(
            {
                "source_row_index": 10,
                "distribution": "validation750",
                "artifact_path": "hybrid.jsonl",
                "candidate_name": "state_graph_projection",
                "component_owner": "graph_projection",
                "candidate_label": "1 per month",
                "baseline_label": "4 per day",
                "gold_label": "4 per day",
                "purist_correct": False,
                "baseline_purist_correct": True,
                "changed_from_deterministic": True,
                "wrong_to_correct": False,
                "correct_to_wrong": True,
                "evidence_status": "exact",
                "source_id_status": "valid",
                "hidden_families": ["temporal_conflict"],
            }
        )
        + _jsonl(
            {
                "source_row_index": 10,
                "distribution": "validation750",
                "candidate_name": "llm_candidate_selector_raw",
                "candidate_label": "1 per month",
            }
        ),
        encoding="utf-8",
    )
    arbitration_path.write_text("", encoding="utf-8")
    duration_path.write_text("", encoding="utf-8")

    rows, metadata = projection_decision_matrix.build_projection_decision_matrix(
        evidence_matrix_path=evidence_path,
        arbitration_path=arbitration_path,
        duration_path=duration_path,
    )

    assert [row["component_name"] for row in rows] == ["state_graph_projection"]
    assert rows[0]["clinical_subproblem"] == "projection"
    assert rows[0]["correct_to_wrong"] is True
    assert metadata["by_component"]["state_graph_projection"]["projection_correct_rate"] == 0


def test_projection_matrix_extracts_graph_arbitration_and_duration_rows(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "rq2.jsonl"
    arbitration_path = tmp_path / "arbitration.jsonl"
    duration_path = tmp_path / "duration.jsonl"
    evidence_path.write_text("", encoding="utf-8")
    arbitration_path.write_text(
        _jsonl(
            {
                "source_row_index": 20,
                "gold_normalized_label": "unknown",
                "failure_family": "unknown_arbitration",
                "variant_results": {
                    "baseline_v0": {
                        "final_label": "1 per month",
                        "correct": False,
                        "evidence": "one per month",
                        "selected_node_ids": ["sg-1"],
                    },
                    "boundary_state_priority": {
                        "final_label": "unknown",
                        "correct": True,
                        "evidence": "frequency unclear",
                        "selected_node_ids": ["sg-2"],
                    },
                    "oracle_gold_node": {
                        "final_label": "unknown",
                        "correct": True,
                        "evidence": "frequency unclear",
                        "selected_node_ids": ["sg-2"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    duration_path.write_text(
        _jsonl(
            {
                "source_row_index": 30,
                "surface": "target_duration_enriched",
                "gold_normalized_label": "seizure free for multiple month",
                "baseline_projection": {"final_label": "seizure free for multiple year"},
                "month_bucket_projection": {
                    "final_label": "seizure free for multiple month",
                    "selected_node_ids": ["duration-sg-1"],
                },
                "baseline_correct": False,
                "month_bucket_correct": True,
                "label_changed": True,
                "selected_evidence_valid": True,
            }
        ),
        encoding="utf-8",
    )

    rows, metadata = projection_decision_matrix.build_projection_decision_matrix(
        evidence_matrix_path=evidence_path,
        arbitration_path=arbitration_path,
        duration_path=duration_path,
    )

    by_component = {row["component_name"]: row for row in rows}
    assert by_component["boundary_state_priority"]["wrong_to_correct"] is True
    assert by_component["graph_gated_month_bucket_duration"]["wrong_to_correct"] is True
    assert metadata["by_component"]["oracle_gold_node"]["projection_correct_rate"] == 1
    assert metadata["by_surface"]["target_duration_enriched"]["wrong_to_correct"] == 1


def test_projection_matrix_writes_report(tmp_path: Path) -> None:
    rows = [
        {
            "source_row_index": 1,
            "surface": "validation750",
            "component_name": "deterministic_top_candidate",
            "projection_correct": True,
            "changed_from_baseline": False,
            "wrong_to_correct": False,
            "correct_to_wrong": False,
            "evidence_status": "exact",
            "source_id_status": "valid",
        }
    ]
    metadata = projection_decision_matrix.summarize_projection_rows(rows)
    jsonl_path = tmp_path / "matrix.jsonl"
    report_path = tmp_path / "matrix.md"

    projection_decision_matrix.write_matrix_jsonl(rows, jsonl_path)
    projection_decision_matrix.write_matrix_report(
        rows,
        metadata,
        report_path,
        jsonl_path=jsonl_path,
    )

    assert json.loads(jsonl_path.read_text(encoding="utf-8"))["source_row_index"] == 1
    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 RQ4 Projection-Decision Matrix" in report
    assert "deterministic_top_candidate" in report


def _jsonl(row: dict) -> str:
    return json.dumps(row) + "\n"
