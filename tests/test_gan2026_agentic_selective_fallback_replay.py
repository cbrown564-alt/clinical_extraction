from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.selective_fallback_replay import (
    run_selective_fallback_replay,
)


def test_selective_replay_scores_policy_transitions_against_fallback() -> None:
    rows = [
        _row(
            1,
            gold_monthly=8.0,
            self_consistency="unknown",
            single_agent="2 per week",
            multi_agent="unknown",
        ),
        _row(
            2,
            gold_monthly=8.0,
            self_consistency="2 per week",
            single_agent="seizure free for multiple year",
            multi_agent="seizure free for multiple year",
        ),
    ]

    replay_rows, metadata = run_selective_fallback_replay(rows, manifest_records=[])

    assert replay_rows[0]["policies"]["all_agree_tool_accept"]["transition"] == (
        "wrong_to_correct"
    )
    assert replay_rows[1]["policies"]["all_agree_tool_accept"]["transition"] == (
        "correct_to_wrong"
    )

    summary = metadata["policy_summaries"]["all_agree_tool_accept"]
    assert summary["changed_labels"] == 2
    assert summary["wrong_to_correct"] == 1
    assert summary["correct_to_wrong"] == 1
    assert summary["net_purist_gain"] == 0
    assert summary["promotion_eligible"] is True
    assert summary["gate_status"] == "reject"


def test_manifest_family_oracle_is_diagnostic_only() -> None:
    rows = [
        _row(
            3,
            gold_monthly=8.0,
            self_consistency="unknown",
            single_agent="2 per week",
            multi_agent="2 per week",
        )
    ]
    manifest_records = [
        {
            "source_row_index": 3,
            "hidden_families": ["cluster_burden"],
        }
    ]

    _replay_rows, metadata = run_selective_fallback_replay(
        rows,
        manifest_records=manifest_records,
    )

    summary = metadata["policy_summaries"]["manifest_family_oracle"]
    assert summary["promotion_eligible"] is False
    assert summary["gate_status"] == "diagnostic_only"


def test_raw_repair_disagreement_policy_tolerates_unparseable_raw_label() -> None:
    rows = [
        _row(
            4,
            gold_monthly=1000.0,
            self_consistency="unknown",
            single_agent="unknown",
            multi_agent="unknown",
        )
    ]
    rows[0]["condition_traces"]["multi_agent_matched"]["model_call_results"][0][
        "raw_model_final_label"
    ] = "increased brief absences and jerks"

    replay_rows, metadata = run_selective_fallback_replay(rows, manifest_records=[])

    assert (
        replay_rows[0]["policies"]["raw_repair_disagreement_fallback"]["action"]
        == "fallback_self_consistency"
    )
    assert metadata["policy_summaries"]["raw_repair_disagreement_fallback"]["rows"] == 1


def _row(
    source_row_index: int,
    *,
    gold_monthly: float,
    self_consistency: str,
    single_agent: str,
    multi_agent: str,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "condition_traces": {
            "single_self_consistency_temperature": _trace(
                self_consistency,
                gold_monthly=gold_monthly,
                call_roles=("self_consistency_sample", "self_consistency_sample"),
            ),
            "single_agent_tools": _trace(
                single_agent,
                gold_monthly=gold_monthly,
                call_roles=("agent_loop",),
                tool_candidate_kinds=("frequency_rate",),
            ),
            "multi_agent_matched": _trace(
                multi_agent,
                gold_monthly=gold_monthly,
                call_roles=(
                    "extractor_agent",
                    "boundary_agent",
                    "adjudicator_agent",
                    "coordinator_agent",
                ),
                tool_candidate_kinds=("frequency_rate",),
            ),
        },
    }


def _trace(
    label: str,
    *,
    gold_monthly: float,
    call_roles: tuple[str, ...],
    tool_candidate_kinds: tuple[str, ...] = (),
) -> dict:
    return {
        "final_label": label,
        "normalized_label_vote": {
            "selected_label": label,
            "raw_labels": [label for _role in call_roles],
            "vote_input_labels": [label for _role in call_roles],
            "normalized_labels": [label for _role in call_roles],
            "vote_counts": {label: len(call_roles)},
            "repair_event_counts": {},
        },
        "model_call_results": [
            {
                "call_role": role,
                "raw_model_final_label": label,
                "normalized_vote_input_label": label,
                "normalized_vote_label": label,
                "normalized_vote_repair_events": [],
                "decision_record": {
                    "final_label": label,
                    "answer_kind": "frequency",
                    "confidence": "high",
                },
                "comparison": {"gold_monthly_frequency": gold_monthly},
            }
            for role in call_roles
        ],
        "tool_calls": [
            {
                "tool_name": "parse_seizure_frequency_candidates",
                "result": {
                    "candidates": [
                        {"candidate_kind": kind}
                        for kind in tool_candidate_kinds
                    ]
                },
            }
        ],
    }
