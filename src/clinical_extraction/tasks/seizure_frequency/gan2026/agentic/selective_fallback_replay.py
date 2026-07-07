"""No-call selective fallback replay for Gan 2026 agentic traces."""

from __future__ import annotations

import argparse
import json
from collections import Counter
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

FALLBACK_CONDITION = "single_self_consistency_temperature"
TOOL_CONDITION = "single_agent_tools"
MULTI_AGENT_CONDITION = "multi_agent_matched"
RISKY_ORACLE_FAMILIES = {
    "seizure_free_duration",
    "competing_semiologies",
    "cluster_burden",
}

POLICY_ELIGIBILITY = {
    "all_agree_tool_accept": True,
    "all_agree_multi_accept": True,
    "boundary_coordinator_agree": True,
    "no_seizure_free_introduction": True,
    "raw_repair_disagreement_fallback": True,
    "manifest_family_oracle": False,
}


def run_selective_fallback_replay(
    rows: Sequence[Mapping[str, Any]],
    *,
    manifest_records: Sequence[Mapping[str, Any]],
    input_jsonl_path: Path | None = None,
    manifest_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Replay saved hard50 traces through conservative no-call policies."""

    manifest_by_source_index = {
        int(record["source_row_index"]): dict(record)
        for record in manifest_records
        if record.get("source_row_index") is not None
    }
    replay_rows = [
        _replay_row(row, manifest_by_source_index.get(int(row["source_row_index"]), {}))
        for row in rows
    ]
    policy_summaries = {
        policy: _summarize_policy(replay_rows, policy) for policy in POLICY_ELIGIBILITY
    }
    metadata = {
        "artifact_kind": "gan2026_agentic_selective_fallback_replay",
        "date": datetime.now(UTC).date().isoformat(),
        "run_started_at_utc": datetime.now(UTC).isoformat(),
        "mode": "no_call_replay",
        "pipeline_family": "agentic_matched_budget",
        "split": "validation",
        "split_manifest": _first_value(rows, "split_manifest", "gan2026_split_v1"),
        "row_count": len(replay_rows),
        "fallback_condition": FALLBACK_CONDITION,
        "source_jsonl_path": str(input_jsonl_path) if input_jsonl_path else None,
        "hard50_manifest_path": str(manifest_path) if manifest_path else None,
        "policies": {
            policy: {"promotion_eligible": eligible}
            for policy, eligible in POLICY_ELIGIBILITY.items()
        },
        "policy_summaries": policy_summaries,
        "summary": {
            "rows": len(replay_rows),
            "best_promotable_policy": _best_promotable_policy(policy_summaries),
            "promoted_policy_count": sum(
                1 for summary in policy_summaries.values() if summary["gate_status"] == "promote"
            ),
            "diagnostic_policy_count": sum(
                1
                for summary in policy_summaries.values()
                if summary["gate_status"] == "diagnostic_only"
            ),
        },
        "claim_boundary": (
            "validation-development no-call replay over saved hard50 traces; no "
            "new model calls, no holdout use, no scorer change, and no benchmark claim"
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
    """Write a compact markdown report for selective fallback replay."""

    lines = [
        "# Gan 2026 Agentic Hard50 Selective Fallback Replay",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "## Experiment Unit",
        "",
        "- Work class: validation hard-slice no-call selective-action replay.",
        f"- Rows: {metadata.get('row_count', 0)}",
        f"- Fallback comparator: `{metadata.get('fallback_condition')}`",
        f"- Source JSONL: `{metadata.get('source_jsonl_path')}`",
        f"- Hard50 manifest: `{metadata.get('hard50_manifest_path')}`",
        "- Scorer: existing Gan-compatible Purist first, Pragmatic side-car.",
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
            "## Row-Level Changed Labels",
            "",
            "| Row | Policy | Action | Transition | Fallback | Selected | Families |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        families = ", ".join(row.get("hidden_families") or [])
        for policy, decision in dict(row.get("policies") or {}).items():
            if not decision.get("changed_label"):
                continue
            lines.append(
                f"| {row.get('source_row_index')} | `{policy}` | "
                f"{decision.get('action')} | {decision.get('transition')} | "
                f"`{row.get('fallback_label')}` | `{decision.get('selected_label')}` | "
                f"{families} |"
            )
    write_markdown_report(path, lines)


def _replay_row(
    row: Mapping[str, Any],
    manifest_record: Mapping[str, Any],
) -> dict[str, Any]:
    source_row_index = int(row["source_row_index"])
    traces = dict(row.get("condition_traces") or {})
    fallback_trace = dict(traces[FALLBACK_CONDITION])
    fallback_label = _trace_label(fallback_trace)
    gold_monthly = _gold_monthly_frequency(traces)
    fallback_score = _score_label(fallback_label, gold_monthly)
    decisions = {
        "all_agree_tool_accept": _policy_accept_if_all_agree(
            traces=traces,
            candidate_condition=TOOL_CONDITION,
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
            fallback_action="fallback_self_consistency",
        ),
        "all_agree_multi_accept": _policy_accept_if_all_agree(
            traces=traces,
            candidate_condition=MULTI_AGENT_CONDITION,
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
            fallback_action="fallback_self_consistency",
        ),
        "boundary_coordinator_agree": _policy_boundary_coordinator_agree(
            traces=traces,
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        ),
        "no_seizure_free_introduction": _policy_no_seizure_free_introduction(
            traces=traces,
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        ),
        "raw_repair_disagreement_fallback": _policy_raw_repair_disagreement_fallback(
            traces=traces,
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        ),
        "manifest_family_oracle": _policy_manifest_family_oracle(
            traces=traces,
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
            hidden_families=tuple(manifest_record.get("hidden_families") or ()),
        ),
    }
    return {
        "source_row_index": source_row_index,
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "fallback_condition": FALLBACK_CONDITION,
        "fallback_label": fallback_label,
        "fallback_score": fallback_score,
        "gold_monthly_frequency": gold_monthly,
        "hidden_families": list(manifest_record.get("hidden_families") or []),
        "slice_names": list(manifest_record.get("slice_names") or []),
        "policies": decisions,
    }


def _policy_accept_if_all_agree(
    *,
    traces: Mapping[str, Any],
    candidate_condition: str,
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
    fallback_action: str,
) -> dict[str, Any]:
    candidate_trace = dict(traces.get(candidate_condition) or {})
    candidate_label = _trace_label(candidate_trace)
    if candidate_label is not None and _normalized_labels_all_agree(candidate_trace):
        return _decision(
            selected_label=candidate_label,
            selected_condition=candidate_condition,
            action=f"accept_{candidate_condition}",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _decision(
        selected_label=fallback_label,
        selected_condition=FALLBACK_CONDITION,
        action=fallback_action,
        gold_monthly=gold_monthly,
        fallback_label=fallback_label,
        fallback_score=fallback_score,
    )


def _policy_boundary_coordinator_agree(
    *,
    traces: Mapping[str, Any],
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    multi_trace = dict(traces.get(MULTI_AGENT_CONDITION) or {})
    role_labels = _role_labels(multi_trace)
    boundary_label = role_labels.get("boundary_agent")
    coordinator_label = role_labels.get("coordinator_agent")
    candidate_label = _trace_label(multi_trace)
    fallback_kind = _label_kind(fallback_label)
    candidate_kind = _label_kind(candidate_label)
    introduces_seizure_free = candidate_kind == "seizure_free" and fallback_kind != "seizure_free"
    if (
        boundary_label is not None
        and coordinator_label is not None
        and boundary_label == coordinator_label
        and candidate_label == coordinator_label
        and not introduces_seizure_free
    ):
        return _decision(
            selected_label=candidate_label,
            selected_condition=MULTI_AGENT_CONDITION,
            action="accept_boundary_coordinator_agree",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _decision(
        selected_label=fallback_label,
        selected_condition=FALLBACK_CONDITION,
        action="fallback_self_consistency",
        gold_monthly=gold_monthly,
        fallback_label=fallback_label,
        fallback_score=fallback_score,
    )


def _policy_no_seizure_free_introduction(
    *,
    traces: Mapping[str, Any],
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    candidate_label = _trace_label(dict(traces.get(MULTI_AGENT_CONDITION) or {}))
    fallback_kind = _label_kind(fallback_label)
    candidate_kind = _label_kind(candidate_label)
    if candidate_label is not None and not (
        candidate_kind == "seizure_free"
        and fallback_kind in {"frequency", "unknown", "no_reference", "unresolved_multiple"}
    ):
        return _decision(
            selected_label=candidate_label,
            selected_condition=MULTI_AGENT_CONDITION,
            action="accept_multi_unless_seizure_free_introduction",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _decision(
        selected_label=fallback_label,
        selected_condition=FALLBACK_CONDITION,
        action="fallback_self_consistency",
        gold_monthly=gold_monthly,
        fallback_label=fallback_label,
        fallback_score=fallback_score,
    )


def _policy_raw_repair_disagreement_fallback(
    *,
    traces: Mapping[str, Any],
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
) -> dict[str, Any]:
    multi_trace = dict(traces.get(MULTI_AGENT_CONDITION) or {})
    candidate_label = _trace_label(multi_trace)
    if candidate_label is not None and not _has_semantic_repair_disagreement(multi_trace):
        return _decision(
            selected_label=candidate_label,
            selected_condition=MULTI_AGENT_CONDITION,
            action="accept_multi_no_raw_repair_kind_disagreement",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _decision(
        selected_label=fallback_label,
        selected_condition=FALLBACK_CONDITION,
        action="fallback_self_consistency",
        gold_monthly=gold_monthly,
        fallback_label=fallback_label,
        fallback_score=fallback_score,
    )


def _policy_manifest_family_oracle(
    *,
    traces: Mapping[str, Any],
    gold_monthly: float,
    fallback_label: str | None,
    fallback_score: Mapping[str, Any],
    hidden_families: Sequence[str],
) -> dict[str, Any]:
    candidate_label = _trace_label(dict(traces.get(MULTI_AGENT_CONDITION) or {}))
    if candidate_label is not None and not (set(hidden_families) & RISKY_ORACLE_FAMILIES):
        return _decision(
            selected_label=candidate_label,
            selected_condition=MULTI_AGENT_CONDITION,
            action="accept_multi_manifest_family_oracle",
            gold_monthly=gold_monthly,
            fallback_label=fallback_label,
            fallback_score=fallback_score,
        )
    return _decision(
        selected_label=fallback_label,
        selected_condition=FALLBACK_CONDITION,
        action="fallback_manifest_family_oracle",
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
    changed_label = selected_label != fallback_label
    return {
        "selected_condition": selected_condition,
        "selected_label": selected_label,
        "selected_kind": _label_kind(selected_label),
        "action": action,
        "changed_label": changed_label,
        "transition": _transition(fallback_score, selected_score, changed_label),
        "score": selected_score,
    }


def _score_label(label: str | None, gold_monthly: float) -> dict[str, Any]:
    if label is None:
        return {
            "predicted_monthly_frequency": None,
            "predicted_kind": "no_prediction",
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
        "predicted_purist_category": str(map_purist(predicted_monthly)),
        "gold_purist_category": str(map_purist(gold_monthly)),
        "purist_correct": map_purist(predicted_monthly) == map_purist(gold_monthly),
        "predicted_pragmatic_category": str(map_pragmatic(predicted_monthly)),
        "gold_pragmatic_category": str(map_pragmatic(gold_monthly)),
        "pragmatic_correct": map_pragmatic(predicted_monthly) == map_pragmatic(gold_monthly),
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
        (
            str(row.get("fallback_score", {}).get("predicted_kind")),
            str(decision.get("selected_kind")),
        )
        for row, decision in zip(replay_rows, decisions, strict=True)
    )
    changed_labels = sum(bool(decision["changed_label"]) for decision in decisions)
    wrong_to_correct = transition_counts["wrong_to_correct"]
    correct_to_wrong = transition_counts["correct_to_wrong"]
    promotion_eligible = POLICY_ELIGIBILITY[policy]
    gate_status = _gate_status(
        promotion_eligible=promotion_eligible,
        changed_labels=changed_labels,
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
            decision["selected_condition"] == FALLBACK_CONDITION for decision in decisions
        ),
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "net_purist_gain": wrong_to_correct - correct_to_wrong,
        "changed_label_precision": (wrong_to_correct / changed_labels if changed_labels else None),
        "transition_counts": dict(transition_counts),
        "action_counts": dict(action_counts),
        "kind_transition_counts": {
            f"{before}->{after}": count for (before, after), count in kind_transition_counts.items()
        },
    }


def _gate_status(
    *,
    promotion_eligible: bool,
    changed_labels: int,
    wrong_to_correct: int,
    correct_to_wrong: int,
) -> str:
    if not promotion_eligible:
        return "diagnostic_only"
    if (
        changed_labels
        and wrong_to_correct > correct_to_wrong
        and wrong_to_correct - correct_to_wrong >= 3
        and correct_to_wrong <= 2
    ):
        return "promote"
    return "reject"


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
        ),
    )[0]


def _trace_label(trace: Mapping[str, Any]) -> str | None:
    label = trace.get("final_label")
    if label is None:
        label = dict(trace.get("normalized_label_vote") or {}).get("selected_label")
    return str(label) if label is not None else None


def _normalized_labels_all_agree(trace: Mapping[str, Any]) -> bool:
    vote = dict(trace.get("normalized_label_vote") or {})
    labels = [str(label) for label in vote.get("normalized_labels") or []]
    if not labels:
        labels = [
            str(result.get("normalized_vote_label"))
            for result in trace.get("model_call_results") or []
            if result.get("normalized_vote_label") is not None
        ]
    return bool(labels) and len(set(labels)) == 1


def _role_labels(trace: Mapping[str, Any]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for result in trace.get("model_call_results") or []:
        role = result.get("call_role")
        label = result.get("normalized_vote_label")
        if role is not None and label is not None:
            labels[str(role)] = str(label)
    return labels


def _has_semantic_repair_disagreement(trace: Mapping[str, Any]) -> bool:
    for result in trace.get("model_call_results") or []:
        labels = [
            result.get("raw_model_final_label"),
            dict(result.get("decision_record") or {}).get("final_label"),
            result.get("normalized_vote_label"),
        ]
        kinds = {_label_kind(str(label)) for label in labels if label is not None}
        if len(kinds) > 1:
            return True
    return False


def _label_kind(label: str | None) -> str:
    if label is None:
        return "no_prediction"
    try:
        return str(label_to_frequency_record(str(label)).kind)
    except ValueError:
        return "unparseable"


def _gold_monthly_frequency(traces: Mapping[str, Any]) -> float:
    for trace in traces.values():
        for result in trace.get("model_call_results") or []:
            comparison = dict(result.get("comparison") or {})
            if comparison.get("gold_monthly_frequency") is not None:
                return float(comparison["gold_monthly_frequency"])
    raise ValueError("Saved trace row does not include gold_monthly_frequency")


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
            f"`{best}` passes the predeclared selective-action gate. Treat it as "
            "a validation-development promote signal only; implement and rerun "
            "on the frozen hard50 trace before broader escalation."
        )
    return (
        "No promotable selective fallback policy passed the predeclared gate. "
        "Use this as a revise/reject signal and move to tool-context ablation "
        "before any new live multi-agent calls."
    )


def _load_manifest_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [dict(record) for record in payload.get("records", [])]


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run no-call selective fallback replay over saved agentic traces."
    )
    parser.add_argument("--input-jsonl", type=Path, required=True)
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
    rows = load_jsonl_rows(args.input_jsonl)
    manifest_records = _load_manifest_records(args.manifest_json)
    replay_rows, metadata = run_selective_fallback_replay(
        rows,
        manifest_records=manifest_records,
        input_jsonl_path=args.input_jsonl,
        manifest_path=args.manifest_json,
    )
    write_jsonl_rows(replay_rows, args.jsonl)
    write_replay_report(replay_rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
