"""Unified analyzer for projection rendering, scoring, routing, and verification decisions.

Consolidates projection render, scoring, routing, and decision diagnostics.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)


class ProjectionScoringAnalyzer:
    """Consolidated tool for downstream projection, scoring, routing, and decisions."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def analyze_pipeline_stages(
        self,
        projection_rows: Sequence[Mapping[str, Any]],
        score_rows: Sequence[Mapping[str, Any]],
        route_rows: Sequence[Mapping[str, Any]],
        decision_rows: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Perform combined analysis of pipeline stage metrics and routing efficiency."""
        purist_correct = sum(
            bool(row.get("comparison", {}).get("purist_correct", False))
            for row in score_rows
        )
        routed_rows = sum(
            bool(row.get("verification_route", {}).get("routed", False))
            for row in route_rows
        )
        actions = [
            row.get("verification_decision", {}).get("action", "abstain")
            for row in decision_rows
        ]
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "phase_f_consolidated": True,
            "analyzer_cluster": "projection_render_scoring",
            "analyzer_module": "projection_scoring",
            "summary": {
                "projection_rows": len(projection_rows),
                "score_rows": len(score_rows),
                "route_rows": len(route_rows),
                "decision_rows": len(decision_rows),
                "purist_correct": purist_correct,
                "purist_accuracy": (
                    round(purist_correct / len(score_rows), 4) if score_rows else 0.0
                ),
                "routed_rows": routed_rows,
                "routing_rate": round(routed_rows / len(route_rows), 4) if route_rows else 0.0,
                "action_counts": action_counts,
            }
        }

    def write_summary_report(
        self,
        analysis: Mapping[str, Any],
        path: Path,
    ) -> None:
        summary = analysis["summary"]
        lines = [
            f"# Projection & Scoring Analysis: {self.description}",
            "",
            "## Stage Summary",
            "",
            f"- Rendered projections: {summary['projection_rows']}",
            f"- Scored rows: {summary['score_rows']}",
            f"- Purist correct: {summary['purist_correct']} ({summary['purist_accuracy']:.2%})",
            f"- Routed rows: {summary['routed_rows']} ({summary['routing_rate']:.2%})",
            f"- Final decisions: {summary['decision_rows']}",
            "",
            "## Action Distributions",
            "",
            "| Action | Count |",
            "| --- | ---: |",
        ]
        for action, count in sorted(summary["action_counts"].items()):
            lines.append(f"| `{action}` | {count} |")
        write_markdown_report(path, lines)
