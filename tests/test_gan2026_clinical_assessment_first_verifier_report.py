from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_first_verifier_report as first_verifier_report,
)


def _route_row(
    *,
    source_row_index: int,
    route_families: list[str],
    route_reasons: list[str] | None = None,
    rendered_label: str | None = None,
    exact_trace: bool = True,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "projection_decision": {
            "projection_kind": "frequency_rate",
            "projection_basis": "frequency_rate",
            "projected_label_semantics": rendered_label or "",
            "projection_issues": ["issue_a"],
            "projection_owner": "rate_projection_policy",
            "projection_rule_id": "rule_v0",
        },
        "final_rendered_label": {
            "rendered_label": rendered_label,
            "render_basis": "frequency_rate",
            "render_issues": [] if rendered_label else ["projection_semantics_missing"],
            "projection_owner": "rate_projection_policy",
            "projection_rule_id": "rule_v0",
        },
        "verification_route": {
            "routed": True,
            "route_families": route_families,
            "route_reasons": route_reasons or ["reason_a"],
            "route_evidence": {
                "projection_basis": "frequency_rate",
                "projection_kind": "frequency_rate",
                "projection_issues": ["issue_a"],
                "rendered_label_present": rendered_label is not None,
                "render_issues": [] if rendered_label else ["projection_semantics_missing"],
                "source_candidate_ids": ["llm:1"],
                "source_aggregation_policy": "single_fact",
                "source_normalized_phrase": "about once per week",
                "selected_evidence_status": {
                    "exact_trace": exact_trace,
                    "source_id_status": "valid" if exact_trace else "invalid",
                    "source_id_trace": {
                        "selected_source_ids": ["note:1:span:0-10"],
                        "expected_source_ids": ["note:1:span:0-10"] if exact_trace else [],
                        "missing_expected_source_ids": [],
                        "unexpected_source_ids": [] if exact_trace else ["note:1:span:0-10"],
                        "trace_basis": (
                            "exact_selected_evidence"
                            if exact_trace
                            else "non_exact_or_missing_evidence"
                        ),
                    },
                },
            },
            "score_context": {
                "gold_label": "1 per week",
                "purist_correct": True,
                "pragmatic_correct": True,
                "exact_normalized_label_match": True,
                "score_status": "scored" if rendered_label else "not_scored_null_rendered_label",
            },
        },
    }


def _decision_row(
    *,
    source_row_index: int,
    route_families: list[str],
    rendered_label: str | None,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "verification_decision": {
            "action": "abstain",
            "action_basis": "route_family_policy",
            "action_reason": "baseline abstain",
            "proposed_rendered_label": rendered_label,
            "route_families": route_families,
        },
    }


def _assessment_row(*, source_row_index: int) -> dict:
    return {
        "source_row_index": source_row_index,
        "clinical_assessment": {
            "assessment_kind": "frequency_rate",
            "aggregation_policy": "single_fact",
            "assessment_summary": "Current weekly seizure burden.",
            "normalized_burden": {"source_normalized_phrase": "about once per week"},
            "normalization_issues": ["issue_a"],
            "primary_candidate_ids": ["llm:1"],
            "supporting_candidate_ids": ["llm:2"],
            "rejected_candidate_ids": ["llm:3"],
        },
        "typed_input": {
            "candidate_set": {
                "candidates": [
                    {
                        "candidate_id": "llm:1",
                        "candidate_kind": "frequency_rate",
                        "event_type": "seizure",
                        "temporality": "current",
                        "certainty": "certain",
                        "assertion_status": "asserted",
                        "source_phrase": "about once per week",
                        "evidence_text": "Seizures occur about once per week.",
                        "source_ids": ["note:1:span:0-10"],
                    }
                ]
            }
        },
    }


def test_build_first_verifier_report_rows_assigns_predeclared_buckets_and_sidecars() -> None:
    route_rows = [
        _route_row(
            source_row_index=101,
            route_families=[
                "selected_evidence_missing_exact_trace",
                "mixed_window_or_vague_addition",
            ],
            exact_trace=False,
        ),
        _route_row(
            source_row_index=202,
            route_families=["cyclic_window_without_event_count"],
        ),
        _route_row(
            source_row_index=303,
            route_families=["selected_source_id_invalid"],
            exact_trace=False,
        ),
        _route_row(
            source_row_index=404,
            route_families=["rendered_label_supported_but_policy_sensitive"],
            rendered_label="seizure free for 12 month",
        ),
    ]
    decision_rows = [
        _decision_row(
            source_row_index=101,
            route_families=[
                "selected_evidence_missing_exact_trace",
                "mixed_window_or_vague_addition",
            ],
            rendered_label=None,
        ),
        _decision_row(
            source_row_index=202,
            route_families=["cyclic_window_without_event_count"],
            rendered_label=None,
        ),
        _decision_row(
            source_row_index=303,
            route_families=["selected_source_id_invalid"],
            rendered_label=None,
        ),
        _decision_row(
            source_row_index=404,
            route_families=["rendered_label_supported_but_policy_sensitive"],
            rendered_label="seizure free for 12 month",
        ),
    ]
    assessment_rows = [
        _assessment_row(source_row_index=101),
        _assessment_row(source_row_index=202),
        _assessment_row(source_row_index=303),
        _assessment_row(source_row_index=404),
    ]

    rows, metadata = first_verifier_report.build_first_verifier_report_rows(
        route_rows,
        decision_rows,
        assessment_rows,
        route_artifact_path="route.jsonl",
        decision_artifact_path="decision.jsonl",
        assessment_artifact_path="assessment.jsonl",
    )

    by_row = {row["source_row_index"]: row for row in rows}
    assert by_row[101]["route_bucket"] == "verifier_eligible_ambiguity"
    assert by_row[101]["provenance_sidecar_present"] is True
    assert by_row[101]["provenance_sidecar_families"] == [
        "selected_evidence_missing_exact_trace"
    ]
    assert by_row[202]["route_bucket"] == "upstream_policy_appendix"
    assert by_row[303]["route_bucket"] == "provenance_only_audit"
    assert by_row[404]["route_bucket"] == "rendered_policy_sensitive_appendix"
    assert metadata["metrics"]["clinical_policy_rows"] == 3
    assert metadata["metrics"]["clinical_policy_rows_with_provenance_sidecar"] == 1
    assert metadata["metrics"]["provenance_only_rows"] == 1


def test_model_input_keeps_gold_and_score_fields_out_of_model_visible_packet() -> None:
    rows, _ = first_verifier_report.build_first_verifier_report_rows(
        [
            _route_row(
                source_row_index=101,
                route_families=["mixed_window_or_vague_addition"],
            )
        ],
        [
            _decision_row(
                source_row_index=101,
                route_families=["mixed_window_or_vague_addition"],
                rendered_label=None,
            )
        ],
        [_assessment_row(source_row_index=101)],
        route_artifact_path="route.jsonl",
        decision_artifact_path="decision.jsonl",
        assessment_artifact_path="assessment.jsonl",
    )

    model_input = rows[0]["verifier_model_input"]
    payload_text = str(model_input)

    baseline = model_input["verification_case"]["baseline_verification_decision_v0"]
    assert baseline["action"] == "abstain"
    candidate_packets = model_input["verification_case"]["candidate_evidence_packets"]
    assert candidate_packets[0]["candidate_id"] == "llm:1"
    for term in [
        "gold_label",
        "purist_correct",
        "pragmatic_correct",
        "exact_normalized_label_match",
        "score_status",
        "audit_only_w_to_c",
        "audit_only_c_to_w",
        "W_to_C",
        "C_to_W",
    ]:
        assert term not in payload_text


def test_clean_first_verifier_experiment_input_excludes_provenance_only_rows() -> None:
    rows, _ = first_verifier_report.build_first_verifier_report_rows(
        [
            _route_row(
                source_row_index=101,
                route_families=[
                    "selected_evidence_missing_exact_trace",
                    "mixed_window_or_vague_addition",
                ],
                exact_trace=False,
            ),
            _route_row(
                source_row_index=202,
                route_families=["selected_source_id_invalid"],
                exact_trace=False,
            ),
            _route_row(
                source_row_index=303,
                route_families=["cyclic_window_without_event_count"],
            ),
        ],
        [
            _decision_row(
                source_row_index=101,
                route_families=[
                    "selected_evidence_missing_exact_trace",
                    "mixed_window_or_vague_addition",
                ],
                rendered_label=None,
            ),
            _decision_row(
                source_row_index=202,
                route_families=["selected_source_id_invalid"],
                rendered_label=None,
            ),
            _decision_row(
                source_row_index=303,
                route_families=["cyclic_window_without_event_count"],
                rendered_label=None,
            ),
        ],
        [
            _assessment_row(source_row_index=101),
            _assessment_row(source_row_index=202),
            _assessment_row(source_row_index=303),
        ],
        route_artifact_path="route.jsonl",
        decision_artifact_path="decision.jsonl",
        assessment_artifact_path="assessment.jsonl",
    )

    clean_rows, metadata = first_verifier_report.build_clean_first_verifier_experiment_input(
        rows
    )

    assert [row["source_row_index"] for row in clean_rows] == [101, 303]
    assert metadata["metrics"]["provenance_only_rows_excluded"] == 1
    assert clean_rows[0]["appendix_policy"]["main_score_table"] is True
    assert clean_rows[1]["appendix_policy"]["appendix_only"] is True
    assert "gold_label" not in str(clean_rows[0]["verifier_model_input"])
