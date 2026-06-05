"""Validation hard/control port of synthetic structured projection mechanisms."""

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

POLICY_NAME = "gan2026_structured_validation_projection_port_panel_v0"
REPRESENTATION_VERSION = "structured_event_projection_v0"
DEFAULT_MINER_JSONL_PATH = Path(
    "experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_structured_validation_projection_port_panel_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_structured_validation_projection_port_panel_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_structured_validation_projection_port_panel_v0_2026-06-05.md"
)


def build_validation_projection_port_rows(
    miner_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build an exact-evidence validation panel for the synthetic port."""

    hard_rows = [
        _ported_row(row)
        for row in miner_rows
        if row["panel_role"] == "hard" and _has_clean_exact_evidence(row)
    ]
    hard_family_counts = Counter(str(row["target_family"]) for row in hard_rows)
    control_rows = _matched_exact_control_rows(miner_rows, hard_family_counts)
    no_regression_rows = [
        _ported_row(row)
        for row in miner_rows
        if row["panel_role"] == "no_regression" and _has_clean_exact_evidence(row)
    ]
    rows = hard_rows + control_rows + no_regression_rows
    rows.sort(
        key=lambda row: (
            row["panel_role"],
            row.get("target_family") or "no_regression",
            row["source_row_index"],
        )
    )
    return rows


def summarize_validation_projection_port_rows(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize validation panel readiness and promotion gates."""

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
    hard_family_counts = Counter(
        str(row["target_family"]) for row in rows if row["panel_role"] == "hard"
    )
    control_family_counts = Counter(
        str(row["target_family"]) for row in rows if row["panel_role"] == "control"
    )
    exact_evidence_rows = sum(bool(row["exact_evidence"]) for row in rows)
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
    if exact_evidence_rows != len(rows):
        gate_failures.append("non_exact_evidence_rows_present")
    if projection_ownership_explicit_rows != len(rows):
        gate_failures.append("projection_ownership_not_explicit")
    if source_note_text_rows:
        gate_failures.append("source_note_text_present")
    if dict(hard_family_counts) != dict(control_family_counts):
        gate_failures.append("hard_control_family_mismatch")
    return {
        "artifact_kind": "gan2026_structured_validation_projection_port_panel_summary",
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
        "exact_evidence_rows": exact_evidence_rows,
        "projection_ownership_explicit_rows": projection_ownership_explicit_rows,
        "source_note_text_rows": source_note_text_rows,
        "hard_family_counts": dict(sorted(hard_family_counts.items())),
        "control_family_counts": dict(sorted(control_family_counts.items())),
        "target_family_counts": dict(
            sorted(Counter(str(row.get("target_family")) for row in rows).items())
        ),
        "projection_owner_counts": dict(
            sorted(Counter(str(row["projection_owner"]) for row in rows).items())
        ),
        "frozen_test_audit_ready": not gate_failures,
        "holdout_authorized": False,
        "locked_test_row_level_artifacts_used": 0,
        "gate_failures": gate_failures,
        "claim_boundary": (
            "Validation-development hard/control port of the passing synthetic "
            "structured projection mechanisms. It keeps only exact-evidence rows, "
            "balances matched controls by target family, writes no note text, uses "
            "no locked-test row-level artifacts, and does not authorize holdout use."
        ),
        "decision": (
            "validation_projection_port_panel_ready_for_extractor_smoke_undercoverage"
            if rows
            and exact_evidence_rows == len(rows)
            and source_note_text_rows == 0
            and dict(hard_family_counts) == dict(control_family_counts)
            else "revise_validation_projection_port_panel"
        ),
        "recommended_next_step": (
            "Run an extractor smoke over this exact-evidence validation port panel. "
            "Treat it as mechanism diagnostics only unless coverage and W->C gates "
            "are changed by a written protocol."
        ),
    }


def materialize_validation_projection_port_panel(
    *,
    miner_jsonl_path: Path = DEFAULT_MINER_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    miner_rows = load_jsonl_rows(miner_jsonl_path)
    rows = build_validation_projection_port_rows(miner_rows)
    summary = summarize_validation_projection_port_rows(rows)
    summary = {
        **summary,
        "source_miner_artifact": str(miner_jsonl_path),
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
        "# Gan 2026 Structured Validation Projection Port Panel v0",
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
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
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
    lines.extend(
        ["", "## Target Families", "", "| Family | Hard | Control |", "| --- | ---: | ---: |"]
    )
    for family, hard_count in summary["hard_family_counts"].items():
        lines.append(
            f"| `{family}` | {hard_count} | "
            f"{summary['control_family_counts'].get(family, 0)} |"
        )
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
            f"- Panel JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source miner JSONL: `{summary['source_miner_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _matched_exact_control_rows(
    miner_rows: Sequence[Mapping[str, Any]],
    hard_family_counts: Counter[str],
) -> list[dict[str, Any]]:
    controls = []
    control_counts: Counter[str] = Counter()
    for row in miner_rows:
        if row["panel_role"] != "control" or not _has_clean_exact_evidence(row):
            continue
        family = str(row["target_family"])
        if control_counts[family] >= hard_family_counts[family]:
            continue
        controls.append(_ported_row(row))
        control_counts[family] += 1
    return controls


def _ported_row(row: Mapping[str, Any]) -> dict[str, Any]:
    panel_source = str(row.get("policy_name") or "unknown_source")
    return {
        **dict(row),
        "artifact_kind": "gan2026_structured_validation_projection_port_panel_row",
        "policy_name": POLICY_NAME,
        "representation_version": REPRESENTATION_VERSION,
        "panel_source": panel_source,
        "source_note_text": None,
        "source_note_text_present": False,
        "promotion_scope": "validation_projection_port_panel_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def _has_clean_exact_evidence(row: Mapping[str, Any]) -> bool:
    return bool(row["exact_evidence"]) and not row["contract_issues"]


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--miner-jsonl-path", type=Path, default=DEFAULT_MINER_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_validation_projection_port_panel(
        miner_jsonl_path=args.miner_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "frozen_test_audit_ready": summary["frozen_test_audit_ready"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
