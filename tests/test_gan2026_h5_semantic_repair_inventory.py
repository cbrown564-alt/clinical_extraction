from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    h5_semantic_repair_inventory,
)


def test_h5_inventory_classifies_format_and_semantic_layers() -> None:
    artifact = h5_semantic_repair_inventory.build_h5_semantic_repair_inventory(
        _replacement_ablation()
    )

    assert artifact["hypothesis_id"] == "H5"
    assert artifact["locked_test_row_level_artifacts_used"] == 0
    assert artifact["inspection_policy"]["locked_test"] == "not_used"
    assert artifact["summary"]["semantic_families"] >= 3
    assert artifact["summary"]["quarantined_or_review_required_families"] >= 1

    by_id = {item["family_id"]: item for item in artifact["repair_families"]}
    assert by_id["format_only_prediction_surface"]["semantic_effect"] == "format_only"
    assert by_id["format_only_prediction_surface"]["default_policy"] == "allowed"
    assert (
        by_id["selected_evidence_arithmetic"]["semantic_effect"]
        == "denominator_or_window_policy"
    )
    assert by_id["benchmark_convention_renderer"]["portability_category"] == (
        "benchmark_format"
    )
    assert by_id["benchmark_convention_renderer"]["default_policy"] == "review_required"

    condition = artifact["condition_ladder"]["selected_evidence_arithmetic_only"]
    assert condition["family_id"] == "selected_evidence_arithmetic"
    assert condition["changed_from_raw"] == 57
    assert condition["semantic_kind_transitions"] == 16
    assert condition["raw_correct_to_condition_wrong"] == 1


def test_h5_inventory_writes_json_and_report(tmp_path: Path) -> None:
    artifact = h5_semantic_repair_inventory.build_h5_semantic_repair_inventory(
        _replacement_ablation()
    )
    json_path = tmp_path / "inventory.json"
    report_path = tmp_path / "inventory.md"

    h5_semantic_repair_inventory.write_h5_inventory_outputs(
        artifact,
        json_path=json_path,
        markdown_path=report_path,
    )

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["artifact_kind"] == "gan2026_h5_semantic_repair_inventory_v0"
    report = report_path.read_text(encoding="utf-8")
    assert "H5 Semantic Repair Inventory" in report
    assert "Locked-test row-level artifacts used: `0`" in report
    assert "`benchmark_convention_renderer`" in report


def test_h5_family_ablation_interprets_saved_ladder_without_new_policy() -> None:
    inventory = h5_semantic_repair_inventory.build_h5_semantic_repair_inventory(
        _replacement_ablation()
    )

    artifact = h5_semantic_repair_inventory.build_h5_repair_family_ablation(
        inventory
    )

    assert artifact["artifact_kind"] == "gan2026_h5_repair_family_ablation_v0"
    assert artifact["locked_test_row_level_artifacts_used"] == 0
    by_family = {item["family_id"]: item for item in artifact["family_ablation"]}
    assert by_family["format_only_prediction_surface"]["decision"] == "keep_allowed"
    assert by_family["selected_evidence_arithmetic"]["decision"] == "revise_or_bound"
    assert by_family["selected_evidence_arithmetic"]["raw_correct_to_wrong"] == 1
    assert by_family["benchmark_convention_renderer"]["decision"] == "review_required"
    assert by_family["benchmark_convention_renderer"]["changed_from_raw"] == 28
    assert by_family["benchmark_convention_renderer"]["semantic_kind_transitions"] == 15


def _replacement_ablation() -> dict[str, object]:
    return {
        "split_manifest": "gan2026_split_v1",
        "conditions": [
            _condition(
                "format_only_repair",
                changed=7,
                exact=7,
                pragmatic=0,
                purist=0,
                semantic=0,
                wtc=0,
                ctw=0,
            ),
            _condition(
                "selected_evidence_arithmetic_only",
                changed=57,
                exact=57,
                pragmatic=32,
                purist=36,
                semantic=16,
                wtc=32,
                ctw=1,
            ),
            _condition(
                "full_stack",
                changed=28,
                exact=28,
                pragmatic=24,
                purist=24,
                semantic=15,
                wtc=16,
                ctw=0,
            ),
        ],
    }


def _condition(
    condition: str,
    *,
    changed: int,
    exact: int,
    pragmatic: int,
    purist: int,
    semantic: int,
    wtc: int,
    ctw: int,
) -> dict[str, object]:
    return {
        "condition": condition,
        "repair_attribution": {
            "changed_from_raw": changed,
            "exact_normalized_label_transitions": exact,
            "pragmatic_category_transitions": pragmatic,
            "purist_category_transitions": purist,
            "semantic_kind_transitions": semantic,
            "raw_wrong_to_condition_correct": wtc,
            "raw_correct_to_condition_wrong": ctw,
        },
    }
