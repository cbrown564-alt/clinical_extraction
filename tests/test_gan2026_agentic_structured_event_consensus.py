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
) -> dict:
    return {
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
