from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DEFAULT_SPLIT_MANIFEST,
)
from scripts import check_exectv2_prescription_bounded_policy_candidate as candidate_check


def _record(index: int, direction: str) -> dict[str, object]:
    model_correct = direction in {"correct_to_wrong", "changed_still_correct"}
    final_correct = direction in {"wrong_to_correct", "changed_still_correct"}
    return {
        "model_label": "model",
        "family": "Prescription",
        "letter_id": f"DEV-{index}",
        "family_local_change_direction": direction,
        "family_local_model_owned_correct": model_correct,
        "family_local_final_correct": final_correct,
        "evidence_status": "exact",
        "deterministic_actions": [],
    }


def test_bounded_candidate_gate_requires_demonstrated_rescue_identities() -> None:
    comparator = [_record(index, "wrong_to_correct") for index in range(41)]
    candidate = [_record(index, "wrong_to_correct") for index in range(39)]
    changed_rows: list[dict[str, object]] = []
    required = {
        ("model", "EA0096"),
        ("model", "EA0127"),
        ("model", "EA0150"),
    }

    gates = candidate_check._evaluate_gates(
        comparator,
        candidate,
        changed_rows,
        diagnostics_match=True,
        required_rescues=required,
    )

    assert gates["checks"]["retain_all_demonstrated_missing_regimen_rescues"] is False
    assert gates["status"] == "fail"


def test_bounded_candidate_artifact_is_dev_only_and_records_all_ablations() -> None:
    artifact = json.loads(
        Path(
            "experiments/exectv2_prescription_bounded_policy_candidate_dev140_20260715.json"
        ).read_text(encoding="utf-8")
    )
    manifest = json.loads(DEFAULT_SPLIT_MANIFEST.read_text(encoding="utf-8"))
    dev_ids = set(manifest["splits"]["dev"]["letter_ids"])
    test_ids = set(manifest["splits"]["test"]["letter_ids"])
    retained_ids = {str(row["letter_id"]) for row in artifact["rows"]}

    assert artifact["split"] == "dev140"
    assert artifact["new_model_calls"] == 0
    assert set(artifact["ablations"]) == set(candidate_check.PRESCRIPTION_VARIANTS)
    assert retained_ids <= dev_ids
    assert retained_ids.isdisjoint(test_ids)
    assert {row["family"] for row in artifact["rows"]} == {"Prescription"}
    assert {row["evidence_status"] for row in artifact["rows"]} == {"exact"}
    assert artifact["fallback_reference"]["candidate_id"] == (
        "decision_0040_model_preserving_dev140_v1"
    )
