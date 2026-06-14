"""Tests for the exact-label structured-event consensus selector.

These tests pin the *mechanic*: switch off the deterministic baseline only when
every agent emits the same non-null exact label. That is intentionally narrow,
and the narrowness is the point — two-agent majorities were net-negative in the
validation error analysis, so the selector trades recall for precision.

What the tests deliberately do NOT assert is that unanimity is a good *signal*,
because the replay evidence says it is not robust:

- Validation750: 122 changed labels but only 27 wrong->correct / 16
  correct->wrong (precision 0.2213). Most "changes" were category-neutral.
- Test450: with DeepSeek's artifact missing the policy silently degraded to two
  agents and landed at 365/450 (0.8111), barely above pure GPT structured-events
  and well below the 0.9440 validation rate.

Read together these say unanimity is a proxy for "easy row," not "correct on a
hard row": three models agreeing means the row was easy, while 16-23 already
-correct rows get broken. The durable selector metric is changed-label
precision, not raw switch count, and any cross-model policy must guarantee
identical panel/source coverage on both splits. See
docs/research/gan2026_agentic_next_phase_brief_2026-06-14.md for the full
rationale and the next-phase gates this surface should be measured against.
"""

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.structured_event_consensus import (
    AgentVote,
    build_exact_label_consensus_decision,
    run_exact_label_consensus_replay,
    summarize_consensus_rows,
)


def _rules_row(
    *,
    source_row_index: int = 1,
    baseline_label: str = "seizure free for multiple year",
    gold_monthly: float = 1000.0,
    baseline_correct: bool = False,
    note_text: str | None = None,
) -> dict:
    row = {
        "source_row_index": source_row_index,
        "scores": {
            "deterministic_top": {
                "final_label": baseline_label,
                "gold_monthly_frequency": gold_monthly,
                "purist_correct": baseline_correct,
                "pragmatic_correct": baseline_correct,
            }
        },
        "reference": {"gold_monthly_frequency": gold_monthly},
    }
    if note_text is not None:
        row["note_text"] = note_text
    return row


def _agent_row(*, source_row_index: int = 1, label: str | None = "unknown") -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "selection": {
                "final_label": label,
                "selected_event_ids": ["e1"] if label else [],
                "confidence": "high",
                "evidence": "agent evidence",
            }
        },
    }


def test_exact_label_consensus_switches_when_all_agents_match() -> None:
    decision = build_exact_label_consensus_decision(
        source_row_index=1,
        baseline_label="seizure free for multiple year",
        votes=(
            AgentVote(agent_id="gpt", final_label="unknown"),
            AgentVote(agent_id="qwen", final_label="unknown"),
            AgentVote(agent_id="deepseek", final_label="unknown"),
        ),
    )

    assert decision.final_label == "unknown"
    assert decision.action == "switch_to_consensus"
    assert decision.reason == "accepted_unanimous_exact_label"


def test_exact_label_consensus_keeps_baseline_without_unanimity() -> None:
    decision = build_exact_label_consensus_decision(
        source_row_index=1,
        baseline_label="1 per month",
        votes=(
            AgentVote(agent_id="gpt", final_label="unknown"),
            AgentVote(agent_id="qwen", final_label="unknown"),
            AgentVote(agent_id="deepseek", final_label="1 per month"),
        ),
    )

    assert decision.final_label == "1 per month"
    assert decision.action == "keep_baseline"
    assert decision.reason == "no_unanimous_exact_label"


def test_exact_label_consensus_keeps_baseline_when_consensus_is_baseline() -> None:
    decision = build_exact_label_consensus_decision(
        source_row_index=1,
        baseline_label="1 per month",
        votes=(
            AgentVote(agent_id="gpt", final_label="1 per month"),
            AgentVote(agent_id="qwen", final_label="1 per month"),
            AgentVote(agent_id="deepseek", final_label="1 per month"),
        ),
    )

    assert decision.final_label == "1 per month"
    assert decision.action == "keep_baseline"
    assert decision.reason == "consensus_matches_baseline"


def test_run_exact_label_consensus_replay_reports_transitions() -> None:
    rules_rows = [
        _rules_row(source_row_index=1, baseline_label="seizure free for multiple year"),
        _rules_row(
            source_row_index=2,
            baseline_label="1 per month",
            gold_monthly=1.0138888888888888,
            baseline_correct=True,
        ),
    ]
    agent_rows = {
        "gpt": [
            _agent_row(source_row_index=1, label="unknown"),
            _agent_row(source_row_index=2, label="2 per month"),
        ],
        "qwen": [
            _agent_row(source_row_index=1, label="unknown"),
            _agent_row(source_row_index=2, label="2 per month"),
        ],
        "deepseek": [
            _agent_row(source_row_index=1, label="unknown"),
            _agent_row(source_row_index=2, label="1 per month"),
        ],
    }

    replay_rows, metadata = run_exact_label_consensus_replay(
        rules_rows,
        agent_rows,
        split="validation",
        split_manifest="gan2026_split_v1",
        source_artifacts={"rules": "rules.jsonl"},
    )

    summary = metadata["summary"]

    assert len(replay_rows) == 2
    assert summary["baseline_purist_correct"] == 1
    assert summary["consensus_purist_correct"] == 2
    assert summary["wrong_to_correct"] == 1
    assert summary["correct_to_wrong"] == 0


def test_summarize_consensus_rows_counts_regressions() -> None:
    replay_rows, _ = run_exact_label_consensus_replay(
        [
            _rules_row(
                source_row_index=1,
                baseline_label="1 per month",
                gold_monthly=1.0138888888888888,
                baseline_correct=True,
            )
        ],
        {
            "gpt": [_agent_row(source_row_index=1, label="unknown")],
            "qwen": [_agent_row(source_row_index=1, label="unknown")],
            "deepseek": [_agent_row(source_row_index=1, label="unknown")],
        },
        split="validation",
        split_manifest="gan2026_split_v1",
        source_artifacts={"rules": "rules.jsonl"},
    )

    summary = summarize_consensus_rows(replay_rows)

    assert summary["switched_labels"] == 1
    assert summary["correct_to_wrong"] == 1
    assert summary["net_purist_gain"] == -1


def test_replay_summary_by_family_decomposes_transitions() -> None:
    replay_rows, metadata = run_exact_label_consensus_replay(
        [
            _rules_row(
                source_row_index=1,
                baseline_label="seizure free for multiple year",
                note_text="patient reports being seizure-free for several years",
            )
        ],
        {
            "gpt": [_agent_row(source_row_index=1, label="unknown")],
            "qwen": [_agent_row(source_row_index=1, label="unknown")],
            "deepseek": [_agent_row(source_row_index=1, label="unknown")],
        },
        split="validation",
        split_manifest="gan2026_split_v1",
        source_artifacts={"rules": "rules.jsonl"},
    )

    assert all("hidden_families" in row for row in replay_rows)
    by_family = metadata["summary_by_family"]["families"]
    # Partitioning band from the gold rate (1000 -> unknown) plus the
    # note-text-derived qualitative family.
    assert "band_unknown" in by_family
    assert "seizure_free_duration" in by_family
    assert by_family["seizure_free_duration"]["wrong_to_correct"] == 1
    assert metadata["summary_by_family"]["total_rows"] == 1


def test_replay_omits_summary_by_family_on_holdout() -> None:
    _, metadata = run_exact_label_consensus_replay(
        [_rules_row(source_row_index=1)],
        {
            "gpt": [_agent_row(source_row_index=1, label="unknown")],
            "qwen": [_agent_row(source_row_index=1, label="unknown")],
            "deepseek": [_agent_row(source_row_index=1, label="unknown")],
        },
        split="test",
        split_manifest="gan2026_split_v1",
        source_artifacts={"rules": "rules.jsonl"},
    )

    assert "summary_by_family" not in metadata
