"""Materialize Gan 2026 suspicious selected-state routing diagnostics."""

from __future__ import annotations

import argparse
import json
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
from clinical_extraction.tasks.seizure_frequency.gan2026.components.source_trace import (
    build_selected_source_id_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.components.suspicious_state_policy import (
    final_policy_label,
    first_failure_owner,
    routing_action,
    suspicious_flags,
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
    source_id_trace = build_selected_source_id_trace(
        structured_record, exact_trace=exact_trace
    )
    source_id_status = source_id_trace["source_id_status"]
    flags = suspicious_flags(
        state,
        exact_trace=exact_trace,
        source_id_status=source_id_status,
    )
    action = routing_action(flags)
    final_label = final_policy_label(comparator_label, action)
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
        "first_failure_owner": first_failure_owner(flags),
    }


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
