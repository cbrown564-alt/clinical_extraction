"""Validation-only candidate assembly for boundary and benchmark typed fields."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
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

POLICY_NAME = "gan2026_boundary_benchmark_candidate_assembly_v0"
DEFAULT_CONTRACT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.jsonl"
)
DEFAULT_CURRENT_CANDIDATE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_"
    "2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.md"
)


def build_candidate_rows(
    contract_rows: Sequence[Mapping[str, Any]],
    current_candidate_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Layer passed typed-field contract rows over the current validation candidate."""

    current_by_source_index = {
        int(row["source_row_index"]): row for row in current_candidate_rows
    }
    rows = []
    for contract_row in contract_rows:
        source_row_index = int(contract_row["source_row_index"])
        current_row = current_by_source_index.get(source_row_index, {})
        rows.append(_candidate_row(contract_row, current_row))
    rows.sort(key=lambda row: (row["target_mechanism"], row["source_row_index"]))
    return rows


def summarize_candidate_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize the validation-only candidate-contract bridge."""

    selected = [row for row in rows if row["selected_for_ablation"]]
    transitions = Counter(str(row["transition"]) for row in selected)
    selected_count = len(selected)
    c_to_w_rows = transitions["C_to_W"]
    c_to_w_rate = _rate(c_to_w_rows, selected_count)
    parse_ok_exact_rows = sum(
        row["parse_ok"] is True
        and row["exact_evidence"] is True
        and not row["contract_issues"]
        for row in selected
    )
    parse_ok_exact_rate = _rate(parse_ok_exact_rows, selected_count)
    final_label_policy_connected = any(
        bool(row["final_label_policy_connected"]) for row in rows
    )
    gate_failures = []
    if selected_count < structured_candidate_contract.MIN_VALIDATION_COVERAGE:
        gate_failures.append("coverage_below_150")
    if transitions["W_to_C"] < structured_candidate_contract.MIN_W_TO_C:
        gate_failures.append(structured_candidate_contract.W_TO_C_GATE_FAILURE)
    if c_to_w_rate > structured_candidate_contract.MAX_C_TO_W_RATE:
        gate_failures.append("c_to_w_above_5_percent")
    if (
        parse_ok_exact_rate
        < structured_candidate_contract.MIN_PARSE_OK_EXACT_EVIDENCE_RATE
    ):
        gate_failures.append("parse_ok_exact_evidence_below_95_percent")
    if final_label_policy_connected:
        gate_failures.append("final_label_policy_connected")

    return {
        "artifact_kind": "gan2026_boundary_benchmark_candidate_assembly_summary",
        "policy_name": POLICY_NAME,
        "architecture_decision": "typed_candidate_contract_layer",
        "architecture_decision_reason": (
            "Use the passed boundary/renderer typed fields as a shallow "
            "validation-only candidate-contract layer over the current assembled "
            "candidate. Defer a richer structured event representation until this "
            "layer shows enough coverage and no-regression signal."
        ),
        "candidate_rows": len(rows),
        "selected_prediction_bearing_rows": selected_count,
        "w_to_c_rows": transitions["W_to_C"],
        "c_to_w_rows": c_to_w_rows,
        "c_to_w_rate": c_to_w_rate,
        "transition_counts": dict(sorted(transitions.items())),
        "parse_ok_exact_evidence_rows": parse_ok_exact_rows,
        "parse_ok_exact_evidence_rate": parse_ok_exact_rate,
        "contract_matched_rows": sum(row["contract_matched"] is True for row in rows),
        "exact_evidence_rows": sum(row["exact_evidence"] is True for row in rows),
        "source_note_text_rows": sum(bool(row["source_note_text_present"]) for row in rows),
        "final_label_policy_connected": final_label_policy_connected,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "frozen_test_audit_ready": not gate_failures,
        "gate_failures": gate_failures,
        "target_mechanism_counts": dict(
            sorted(Counter(str(row["target_mechanism"]) for row in rows).items())
        ),
        "component_owner_counts": dict(
            sorted(Counter(str(row["component_owner"]) for row in rows).items())
        ),
        "slice_counts": dict(
            sorted(Counter(str(row["slice_id"]) for row in rows).items())
        ),
        "claim_boundary": (
            "Validation-development candidate assembly protocol only. It connects "
            "passed H3/H7 boundary and benchmark typed fields to candidate rows "
            "for diagnostic transition accounting, writes no source note text, "
            "and does not authorize final-label promotion or holdout use."
        ),
        "decision": (
            "candidate_contract_layer_ready_for_validation_expansion"
            if not gate_failures
            else "candidate_contract_layer_diagnostic_only"
        ),
        "recommended_next_step": (
            "Expand the validation hard/control surface before any frozen test "
            "audit. If the typed layer still stays below coverage or W->C gates, "
            "move to a richer structured event representation with explicit "
            "projection ownership."
        ),
    }


def materialize_candidate_assembly(
    *,
    contract_jsonl_path: Path = DEFAULT_CONTRACT_JSONL_PATH,
    current_candidate_jsonl_path: Path = DEFAULT_CURRENT_CANDIDATE_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    contract_rows = load_jsonl_rows(contract_jsonl_path)
    current_candidate_rows = load_jsonl_rows(current_candidate_jsonl_path)
    rows = build_candidate_rows(contract_rows, current_candidate_rows)
    summary = summarize_candidate_rows(rows)
    summary = {
        **summary,
        "source_contract_artifact": str(contract_jsonl_path),
        "source_current_candidate_artifact": str(current_candidate_jsonl_path),
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
        "# Gan 2026 Boundary/Benchmark Candidate Assembly v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Architecture Decision",
        "",
        str(summary["architecture_decision_reason"]),
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| candidate rows | {summary['candidate_rows']} |",
        (
            "| selected prediction-bearing rows | "
            f"{summary['selected_prediction_bearing_rows']} |"
        ),
        f"| W->C rows | {summary['w_to_c_rows']} |",
        f"| C->W rows | {summary['c_to_w_rows']} |",
        f"| parse-ok plus exact-evidence rate | {summary['parse_ok_exact_evidence_rate']:.4f} |",
        f"| source-note-text rows | {summary['source_note_text_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        f"| frozen test audit ready | {summary['frozen_test_audit_ready']} |",
        f"| holdout authorized | {summary['holdout_authorized']} |",
        "",
        "## Gate Failures",
        "",
    ]
    if summary["gate_failures"]:
        for failure in summary["gate_failures"]:
            lines.append(f"- `{failure}`")
    else:
        lines.append("- none")
    lines.extend(["", "## Target Mechanisms", "", "| Mechanism | Rows |", "| --- | ---: |"])
    for mechanism, count in summary["target_mechanism_counts"].items():
        lines.append(f"| `{mechanism}` | {count} |")
    lines.extend(["", "## Component Owners", "", "| Owner | Rows |", "| --- | ---: |"])
    for owner, count in summary["component_owner_counts"].items():
        lines.append(f"| `{owner}` | {count} |")
    lines.extend(["", "## Slices", "", "| Slice | Rows |", "| --- | ---: |"])
    for slice_id, count in summary["slice_counts"].items():
        lines.append(f"| `{slice_id}` | {count} |")
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
            f"- Source contract JSONL: `{summary['source_contract_artifact']}`",
            (
                "- Source current candidate JSONL: "
                f"`{summary['source_current_candidate_artifact']}`"
            ),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _candidate_row(
    contract_row: Mapping[str, Any],
    current_row: Mapping[str, Any],
) -> dict[str, Any]:
    current_label = str(current_row.get("candidate_label") or "")
    proposed_label = str(contract_row["gan_rendered_label"])
    selected = (
        bool(contract_row["contract_matched"])
        and bool(contract_row["exact_evidence"])
        and proposed_label != ""
    )
    transition = _transition(
        current_label=current_label,
        proposed_label=proposed_label,
        gold_label=str(contract_row["gold_label"]),
        selected=selected,
    )
    target_mechanism = str(contract_row["target_mechanism"])
    return {
        "artifact_kind": "gan2026_boundary_benchmark_candidate_assembly_row",
        "policy_name": POLICY_NAME,
        "architecture_decision": "typed_candidate_contract_layer",
        "candidate_version": POLICY_NAME,
        "source_row_index": int(contract_row["source_row_index"]),
        "split": contract_row["split"],
        "split_manifest": contract_row["split_manifest"],
        "slice_id": contract_row["slice_id"],
        "panel_role": contract_row["panel_role"],
        "target_family": contract_row["target_family"],
        "target_mechanism": target_mechanism,
        "component_owner": str(contract_row["component_owner"]),
        "component_ownership_basis": target_mechanism,
        "candidate_source": "typed_candidate_contract",
        "candidate_exposure": contract_row["candidate_exposure"],
        "event_kind": _event_kind(contract_row),
        "event_target": "seizure",
        "temporality": _temporality(contract_row),
        "assertion_status": _assertion_status(contract_row),
        "benchmark_policy_id": contract_row["benchmark_policy_id"],
        "benchmark_format_rule_id": contract_row["benchmark_format_rule_id"],
        "boundary_state": contract_row["boundary_state"],
        "clinical_final_state": contract_row["clinical_final_state"],
        "current_label": current_label,
        "proposed_label": proposed_label,
        "gold_label": contract_row["gold_label"],
        "transition": transition,
        "selected_for_ablation": selected,
        "prediction_bearing": selected,
        "parse_ok": True,
        "exact_evidence": bool(contract_row["exact_evidence"]),
        "evidence": contract_row["evidence"],
        "source_note_text": None,
        "source_note_text_present": bool(contract_row["source_note_text_present"]),
        "contract_matched": bool(contract_row["contract_matched"]),
        "contract_issues": list(contract_row.get("contract_issues", [])),
        "current_candidate_component_owner": current_row.get("component_owner", ""),
        "final_label_policy_connected": False,
        "promotion_scope": "validation_candidate_contract_layer_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _event_kind(row: Mapping[str, Any]) -> str:
    rule_id = str(row["benchmark_format_rule_id"])
    boundary_state = str(row["boundary_state"])
    if "cluster" in rule_id:
        return "cluster_frequency"
    if boundary_state == "asserted_seizure_free_interval":
        return "seizure_free"
    if boundary_state == "last_event_only":
        return "last_event_only"
    if str(row["gan_rendered_label"]) == "unknown":
        return "unknown_frequency"
    return "frequency_rate"


def _temporality(row: Mapping[str, Any]) -> str:
    boundary_state = str(row["boundary_state"])
    if boundary_state == "last_event_only":
        return "historical"
    if boundary_state in {"conditional_or_trigger_only", "not_applicable"}:
        return "unclear"
    return "current"


def _assertion_status(row: Mapping[str, Any]) -> str:
    boundary_state = str(row["boundary_state"])
    if boundary_state in {"conditional_or_trigger_only", "last_event_only"}:
        return "uncertain"
    if boundary_state == "non_epileptic_current_events":
        return "negated"
    return "asserted"


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the Gan 2026 boundary/benchmark validation-only "
            "candidate assembly artifact."
        )
    )
    parser.add_argument(
        "--contract-jsonl-path",
        type=Path,
        default=DEFAULT_CONTRACT_JSONL_PATH,
    )
    parser.add_argument(
        "--current-candidate-jsonl-path",
        type=Path,
        default=DEFAULT_CURRENT_CANDIDATE_JSONL_PATH,
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument(
        "--output-report-path",
        type=Path,
        default=DEFAULT_OUTPUT_REPORT_PATH,
    )
    args = parser.parse_args()
    summary = materialize_candidate_assembly(
        contract_jsonl_path=args.contract_jsonl_path,
        current_candidate_jsonl_path=args.current_candidate_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
