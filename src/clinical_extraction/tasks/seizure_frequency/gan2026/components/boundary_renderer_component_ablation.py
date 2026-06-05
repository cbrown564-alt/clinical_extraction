"""Validation diagnostic ablation for boundary and renderer typed events."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_event_validation_panel,
    structured_candidate_contract,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

POLICY_NAME = "gan2026_boundary_renderer_component_ablation_v1"
DEFAULT_PANEL_JSONL_PATH = boundary_event_validation_panel.DEFAULT_OUTPUT_JSONL_PATH
DEFAULT_CURRENT_CANDIDATE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_"
    "2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_renderer_component_ablation_v1_2026-06-05.md"
)


def build_ablation_rows(
    panel_rows: Sequence[Mapping[str, Any]],
    current_candidate_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Layer typed event rows over the current validation assembly."""

    current_by_source_index = {
        int(row["source_row_index"]): row for row in current_candidate_rows
    }
    rows = [
        _ablation_row(row, current_by_source_index.get(int(row["source_row_index"]), {}))
        for row in panel_rows
    ]
    rows.sort(key=lambda row: (row["effect_class"], row["source_row_index"]))
    return rows


def build_rows_and_summary(
    panel_rows: Sequence[Mapping[str, Any]],
    current_candidate_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = build_ablation_rows(panel_rows, current_candidate_rows)
    return rows, summarize_ablation_rows(rows, current_candidate_rows)


def summarize_ablation_rows(
    rows: Sequence[Mapping[str, Any]],
    current_candidate_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize validation diagnostic transitions and gates."""

    selected = [row for row in rows if row["selected_for_ablation"]]
    transitions = Counter(str(row["transition"]) for row in selected)
    effect_transitions = _nested_transition_counts(selected, "effect_class")
    mechanism_transitions = _nested_transition_counts(selected, "target_mechanism")
    slice_transitions = _nested_transition_counts(selected, "slice_id")
    target_family_transitions = _nested_transition_counts(selected, "target_family")
    h6_control_rows = [
        row
        for row in current_candidate_rows
        if row.get("h6_member") is True and row.get("h6_panel_role") == "control"
    ]
    selected_h6_rows = [
        row for row in selected if row.get("h6_member") is True
    ]
    h6_regression_rows = [
        row for row in selected_h6_rows if row["transition"] == "C_to_W"
    ]
    non_convention_c_to_w_rows = [
        row
        for row in selected
        if row["transition"] == "C_to_W"
        and row["effect_class"] != "benchmark_only_rendering"
    ]
    selected_count = len(selected)
    c_to_w_rate = _rate(transitions["C_to_W"], selected_count)
    gate_failures = []
    if selected_count < structured_candidate_contract.MIN_VALIDATION_COVERAGE:
        gate_failures.append("coverage_below_150")
    if transitions["W_to_C"] < structured_candidate_contract.MIN_W_TO_C:
        gate_failures.append(structured_candidate_contract.W_TO_C_GATE_FAILURE)
    if c_to_w_rate > structured_candidate_contract.MAX_C_TO_W_RATE:
        gate_failures.append("c_to_w_above_5_percent")
    if non_convention_c_to_w_rows:
        gate_failures.append("c_to_w_outside_benchmark_convention")
    if h6_regression_rows:
        gate_failures.append("h6_control_regression")
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    if final_policy_connected:
        gate_failures.append("final_label_policy_connected")
    source_note_text_rows = sum(bool(row.get("source_note_text_present")) for row in rows)
    if source_note_text_rows:
        gate_failures.append("source_note_text_present")
    return {
        "artifact_kind": "gan2026_boundary_renderer_component_ablation_v1_summary",
        "policy_name": POLICY_NAME,
        "candidate_rows": len(rows),
        "selected_prediction_bearing_rows": selected_count,
        "transition_counts": dict(sorted(transitions.items())),
        "w_to_c_rows": transitions["W_to_C"],
        "c_to_w_rows": transitions["C_to_W"],
        "c_to_w_rate": c_to_w_rate,
        "benchmark_only_transition_counts": effect_transitions.get(
            "benchmark_only_rendering", {}
        ),
        "clinical_boundary_transition_counts": effect_transitions.get(
            "clinical_boundary_projection", {}
        ),
        "effect_class_transition_counts": effect_transitions,
        "target_mechanism_transition_counts": mechanism_transitions,
        "target_family_transition_counts": target_family_transitions,
        "slice_transition_counts": slice_transitions,
        "exact_evidence_rows": sum(row["exact_evidence"] is True for row in rows),
        "contract_matched_rows": sum(row["contract_matched"] is True for row in rows),
        "source_note_text_rows": source_note_text_rows,
        "h6_control_rows": len(h6_control_rows),
        "selected_h6_rows": len(selected_h6_rows),
        "h6_control_regression_rows": len(h6_regression_rows),
        "h6_control_regression_source_row_indices": [
            row["source_row_index"] for row in h6_regression_rows
        ],
        "non_convention_c_to_w_rows": len(non_convention_c_to_w_rows),
        "non_convention_c_to_w_source_row_indices": [
            row["source_row_index"] for row in non_convention_c_to_w_rows
        ],
        "final_label_policy_connected": final_policy_connected,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "frozen_test_audit_ready": not gate_failures,
        "gate_failures": gate_failures,
        "claim_boundary": (
            "Validation-development boundary_renderer_component_ablation_v1. It "
            "connects the passed typed-event panel only inside a validation "
            "diagnostic layer, separates benchmark-only rendering from clinical "
            "boundary projection, writes no source note text, and does not "
            "authorize final-label promotion or holdout use."
        ),
        "decision": (
            "boundary_renderer_component_ablation_v1_ready_for_expansion"
            if not gate_failures
            else "boundary_renderer_component_ablation_v1_rejected_revise_only"
        ),
        "recommended_next_step": (
            "Do not promote this low-exposure typed layer. Revise the validation-only "
            "cycle to improve selector precision for last-event and unknown-frequency "
            "boundary rows before any larger diagnostic assembly."
        ),
    }


def materialize_component_ablation(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    current_candidate_jsonl_path: Path = DEFAULT_CURRENT_CANDIDATE_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    panel_rows = load_jsonl_rows(panel_jsonl_path)
    current_candidate_rows = load_jsonl_rows(current_candidate_jsonl_path)
    rows, summary = build_rows_and_summary(panel_rows, current_candidate_rows)
    summary = {
        **summary,
        "source_panel_artifact": str(panel_jsonl_path),
        "source_current_candidate_artifact": str(current_candidate_jsonl_path),
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
        "# Gan 2026 Boundary Renderer Component Ablation v1",
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
        f"| W->C rows | {summary['w_to_c_rows']} |",
        f"| C->W rows | {summary['c_to_w_rows']} |",
        f"| C->W rate | {summary['c_to_w_rate']:.4f} |",
        f"| non-convention C->W rows | {summary['non_convention_c_to_w_rows']} |",
        f"| H6 control rows | {summary['h6_control_rows']} |",
        f"| selected H6 rows | {summary['selected_h6_rows']} |",
        f"| H6 control regression rows | {summary['h6_control_regression_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| source-note-text rows | {summary['source_note_text_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        f"| frozen test audit ready | {summary['frozen_test_audit_ready']} |",
        "",
        "## Gate Failures",
        "",
    ]
    if summary["gate_failures"]:
        for failure in summary["gate_failures"]:
            lines.append(f"- `{failure}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Effect Classes",
            "",
            "| Effect class | W->C | C->W | C->C | W->W |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for effect_class, counts in summary["effect_class_transition_counts"].items():
        lines.append(
            f"| `{effect_class}` | {counts.get('W_to_C', 0)} | "
            f"{counts.get('C_to_W', 0)} | {counts.get('C_to_C', 0)} | "
            f"{counts.get('W_to_W', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Ablation JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            (
                "- Source current candidate JSONL: "
                f"`{summary['source_current_candidate_artifact']}`"
            ),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _ablation_row(
    panel_row: Mapping[str, Any],
    current_row: Mapping[str, Any],
) -> dict[str, Any]:
    current_label = str(current_row.get("candidate_label") or "")
    proposed_label = str(panel_row["gan_rendered_label"])
    selected = (
        panel_row["exact_evidence"] is True
        and proposed_label != ""
        and panel_row.get("final_label_policy_connected") is False
    )
    transition = _transition(
        current_label=current_label,
        proposed_label=proposed_label,
        gold_label=str(panel_row["gold_label"]),
        selected=selected,
    )
    effect_class = _effect_class(panel_row)
    return {
        "artifact_kind": "gan2026_boundary_renderer_component_ablation_v1_row",
        "policy_name": POLICY_NAME,
        "source_row_index": int(panel_row["source_row_index"]),
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "slice_id": panel_row["slice_id"],
        "panel_role": panel_row["panel_role"],
        "target_family": panel_row["target_family"],
        "target_mechanism": panel_row["target_mechanism"],
        "effect_class": effect_class,
        "component_owner": panel_row["clinical_event"]["component_owner"],
        "clinical_event": panel_row["clinical_event"],
        "boundary_state": panel_row["boundary_state"],
        "selected_frequency_state": panel_row["selected_frequency_state"],
        "projection_policy": panel_row["projection_policy"],
        "benchmark_format_rule_id": panel_row["projection_policy"][
            "benchmark_format_rule_id"
        ],
        "current_label": current_label,
        "proposed_label": proposed_label,
        "gold_label": panel_row["gold_label"],
        "transition": transition,
        "selected_for_ablation": selected,
        "prediction_bearing": selected,
        "exact_evidence": bool(panel_row["exact_evidence"]),
        "evidence": panel_row["evidence"],
        "source_note_text": None,
        "source_note_text_present": bool(panel_row["source_note_text_present"]),
        "contract_matched": True,
        "contract_issues": [],
        "current_candidate_action": current_row.get("candidate_action", ""),
        "current_candidate_component_owner": current_row.get("component_owner", ""),
        "current_candidate_purist_correct": current_row.get("candidate_purist_correct"),
        "h6_member": bool(current_row.get("h6_member")),
        "h6_panel_role": current_row.get("h6_panel_role", ""),
        "final_label_policy_connected": False,
        "promotion_scope": "validation_component_ablation_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _effect_class(row: Mapping[str, Any]) -> str:
    if row["target_mechanism"] == "benchmark_convention_renderer_v0":
        return "benchmark_only_rendering"
    return "clinical_boundary_projection"


def _nested_transition_counts(
    rows: Sequence[Mapping[str, Any]],
    field: str,
) -> dict[str, dict[str, int]]:
    nested: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        nested[str(row[field])][str(row["transition"])] += 1
    return {
        key: dict(sorted(counts.items()))
        for key, counts in sorted(nested.items())
    }


def _transition(
    *,
    current_label: str,
    proposed_label: str,
    gold_label: str,
    selected: bool,
) -> str:
    if not selected:
        return "not_selected"
    current_correct = _purist_correct(current_label, gold_label)
    proposed_correct = _purist_correct(proposed_label, gold_label)
    if not current_correct and proposed_correct:
        return "W_to_C"
    if current_correct and not proposed_correct:
        return "C_to_W"
    if current_correct and proposed_correct:
        return "C_to_C"
    return "W_to_W"


def _purist_correct(prediction_label: str, gold_label: str) -> bool:
    try:
        parsed_prediction = label_to_frequency_record(prediction_label)
        parsed_gold = label_to_frequency_record(gold_label)
    except ValueError:
        return False
    if parsed_prediction is None or parsed_gold is None:
        return False
    return map_purist(parsed_prediction.monthly_frequency) == map_purist(
        parsed_gold.monthly_frequency
    )


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument(
        "--current-candidate-jsonl-path",
        type=Path,
        default=DEFAULT_CURRENT_CANDIDATE_JSONL_PATH,
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_component_ablation(
        panel_jsonl_path=args.panel_jsonl_path,
        current_candidate_jsonl_path=args.current_candidate_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "row_count": summary["candidate_rows"],
                "w_to_c_rows": summary["w_to_c_rows"],
                "c_to_w_rows": summary["c_to_w_rows"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
