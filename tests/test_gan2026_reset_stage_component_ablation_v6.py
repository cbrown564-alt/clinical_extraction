from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reset_stage_component_ablation_v6 as ablation_v6,
)


def _route_row(
    *,
    source_row_index: int,
    rendered_label: str | None,
    phrase: str = "",
    route_families: list[str] | None = None,
    purist_correct: bool | None = None,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "final_rendered_label": {"rendered_label": rendered_label},
        "projection_decision": {
            "projection_rule_id": "frequency_rate_values_v0",
            "projection_issues": [],
            "source_normalized_phrase": phrase,
        },
        "verification_route": {
            "routed": bool(route_families),
            "route_families": route_families or [],
            "route_evidence": {
                "source_normalized_phrase": phrase,
                "selected_evidence_status": {
                    "exact_trace": True,
                    "source_id_status": "valid",
                },
            },
            "score_context": {"purist_correct": purist_correct},
        },
    }


def test_component_ablation_isolates_recovered_frequency_families_and_audit_counts() -> None:
    route_v5_rows = [
        _route_row(source_row_index=1, rendered_label=None, purist_correct=None),
        _route_row(source_row_index=2, rendered_label=None, purist_correct=None),
        _route_row(
            source_row_index=3,
            rendered_label="1 per week",
            route_families=["relative_only_trend"],
            purist_correct=False,
        ),
    ]
    route_v6_rows = [
        _route_row(
            source_row_index=1,
            rendered_label="1 per day",
            phrase="occurring once per night",
            purist_correct=True,
        ),
        _route_row(
            source_row_index=2,
            rendered_label="multiple per week",
            phrase="several occasions each week",
            purist_correct=True,
        ),
        _route_row(
            source_row_index=3,
            rendered_label="1 per week",
            route_families=["relative_only_trend"],
            purist_correct=True,
        ),
    ]

    artifact = ablation_v6.build_reset_stage_component_ablation_v6(
        route_v5_rows=route_v5_rows,
        route_v6_rows=route_v6_rows,
        route_candidate_trace_rows=[],
    )

    summary = artifact["surface_summary"]
    assert summary["recovered_frequency_family_counts"] == {
        "selected_evidence_frequency_value_recovery": 1,
        "vague_period_frequency_value_recovery": 1,
    }
    assert summary["recovered_frequency_family_rows"][
        "selected_evidence_frequency_value_recovery"
    ] == [1]
    assert (
        summary["audit_only_transition_counts_v5_to_v6"]["by_family"]["relative_only_trend"][
            "W_to_C"
        ]
        == 1
    )

    by_family = {
        row["family"]: row for row in artifact["sections"]["clinical_policy_route_families"]
    }
    assert by_family["relative_only_trend"]["audit_only_w_to_c"] == 1
    assert by_family["relative_only_trend"]["audit_only_c_to_w"] == 0
    assert artifact["one_family_off_replay_attempts"] == []
