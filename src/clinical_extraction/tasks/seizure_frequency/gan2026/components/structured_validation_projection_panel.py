"""Validation projection-owner panel for structured event expansion."""

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

POLICY_NAME = "gan2026_structured_validation_projection_panel_v0"
REPRESENTATION_VERSION = "structured_event_projection_v0"
DEFAULT_SEED_PANEL_JSONL_PATH = Path(
    "experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.jsonl"
)
DEFAULT_PROJECTION_AUDIT_JSONL_PATH = Path(
    "experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.md"
)


def build_validation_projection_rows(
    seed_panel_rows: Sequence[Mapping[str, Any]],
    projection_audit_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build validation hard/control rows with explicit projection ownership."""

    rows = [_seed_projection_row(row) for row in seed_panel_rows]
    rows.extend(
        _no_regression_row(row)
        for row in projection_audit_rows
        if row["no_regression_case"]
    )
    rows.sort(key=lambda row: (row["panel_source"], row["panel_role"], row["source_row_index"]))
    return rows


def summarize_validation_projection_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize validation projection-owner panel readiness."""

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
    projection_ownership_explicit_rows = sum(
        bool(row["projection_ownership_explicit"]) for row in rows
    )
    source_note_text_rows = sum(bool(row["source_note_text_present"]) for row in rows)
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
    if projection_ownership_explicit_rows != len(rows):
        gate_failures.append("projection_ownership_not_explicit")
    if source_note_text_rows:
        gate_failures.append("source_note_text_present")
    return {
        "artifact_kind": "gan2026_structured_validation_projection_panel_summary",
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
        "transition_counts": dict(sorted(transitions.items())),
        "parse_ok_exact_evidence_rows": parse_ok_exact_rows,
        "parse_ok_exact_evidence_rate": parse_ok_exact_rate,
        "projection_ownership_explicit_rows": projection_ownership_explicit_rows,
        "source_note_text_rows": source_note_text_rows,
        "frozen_test_audit_ready": not gate_failures,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "gate_failures": gate_failures,
        "panel_source_counts": dict(
            sorted(Counter(str(row["panel_source"]) for row in rows).items())
        ),
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
            "Validation-development projection-owner panel only. It combines saved "
            "validation seed hard/control rows with the named boundary no-regression "
            "case, writes no note text, uses no locked-test row-level artifacts, and "
            "does not authorize holdout-facing use."
        ),
        "decision": (
            "validation_projection_panel_ready_for_extractor_design"
            if rows
            and projection_ownership_explicit_rows == len(rows)
            and source_note_text_rows == 0
            else "revise_validation_projection_panel"
        ),
        "recommended_next_step": (
            "Implement the validation projection-owner extractor smoke over this "
            "panel. Keep the boundary C->W row as a no-regression control and do "
            "not write a frozen test450 protocol until validation gates pass."
        ),
    }


def materialize_validation_projection_panel(
    *,
    seed_panel_jsonl_path: Path = DEFAULT_SEED_PANEL_JSONL_PATH,
    projection_audit_jsonl_path: Path = DEFAULT_PROJECTION_AUDIT_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    seed_rows = load_jsonl_rows(seed_panel_jsonl_path)
    projection_audit_rows = load_jsonl_rows(projection_audit_jsonl_path)
    rows = build_validation_projection_rows(seed_rows, projection_audit_rows)
    summary = summarize_validation_projection_rows(rows)
    summary = {
        **summary,
        "source_seed_panel_artifact": str(seed_panel_jsonl_path),
        "source_projection_audit_artifact": str(projection_audit_jsonl_path),
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
        "# Gan 2026 Structured Validation Projection Panel v0",
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
        f"| no-regression case rows | {summary['no_regression_case_rows']} |",
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
        f"| source-note-text rows | {summary['source_note_text_rows']} |",
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
            f"- Panel JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source seed panel JSONL: `{summary['source_seed_panel_artifact']}`",
            (
                "- Source projection audit JSONL: "
                f"`{summary['source_projection_audit_artifact']}`"
            ),
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _seed_projection_row(row: Mapping[str, Any]) -> dict[str, Any]:
    seed_family = str(row["seed_family"])
    ownership = _ownership_for_seed_family(seed_family)
    selected = str(row["expected_generator_action"]) == "emit_candidate"
    proposed_label = str(row.get("expected_candidate_label") or "")
    return {
        "artifact_kind": "gan2026_structured_validation_projection_panel_row",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "panel_source": "structured_seed_validation_panel_v0",
        "source_row_index": int(row["source_row_index"]),
        "split": row["split"],
        "split_manifest": row["split_manifest"],
        "panel_role": row["panel_role"],
        "seed_family": seed_family,
        "generator_action": row["expected_generator_action"],
        "candidate_source": "structured_event" if selected else None,
        "clinical_event_owner": ownership["clinical_event_owner"],
        "clinical_event_kind": ownership["clinical_event_kind"],
        "clinical_event_target": "seizure",
        "temporality": ownership["temporality"],
        "assertion_status": ownership["assertion_status"],
        "projection_owner": ownership["projection_owner"],
        "projection_ownership_basis": seed_family,
        "projection_stage": "clinical_event_to_benchmark_label",
        "projection_policy_id": ownership["projection_policy_id"],
        "benchmark_format_rule_id": ownership["benchmark_format_rule_id"],
        "current_label": row["current_label"],
        "projection_input_label": row["current_label"],
        "gan_rendered_label": proposed_label if selected else None,
        "proposed_label": proposed_label if selected else "",
        "gold_label": row["gold_label"],
        "unsafe_candidate_label": row.get("unsafe_candidate_label"),
        "transition": "W_to_C" if selected else "not_selected",
        "no_regression_case": False,
        "selected_for_ablation": selected,
        "prediction_bearing": selected,
        "parse_ok": True,
        "exact_evidence": bool(row["expected_evidence_substring"]),
        "evidence": row["expected_evidence_substring"],
        "source_note_text": None,
        "source_note_text_present": row.get("source_note_text") is not None,
        "contract_matched": True,
        "contract_issues": [],
        "projection_ownership_explicit": True,
        "final_label_policy_connected": False,
        "promotion_scope": "validation_projection_panel_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _no_regression_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        **dict(row),
        "artifact_kind": "gan2026_structured_validation_projection_panel_row",
        "policy_name": POLICY_NAME,
        "panel_source": "structured_event_projection_audit_v0",
        "panel_role": "no_regression",
        "generator_action": "no_regression_control",
        "seed_family": None,
        "promotion_scope": "validation_projection_panel_no_final_label_promotion",
    }


def _ownership_for_seed_family(seed_family: str) -> dict[str, str]:
    if seed_family == "seizure_free_to_unknown":
        return {
            "clinical_event_owner": "typed_boundary_classifier",
            "clinical_event_kind": "unknown_frequency",
            "temporality": "unclear",
            "assertion_status": "uncertain",
            "projection_owner": "boundary_projection_policy",
            "projection_policy_id": "gan2026_boundary_projection_policy_v0",
            "benchmark_format_rule_id": "none_boundary_state_only",
        }
    if seed_family == "yearly_to_daily":
        return {
            "clinical_event_owner": "typed_event_extractor",
            "clinical_event_kind": "frequency_rate",
            "temporality": "current",
            "assertion_status": "asserted",
            "projection_owner": "rate_projection_policy",
            "projection_policy_id": "gan2026_rate_projection_policy_v0",
            "benchmark_format_rule_id": "none_rate_projection_only",
        }
    if seed_family == "cluster_completion":
        return {
            "clinical_event_owner": "typed_event_extractor",
            "clinical_event_kind": "cluster_frequency",
            "temporality": "current",
            "assertion_status": "asserted",
            "projection_owner": "cluster_projection_policy",
            "projection_policy_id": "gan2026_cluster_projection_policy_v0",
            "benchmark_format_rule_id": "gan_cluster_completion",
        }
    return {
        "clinical_event_owner": "typed_event_extractor",
        "clinical_event_kind": "frequency_rate",
        "temporality": "unclear",
        "assertion_status": "uncertain",
        "projection_owner": "structured_event_projection_policy",
        "projection_policy_id": "gan2026_structured_event_projection_policy_v0",
        "benchmark_format_rule_id": "none",
    }


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize the validation projection-owner panel."
    )
    parser.add_argument(
        "--seed-panel-jsonl-path",
        type=Path,
        default=DEFAULT_SEED_PANEL_JSONL_PATH,
    )
    parser.add_argument(
        "--projection-audit-jsonl-path",
        type=Path,
        default=DEFAULT_PROJECTION_AUDIT_JSONL_PATH,
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args()
    summary = materialize_validation_projection_panel(
        seed_panel_jsonl_path=args.seed_panel_jsonl_path,
        projection_audit_jsonl_path=args.projection_audit_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "frozen_test_audit_ready": summary["frozen_test_audit_ready"],
                "row_count": summary["row_count"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
