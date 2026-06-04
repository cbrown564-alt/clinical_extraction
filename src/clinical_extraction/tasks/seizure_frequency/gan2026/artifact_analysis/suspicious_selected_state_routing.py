"""Materialize Gan 2026 suspicious selected-state routing diagnostics."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_union import (  # noqa: E501
    DEFAULT_RICH_STATE_REPLAY_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.rq1_rq2_control_panels import (  # noqa: E501
    DEFAULT_PANEL_JSONL_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_suspicious_selected_state_routing_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_suspicious_selected_state_routing_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_suspicious_selected_state_routing_answer_2026-06-04.md"
)
DEFAULT_PROTOCOL_PATH = Path(
    "docs/research/gan2026_ambiguity_ownership_protocol_2026-06-04.md"
)


def build_suspicious_routing_rows(
    saved_rows: Sequence[Mapping[str, Any]],
    *,
    panel_rows: Sequence[Mapping[str, Any]] = (),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    panels_by_source = {int(row["source_row_index"]): row for row in panel_rows}
    rows = [
        _suspicious_routing_row(
            row,
            panel_row=panels_by_source.get(int(row["source_row_index"])),
        )
        for row in saved_rows
    ]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_suspicious_routing_rows(rows)


def summarize_suspicious_routing_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    action_counts = Counter(str(row["suspicious_state_action"]) for row in rows)
    flag_counts = Counter(flag for row in rows for flag in row["suspicious_state_flags"])
    scorable_rows = [row for row in rows if row["final_policy_under_test"]["scorable"]]
    comparator_correct = sum(bool(row["comparison"]["comparator_correct"]) for row in rows)
    final_correct = sum(bool(row["comparison"]["final_policy_correct"]) for row in scorable_rows)
    w_to_c_rows = [
        int(row["source_row_index"])
        for row in scorable_rows
        if row["comparison"]["w_to_c_against_comparator"]
    ]
    c_to_w_rows = [
        int(row["source_row_index"])
        for row in scorable_rows
        if row["comparison"]["c_to_w_against_comparator"]
    ]
    suspicious_rows = [row for row in rows if row["suspicious_state_flags"]]
    no_call_resolution_rows = [
        int(row["source_row_index"])
        for row in rows
        if row["suspicious_state_flags"]
        and row["suspicious_state_action"] in {"route_unknown", "route_review"}
    ]
    return {
        "artifact_kind": "gan2026_suspicious_selected_state_routing",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "source_artifact": str(DEFAULT_RICH_STATE_REPLAY_PATH),
        "row_count": len(rows),
        "claim_language": (
            "Validation-development saved-artifact suspicious-state routing diagnostic "
            "only. No new live LLM calls, locked-test inspection, whole-pipeline "
            "promotion, or benchmark-comparable claim."
        ),
        "metrics": {
            "suspicious_state_rows": len(suspicious_rows),
            "non_suspicious_rows": len(rows) - len(suspicious_rows),
            "route_unknown_rows": action_counts["route_unknown"],
            "route_review_rows": action_counts["route_review"],
            "render_rows": action_counts["render"],
            "comparator_correct_rows": comparator_correct,
            "final_policy_scorable_rows": len(scorable_rows),
            "final_policy_correct_rows": final_correct,
            "w_to_c_against_comparator_rows": len(w_to_c_rows),
            "c_to_w_against_comparator_rows": len(c_to_w_rows),
            "exact_trace_rate": _safe_rate(
                sum(row["selected_evidence_status"]["exact_trace"] for row in rows),
                len(rows),
            ),
            "suspicious_no_call_resolution_rows": len(no_call_resolution_rows),
        },
        "action_counts": dict(sorted(action_counts.items())),
        "flag_counts": dict(sorted(flag_counts.items())),
        "w_to_c_source_row_indices": w_to_c_rows,
        "c_to_w_source_row_indices": c_to_w_rows,
        "suspicious_no_call_resolution_source_row_indices": no_call_resolution_rows,
        "by_hidden_family": _by_hidden_family(rows),
        "verifier_decision": _verifier_decision(rows, c_to_w_rows),
    }


def write_suspicious_routing_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_suspicious_routing_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
    protocol_path: Path = DEFAULT_PROTOCOL_PATH,
) -> None:
    metrics = metadata["metrics"]
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gan 2026 Suspicious Selected-State Routing Answer",
        "",
        "This is a no-call validation-development diagnostic over saved rich "
        "selected-state hard-panel replay artifacts.",
        "",
        "## Answer",
        "",
        (
            "Deterministic suspicious-state routing is useful as a no-call safety and "
            "review layer, but it is not enough to replace a selective verifier for the "
            "remaining unresolved suspicious rows. The pass flagged "
            f"{metrics['suspicious_state_rows']}/{metadata['row_count']} "
            "rows, routed "
            f"{metrics['route_unknown_rows']} to `unknown` and "
            f"{metrics['route_review_rows']} to review, with "
            f"{metrics['w_to_c_against_comparator_rows']} W->C and "
            f"{metrics['c_to_w_against_comparator_rows']} C->W changes among scorable "
            "rows."
        ),
        "",
        "## Verifier Decision",
        "",
        str(metadata["verifier_decision"]),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- Protocol: `{protocol_path}`",
        f"- Routing JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Source replay: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Suspicious Flags", "", "| Flag | Rows |", "| --- | ---: |"])
    for key, value in metadata["flag_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Hidden-Family Readout",
            "",
            "| Hidden family | Rows | Suspicious | Route unknown | Route review |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for family, summary in sorted(metadata["by_hidden_family"].items()):
        lines.append(
            f"| `{family}` | {summary.get('rows', 0)} | "
            f"{summary.get('suspicious_rows', 0)} | "
            f"{summary.get('route_unknown_rows', 0)} | "
            f"{summary.get('route_review_rows', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Routed Rows",
            "",
            "| Row | Action | Flags | Comparator label | Final policy label | Gold | Delta |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["suspicious_state_action"] == "render":
            continue
        lines.append(
            f"| {row['source_row_index']} | `{row['suspicious_state_action']}` | "
            f"{_join_code(row['suspicious_state_flags'])} | "
            f"`{row['deterministic_policy_label']}` | "
            f"`{row['final_policy_under_test']['label'] or 'abstain'}` | "
            f"`{row['gold_label']}` | `{row['comparison']['delta']}` |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _suspicious_routing_row(
    row: Mapping[str, Any],
    *,
    panel_row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    structured_record = row.get("structured_record") or {}
    state = dict(structured_record.get("selected_state") or {})
    note_text = str(row.get("typed_input", {}).get("note_text") or "")
    gold_label = _normalize_label(row.get("reference", {}).get("gold_normalized_label"))
    comparator_label = _normalize_label(
        row.get("policy_replay", {}).get("revised_deterministic_projected_label")
        or row.get("deterministic_projected_label")
    )
    exact_trace = bool(state.get("selected_evidence")) and evidence_is_substring(
        note_text, str(state.get("selected_evidence") or "")
    )
    source_id_trace = _source_id_trace(structured_record, exact_trace=exact_trace)
    source_id_status = source_id_trace["source_id_status"]
    flags = _suspicious_flags(
        state,
        exact_trace=exact_trace,
        source_id_status=source_id_status,
    )
    action = _routing_action(flags)
    final_label = _final_policy_label(comparator_label, action)
    comparator_correct = comparator_label == gold_label
    final_correct = final_label == gold_label if final_label is not None else None
    return {
        "artifact_kind": "gan2026_suspicious_selected_state_routing_row",
        "claim_boundary": "validation_development_saved_artifact_no_call_suspicious_routing",
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "gold_label": gold_label,
        "hidden_families": list(panel_row.get("hidden_families") or []) if panel_row else [],
        "selected_state": state,
        "selected_evidence_status": {
            "exact_trace": exact_trace,
            "selected_evidence_present": bool(str(state.get("selected_evidence") or "").strip()),
            "source_id_status": source_id_status,
            "source_id_trace": source_id_trace,
        },
        "embedded_ambiguity_fields": {
            "ambiguity_flags": list(state.get("ambiguity_flags") or []),
            "competing_state_summary": str(state.get("competing_state_summary") or ""),
            "conditionality_note": str(state.get("conditionality_note") or ""),
            "cluster_uncertainty": str(
                (state.get("cluster") or {}).get("cluster_uncertainty") or ""
            ),
            "seizure_free_boundary_note": str(
                (state.get("seizure_free_boundary") or {}).get("boundary_note") or ""
            ),
        },
        "deterministic_policy_label": comparator_label,
        "deterministic_policy_action": "render",
        "suspicious_state_flags": flags,
        "suspicious_state_action": action,
        "llm_verifier_input": (
            _verifier_input(row, state, flags) if action == "route_review" else None
        ),
        "llm_verifier_output": None,
        "final_policy_under_test": {
            "label": final_label,
            "action": action,
            "scorable": final_label is not None,
        },
        "comparison": {
            "comparator_correct": comparator_correct,
            "final_policy_correct": final_correct,
            "w_to_c_against_comparator": bool(
                final_correct is True and comparator_correct is False
            ),
            "c_to_w_against_comparator": bool(
                final_correct is False and comparator_correct is True
            ),
            "delta": _delta(comparator_correct, final_correct),
        },
        "first_failure_owner": _first_failure_owner(flags),
    }


def _suspicious_flags(
    state: Mapping[str, Any],
    *,
    exact_trace: bool,
    source_id_status: str,
) -> list[str]:
    flags: list[str] = []
    state_kind = str(state.get("state_kind") or "")
    currentness = str(state.get("currentness") or "")
    conditionality_note = str(state.get("conditionality_note") or "")
    ambiguity_text = _lower_join(
        state.get("ambiguity_flags") or [],
        state.get("competing_state_summary"),
        state.get("raw_model_label_hint"),
    )
    cluster = state.get("cluster") or {}
    rate = state.get("rate") or {}
    boundary = state.get("seizure_free_boundary") or {}
    selected_text = _lower_join(
        state.get("selected_evidence"),
        state.get("raw_source_phrase"),
        rate.get("rate_text"),
        conditionality_note,
    )

    if state_kind == "frequency" and _exclusive_conditionality(currentness, conditionality_note):
        flags.append("frequency_with_exclusive_conditionality")
    if state_kind == "frequency" and _ambiguity_blocks_count(ambiguity_text):
        flags.append("frequency_with_count_blocking_ambiguity")
    if (
        cluster.get("has_cluster_pattern")
        and not cluster.get("cluster_cadence_known")
        and (
            cluster.get("seizures_per_cluster_low") is not None
            or cluster.get("seizures_per_cluster_high") is not None
        )
    ):
        flags.append("unresolved_cluster_cadence_with_per_cluster_burden")
    if state_kind == "seizure_free" and boundary.get("has_recent_events_or_conditions"):
        flags.append("seizure_free_with_recent_event_blocker")
    if (
        state_kind == "seizure_free"
        and not boundary.get("applies_to_all_seizure_types")
        and _has_current_nonzero_events(selected_text, ambiguity_text)
    ):
        flags.append("seizure_free_non_all_type_scope_with_current_events")
    if _competing_current_rates_without_controlling_semiology(state, ambiguity_text):
        flags.append("competing_current_rates_without_controlling_semiology")
    if _diary_log_without_window(selected_text, rate):
        flags.append("diary_log_date_list_without_defined_observation_window")
    if _denominator_window_mismatch(selected_text, rate):
        flags.append("denominator_window_mismatch")
    if _vague_trend_without_absolute_frequency(selected_text, ambiguity_text, rate):
        flags.append("vague_trend_without_absolute_current_frequency")
    if not exact_trace:
        flags.append("selected_evidence_missing_exact_trace")
    if exact_trace and source_id_status not in {"valid", "not_instrumented"}:
        flags.append("selected_source_id_invalid")
    return sorted(set(flags))


def _routing_action(flags: Sequence[str]) -> str:
    if not flags:
        return "render"
    review_flags = {
        "selected_evidence_missing_exact_trace",
        "competing_current_rates_without_controlling_semiology",
        "diary_log_date_list_without_defined_observation_window",
        "denominator_window_mismatch",
        "selected_source_id_invalid",
    }
    unknown_flags = {
        "frequency_with_exclusive_conditionality",
        "frequency_with_count_blocking_ambiguity",
        "unresolved_cluster_cadence_with_per_cluster_burden",
        "seizure_free_with_recent_event_blocker",
        "seizure_free_non_all_type_scope_with_current_events",
        "vague_trend_without_absolute_current_frequency",
    }
    if any(flag in review_flags for flag in flags):
        return "route_review"
    if any(flag in unknown_flags for flag in flags):
        return "route_unknown"
    return "render"


def _final_policy_label(comparator_label: str, action: str) -> str | None:
    if action == "route_unknown":
        return "unknown"
    if action == "route_review":
        return None
    return comparator_label


def _verifier_input(
    row: Mapping[str, Any],
    state: Mapping[str, Any],
    flags: Sequence[str],
) -> dict[str, Any]:
    return {
        "source_row_index": int(row["source_row_index"]),
        "selected_state": state,
        "suspicious_state_flags": list(flags),
        "allowed_recommendations": [
            "render_as_selected_state",
            "render_as_unknown",
            "abstain_review",
            "choose_listed_competing_hypothesis",
        ],
        "provided_competing_hypotheses": str(state.get("competing_state_summary") or ""),
    }


def _normalize_label(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    try:
        return label_to_frequency_record(text).normalized_label
    except ValueError:
        return text


def _exclusive_conditionality(currentness: str, note: str) -> bool:
    text = note.lower()
    if currentness == "conditional":
        return True
    return bool(
        re.search(r"\b(only|exclusively)\s+(?:after|when|if|with|during)\b", text)
        or re.search(r"\b(?:when|if|with|during)\b.*\bonly\b", text)
    )


def _ambiguity_blocks_count(text: str) -> bool:
    return bool(
        re.search(
            r"\b(exact|absolute|number|count|events?).*\b(unclear|unknown|not stated)\b",
            text,
        )
        or re.search(r"\b(unclear|unknown|not stated).*\b(exact|absolute|number|count)\b", text)
    )


def _has_current_nonzero_events(*texts: str) -> bool:
    text = " ".join(texts)
    return bool(
        re.search(r"\b(recent|current|ongoing|continues?|still|breakthrough)\b", text)
        and re.search(r"\b(seizure|event|convulsion|absence|cluster)s?\b", text)
    )


def _competing_current_rates_without_controlling_semiology(
    state: Mapping[str, Any], ambiguity_text: str
) -> bool:
    competing = str(state.get("competing_state_summary") or "").lower()
    applies_to = str(state.get("applies_to") or "").lower()
    if not competing or not re.search(
        r"\b(per|daily|weekly|monthly|yearly|week|month)\b", competing
    ):
        return False
    if any(word in applies_to for word in ("all", "overall", "total")):
        return False
    return "competing" in ambiguity_text or "different" in competing or "also" in competing


def _diary_log_without_window(text: str, rate: Mapping[str, Any]) -> bool:
    if not re.search(r"\b(diary|log|recorded|dates?|entries)\b", text):
        return False
    return not bool(rate.get("rate_time_basis_known") and rate.get("time_unit"))


def _denominator_window_mismatch(text: str, rate: Mapping[str, Any]) -> bool:
    if not bool(rate.get("rate_time_basis_known") and rate.get("time_unit")):
        return False
    if re.search(r"\bper\s+(?:day|week|month|year)\b", text):
        return False
    return bool(
        re.search(r"\b(on|most|many|several)\s+(?:shifts|days|weekdays|nights)\b", text)
        or re.search(r"\bwithin\s+\d+\s+(?:day|week|month|year)s?\b", text)
    )


def _vague_trend_without_absolute_frequency(
    text: str, ambiguity_text: str, rate: Mapping[str, Any]
) -> bool:
    trend_text = f"{text} {ambiguity_text}"
    if not re.search(
        r"\b(more frequent|increased|increase|worse|worsening|thin out)\b", trend_text
    ):
        return False
    return not bool(
        rate.get("time_unit")
        and (rate.get("count_is_multiple") or rate.get("count_low") is not None)
    )


def _lower_join(*values: Any) -> str:
    flattened: list[str] = []
    for value in values:
        if isinstance(value, (list, tuple)):
            flattened.extend(str(item) for item in value)
        elif value is not None:
            flattened.append(str(value))
    return " ".join(flattened).lower()


def _delta(comparator_correct: bool, final_correct: bool | None) -> str:
    if final_correct is None:
        return "routed_to_review"
    if final_correct and not comparator_correct:
        return "W_to_C"
    if not final_correct and comparator_correct:
        return "C_to_W"
    if final_correct:
        return "C_to_C"
    return "W_to_W"


def _first_failure_owner(flags: Sequence[str]) -> str:
    if not flags:
        return "none"
    if "selected_evidence_missing_exact_trace" in flags:
        return "evidence_trace"
    if "selected_source_id_invalid" in flags:
        return "source_id_trace"
    if any(flag.startswith("seizure_free") for flag in flags):
        return "seizure_free_boundary"
    if any("cluster" in flag for flag in flags):
        return "cluster_boundary"
    if any("conditionality" in flag for flag in flags):
        return "conditionality"
    if any("denominator" in flag or "diary" in flag for flag in flags):
        return "rate_window"
    return "selected_state_ambiguity"


def _by_hidden_family(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        families = row["hidden_families"] or ["unclassified"]
        for family in families:
            by_family[str(family)]["rows"] += 1
            if row["suspicious_state_flags"]:
                by_family[str(family)]["suspicious_rows"] += 1
            if row["suspicious_state_action"] == "route_unknown":
                by_family[str(family)]["route_unknown_rows"] += 1
            if row["suspicious_state_action"] == "route_review":
                by_family[str(family)]["route_review_rows"] += 1
    return {family: dict(counts) for family, counts in sorted(by_family.items())}


def _source_id_trace(structured_record: Mapping[str, Any], *, exact_trace: bool) -> dict[str, Any]:
    selected_source_ids = [
        str(value) for value in structured_record.get("selected_source_ids") or []
    ]
    declared_status = str(structured_record.get("source_id_status") or "").strip()
    expected_source_ids = ["note"] if exact_trace else []
    missing_expected_source_ids = [
        source_id for source_id in expected_source_ids if source_id not in selected_source_ids
    ]
    unexpected_source_ids = [
        source_id for source_id in selected_source_ids if source_id not in expected_source_ids
    ]
    if declared_status:
        status = declared_status
    elif not exact_trace:
        status = "invalid"
    elif selected_source_ids:
        status = (
            "valid"
            if not missing_expected_source_ids and not unexpected_source_ids
            else "invalid"
        )
    else:
        status = "not_instrumented"
    return {
        "source_id_status": status,
        "declared_source_id_status": declared_status or None,
        "selected_source_ids": selected_source_ids,
        "expected_source_ids": expected_source_ids,
        "missing_expected_source_ids": missing_expected_source_ids,
        "unexpected_source_ids": unexpected_source_ids,
        "trace_basis": (
            "exact_selected_evidence" if exact_trace else "non_exact_or_missing_evidence"
        ),
    }


def _verifier_decision(rows: Sequence[Mapping[str, Any]], c_to_w_rows: Sequence[int]) -> str:
    unresolved_review = [
        int(row["source_row_index"])
        for row in rows
        if row["suspicious_state_action"] == "route_review"
    ]
    unresolved_wrong_unknown = [
        int(row["source_row_index"])
        for row in rows
        if row["suspicious_state_action"] == "route_unknown"
        and row["comparison"]["final_policy_correct"] is False
    ]
    if c_to_w_rows:
        return (
            "Predeclare a selective verifier only for the stable suspicious slices; "
            f"deterministic routing caused C->W rows {list(c_to_w_rows)}, so the "
            "verifier must prove no-regression value before it can affect labels."
        )
    if unresolved_review or unresolved_wrong_unknown:
        return (
            "Predeclare a selective verifier for the unresolved suspicious slice only. "
            f"Review rows: {unresolved_review}; route-unknown still-wrong rows: "
            f"{unresolved_wrong_unknown}."
        )
    return (
        "No selective verifier is needed on this saved surface; deterministic "
        "suspicious-state routing resolved the named ambiguity families without "
        "scorable regressions."
    )


def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _join_code(values: Sequence[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rich-state-replay-path", type=Path, default=DEFAULT_RICH_STATE_REPLAY_PATH
    )
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows = load_jsonl_rows(args.rich_state_replay_path)
    panel_rows = load_jsonl_rows(args.panel_jsonl_path) if args.panel_jsonl_path.exists() else []
    artifact_rows, metadata = build_suspicious_routing_rows(rows, panel_rows=panel_rows)
    metadata = {**metadata, "source_artifact": str(args.rich_state_replay_path)}
    write_jsonl_rows(artifact_rows, args.jsonl_path)
    write_suspicious_routing_json(metadata, args.json_path)
    write_suspicious_routing_report(
        artifact_rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
