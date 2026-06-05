from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    h9_action_policy_sidecars,
)


def test_action_summary_sidecar_reports_coverage_burden_and_family_rates() -> None:
    rows = [
        _assembled_row(
            1,
            candidate_action="predict",
            original_action="predict",
            owner="deterministic_adapter",
            families=["family_a"],
            correct=True,
        ),
        _assembled_row(
            2,
            candidate_action="abstain",
            original_action="abstain",
            owner="safety_floor",
            families=["family_a"],
            correct=None,
        ),
        _assembled_row(
            3,
            candidate_action="predict",
            original_action="human_review",
            owner="deterministic_comparator_fallback",
            families=[],
            correct=True,
            release_applied=True,
            transition="C_to_review",
        ),
    ]

    summary = h9_action_policy_sidecars.build_action_summary_sidecar(
        {"control": rows}
    )

    candidate = summary["candidates"][0]
    assert candidate["prediction_bearing_coverage"] == 2 / 3
    assert candidate["abstain_rows"] == 1
    assert candidate["review_rows"] == 0
    assert candidate["release_lane_counts"] == {"human_review": 1}
    assert candidate["fallback_owner_counts"] == {"deterministic_comparator_fallback": 1}
    family_a = {row["family"]: row for row in candidate["family_action_rates"]}[
        "family_a"
    ]
    assert family_a["rows"] == 2
    assert family_a["nonprediction_rows"] == 1
    assert summary["decision"] == "h9_action_summary_sidecar_v1_complete"


def test_release_lane_ablation_releases_one_lane_at_a_time() -> None:
    rows = [
        _assembled_row(
            1,
            candidate_action="predict",
            original_action="abstain",
            owner="deterministic_comparator_fallback",
            correct=True,
            release_applied=True,
            transition="C_to_abstain",
            h6_member=False,
        ),
        _assembled_row(
            2,
            candidate_action="predict",
            original_action="human_review",
            owner="deterministic_comparator_fallback",
            correct=False,
            release_applied=True,
            transition="W_to_review",
            h6_member=True,
        ),
    ]

    summary = h9_action_policy_sidecars.build_release_lane_ablation(rows)
    lanes = {row["release_lane"]: row for row in summary["lanes"]}

    assert lanes["abstain"]["release_rows"] == 1
    assert lanes["abstain"]["w_to_c_rows"] == 1
    assert lanes["abstain"]["c_to_w_rows"] == 0
    assert lanes["human_review"]["h6_control_rows"] == 1
    assert lanes["human_review"]["h6_regression_rows"] == 1
    assert summary["decision"] == "h9_release_lane_ablation_v1_rejected_or_narrow"


def test_h6_control_replay_requires_no_regression_for_every_candidate() -> None:
    replay = h9_action_policy_sidecars.build_h6_control_replay(
        {
            "candidate_a": {
                "h6_control_rows": 2,
                "h6_control_regression_rows": 0,
                "release_correct_rows": 3,
                "release_wrong_rows": 0,
            },
            "candidate_b": {
                "h6_control_rows": 1,
                "h6_control_regression_rows": 1,
                "release_correct_rows": 1,
                "release_wrong_rows": 1,
            },
        }
    )

    assert replay["candidates"][0]["changed_label_precision"] == 1.0
    assert replay["candidates"][1]["changed_label_precision"] == 0.5
    assert replay["decision"] == "h6_control_replay_v1_failed"


def _assembled_row(
    source_row_index: int,
    *,
    candidate_action: str,
    original_action: str,
    owner: str,
    correct: bool | None,
    families: list[str] | None = None,
    release_applied: bool = False,
    transition: str = "C_to_C",
    h6_member: bool = False,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "split_manifest": "gan2026_split_v1",
        "candidate_version": "test_candidate",
        "candidate_action": candidate_action,
        "original_staged_action": original_action,
        "component_owner": owner,
        "hidden_families": families or [],
        "candidate_purist_correct": correct,
        "release_applied": release_applied,
        "release_eligible": release_applied,
        "baseline_transition": transition,
        "h6_member": h6_member,
        "h6_panel_role": "control" if h6_member else "",
    }
