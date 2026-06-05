from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    component_evidence_matrix,
)


def test_component_evidence_matrix_flattens_candidate_contract_fields() -> None:
    assembly_rows = [
        {
            "source_row_index": 101,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "selective_safety_floor_gate_v0": {
                "baseline_label": "unknown",
                "hidden_families": ["trigger_conditioned_frequency"],
                "first_failure_owner": "router",
                "first_failure_reason": "trigger boundary",
                "selected_source_ids_exist": True,
                "gate_variants": {
                    "baseline_safety_floor_v2": {"purist_correct": False},
                    "selective_safety_floor_gate_v0": {
                        "changed": True,
                        "label_source": "selective_safety_floor_gate_v0",
                    },
                },
            },
            "hybrid_reasoner_replay": {
                "component_status": {"adapter_layer": "ok", "source_id_trace": "ok"}
            },
            "rq9_selective_action_router_v3": {
                "selective_action": "predict",
                "primary_reason": "plain_predictable_frequency",
            },
        }
    ]
    decision_rows = [
        {
            "source_row_index": 101,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "gold_label": "1 per month",
            "final_action": "predict",
            "prediction_bearing": True,
            "prediction_label": "1 per month",
            "selected_evidence_exact": True,
            "selected_source_ids_exist": True,
            "development_accounting": {"purist_correct": True},
            "verifier_used": False,
        }
    ]
    trigger_rows = [
        {
            "source_row_index": 101,
            "release_decision": "release_as_prediction",
            "prediction_label": "1 per month",
        }
    ]
    last_event_rows = [
        {
            "source_row_index": 101,
            "duration_auditable": False,
            "release_blocker": "not_last_event_row",
        }
    ]

    rows = component_evidence_matrix.build_matrix_rows(
        assembly_rows,
        decision_rows,
        trigger_release_rows=trigger_rows,
        last_event_rows=last_event_rows,
    )

    assert rows[0]["candidate_version"] == "hybrid_multi_component_staged_assembly_v0"
    assert rows[0]["deterministic_comparator_label"] == "unknown"
    assert rows[0]["comparator_transition"] == "W_to_C"
    assert rows[0]["hidden_families"] == "trigger_conditioned_frequency"
    assert rows[0]["verifier_status"] == "not_run"
    assert rows[0]["trigger_release_status"] == "release_as_prediction"
    assert rows[0]["last_event_release_blocker"] == "not_last_event_row"
    assert rows[0]["reasoner_status"] == "adapter_layer:ok|source_id_trace:ok"


def test_component_evidence_matrix_summary_and_contract() -> None:
    rows = [
        {
            "source_row_index": 1,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "final_action": "predict",
            "prediction_bearing": True,
            "prediction_label": "1 per month",
            "selected_evidence_exact": True,
            "selected_source_ids_exist": True,
            "comparator_transition": "W_to_C",
            "verifier_status": "not_run",
            "trigger_release_status": "not_applicable",
            "last_event_duration_auditable": False,
            "parse_issue_count": 0,
            "evidence_issue_count": 0,
            "schema_issue_count": 0,
        },
        {
            "source_row_index": 2,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "final_action": "human_review",
            "prediction_bearing": False,
            "prediction_label": None,
            "selected_evidence_exact": None,
            "selected_source_ids_exist": None,
            "comparator_transition": "C_to_review",
            "verifier_status": "not_run",
            "trigger_release_status": "release_as_prediction",
            "last_event_duration_auditable": True,
            "parse_issue_count": 0,
            "evidence_issue_count": 0,
            "schema_issue_count": 0,
        },
    ]

    summary = component_evidence_matrix.summarize_matrix_rows(rows)
    issues = component_evidence_matrix.validate_matrix_contract(rows, expected_rows=2)

    assert summary["row_count"] == 2
    assert summary["transition_counts"] == {"C_to_review": 1, "W_to_C": 1}
    assert summary["trigger_release_rows"] == 1
    assert summary["last_event_duration_auditable_rows"] == 1
    assert issues == []


def test_component_evidence_matrix_contract_blocks_verifier_use() -> None:
    rows = [
        {
            "source_row_index": 1,
            "split": "validation",
            "split_manifest": "gan2026_split_v1",
            "prediction_bearing": True,
            "prediction_label": "unknown",
            "verifier_status": "used",
        }
    ]

    issues = component_evidence_matrix.validate_matrix_contract(rows, expected_rows=1)

    assert issues == ["verifier_used_without_full_validation_protocol"]
