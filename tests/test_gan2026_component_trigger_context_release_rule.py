from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    trigger_context_release_rule,
)


def test_trigger_context_release_rule_releases_only_predeclared_lane() -> None:
    pressure_rows = [
        {
            "source_row_index": 101,
            "review_lane": "trigger_release_candidate",
            "blocked_candidate_label": "1 per week",
        },
        {
            "source_row_index": 102,
            "review_lane": "trigger_sentinel_boundary_review",
            "blocked_candidate_label": "unknown",
        },
    ]
    residual_rows = [
        {
            "source_row_index": 101,
            "blocked_candidate_label": "1 per week",
            "blocked_candidate_evidence": "seizure episodes occurring roughly weekly",
            "blocked_candidate_source_ids": ["det:event_1"],
            "blocked_candidate_purist_correct": True,
            "blocked_candidate_pragmatic_correct": True,
        },
        {
            "source_row_index": 102,
            "blocked_candidate_label": "unknown",
            "blocked_candidate_evidence": "only when tired",
            "blocked_candidate_source_ids": ["graph:sg-001"],
            "blocked_candidate_purist_correct": True,
            "blocked_candidate_pragmatic_correct": True,
        },
    ]

    release_rows = trigger_context_release_rule.build_release_rows(
        pressure_rows,
        residual_rows,
    )

    assert release_rows == [
        {
            "artifact_kind": "gan2026_trigger_context_release_rule_row",
            "source_row_index": 101,
            "release_decision": "release_as_prediction",
            "prediction_label": "1 per week",
            "selected_evidence": "seizure episodes occurring roughly weekly",
            "selected_source_ids": ["det:event_1"],
            "rule_name": "trigger_context_release_rule_v0",
            "release_reason": "predeclared_trigger_context_release_candidate",
            "development_accounting": {
                "purist_correct": True,
                "pragmatic_correct": True,
            },
        }
    ]


def test_trigger_context_release_rule_rejects_exclusive_trigger_wording() -> None:
    release_rows = trigger_context_release_rule.build_release_rows(
        [
            {
                "source_row_index": 101,
                "review_lane": "trigger_release_candidate",
                "blocked_candidate_label": "1 per week",
            }
        ],
        [
            {
                "source_row_index": 101,
                "blocked_candidate_label": "1 per week",
                "blocked_candidate_evidence": "only when sleep deprived",
                "blocked_candidate_source_ids": ["det:event_1"],
                "blocked_candidate_purist_correct": False,
                "blocked_candidate_pragmatic_correct": False,
            }
        ],
    )

    assert release_rows == []


def test_trigger_context_release_rule_applies_proposed_decisions() -> None:
    decision_rows = [
        {
            "source_row_index": 101,
            "final_action": "abstain",
            "prediction_bearing": False,
            "prediction_label": None,
            "selected_evidence": None,
            "selected_source_ids": [],
            "development_accounting": {
                "purist_correct": None,
                "pragmatic_correct": None,
            },
        }
    ]
    release_rows = [
        {
            "source_row_index": 101,
            "prediction_label": "1 per week",
            "selected_evidence": "seizure episodes occurring roughly weekly",
            "selected_source_ids": ["det:event_1"],
            "development_accounting": {
                "purist_correct": True,
                "pragmatic_correct": True,
            },
        }
    ]

    proposed = trigger_context_release_rule.apply_release_rows(
        decision_rows,
        release_rows,
    )
    summary = trigger_context_release_rule.summarize_proposed_decisions(proposed)

    assert proposed[0]["final_action"] == "predict"
    assert proposed[0]["prediction_bearing"] is True
    assert proposed[0]["prediction_label"] == "1 per week"
    assert proposed[0]["policy_name"] == (
        "gan2026_staged_decision_policy_v0_trigger_context_release_v0"
    )
    assert proposed[0]["release_rule_applied"] == "trigger_context_release_rule_v0"
    assert summary["released_rows"] == 1
    assert summary["prediction_bearing_rows"] == 1
    assert summary["selective_purist_accuracy"] == 1.0
