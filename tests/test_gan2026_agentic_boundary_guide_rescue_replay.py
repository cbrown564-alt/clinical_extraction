from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    boundary_guide_rescue_replay,
)


def test_unanimous_frequency_or_cluster_override_can_promote() -> None:
    e1_rows = []
    e2_rows = []
    for source_row_index in (1, 2, 3):
        e1_rows.append(
            _e1_row(
                source_row_index,
                gold_monthly=8.0,
                no_tool="unknown",
                boundary="2 per week",
            )
        )
        e2_rows.append(
            _e2_row(
                source_row_index,
                gold_monthly=8.0,
                reference="unknown",
                candidate="2 per week",
                normalized_votes=("2 per week",) * 4,
            )
        )

    replay_rows, metadata = boundary_guide_rescue_replay.run_boundary_guide_rescue_replay(
        e1_rows=e1_rows,
        e2_rows=e2_rows,
        manifest_records=[],
    )

    assert replay_rows[0]["policies"]["unanimous_frequency_or_cluster_override"][
        "transition"
    ] == "wrong_to_correct"
    summary = metadata["policy_summaries"]["unanimous_frequency_or_cluster_override"]
    assert summary["gate_status"] == "promote"
    assert summary["wrong_to_correct"] == 3
    assert summary["correct_to_wrong"] == 0
    assert summary["changed_label_precision"] == 1.0


def test_guide_and_vote_agree_blocks_boundary_labels() -> None:
    e1_rows = [
        _e1_row(10, gold_monthly=8.0, no_tool="2 per week", boundary="unknown")
    ]
    e2_rows = [
        _e2_row(
            10,
            gold_monthly=8.0,
            reference="2 per week",
            candidate="unknown",
            normalized_votes=("unknown",) * 4,
        )
    ]

    replay_rows, _metadata = boundary_guide_rescue_replay.run_boundary_guide_rescue_replay(
        e1_rows=e1_rows,
        e2_rows=e2_rows,
        manifest_records=[],
    )

    decision = replay_rows[0]["policies"]["guide_and_vote_agree_override"]
    assert decision["selected_label"] == "2 per week"
    assert decision["action"] == "fallback_self_consistency_no_e1_e2_safe_agreement"


def test_boundary_demotion_block_falls_back_over_frequency_fallback() -> None:
    e1_rows = [
        _e1_row(
            20,
            gold_monthly=8.0,
            no_tool="2 per week",
            boundary="seizure free for multiple year",
        )
    ]
    e2_rows = [
        _e2_row(
            20,
            gold_monthly=8.0,
            reference="2 per week",
            candidate="seizure free for multiple year",
            normalized_votes=("seizure free for multiple year",) * 4,
        )
    ]

    replay_rows, _metadata = boundary_guide_rescue_replay.run_boundary_guide_rescue_replay(
        e1_rows=e1_rows,
        e2_rows=e2_rows,
        manifest_records=[],
    )

    decision = replay_rows[0]["policies"]["boundary_demotion_block"]
    assert decision["selected_label"] == "2 per week"
    assert decision["action"] == "fallback_self_consistency_block_boundary_demotion"
    assert decision["transition"] == "unchanged_correct"


def test_cluster_restore_and_hidden_family_diagnostic_summary() -> None:
    e1_rows = [
        _e1_row(
            30,
            gold_monthly=8.0,
            no_tool="1 per month",
            boundary="1 cluster per month, 8 per cluster",
        )
    ]
    e2_rows = [
        _e2_row(
            30,
            gold_monthly=8.0,
            reference="1 per month",
            candidate="1 cluster per month, 8 per cluster",
            normalized_votes=("1 cluster per month, 8 per cluster",) * 4,
        )
    ]
    manifest_records = [
        {
            "source_row_index": 30,
            "hidden_families": ["cluster_burden"],
        }
    ]

    replay_rows, metadata = boundary_guide_rescue_replay.run_boundary_guide_rescue_replay(
        e1_rows=e1_rows,
        e2_rows=e2_rows,
        manifest_records=manifest_records,
    )

    decision = replay_rows[0]["policies"]["cluster_restore_only"]
    assert decision["selected_label"] == "1 cluster per month, 8 per cluster"
    assert decision["changed_label"] is True
    family_summary = metadata["diagnostic_hidden_family_summaries"][
        "cluster_restore_only"
    ]["cluster_burden"]
    assert family_summary["changed_labels"] == 1


def _e1_row(
    source_row_index: int,
    *,
    gold_monthly: float,
    no_tool: str,
    boundary: str,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "condition_traces": {
            "direct_no_tool_context": _trace(
                no_tool,
                gold_monthly=gold_monthly,
                call_roles=("direct_context_ablation",),
            ),
            "direct_boundary_guide_only": _trace(
                boundary,
                gold_monthly=gold_monthly,
                call_roles=("direct_context_ablation",),
            ),
        },
    }


def _e2_row(
    source_row_index: int,
    *,
    gold_monthly: float,
    reference: str,
    candidate: str,
    normalized_votes: tuple[str, ...],
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "reference_label": reference,
        "reference_comparison": _comparison(reference, gold_monthly),
        "condition_trace": _trace(
            candidate,
            gold_monthly=gold_monthly,
            call_roles=("tool_self_consistency_sample",) * len(normalized_votes),
            normalized_votes=normalized_votes,
        ),
    }


def _trace(
    label: str,
    *,
    gold_monthly: float,
    call_roles: tuple[str, ...],
    normalized_votes: tuple[str, ...] | None = None,
) -> dict:
    votes = normalized_votes or tuple(label for _role in call_roles)
    return {
        "final_label": label,
        "final_comparison": _comparison(label, gold_monthly),
        "normalized_label_vote": {
            "selected_label": label,
            "raw_labels": list(votes),
            "vote_input_labels": list(votes),
            "normalized_labels": list(votes),
            "vote_counts": {vote: votes.count(vote) for vote in set(votes)},
            "repair_event_counts": {},
        },
        "model_call_results": [
            {
                "call_role": role,
                "raw_model_final_label": vote,
                "normalized_vote_input_label": vote,
                "normalized_vote_label": vote,
                "normalized_vote_repair_events": [],
                "decision_record": {
                    "final_label": vote,
                    "answer_kind": "frequency",
                    "confidence": "high",
                },
                "comparison": {"gold_monthly_frequency": gold_monthly},
            }
            for role, vote in zip(call_roles, votes, strict=True)
        ],
    }


def _comparison(label: str, gold_monthly: float) -> dict:
    return {
        "gold_monthly_frequency": gold_monthly,
        "purist_correct": label == "2 per week"
        or label == "1 cluster per month, 8 per cluster",
        "pragmatic_correct": label == "2 per week"
        or label == "1 cluster per month, 8 per cluster",
    }
