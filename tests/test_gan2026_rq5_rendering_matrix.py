from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq5_rendering_matrix,
)


def test_rq5_matrix_extracts_materialized_replay_state_bundle(tmp_path: Path) -> None:
    replay_path = tmp_path / "replay.jsonl"
    rq4_path = tmp_path / "rq4.jsonl"
    panel_path = tmp_path / "panel.jsonl"
    replay_path.write_text(
        _jsonl(
            {
                "source_row_index": 10,
                "split": "validation",
                "split_manifest": "gan2026_split_v1",
                "reference": {
                    "gold_label": "4 per day",
                    "gold_label_kind": "frequency",
                    "gold_normalized_label": "4 per day",
                },
                "diagnostics": {"deterministic_correct": True},
                "component_inputs": {
                    "deterministic_top": {"final_label": "4 per day"},
                    "state_graph_nodes": [
                        {
                            "node_id": "sg-001",
                            "kind": "frequency_rate",
                            "semantic_kind": "frequency",
                            "normalized_label": "4 per day",
                            "monthly_frequency": 121.7,
                            "evidence": "four per day",
                            "rule_id": "rate.direct_count_per_period",
                            "temporality": "current",
                            "assertion_status": "asserted",
                            "certainty": "certain",
                        }
                    ],
                    "state_graph_projection": {
                        "final_label": "4 per day",
                        "final_kind": "frequency",
                        "evidence": "four per day",
                        "projection_policy": "gan2026_state_graph_projection_v0",
                        "rationale": "Projected.",
                        "selected_node_ids": ["sg-001"],
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    rq4_path.write_text(
        _jsonl(
            {
                "source_row_index": 10,
                "hidden_families": ["rate_bucket_or_denominator"],
            }
        ),
        encoding="utf-8",
    )
    panel_path.write_text("", encoding="utf-8")

    rows, metadata = rq5_rendering_matrix.build_rendering_matrix(
        replay_path=replay_path,
        rq4_matrix_path=rq4_path,
        panel_path=panel_path,
        include_replay_limit=1,
    )

    replay_rows = [row for row in rows if row["claim_boundary"] == "materialized_replay"]
    assert [row["compiler_rendering_variant"] for row in replay_rows] == [
        "current_production",
        "evidence_preserving",
        "strict_format",
    ]
    assert replay_rows[0]["fixed_selected_state_ids"] == ["sg-001"]
    assert replay_rows[0]["exact_label_match"] is True
    assert replay_rows[0]["hidden_families"] == ["rate_bucket_or_denominator"]
    assert metadata["by_variant"]["current_production"]["parse_valid_rate"] == 1


def test_rq5_matrix_records_acd_policy_ablation_drift(tmp_path: Path) -> None:
    replay_path = tmp_path / "replay.jsonl"
    rq4_path = tmp_path / "rq4.jsonl"
    panel_path = tmp_path / "panel.jsonl"
    replay_path.write_text("", encoding="utf-8")
    rq4_path.write_text("", encoding="utf-8")
    panel_path.write_text("", encoding="utf-8")

    rows, metadata = rq5_rendering_matrix.build_rendering_matrix(
        replay_path=replay_path,
        rq4_matrix_path=rq4_path,
        panel_path=panel_path,
    )

    acd_008 = [
        row
        for row in rows
        if row["acd_id"] == "ACD-008"
        and row["compiler_rendering_variant"] == "acd_off_ablation"
    ][0]
    acd_aware = [
        row
        for row in rows
        if row["acd_id"] == "ACD-008"
        and row["compiler_rendering_variant"] == "acd_aware"
    ][0]
    assert acd_aware["rendered_label"] == "1 per month"
    assert acd_aware["semantic_drift"] is False
    assert acd_008["semantic_drift"] is True
    assert acd_008["first_failure_owner_after_rendering"] == "compiler_renderer"
    assert metadata["by_acd_id"]["ACD-008"]["semantic_drift_count"] >= 1


def test_rq5_matrix_writes_jsonl_and_report(tmp_path: Path) -> None:
    rows = [
        {
            "source_row_index": 1,
            "compiler_rendering_variant": "current_production",
            "claim_boundary": "focused_fixture",
            "acd_id": "ACD-004",
            "parse_valid": True,
            "exact_label_match": True,
            "purist_correct": True,
            "pragmatic_correct": True,
            "semantic_drift": False,
            "benchmark_format_leakage": False,
            "exact_evidence_retained": True,
            "source_id_retained": True,
            "wrong_to_correct": False,
            "correct_to_wrong": False,
            "first_failure_owner_after_rendering": "none_observed",
        }
    ]
    metadata = rq5_rendering_matrix.summarize_rendering_rows(rows)
    jsonl_path = tmp_path / "matrix.jsonl"
    report_path = tmp_path / "matrix.md"

    rq5_rendering_matrix.write_matrix_jsonl(rows, jsonl_path)
    rq5_rendering_matrix.write_matrix_report(
        rows,
        metadata,
        report_path,
        jsonl_path=jsonl_path,
    )

    assert json.loads(jsonl_path.read_text(encoding="utf-8"))["source_row_index"] == 1
    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 RQ5 Fixed Selected-State Rendering Matrix" in report
    assert "ACD-004" in report


def _jsonl(row: dict) -> str:
    return json.dumps(row) + "\n"
