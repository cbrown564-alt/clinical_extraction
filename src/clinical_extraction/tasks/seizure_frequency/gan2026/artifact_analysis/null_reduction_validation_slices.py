"""Generate validation proxy slices for holdout-aligned null reduction diagnostic report."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

DEFAULT_SCORE_JSONL_PATH = Path(
    "experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0.score.jsonl"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "docs/research/gan2026_validation750_null_reduction_slices_baseline_2026-06-07.md"
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


def build_validation_slices(
    score_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Analyze score rows and group them into validation proxy slices."""

    slices_summary: dict[str, Any] = {}
    
    for slice_name, spec in SLICE_DEFINITIONS.items():
        matching_rows = []
        for row in score_rows:
            proj = row.get("projection_decision") or {}
            issues = set(proj.get("projection_issues") or [])
            rendered_label = (row.get("final_rendered_label") or {}).get("rendered_label")
            
            # Check if this row matches the slice definition
            if spec["match_fn"](issues):
                score_info = row.get("score") or {}
                matching_rows.append({
                    "source_row_index": int(row["source_row_index"]),
                    "source_normalized_phrase": proj.get("source_normalized_phrase", ""),
                    "gold_label": score_info.get("gold_label", ""),
                    "rendered_label": rendered_label,
                    "purist_correct": bool(score_info.get("purist_correct", False)),
                    "pragmatic_correct": bool(score_info.get("pragmatic_correct", False)),
                    "issues": sorted(list(issues)),
                })
        
        # Calculate summary metrics for the slice
        row_count = len(matching_rows)
        rendered_count = sum(r["rendered_label"] is not None for r in matching_rows)
        null_count = sum(r["rendered_label"] is None for r in matching_rows)
        purist_correct_count = sum(r["purist_correct"] for r in matching_rows)
        pragmatic_correct_count = sum(r["pragmatic_correct"] for r in matching_rows)
        
        slices_summary[slice_name] = {
            "description": spec["description"],
            "row_count": row_count,
            "rendered_count": rendered_count,
            "null_count": null_count,
            "purist_correct_count": purist_correct_count,
            "pragmatic_correct_count": pragmatic_correct_count,
            "rows": matching_rows,
        }

    return {
        "artifact_kind": "gan2026_validation750_null_reduction_slices_baseline",
        "claim_boundary": "baseline validation-development null reduction proxy slices; no holdout use",
        "slices": slices_summary,
    }


def write_report(summary: Mapping[str, Any], path: Path) -> None:
    """Write markdown report with proxy slice diagnostics."""

    lines = [
        "# Gan 2026 Validation750 Null Reduction Proxy Slices Baseline",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Summary of Slices",
        "",
        "| Slice Family | Description | Total Rows | Rendered | Null | Purist Correct | Pragmatic Correct |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    
    for slice_name, data in sorted(summary["slices"].items()):
        lines.append(
            f"| `{slice_name}` | {data['description']} | "
            f"{data['row_count']} | {data['rendered_count']} | {data['null_count']} | "
            f"{data['purist_correct_count']} | {data['pragmatic_correct_count']} |"
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
            "",
            "### First 15 matching rows:",
            "",
            "| Row Index | Source Phrase | Gold Label | Rendered | Purist Correct | Pragmatic Correct | Normalization Issues |",
            "| ---: | --- | --- | --- | --- | --- | --- |",
        ])
        
        for r in data["rows"][:15]:
            issues_str = ", ".join(f"`{i}`" for i in r["issues"])
            lines.append(
                f"| {r['source_row_index']} | `{r['source_normalized_phrase']}` | "
                f"`{r['gold_label']}` | `{r['rendered_label'] or 'NULL'}` | "
                f"{r['purist_correct']} | {r['pragmatic_correct']} | {issues_str} |"
            )
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate validation proxy slices for null reduction.")
    parser.add_argument("--score-jsonl-path", type=Path, default=DEFAULT_SCORE_JSONL_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    args = parser.parse_args()

    score_rows = load_jsonl_rows(args.score_jsonl_path)
    summary = build_validation_slices(score_rows)

    args.output_json_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    
    write_report(summary, args.output_report_path)
    print(f"Slice summary report written to {args.output_report_path}")


if __name__ == "__main__":
    main()
