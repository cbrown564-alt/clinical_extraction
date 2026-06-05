from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid import (
    staged_assembly_v1,
)


def _control_row(source_row_index: int = 101, **overrides):
    row = {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "gold_label": "1 per month",
        "candidate_action": "predict",
        "candidate_label": "1 per month",
        "candidate_purist_correct": True,
        "fallback_label": "unknown",
        "fallback_label_source": "deterministic_comparator",
        "baseline_purist_correct": False,
        "baseline_transition": "W_to_C",
        "component_owner": "deterministic_adapter",
        "hidden_families": ["seizure_free_duration"],
        "first_failure_owner": "state_graph_projection",
        "first_failure_reason": "unknown_boundary",
        "selected_evidence_exact": True,
        "selected_source_ids_exist": True,
        "parse_issue_count": 0,
        "evidence_issue_count": 0,
        "schema_issue_count": 0,
        "release_applied": False,
        "release_wrong_rows": 0,
        "router_action": "predict",
        "h6_member": False,
    }
    row.update(overrides)
    return row


def _boundary_row(source_row_index: int = 101, **overrides):
    row = {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "selector_action": "select",
        "selector_reason": "selector_precision_pass",
        "component_owner": "typed_boundary_classifier",
        "effect_class": "clinical_boundary_projection",
        "target_family": "seizure_free_duration",
        "target_mechanism": "seizure_free_boundary_event_v0",
        "proposed_label": "1 per month",
        "transition": "W_to_C",
        "exact_evidence": True,
        "final_label_policy_connected": False,
        "projection_policy": {"projection_policy_id": "seizure_free_boundary_event_v0"},
    }
    row.update(overrides)
    return row


def test_v1_final_rows_overlay_selected_boundary_attribution_without_label_churn():
    rows, metadata = staged_assembly_v1.build_saved_replay_validation_rows(
        [_control_row()],
        boundary_rows=[_boundary_row()],
        sidecar_summaries={
            "h6_control_replay_v1": {"decision": "h6_control_replay_v1_passed"},
            "h9_release_lane_ablation_v1": {"release_wrong_rows": 0},
        },
    )

    assert metadata["candidate_version"] == (
        "hybrid_multi_component_staged_assembly_v1"
    )
    assert metadata["metrics"]["row_count"] == 1
    assert metadata["metrics"]["boundary_selected_rows"] == 1
    assert rows[0]["final_label"] == "1 per month"
    assert rows[0]["component_owner"] == "typed_boundary_classifier"
    assert rows[0]["base_component_owner"] == "deterministic_adapter"
    assert rows[0]["boundary_selector_action"] == "select"
    assert rows[0]["boundary_policy_id"] == "seizure_free_boundary_event_v0"
    assert rows[0]["repair_policy_id"] == "h5_repair_policy_v1"
    assert rows[0]["source_id_valid"] is True


def test_v1_suppressed_boundary_rows_keep_base_owner():
    rows, metadata = staged_assembly_v1.build_saved_replay_validation_rows(
        [_control_row()],
        boundary_rows=[
            _boundary_row(
                selector_action="suppress",
                selector_reason="unknown_no_reference_sentinel_churn",
                selected_for_ablation=False,
            )
        ],
    )

    assert metadata["metrics"]["boundary_suppressed_rows"] == 1
    assert rows[0]["component_owner"] == "deterministic_adapter"
    assert rows[0]["boundary_selector_action"] == "suppress"
    assert rows[0]["boundary_suppression_reason"] == (
        "unknown_no_reference_sentinel_churn"
    )


def test_v1_contract_pins_unique_validation_rows_and_changed_evidence():
    rows, _ = staged_assembly_v1.build_saved_replay_validation_rows(
        [
            _control_row(101),
            _control_row(
                202,
                candidate_label="unknown",
                fallback_label="unknown",
                baseline_purist_correct=True,
                baseline_transition="C_to_C",
                h6_member=True,
            ),
        ],
        boundary_rows=[_boundary_row(101)],
    )

    assert staged_assembly_v1.validate_final_row_contract(rows, expected_rows=2) == []

    rows[0]["selected_evidence_exact"] = False
    assert "changed_prediction_row_without_exact_evidence" in (
        staged_assembly_v1.validate_final_row_contract(rows, expected_rows=2)
    )


def test_v1_component_matrix_matches_candidate_rows():
    rows, _ = staged_assembly_v1.build_saved_replay_validation_rows(
        [_control_row(), _control_row(202, candidate_action="abstain")]
    )

    matrix_rows = staged_assembly_v1.build_component_matrix_rows(rows)
    summary = staged_assembly_v1.summarize_component_matrix(matrix_rows, rows)

    assert len(matrix_rows) == len(rows)
    assert matrix_rows[0]["candidate_name"] == (
        "hybrid_multi_component_staged_assembly_v1"
    )
    assert matrix_rows[0]["clinical_subproblem"] == "seizure_free_duration"
    assert summary["contract_issues"] == []
