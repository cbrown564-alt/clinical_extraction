"""D0 no-call boundary-guide rescue replay for Gan 2026 agentic hard50 traces."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

E1_FALLBACK_CONDITION = "direct_no_tool_context"
E1_BOUNDARY_CONDITION = "direct_boundary_guide_only"
E2_FALLBACK_CONDITION = "single_self_consistency_temperature"
E2_BOUNDARY_CONDITION = "single_agent_tools_self_consistency_boundary_guide_only"

POLICY_ELIGIBILITY = {
    "unanimous_frequency_or_cluster_override": True,
    "guide_and_vote_agree_override": True,
    "cluster_restore_only": True,
    "higher_burden_only": True,
    "boundary_demotion_block": True,
}

BOUNDARY_KINDS = {"seizure_free", "unknown", "no_reference"}


def run_boundary_guide_rescue_replay(
    *,
    e1_rows: Sequence[Mapping[str, Any]],
    e2_rows: Sequence[Mapping[str, Any]],
    manifest_records: Sequence[Mapping[str, Any]],
    e1_jsonl_path: Path | None = None,
    e2_jsonl_path: Path | None = None,
    manifest_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay saved E1/E2 boundary-guide traces through D0 rescue policies."""

    e1_by_index = _rows_by_source_index(e1_rows)
    e2_by_index = _rows_by_source_index(e2_rows)
    manifest_by_index = {
        int(record["source_row_index"]): dict(record)
        for record in manifest_records
        if record.get("source_row_index") is not None
    }
    source_indices = [index for index in e2_by_index if index in e1_by_index]
    missing_e1 = sorted(set(e2_by_index) - set(e1_by_index))
    missing_e2 = sorted(set(e1_by_index) - set(e2_by_index))

    replay_rows = [
        _replay_row(
            e1_by_index[index],
            e2_by_index[index],
            manifest_by_index.get(index, {}),
        )
        for index in source_indices
    ]
    policy_summaries = {
        policy: _summarize_policy(replay_rows, policy)
        for policy in POLICY_ELIGIBILITY
    }
    metadata = {
        "artifact_kind": "gan2026_agentic_boundary_guide_rescue_replay",
        "date": datetime.now(UTC).date().isoformat(),
        "run_started_at_utc": datetime.now(UTC).isoformat(),
        "mode": "no_call_replay",
        "pipeline_family": "agentic_boundary_guide_rescue_replay",
        "pipeline_version": "gan2026_agentic_d0_boundary_guide_rescue_replay_v0",
        "split": "validation",
        "split_manifest": _first_value(e2_rows, "split_manifest", "gan2026_split_v1"),
        "row_count": len(replay_rows),
        "e1_source_jsonl_path": str(e1_jsonl_path) if e1_jsonl_path else None,
        "e2_source_jsonl_path": str(e2_jsonl_path) if e2_jsonl_path else None,
        "hard50_manifest_path": str(manifest_path) if manifest_path else None,
        "fallback_conditions": {
            "e1": E1_FALLBACK_CONDITION,
            "e2": E2_FALLBACK_CONDITION,
        },
        "candidate_conditions": {
            "e1": E1_BOUNDARY_CONDITION,
            "e2": E2_BOUNDARY_CONDITION,
        },
        "policies": {
            policy: {"promotion_eligible": eligible}
            for policy, eligible in POLICY_ELIGIBILITY.items()
        },
        "input_integrity": {
            "e1_rows": len(e1_rows),
            "e2_rows": len(e2_rows),
            "matched_rows": len(replay_rows),
            "missing_from_e1": missing_e1,
            "missing_from_e2": missing_e2,
        },
        "policy_summaries": policy_summaries,
        "diagnostic_hidden_family_summaries": _hidden_family_summaries(
            replay_rows,
            policy_summaries.keys(),
        ),
        "summary": {
            "rows": len(replay_rows),
            "best_promotable_policy": _best_promotable_policy(policy_summaries),
            "promoted_policy_count": sum(
                1
                for summary in policy_summaries.values()
                if summary["gate_status"] == "promote"
            ),
            "any_positive_changed_label_precision": any(
                (summary.get("changed_label_precision") or 0) > 0
                for summary in policy_summaries.values()
            ),
        },
        "claim_boundary": (
            "validation-development D0 no-call replay over saved E1/E2 hard50 "
            "boundary-guide traces; no new model calls, no holdout use, no scorer "
            "change, and no benchmark claim"
        ),
    }
    return replay_rows, metadata


def write_replay_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    """Write the D0 replay Markdown report."""

    lines = [
        "# Gan 2026 Agentic Hard50 Boundary-Guide Rescue Replay",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "## Experiment Unit",
        "",
        "- Work class: D0 validation hard-slice no-call rescue-gate replay.",
        f"- Rows: {metadata.get('row_count', 0)}",
        "- Split: `validation`, manifest `gan2026_split_v1`.",
        f"- E1 source JSONL: `{metadata.get('e1_source_jsonl_path')}`",
        f"- E2 source JSONL: `{metadata.get('e2_source_jsonl_path')}`",
        f"- Hard50 manifest: `{metadata.get('hard50_manifest_path')}`",
        "- Scorer: existing Gan-compatible Purist first, Pragmatic side-car.",
        "- Parser candidates: not used as prediction-bearing prompt context.",
        "",
        "## Claim Boundary",
        "",
        str(metadata.get("claim_boundary", "")),
        "",
        "## Policy Summary",
        "",
        (
            "| Policy | Eligible | Gate | Purist | Pragmatic | Changed | "
            "Wrong->Correct | Correct->Wrong | Net | Precision | Fallbacks |"
        ),
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy, summary in dict(metadata.get("policy_summaries") or {}).items():
        precision = summary.get("changed_label_precision")
        precision_text = "" if precision is None else f"{precision:.3f}"
        lines.append(
            f"| `{policy}` | {summary['promotion_eligible']} | "
            f"{summary['gate_status']} | {summary['purist_correct']}/"
            f"{summary['rows']} | {summary['pragmatic_correct']}/{summary['rows']} | "
            f"{summary['changed_labels']} | {summary['wrong_to_correct']} | "
            f"{summary['correct_to_wrong']} | {summary['net_purist_gain']} | "
            f"{precision_text} | {summary['fallback_count']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            _interpretation(metadata),
            "",
            "## Changed Labels",
            "",
            "| Row | Policy | Action | Transition | Fallback | Selected | Kind transition |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        for policy, decision in dict(row.get("policies") or {}).items():
            if not decision.get("changed_label"):
                continue
            lines.append(
                f"| {row.get('source_row_index')} | `{policy}` | "
                f"{decision.get('action')} | {decision.get('transition')} | "
                f"`{decision.get('fallback_label')}` | "
                f"`{decision.get('selected_label')}` | "
                f"{decision.get('kind_transition')} |"
            )
    lines.extend(
        [
            "",
            "## Diagnostic Hidden-Family Summary",
            "",
            (
                "This section uses predeclared hard50 family tags from the validation "
                "manifest. It is non-runtime diagnostic context only and is not an "
                "eligible gate feature."
            ),
            "",
            (
                "| Policy | Hidden family | Changed | Wrong->Correct | "
                "Correct->Wrong | Net |"
            ),
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    hidden_summaries = dict(metadata.get("diagnostic_hidden_family_summaries") or {})
    for policy, by_family in hidden_summaries.items():
        for family, summary in dict(by_family).items():
            lines.append(
                f"| `{policy}` | `{family}` | {summary['changed_labels']} | "
                f"{summary['wrong_to_correct']} | {summary['correct_to_wrong']} | "
                f"{summary['net_purist_gain']} |"
            )
    write_markdown_report(path, lines)


def _replay_row(
    e1_row: Mapping[str, Any],
    e2_row: Mapping[str, Any],
    manifest_record: Mapping[str, Any],
) -> dict[str, Any]:
    source_row_index = int(e2_row["source_row_index"])
    e1_traces = dict(e1_row.get("condition_traces") or {})
    e2_trace = dict(e2_row.get("condition_trace") or {})
    e1_fallback_trace = dict(e1_traces[E1_FALLBACK_CONDITION])
    e1_candidate_trace = dict(e1_traces[E1_BOUNDARY_CONDITION])

    gold_monthly = _gold_monthly_frequency(e1_traces, e2_trace, e2_row)
    e1_fallback_label = _trace_label(e1_fallback_trace)
    e1_candidate_label = _trace_label(e1_candidate_trace)
    e2_fallback_label = _trace_label(e2_row) or _trace_label_from_key(
        e2_row,
        "reference_label",
    )
    e2_candidate_label = _trace_label(e2_trace)
    e1_fallback_score = _score_label(e1_fallback_label, gold_monthly)
    e2_fallback_score = _score_label(e2_fallback_label, gold_monthly)

    decisions = {
        "unanimous_frequency_or_cluster_override": _policy_unanimous_e2_override(
            e2_trace=e2_trace,
            gold_monthly=gold_monthly,
            fallback_label=e2_fallback_label,
            fallback_score=e2_fallback_score,
        ),
        "guide_and_vote_agree_override": _policy_e1_e2_agree_override(
            e1_candidate_label=e1_candidate_label,
            e2_candidate_label=e2_candidate_label,
            gold_monthly=gold_monthly,
            fallback_label=e2_fallback_label,
            fallback_score=e2_fallback_score,
        ),
        "cluster_restore_only": _policy_cluster_restore_only(
            candidate_label=e2_candidate_label,
            gold_monthly=gold_monthly,
            fallback_label=e2_fallback_label,
            fallback_score=e2_fallback_score,
        ),
        "higher_burden_only": _policy_higher_burden_only(
            candidate_label=e2_candidate_label,
            gold_monthly=gold_monthly,
            fallback_label=e2_fallback_label,
            fallback_score=e2_fallback_score,
        ),
        "boundary_demotion_block": _policy_boundary_demotion_block(
            candidate_label=e2_candidate_label,
            gold_monthly=gold_monthly,
            fallback_label=e2_fallback_label,
            fallback_score=e2_fallback_score,
        ),
    }
    return {
        "source_row_index": source_row_index,
        "split": e2_row.get("split", "validation"),
        "split_manifest": e2_row.get("split_manifest", "gan2026_split_v1"),
        "gold_monthly_frequency": gold_monthly,
        "hidden_families": list(manifest_record.get("hidden_families") or []),
        "slice_names": list(manifest_record.get("slice_names") or []),
        "fallbacks": {
            "e1_condition": E1_FALLBACK_CONDITION,
            "e1_label": e1_fallback_label,
            "e1_score": e1_fallback_score,
            "e2_condition": E2_FALLBACK_CONDITION,
            "e2_label": e2_fallback_label,
            "e2_score": e2_fallback_score,
        },
        "candidates": {
            "e1_condition": E1_BOUNDARY_CONDITION,
            "e1_label": e1_candidate_label,
            "e1_features": _trace_features(e1_candidate_trace),
            "e2_condition": E2_BOUNDARY_CONDITION,
            "e2_label": e2_candidate_label,
            "e2_features": _trace_features(e2_trace),
        },
        "policies": decisions,
    }


def _policy_unanimous_e2_override(
    *,
    e2_trace: Mapping[str, Any],
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    candidate_label = _trace_label(e2_trace)
    features = _trace_features(e2_trace)
    if (
        candidate_label is not None
        and features["normalized_vote_total"] == 4
        and features["normalized_vote_unique_count"] == 1
        and _is_frequency_or_cluster_label(candidate_label)
    ):
        return _decision(
            selected_label=candidate_label,
            selected_condition=E2_BOUNDARY_CONDITION,
            action="accept_unanimous_frequency_or_cluster_e2",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _fallback_decision(
        fallback_label=fallback_label,
        fallback_score=fallback_score,
        gold_monthly=gold_monthly,
        action="fallback_self_consistency_not_unanimous_frequency_or_cluster",
    )


def _policy_e1_e2_agree_override(
    *,
    e1_candidate_label: str | None,
    e2_candidate_label: str | None,
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    if (
        e1_candidate_label is not None
        and e2_candidate_label is not None
        and _normalized_label(e1_candidate_label) == _normalized_label(e2_candidate_label)
        and _label_kind(e2_candidate_label) not in BOUNDARY_KINDS
    ):
        return _decision(
            selected_label=e2_candidate_label,
            selected_condition=E2_BOUNDARY_CONDITION,
            action="accept_e1_boundary_and_e2_vote_agree",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _fallback_decision(
        fallback_label=fallback_label,
        fallback_score=fallback_score,
        gold_monthly=gold_monthly,
        action="fallback_self_consistency_no_e1_e2_safe_agreement",
    )


def _policy_cluster_restore_only(
    *,
    candidate_label: str | None,
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    if _has_cluster_burden(candidate_label) and not _has_cluster_burden(fallback_label):
        return _decision(
            selected_label=candidate_label,
            selected_condition=E2_BOUNDARY_CONDITION,
            action="accept_cluster_restore_only",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _fallback_decision(
        fallback_label=fallback_label,
        fallback_score=fallback_score,
        gold_monthly=gold_monthly,
        action="fallback_self_consistency_no_cluster_restore",
    )


def _policy_higher_burden_only(
    *,
    candidate_label: str | None,
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    if _strictly_higher_numeric_burden(candidate_label, fallback_label):
        return _decision(
            selected_label=candidate_label,
            selected_condition=E2_BOUNDARY_CONDITION,
            action="accept_higher_numeric_burden_only",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _fallback_decision(
        fallback_label=fallback_label,
        fallback_score=fallback_score,
        gold_monthly=gold_monthly,
        action="fallback_self_consistency_no_strict_higher_burden",
    )


def _policy_boundary_demotion_block(
    *,
    candidate_label: str | None,
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    if candidate_label is None:
        return _fallback_decision(
            fallback_label=fallback_label,
            fallback_score=fallback_score,
            gold_monthly=gold_monthly,
            action="fallback_self_consistency_missing_boundary_candidate",
        )
    if _introduces_boundary_demotion(candidate_label, fallback_label):
        return _fallback_decision(
            fallback_label=fallback_label,
            fallback_score=fallback_score,
            gold_monthly=gold_monthly,
            action="fallback_self_consistency_block_boundary_demotion",
        )
    return _decision(
        selected_label=candidate_label,
        selected_condition=E2_BOUNDARY_CONDITION,
        action="accept_e2_unless_boundary_demotion",
        gold_monthly=gold_monthly,
        fallback_label=fallback_label,
        fallback_score=fallback_score,
    )


def _fallback_decision(
    *,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
    gold_monthly: float,
    action: str,
) -> dict[str, Any]:
    return _decision(
        selected_label=fallback_label,
        selected_condition=E2_FALLBACK_CONDITION,
        action=action,
        gold_monthly=gold_monthly,
        fallback_label=fallback_label,
        fallback_score=fallback_score,
    )


def _decision(
    *,
    selected_label: str | None,
    selected_condition: str,
    action: str,
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    selected_score = _score_label(selected_label, gold_monthly)
    changed_label = _normalized_label(selected_label) != _normalized_label(fallback_label)
    return {
        "selected_condition": selected_condition,
        "selected_label": selected_label,
        "selected_kind": _label_kind(selected_label),
        "selected_has_cluster_burden": _has_cluster_burden(selected_label),
        "fallback_label": fallback_label,
        "fallback_kind": _label_kind(fallback_label),
        "fallback_has_cluster_burden": _has_cluster_burden(fallback_label),
        "action": action,
        "changed_label": changed_label,
        "transition": _transition(fallback_score, selected_score, changed_label),
        "kind_transition": f"{_label_kind(fallback_label)}->{_label_kind(selected_label)}",
        "score": selected_score,
    }


def _score_label(label: str | None, gold_monthly: float) -> dict[str, Any]:
    if label is None:
        return {
            "predicted_monthly_frequency": None,
            "predicted_kind": "no_prediction",
            "predicted_has_cluster_burden": False,
            "predicted_purist_category": None,
            "gold_purist_category": str(map_purist(gold_monthly)),
            "purist_correct": False,
            "predicted_pragmatic_category": None,
            "gold_pragmatic_category": str(map_pragmatic(gold_monthly)),
            "pragmatic_correct": False,
        }
    try:
        record = label_to_frequency_record(str(label))
    except ValueError:
        return {
            "predicted_monthly_frequency": None,
            "predicted_kind": "unparseable",
            "predicted_has_cluster_burden": _has_cluster_burden(label),
            "predicted_purist_category": None,
            "gold_purist_category": str(map_purist(gold_monthly)),
            "purist_correct": False,
            "predicted_pragmatic_category": None,
            "gold_pragmatic_category": str(map_pragmatic(gold_monthly)),
            "pragmatic_correct": False,
        }
    predicted_monthly = record.monthly_frequency
    return {
        "predicted_monthly_frequency": predicted_monthly,
        "predicted_kind": str(record.kind),
        "predicted_has_cluster_burden": _has_cluster_burden(label),
        "predicted_purist_category": str(map_purist(predicted_monthly)),
        "gold_purist_category": str(map_purist(gold_monthly)),
        "purist_correct": map_purist(predicted_monthly) == map_purist(gold_monthly),
        "predicted_pragmatic_category": str(map_pragmatic(predicted_monthly)),
        "gold_pragmatic_category": str(map_pragmatic(gold_monthly)),
        "pragmatic_correct": map_pragmatic(predicted_monthly)
        == map_pragmatic(gold_monthly),
    }


def _transition(
    fallback_score: Mapping[str, Any],
    selected_score: Mapping[str, Any],
    changed_label: bool,
) -> str:
    fallback_correct = bool(fallback_score.get("purist_correct"))
    selected_correct = bool(selected_score.get("purist_correct"))
    if not changed_label:
        return "unchanged_correct" if selected_correct else "unchanged_wrong"
    if not fallback_correct and selected_correct:
        return "wrong_to_correct"
    if fallback_correct and not selected_correct:
        return "correct_to_wrong"
    if selected_correct:
        return "changed_both_correct"
    return "changed_both_wrong"


def _summarize_policy(
    replay_rows: Sequence[Mapping[str, Any]],
    policy: str,
) -> dict[str, Any]:
    decisions = [dict(row["policies"][policy]) for row in replay_rows]
    transition_counts = Counter(decision["transition"] for decision in decisions)
    action_counts = Counter(decision["action"] for decision in decisions)
    kind_transition_counts = Counter(
        str(decision.get("kind_transition")) for decision in decisions
    )
    changed_labels = sum(bool(decision["changed_label"]) for decision in decisions)
    wrong_to_correct = transition_counts["wrong_to_correct"]
    correct_to_wrong = transition_counts["correct_to_wrong"]
    precision = wrong_to_correct / changed_labels if changed_labels else None
    promotion_eligible = POLICY_ELIGIBILITY[policy]
    gate_status = _gate_status(
        promotion_eligible=promotion_eligible,
        changed_labels=changed_labels,
        changed_label_precision=precision,
        wrong_to_correct=wrong_to_correct,
        correct_to_wrong=correct_to_wrong,
    )
    return {
        "rows": len(replay_rows),
        "promotion_eligible": promotion_eligible,
        "gate_status": gate_status,
        "purist_correct": sum(
            bool(decision["score"].get("purist_correct")) for decision in decisions
        ),
        "pragmatic_correct": sum(
            bool(decision["score"].get("pragmatic_correct")) for decision in decisions
        ),
        "changed_labels": changed_labels,
        "fallback_count": sum(
            decision["selected_condition"] == E2_FALLBACK_CONDITION
            for decision in decisions
        ),
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "net_purist_gain": wrong_to_correct - correct_to_wrong,
        "changed_label_precision": precision,
        "transition_counts": dict(transition_counts),
        "action_counts": dict(action_counts),
        "kind_transition_counts": dict(kind_transition_counts),
    }


def _gate_status(
    *,
    promotion_eligible: bool,
    changed_labels: int,
    changed_label_precision: float | None,
    wrong_to_correct: int,
    correct_to_wrong: int,
) -> str:
    if not promotion_eligible:
        return "diagnostic_only"
    net_gain = wrong_to_correct - correct_to_wrong
    if (
        changed_labels
        and net_gain >= 3
        and (changed_label_precision or 0) >= 0.60
        and correct_to_wrong <= 1
    ):
        return "promote"
    return "reject"


def _hidden_family_summaries(
    replay_rows: Sequence[Mapping[str, Any]],
    policies: Sequence[str],
) -> dict[str, dict[str, dict[str, int]]]:
    summaries: dict[str, dict[str, dict[str, int]]] = {}
    for policy in policies:
        by_family: dict[str, Counter[str]] = defaultdict(Counter)
        for row in replay_rows:
            families = row.get("hidden_families") or ["unclassified"]
            decision = dict(row["policies"][policy])
            for family in families:
                counter = by_family[str(family)]
                counter["changed_labels"] += int(bool(decision["changed_label"]))
                counter["wrong_to_correct"] += int(
                    decision["transition"] == "wrong_to_correct"
                )
                counter["correct_to_wrong"] += int(
                    decision["transition"] == "correct_to_wrong"
                )
        summaries[policy] = {
            family: {
                "changed_labels": counter["changed_labels"],
                "wrong_to_correct": counter["wrong_to_correct"],
                "correct_to_wrong": counter["correct_to_wrong"],
                "net_purist_gain": (
                    counter["wrong_to_correct"] - counter["correct_to_wrong"]
                ),
            }
            for family, counter in sorted(by_family.items())
        }
    return summaries


def _best_promotable_policy(policy_summaries: Mapping[str, Mapping[str, Any]]) -> str | None:
    promotable = [
        (policy, summary)
        for policy, summary in policy_summaries.items()
        if summary.get("gate_status") == "promote"
    ]
    if not promotable:
        return None
    return max(
        promotable,
        key=lambda item: (
            item[1].get("net_purist_gain", 0),
            item[1].get("changed_label_precision") or 0,
            item[1].get("purist_correct", 0),
        ),
    )[0]


def _trace_features(trace: Mapping[str, Any]) -> dict[str, Any]:
    vote = dict(trace.get("normalized_label_vote") or {})
    normalized_labels = [str(label) for label in vote.get("normalized_labels") or []]
    if not normalized_labels:
        normalized_labels = [
            str(result.get("normalized_vote_label"))
            for result in trace.get("model_call_results") or []
            if result.get("normalized_vote_label") is not None
        ]
    vote_counts = Counter(normalized_labels)
    repair_event_counts = Counter(vote.get("repair_event_counts") or {})
    for result in trace.get("model_call_results") or []:
        repair_event_counts.update(result.get("normalized_vote_repair_events") or [])
    raw_labels = [
        result.get("raw_model_final_label")
        for result in trace.get("model_call_results") or []
        if result.get("raw_model_final_label") is not None
    ]
    decision_labels = [
        dict(result.get("decision_record") or {}).get("final_label")
        for result in trace.get("model_call_results") or []
        if dict(result.get("decision_record") or {}).get("final_label") is not None
    ]
    return {
        "final_label": _trace_label(trace),
        "final_kind": _label_kind(_trace_label(trace)),
        "introduces_boundary_label": _label_kind(_trace_label(trace)) in BOUNDARY_KINDS,
        "has_cluster_burden": _has_cluster_burden(_trace_label(trace)),
        "normalized_vote_total": sum(vote_counts.values()),
        "normalized_vote_unique_count": len(vote_counts),
        "normalized_vote_entropy": _vote_entropy(vote_counts),
        "normalized_vote_counts": dict(sorted(vote_counts.items())),
        "repair_event_counts": dict(sorted(repair_event_counts.items())),
        "raw_model_final_labels": raw_labels,
        "decision_record_final_labels": decision_labels,
    }


def _vote_entropy(vote_counts: Counter[str]) -> float:
    total = sum(vote_counts.values())
    if not total:
        return 0.0
    entropy = 0.0
    for count in vote_counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)
    return round(entropy, 6)


def _strictly_higher_numeric_burden(
    candidate_label: str | None,
    fallback_label: str | None,
) -> bool:
    candidate = _frequency_record(candidate_label)
    fallback = _frequency_record(fallback_label)
    if candidate is None or fallback is None:
        return False
    if str(candidate.kind) != "frequency" or str(fallback.kind) != "frequency":
        return False
    return candidate.monthly_frequency > fallback.monthly_frequency


def _is_frequency_or_cluster_label(label: str | None) -> bool:
    if _has_cluster_burden(label):
        return True
    kind = _label_kind(label)
    return kind not in {"no_prediction", "unparseable", *BOUNDARY_KINDS}


def _introduces_boundary_demotion(
    candidate_label: str | None,
    fallback_label: str | None,
) -> bool:
    return (
        _label_kind(candidate_label) in BOUNDARY_KINDS
        and _is_frequency_or_cluster_label(fallback_label)
    )


def _frequency_record(label: str | None) -> Any | None:
    if label is None:
        return None
    try:
        return label_to_frequency_record(str(label))
    except ValueError:
        return None


def _label_kind(label: str | None) -> str:
    record = _frequency_record(label)
    if record is None:
        return "no_prediction" if label is None else "unparseable"
    return str(record.kind)


def _has_cluster_burden(label: str | None) -> bool:
    if label is None:
        return False
    normalized = _normalized_label(label) or ""
    return "cluster" in normalized and "per cluster" in normalized


def _normalized_label(label: str | None) -> str | None:
    if label is None:
        return None
    record = _frequency_record(label)
    if record is not None:
        return str(record.normalized_label)
    return " ".join(str(label).strip().lower().split())


def _trace_label(trace: Mapping[str, Any]) -> str | None:
    label = trace.get("final_label")
    if label is None:
        label = dict(trace.get("normalized_label_vote") or {}).get("selected_label")
    return str(label) if label is not None else None


def _trace_label_from_key(row: Mapping[str, Any], key: str) -> str | None:
    label = row.get(key)
    return str(label) if label is not None else None


def _gold_monthly_frequency(
    e1_traces: Mapping[str, Any],
    e2_trace: Mapping[str, Any],
    e2_row: Mapping[str, Any],
) -> float:
    for trace in (*e1_traces.values(), e2_trace):
        trace_score = dict(trace.get("final_comparison") or {})
        if trace_score.get("gold_monthly_frequency") is not None:
            return float(trace_score["gold_monthly_frequency"])
        for result in trace.get("model_call_results") or []:
            comparison = dict(result.get("comparison") or {})
            if comparison.get("gold_monthly_frequency") is not None:
                return float(comparison["gold_monthly_frequency"])
    reference_comparison = dict(e2_row.get("reference_comparison") or {})
    if reference_comparison.get("gold_monthly_frequency") is not None:
        return float(reference_comparison["gold_monthly_frequency"])
    raise ValueError("Saved E1/E2 trace row does not include gold_monthly_frequency")


def _rows_by_source_index(rows: Sequence[Mapping[str, Any]]) -> dict[int, Mapping[str, Any]]:
    by_index: dict[int, Mapping[str, Any]] = {}
    for row in rows:
        source_row_index = row.get("source_row_index")
        if source_row_index is None:
            continue
        by_index[int(source_row_index)] = row
    return by_index


def _first_value(
    rows: Sequence[Mapping[str, Any]],
    key: str,
    default: str,
) -> str:
    for row in rows:
        value = row.get(key)
        if value is not None:
            return str(value)
    return default


def _interpretation(metadata: Mapping[str, Any]) -> str:
    best = dict(metadata.get("summary") or {}).get("best_promotable_policy")
    if best:
        return (
            f"`{best}` passes the predeclared D0 no-call gate. Treat it as a "
            "validation-development promote signal only; it does not authorize "
            "validation250 or holdout escalation."
        )
    if dict(metadata.get("summary") or {}).get("any_positive_changed_label_precision"):
        return (
            "No D0 no-call rescue policy passed the predeclared promotion gate, "
            "but at least one policy produced a positive changed-label precision. "
            "Keep D0 as diagnostic and move to D1 boundary audit prompt v2."
        )
    return (
        "No D0 no-call rescue policy passed the predeclared promotion gate or "
        "produced a positive changed-label precision. Per the D-series stop "
        "rules, D1 is still needed before stopping the branch on this criterion."
    )


def _load_manifest_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [dict(record) for record in payload.get("records", [])]


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run D0 no-call boundary-guide rescue replay over saved E1/E2 traces."
    )
    parser.add_argument("--e1-jsonl", type=Path, required=True)
    parser.add_argument("--e2-jsonl", type=Path, required=True)
    parser.add_argument("--manifest-json", type=Path, required=True)
    parser.add_argument("--jsonl", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--overwrite-existing", action="store_true")
    args = parser.parse_args(argv)
    if not args.overwrite_existing:
        existing = [path for path in (args.jsonl, args.markdown) if path.exists()]
        if existing:
            parser.error(
                "output artifact already exists; use --overwrite-existing to replace: "
                + ", ".join(str(path) for path in existing)
            )
    rows, metadata = run_boundary_guide_rescue_replay(
        e1_rows=load_jsonl_rows(args.e1_jsonl),
        e2_rows=load_jsonl_rows(args.e2_jsonl),
        manifest_records=_load_manifest_records(args.manifest_json),
        e1_jsonl_path=args.e1_jsonl,
        e2_jsonl_path=args.e2_jsonl,
        manifest_path=args.manifest_json,
    )
    write_jsonl_rows(rows, args.jsonl)
    write_replay_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
