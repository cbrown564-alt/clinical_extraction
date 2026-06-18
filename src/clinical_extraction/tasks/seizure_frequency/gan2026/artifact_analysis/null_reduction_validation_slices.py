"""Generate validation proxy slices for holdout-aligned null reduction diagnostics."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_SCORE_JSONL_PATH = Path(
    "experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0.score.jsonl"
)
DEFAULT_ROUTE_JSONL_PATH = Path(
    "experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0.route.jsonl"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    ""
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_validation750_null_reduction_slices_baseline_2026-06-07.json"
)

SLICE_DEFINITIONS = {
    "frequency_rate_values_unparsed": {
        "description": "Frequency rate facts extracted but count/range/period operands remained unparsed.",
        "match_fn": lambda issues: "frequency_rate_values_unparsed" in issues or "frequency_label_values_unparsed" in issues,
    },
    "frequency_rate_values_incomplete": {
        "description": "Frequency rate facts extracted but required count/period operands were incomplete.",
        "match_fn": lambda issues: "frequency_rate_values_incomplete" in issues,
    },
    "vague_count": {
        "description": "Frequency count is vague (e.g. multiple) but Observation period is explicit.",
        "match_fn": lambda issues: "vague_count" in issues,
    },
    "seizure_free_duration_required": {
        "description": "Seizure free state extracted but durational boundaries/anchors were missing.",
        "match_fn": lambda issues: "seizure_free_duration_required" in issues,
    },
    "seizure_free_duration_unparsed": {
        "description": "Seizure free state extracted but durational values could not be parsed.",
        "match_fn": lambda issues: "seizure_free_duration_unparsed" in issues or "seizure_free_label_values_unparsed" in issues,
    },
    "cluster_frequency_values_unparsed": {
        "description": "Cluster frequency state extracted but cluster cadence/size operands remained unparsed.",
        "match_fn": lambda issues: "cluster_frequency_values_unparsed" in issues or "cluster_label_values_unparsed" in issues,
    },
    "cluster_cadence_values_incomplete": {
        "description": "Cluster frequency state extracted but required cadence or size operands were incomplete.",
        "match_fn": lambda issues: "cluster_cadence_values_incomplete" in issues,
    },
}


def _index_rows_by_source_row_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    indexed: dict[int, Mapping[str, Any]] = {}
    for row in rows:
        source_row_index = row.get("source_row_index")
        if isinstance(source_row_index, int):
            indexed[source_row_index] = row
    return indexed


def _selected_evidence_status(row: Mapping[str, Any]) -> Mapping[str, Any]:
    projection = row.get("projection_decision")
    if isinstance(projection, Mapping):
        status = projection.get("selected_evidence_status")
        if isinstance(status, Mapping):
            return status
    return {}


def _row_state(
    score_row: Mapping[str, Any],
    route_row: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    projection = score_row.get("projection_decision")
    projection = projection if isinstance(projection, Mapping) else {}
    score_info = score_row.get("score")
    score_info = score_info if isinstance(score_info, Mapping) else {}
    issues = sorted({str(issue) for issue in (projection.get("projection_issues") or [])})
    rendered_label = (score_row.get("final_rendered_label") or {}).get("rendered_label")
    selected_evidence_status = _selected_evidence_status(score_row)
    exact_trace = selected_evidence_status.get("exact_trace")
    source_id_status = str(selected_evidence_status.get("source_id_status") or "")

    routed = False
    route_families: list[str] = []
    if route_row is not None:
        verification_route = route_row.get("verification_route")
        verification_route = (
            verification_route if isinstance(verification_route, Mapping) else {}
        )
        routed = bool(verification_route.get("routed"))
        route_families = sorted(
            str(family) for family in (verification_route.get("route_families") or [])
        )

    return {
        "source_row_index": int(score_row["source_row_index"]),
        "source_normalized_phrase": str(projection.get("source_normalized_phrase") or ""),
        "gold_label": str(score_info.get("gold_label") or ""),
        "rendered_label": rendered_label,
        "rendered": rendered_label is not None,
        "purist_correct": bool(score_info.get("purist_correct", False)),
        "pragmatic_correct": bool(score_info.get("pragmatic_correct", False)),
        "routed": routed,
        "issues": issues,
        "route_families": route_families,
        "exact_trace": exact_trace,
        "source_id_status": source_id_status,
        "trace_valid": exact_trace is True,
        "source_id_valid": source_id_status == "valid",
    }


def _transition_metrics(
    current_rows: Sequence[Mapping[str, Any]],
    baseline_rows: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    baseline_by_index = {
        int(row["source_row_index"]): row for row in baseline_rows if "source_row_index" in row
    }
    current_by_index = {
        int(row["source_row_index"]): row for row in current_rows if "source_row_index" in row
    }
    shared_indices = sorted(set(current_by_index) & set(baseline_by_index))

    newly_rendered = 0
    newly_null = 0
    wrong_to_correct = 0
    correct_to_wrong = 0
    newly_routed = 0
    newly_unrouted = 0

    for source_row_index in shared_indices:
        baseline = baseline_by_index[source_row_index]
        current = current_by_index[source_row_index]
        if (not baseline["rendered"]) and current["rendered"]:
            newly_rendered += 1
        if baseline["rendered"] and (not current["rendered"]):
            newly_null += 1
        if (not baseline["purist_correct"]) and current["purist_correct"]:
            wrong_to_correct += 1
        if baseline["purist_correct"] and (not current["purist_correct"]):
            correct_to_wrong += 1
        if (not baseline["routed"]) and current["routed"]:
            newly_routed += 1
        if baseline["routed"] and (not current["routed"]):
            newly_unrouted += 1

    return {
        "shared_row_count": len(shared_indices),
        "baseline_only_row_count": len(set(baseline_by_index) - set(current_by_index)),
        "current_only_row_count": len(set(current_by_index) - set(baseline_by_index)),
        "newly_rendered_count": newly_rendered,
        "newly_null_count": newly_null,
        "wrong_to_correct_count": wrong_to_correct,
        "correct_to_wrong_count": correct_to_wrong,
        "newly_routed_count": newly_routed,
        "newly_unrouted_count": newly_unrouted,
    }


def _summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "row_count": len(rows),
        "rendered_count": sum(bool(row["rendered"]) for row in rows),
        "null_count": sum(not bool(row["rendered"]) for row in rows),
        "routed_count": sum(bool(row["routed"]) for row in rows),
        "purist_correct_count": sum(bool(row["purist_correct"]) for row in rows),
        "pragmatic_correct_count": sum(bool(row["pragmatic_correct"]) for row in rows),
        "trace_valid_count": sum(bool(row["trace_valid"]) for row in rows),
        "source_id_valid_count": sum(bool(row["source_id_valid"]) for row in rows),
        "trace_or_source_gap_count": sum(
            not (bool(row["trace_valid"]) and bool(row["source_id_valid"])) for row in rows
        ),
    }


def build_validation_slices(
    score_rows: Sequence[Mapping[str, Any]],
    *,
    route_rows: Sequence[Mapping[str, Any]] | None = None,
    baseline_score_rows: Sequence[Mapping[str, Any]] | None = None,
    baseline_route_rows: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Analyze score and route rows and group them into validation proxy slices."""

    slices_summary: dict[str, Any] = {}
    route_by_index = _index_rows_by_source_row_index(route_rows or [])
    baseline_route_by_index = _index_rows_by_source_row_index(baseline_route_rows or [])

    for slice_name, spec in SLICE_DEFINITIONS.items():
        matching_rows: list[dict[str, Any]] = []
        for row in score_rows:
            proj = row.get("projection_decision") or {}
            issues = set(proj.get("projection_issues") or [])
            if spec["match_fn"](issues):
                source_row_index = int(row["source_row_index"])
                matching_rows.append(
                    _row_state(
                        row,
                        route_row=route_by_index.get(source_row_index),
                    )
                )

        slice_summary = {
            "description": spec["description"],
            **_summarize_rows(matching_rows),
            "rows": matching_rows,
        }
        if baseline_score_rows is not None:
            baseline_rows: list[dict[str, Any]] = []
            for row in baseline_score_rows:
                proj = row.get("projection_decision") or {}
                issues = set(proj.get("projection_issues") or [])
                if spec["match_fn"](issues):
                    source_row_index = int(row["source_row_index"])
                    baseline_rows.append(
                        _row_state(
                            row,
                            route_row=baseline_route_by_index.get(source_row_index),
                        )
                    )
            slice_summary["baseline"] = {
                **_summarize_rows(baseline_rows),
                "rows": baseline_rows,
            }
            slice_summary["transitions"] = _transition_metrics(
                current_rows=matching_rows,
                baseline_rows=baseline_rows,
            )
            changed_rows: list[dict[str, Any]] = []
            baseline_by_index = {
                int(row["source_row_index"]): row for row in baseline_rows
            }
            for row in matching_rows:
                baseline = baseline_by_index.get(int(row["source_row_index"]))
                if baseline is None:
                    continue
                if (
                    baseline["rendered_label"] != row["rendered_label"]
                    or baseline["purist_correct"] != row["purist_correct"]
                    or baseline["routed"] != row["routed"]
                ):
                    changed_rows.append(
                        {
                            "source_row_index": row["source_row_index"],
                            "source_normalized_phrase": row["source_normalized_phrase"],
                            "gold_label": row["gold_label"],
                            "baseline_rendered_label": baseline["rendered_label"],
                            "current_rendered_label": row["rendered_label"],
                            "baseline_purist_correct": baseline["purist_correct"],
                            "current_purist_correct": row["purist_correct"],
                            "baseline_routed": baseline["routed"],
                            "current_routed": row["routed"],
                        }
                    )
            slice_summary["changed_rows"] = changed_rows
        slices_summary[slice_name] = slice_summary

    return {
        "artifact_kind": "gan2026_validation750_null_reduction_slices_v1",
        "claim_boundary": "baseline validation-development null reduction proxy slices; no holdout use",
        "comparison_enabled": baseline_score_rows is not None,
        "report_title": (
            "Gan 2026 Validation750 Null Reduction Proxy Slices Comparison"
            if baseline_score_rows is not None
            else "Gan 2026 Validation750 Null Reduction Proxy Slices Baseline"
        ),
        "slices": slices_summary,
    }


def write_report(summary: Mapping[str, Any], path: Path) -> None:
    """Write markdown report with proxy slice diagnostics."""

    lines = [
        f"# {summary['report_title']}",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Summary of Slices",
        "",
        "| Slice Family | Rows | Rendered | Null | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Valid Source IDs |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for slice_name, data in sorted(summary["slices"].items()):
        lines.append(
            f"| `{slice_name}` | {data['row_count']} | {data['rendered_count']} | "
            f"{data['null_count']} | {data['routed_count']} | "
            f"{data['purist_correct_count']} | {data['pragmatic_correct_count']} | "
            f"{data['trace_valid_count']} | {data['source_id_valid_count']} |"
        )

    lines.append("")

    for slice_name, data in sorted(summary["slices"].items()):
        lines.extend([
            f"## Slice Details: `{slice_name}`",
            "",
            f"- **Description**: {data['description']}",
            f"- **Row count**: {data['row_count']}",
            f"- **Null count**: {data['null_count']}",
            f"- **Rendered count**: {data['rendered_count']}",
            f"- **Routed count**: {data['routed_count']}",
            f"- **Purist-correct count**: {data['purist_correct_count']}",
            f"- **Pragmatic-correct count**: {data['pragmatic_correct_count']}",
            f"- **Exact-trace rows**: {data['trace_valid_count']}",
            f"- **Valid source-id rows**: {data['source_id_valid_count']}",
            f"- **Trace or source-id gap rows**: {data['trace_or_source_gap_count']}",
            "",
        ])

        if "baseline" in data and "transitions" in data:
            baseline = data["baseline"]
            transitions = data["transitions"]
            lines.extend([
                "### Baseline Comparison",
                "",
                f"- **Baseline row count**: {baseline['row_count']}",
                f"- **Baseline rendered/null/routed**: {baseline['rendered_count']} / {baseline['null_count']} / {baseline['routed_count']}",
                f"- **Shared rows**: {transitions['shared_row_count']}",
                f"- **Current-only rows**: {transitions['current_only_row_count']}",
                f"- **Baseline-only rows**: {transitions['baseline_only_row_count']}",
                f"- **Wrong-to-correct**: {transitions['wrong_to_correct_count']}",
                f"- **Correct-to-wrong**: {transitions['correct_to_wrong_count']}",
                f"- **Newly rendered**: {transitions['newly_rendered_count']}",
                f"- **Newly null**: {transitions['newly_null_count']}",
                f"- **Newly routed**: {transitions['newly_routed_count']}",
                f"- **Newly unrouted**: {transitions['newly_unrouted_count']}",
                "",
            ])
            if data["changed_rows"]:
                lines.extend([
                    "### Changed rows (first 15 shared rows)",
                    "",
                    "| Row Index | Source Phrase | Gold Label | Baseline Rendered | Current Rendered | Baseline Purist | Current Purist | Baseline Routed | Current Routed |",
                    "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
                ])
                for row in data["changed_rows"][:15]:
                    lines.append(
                        f"| {row['source_row_index']} | `{row['source_normalized_phrase']}` | "
                        f"`{row['gold_label']}` | `{row['baseline_rendered_label'] or 'NULL'}` | "
                        f"`{row['current_rendered_label'] or 'NULL'}` | "
                        f"{row['baseline_purist_correct']} | {row['current_purist_correct']} | "
                        f"{row['baseline_routed']} | {row['current_routed']} |"
                    )
                lines.append("")

        lines.extend([
            "### First 15 matching rows:",
            "",
            "| Row Index | Source Phrase | Gold Label | Rendered | Routed | Purist Correct | Pragmatic Correct | Exact Trace | Source ID Status | Issues | Route Families |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ])
        for r in data["rows"][:15]:
            issues_str = ", ".join(f"`{i}`" for i in r["issues"]) or "-"
            route_families_str = ", ".join(f"`{i}`" for i in r["route_families"]) or "-"
            lines.append(
                f"| {r['source_row_index']} | `{r['source_normalized_phrase']}` | "
                f"`{r['gold_label']}` | `{r['rendered_label'] or 'NULL'}` | "
                f"{r['routed']} | {r['purist_correct']} | {r['pragmatic_correct']} | "
                f"{r['trace_valid']} | `{r['source_id_status'] or 'missing'}` | "
                f"{issues_str} | {route_families_str} |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate validation proxy slices for null reduction.")
    parser.add_argument("--score-jsonl-path", type=Path, default=DEFAULT_SCORE_JSONL_PATH)
    parser.add_argument("--route-jsonl-path", type=Path, default=DEFAULT_ROUTE_JSONL_PATH)
    parser.add_argument("--baseline-score-jsonl-path", type=Path, default=None)
    parser.add_argument("--baseline-route-jsonl-path", type=Path, default=None)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    args = parser.parse_args()

    score_rows = load_jsonl_rows(args.score_jsonl_path)
    route_rows = load_jsonl_rows(args.route_jsonl_path)
    baseline_score_rows = (
        load_jsonl_rows(args.baseline_score_jsonl_path)
        if args.baseline_score_jsonl_path
        else None
    )
    baseline_route_rows = (
        load_jsonl_rows(args.baseline_route_jsonl_path)
        if args.baseline_route_jsonl_path
        else None
    )
    summary = build_validation_slices(
        score_rows,
        route_rows=route_rows,
        baseline_score_rows=baseline_score_rows,
        baseline_route_rows=baseline_route_rows,
    )

    args.output_json_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    
    write_report(summary, args.output_report_path)
    print(f"Slice summary report written to {args.output_report_path}")


if __name__ == "__main__":
    main()
