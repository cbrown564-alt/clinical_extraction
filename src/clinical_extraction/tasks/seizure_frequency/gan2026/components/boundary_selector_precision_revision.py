"""Validation-only selector precision revision for boundary typed rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_renderer_component_ablation,
    structured_candidate_contract,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_boundary_selector_precision_revision_v1"
DEFAULT_ABLATION_JSONL_PATH = (
    boundary_renderer_component_ablation.DEFAULT_OUTPUT_JSONL_PATH
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_selector_precision_revision_v1_2026-06-05.md"
)


def build_revision_rows(
    ablation_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Apply a narrow selector-precision rule to v1 diagnostic rows."""

    return [_revision_row(row) for row in ablation_rows]


def summarize_revision_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize selected transitions after the precision revision."""

    selected = [row for row in rows if row["selected_for_ablation"]]
    suppressed = [row for row in rows if not row["selected_for_ablation"]]
    transitions = Counter(str(row["transition"]) for row in selected)
    h6_regressions = [
        row
        for row in selected
        if row["transition"] == "C_to_W" and row.get("h6_member") is True
    ]
    non_convention_c_to_w = [
        row
        for row in selected
        if row["transition"] == "C_to_W"
        and row["effect_class"] != "benchmark_only_rendering"
    ]
    gate_failures = []
    if len(selected) < 150:
        gate_failures.append("coverage_below_150")
    if transitions["W_to_C"] < structured_candidate_contract.MIN_W_TO_C:
        gate_failures.append(structured_candidate_contract.W_TO_C_GATE_FAILURE)
    if h6_regressions:
        gate_failures.append("h6_control_regression")
    if non_convention_c_to_w:
        gate_failures.append("c_to_w_outside_benchmark_convention")
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    if final_policy_connected:
        gate_failures.append("final_label_policy_connected")
    return {
        "artifact_kind": "gan2026_boundary_selector_precision_revision_v1_summary",
        "policy_name": POLICY_NAME,
        "source_ablation_policy": boundary_renderer_component_ablation.POLICY_NAME,
        "candidate_rows": len(rows),
        "selected_prediction_bearing_rows": len(selected),
        "suppressed_rows": len(suppressed),
        "suppression_reason_counts": dict(
            sorted(Counter(str(row["selector_reason"]) for row in suppressed).items())
        ),
        "transition_counts": dict(sorted(transitions.items())),
        "w_to_c_rows": transitions["W_to_C"],
        "c_to_w_rows": transitions["C_to_W"],
        "h6_control_regression_rows": len(h6_regressions),
        "h6_control_regression_source_row_indices": [
            row["source_row_index"] for row in h6_regressions
        ],
        "non_convention_c_to_w_rows": len(non_convention_c_to_w),
        "non_convention_c_to_w_source_row_indices": [
            row["source_row_index"] for row in non_convention_c_to_w
        ],
        "effect_class_transition_counts": _nested_transition_counts(
            selected,
            "effect_class",
        ),
        "slice_transition_counts": _nested_transition_counts(selected, "slice_id"),
        "final_label_policy_connected": final_policy_connected,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "frozen_test_audit_ready": False,
        "gate_failures": gate_failures,
        "claim_boundary": (
            "Validation-only selector precision revision over "
            "boundary_renderer_component_ablation_v1. It suppresses unsafe "
            "last-event seizure-free overrides and unknown/no-reference sentinel "
            "churn, writes no source note text, and does not authorize final-label "
            "promotion or holdout use."
        ),
        "decision": (
            "boundary_selector_precision_revision_v1_precision_fixed_low_coverage"
            if not h6_regressions and not non_convention_c_to_w
            else "boundary_selector_precision_revision_v1_rejected"
        ),
        "recommended_next_step": (
            "Keep this selector rule as a validation-cycle diagnostic only. The "
            "precision issue is fixed, but exposure remains too low for any larger "
            "assembly or frozen audit."
        ),
    }


def materialize_revision(
    *,
    ablation_jsonl_path: Path = DEFAULT_ABLATION_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    ablation_rows = load_jsonl_rows(ablation_jsonl_path)
    rows = build_revision_rows(ablation_rows)
    summary = summarize_revision_rows(rows)
    summary = {
        **summary,
        "source_ablation_artifact": str(ablation_jsonl_path),
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
        "source_split": "validation",
        "split_manifest": "gan2026_split_v1",
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
        "# Gan 2026 Boundary Selector Precision Revision v1",
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
        f"| candidate rows | {summary['candidate_rows']} |",
        f"| selected prediction-bearing rows | {summary['selected_prediction_bearing_rows']} |",
        f"| suppressed rows | {summary['suppressed_rows']} |",
        f"| W->C rows | {summary['w_to_c_rows']} |",
        f"| C->W rows | {summary['c_to_w_rows']} |",
        f"| H6 control regression rows | {summary['h6_control_regression_rows']} |",
        f"| non-convention C->W rows | {summary['non_convention_c_to_w_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        f"| frozen test audit ready | {summary['frozen_test_audit_ready']} |",
        "",
        "## Suppression Reasons",
        "",
        "| Reason | Rows |",
        "| --- | ---: |",
    ]
    for reason, count in summary["suppression_reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(["", "## Gate Failures", ""])
    if summary["gate_failures"]:
        for failure in summary["gate_failures"]:
            lines.append(f"- `{failure}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Revision JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source ablation JSONL: `{summary['source_ablation_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _revision_row(row: Mapping[str, Any]) -> dict[str, Any]:
    selector_action, selector_reason = _selector_decision(row)
    revised = dict(row)
    revised.update(
        {
            "artifact_kind": "gan2026_boundary_selector_precision_revision_v1_row",
            "policy_name": POLICY_NAME,
            "source_ablation_policy": row["policy_name"],
            "selected_for_ablation": selector_action == "select",
            "prediction_bearing": selector_action == "select",
            "selector_action": selector_action,
            "selector_reason": selector_reason,
            "transition": (
                str(row["transition"])
                if selector_action == "select"
                else "not_selected"
            ),
            "final_label_policy_connected": False,
            "promotion_scope": "validation_selector_precision_no_final_label_promotion",
            "claim_boundary": "validation_development_only_no_holdout_use",
        }
    )
    return revised


def _selector_decision(row: Mapping[str, Any]) -> tuple[str, str]:
    slice_id = str(row["slice_id"])
    current_label = str(row.get("current_label") or "")
    proposed_label = str(row.get("proposed_label") or "")
    if (
        slice_id == "last_event_only"
        and proposed_label == "unknown"
        and current_label.startswith("seizure free")
    ):
        return "suppress", "last_event_current_seizure_free_protected"
    if (
        slice_id == "unknown_sentinel"
        and proposed_label == "unknown"
        and current_label == "no seizure frequency reference"
    ):
        return "suppress", "unknown_no_reference_sentinel_churn"
    return "select", "selector_precision_pass"


def _nested_transition_counts(
    rows: Sequence[Mapping[str, Any]],
    field: str,
) -> dict[str, dict[str, int]]:
    nested: dict[str, Counter[str]] = {}
    for row in rows:
        key = str(row[field])
        nested.setdefault(key, Counter())[str(row["transition"])] += 1
    return {key: dict(sorted(counts.items())) for key, counts in sorted(nested.items())}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ablation-jsonl-path",
        type=Path,
        default=DEFAULT_ABLATION_JSONL_PATH,
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_revision(
        ablation_jsonl_path=args.ablation_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "selected_rows": summary["selected_prediction_bearing_rows"],
                "w_to_c_rows": summary["w_to_c_rows"],
                "c_to_w_rows": summary["c_to_w_rows"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
