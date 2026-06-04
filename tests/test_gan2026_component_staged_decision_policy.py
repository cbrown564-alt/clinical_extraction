from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    staged_decision_policy,
)


def _assembly_row(selective_action: str = "predict") -> dict:
    return {
        "source_row_index": 101,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "gold_label": "1 per month",
        "component_presence": {
            "hybrid_reasoner_replay": True,
            "selective_safety_floor_gate_v0": True,
            "rq9_selective_action_router_v3": True,
        },
        "hybrid_reasoner_replay": {
            "component_status": {
                "selected_evidence_exactness": "ok",
                "source_id_trace": "ok",
            },
            "score_layer": {
                "final_label": "1 per month",
                "purist_correct": True,
                "pragmatic_correct": True,
            },
        },
        "selective_safety_floor_gate_v0": {
            "selected_evidence_exact": True,
            "selected_source_ids_exist": True,
            "gate_variants": {
                "combined_selective_gate_v0": {
                    "final_label": "1 per month",
                    "changed": True,
                }
            },
        },
        "rq9_selective_action_router_v3": {
            "selective_action": selective_action,
            "final_label": "1 per month" if selective_action == "predict" else None,
            "primary_reason": "plain_predictable_frequency",
            "secondary_reasons": [],
            "source_candidate": {
                "final_label": "1 per month",
                "selected_evidence": "one seizure a month",
                "selected_source_ids": ["det:event_1"],
                "selected_evidence_exact": True,
                "purist_correct": True,
                "pragmatic_correct": True,
            },
        },
    }


def test_staged_decision_policy_predicts_only_router_predict_rows() -> None:
    decision = staged_decision_policy.build_decision_row(_assembly_row("predict"))

    assert decision["final_action"] == "predict"
    assert decision["prediction_bearing"] is True
    assert decision["prediction_label"] == "1 per month"
    assert decision["selected_evidence"] == "one seizure a month"
    assert decision["selected_source_ids"] == ["det:event_1"]
    assert decision["verifier_used"] is False


def test_staged_decision_policy_keeps_abstain_non_prediction() -> None:
    decision = staged_decision_policy.build_decision_row(_assembly_row("abstain"))

    assert decision["final_action"] == "abstain"
    assert decision["prediction_bearing"] is False
    assert decision["prediction_label"] is None
    assert decision["selected_evidence"] is None
    assert decision["decision_reason"] == "plain_predictable_frequency"


def test_staged_decision_policy_summarizes_decision_rows() -> None:
    decisions = staged_decision_policy.build_decision_rows(
        [
            _assembly_row("predict"),
            _assembly_row("abstain"),
            _assembly_row("human_review"),
        ]
    )
    summary = staged_decision_policy.summarize_decision_rows(decisions)

    assert summary["row_count"] == 3
    assert summary["prediction_bearing_rows"] == 1
    assert summary["non_prediction_rows"] == 2
    assert summary["action_counts"] == {
        "abstain": 1,
        "human_review": 1,
        "predict": 1,
    }
    assert summary["selective_purist_accuracy"] == 1.0
    assert summary["verifier_rows_used"] == 0
