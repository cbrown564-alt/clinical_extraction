from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    h5_semantic_repair_gap,
)


def test_h5_semantic_repair_gap_reports_repair_gain_without_test_rows() -> None:
    replacement = {
        "conditions": [
            _condition(
                "raw_model_selected_label",
                purist_accuracy=0.75,
                purist_correct=75,
                changed=0,
                raw_wrong_to_correct=0,
                raw_correct_to_wrong=0,
            ),
            _condition(
                "format_only_repair",
                purist_accuracy=0.75,
                purist_correct=75,
                changed=3,
                raw_wrong_to_correct=0,
                raw_correct_to_wrong=0,
            ),
            _condition(
                "selected_evidence_arithmetic_only",
                purist_accuracy=0.87,
                purist_correct=87,
                changed=20,
                raw_wrong_to_correct=12,
                raw_correct_to_wrong=1,
                prediction_owner="llm_selected_evidence_then_deterministic_arithmetic",
            ),
            _condition(
                "benchmark_aligned_adapter",
                purist_accuracy=0.81,
                purist_correct=81,
                changed=12,
                raw_wrong_to_correct=8,
                raw_correct_to_wrong=0,
                prediction_owner="deterministic_benchmark_renderer",
            ),
        ],
        "split_manifest": "gan2026_split_v1",
        "summary": {"row_count": 100},
    }
    validation = {
        "metrics": {
            "row_count": 750,
            "raw_proposed_purist_proxy": 0.736,
            "contract_projected_purist_proxy": 0.968,
            "contract_selected_rows": 23,
            "parse_ok_rows": 269,
            "exact_evidence_rows": 688,
        }
    }
    test = {
        "claim_boundary": "aggregate-only test audit",
        "metrics": {
            "test_rows": 450,
            "raw_base_purist_proxy": 0.760,
            "final_purist_proxy": 0.7933333333333333,
            "contract_selected_rows": 4,
            "fewshot_parse_ok_rows": 158,
            "fewshot_exact_evidence_rows": 408,
        },
    }

    artifact = h5_semantic_repair_gap.build_h5_semantic_repair_gap(
        replacement,
        validation_summary=validation,
        test_summary=test,
    )

    assert artifact["hypothesis_id"] == "H5"
    assert artifact["split_manifest"] == "gan2026_split_v1"
    assert artifact["locked_test_row_level_artifacts_used"] == 0
    assert artifact["same_output_ladder"]["benchmark_aligned_gain_over_raw"] == 0.06
    assert artifact["same_output_ladder"]["format_only_gain_over_raw"] == 0.0
    assert artifact["validation_test_repair_gain"]["validation_repair_gain"] == 0.232
    assert artifact["validation_test_repair_gain"]["test_repair_gain"] == 0.0333
    assert artifact["validation_test_repair_gain"]["repair_gain_validation_minus_test"] == 0.1987
    assert artifact["outcome"] == "partially_supported_revise"


def test_h5_semantic_repair_gap_writes_json_and_markdown(tmp_path: Path) -> None:
    artifact = h5_semantic_repair_gap.build_h5_semantic_repair_gap(
        {"conditions": [], "split_manifest": "gan2026_split_v1", "summary": {}},
        validation_summary={"metrics": {}},
        test_summary={"metrics": {}},
    )
    json_path = tmp_path / "h5.json"
    report_path = tmp_path / "h5.md"

    h5_semantic_repair_gap.write_h5_outputs(
        artifact,
        json_path=json_path,
        markdown_path=report_path,
    )

    assert json.loads(json_path.read_text(encoding="utf-8"))["hypothesis_id"] == "H5"
    report = report_path.read_text(encoding="utf-8")
    assert "H5 Semantic Repair Gap Test" in report
    assert "Locked-test row-level artifacts used: `0`" in report


def _condition(
    condition: str,
    *,
    purist_accuracy: float,
    purist_correct: int,
    changed: int,
    raw_wrong_to_correct: int,
    raw_correct_to_wrong: int,
    prediction_owner: str = "llm",
) -> dict[str, object]:
    return {
        "condition": condition,
        "prediction_owner": prediction_owner,
        "score": {
            "rows": 100,
            "purist_accuracy": purist_accuracy,
            "purist_correct": purist_correct,
        },
        "repair_attribution": {
            "changed_from_raw": changed,
            "raw_wrong_to_condition_correct": raw_wrong_to_correct,
            "raw_correct_to_condition_wrong": raw_correct_to_wrong,
        },
    }
