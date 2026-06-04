from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    abstention_policy_predeclaration,
)


def test_abstention_policy_predeclaration_counts_policy_lanes() -> None:
    pressure_rows = [
        {
            "source_row_index": 101,
            "review_lane": "trigger_release_candidate",
            "decision_reason": "trigger_conditioned_frequency",
            "blocked_candidate_label": "1 per week",
        },
        {
            "source_row_index": 102,
            "review_lane": "trigger_sentinel_boundary_review",
            "decision_reason": "trigger_conditioned_frequency",
            "blocked_candidate_label": "unknown",
        },
        {
            "source_row_index": 103,
            "review_lane": "date_policy_needed",
            "decision_reason": "last_event_boundary",
            "blocked_candidate_label": "seizure free for 4 month",
        },
    ]

    predeclaration = abstention_policy_predeclaration.build_predeclaration(
        pressure_rows
    )

    assert predeclaration["policy_name"] == (
        "gan2026_staged_hybrid_abstention_policy_predeclaration_v0"
    )
    assert predeclaration["lane_counts"] == {
        "date_policy_needed": 1,
        "trigger_release_candidate": 1,
        "trigger_sentinel_boundary_review": 1,
    }
    assert predeclaration["candidate_behavior_change_counts"] == {
        "direct_trigger_release_candidates": 1,
        "last_event_automatic_release_candidates": 0,
    }
    assert predeclaration["rules"][0]["portability"] == "seizure_frequency"
    assert predeclaration["rules"][1]["portability"] == "seizure_frequency"


def test_abstention_policy_predeclaration_writes_report(tmp_path) -> None:
    predeclaration = abstention_policy_predeclaration.build_predeclaration([])
    report_path = tmp_path / "predeclaration.md"
    json_path = tmp_path / "predeclaration.json"

    abstention_policy_predeclaration.write_summary_json(predeclaration, json_path)
    abstention_policy_predeclaration.write_report(
        predeclaration,
        report_path,
        json_path=json_path,
    )

    report = report_path.read_text()
    assert json_path.exists()
    assert "Gold-Blinded Release Criteria" in report
    assert "does not change prediction-bearing behavior" in report
