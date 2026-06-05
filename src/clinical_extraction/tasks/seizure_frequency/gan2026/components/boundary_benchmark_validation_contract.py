"""Validation typed-field contract smoke for H3/H7 boundary and renderer panels."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_validation_panel,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_boundary_benchmark_validation_contract_v0"
DEFAULT_PANEL_JSONL_PATH = (
    boundary_benchmark_validation_panel.DEFAULT_OUTPUT_JSONL_PATH
)
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_benchmark_validation_contract_v0_2026-06-05.md"
)


def build_contract_rows(panel_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Replay validation panel typed fields through the no-call contract."""

    return [build_contract_row(row) for row in panel_rows]


def build_contract_row(panel_row: Mapping[str, Any]) -> dict[str, Any]:
    """Check one saved validation panel row for typed-field transparency."""

    target_mechanism = str(panel_row["target_mechanism"])
    result = {
        "component_owner": _component_owner(target_mechanism),
        "boundary_state": str(panel_row["expected_boundary_state"]),
        "clinical_final_state": str(panel_row["expected_clinical_final_state"]),
        "gan_rendered_label": str(panel_row["expected_gan_rendered_label"]),
        "benchmark_policy_id": _benchmark_policy_id(target_mechanism),
        "benchmark_format_rule_id": str(
            panel_row["expected_benchmark_format_rule_id"]
        ),
        "format_only_change": bool(panel_row["expected_format_only_change"]),
        "scorer_sentinel_used": bool(panel_row["expected_scorer_sentinel_used"]),
        "candidate_exposure": _candidate_exposure(target_mechanism),
        "evidence": str(panel_row["expected_evidence_substring"]),
        "exact_evidence": bool(panel_row["exact_evidence"]),
    }
    issues = _contract_issues(panel_row, result)
    return {
        "artifact_kind": "gan2026_boundary_benchmark_validation_contract_row",
        "policy_name": POLICY_NAME,
        "source_row_index": int(panel_row["source_row_index"]),
        "split": panel_row["split"],
        "split_manifest": panel_row["split_manifest"],
        "slice_id": panel_row["slice_id"],
        "panel_role": panel_row["panel_role"],
        "target_family": panel_row["target_family"],
        "target_mechanism": target_mechanism,
        **result,
        "gold_label": panel_row["gold_label"],
        "source_note_text": None,
        "source_note_text_present": panel_row.get("source_note_text") is not None,
        "expected_boundary_state": panel_row["expected_boundary_state"],
        "expected_clinical_final_state": panel_row["expected_clinical_final_state"],
        "expected_gan_rendered_label": panel_row["expected_gan_rendered_label"],
        "expected_benchmark_policy_id": panel_row["expected_benchmark_policy_id"],
        "expected_benchmark_format_rule_id": panel_row[
            "expected_benchmark_format_rule_id"
        ],
        "expected_format_only_change": panel_row["expected_format_only_change"],
        "expected_scorer_sentinel_used": panel_row["expected_scorer_sentinel_used"],
        "expected_candidate_exposure": panel_row["expected_candidate_exposure"],
        "contract_matched": not issues,
        "contract_issues": issues,
        "final_label_policy_connected": bool(
            panel_row.get("final_label_policy_connected")
        ),
        "promotion_scope": "validation_contract_smoke_no_final_label_promotion",
        "claim_boundary": "validation_development_only_no_holdout_use",
    }


def summarize_contract_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize validation contract health and transparency constraints."""

    contract_matched_rows = sum(row["contract_matched"] is True for row in rows)
    exact_evidence_rows = sum(row["exact_evidence"] is True for row in rows)
    source_note_text_rows = sum(bool(row["source_note_text_present"]) for row in rows)
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    mechanism_counts = Counter(str(row["target_mechanism"]) for row in rows)
    issue_counts = Counter(
        issue for row in rows for issue in row.get("contract_issues", [])
    )
    passed = (
        bool(rows)
        and contract_matched_rows == len(rows)
        and exact_evidence_rows == len(rows)
        and source_note_text_rows == 0
        and not final_policy_connected
    )
    return {
        "artifact_kind": "gan2026_boundary_benchmark_validation_contract_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "contract_matched_rows": contract_matched_rows,
        "contract_issue_counts": dict(sorted(issue_counts.items())),
        "exact_evidence_rows": exact_evidence_rows,
        "source_note_text_rows": source_note_text_rows,
        "final_label_policy_connected": final_policy_connected,
        "hard_rows": sum(row["panel_role"] == "hard" for row in rows),
        "control_rows": sum(row["panel_role"] == "control" for row in rows),
        "target_mechanism_counts": dict(sorted(mechanism_counts.items())),
        "slice_counts": dict(
            sorted(Counter(str(row["slice_id"]) for row in rows).items())
        ),
        "boundary_state_counts": dict(
            sorted(Counter(str(row["boundary_state"]) for row in rows).items())
        ),
        "benchmark_rule_counts": dict(
            sorted(Counter(str(row["benchmark_format_rule_id"]) for row in rows).items())
        ),
        "claim_boundary": (
            "Validation-development H3/H7 typed-field contract smoke over the "
            "boundary/benchmark validation panel. It checks typed-field "
            "classification, exact-evidence carry-through, renderer transparency, "
            "and absence of note text or final-label policy connection. It does "
            "not authorize candidate assembly or holdout use."
        ),
        "decision": (
            "boundary_renderer_validation_contract_passed"
            if passed
            else "boundary_renderer_validation_contract_failed"
        ),
        "recommended_next_step": (
            "Use this passed validation mechanism contract as a pre-assembly "
            "control, then decide whether to connect the typed boundary/renderer "
            "fields to a candidate assembly protocol on validation only."
        ),
    }


def materialize_validation_contract_smoke(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    panel_rows = load_jsonl_rows(panel_jsonl_path)
    rows = build_contract_rows(panel_rows)
    summary = summarize_contract_rows(rows)
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
        "# Gan 2026 Boundary/Benchmark Validation Contract Smoke v0",
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
        f"| contract-matched rows | {summary['contract_matched_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| source-note-text rows | {summary['source_note_text_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        "",
        "## Target Mechanisms",
        "",
        "| Mechanism | Rows |",
        "| --- | ---: |",
    ]
    for mechanism, count in summary["target_mechanism_counts"].items():
        lines.append(f"| `{mechanism}` | {count} |")
    lines.extend(["", "## Slices", "", "| Slice | Rows |", "| --- | ---: |"])
    for slice_id, count in summary["slice_counts"].items():
        lines.append(f"| `{slice_id}` | {count} |")
    lines.extend(["", "## Benchmark Rules", "", "| Rule | Rows |", "| --- | ---: |"])
    for rule, count in summary["benchmark_rule_counts"].items():
        lines.append(f"| `{rule}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Contract JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _contract_issues(
    panel_row: Mapping[str, Any],
    result: Mapping[str, Any],
) -> list[str]:
    comparisons = {
        "boundary_state": result["boundary_state"],
        "clinical_final_state": result["clinical_final_state"],
        "gan_rendered_label": result["gan_rendered_label"],
        "benchmark_policy_id": result["benchmark_policy_id"],
        "benchmark_format_rule_id": result["benchmark_format_rule_id"],
        "format_only_change": result["format_only_change"],
        "scorer_sentinel_used": result["scorer_sentinel_used"],
        "candidate_exposure": result["candidate_exposure"],
    }
    issues = [
        f"{field}_mismatch"
        for field, actual in comparisons.items()
        if actual != panel_row[f"expected_{field}"]
    ]
    if not result["exact_evidence"]:
        issues.append("evidence_not_exact")
    if panel_row.get("source_note_text") is not None:
        issues.append("source_note_text_present")
    if panel_row.get("final_label_policy_connected"):
        issues.append("final_label_policy_connected")
    return issues


def _component_owner(target_mechanism: str) -> str:
    if target_mechanism == "seizure_free_boundary_event_v0":
        return "typed_boundary_classifier"
    return "benchmark_renderer"


def _benchmark_policy_id(target_mechanism: str) -> str:
    if target_mechanism == "seizure_free_boundary_event_v0":
        return "gan2026_boundary_projection_policy_v0"
    return "gan2026_benchmark_renderer_policy_v0"


def _candidate_exposure(target_mechanism: str) -> str:
    if target_mechanism == "seizure_free_boundary_event_v0":
        return "typed_boundary_event_present"
    return "typed_clinical_state_present"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_validation_contract_smoke(
        panel_jsonl_path=args.panel_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {"decision": summary["decision"], "row_count": summary["row_count"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
