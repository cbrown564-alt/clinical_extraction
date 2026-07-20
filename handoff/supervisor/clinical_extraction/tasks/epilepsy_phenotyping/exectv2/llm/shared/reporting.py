"""Shared run-report helpers for ExECTv2 LLM pipelines."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any


def ensure_summary(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    summarize_rows: Callable[[Sequence[dict[str, Any]]], dict[str, Any]],
) -> dict[str, Any]:
    """Return a summary dict, computing it from rows when metadata omits one."""

    summary = metadata.get("summary")
    if isinstance(summary, dict):
        return summary
    return summarize_rows(rows)


def build_run_progress_payload(
    *,
    processed: int,
    total: int,
    summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the standard JSON progress object emitted during run_split."""

    return {
        "processed": processed,
        "total": total,
        "call_failures": summary.get("call_failures", 0),
        "parse_failures": summary.get("parse_failures", 0),
        "n_mentions_scored": summary.get("n_mentions_scored", 0),
    }


def format_gate_summary_lines(
    summary: Mapping[str, Any],
    *,
    extra_lines: Sequence[tuple[str, str]] = (),
) -> list[str]:
    """Render the common gate-summary section shared across run reports."""

    lines = [
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored (evidence-valid): {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        (f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}"),
        "",
    ]
    for label, value in extra_lines:
        lines.insert(-1, f"- {label}: {value}")
    return lines
