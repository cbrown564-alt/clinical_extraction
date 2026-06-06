from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    clinical_assessment_verification_decision as verification_decision,
)


def test_cyclic_window_routes_to_abstain() -> None:
    decision = verification_decision.decision_for_route(
        source_row_index=3468,
        route_families=["cyclic_window_without_event_count"],
        route_reasons=["cyclic vulnerability window is present without event count or burden"],
        source_route_policy_id="gan2026_validation250_verification_route_policy_v0",
        proposed_rendered_label=None,
        score_context=_score_context(),
    )

    assert decision.action == "abstain"
    assert decision.action_basis == "route_family_policy"
    assert decision.final_rendered_label is None
    assert decision.score_context["score_status"] == "not_scored_null_rendered_label"


def test_medication_cadence_routes_to_human_review() -> None:
    decision = verification_decision.decision_for_route(
        source_row_index=5476,
        route_families=["medication_cadence_ambiguity"],
        route_reasons=["cadence evidence may describe medication or rescue use rather than events"],
        source_route_policy_id="gan2026_validation250_verification_route_policy_v0",
        proposed_rendered_label=None,
        score_context=_score_context(),
    )

    assert decision.action == "human_review"
    assert decision.action_basis == "manual_review_required"
    assert decision.final_rendered_label is None


def test_proxy_overreach_without_proposed_rendering_abstains() -> None:
    decision = verification_decision.decision_for_route(
        source_row_index=3534,
        route_families=["seizure_free_proxy_evidence_overreach"],
        route_reasons=["seizure-free projection is based on proxy or conditional evidence"],
        source_route_policy_id="gan2026_validation250_verification_route_policy_v0",
        proposed_rendered_label=None,
        score_context=_score_context(),
    )

    assert decision.action == "abstain"
    assert decision.action_basis == "route_family_policy"
    assert decision.proposed_rendered_label is None
    assert decision.final_rendered_label is None


def test_proxy_overreach_with_proposed_rendering_rejects() -> None:
    decision = verification_decision.decision_for_route(
        source_row_index=3534,
        route_families=["seizure_free_proxy_evidence_overreach"],
        route_reasons=["seizure-free projection is based on proxy or conditional evidence"],
        source_route_policy_id="gan2026_validation250_verification_route_policy_v0",
        proposed_rendered_label="seizure free for 7 month",
        score_context=_score_context(score_status="scored"),
    )

    assert decision.action == "reject"
    assert decision.action_basis == "proposed_outcome_block"
    assert decision.proposed_rendered_label == "seizure free for 7 month"
    assert decision.final_rendered_label is None


def test_build_verification_decision_artifact_only_emits_routed_rows() -> None:
    rows, metadata = verification_decision.build_verification_decision_artifact(
        [
            _route_row(
                3468,
                routed=True,
                families=["cyclic_window_without_event_count"],
            ),
            _route_row(200, routed=False, families=[]),
            _route_row(
                5476,
                routed=True,
                families=["medication_cadence_ambiguity"],
            ),
        ],
        route_artifact_path="route.jsonl",
    )

    assert [row["source_row_index"] for row in rows] == [3468, 5476]
    assert rows[0]["verification_decision"]["action"] == "abstain"
    assert rows[1]["verification_decision"]["action"] == "human_review"
    assert metadata["summary"]["input_route_rows"] == 3
    assert metadata["summary"]["input_routed_rows"] == 2
    assert metadata["summary"]["decision_rows"] == 2
    assert metadata["summary"]["action_counts"] == {
        "abstain": 1,
        "human_review": 1,
    }


def _route_row(
    source_row_index: int,
    *,
    routed: bool,
    families: list[str],
    proposed_rendered_label: str | None = None,
) -> dict:
    return {
        "artifact_kind": "gan2026_verification_route_row",
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "source_artifacts": {
            "scoring_policy_id": "gan2026_rendered_label_scoring_policy_v0",
            "projection_policy_id": "gan2026_clinical_assessment_projection_v0",
            "render_policy_id": "gan2026_final_label_renderer_v0",
        },
        "final_rendered_label": {"rendered_label": proposed_rendered_label},
        "score_context": _score_context(),
        "verification_route": {
            "source_row_index": source_row_index,
            "component_owner": "verification_route",
            "route_policy_id": "gan2026_validation250_verification_route_policy_v0",
            "routed": routed,
            "route_families": families,
            "route_reasons": [
                "cyclic vulnerability window is present without event count or burden"
            ]
            if families
            else [],
            "route_evidence": {},
            "score_context": _score_context(),
            "schema_version": "gan2026_verification_route_v0",
        },
    }


def _score_context(*, score_status: str = "not_scored_null_rendered_label") -> dict:
    return {
        "score_status": score_status,
        "rendered_label": None,
        "gold_label": "unknown",
        "purist_correct": None,
        "pragmatic_correct": None,
    }
