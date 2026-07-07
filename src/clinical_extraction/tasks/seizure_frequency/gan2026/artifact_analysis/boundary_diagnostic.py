"""Unified parameterized analyzer for boundary state and seizure-free duration diagnostics.

Consolidates boundary state graph replay, last event boundaries, and boundary
candidate experiments.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)


class BoundaryDiagnosticAnalyzer:
    """Consolidated parameterized tool for boundary and seizure-free node diagnostics."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def run_diagnostic(
        self,
        rows: Sequence[Mapping[str, Any]],
        *,
        diagnostic_family: str,
    ) -> dict[str, Any]:
        """Perform diagnostic analysis over replayed boundary rows."""
        total = len(rows)
        boundary_matches = 0
        seizure_free_count = 0
        details = []

        for row in rows:
            normalized_label = str(row.get("normalized_label", "")).lower()
            is_sf = row.get("semantic_kind") == "seizure_free" or "seizure free" in normalized_label
            if is_sf:
                seizure_free_count += 1

            matched = bool(row.get("boundary_matched", False))
            if matched:
                boundary_matches += 1

            details.append(
                {
                    "source_row_index": row.get("source_row_index"),
                    "semantic_kind": row.get("semantic_kind", "unknown"),
                    "normalized_label": row.get("normalized_label"),
                    "gold_normalized_label": row.get("gold_normalized_label"),
                    "boundary_matched": matched,
                }
            )

        return {
            "phase_f_consolidated": True,
            "analyzer_cluster": "boundary_seizure_free",
            "analyzer_module": "boundary_diagnostic",
            "diagnostic_family": diagnostic_family,
            "summary": {
                "total_rows": total,
                "boundary_matches": boundary_matches,
                "seizure_free_rows": seizure_free_count,
                "boundary_match_rate": round(boundary_matches / total, 4) if total else 0.0,
            },
            "details": details,
        }

    def write_report(
        self,
        analysis: Mapping[str, Any],
        path: Path,
    ) -> None:
        summary = analysis["summary"]
        lines = [
            f"# Boundary Diagnostic: {self.description}",
            "",
            f"- Diagnostic family: `{analysis['diagnostic_family']}`",
            f"- Total replayed rows: {summary['total_rows']}",
            f"- Seizure-free rows: {summary['seizure_free_rows']}",
            (
                f"- Boundary matches: {summary['boundary_matches']} "
                f"({summary['boundary_match_rate']:.2%})"
            ),
            "",
            "## Node Details",
            "",
            "| Row | Kind | Label | Gold | Boundary Matched |",
            "| ---: | --- | --- | --- | --- |",
        ]
        for detail in analysis["details"]:
            lines.append(
                f"| {detail['source_row_index']} | {detail['semantic_kind']} | "
                f"{detail['normalized_label']} | {detail['gold_normalized_label']} | "
                f"{'yes' if detail['boundary_matched'] else 'no'} |"
            )
        write_markdown_report(path, lines)
