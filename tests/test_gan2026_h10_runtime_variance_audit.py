from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    h10_runtime_variance_audit,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_h10_audit_separates_raw_identity_from_score_layer_drift(
    tmp_path: Path,
) -> None:
    live_path = tmp_path / "live.jsonl"
    replay_path = tmp_path / "replay.jsonl"
    surface_map_path = tmp_path / "surface.json"

    _write_jsonl(
        live_path,
        [
            {
                "source_row_index": 1,
                "raw_output": "same",
                "llm_candidate_raw_output": "same-candidate",
                "adjudicator_raw_output": "same-adjudicator",
                "reused_llm_candidate_output": False,
                "reused_adjudicator_output": False,
                "score_layers": {
                    "raw": {
                        "final_label": "1 per month",
                        "purist_correct": True,
                        "scorable": True,
                    },
                    "adapter": {
                        "final_label": "unknown",
                        "purist_correct": False,
                        "scorable": True,
                    },
                },
            }
        ],
    )
    _write_jsonl(
        replay_path,
        [
            {
                "source_row_index": 1,
                "raw_output": "same",
                "llm_candidate_raw_output": "same-candidate",
                "adjudicator_raw_output": "same-adjudicator",
                "reused_llm_candidate_output": True,
                "reused_adjudicator_output": True,
                "score_layers": {
                    "raw": {
                        "final_label": "1 per month",
                        "purist_correct": True,
                        "scorable": True,
                    },
                    "adapter": {
                        "final_label": "1 per month",
                        "purist_correct": True,
                        "scorable": True,
                    },
                },
            }
        ],
    )
    surface_map_path.write_text(
        json.dumps(
            {
                "candidate_gap_summary": [
                    {
                        "candidate_name": "same_output_candidate",
                        "validation_final_purist_proxy": 0.94,
                        "test_final_purist_proxy": 0.78,
                        "validation_minus_test_gap": 0.16,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    audit = h10_runtime_variance_audit.build_h10_runtime_variance_audit(
        live_path=live_path,
        replay_path=replay_path,
        surface_map_path=surface_map_path,
    )

    assert audit["decision"] == "h10_rejected_as_primary_gap_explanation"
    assert audit["raw_output_identity"]["raw_output"]["identical_rows"] == 1
    assert audit["raw_output_identity"]["adjudicator_raw_output"]["identity_rate"] == 1
    assert audit["score_layer_drift"]["adapter"]["purist_correct_changed_rows"] == 1
    assert audit["surface_gap_context"]["max_validation_minus_test_gap"] == 0.16


def test_h10_report_names_claim_boundary(tmp_path: Path) -> None:
    report_path = tmp_path / "h10.md"
    audit = {
        "decision": "h10_rejected_as_primary_gap_explanation",
        "claim_boundary": "No locked-test row-level failures were inspected.",
        "matched_source_rows": 1,
        "raw_output_identity": {
            "raw_output": {"identical_rows": 1, "identity_rate": 1.0},
        },
        "score_layer_drift": {
            "adapter": {
                "rows": 1,
                "final_label_changed_rows": 1,
                "purist_correct_changed_rows": 1,
                "live_purist_accuracy": 0.0,
                "replay_purist_accuracy": 1.0,
            }
        },
        "surface_gap_context": {
            "paired_candidates_with_gap": 1,
            "max_validation_minus_test_gap": 0.16,
        },
        "interpretation": "Same-output replay still leaves the saved gap context in place.",
    }

    h10_runtime_variance_audit.write_h10_report(audit, report_path)

    report = report_path.read_text(encoding="utf-8")
    assert "H10 Runtime Variance Audit" in report
    assert "No locked-test row-level failures were inspected." in report
    assert "h10_rejected_as_primary_gap_explanation" in report
