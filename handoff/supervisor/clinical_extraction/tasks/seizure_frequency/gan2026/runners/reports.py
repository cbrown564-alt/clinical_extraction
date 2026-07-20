"""Deterministic split-run markdown report writer."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)


def write_deterministic_report(
    rows: Sequence[Mapping[str, object]],
    metadata: Mapping[str, object],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    del jsonl_path
    summary_value = metadata.get("summary", {})
    summary = summary_value if isinstance(summary_value, Mapping) else {}
    lines = [
        "# Gan 2026 Deterministic Pipeline Validation Run",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation run of the deterministic baseline pipeline.",
        "",
        "## Summary",
        "",
        f"- Examples: {summary.get('examples', 0)}",
        f"- Purist-correct: {summary.get('purist_correct', 0)}",
        f"- Purist-accuracy: {summary.get('purist_accuracy', 0.0):.4f}",
        f"- Pragmatic-correct: {summary.get('pragmatic_correct', 0)}",
        f"- Pragmatic-accuracy: {summary.get('pragmatic_accuracy', 0.0):.4f}",
        "",
        "## Rows",
        "",
        "| Row | Predicted | Gold | Purist Correct | Pragmatic Correct |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        comp_value = row.get("comparison", {})
        comp = comp_value if isinstance(comp_value, Mapping) else {}
        reference_value = row.get("reference", {})
        reference = reference_value if isinstance(reference_value, Mapping) else {}
        lines.append(
            f"| {row.get('source_row_index')} | {row.get('final_label')} | "
            f"{reference.get('gold_label')} | "
            f"{'yes' if comp.get('purist_correct') else 'no'} | "
            f"{'yes' if comp.get('pragmatic_correct') else 'no'} |"
        )
    write_markdown_report(path, lines)
