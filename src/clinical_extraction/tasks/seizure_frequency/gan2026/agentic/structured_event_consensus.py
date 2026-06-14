"""Multi-agent consensus replay over Gan structured-event outputs.

This module treats saved `hybrid_structured_events` artifacts as agent votes
and a deterministic top candidate as the tool-backed safety floor. It is a
no-call replay surface for testing whether a future live tool/multi-agent
pipeline has enough calibrated signal to improve the strong rules baseline.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_cv_promotion import (
    summarize_family_holdout_cv,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_transitions import (
    CONSENSUS_PATHS,
    note_text_from_rules_row,
    summarize_transitions_by_family,
    tag_hidden_families,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist

ConsensusAction = Literal["keep_baseline", "switch_to_consensus"]


class AgentVote(BaseModel):
    """One structured-event agent's final-label vote."""

    model_config = ConfigDict(extra="forbid")

    agent_id: str
    final_label: str | None


class ConsensusDecision(BaseModel):
    """Decision emitted by the consensus adjudicator."""

    model_config = ConfigDict(extra="forbid")

    source_row_index: int | str
    action: ConsensusAction
    reason: str
    baseline_label: str | None
    consensus_label: str | None
    final_label: str | None
    votes: tuple[AgentVote, ...]


def build_exact_label_consensus_decision(
    *,
    source_row_index: int | str,
    baseline_label: str | None,
    votes: Sequence[AgentVote],
) -> ConsensusDecision:
    """Switch only when every agent supplies the same non-null exact label."""

    vote_tuple = tuple(votes)
    labels = [vote.final_label for vote in vote_tuple]
    consensus_label: str | None = None
    action: ConsensusAction = "keep_baseline"
    reason = "no_unanimous_exact_label"
    final_label = baseline_label

    if labels and labels[0] is not None and all(label == labels[0] for label in labels):
        consensus_label = labels[0]
        if consensus_label == baseline_label:
            reason = "consensus_matches_baseline"
        else:
            action = "switch_to_consensus"
            reason = "accepted_unanimous_exact_label"
            final_label = consensus_label

    return ConsensusDecision(
        source_row_index=source_row_index,
        action=action,
        reason=reason,
        baseline_label=baseline_label,
        consensus_label=consensus_label,
        final_label=final_label,
        votes=vote_tuple,
    )


def run_exact_label_consensus_replay(
    rules_rows: Sequence[Mapping[str, Any]],
    agent_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    split: str,
    split_manifest: str,
    source_artifacts: Mapping[str, str],
    condition: str = "rules_tool_plus_structured_event_unanimous_exact_label_v0",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay exact-label consensus over deterministic-top rows and agent votes."""

    agent_rows_by_id = {
        agent_id: _rows_by_source_index(rows) for agent_id, rows in agent_rows.items()
    }
    replay_rows: list[dict[str, Any]] = []
    for rules_row in rules_rows:
        source_row_index = rules_row.get("source_row_index")
        if source_row_index is None:
            continue
        baseline_label = _rules_top_label(rules_row)
        votes = tuple(
            AgentVote(
                agent_id=agent_id,
                final_label=_structured_event_label(rows_by_id.get(source_row_index)),
            )
            for agent_id, rows_by_id in agent_rows_by_id.items()
        )
        decision = build_exact_label_consensus_decision(
            source_row_index=source_row_index,
            baseline_label=baseline_label,
            votes=votes,
        )
        consensus_comparison = _comparison_for_label(decision.final_label, rules_row)
        baseline_comparison = _rules_top_comparison(rules_row)
        reference = dict(rules_row.get("reference") or {})
        hidden_families = tag_hidden_families(
            note_text=note_text_from_rules_row(rules_row),
            gold_per_month=reference.get("gold_monthly_frequency"),
        )
        replay_rows.append(
            {
                "source_row_index": source_row_index,
                "reference": reference,
                "hidden_families": list(hidden_families),
                "baseline_label": baseline_label,
                "baseline_comparison": baseline_comparison,
                "consensus_decision": decision.model_dump(mode="json"),
                "consensus_final_label": decision.final_label,
                "consensus_comparison": consensus_comparison,
                "consensus_transition": _transition(
                    baseline_comparison=baseline_comparison,
                    consensus_comparison=consensus_comparison,
                    baseline_label=baseline_label,
                    final_label=decision.final_label,
                    switched=decision.action == "switch_to_consensus",
                ),
            }
        )

    metadata = {
        "artifact_kind": "gan2026_agentic_structured_event_consensus_replay",
        "pipeline_family": "agentic_structured_event_consensus",
        "condition": condition,
        "split": split,
        "split_manifest": split_manifest,
        "source_artifacts": dict(source_artifacts),
        "mode": "no_call_replay",
        "claim_boundary": (
            "validation-development replay over saved deterministic-tool and "
            "structured-event multi-agent artifacts; gold labels are used only "
            "for post-hoc scoring"
        ),
        "summary": summarize_consensus_rows(replay_rows),
    }
    if split != "test":
        # Per-family breakdown and the held-out-family CV promotion verdict are
        # validation-only instruments; the holdout audit is aggregate-only, so
        # neither is attached for `test`.
        summary_by_family = summarize_transitions_by_family(
            replay_rows, **CONSENSUS_PATHS
        )
        metadata["summary_by_family"] = summary_by_family
        metadata["family_holdout_cv"] = summarize_family_holdout_cv(summary_by_family)
    return replay_rows, metadata


def summarize_consensus_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize baseline versus consensus adjudicator performance."""

    baseline_purist = 0
    baseline_pragmatic = 0
    consensus_purist = 0
    consensus_pragmatic = 0
    switched = 0
    wrong_to_correct = 0
    correct_to_wrong = 0
    correct_to_correct = 0
    wrong_to_wrong = 0
    reasons: dict[str, int] = {}

    for row in rows:
        baseline = row.get("baseline_comparison") or {}
        consensus = row.get("consensus_comparison") or {}
        transition = row.get("consensus_transition") or {}
        decision = row.get("consensus_decision") or {}
        baseline_purist += int(baseline.get("purist_correct") is True)
        baseline_pragmatic += int(baseline.get("pragmatic_correct") is True)
        consensus_purist += int(consensus.get("purist_correct") is True)
        consensus_pragmatic += int(consensus.get("pragmatic_correct") is True)
        switched += int(transition.get("label_changed") is True)
        reason = str(decision.get("reason") or "missing_decision")
        reasons[reason] = reasons.get(reason, 0) + 1

        purist_transition = transition.get("purist_transition")
        if purist_transition == "wrong_to_correct":
            wrong_to_correct += 1
        elif purist_transition == "correct_to_wrong":
            correct_to_wrong += 1
        elif purist_transition == "correct_to_correct":
            correct_to_correct += 1
        elif purist_transition == "wrong_to_wrong":
            wrong_to_wrong += 1

    count = len(rows)
    return {
        "rows": count,
        "baseline_purist_correct": baseline_purist,
        "baseline_purist_accuracy": baseline_purist / count if count else 0.0,
        "consensus_purist_correct": consensus_purist,
        "consensus_purist_accuracy": consensus_purist / count if count else 0.0,
        "baseline_pragmatic_correct": baseline_pragmatic,
        "baseline_pragmatic_accuracy": baseline_pragmatic / count if count else 0.0,
        "consensus_pragmatic_correct": consensus_pragmatic,
        "consensus_pragmatic_accuracy": consensus_pragmatic / count if count else 0.0,
        "switched_labels": switched,
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "correct_to_correct": correct_to_correct,
        "wrong_to_wrong": wrong_to_wrong,
        "net_purist_gain": wrong_to_correct - correct_to_wrong,
        "changed_label_precision": wrong_to_correct / switched if switched else 0.0,
        "reasons": reasons,
    }


def _rows_by_source_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int | str, Mapping[str, Any]]:
    return {
        row["source_row_index"]: row
        for row in rows
        if row.get("source_row_index") is not None
    }


def _rules_top_label(row: Mapping[str, Any]) -> str | None:
    score = _rules_top_comparison(row)
    label = score.get("final_label")
    if label is not None:
        return str(label)
    diagnostics = row.get("deterministic_diagnostics") or {}
    if isinstance(diagnostics, Mapping):
        final_selection = diagnostics.get("final_selection") or {}
        if isinstance(final_selection, Mapping):
            final_label = final_selection.get("final_label")
            return str(final_label) if final_label is not None else None
    return None


def _rules_top_comparison(row: Mapping[str, Any]) -> dict[str, Any]:
    scores = row.get("scores") or {}
    if isinstance(scores, Mapping):
        deterministic_top = scores.get("deterministic_top") or {}
        if isinstance(deterministic_top, Mapping):
            return dict(deterministic_top)
    comparison = row.get("comparison") or {}
    return dict(comparison) if isinstance(comparison, Mapping) else {}


def _structured_event_label(row: Mapping[str, Any] | None) -> str | None:
    if row is None:
        return None
    patched_label = row.get("patched_final_label")
    if patched_label is not None:
        return str(patched_label)
    structured = row.get("structured_record") or {}
    if isinstance(structured, Mapping):
        selection = structured.get("selection") or {}
        if isinstance(selection, Mapping):
            final_label = selection.get("final_label")
            return str(final_label) if final_label is not None else None
    return None


def _comparison_for_label(label: str | None, row: Mapping[str, Any]) -> dict[str, Any]:
    if label is None:
        return {}
    baseline = _rules_top_comparison(row)
    gold_monthly = baseline.get("gold_monthly_frequency")
    if gold_monthly is None:
        reference = row.get("reference") or {}
        if isinstance(reference, Mapping):
            gold_monthly = reference.get("gold_monthly_frequency")
    if gold_monthly is None:
        return {}
    try:
        predicted = label_to_frequency_record(label)
    except ValueError:
        return {}
    predicted_purist = str(map_purist(predicted.monthly_frequency))
    gold_purist = str(map_purist(float(gold_monthly)))
    predicted_pragmatic = str(map_pragmatic(predicted.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(float(gold_monthly)))
    return {
        "final_label": label,
        "predicted_monthly_frequency": predicted.monthly_frequency,
        "gold_monthly_frequency": float(gold_monthly),
        "predicted_purist_category": predicted_purist,
        "gold_purist_category": gold_purist,
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": predicted_pragmatic,
        "gold_pragmatic_category": gold_pragmatic,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


def _transition(
    *,
    baseline_comparison: Mapping[str, Any],
    consensus_comparison: Mapping[str, Any],
    baseline_label: str | None,
    final_label: str | None,
    switched: bool,
) -> dict[str, Any]:
    baseline_correct = baseline_comparison.get("purist_correct")
    consensus_correct = consensus_comparison.get("purist_correct")
    if baseline_correct is True and consensus_correct is True:
        purist_transition = "correct_to_correct"
    elif baseline_correct is True and consensus_correct is False:
        purist_transition = "correct_to_wrong"
    elif baseline_correct is False and consensus_correct is True:
        purist_transition = "wrong_to_correct"
    elif baseline_correct is False and consensus_correct is False:
        purist_transition = "wrong_to_wrong"
    else:
        purist_transition = "unscored"
    return {
        "switched": switched,
        "label_changed": baseline_label != final_label,
        "purist_transition": purist_transition,
    }
