"""Richer structured event/projection audit for validation candidate rows."""

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
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_event_projection_audit_v0"
REPRESENTATION_VERSION = "structured_event_projection_v0"
DEFAULT_CANDIDATE_JSONL_PATH = Path(
    "experiments/gan2026_boundary_benchmark_candidate_assembly_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.md"
)


def build_projection_rows(
    candidate_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Convert shallow candidate rows into explicit event/projection rows."""

    rows = [_projection_row(row) for row in candidate_rows]
    rows.sort(key=lambda row: (row["projection_owner"], row["source_row_index"]))
    return rows


def summarize_projection_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize the richer structured event/projection validation surface."""

    selected = [row for row in rows if row["selected_for_ablation"]]
    transitions = Counter(str(row["transition"]) for row in selected)
    selected_count = len(selected)
    c_to_w_rows = transitions["C_to_W"]
    c_to_w_rate = _rate(c_to_w_rows, selected_count)
    parse_ok_exact_rows = sum(
        bool(row["parse_ok"])
        and bool(row["exact_evidence"])
        and not row["contract_issues"]
        for row in selected
    )
    parse_ok_exact_rate = _rate(parse_ok_exact_rows, selected_count)
    projection_ownership_explicit_rows = sum(
        bool(row["projection_ownership_explicit"]) for row in rows
    )
    schema_ready = projection_ownership_explicit_rows == len(rows) and all(
        not row["source_note_text_present"] for row in rows
    )
    gate_failures = []
    if selected_count < structured_candidate_contract.MIN_VALIDATION_COVERAGE:
        gate_failures.append("coverage_below_150")
    if transitions["W_to_C"] < structured_candidate_contract.MIN_W_TO_C:
        gate_failures.append("w_to_c_below_60")
    if c_to_w_rate > structured_candidate_contract.MAX_C_TO_W_RATE:
        gate_failures.append("c_to_w_above_5_percent")
    if (
        parse_ok_exact_rate
        < structured_candidate_contract.MIN_PARSE_OK_EXACT_EVIDENCE_RATE
    ):
        gate_failures.append("parse_ok_exact_evidence_below_95_percent")
    if not schema_ready:
        gate_failures.append("projection_ownership_schema_not_ready")
    return {
        "artifact_kind": "gan2026_structured_event_projection_audit_summary",
        "policy_name": POLICY_NAME,
        "representation_decision": "rich_structured_event_projection_layer",
        "representation_decision_reason": (
            "Replace the shallow typed-candidate bridge with explicit clinical "
            "event ownership and benchmark projection/rendering ownership. This "
            "audit is schema and attribution evidence only; validation gates "
            "still control any later frozen-test protocol."
        ),
        "candidate_rows": len(rows),
        "selected_prediction_bearing_rows": selected_count,
        "w_to_c_rows": transitions["W_to_C"],
        "c_to_w_rows": c_to_w_rows,
        "c_to_w_rate": c_to_w_rate,
        "transition_counts": dict(sorted(transitions.items())),
        "parse_ok_exact_evidence_rows": parse_ok_exact_rows,
        "parse_ok_exact_evidence_rate": parse_ok_exact_rate,
        "projection_ownership_explicit_rows": projection_ownership_explicit_rows,
        "schema_ready": schema_ready,
        "no_regression_case_rows": sum(bool(row["no_regression_case"]) for row in rows),
        "source_note_text_rows": sum(bool(row["source_note_text_present"]) for row in rows),
        "frozen_test_audit_ready": not gate_failures,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "gate_failures": gate_failures,
        "clinical_event_owner_counts": dict(
            sorted(Counter(str(row["clinical_event_owner"]) for row in rows).items())
        ),
        "projection_owner_counts": dict(
            sorted(Counter(str(row["projection_owner"]) for row in rows).items())
        ),
        "claim_boundary": (
            "Validation-development structured event/projection audit only. It "
            "writes no source note text, uses no locked-test row-level artifacts, "
            "and does not authorize holdout-facing use."
        ),
        "decision": (
            "structured_projection_schema_ready_for_validation_expansion"
            if schema_ready
            else "revise_structured_projection_schema"
        ),
        "recommended_next_step": (
            "Broaden the structured event generator around this projection-owner "
            "schema and carry the C->W row as a named no-regression control. Do "
            "not write a frozen test450 protocol until validation coverage, W->C, "
            "C->W, and parse/evidence gates pass."
        ),
    }


def materialize_projection_audit(
    *,
    candidate_jsonl_path: Path = DEFAULT_CANDIDATE_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    candidate_rows = load_jsonl_rows(candidate_jsonl_path)
    rows = build_projection_rows(candidate_rows)
    summary = summarize_projection_rows(rows)
    summary = {
        **summary,
        "source_candidate_artifact": str(candidate_jsonl_path),
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
        "# Gan 2026 Structured Event Projection Audit v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Representation Decision",
        "",
        str(summary["representation_decision_reason"]),
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
        f"| C->W rate | {summary['c_to_w_rate']:.4f} |",
        f"| parse-ok plus exact-evidence rate | {summary['parse_ok_exact_evidence_rate']:.4f} |",
        (
            "| projection-ownership explicit rows | "
            f"{summary['projection_ownership_explicit_rows']} |"
        ),
        f"| no-regression case rows | {summary['no_regression_case_rows']} |",
        f"| source-note-text rows | {summary['source_note_text_rows']} |",
        f"| schema ready | {summary['schema_ready']} |",
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
    lines.extend(
        [
            "",
            "## Clinical Event Owners",
            "",
            "| Owner | Rows |",
            "| --- | ---: |",
        ]
    )
    for owner, count in summary["clinical_event_owner_counts"].items():
        lines.append(f"| `{owner}` | {count} |")
    lines.extend(["", "## Projection Owners", "", "| Owner | Rows |", "| --- | ---: |"])
    for owner, count in summary["projection_owner_counts"].items():
        lines.append(f"| `{owner}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Projection audit JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source candidate JSONL: `{summary['source_candidate_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _projection_row(candidate_row: Mapping[str, Any]) -> dict[str, Any]:
    component_owner = str(candidate_row["component_owner"])
    mechanism = str(candidate_row["target_mechanism"])
    projection_owner = _projection_owner(component_owner, mechanism)
    transition = str(candidate_row["transition"])
    return {
        "artifact_kind": "gan2026_structured_event_projection_audit_row",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "source_row_index": int(candidate_row["source_row_index"]),
        "split": candidate_row["split"],
        "split_manifest": candidate_row["split_manifest"],
        "slice_id": candidate_row["slice_id"],
        "panel_role": candidate_row["panel_role"],
        "target_family": candidate_row["target_family"],
        "target_mechanism": mechanism,
        "candidate_source": "structured_event",
        "clinical_event_owner": _clinical_event_owner(component_owner, mechanism),
        "clinical_event_kind": candidate_row["event_kind"],
        "clinical_event_target": candidate_row["event_target"],
        "temporality": candidate_row["temporality"],
        "assertion_status": candidate_row["assertion_status"],
        "projection_owner": projection_owner,
        "projection_ownership_basis": mechanism,
        "projection_stage": _projection_stage(projection_owner),
        "projection_policy_id": candidate_row["benchmark_policy_id"],
        "benchmark_format_rule_id": candidate_row["benchmark_format_rule_id"],
        "clinical_final_state": candidate_row["clinical_final_state"],
        "boundary_state": candidate_row["boundary_state"],
        "current_label": candidate_row["current_label"],
        "projection_input_label": candidate_row["current_label"],
        "gan_rendered_label": candidate_row["proposed_label"],
        "proposed_label": candidate_row["proposed_label"],
        "gold_label": candidate_row["gold_label"],
        "transition": transition,
        "no_regression_case": transition == "C_to_W",
        "selected_for_ablation": bool(candidate_row["selected_for_ablation"]),
        "prediction_bearing": bool(candidate_row["prediction_bearing"]),
        "parse_ok": bool(candidate_row["parse_ok"]),
        "exact_evidence": bool(candidate_row["exact_evidence"]),
        "evidence": candidate_row["evidence"],
        "source_note_text": None,
        "source_note_text_present": bool(candidate_row["source_note_text_present"]),
        "contract_matched": bool(candidate_row["contract_matched"]),
        "contract_issues": list(candidate_row.get("contract_issues", [])),
        "projection_ownership_explicit": True,
        "final_label_policy_connected": False,
        "promotion_scope": (
            "validation_structured_event_projection_audit_no_final_label_promotion"
        ),
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _clinical_event_owner(component_owner: str, mechanism: str) -> str:
    if component_owner == "benchmark_renderer":
        return "typed_event_extractor"
    if "boundary" in mechanism:
        return "typed_boundary_classifier"
    return component_owner


def _projection_owner(component_owner: str, mechanism: str) -> str:
    if component_owner == "benchmark_renderer":
        return "benchmark_renderer"
    if "boundary" in mechanism:
        return "boundary_projection_policy"
    return "structured_event_projection_policy"


def _projection_stage(projection_owner: str) -> str:
    if projection_owner == "benchmark_renderer":
        return "benchmark_format_rendering"
    return "clinical_event_to_benchmark_label"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize the Gan 2026 structured event/projection audit."
    )
    parser.add_argument(
        "--candidate-jsonl-path",
        type=Path,
        default=DEFAULT_CANDIDATE_JSONL_PATH,
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args()
    summary = materialize_projection_audit(
        candidate_jsonl_path=args.candidate_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "schema_ready": summary["schema_ready"],
                "frozen_test_audit_ready": summary["frozen_test_audit_ready"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
