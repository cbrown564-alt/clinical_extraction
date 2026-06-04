"""Interpret RQ9 last-event human-review boundaries."""

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
    "experiments/gan2026_rq9_last_event_boundary_decision_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_rq9_last_event_boundary_decision_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_rq9_last_event_boundary_decision_2026-06-04.md"
)
ANALYSIS_VERSION = "gan2026_rq9_last_event_boundary_decision_v0"


def interpret_last_event_rows(
    router_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        interpret_last_event_row(row)
        for row in router_rows
        if row.get("primary_reason") == "last_event_boundary"
    ]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_last_event_rows(rows)


def interpret_last_event_row(row: Mapping[str, Any]) -> dict[str, Any]:
    source_candidate = row.get("source_candidate", {})
    accounting = row.get("development_accounting", {})
    reasons = list(accounting.get("codex_ambiguity_reasons") or [])
    final_label = _text(source_candidate.get("final_label"))
    gold_kind = _text(accounting.get("gold_label_kind"))
    failure_mode = _failure_mode(final_label, gold_kind, reasons)
    return {
        "artifact_kind": "gan2026_rq9_last_event_boundary_row",
        "analysis_version": ANALYSIS_VERSION,
        "source_row_index": int(row["source_row_index"]),
        "decision": "keep_human_review",
        "failure_mode": failure_mode,
        "date_policy_ready": False,
        "candidate_final_label": final_label,
        "selected_evidence": _text(source_candidate.get("selected_evidence")),
        "development_safe_if_predicted": source_candidate.get("purist_correct") is True,
        "development_accounting": {
            "purist_correct": source_candidate.get("purist_correct"),
            "human_simple_class": accounting.get("human_simple_class"),
            "gold_label_kind": gold_kind,
            "codex_ambiguity_reasons": reasons,
        },
    }


def summarize_last_event_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    mode_counts = Counter(str(row["failure_mode"]) for row in rows)
    metrics = {
        "rows": len(rows),
        "keep_human_review_rows": sum(
            row["decision"] == "keep_human_review" for row in rows
        ),
        "date_policy_ready_rows": sum(row["date_policy_ready"] for row in rows),
        "development_safe_if_predicted_rows": sum(
            row["development_safe_if_predicted"] for row in rows
        ),
        "development_unsafe_if_predicted_rows": sum(
            not row["development_safe_if_predicted"] for row in rows
        ),
    }
    return {
        "artifact_kind": "gan2026_rq9_last_event_boundary_decision",
        "date": "2026-06-04",
        "analysis_version": ANALYSIS_VERSION,
        "source_artifact": str(DEFAULT_ROUTER_JSONL_PATH),
        "decision": "keep_last_event_as_human_review",
        "claim_language": (
            "Validation-development decision over v3 last-event human-review rows. "
            "This artifact does not change scorer, gold, router, prompt, projection, "
            "locked-test, or benchmark-comparable policy."
        ),
        "metrics": metrics,
        "failure_mode_counts": dict(sorted(mode_counts.items())),
        "rationale": (
            "Do not implement a v4 date-window projection policy for this slice. "
            "The eight last-event rows are heterogeneous: unknown-convention "
            "seizure-free projections, already-unknown last-event rows, and recent "
            "frequency-selection failures. A single date-window rule would either "
            "predict development-wrong seizure-free labels or fail to address the "
            "frequency-selection rows."
        ),
    }


def write_last_event_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_last_event_report(
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
        "# Gan 2026 RQ9 Last-Event Boundary Decision",
        "",
        "This is a no-call validation-development decision over the remaining "
        "last-event human-review rows in the v3 RQ9 selective-action router.",
        "",
        "## Decision",
        "",
        "Keep last-event rows as human-review boundaries. Do not promote a v4 "
        "date-window projection policy for this slice.",
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
        f"- Row decision JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {value} |")
    lines.extend(["", "## Failure Modes", "", "| Failure mode | Rows |", "| --- | ---: |"])
    for mode, count in metadata["failure_mode_counts"].items():
        lines.append(f"| `{mode}` | {count} |")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Failure mode | Candidate label | Dev safe if predicted | Evidence |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['source_row_index']} | `{row['failure_mode']}` | "
            f"`{row['candidate_final_label']}` | "
            f"{_yes_no(row['development_safe_if_predicted'])} | "
            f"{_short(row['selected_evidence'])} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _failure_mode(final_label: str, gold_kind: str, reasons: Sequence[str]) -> str:
    label = final_label.lower()
    reason_set = set(reasons)
    if gold_kind == "frequency":
        return "recent_event_frequency_selection_boundary"
    if label == "unknown":
        return "unresolved_last_event_unknown_boundary"
    if "unknown_gold_boundary" in reason_set and label.startswith("seizure free"):
        return "unknown_convention_blocks_seizure_free_projection"
    return "last_event_boundary_not_date_policy_ready"


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
        description="Interpret Gan 2026 RQ9 last-event human-review boundaries."
    )
    parser.add_argument("--router-jsonl", type=Path, default=DEFAULT_ROUTER_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    rows, metadata = interpret_last_event_rows(load_jsonl_rows(args.router_jsonl))
    write_jsonl_rows(rows, args.jsonl_path)
    write_last_event_json(metadata, args.json_path)
    write_last_event_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )


if __name__ == "__main__":
    main()
