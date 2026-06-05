"""Apply the untagged-nonprediction release candidate over validation artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_untagged_nonprediction_release_candidate_v0"
DEFAULT_COMPONENT_CSV_PATH = Path(
    "experiments/"
    "gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_"
    "2026-06-04.csv"
)
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.md"
)

NONPREDICTION_ACTIONS = {"abstain", "human_review"}


def build_release_candidate_rows(
    component_rows: Sequence[Mapping[str, Any]],
    panel_rows: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Apply the untagged-nonprediction release candidate to validation rows."""

    panel_indices = {int(row["source_row_index"]) for row in panel_rows}
    rows = []
    for row in component_rows:
        hidden_families = _split_hidden_families(row.get("hidden_families", ""))
        original_action = row.get("final_action")
        release_applied = (
            original_action in NONPREDICTION_ACTIONS
            and not hidden_families
        )
        candidate_action = "predict" if release_applied else original_action
        candidate_label = (
            row.get("deterministic_comparator_label")
            if release_applied
            else row.get("prediction_label")
        )
        candidate_correct = (
            _bool(row.get("deterministic_comparator_purist_correct"))
            if release_applied
            else _bool(row.get("final_purist_correct"))
        )
        rows.append(
            {
                "artifact_kind": "gan2026_untagged_nonprediction_release_candidate_row",
                "policy_name": POLICY_NAME,
                "source_row_index": int(row["source_row_index"]),
                "split": row.get("split", "validation"),
                "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
                "surface_membership": (
                    "h2_h4_component_stress_panel"
                    if int(row["source_row_index"]) in panel_indices
                    else "validation750_nonpanel"
                ),
                "hidden_families": hidden_families,
                "original_action": original_action,
                "candidate_action": candidate_action,
                "release_applied": release_applied,
                "release_reason": (
                    "untagged_nonprediction" if release_applied else "unchanged"
                ),
                "original_label": row.get("prediction_label") or None,
                "candidate_label": candidate_label or None,
                "baseline_label": row.get("deterministic_comparator_label"),
                "gold_label": row.get("gold_label"),
                "baseline_transition": row.get("comparator_transition"),
                "original_purist_correct": _bool(row.get("final_purist_correct")),
                "candidate_purist_correct": candidate_correct,
                "baseline_purist_correct": _bool(
                    row.get("deterministic_comparator_purist_correct")
                ),
                "router_reason": row.get("router_reason"),
                "claim_boundary": "validation_development_only_no_holdout_row_level_use",
            }
        )
    rows.sort(key=lambda item: item["source_row_index"])
    return rows


def summarize_release_candidate_rows(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize candidate coverage, correctness, and H6 control behavior."""

    release_rows = [row for row in rows if row["release_applied"] is True]
    panel_rows = [
        row for row in rows if row["surface_membership"] == "h2_h4_component_stress_panel"
    ]
    panel_release_rows = [row for row in panel_rows if row["release_applied"] is True]
    h6_controls = [
        row
        for row in panel_rows
        if row["original_action"] == "predict"
        and row["baseline_transition"] == "C_to_C"
    ]
    candidate_prediction_rows = [
        row for row in rows if row["candidate_action"] == "predict"
    ]
    return {
        "artifact_kind": "gan2026_untagged_nonprediction_release_candidate_summary",
        "policy_name": POLICY_NAME,
        "split_manifest": _first_nonempty(row.get("split_manifest") for row in rows),
        "row_count": len(rows),
        "release_rows": len(release_rows),
        "panel_release_rows": len(panel_release_rows),
        "candidate_prediction_bearing_rows": len(candidate_prediction_rows),
        "candidate_correct_prediction_rows": sum(
            row["candidate_purist_correct"] is True for row in candidate_prediction_rows
        ),
        "release_correct_rows": sum(
            row["candidate_purist_correct"] is True for row in release_rows
        ),
        "release_wrong_rows": sum(
            row["candidate_purist_correct"] is False for row in release_rows
        ),
        "release_transition_counts": dict(
            Counter(str(row["baseline_transition"]) for row in release_rows)
        ),
        "release_reason_counts": dict(
            Counter(str(row["router_reason"]) for row in release_rows)
        ),
        "h6_control_rows": len(h6_controls),
        "h6_control_preserved_rows": sum(
            row["candidate_purist_correct"] is True for row in h6_controls
        ),
        "h6_control_regression_rows": sum(
            row["candidate_purist_correct"] is not True for row in h6_controls
        ),
        "locked_test_row_level_artifacts_used": 0,
        "claim_boundary": (
            "Validation-development no-call candidate patch. It releases only "
            "staged-policy nonprediction rows with no hidden-family tags by "
            "falling back to the deterministic comparator label. This does not "
            "authorize holdout use or benchmark-comparable claims."
        ),
        "decision": _decision(release_rows, h6_controls),
        "recommended_next_step": _recommended_next_step(release_rows, h6_controls),
    }


def materialize_release_candidate(
    *,
    component_csv_path: Path = DEFAULT_COMPONENT_CSV_PATH,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    component_rows = _read_csv_rows(component_csv_path)
    panel_rows = load_jsonl_rows(panel_jsonl_path) if panel_jsonl_path.exists() else []
    rows = build_release_candidate_rows(component_rows, panel_rows)
    summary = summarize_release_candidate_rows(rows)
    summary = {
        **summary,
        "source_component_matrix": str(component_csv_path),
        "source_panel_artifact": str(panel_jsonl_path),
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
    }
    write_jsonl_rows(rows, output_jsonl_path)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(summary, output_report_path)
    return summary


def write_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 Untagged Nonprediction Release Candidate v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| rows | {summary['row_count']} |",
        f"| released rows | {summary['release_rows']} |",
        f"| panel released rows | {summary['panel_release_rows']} |",
        f"| prediction-bearing rows | {summary['candidate_prediction_bearing_rows']} |",
        f"| correct prediction rows | {summary['candidate_correct_prediction_rows']} |",
        f"| release correct rows | {summary['release_correct_rows']} |",
        f"| release wrong rows | {summary['release_wrong_rows']} |",
        f"| H6 controls | {summary['h6_control_rows']} |",
        f"| H6 regressions | {summary['h6_control_regression_rows']} |",
        "",
        "## Release Transitions",
        "",
        "| Transition | Rows |",
        "| --- | ---: |",
    ]
    for transition, count in sorted(summary["release_transition_counts"].items()):
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Candidate JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Component matrix: `{summary['source_component_matrix']}`",
            f"- H2/H4 panel: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _decision(
    release_rows: Sequence[Mapping[str, Any]],
    h6_controls: Sequence[Mapping[str, Any]],
) -> str:
    release_wrong = sum(row["candidate_purist_correct"] is False for row in release_rows)
    h6_regressions = sum(row["candidate_purist_correct"] is not True for row in h6_controls)
    if release_rows and release_wrong == 0 and h6_regressions == 0:
        return "candidate_patch_passes_validation_no_regression_gate"
    return "candidate_patch_rejected_or_needs_narrowing"


def _recommended_next_step(
    release_rows: Sequence[Mapping[str, Any]],
    h6_controls: Sequence[Mapping[str, Any]],
) -> str:
    if (
        release_rows
        and sum(row["candidate_purist_correct"] is False for row in release_rows) == 0
        and sum(row["candidate_purist_correct"] is not True for row in h6_controls) == 0
    ):
        return (
            "Freeze this validation-cycle candidate in a protocol addendum before "
            "any broader assembly use: no hidden-family tags, staged nonprediction, "
            "deterministic comparator fallback, and H6 controls unchanged."
        )
    return "Narrow the release rule before any protocol or holdout-facing work."


def _read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _split_hidden_families(value: Any) -> list[str]:
    text = str(value or "")
    delimiter = "|" if "|" in text else ";"
    return [part for part in text.split(delimiter) if part]


def _bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if value == "True":
        return True
    if value == "False":
        return False
    return None


def _first_nonempty(values: Sequence[Any] | Any) -> str:
    for value in values:
        if value:
            return str(value)
    return ""


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component-csv-path", type=Path, default=DEFAULT_COMPONENT_CSV_PATH)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    materialize_release_candidate(
        component_csv_path=args.component_csv_path,
        panel_jsonl_path=args.panel_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
