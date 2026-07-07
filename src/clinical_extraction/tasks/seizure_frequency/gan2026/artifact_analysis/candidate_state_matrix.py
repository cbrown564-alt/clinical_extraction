"""Unified parameterized analyzer for CandidateSet and state-space matrix diagnostics.

Consolidates candidate set comparisons, union metrics, and decision diagnostics.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)


class CandidateStateMatrixAnalyzer:
    """Consolidated tool for CandidateSet comparison and state decision diagnostics."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def compare_candidate_sets(
        self,
        set_a_rows: Sequence[Mapping[str, Any]],
        set_b_rows: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Compare two sets of extracted candidates and compute overlap/discrepancies."""
        a_by_idx = {row["source_row_index"]: row for row in set_a_rows if "source_row_index" in row}
        b_by_idx = {row["source_row_index"]: row for row in set_b_rows if "source_row_index" in row}

        common_indices = set(a_by_idx.keys()) & set(b_by_idx.keys())
        matches = 0
        discrepancies = []

        for idx in sorted(common_indices):
            labels_a = sorted(c.get("label") for c in a_by_idx[idx].get("candidates", []))
            labels_b = sorted(c.get("label") for c in b_by_idx[idx].get("candidates", []))
            if labels_a == labels_b:
                matches += 1
            else:
                discrepancies.append(
                    {
                        "source_row_index": idx,
                        "set_a": labels_a,
                        "set_b": labels_b,
                    }
                )

        return {
            "phase_f_consolidated": True,
            "analyzer_cluster": "candidate_state",
            "analyzer_module": "candidate_state_matrix",
            "summary": {
                "set_a_count": len(set_a_rows),
                "set_b_count": len(set_b_rows),
                "overlapping_keys": len(common_indices),
                "exact_candidate_set_matches": matches,
                "discrepancies_count": len(discrepancies),
            },
            "discrepancies": discrepancies,
        }

    def write_comparison_report(
        self,
        analysis: Mapping[str, Any],
        path: Path,
    ) -> None:
        summary = analysis["summary"]
        lines = [
            f"# CandidateSet Comparison: {self.description}",
            "",
            f"- Set A rows: {summary['set_a_count']}",
            f"- Set B rows: {summary['set_b_count']}",
            f"- Common rows: {summary['overlapping_keys']}",
            f"- Exact matches: {summary['exact_candidate_set_matches']}",
            f"- Discrepancy rows: {summary['discrepancies_count']}",
            "",
            "## Discrepancies Details",
            "",
            "| Row | Set A Candidates | Set B Candidates |",
            "| ---: | --- | --- |",
        ]
        for disc in analysis["discrepancies"]:
            lines.append(
                f"| {disc['source_row_index']} | {', '.join(disc['set_a'])} | "
                f"{', '.join(disc['set_b'])} |"
            )
        write_markdown_report(path, lines)
