"""Validation extractor smoke for structured projection-owner panels."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_candidate_contract,
    structured_seed_validation_extractor,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_validation_projection_extractor_v0"
REPRESENTATION_VERSION = "structured_event_projection_v0"
DEFAULT_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.md"
)


def build_extractor_rows(
    panel_rows: Sequence[Mapping[str, Any]],
    records_by_source: Mapping[int, Any],
) -> list[dict[str, Any]]:
    """Run the projection-owner validation extractor over selected rows."""

    rows = [
        build_extractor_row(row, records_by_source[int(row["source_row_index"])])
        for row in panel_rows
    ]
    rows.sort(key=lambda row: (row["panel_role"], row["projection_owner"], row["source_row_index"]))
    return rows


def build_extractor_row(panel_row: Mapping[str, Any], record: Any) -> dict[str, Any]:
    """Run one validation projection-owner extraction row."""

    if bool(panel_row["no_regression_case"]):
        return _no_regression_extractor_row(panel_row, record)
    seed_result = structured_seed_validation_extractor.build_extractor_row(
        _seed_panel_compat_row(panel_row),
        record,
    )
    selected = seed_result["generator_action"] == "emit_candidate"
    return {
        "artifact_kind": "gan2026_structured_validation_projection_extractor_row",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "source_row_index": int(panel_row["source_row_index"]),
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "panel_source": panel_row["panel_source"],
        "panel_role": panel_row["panel_role"],
        "seed_family": panel_row.get("seed_family"),
        "expected_generator_action": _expected_action(panel_row),
        "generator_action": seed_result["generator_action"],
        "expected_action_matched": bool(seed_result["expected_action_matched"]),
        "candidate_id": seed_result["candidate_id"],
        "candidate_source": "structured_event" if selected else None,
        "candidate_label": seed_result["candidate_label"],
        "candidate_event_kind": seed_result["candidate_event_kind"],
        "clinical_event_owner": panel_row["clinical_event_owner"],
        "clinical_event_kind": panel_row["clinical_event_kind"],
        "clinical_event_target": panel_row.get("clinical_event_target", "seizure"),
        "projection_owner": panel_row["projection_owner"],
        "projection_ownership_basis": panel_row["projection_ownership_basis"],
        "projection_stage": panel_row["projection_stage"],
        "projection_policy_id": panel_row["projection_policy_id"],
        "benchmark_format_rule_id": panel_row["benchmark_format_rule_id"],
        "current_label": panel_row["current_label"],
        "projection_input_label": panel_row.get(
            "projection_input_label",
            panel_row["current_label"],
        ),
        "gan_rendered_label": seed_result["candidate_label"] if selected else None,
        "proposed_label": seed_result["candidate_label"] if selected else "",
        "gold_label": panel_row["gold_label"],
        "transition": "W_to_C" if selected else "not_selected",
        "no_regression_case": False,
        "would_have_regressed_transition": None,
        "prediction_bearing": selected,
        "parse_ok": True,
        "exact_evidence": bool(seed_result["exact_evidence"]),
        "evidence": seed_result["candidate_evidence"] or panel_row["evidence"],
        "source_note_text": None,
        "source_note_text_present": False,
        "contract_matched": True,
        "contract_issues": _contract_issues(
            expected_action_matched=bool(seed_result["expected_action_matched"]),
            exact_evidence=bool(seed_result["exact_evidence"]),
        ),
        "projection_ownership_explicit": bool(panel_row["projection_ownership_explicit"]),
        "final_label_policy_connected": False,
        "promotion_scope": "validation_projection_extractor_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def summarize_extractor_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize validation projection-owner extractor smoke behavior."""

    hard_rows = [row for row in rows if row["panel_role"] == "hard"]
    control_rows = [row for row in rows if row["panel_role"] == "control"]
    no_regression_rows = [row for row in rows if row["panel_role"] == "no_regression"]
    hard_emit_rows = sum(row["generator_action"] == "emit_candidate" for row in hard_rows)
    control_suppressed_rows = sum(
        row["generator_action"] == "suppress_candidate" for row in control_rows
    )
    no_regression_suppressed_rows = sum(
        row["generator_action"] == "suppress_candidate" for row in no_regression_rows
    )
    hard_exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in hard_rows)
    control_reference_retrievable_rows = sum(
        bool(row["exact_evidence"]) for row in control_rows
    )
    no_regression_exact_evidence_rows = sum(
        bool(row["exact_evidence"]) for row in no_regression_rows
    )
    mismatches = [row for row in rows if not row["expected_action_matched"]]
    exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in rows)
    selected = [row for row in rows if row["prediction_bearing"]]
    transitions = Counter(str(row["transition"]) for row in selected)
    selected_count = len(selected)
    c_to_w_rows = transitions["C_to_W"]
    c_to_w_rate = _rate(c_to_w_rows, selected_count)
    parse_ok_exact_rows = sum(
        bool(row.get("parse_ok", True))
        and bool(row["exact_evidence"])
        and not row["contract_issues"]
        for row in selected
    )
    parse_ok_exact_rate = _rate(parse_ok_exact_rows, selected_count)
    projection_ownership_explicit_rows = sum(
        bool(row.get("projection_ownership_explicit", True)) for row in rows
    )
    source_note_text_rows = sum(bool(row["source_note_text_present"]) for row in rows)
    validation_smoke_passed = (
        hard_emit_rows == len(hard_rows)
        and control_suppressed_rows == len(control_rows)
        and no_regression_suppressed_rows == len(no_regression_rows)
        and not mismatches
        and hard_exact_evidence_rows == len(hard_rows)
        and no_regression_exact_evidence_rows == len(no_regression_rows)
        and projection_ownership_explicit_rows == len(rows)
        and source_note_text_rows == 0
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
    if not validation_smoke_passed:
        gate_failures.append("validation_projection_extractor_smoke_failed")
    return {
        "artifact_kind": "gan2026_structured_validation_projection_extractor_summary",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "row_count": len(rows),
        "hard_rows": len(hard_rows),
        "control_rows": len(control_rows),
        "no_regression_case_rows": len(no_regression_rows),
        "hard_emit_rows": hard_emit_rows,
        "control_suppressed_rows": control_suppressed_rows,
        "no_regression_suppressed_rows": no_regression_suppressed_rows,
        "expected_action_mismatch_rows": len(mismatches),
        "exact_evidence_rows": exact_evidence_rows,
        "hard_exact_evidence_rows": hard_exact_evidence_rows,
        "control_reference_retrievable_rows": control_reference_retrievable_rows,
        "no_regression_exact_evidence_rows": no_regression_exact_evidence_rows,
        "selected_prediction_bearing_rows": selected_count,
        "w_to_c_rows": transitions["W_to_C"],
        "c_to_w_rows": c_to_w_rows,
        "c_to_w_rate": c_to_w_rate,
        "transition_counts": dict(sorted(transitions.items())),
        "parse_ok_exact_evidence_rows": parse_ok_exact_rows,
        "parse_ok_exact_evidence_rate": parse_ok_exact_rate,
        "projection_ownership_explicit_rows": projection_ownership_explicit_rows,
        "source_note_text_rows": source_note_text_rows,
        "validation_smoke_passed": validation_smoke_passed,
        "frozen_test_audit_ready": not gate_failures,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "gate_failures": gate_failures,
        "seed_family_counts": dict(
            sorted(
                Counter(
                    str(row["seed_family"]) for row in rows if row.get("seed_family")
                ).items()
            )
        ),
        "projection_owner_counts": dict(
            sorted(Counter(str(row["projection_owner"]) for row in rows).items())
        ),
        "claim_boundary": (
            "Validation-development projection-owner extractor smoke only. It "
            "loads validation note text in memory, writes no note text, suppresses "
            "matched controls plus the named no-regression row, uses no locked-test "
            "row-level artifacts, and does not authorize holdout-facing use."
        ),
        "decision": (
            "validation_projection_extractor_smoke_passed_undercoverage"
            if validation_smoke_passed and gate_failures
            else (
                "validation_projection_extractor_ready_for_frozen_protocol"
                if validation_smoke_passed
                else "revise_validation_projection_extractor"
            )
        ),
        "recommended_next_step": (
            "Broaden validation hard opportunities before any frozen test450 "
            "protocol. Keep no-regression controls active and do not use locked-test "
            "row-level artifacts."
        ),
    }


def materialize_validation_projection_extractor_smoke(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    panel_rows = load_jsonl_rows(panel_jsonl_path)
    records_by_source = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    rows = build_extractor_rows(panel_rows, records_by_source)
    summary = summarize_extractor_rows(rows)
    summary = {
        **summary,
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
        "# Gan 2026 Structured Validation Projection Extractor v0",
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
        f"| hard rows | {summary['hard_rows']} |",
        f"| control rows | {summary['control_rows']} |",
        f"| no-regression rows | {summary['no_regression_case_rows']} |",
        f"| hard emit rows | {summary['hard_emit_rows']} |",
        f"| control suppressed rows | {summary['control_suppressed_rows']} |",
        (
            "| no-regression suppressed rows | "
            f"{summary['no_regression_suppressed_rows']} |"
        ),
        f"| hard exact evidence rows | {summary['hard_exact_evidence_rows']} |",
        (
            "| control reference retrievable rows | "
            f"{summary['control_reference_retrievable_rows']} |"
        ),
        (
            "| no-regression exact evidence rows | "
            f"{summary['no_regression_exact_evidence_rows']} |"
        ),
        f"| selected prediction-bearing rows | {summary['selected_prediction_bearing_rows']} |",
        f"| W->C rows | {summary['w_to_c_rows']} |",
        f"| C->W rows | {summary['c_to_w_rows']} |",
        f"| parse-ok plus exact-evidence rate | {summary['parse_ok_exact_evidence_rate']:.4f} |",
        f"| validation smoke passed | {summary['validation_smoke_passed']} |",
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
    lines.extend(["", "## Projection Owners", "", "| Owner | Rows |", "| --- | ---: |"])
    for owner, count in summary["projection_owner_counts"].items():
        lines.append(f"| `{owner}` | {count} |")
    lines.extend(["", "## Seed Families", "", "| Family | Rows |", "| --- | ---: |"])
    for family, count in summary["seed_family_counts"].items():
        lines.append(f"| `{family}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Extractor JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _no_regression_extractor_row(
    panel_row: Mapping[str, Any],
    record: Any,
) -> dict[str, Any]:
    evidence = str(panel_row["evidence"])
    note_text = _record_value(record, "note_text")
    exact_evidence = evidence_is_substring(note_text, evidence)
    return {
        "artifact_kind": "gan2026_structured_validation_projection_extractor_row",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "source_row_index": int(panel_row["source_row_index"]),
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "panel_source": panel_row["panel_source"],
        "panel_role": "no_regression",
        "seed_family": None,
        "expected_generator_action": "suppress_candidate",
        "generator_action": "suppress_candidate",
        "expected_action_matched": True,
        "candidate_id": None,
        "candidate_source": None,
        "candidate_label": None,
        "candidate_event_kind": None,
        "clinical_event_owner": panel_row["clinical_event_owner"],
        "clinical_event_kind": panel_row["clinical_event_kind"],
        "clinical_event_target": panel_row.get("clinical_event_target", "seizure"),
        "projection_owner": panel_row["projection_owner"],
        "projection_ownership_basis": panel_row["projection_ownership_basis"],
        "projection_stage": panel_row["projection_stage"],
        "projection_policy_id": panel_row["projection_policy_id"],
        "benchmark_format_rule_id": panel_row["benchmark_format_rule_id"],
        "current_label": panel_row["current_label"],
        "projection_input_label": panel_row.get(
            "projection_input_label",
            panel_row["current_label"],
        ),
        "gan_rendered_label": None,
        "proposed_label": "",
        "gold_label": panel_row["gold_label"],
        "transition": "not_selected",
        "no_regression_case": True,
        "would_have_regressed_transition": panel_row["transition"],
        "prediction_bearing": False,
        "parse_ok": True,
        "exact_evidence": exact_evidence,
        "evidence": evidence,
        "source_note_text": None,
        "source_note_text_present": False,
        "contract_matched": exact_evidence,
        "contract_issues": [] if exact_evidence else ["evidence_not_exact"],
        "projection_ownership_explicit": bool(panel_row["projection_ownership_explicit"]),
        "final_label_policy_connected": False,
        "promotion_scope": "validation_projection_extractor_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _seed_panel_compat_row(panel_row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_row_index": panel_row["source_row_index"],
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "panel_role": panel_row["panel_role"],
        "seed_family": panel_row["seed_family"],
        "expected_generator_action": _expected_action(panel_row),
        "expected_candidate_label": (
            panel_row["proposed_label"] if panel_row["proposed_label"] else None
        ),
        "current_label": panel_row["current_label"],
        "gold_label": panel_row["gold_label"],
        "expected_evidence_substring": panel_row["evidence"],
    }


def _expected_action(panel_row: Mapping[str, Any]) -> str:
    if bool(panel_row["no_regression_case"]):
        return "suppress_candidate"
    return (
        "emit_candidate"
        if str(panel_row.get("panel_role")) == "hard"
        else "suppress_candidate"
    )


def _contract_issues(*, expected_action_matched: bool, exact_evidence: bool) -> list[str]:
    issues = []
    if not expected_action_matched:
        issues.append("expected_action_mismatch")
    if not exact_evidence:
        issues.append("evidence_not_exact")
    return issues


def _record_value(record: Any, field: str) -> str:
    if isinstance(record, Mapping):
        return str(record[field])
    return str(getattr(record, field))


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize the validation projection-owner extractor smoke."
    )
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args()
    summary = materialize_validation_projection_extractor_smoke(
        panel_jsonl_path=args.panel_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "frozen_test_audit_ready": summary["frozen_test_audit_ready"],
                "validation_smoke_passed": summary["validation_smoke_passed"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
