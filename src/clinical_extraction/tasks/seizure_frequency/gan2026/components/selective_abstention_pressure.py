"""Review pressure from staged-hybrid non-prediction rows."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

SENTINEL_LABELS = {"", "unknown", "no seizure frequency reference"}


def build_pressure_review_rows(
    residual_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Assign review lanes to residual non-prediction rows."""

    return [_pressure_review_row(row) for row in residual_rows]


def summarize_pressure_review(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize selective abstention and review pressure."""

    pressure_counts = Counter(str(row.get("pressure_class")) for row in rows)
    lane_counts = Counter(str(row.get("review_lane")) for row in rows)
    reason_counts = Counter(str(row.get("decision_reason")) for row in rows)
    return {
        "component_name": "selective_abstention_pressure",
        "row_count": len(rows),
        "pressure_class_counts": dict(sorted(pressure_counts.items())),
        "review_lane_counts": dict(sorted(lane_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "coverage_cost_rows": pressure_counts["coverage_cost"],
        "protective_block_rows": pressure_counts["protective_block"],
        "recommended_next_step": (
            "Predeclare a gold-blinded trigger-context release rule and a frozen "
            "last-event date policy before changing prediction-bearing behavior."
        ),
        "claim_language": (
            "Validation-development pressure review of staged-hybrid "
            "non-prediction rows. Blocked-candidate correctness is development "
            "accounting only; this artifact does not change router behavior, "
            "prompts, scorer policy, gold labels, locked-test behavior, verifier "
            "use, or benchmark-comparable claims."
        ),
    }


def write_summary_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Selective Abstention-Pressure Review",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        (
            f"The review covers {summary['row_count']} residual non-prediction "
            f"rows: {summary['coverage_cost_rows']} coverage-cost rows and "
            f"{summary['protective_block_rows']} protective blocks."
        ),
        "",
        "## Review Lanes",
        "",
        "| Lane | Rows |",
        "| --- | ---: |",
    ]
    for lane, count in summary["review_lane_counts"].items():
        lines.append(f"| `{lane}` | {count} |")
    lines.extend(
        [
            "",
            "## Pressure Classes",
            "",
            "| Class | Rows |",
            "| --- | ---: |",
        ]
    )
    for pressure_class, count in summary["pressure_class_counts"].items():
        lines.append(f"| `{pressure_class}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Pressure review JSONL: `{jsonl_path}`",
            f"- Pressure review summary JSON: `{json_path}`",
            "",
            "## Rows",
            "",
            "| Row | Reason | Blocked label | Class | Lane |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | `{row['decision_reason']}` | "
            f"`{row['blocked_candidate_label']}` | `{row['pressure_class']}` | "
            f"`{row['review_lane']}` |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _pressure_review_row(row: Mapping[str, Any]) -> dict[str, Any]:
    pressure_class = _pressure_class(row.get("blocked_candidate_purist_correct"))
    return {
        "artifact_kind": "gan2026_selective_abstention_pressure_row",
        "source_row_index": int(row["source_row_index"]),
        "final_action": row.get("final_action"),
        "decision_reason": row.get("decision_reason"),
        "gold_label": row.get("gold_label"),
        "blocked_candidate_label": row.get("blocked_candidate_label"),
        "blocked_candidate_purist_correct": row.get(
            "blocked_candidate_purist_correct"
        ),
        "blocked_candidate_pragmatic_correct": row.get(
            "blocked_candidate_pragmatic_correct"
        ),
        "pressure_class": pressure_class,
        "review_lane": _review_lane(row, pressure_class),
        "claim_boundary": "validation_development_accounting_only",
    }


def _pressure_class(correct: Any) -> str:
    if correct is True:
        return "coverage_cost"
    if correct is False:
        return "protective_block"
    return "unclassified"


def _review_lane(row: Mapping[str, Any], pressure_class: str) -> str:
    reason = str(row.get("decision_reason") or "")
    if reason == "last_event_boundary":
        return "date_policy_needed"
    if reason == "missing_denominator_anchor":
        return "anchor_policy_needed"
    if reason == "trigger_conditioned_frequency" and pressure_class == "coverage_cost":
        if _is_sentinel_label(row.get("blocked_candidate_label")):
            return "trigger_sentinel_boundary_review"
        return "trigger_release_candidate"
    if pressure_class == "protective_block":
        return "keep_nonprediction"
    return "manual_review_needed"


def _is_sentinel_label(label: Any) -> bool:
    return str(label or "").strip().lower() in SENTINEL_LABELS
