from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    suspicious_selected_state_routing,
)


def _saved_row() -> dict:
    note = (
        "Clinic Date: 01 January 2026. At present she has seizures only after "
        "missed medication doses."
    )
    return {
        "source_row_index": 501,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "reference": {"gold_normalized_label": "unknown"},
        "typed_input": {"note_text": note},
        "policy_replay": {"revised_deterministic_projected_label": "2 per month"},
        "structured_record": {
            "selected_state": {
                "state_kind": "frequency",
                "selected_evidence": (
                    "At present she has seizures only after missed medication doses."
                ),
                "currentness": "current",
                "assertion_status": "asserted",
                "applies_to": "seizures",
                "raw_model_label_hint": "2 per month",
                "raw_source_phrase": "seizures only after missed medication doses",
                "selection_reason": "Selected current seizure statement.",
                "ambiguity_flags": [],
                "rate": {
                    "count_low": 2.0,
                    "count_high": None,
                    "count_is_multiple": False,
                    "rate_time_basis_known": True,
                    "time_count_low": 1.0,
                    "time_count_high": None,
                    "time_unit": "month",
                    "rate_text": "2 per month",
                },
                "cluster": {"has_cluster_pattern": False},
                "seizure_free_boundary": {"has_no_event_claim": False},
                "conditionality_note": "only after missed medication doses",
                "competing_state_summary": "",
            }
        },
    }


def test_suspicious_routing_routes_exclusive_conditional_frequency_to_unknown() -> None:
    rows, metadata = suspicious_selected_state_routing.build_suspicious_routing_rows(
        [_saved_row()],
        panel_rows=[
            {
                "source_row_index": 501,
                "hidden_families": ["unknown_boundary"],
            }
        ],
    )

    row = rows[0]
    assert row["suspicious_state_action"] == "route_unknown"
    assert "frequency_with_exclusive_conditionality" in row["suspicious_state_flags"]
    assert row["final_policy_under_test"]["label"] == "unknown"
    assert row["comparison"]["w_to_c_against_comparator"] is True
    assert metadata["metrics"]["w_to_c_against_comparator_rows"] == 1
    assert metadata["by_hidden_family"]["unknown_boundary"]["route_unknown_rows"] == 1


def test_suspicious_routing_routes_missing_exact_trace_to_review() -> None:
    saved = _saved_row()
    saved["structured_record"]["selected_state"]["selected_evidence"] = "not in the note"

    rows, metadata = suspicious_selected_state_routing.build_suspicious_routing_rows(
        [saved]
    )

    row = rows[0]
    assert row["suspicious_state_action"] == "route_review"
    assert "selected_evidence_missing_exact_trace" in row["suspicious_state_flags"]
    assert row["final_policy_under_test"]["scorable"] is False
    assert row["llm_verifier_input"]["allowed_recommendations"] == [
        "render_as_selected_state",
        "render_as_unknown",
        "abstain_review",
        "choose_listed_competing_hypothesis",
    ]
    assert metadata["metrics"]["route_review_rows"] == 1


def test_suspicious_routing_routes_invalid_source_id_trace_to_review() -> None:
    saved = _saved_row()
    saved["structured_record"]["selected_source_ids"] = []
    saved["structured_record"]["source_id_status"] = "invalid"

    rows, _metadata = suspicious_selected_state_routing.build_suspicious_routing_rows(
        [saved]
    )

    row = rows[0]
    assert row["selected_evidence_status"]["exact_trace"] is True
    assert row["selected_evidence_status"]["source_id_status"] == "invalid"
    assert "selected_source_id_invalid" in row["suspicious_state_flags"]
    assert row["suspicious_state_action"] == "route_review"
    assert row["first_failure_owner"] == "source_id_trace"
