from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DEFAULT_SPLIT_MANIFEST,
)
from scripts import check_exectv2_joint_bounded_policy_replay as joint_check


def test_joint_candidate_must_dominate_fallback_on_all_direction_counts() -> None:
    joint = {
        "wrong_to_correct": 172,
        "correct_to_wrong": 3,
        "changed_still_wrong": 108,
    }
    fallback = {
        "wrong_to_correct": 161,
        "correct_to_wrong": 9,
        "changed_still_wrong": 108,
    }

    assert joint_check._direction_dominates(joint, fallback) is True
    assert joint_check._direction_dominates(
        {**joint, "correct_to_wrong": 9}, fallback
    ) is False
    assert joint_check._direction_dominates(
        {**joint, "wrong_to_correct": 161}, fallback
    ) is False


def test_joint_replay_artifact_is_dev_only_and_compares_three_policies() -> None:
    artifact = json.loads(
        Path(
            "experiments/exectv2_joint_bounded_policy_replay_dev140_20260715.json"
        ).read_text(encoding="utf-8")
    )
    manifest = json.loads(DEFAULT_SPLIT_MANIFEST.read_text(encoding="utf-8"))
    dev_ids = set(manifest["splits"]["dev"]["letter_ids"])
    test_ids = set(manifest["splits"]["test"]["letter_ids"])
    retained_ids = {str(row["letter_id"]) for row in artifact["rows"]}

    assert artifact["split"] == "dev140"
    assert artifact["new_model_calls"] == 0
    assert set(artifact["policies"]) == {"current", "implemented_fallback", "joint"}
    assert retained_ids <= dev_ids
    assert retained_ids.isdisjoint(test_ids)
    assert {row["evidence_status"] for row in artifact["rows"]} == {"exact"}
    assert artifact["gates"]["component_identity"]["status"] == "pass"
