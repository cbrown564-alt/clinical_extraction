from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_verifier_predeclaration,
)


def _routing_row(
    *,
    source_row_index: int = 101,
    action: str = "route_unknown",
    exact_trace: bool = True,
    delta: str = "C_to_W",
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "gold_label": "1 per month",
        "hidden_families": ["unknown_boundary"],
        "selected_evidence_status": {
            "exact_trace": exact_trace,
            "selected_evidence_present": True,
        },
        "selected_state": {
            "state_kind": "frequency",
            "selected_evidence": "Current seizures occur about once per month.",
            "competing_state_summary": "Recent seizure-free interval is also mentioned.",
        },
        "embedded_ambiguity_fields": {
            "competing_state_summary": "Recent seizure-free interval is also mentioned."
        },
        "deterministic_policy_label": "1 per month",
        "deterministic_policy_action": "render",
        "suspicious_state_action": action,
        "suspicious_state_flags": ["frequency_with_count_blocking_ambiguity"],
        "final_policy_under_test": {
            "action": action,
            "label": "unknown" if action == "route_unknown" else None,
            "scorable": action == "route_unknown",
        },
        "comparison": {
            "delta": delta,
            "comparator_correct": delta == "C_to_W",
            "final_policy_correct": delta in {"W_to_C", "C_to_C"},
        },
    }


def test_predeclaration_includes_exact_suspicious_rows_and_model_input_contract() -> None:
    rows, metadata = (
        selective_verifier_predeclaration.build_selective_verifier_predeclaration_rows(
            [_routing_row()]
        )
    )

    assert len(rows) == 1
    row = rows[0]
    model_input = row["verifier_model_input"]
    assert model_input["allowed_recommendations"] == [
        "render_as_selected_state",
        "render_as_unknown",
        "abstain_review",
        "choose_listed_competing_hypothesis",
    ]
    assert model_input["provided_competing_hypotheses"] == [
        "Recent seizure-free interval is also mentioned."
    ]
    assert "gold_label" not in model_input
    assert "delta" not in model_input
    assert row["development_accounting"]["delta"] == "C_to_W"
    assert metadata["metrics"]["eligible_verifier_rows"] == 1
    assert metadata["metrics"]["c_to_w_against_comparator_rows"] == 1
    assert metadata["metrics"]["exact_evidence_rate"] == 1.0


def test_predeclaration_excludes_non_exact_suspicious_rows() -> None:
    rows, metadata = (
        selective_verifier_predeclaration.build_selective_verifier_predeclaration_rows(
            [
                _routing_row(source_row_index=101, exact_trace=True),
                _routing_row(source_row_index=202, exact_trace=False),
                _routing_row(source_row_index=303, action="render"),
            ]
        )
    )

    assert [row["source_row_index"] for row in rows] == [101]
    assert metadata["excluded_source_row_indices"] == [202]
    assert metadata["metrics"]["excluded_non_exact_or_missing_evidence_rows"] == 1
