import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reset_stage_component_inventory,
)


def test_inventory_tracks_portability_stage_and_status() -> None:
    artifact = reset_stage_component_inventory.build_reset_stage_component_inventory()

    assert artifact["artifact_kind"] == "gan2026_reset_stage_component_inventory_v0"
    assert artifact["split_manifest"] == "gan2026_split_v1"
    assert artifact["summary"]["component_families"] >= 10
    assert artifact["summary"]["by_stage"]["normalize"] >= 3
    assert artifact["summary"]["by_status"]["ported_v6"] >= 3

    by_family = {row["new_family"]: row for row in artifact["inventory"]}
    assert by_family["diary_date_list_frequency_recovery"]["portability_category"] == (
        "gan2026_specific"
    )
    assert by_family["selected_evidence_missing_exact_trace"][
        "portability_category"
    ] == "general"
    assert by_family["anchor_window_frequency_value_recovery"][
        "ablation_switch"
    ] == "normalize_frequency_anchor_window_value_recovery"
    assert by_family["multi_month_bucket_frequency_value_recovery"][
        "ablation_switch"
    ] == "normalize_frequency_multi_month_bucket_value_recovery"
    assert by_family["named_comparator_preservation_action_policy"]["status"] == (
        "pending_policy_decision"
    )
    assert by_family["do_not_port_broad_hybrid_fallback"]["status"] == (
        "retired_do_not_port"
    )


def test_inventory_writes_json_and_markdown(tmp_path: Path) -> None:
    artifact = reset_stage_component_inventory.build_reset_stage_component_inventory()
    json_path = tmp_path / "inventory.json"
    markdown_path = tmp_path / "inventory.md"

    reset_stage_component_inventory.write_reset_stage_component_inventory_outputs(
        artifact,
        json_path=json_path,
        markdown_path=markdown_path,
    )

    saved = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved["artifact_kind"] == "gan2026_reset_stage_component_inventory_v0"
    report = markdown_path.read_text(encoding="utf-8")
    assert "Gan 2026 Reset-Stage Component Inventory" in report
    assert "`selected_evidence_missing_exact_trace`" in report
    assert "`retired_do_not_port`" in report
