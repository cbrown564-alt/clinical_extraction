"""Analyze RQ9 selective-action router review pressure points."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_ROUTER_JSONL_PATH = Path(
    "experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_rq9_selective_action_router_v3_pressure_points_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_rq9_selective_action_router_v3_pressure_points_2026-06-04.md"
)
ANALYSIS_VERSION = "gan2026_rq9_selective_action_router_pressure_points_v0"
PREDICT = "predict"


def summarize_pressure_points(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    nonprediction_rows = [row for row in rows if row.get("selective_action") != PREDICT]
    return {
        "artifact_kind": "gan2026_rq9_selective_action_router_pressure_points",
        "date": "2026-06-04",
        "analysis_version": ANALYSIS_VERSION,
        "source_artifact": str(DEFAULT_ROUTER_JSONL_PATH),
        "claim_language": (
            "Validation-development pressure-point analysis over a saved RQ9 router "
            "artifact. Gold labels and human decisions are offline accounting only; "
            "this analysis does not change router, scorer, prompt, projection, "
            "locked-test, or benchmark-comparable policy."
        ),
        "metrics": _summarize_group(nonprediction_rows),
        "by_reason": _by_reason(nonprediction_rows),
        "recommendation": _recommendation(nonprediction_rows),
    }


def write_pressure_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_pressure_report(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics = summary["metrics"]
    lines = [
        "# Gan 2026 RQ9 Router Pressure Points",
        "",
        "This is a no-call validation-development interpretation of the saved RQ9 "
        "selective-action router artifact.",
        "",
        "## Decision",
        "",
        str(summary["recommendation"]),
        "",
        "## Claim Boundary",
        "",
        str(summary["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- Source router JSONL: `{summary['source_artifact']}`",
        f"- Pressure summary JSON: `{DEFAULT_JSON_PATH}`",
        "",
        "## Overall Non-Prediction Pressure",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key in (
        "rows",
        "blocked_wrong_predictions",
        "blocked_likely_correct_predictions",
        "source_wrong_rate",
        "source_likely_correct_rate",
        "reviewed_rows",
        "reviewed_correct_rows",
        "reviewed_noncorrect_rows",
        "reviewed_correct_rate",
        "reviewed_noncorrect_rate",
    ):
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(metrics.get(key))} |")

    lines.extend(["", "## By Reason", ""])
    for reason, reason_summary in summary["by_reason"].items():
        lines.extend(
            [
                f"### {reason}",
                "",
                "| Metric | Value |",
                "| --- | ---: |",
            ]
        )
        for key in (
            "rows",
            "blocked_wrong_predictions",
            "blocked_likely_correct_predictions",
            "source_wrong_rate",
            "reviewed_rows",
            "reviewed_correct_rows",
            "reviewed_noncorrect_rows",
            "reviewed_correct_rate",
        ):
            lines.append(f"| {key.replace('_', ' ')} | {_format_metric(reason_summary.get(key))} |")
        lines.extend(["", "| Source label bucket | Rows | Source wrong | Reviewed correct |"])
        lines.append("| --- | ---: | ---: | ---: |")
        for bucket, bucket_summary in reason_summary["by_source_label_bucket"].items():
            lines.append(
                f"| `{bucket}` | {bucket_summary['rows']} | "
                f"{bucket_summary['source_wrong_rows']} | "
                f"{bucket_summary['reviewed_correct_rows']} |"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _by_reason(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get("primary_reason") or "unknown")].append(row)
    return {
        reason: {
            **_summarize_group(reason_rows),
            "by_source_label_bucket": _by_source_label_bucket(reason_rows),
            "gold_label_kind_counts": dict(
                sorted(
                    Counter(
                        str(
                            row.get("development_accounting", {}).get("gold_label_kind")
                            or "unknown"
                        )
                        for row in reason_rows
                    ).items()
                )
            ),
        }
        for reason, reason_rows in sorted(grouped.items())
    }


def _by_source_label_bucket(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[_source_label_bucket(row)].append(row)
    return {
        bucket: _summarize_group(bucket_rows) for bucket, bucket_rows in sorted(grouped.items())
    }


def _summarize_group(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    reviewed_rows = [
        row for row in rows if row.get("development_accounting", {}).get("human_simple_class")
    ]
    source_wrong_rows = [
        row for row in rows if row.get("source_candidate", {}).get("purist_correct") is False
    ]
    source_correct_rows = [
        row for row in rows if row.get("source_candidate", {}).get("purist_correct") is True
    ]
    reviewed_correct_rows = [
        row
        for row in reviewed_rows
        if row.get("development_accounting", {}).get("human_simple_class") == "correct"
    ]
    reviewed_noncorrect_rows = [
        row
        for row in reviewed_rows
        if row.get("development_accounting", {}).get("human_simple_class") in {"ambiguous", "wrong"}
    ]
    return {
        "nonprediction_rows": len(rows),
        "rows": len(rows),
        "blocked_wrong_predictions": len(source_wrong_rows),
        "blocked_likely_correct_predictions": len(source_correct_rows),
        "source_wrong_rows": len(source_wrong_rows),
        "source_likely_correct_rows": len(source_correct_rows),
        "source_wrong_rate": _safe_rate(len(source_wrong_rows), len(rows)),
        "source_likely_correct_rate": _safe_rate(len(source_correct_rows), len(rows)),
        "reviewed_rows": len(reviewed_rows),
        "reviewed_correct_rows": len(reviewed_correct_rows),
        "reviewed_noncorrect_rows": len(reviewed_noncorrect_rows),
        "reviewed_correct_rate": _safe_rate(len(reviewed_correct_rows), len(reviewed_rows)),
        "reviewed_noncorrect_rate": _safe_rate(len(reviewed_noncorrect_rows), len(reviewed_rows)),
    }


def _source_label_bucket(row: Mapping[str, Any]) -> str:
    label = str(row.get("source_candidate", {}).get("final_label") or "").lower()
    if "cluster" in label or "per cluster" in label:
        return "label_contains_cluster"
    if label == "no seizure frequency reference":
        return "label_no_reference"
    if label.startswith("seizure free"):
        return "label_seizure_free"
    if label == "unknown":
        return "label_unknown"
    if label:
        return "label_plain_frequency"
    return "label_missing"


def _recommendation(rows: Sequence[Mapping[str, Any]]) -> str:
    by_reason = _by_reason(rows)
    cluster = by_reason.get("cluster_projection_boundary", {})
    convention = by_reason.get("benchmark_convention_boundary", {})
    cluster_rows = int(cluster.get("rows", 0))
    convention_rows = int(convention.get("rows", 0))
    cluster_correct = int(cluster.get("blocked_likely_correct_predictions", 0))
    convention_correct = int(convention.get("blocked_likely_correct_predictions", 0))
    if cluster_rows == 0 and convention_rows == 0:
        return (
            "The tightened router no longer treats cluster/convention ambiguity "
            "flags as automatic human-review criteria. Remaining non-prediction "
            "pressure is limited to trigger-conditioned, missing-anchor, and "
            "last-event boundaries; cluster/convention cases should be monitored "
            "or verifier-sliced separately rather than blocked by default."
        )
    return (
        "Do not promote wholesale cluster/convention human-review routing. "
        f"Cluster review blocks {cluster_correct}/{cluster_rows} saved source "
        "predictions that are already Purist-correct, and benchmark-convention "
        f"review blocks {convention_correct}/{convention_rows}. The next policy "
        "iteration should narrow review to suspicious subfamilies or predeclare a "
        "verifier slice, while allowing low-risk cluster/convention labels to remain "
        "prediction-bearing."
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze pressure points in the Gan 2026 RQ9 selective-action router."
    )
    parser.add_argument("--router-jsonl", type=Path, default=DEFAULT_ROUTER_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    summary = summarize_pressure_points(load_jsonl_rows(args.router_jsonl))
    write_pressure_json(summary, args.json_path)
    write_pressure_report(summary, args.report_path)


if __name__ == "__main__":
    main()
