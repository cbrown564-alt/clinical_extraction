from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    selective_abstention_pressure,
)


def test_selective_abstention_pressure_assigns_review_lanes() -> None:
    rows = [
        {
            "source_row_index": 101,
            "final_action": "abstain",
            "decision_reason": "trigger_conditioned_frequency",
            "gold_label": "unknown",
            "blocked_candidate_label": "1 per week",
            "blocked_candidate_purist_correct": True,
        },
        {
            "source_row_index": 102,
            "final_action": "abstain",
            "decision_reason": "trigger_conditioned_frequency",
            "gold_label": "unknown",
            "blocked_candidate_label": "1 per day",
            "blocked_candidate_purist_correct": False,
        },
        {
            "source_row_index": 103,
            "final_action": "human_review",
            "decision_reason": "last_event_boundary",
            "gold_label": "unknown",
            "blocked_candidate_label": "seizure free for 4 month",
            "blocked_candidate_purist_correct": False,
        },
        {
            "source_row_index": 104,
            "final_action": "abstain",
            "decision_reason": "missing_denominator_anchor",
            "gold_label": "unknown",
            "blocked_candidate_label": "no seizure frequency reference",
            "blocked_candidate_purist_correct": True,
        },
        {
            "source_row_index": 105,
            "final_action": "abstain",
            "decision_reason": "trigger_conditioned_frequency",
            "gold_label": "unknown",
            "blocked_candidate_label": "unknown",
            "blocked_candidate_purist_correct": True,
        },
    ]

    reviewed = selective_abstention_pressure.build_pressure_review_rows(rows)

    assert [row["review_lane"] for row in reviewed] == [
        "trigger_release_candidate",
        "keep_nonprediction",
        "date_policy_needed",
        "anchor_policy_needed",
        "trigger_sentinel_boundary_review",
    ]
    assert [row["pressure_class"] for row in reviewed] == [
        "coverage_cost",
        "protective_block",
        "protective_block",
        "coverage_cost",
        "coverage_cost",
    ]


def test_selective_abstention_pressure_summary_keeps_claim_boundary() -> None:
    reviewed = selective_abstention_pressure.build_pressure_review_rows(
        [
                {
                    "source_row_index": 101,
                    "final_action": "abstain",
                    "decision_reason": "trigger_conditioned_frequency",
                    "blocked_candidate_label": "1 per week",
                    "blocked_candidate_purist_correct": True,
                },
            {
                "source_row_index": 102,
                "final_action": "abstain",
                "decision_reason": "trigger_conditioned_frequency",
                "blocked_candidate_purist_correct": False,
            },
        ]
    )

    summary = selective_abstention_pressure.summarize_pressure_review(reviewed)

    assert summary["row_count"] == 2
    assert summary["pressure_class_counts"] == {
        "coverage_cost": 1,
        "protective_block": 1,
    }
    assert summary["review_lane_counts"] == {
        "keep_nonprediction": 1,
        "trigger_release_candidate": 1,
    }
    assert summary["recommended_next_step"] == (
        "Predeclare a gold-blinded trigger-context release rule and a frozen "
        "last-event date policy before changing prediction-bearing behavior."
    )
    assert "development accounting only" in summary["claim_language"]
