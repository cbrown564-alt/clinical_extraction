"""Apply the predeclared trigger-context release rule as a proposal."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import Any

RULE_NAME = "trigger_context_release_rule_v0"
PROPOSED_POLICY_NAME = "gan2026_staged_decision_policy_v0_trigger_context_release_v0"
SENTINEL_LABELS = {"", "unknown", "no seizure frequency reference"}
EXCLUSIVE_TRIGGER_MARKERS = (
    "only when",
    "only with",
    "only after",
    "outside this window",
    "exclusively",
)
EVENT_TARGET_TERMS = (
    "seizure",
    "seizures",
    "episode",
    "episodes",
    "event",
    "events",
    "cluster",
    "clusters",
    "convulsion",
    "convulsive",
    "myoclonic",
    "focal",
    "absence",
)
RATE_OR_WINDOW_TERMS = (
    "per",
    "weekly",
    "daily",
    "monthly",
    "yearly",
    "week",
    "weeks",
    "month",
    "months",
    "year",
    "years",
    "day",
    "days",
    "several",
    "multiple",
    "roughly",
)


def build_release_rows(
    pressure_rows: Sequence[Mapping[str, Any]],
    residual_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build proposed prediction releases from pressure and residual rows."""

    residual_by_source = {
        int(row["source_row_index"]): row
        for row in residual_rows
        if row.get("source_row_index") is not None
    }
    release_rows = []
    for pressure in pressure_rows:
        if pressure.get("review_lane") != "trigger_release_candidate":
            continue
        source_row_index = int(pressure["source_row_index"])
        residual = residual_by_source.get(source_row_index, {})
        if not _passes_release_rule(pressure, residual):
            continue
        release_rows.append(
            {
                "artifact_kind": "gan2026_trigger_context_release_rule_row",
                "source_row_index": source_row_index,
                "release_decision": "release_as_prediction",
                "prediction_label": residual.get("blocked_candidate_label"),
                "selected_evidence": residual.get("blocked_candidate_evidence"),
                "selected_source_ids": residual.get("blocked_candidate_source_ids", []),
                "rule_name": RULE_NAME,
                "release_reason": "predeclared_trigger_context_release_candidate",
                "development_accounting": {
                    "purist_correct": residual.get(
                        "blocked_candidate_purist_correct"
                    ),
                    "pragmatic_correct": residual.get(
                        "blocked_candidate_pragmatic_correct"
                    ),
                },
            }
        )
    return release_rows


def apply_release_rows(
    decision_rows: Sequence[Mapping[str, Any]],
    release_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Apply proposed releases to a copy of decision rows."""

    release_by_source = {
        int(row["source_row_index"]): row
        for row in release_rows
        if row.get("source_row_index") is not None
    }
    proposed = []
    for decision in decision_rows:
        row = deepcopy(dict(decision))
        row["policy_name"] = PROPOSED_POLICY_NAME
        row["release_rule_applied"] = None
        release = release_by_source.get(int(row["source_row_index"]))
        if release is not None:
            row.update(
                {
                    "final_action": "predict",
                    "prediction_bearing": True,
                    "prediction_label": release.get("prediction_label"),
                    "selected_evidence": release.get("selected_evidence"),
                    "selected_source_ids": release.get("selected_source_ids", []),
                    "selected_evidence_exact": True,
                    "release_rule_applied": RULE_NAME,
                    "decision_reason": "trigger_context_released",
                    "development_accounting": dict(
                        release.get("development_accounting", {})
                    ),
                }
            )
        proposed.append(row)
    return proposed


def summarize_proposed_decisions(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize the proposed decision layer after release rows are applied."""

    action_counts = Counter(str(row.get("final_action")) for row in rows)
    prediction_rows = [row for row in rows if row.get("prediction_bearing") is True]
    released_rows = [row for row in rows if row.get("release_rule_applied") == RULE_NAME]
    return {
        "component_name": "trigger_context_release_rule",
        "policy_name": PROPOSED_POLICY_NAME,
        "row_count": len(rows),
        "released_rows": len(released_rows),
        "prediction_bearing_rows": len(prediction_rows),
        "non_prediction_rows": len(rows) - len(prediction_rows),
        "action_counts": dict(sorted(action_counts.items())),
        "selective_purist_accuracy": _safe_rate(
            sum(
                row.get("development_accounting", {}).get("purist_correct") is True
                for row in prediction_rows
            ),
            len(prediction_rows),
        ),
        "selective_pragmatic_accuracy": _safe_rate(
            sum(
                row.get("development_accounting", {}).get("pragmatic_correct") is True
                for row in prediction_rows
            ),
            len(prediction_rows),
        ),
        "claim_language": (
            "Validation-development proposed decision layer. It applies only the "
            "predeclared trigger-context release rule to the conservative staged "
            "decision layer. It does not change prompts, scorer policy, gold "
            "labels, locked-test behavior, verifier use, or benchmark-comparable "
            "claims."
        ),
    }


def write_summary_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    release_rows: Sequence[Mapping[str, Any]],
    summary: Mapping[str, Any],
    path: Path,
    *,
    release_jsonl_path: Path,
    proposed_jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Trigger-Context Release Rule Proposal",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        (
            f"The rule releases {summary['released_rows']} rows. The proposed "
            f"decision layer has {summary['prediction_bearing_rows']} "
            f"prediction-bearing rows and {summary['non_prediction_rows']} "
            "non-prediction rows."
        ),
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| released rows | {summary['released_rows']} |",
        f"| prediction bearing rows | {summary['prediction_bearing_rows']} |",
        f"| non prediction rows | {summary['non_prediction_rows']} |",
        f"| selective purist accuracy | {_format_metric(summary['selective_purist_accuracy'])} |",
        (
            "| selective pragmatic accuracy | "
            f"{_format_metric(summary['selective_pragmatic_accuracy'])} |"
        ),
        "",
        "## Released Rows",
        "",
        "| Row | Label | Evidence | Source ids |",
        "| ---: | --- | --- | --- |",
    ]
    for row in release_rows:
        lines.append(
            f"| {row['source_row_index']} | `{row['prediction_label']}` | "
            f"{_short(row['selected_evidence'])} | "
            f"`{', '.join(row['selected_source_ids'])}` |"
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Release rows JSONL: `{release_jsonl_path}`",
            f"- Proposed decision JSONL: `{proposed_jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _passes_release_rule(
    pressure: Mapping[str, Any],
    residual: Mapping[str, Any],
) -> bool:
    label = str(residual.get("blocked_candidate_label") or "").strip().lower()
    evidence = str(residual.get("blocked_candidate_evidence") or "").strip().lower()
    return (
        pressure.get("review_lane") == "trigger_release_candidate"
        and label not in SENTINEL_LABELS
        and bool(residual.get("blocked_candidate_source_ids"))
        and _has_event_target(evidence)
        and _has_rate_or_window(evidence)
        and not _has_exclusive_trigger_marker(evidence)
    )


def _has_event_target(text: str) -> bool:
    return any(term in text for term in EVENT_TARGET_TERMS)


def _has_rate_or_window(text: str) -> bool:
    return any(term in text for term in RATE_OR_WINDOW_TERMS)


def _has_exclusive_trigger_marker(text: str) -> bool:
    return any(marker in text for marker in EXCLUSIVE_TRIGGER_MARKERS)


def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _short(value: Any, limit: int = 96) -> str:
    text = str(value or "").replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 3] + "..."
