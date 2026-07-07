from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    h9_action_policy_gap,
)


def test_h9_action_policy_gap_detects_validation_overblocking_and_test_shift() -> None:
    rows = [
        _final_row(1, owner="deterministic_adapter", correct=True),
        _final_row(2, owner="safety_floor", correct=None, families=["unknown_boundary"]),
        _final_row(3, owner="safety_floor", correct=None, families=["seizure_free_duration"]),
        _monitor_row(
            2,
            action="abstain",
            reason="trigger_conditioned_frequency",
            baseline_correct=True,
            families=["unknown_boundary"],
        ),
        _monitor_row(
            3,
            action="human_review",
            reason="last_event_boundary",
            baseline_correct=False,
            families=["seizure_free_duration"],
        ),
    ]
    test_nonprediction = {
        "inspection_policy": "aggregate_only_no_row_level_test_failure_inspection",
        "router_metrics": {
            "eligible_rows": 450,
            "abstained_rows": 1,
            "human_review_rows": 0,
            "coverage": 449 / 450,
            "selective_accuracy": 0.76,
        },
    }
    h1 = {
        "family_gaps": [
            {
                "family": "unknown_boundary",
                "test_rows": 57,
                "test_purist_proxy": 0.7368,
                "test_changed_rate": 0.1053,
                "validation_minus_test_gap": 0.1368,
            }
        ]
    }

    summary = h9_action_policy_gap.build_h9_action_policy_gap(
        rows,
        h1_summary=h1,
        test_nonprediction_summary=test_nonprediction,
    )

    assert summary["hypothesis_id"] == "H9"
    assert summary["decision"] == (
        "h9_partially_supported_action_policy_shift_not_primary_gap_explanation"
    )
    assert summary["validation"]["overall"]["nonprediction_rows"] == 2
    assert summary["validation"]["overall"]["blocked_baseline_correct_rows"] == 1
    assert summary["locked_test"]["router_metrics"]["nonprediction_rows"] == 1
    assert summary["locked_test_row_level_artifacts_written"] == 0


def test_h9_action_policy_gap_summarizes_family_and_owner_rates() -> None:
    rows = [
        _final_row(1, owner="deterministic_adapter", correct=True, families=["family_a"]),
        _final_row(2, owner="safety_floor", correct=None, families=["family_a"]),
        _final_row(3, owner="safety_floor", correct=None, families=["family_b"]),
        _monitor_row(
            2,
            action="abstain",
            reason="trigger_conditioned_frequency",
            baseline_correct=True,
            families=["family_a"],
        ),
    ]

    summary = h9_action_policy_gap.build_h9_action_policy_gap(rows)

    families = {row["family"]: row for row in summary["validation"]["by_hidden_family"]}
    owners = {row["component_owner"]: row for row in summary["validation"]["by_component_owner"]}
    assert families["family_a"]["rows"] == 2
    assert families["family_a"]["nonprediction_rows"] == 1
    assert families["family_b"]["nonprediction_rows"] == 0
    assert owners["deterministic_adapter"]["nonprediction_rows"] == 0
    assert owners["safety_floor"]["nonprediction_rows"] == 1


def _final_row(
    source_row_index: int,
    *,
    owner: str,
    correct: bool | None,
    families: list[str] | None = None,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "score_layer": "final_policy",
        "component_owner": owner,
        "purist_correct": correct,
        "split_manifest": "gan2026_split_v1",
        "hidden_families": families or [],
    }


def _monitor_row(
    source_row_index: int,
    *,
    action: str,
    reason: str,
    baseline_correct: bool,
    families: list[str] | None = None,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "score_layer": "abstain_review_monitor",
        "component_owner": "safety_floor",
        "abstain_review_monitor_action": action,
        "abstain_review_monitor_reason": reason,
        "baseline_purist_correct": baseline_correct,
        "split_manifest": "gan2026_split_v1",
        "hidden_families": families or [],
    }
