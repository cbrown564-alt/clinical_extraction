"""Predeclare and materialize RQ9 cluster/convention monitoring."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_ROUTER_JSONL_PATH = Path(
    "experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_rq9_cluster_convention_monitoring_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_rq9_cluster_convention_monitoring_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_rq9_cluster_convention_monitoring_2026-06-04.md"
)
DEFAULT_PREDECLARATION_PATH = Path(
    ""
)
ANALYSIS_VERSION = "gan2026_rq9_cluster_convention_monitoring_v0"


def interpret_cluster_rows(
    router_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        interpret_cluster_row(row)
        for row in router_rows
        if _is_prediction_bearing_cluster_row(row)
    ]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_cluster_rows(rows)


def interpret_cluster_row(row: Mapping[str, Any]) -> dict[str, Any]:
    source_candidate = row.get("source_candidate", {})
    accounting = row.get("development_accounting", {})
    reasons = list(accounting.get("codex_ambiguity_reasons") or [])
    final_label = _text(source_candidate.get("final_label") or row.get("final_label"))
    selected_evidence = _text(source_candidate.get("selected_evidence"))
    monitoring_group = _monitoring_group(final_label)
    verifier_priority = _verifier_priority(monitoring_group, reasons, selected_evidence)
    purist_correct = source_candidate.get("purist_correct")
    return {
        "artifact_kind": "gan2026_rq9_cluster_convention_monitoring_row",
        "analysis_version": ANALYSIS_VERSION,
        "source_row_index": int(row["source_row_index"]),
        "keep_prediction_bearing": True,
        "monitoring_group": monitoring_group,
        "verifier_priority": verifier_priority,
        "candidate_final_label": final_label,
        "selected_evidence": selected_evidence,
        "development_safe_if_predicted": purist_correct is True,
        "development_unsafe_if_predicted": purist_correct is False,
        "development_accounting": {
            "purist_correct": purist_correct,
            "human_simple_class": accounting.get("human_simple_class"),
            "gold_label_kind": accounting.get("gold_label_kind"),
            "codex_ambiguity_reasons": reasons,
        },
    }


def summarize_cluster_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    group_counts = Counter(str(row["monitoring_group"]) for row in rows)
    priority_counts = Counter(str(row["verifier_priority"]) for row in rows)
    metrics = {
        "eligible_prediction_bearing_rows": len(rows),
        "keep_prediction_bearing_rows": sum(row["keep_prediction_bearing"] for row in rows),
        "high_priority_verifier_rows": priority_counts["high_priority_verifier"],
        "routine_monitoring_rows": priority_counts["routine_monitoring"],
        "development_safe_rows": sum(row["development_safe_if_predicted"] for row in rows),
        "development_unsafe_rows": sum(
            row["development_unsafe_if_predicted"] for row in rows
        ),
        "development_unsafe_rate": _safe_rate(
            sum(row["development_unsafe_if_predicted"] for row in rows),
            len(rows),
        ),
    }
    return {
        "artifact_kind": "gan2026_rq9_cluster_convention_monitoring",
        "date": "2026-06-04",
        "analysis_version": ANALYSIS_VERSION,
        "source_artifact": str(DEFAULT_ROUTER_JSONL_PATH),
        "predeclaration": str(DEFAULT_PREDECLARATION_PATH),
        "decision": "keep_prediction_bearing_with_verifier_monitoring",
        "claim_language": (
            "Validation-development monitoring predeclaration over v3 "
            "prediction-bearing cluster/convention rows. The slice stays "
            "prediction-bearing; verifier priority is for monitoring and future "
            "audit only, not router action routing. This artifact does not change "
            "scorer, gold, prompts, projection policy, locked-test behavior, or "
            "benchmark-comparable claims."
        ),
        "metrics": metrics,
        "monitoring_group_counts": dict(sorted(group_counts.items())),
        "verifier_priority_counts": dict(sorted(priority_counts.items())),
        "rationale": (
            "Do not restore default human-review routing for cluster/convention "
            "rows. Most v3 prediction-bearing cluster/convention rows are "
            "development-correct, but convention-risk subfamilies should be "
            "monitored through a high-priority verifier queue."
        ),
    }


def write_cluster_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_cluster_report(
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
        "# Gan 2026 RQ9 Cluster/Convention Monitoring",
        "",
        "This is a validation-development monitoring artifact over v3 "
        "prediction-bearing cluster/convention rows.",
        "",
        "## Decision",
        "",
        "Keep cluster/convention rows prediction-bearing. Use the high-priority "
        "verifier queue for monitoring and future audit, not default human-review "
        "routing.",
        "",
        "## Rationale",
        "",
        str(metadata["rationale"]),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- Source router JSONL: `{metadata['source_artifact']}`",
        f"- Predeclaration: `{metadata['predeclaration']}`",
        f"- Row monitoring JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(
        ["", "## Monitoring Groups", "", "| Group | Rows |", "| --- | ---: |"]
    )
    for group, count in metadata["monitoring_group_counts"].items():
        lines.append(f"| `{group}` | {count} |")
    lines.extend(
        [
            "",
            "## High-Priority Verifier Rows",
            "",
            "| Row | Group | Candidate label | Dev unsafe | Evidence |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["verifier_priority"] != "high_priority_verifier":
            continue
        lines.append(
            f"| {row['source_row_index']} | `{row['monitoring_group']}` | "
            f"`{row['candidate_final_label']}` | "
            f"{_yes_no(row['development_unsafe_if_predicted'])} | "
            f"{_short(row['selected_evidence'])} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_predeclaration(path: Path = DEFAULT_PREDECLARATION_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# Gan 2026 RQ9 Cluster/Convention Monitoring Predeclaration",
                "",
                "This is a validation-development predeclaration for monitoring "
                "cluster/convention rows left prediction-bearing by the v3 RQ9 "
                "selective-action router.",
                "",
                "It does not change scorer policy, gold labels, deterministic "
                "extraction rules, prompts, projection policy, locked-test behavior, "
                "or benchmark-comparable claims.",
                "",
                "## Decision",
                "",
                "Keep cluster/convention rows prediction-bearing by default. Do not "
                "restore wholesale human-review routing. Instead, materialize a "
                "monitoring artifact and a high-priority verifier queue for "
                "convention-risk subfamilies.",
                "",
                "## Eligible Surface",
                "",
                "Rows are eligible when they are v3 `predict` rows and their "
                "pre-routing ambiguity reasons include "
                "`cluster_or_per_cluster_convention`.",
                "",
                "## Verifier Priority",
                "",
                "Use high-priority verifier monitoring for prediction-bearing "
                "cluster/convention rows whose label is not cluster-structured: "
                "`no seizure frequency reference`, `unknown`, seizure-free labels, "
                "or plain frequency labels where cluster/per-cluster structure may "
                "have been flattened. Cluster-structured labels remain routine "
                "monitoring.",
                "",
                "Verifier priority is not a router action. It is an audit queue for "
                "future adjudication, robustness checks, or a separately "
                "predeclared verifier experiment.",
                "",
                "## Required Accounting",
                "",
                "The monitoring artifact must report eligible rows, high-priority "
                "verifier rows, routine monitoring rows, development-safe and "
                "development-unsafe rows, monitoring groups, and row-level packets "
                "with selected evidence.",
                "",
                "## Claim Boundary",
                "",
                "This predeclaration can support validation-development monitoring. "
                "It does not authorize holdout use, scorer changes, gold rewrites, "
                "or benchmark-comparable language.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _is_prediction_bearing_cluster_row(row: Mapping[str, Any]) -> bool:
    reasons = set(row.get("development_accounting", {}).get("codex_ambiguity_reasons") or [])
    return (
        row.get("selective_action") == "predict"
        and "cluster_or_per_cluster_convention" in reasons
    )


def _monitoring_group(final_label: str) -> str:
    label = final_label.lower()
    if "cluster" in label or "per cluster" in label:
        return "cluster_structured_prediction"
    if label == "no seizure frequency reference":
        return "sentinel_no_reference_with_cluster_context"
    if label.startswith("unknown"):
        return "unknown_cluster_burden"
    if label.startswith("seizure free"):
        return "seizure_free_with_cluster_context"
    return "plain_frequency_with_cluster_context"


def _verifier_priority(
    monitoring_group: str,
    reasons: Sequence[str],
    selected_evidence: str,
) -> str:
    if monitoring_group != "cluster_structured_prediction":
        return "high_priority_verifier"
    reason_set = set(reasons)
    if {"unknown_gold_boundary", "explicit_unknown_frequency", "uncertainty_language"} & reason_set:
        return "high_priority_verifier"
    if _has_any(selected_evidence.lower(), "frequency unclear", "unclear frequency"):
        return "high_priority_verifier"
    return "routine_monitoring"


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


def _has_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize Gan 2026 RQ9 cluster/convention monitoring."
    )
    parser.add_argument("--router-jsonl", type=Path, default=DEFAULT_ROUTER_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--predeclaration-path", type=Path, default=DEFAULT_PREDECLARATION_PATH
    )
    args = parser.parse_args()

    rows, metadata = interpret_cluster_rows(load_jsonl_rows(args.router_jsonl))
    write_predeclaration(args.predeclaration_path)
    write_jsonl_rows(rows, args.jsonl_path)
    write_cluster_json(metadata, args.json_path)
    write_cluster_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )


if __name__ == "__main__":
    main()
