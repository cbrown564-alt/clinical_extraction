"""Mine broad validation hard opportunities for structured projection mechanisms."""

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
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_structured_validation_hard_opportunity_miner_v0"
REPRESENTATION_VERSION = "structured_event_projection_v0"
DEFAULT_CURRENT_CANDIDATE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_"
    "2026-06-05.jsonl"
)
DEFAULT_NO_REGRESSION_JSONL_PATH = Path(
    "experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.md"
)


def build_opportunity_rows(
    current_candidate_rows: Sequence[Mapping[str, Any]],
    records_by_source: Mapping[int, Any],
    *,
    no_regression_rows: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Build a broad validation-only opportunity panel from residual misses."""

    hard_rows = [
        _hard_row(row, records_by_source[int(row["source_row_index"])])
        for row in current_candidate_rows
        if _is_residual_miss(row)
    ]
    hard_family_counts = Counter(str(row["target_family"]) for row in hard_rows)
    control_rows = _matched_control_rows(
        current_candidate_rows,
        records_by_source,
        hard_family_counts,
    )
    regression_rows = [
        _no_regression_row(row) for row in no_regression_rows if row.get("no_regression_case")
    ]
    rows = hard_rows + control_rows + regression_rows
    rows.sort(
        key=lambda row: (
            row["panel_role"],
            row.get("target_family", "no_regression"),
            row["source_row_index"],
        )
    )
    return rows


def summarize_opportunity_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize opportunity miner coverage and gate reachability."""

    selected = [row for row in rows if row["prediction_bearing"]]
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
    return {
        "artifact_kind": "gan2026_structured_validation_hard_opportunity_miner_summary",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "row_count": len(rows),
        "hard_rows": sum(row["panel_role"] == "hard" for row in rows),
        "control_rows": sum(row["panel_role"] == "control" for row in rows),
        "no_regression_case_rows": sum(bool(row["no_regression_case"]) for row in rows),
        "selected_prediction_bearing_rows": selected_count,
        "w_to_c_rows": transitions["W_to_C"],
        "c_to_w_rows": c_to_w_rows,
        "c_to_w_rate": c_to_w_rate,
        "parse_ok_exact_evidence_rows": parse_ok_exact_rows,
        "parse_ok_exact_evidence_rate": parse_ok_exact_rate,
        "exact_evidence_rows": sum(bool(row["exact_evidence"]) for row in rows),
        "projection_ownership_explicit_rows": sum(
            bool(row["projection_ownership_explicit"]) for row in rows
        ),
        "source_note_text_rows": sum(bool(row["source_note_text_present"]) for row in rows),
        "target_family_counts": dict(
            sorted(Counter(str(row.get("target_family", "unknown")) for row in rows).items())
        ),
        "projection_owner_counts": dict(
            sorted(Counter(str(row["projection_owner"]) for row in rows).items())
        ),
        "transition_counts": dict(sorted(transitions.items())),
        "w_to_c_gate_reachable_on_current_surface": (
            transitions["W_to_C"] >= structured_candidate_contract.MIN_W_TO_C
        ),
        "frozen_test_audit_ready": not gate_failures,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "gate_failures": gate_failures,
        "claim_boundary": (
            "Validation-development hard-opportunity miner only. It uses validation "
            "gold labels to define development opportunities, writes no note text, "
            "uses no locked-test row-level artifacts, and does not authorize "
            "holdout-facing use."
        ),
        "decision": (
            "validation_hard_opportunity_gate_reachable"
            if not gate_failures
            else "validation_hard_opportunity_surface_under_gate"
        ),
        "recommended_next_step": (
            "The current validation assembly does not expose enough residual misses "
            "to satisfy the 60 W->C gate if this surface remains fixed. Either lower "
            "the gate for validation-development diagnostics or change the base "
            "surface/objective before writing any frozen test protocol."
        ),
    }


def materialize_hard_opportunity_miner(
    *,
    current_candidate_jsonl_path: Path = DEFAULT_CURRENT_CANDIDATE_JSONL_PATH,
    no_regression_jsonl_path: Path = DEFAULT_NO_REGRESSION_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    current_rows = load_jsonl_rows(current_candidate_jsonl_path)
    no_regression_rows = load_jsonl_rows(no_regression_jsonl_path)
    records_by_source = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    rows = build_opportunity_rows(
        current_rows,
        records_by_source,
        no_regression_rows=no_regression_rows,
    )
    summary = summarize_opportunity_rows(rows)
    summary = {
        **summary,
        "source_current_candidate_artifact": str(current_candidate_jsonl_path),
        "source_no_regression_artifact": str(no_regression_jsonl_path),
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
        "# Gan 2026 Structured Validation Hard Opportunity Miner v0",
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
        f"| selected prediction-bearing rows | {summary['selected_prediction_bearing_rows']} |",
        f"| W->C rows | {summary['w_to_c_rows']} |",
        f"| C->W rows | {summary['c_to_w_rows']} |",
        f"| parse-ok plus exact-evidence rate | {summary['parse_ok_exact_evidence_rate']:.4f} |",
        (
            "| W->C gate reachable on current surface | "
            f"{summary['w_to_c_gate_reachable_on_current_surface']} |"
        ),
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
    lines.extend(["", "## Target Families", "", "| Family | Rows |", "| --- | ---: |"])
    for family, count in summary["target_family_counts"].items():
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
            f"- Miner JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            (
                "- Source current candidate JSONL: "
                f"`{summary['source_current_candidate_artifact']}`"
            ),
            f"- Source no-regression JSONL: `{summary['source_no_regression_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _hard_row(row: Mapping[str, Any], record: Any) -> dict[str, Any]:
    return _base_row(
        row=row,
        record=record,
        panel_role="hard",
        proposed_label=str(row["gold_label"]),
        prediction_bearing=True,
        transition="W_to_C",
    )


def _matched_control_rows(
    current_candidate_rows: Sequence[Mapping[str, Any]],
    records_by_source: Mapping[int, Any],
    hard_family_counts: Counter[str],
) -> list[dict[str, Any]]:
    controls = []
    control_counts: Counter[str] = Counter()
    for row in current_candidate_rows:
        if not bool(row.get("candidate_purist_correct")):
            continue
        family = _target_family(str(row.get("gold_label") or ""))
        if control_counts[family] >= max(hard_family_counts[family], 1):
            continue
        controls.append(
            _base_row(
                row=row,
                record=records_by_source[int(row["source_row_index"])],
                panel_role="control",
                proposed_label="",
                prediction_bearing=False,
                transition="not_selected",
            )
        )
        control_counts[family] += 1
    return controls


def _base_row(
    *,
    row: Mapping[str, Any],
    record: Any,
    panel_role: str,
    proposed_label: str,
    prediction_bearing: bool,
    transition: str,
) -> dict[str, Any]:
    source_row_index = int(row["source_row_index"])
    gold_label = str(row.get("gold_label") or _record_value(record, "gold_label"))
    current_label = str(row.get("candidate_label") or "")
    evidence = str(_record_value(record, "gold_reference"))
    target_family = _target_family(gold_label)
    ownership = _ownership_for_family(target_family)
    exact_evidence = evidence_is_substring(str(_record_value(record, "note_text")), evidence)
    return {
        "artifact_kind": "gan2026_structured_validation_hard_opportunity_miner_row",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": row.get("split_manifest") or "gan2026_split_v1",
        "panel_role": panel_role,
        "target_family": target_family,
        "candidate_source": "structured_event" if prediction_bearing else None,
        "clinical_event_owner": ownership["clinical_event_owner"],
        "clinical_event_kind": ownership["clinical_event_kind"],
        "clinical_event_target": "seizure",
        "projection_owner": ownership["projection_owner"],
        "projection_ownership_basis": target_family,
        "projection_stage": "clinical_event_to_benchmark_label",
        "projection_policy_id": ownership["projection_policy_id"],
        "benchmark_format_rule_id": ownership["benchmark_format_rule_id"],
        "current_label": current_label,
        "projection_input_label": current_label,
        "gan_rendered_label": proposed_label if prediction_bearing else None,
        "proposed_label": proposed_label,
        "gold_label": gold_label,
        "transition": transition,
        "no_regression_case": False,
        "prediction_bearing": prediction_bearing,
        "parse_ok": True,
        "exact_evidence": exact_evidence,
        "evidence": evidence,
        "source_note_text": None,
        "source_note_text_present": False,
        "contract_matched": exact_evidence,
        "contract_issues": [] if exact_evidence else ["evidence_not_exact"],
        "projection_ownership_explicit": True,
        "final_label_policy_connected": False,
        "promotion_scope": "validation_hard_opportunity_panel_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _no_regression_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **dict(row),
        "artifact_kind": "gan2026_structured_validation_hard_opportunity_miner_row",
        "policy_name": POLICY_NAME,
        "panel_role": "no_regression",
        "prediction_bearing": False,
        "transition": "not_selected",
        "promotion_scope": "validation_hard_opportunity_panel_no_final_label_promotion",
    }


def _is_residual_miss(row: Mapping[str, Any]) -> bool:
    return str(row.get("candidate_action")) == "predict" and not bool(
        row.get("candidate_purist_correct")
    )


def _target_family(label: str) -> str:
    text = label.lower()
    if text == "unknown":
        return "unknown_frequency"
    if text == "no seizure frequency reference":
        return "no_reference"
    if text.startswith("seizure free"):
        return "seizure_free"
    if "cluster" in text:
        return "cluster_frequency"
    if "per day" in text:
        return "daily_frequency"
    if "per week" in text:
        return "weekly_frequency"
    if "per month" in text:
        return "monthly_frequency"
    if "per year" in text:
        return "yearly_frequency"
    return "other_frequency"


def _ownership_for_family(target_family: str) -> dict[str, str]:
    if target_family in {"unknown_frequency", "seizure_free", "no_reference"}:
        return {
            "clinical_event_owner": "typed_boundary_classifier",
            "clinical_event_kind": target_family,
            "projection_owner": "boundary_projection_policy",
            "projection_policy_id": "gan2026_boundary_projection_policy_v0",
            "benchmark_format_rule_id": "none_boundary_state_only",
        }
    if target_family == "cluster_frequency":
        return {
            "clinical_event_owner": "typed_event_extractor",
            "clinical_event_kind": "cluster_frequency",
            "projection_owner": "cluster_projection_policy",
            "projection_policy_id": "gan2026_cluster_projection_policy_v0",
            "benchmark_format_rule_id": "gan_cluster_completion",
        }
    return {
        "clinical_event_owner": "typed_event_extractor",
        "clinical_event_kind": "frequency_rate",
        "projection_owner": "rate_projection_policy",
        "projection_policy_id": "gan2026_rate_projection_policy_v0",
        "benchmark_format_rule_id": "none_rate_projection_only",
    }


def _record_value(record: Any, field: str) -> str:
    if isinstance(record, Mapping):
        return str(record[field])
    return str(getattr(record, field))


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize broad validation hard-opportunity miner."
    )
    parser.add_argument(
        "--current-candidate-jsonl-path",
        type=Path,
        default=DEFAULT_CURRENT_CANDIDATE_JSONL_PATH,
    )
    parser.add_argument(
        "--no-regression-jsonl-path",
        type=Path,
        default=DEFAULT_NO_REGRESSION_JSONL_PATH,
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args()
    summary = materialize_hard_opportunity_miner(
        current_candidate_jsonl_path=args.current_candidate_jsonl_path,
        no_regression_jsonl_path=args.no_regression_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "w_to_c_rows": summary["w_to_c_rows"],
                "w_to_c_gate_reachable_on_current_surface": summary[
                    "w_to_c_gate_reachable_on_current_surface"
                ],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
