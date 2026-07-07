"""Interpret remaining RQ9 v2 abstention and review pressure."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_ROUTER_JSONL_PATH = Path(
    "experiments/gan2026_rq9_selective_action_router_v2_2026-06-04.jsonl"
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_rq9_abstention_pressure_v0_2026-06-04.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_rq9_abstention_pressure_v0_2026-06-04.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_rq9_abstention_pressure_v0_2026-06-04.md")
ANALYSIS_VERSION = "gan2026_rq9_abstention_pressure_v0"
PREDICT = "predict"
SENTINEL_LABELS = {"unknown", "no seizure frequency reference", ""}


def interpret_abstention_rows(
    router_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        interpret_abstention_row(row)
        for row in router_rows
        if row.get("selective_action") != PREDICT
    ]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_abstention_pressure(rows)


def interpret_abstention_row(row: Mapping[str, Any]) -> dict[str, Any]:
    action = str(row.get("selective_action") or "")
    reason = str(row.get("primary_reason") or "")
    source_candidate = row.get("source_candidate", {})
    final_label = _text(source_candidate.get("final_label"))
    purist_correct = source_candidate.get("purist_correct")
    policy_interpretation, pressure_class = _classify_policy_pressure(reason, final_label)
    development_safe = bool(
        pressure_class == "candidate_prediction_bearing" and purist_correct is True
    )
    development_unsafe = bool(
        pressure_class == "candidate_prediction_bearing" and purist_correct is False
    )
    accounting = row.get("development_accounting", {})
    return {
        "artifact_kind": "gan2026_rq9_abstention_pressure_row",
        "analysis_version": ANALYSIS_VERSION,
        "source_row_index": int(row["source_row_index"]),
        "selective_action": action,
        "primary_reason": reason,
        "policy_interpretation": policy_interpretation,
        "pressure_class": pressure_class,
        "candidate_final_label": final_label,
        "selected_evidence": _text(source_candidate.get("selected_evidence")),
        "development_safe_if_predicted": development_safe,
        "development_unsafe_if_predicted": development_unsafe,
        "development_accounting": {
            "purist_correct": purist_correct,
            "human_simple_class": accounting.get("human_simple_class"),
            "gold_label_kind": accounting.get("gold_label_kind"),
            "codex_ambiguity_reasons": list(accounting.get("codex_ambiguity_reasons") or []),
        },
    }


def summarize_abstention_pressure(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    class_counts = Counter(str(row["pressure_class"]) for row in rows)
    reason_counts = Counter(str(row["primary_reason"]) for row in rows)
    metrics = {
        "rows": len(rows),
        "abstain_rows": sum(row["selective_action"] == "abstain" for row in rows),
        "human_review_rows": sum(row["selective_action"] == "human_review" for row in rows),
        "candidate_prediction_bearing_rows": class_counts["candidate_prediction_bearing"],
        "development_safe_candidate_rows": sum(
            row["development_safe_if_predicted"] for row in rows
        ),
        "development_unsafe_candidate_rows": sum(
            row["development_unsafe_if_predicted"] for row in rows
        ),
        "policy_supported_nonprediction_rows": class_counts["policy_supported_nonprediction"],
        "needs_frozen_policy_before_prediction_rows": class_counts[
            "needs_frozen_policy_before_prediction"
        ],
        "development_safe_candidate_rate": _safe_rate(
            sum(row["development_safe_if_predicted"] for row in rows),
            class_counts["candidate_prediction_bearing"],
        ),
    }
    return {
        "artifact_kind": "gan2026_rq9_abstention_pressure",
        "date": "2026-06-04",
        "analysis_version": ANALYSIS_VERSION,
        "source_artifact": str(DEFAULT_ROUTER_JSONL_PATH),
        "claim_language": (
            "Validation-development interpretation of remaining v2 RQ9 "
            "nonprediction rows. Development correctness and human classes are "
            "offline accounting only; this artifact does not change scorer, gold, "
            "router, prompt, projection, locked-test, or benchmark-comparable "
            "policy."
        ),
        "metrics": metrics,
        "reason_counts": dict(sorted(reason_counts.items())),
        "pressure_class_counts": dict(sorted(class_counts.items())),
        "by_reason": _by_reason(rows),
        "decision": _decision(metrics),
    }


def write_abstention_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_abstention_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 RQ9 Abstention Pressure Interpretation",
        "",
        "This is a no-call validation-development interpretation of the remaining "
        "nonprediction rows in the tightened v2 RQ9 selective-action router.",
        "",
        "## Decision",
        "",
        str(metadata["decision"]),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- Source router JSONL: `{metadata['source_artifact']}`",
        f"- Row interpretation JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## By Reason", ""])
    for reason, summary in metadata["by_reason"].items():
        lines.extend(
            [
                f"### {reason}",
                "",
                "| Metric | Value |",
                "| --- | ---: |",
            ]
        )
        for key, value in summary.items():
            if isinstance(value, dict):
                continue
            lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
        lines.append("")
    lines.extend(
        [
            "## Candidate Prediction-Bearing Rows",
            "",
            "| Row | Reason | Candidate label | Dev safe | Evidence |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["pressure_class"] != "candidate_prediction_bearing":
            continue
        lines.append(
            f"| {row['source_row_index']} | `{row['primary_reason']}` | "
            f"`{row['candidate_final_label']}` | "
            f"{_yes_no(row['development_safe_if_predicted'])} | "
            f"{_short(row['selected_evidence'])} |"
        )
    lines.extend(
        [
            "",
            "## Policy-Supported Nonprediction Rows",
            "",
            "| Row | Reason | Interpretation | Candidate label |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["pressure_class"] == "candidate_prediction_bearing":
            continue
        lines.append(
            f"| {row['source_row_index']} | `{row['primary_reason']}` | "
            f"`{row['policy_interpretation']}` | "
            f"`{row['candidate_final_label']}` |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _classify_policy_pressure(reason: str, final_label: str) -> tuple[str, str]:
    label = final_label.lower()
    if reason == "trigger_conditioned_frequency":
        if label not in SENTINEL_LABELS:
            return "rate_with_trigger_context", "candidate_prediction_bearing"
        return "trigger_only_or_unquantified", "policy_supported_nonprediction"
    if reason == "missing_denominator_anchor":
        return "missing_denominator_or_anchor", "policy_supported_nonprediction"
    if reason == "last_event_boundary":
        return "last_event_needs_date_policy", "needs_frozen_policy_before_prediction"
    return "nonprediction_policy_boundary", "policy_supported_nonprediction"


def _by_reason(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["primary_reason"])].append(row)
    return {
        reason: _summarize_reason(reason_rows) for reason, reason_rows in sorted(grouped.items())
    }


def _summarize_reason(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    class_counts = Counter(str(row["pressure_class"]) for row in rows)
    return {
        "rows": len(rows),
        "candidate_prediction_bearing_rows": class_counts["candidate_prediction_bearing"],
        "development_safe_candidate_rows": sum(
            row["development_safe_if_predicted"] for row in rows
        ),
        "development_unsafe_candidate_rows": sum(
            row["development_unsafe_if_predicted"] for row in rows
        ),
        "policy_supported_nonprediction_rows": class_counts["policy_supported_nonprediction"],
        "needs_frozen_policy_before_prediction_rows": class_counts[
            "needs_frozen_policy_before_prediction"
        ],
        "pressure_class_counts": dict(sorted(class_counts.items())),
    }


def _decision(metrics: Mapping[str, Any]) -> str:
    return (
        "Some trigger-conditioned abstentions can plausibly stay prediction-bearing, "
        f"but only under a stricter gold-blinded trigger-context rule. There are "
        f"{metrics['candidate_prediction_bearing_rows']} trigger rows with "
        f"non-sentinel candidate labels, {metrics['development_safe_candidate_rows']} "
        "of which are development-safe if predicted and "
        f"{metrics['development_unsafe_candidate_rows']} of which are not. "
        "Missing-anchor rows should remain abstentions, and last-event rows should "
        "remain human-review until a frozen date-window policy exists."
    )


def _safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _format_metric(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _short(value: str, *, max_len: int = 96) -> str:
    text = " ".join(value.split())
    if len(text) <= max_len:
        return f"`{text}`"
    return f"`{text[: max_len - 1]}...`"


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interpret remaining Gan 2026 RQ9 v2 abstention pressure."
    )
    parser.add_argument("--router-jsonl", type=Path, default=DEFAULT_ROUTER_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    rows, metadata = interpret_abstention_rows(load_jsonl_rows(args.router_jsonl))
    write_jsonl_rows(rows, args.jsonl_path)
    write_abstention_json(metadata, args.json_path)
    write_abstention_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )


if __name__ == "__main__":
    main()
