from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DEFAULT_SPLIT_MANIFEST,
)
from scripts import check_exectv2_model_preserving_policy_candidate as candidate_check


def _record(index: int, direction: str) -> dict[str, object]:
    return {
        "model_label": "model",
        "family": "Diagnosis",
        "letter_id": f"DEV-{index}",
        "family_local_change_direction": direction,
        "evidence_status": "exact",
    }


def test_candidate_gate_does_not_hide_lost_rescues_behind_new_rescues() -> None:
    comparator = [_record(index, "wrong_to_correct") for index in range(160)]
    candidate = [_record(index, "wrong_to_correct") for index in range(143)]
    candidate.extend(
        _record(index, "wrong_to_correct") for index in range(160, 178)
    )

    gates = candidate_check._evaluate_gates(comparator, candidate)

    assert gates["family_local_directions"]["wrong_to_correct"] == 161
    assert gates["comparator_rescue_retention"] == {
        "comparator_rescues": 160,
        "retained": 143,
        "lost": 17,
    }
    assert gates["checks"]["total_wrong_to_correct_at_least_150"] is True
    assert gates["checks"]["lost_at_most_10_of_comparator_160_rescues"] is False
    assert gates["status"] == "fail"


def test_candidate_artifact_is_dev_only_and_records_rejection() -> None:
    artifact = json.loads(
        Path(
            "experiments/exectv2_model_preserving_policy_candidate_dev140_20260715.json"
        ).read_text(encoding="utf-8")
    )
    manifest = json.loads(DEFAULT_SPLIT_MANIFEST.read_text(encoding="utf-8"))
    dev_ids = set(manifest["splits"]["dev"]["letter_ids"])
    test_ids = set(manifest["splits"]["test"]["letter_ids"])
    retained_ids = {str(row["letter_id"]) for row in artifact["rows"]}

    assert artifact["split"] == "dev140"
    assert artifact["new_model_calls"] == 0
    assert artifact["decision"] == "reject"
    assert artifact["gates"]["status"] == "fail"
    assert retained_ids <= dev_ids
    assert retained_ids.isdisjoint(test_ids)
    assert {row["evidence_status"] for row in artifact["rows"]} == {"exact"}
