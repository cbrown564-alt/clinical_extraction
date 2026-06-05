from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    validation_test_surface_map,
)


def test_surface_map_summarizes_artifacts_and_computes_candidate_gap(tmp_path: Path) -> None:
    validation_path = tmp_path / "validation.json"
    test_path = tmp_path / "test.json"
    validation_path.write_text(
        json.dumps(
            {
                "row_count": 750,
                "metrics": {
                    "projected_correct_rows": 720,
                    "projected_purist_proxy": 0.96,
                },
                "transition_counts": {
                    "changed": 20,
                    "wrong_to_correct": 12,
                    "correct_to_wrong": 1,
                },
                "decision": "freeze_candidate_for_aggregate_audit",
            }
        )
    )
    test_path.write_text(
        json.dumps(
            {
                "metrics": {
                    "test_rows": 450,
                    "final_correct_rows": 360,
                    "final_purist_proxy": 0.8,
                },
                "decision": "does_not_meet_goal",
            }
        )
    )
    inventory = {
        "inventory_id": "demo",
        "split_manifest": "gan2026_split_v1",
        "protocol": "protocol.md",
        "inspection_policy": {
            "locked_test": "aggregate_or_predeclared_slice_only",
        },
        "artifacts": [
            {
                "artifact_id": "candidate_validation",
                "candidate_name": "candidate_v0",
                "pipeline_family": "hybrid",
                "distribution": "validation750",
                "paths": [validation_path.name],
                "artifact_role": "validation",
                "replay_status": "saved",
                "score_layers_available": ["final_policy"],
                "allowed_inspection": "validation_row_level_allowed",
                "hypothesis_ids": ["H2"],
            },
            {
                "artifact_id": "candidate_test",
                "candidate_name": "candidate_v0",
                "pipeline_family": "hybrid",
                "distribution": "locked_test450",
                "paths": [test_path.name],
                "artifact_role": "test",
                "replay_status": "aggregate",
                "score_layers_available": ["final_policy"],
                "allowed_inspection": "locked_test_aggregate_only",
                "hypothesis_ids": ["H2"],
            },
        ],
    }

    surface_map = validation_test_surface_map.build_surface_map(inventory, root=tmp_path)

    assert surface_map["surface_count"] == 2
    assert surface_map["surface_summaries"][0]["final_purist_proxy"] == 0.96
    assert surface_map["surface_summaries"][0]["wrong_to_correct"] == 12
    assert surface_map["candidate_gap_summary"] == [
        {
            "candidate_name": "candidate_v0",
            "validation_artifact_id": "candidate_validation",
            "test_artifact_id": "candidate_test",
            "validation_final_purist_proxy": 0.96,
            "test_final_purist_proxy": 0.8,
            "validation_minus_test_gap": 0.15999999999999992,
            "validation_rows": 750,
            "test_rows": 450,
        }
    ]


def test_surface_map_report_states_locked_test_boundary(tmp_path: Path) -> None:
    surface_map = {
        "split_manifest": "gan2026_split_v1",
        "candidate_gap_summary": [],
        "surface_summaries": [],
        "known_gaps": ["example"],
    }
    report_path = tmp_path / "report.md"

    validation_test_surface_map.write_surface_map_report(surface_map, report_path)

    report = report_path.read_text()
    assert "aggregate-only for locked test surfaces" in report
    assert "does not expose locked-test row-level failures" in report

