from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    residual_nonprediction_audit,
)


def test_residual_nonprediction_audit_joins_blocked_source_candidate() -> None:
    decision_rows = [
        {
            "source_row_index": 101,
            "final_action": "abstain",
            "prediction_bearing": False,
            "decision_reason": "trigger_conditioned_frequency",
            "gold_label": "unknown",
        },
        {
            "source_row_index": 102,
            "final_action": "predict",
            "prediction_bearing": True,
            "decision_reason": "plain_predictable_frequency",
            "gold_label": "1 per month",
        },
    ]
    assembly_rows = [
        {
            "source_row_index": 101,
            "rq9_selective_action_router_v3": {
                "source_candidate": {
                    "final_label": "no seizure frequency reference",
                    "purist_correct": True,
                    "pragmatic_correct": True,
                    "selected_evidence": "only with missed medicines",
                    "selected_source_ids": ["graph:sg-001"],
                }
            },
        }
    ]

    audit_rows = residual_nonprediction_audit.build_residual_nonprediction_rows(
        decision_rows,
        assembly_rows,
    )

    assert audit_rows == [
        {
            "artifact_kind": "gan2026_residual_nonprediction_audit_row",
            "source_row_index": 101,
            "final_action": "abstain",
            "decision_reason": "trigger_conditioned_frequency",
            "secondary_reasons": [],
            "gold_label": "unknown",
            "blocked_candidate_label": "no seizure frequency reference",
            "blocked_candidate_purist_correct": True,
            "blocked_candidate_pragmatic_correct": True,
            "blocked_candidate_evidence": "only with missed medicines",
            "blocked_candidate_source_ids": ["graph:sg-001"],
        }
    ]


def test_residual_nonprediction_audit_summary_counts_pressure() -> None:
    rows = [
        {
            "final_action": "abstain",
            "decision_reason": "trigger_conditioned_frequency",
            "gold_label": "unknown",
            "blocked_candidate_purist_correct": True,
        },
        {
            "final_action": "human_review",
            "decision_reason": "last_event_boundary",
            "gold_label": "1 per month",
            "blocked_candidate_purist_correct": False,
        },
    ]

    summary = residual_nonprediction_audit.summarize_residual_nonpredictions(rows)

    assert summary["row_count"] == 2
    assert summary["action_counts"] == {"abstain": 1, "human_review": 1}
    assert summary["reason_counts"] == {
        "last_event_boundary": 1,
        "trigger_conditioned_frequency": 1,
    }
    assert summary["blocked_correct_rows"] == 1
    assert summary["blocked_wrong_rows"] == 1
    assert summary["non_unknown_gold_rows"] == 1
    assert summary["recommended_next_step"] == (
        "Run a selective abstention-pressure review before full-validation "
        "verifier use or promotion."
    )
