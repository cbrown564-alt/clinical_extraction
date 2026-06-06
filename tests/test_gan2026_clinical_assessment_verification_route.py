from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_verification_route as verification_route,
)


def test_null_rendered_label_alone_does_not_route() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=10,
        projection_decision=_projection(
            projection_kind="seizure_free",
            aggregation_policy="seizure_free_state",
            projection_issues=["seizure_free_duration_required"],
        ),
        final_rendered_label=_rendered(None, ["projection_semantics_missing"]),
        score=_score(score_status="not_scored_null_rendered_label"),
    )

    assert route.routed is False
    assert route.route_families == []
    assert route.score_context["score_status"] == "not_scored_null_rendered_label"


def test_seizure_free_proxy_evidence_routes_as_specific_family() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=3534,
        projection_decision=_projection(
            projection_kind="seizure_free",
            aggregation_policy="seizure_free_state",
            source_candidate_ids=["llm:3534:2", "llm:3534:1"],
            projection_basis="seizure_free_proxy_evidence",
            projection_issues=["seizure_free_proxy_evidence_overreach"],
        ),
        final_rendered_label=_rendered(None, ["projection_semantics_missing"]),
        score=_score(score_status="not_scored_null_rendered_label"),
    )

    assert route.routed is True
    assert route.route_families == ["seizure_free_proxy_evidence_overreach"]


def test_score_wrong_alone_does_not_route() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=11,
        projection_decision=_projection(
            projection_kind="frequency_rate",
            aggregation_policy="single_fact",
        ),
        final_rendered_label=_rendered("2 per month", []),
        score=_score(score_status="scored", purist_correct=False),
    )

    assert route.routed is False
    assert route.score_context["purist_correct"] is False


def test_cluster_operand_gaps_route_as_cluster_axis_ambiguity() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=12,
        projection_decision=_projection(
            projection_kind="cluster_frequency",
            aggregation_policy="cluster_axis",
            projection_issues=[
                "cluster_frequency_operands_unparsed",
                "cluster_cadence_operands_incomplete",
            ],
        ),
        final_rendered_label=_rendered(None, ["projection_semantics_missing"]),
        score=_score(score_status="not_scored_null_rendered_label"),
    )

    assert route.routed is True
    assert route.route_families == ["cluster_axis_ambiguity"]


def test_medication_cadence_routes_as_specific_family() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=5476,
        projection_decision=_projection(
            projection_kind="cluster_frequency",
            aggregation_policy="primary_with_context",
            projection_issues=[
                "cluster_frequency_operands_unparsed",
                "cluster_cadence_operands_incomplete",
                "medication_cadence_ambiguity",
            ],
        ),
        final_rendered_label=_rendered(None, ["projection_semantics_missing"]),
        score=_score(score_status="not_scored_null_rendered_label"),
    )

    assert route.routed is True
    assert route.route_families == ["medication_cadence_ambiguity"]


def test_unknown_cadence_cluster_projection_does_not_route() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=1317,
        projection_decision=_projection(
            projection_kind="cluster_frequency",
            aggregation_policy="single_fact",
            projection_basis="unknown_cadence_cluster_burden",
            projection_issues=["cluster_frequency_operands_unparsed"],
        ),
        final_rendered_label=_rendered("unknown, multiple per cluster", []),
        score=_score(score_status="scored"),
    )

    assert route.routed is False
    assert route.route_families == []


def test_cyclic_window_without_event_count_routes_as_specific_family() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=3469,
        projection_decision=_projection(
            projection_kind="cluster_frequency",
            aggregation_policy="single_fact",
            projection_issues=[
                "cluster_frequency_operands_unparsed",
                "cluster_cadence_operands_incomplete",
                "cyclic_window_without_event_count",
            ],
        ),
        final_rendered_label=_rendered(None, ["projection_semantics_missing"]),
        score=_score(score_status="not_scored_null_rendered_label"),
    )

    assert route.routed is True
    assert route.route_families == ["cyclic_window_without_event_count"]


def test_additive_vague_or_mixed_window_routes() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=13,
        projection_decision=_projection(
            projection_kind="frequency_rate",
            aggregation_policy="additive_same_window",
            source_candidate_ids=["llm:13:1", "llm:13:2"],
            projection_issues=[
                "vague_count",
                "additive_frequency_period_mismatch",
            ],
        ),
        final_rendered_label=_rendered(None, ["projection_semantics_missing"]),
        score=_score(score_status="not_scored_null_rendered_label"),
    )

    assert route.routed is True
    assert route.route_families == ["mixed_window_or_vague_addition"]


def test_dominant_vague_projection_resolves_mixed_window_route() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=744,
        projection_decision=_projection(
            projection_kind="frequency_rate",
            aggregation_policy="additive_same_window",
            projection_basis="dominant_vague_current_burden",
            projection_issues=[
                "vague_count",
                "additive_frequency_period_mismatch",
            ],
        ),
        final_rendered_label=_rendered("multiple per week", []),
        score=_score(score_status="scored"),
    )

    assert route.routed is False
    assert route.route_families == []


def test_multiple_primary_nonadditive_routes() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=14,
        projection_decision=_projection(
            projection_kind="unknown_frequency",
            aggregation_policy="primary_with_context",
            source_candidate_ids=["llm:14:1", "llm:14:2"],
        ),
        final_rendered_label=_rendered("unknown", []),
        score=_score(score_status="scored"),
    )

    assert route.routed is True
    assert route.route_families == ["multiple_current_primary_facts"]


def test_unknown_due_to_ambiguity_routes_as_policy_sensitive_render() -> None:
    route = verification_route.route_decision_for_row(
        source_row_index=15,
        projection_decision=_projection(
            projection_kind="unknown_frequency",
            aggregation_policy="unknown_due_to_ambiguity",
            projection_basis="unknown_frequency_internal_state",
        ),
        final_rendered_label=_rendered("unknown", []),
        score=_score(score_status="scored"),
    )

    assert route.routed is True
    assert route.route_families == ["rendered_label_supported_but_policy_sensitive"]


def test_build_verification_route_artifact_summarizes_routes() -> None:
    rows, metadata = verification_route.build_verification_route_artifact(
        [
            _score_row(
                20,
                _projection("cluster_frequency", "cluster_axis", ["llm:20:1"], [
                    "cluster_cadence_operands_incomplete"
                ]),
                _rendered(None, ["projection_semantics_missing"]),
                _score(score_status="not_scored_null_rendered_label"),
            ),
            _score_row(
                21,
                _projection("frequency_rate", "single_fact"),
                _rendered("2 per month", []),
                _score(score_status="scored", purist_correct=False),
            ),
        ],
        score_artifact_path="score.jsonl",
    )

    assert rows[0]["verification_route"]["routed"] is True
    assert rows[1]["verification_route"]["routed"] is False
    assert metadata["summary"]["routed_rows"] == 1
    assert metadata["summary"]["route_family_counts"] == {"cluster_axis_ambiguity": 1}
    assert metadata["summary"]["routed_score_status_counts"] == {
        "not_scored_null_rendered_label": 1
    }


def _projection(
    projection_kind: str,
    aggregation_policy: str,
    source_candidate_ids: list[str] | None = None,
    projection_issues: list[str] | None = None,
    projection_basis: str | None = None,
) -> dict:
    return {
        "source_row_index": 1,
        "projection_kind": projection_kind,
        "projection_basis": projection_basis or (
            "cluster_frequency"
            if projection_kind == "cluster_frequency"
            else "frequency_rate"
        ),
        "source_aggregation_policy": aggregation_policy,
        "source_candidate_ids": source_candidate_ids or ["llm:1:1"],
        "projection_issues": projection_issues or [],
    }


def _rendered(rendered_label: str | None, render_issues: list[str]) -> dict:
    return {
        "rendered_label": rendered_label,
        "render_issues": render_issues,
    }


def _score(
    *,
    score_status: str,
    purist_correct: bool | None = None,
    pragmatic_correct: bool | None = None,
) -> dict:
    return {
        "score_status": score_status,
        "rendered_label": None,
        "gold_label": "unknown",
        "purist_correct": purist_correct,
        "pragmatic_correct": pragmatic_correct,
    }


def _score_row(
    source_row_index: int,
    projection_decision: dict,
    final_rendered_label: dict,
    score: dict,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "scoring_policy_id": "gan2026_rendered_label_scoring_policy_v0",
        "source_artifacts": {
            "projection_policy_id": "gan2026_clinical_assessment_projection_v0",
            "render_policy_id": "gan2026_final_label_renderer_v0",
        },
        "projection_decision": projection_decision,
        "final_rendered_label": final_rendered_label,
        "score": score,
    }
