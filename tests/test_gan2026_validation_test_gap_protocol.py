from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = (
    ROOT / ""
)
HYPOTHESIS_REGISTRY_PATH = (
    ROOT / "experiments/gan2026_validation_test_gap_hypothesis_registry_2026-06-05.json"
)
ARTIFACT_INVENTORY_PATH = (
    ROOT / "experiments/gan2026_validation_test_gap_artifact_inventory_2026-06-05.json"
)


def test_gap_protocol_blocks_locked_test_row_level_tuning() -> None:
    protocol = PROTOCOL_PATH.read_text()

    assert "Do not inspect locked-test row-level failures" in protocol
    assert "aggregate summaries and predeclared-slice summaries" in protocol
    assert (
        "No first-wave analysis should introduce a new prediction-bearing architecture"
        in protocol
    )


def test_gap_hypothesis_registry_is_complete_and_machine_readable() -> None:
    registry = json.loads(HYPOTHESIS_REGISTRY_PATH.read_text())

    assert registry["split_manifest"] == "gan2026_split_v1"
    hypothesis_ids = [item["id"] for item in registry["hypotheses"]]
    assert hypothesis_ids == [f"H{number}" for number in range(1, 11)]
    for hypothesis in registry["hypotheses"]:
        assert hypothesis["name"]
        assert hypothesis["hypothesis"]
        assert hypothesis["primary_signal"]
        assert hypothesis["revise_if"]
        assert hypothesis["initial_surface"]


def test_gap_artifact_inventory_declares_provenance_and_safe_inspection() -> None:
    inventory = json.loads(ARTIFACT_INVENTORY_PATH.read_text())
    registry = json.loads(HYPOTHESIS_REGISTRY_PATH.read_text())
    valid_hypothesis_ids = {item["id"] for item in registry["hypotheses"]}

    assert inventory["split_manifest"] == "gan2026_split_v1"
    assert inventory["protocol"] == PROTOCOL_PATH.relative_to(ROOT).as_posix()
    assert inventory["artifacts"]

    for artifact in inventory["artifacts"]:
        assert artifact["artifact_id"]
        assert artifact["candidate_name"]
        assert artifact["pipeline_family"]
        assert artifact["distribution"]
        assert artifact["paths"]
        assert artifact["artifact_role"]
        assert artifact["replay_status"]
        assert artifact["score_layers_available"]
        assert artifact["allowed_inspection"]
        assert set(artifact["hypothesis_ids"]).issubset(valid_hypothesis_ids)

        if artifact["distribution"] == "locked_test450":
            assert artifact["allowed_inspection"] in {
                "locked_test_aggregate_only",
                "locked_test_predeclared_slice_only",
            }
            assert "row_level" not in artifact["allowed_inspection"]
