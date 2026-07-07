from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    h5_repair_policy_manifest,
)


def test_h5_repair_policy_manifest_freezes_bounded_policy() -> None:
    artifact = h5_repair_policy_manifest.build_h5_repair_policy_manifest(
        _policy_reparse(),
        [
            {
                "condition": "benchmark_aligned_adapter",
                "semantic_kind_transition": "frequency->unresolved_multiple",
                "selected_evidence_valid": "True",
            },
            {
                "condition": "benchmark_aligned_adapter",
                "semantic_kind_transition": "frequency->unknown",
                "selected_evidence_valid": "False",
            },
        ],
    )

    assert artifact["repair_policy_id"] == "h5_repair_policy_v1"
    assert artifact["locked_test_row_level_artifacts_used"] == 0
    assert artifact["decision"] == "current_bounded_policy_for_next_validation_diagnostic"
    assert artifact["next_diagnostic_contract"]["holdout_use_authorized"] is False
    assert (
        artifact["next_diagnostic_contract"]["do_not_restore_broad_frequency_to_sentinel_repair"]
        is True
    )
    assert artifact["semantic_kind_transformations"]["frequency_to_no_reference_rows"] == 0
    assert artifact["semantic_kind_transformations"]["invalid_selected_evidence_rows"] == 1
    assert artifact["condition_summaries"]["benchmark_aligned_adapter"]["raw_correct_to_wrong"] == 0

    by_bound = {item["bound_id"]: item for item in artifact["policy_bounds"]}
    assert (
        by_bound["frequency_bearing_prediction_may_not_become_no_reference"]["status"] == "disabled"
    )
    assert (
        by_bound["per_hour_rates_render_as_multiple_per_day"]["status"]
        == "allowed_benchmark_rendering"
    )


def test_h5_repair_policy_manifest_writes_json_and_markdown(tmp_path: Path) -> None:
    artifact = h5_repair_policy_manifest.build_h5_repair_policy_manifest(
        _policy_reparse(),
        [],
    )
    json_path = tmp_path / "manifest.json"
    report_path = tmp_path / "manifest.md"

    h5_repair_policy_manifest.write_h5_repair_policy_manifest_outputs(
        artifact,
        json_path=json_path,
        markdown_path=report_path,
    )

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["artifact_kind"] == "gan2026_h5_repair_policy_v1_manifest"
    report = report_path.read_text(encoding="utf-8")
    assert "H5 Repair Policy v1 Manifest" in report
    assert "Frequency-to-no-reference rows: `0`" in report


def _policy_reparse() -> dict[str, object]:
    return {
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "conditions": [
            _condition("format_only_repair", 0.776, 20, 6, 0, 0),
            _condition("selected_evidence_arithmetic_only", 0.9, 70, 38, 1, 16),
            _condition("benchmark_aligned_adapter", 0.852, 41, 25, 0, 12),
        ],
    }


def _condition(
    condition: str,
    purist_accuracy: float,
    changed: int,
    wtc: int,
    ctw: int,
    semantic: int,
) -> dict[str, object]:
    return {
        "condition": condition,
        "score": {
            "purist_accuracy": purist_accuracy,
            "purist_correct": int(purist_accuracy * 250),
            "rows": 250,
        },
        "repair_attribution": {
            "changed_from_raw": changed,
            "raw_wrong_to_condition_correct": wtc,
            "raw_correct_to_condition_wrong": ctw,
            "semantic_kind_transitions": semantic,
        },
    }
