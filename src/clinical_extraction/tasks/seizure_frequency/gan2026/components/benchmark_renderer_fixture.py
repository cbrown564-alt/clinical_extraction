"""Benchmark renderer fixture v1 with clinical state frozen."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_contract,
    boundary_benchmark_seed_panel,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_benchmark_renderer_fixture_v1"
DEFAULT_PANEL_JSONL_PATH = boundary_benchmark_seed_panel.DEFAULT_OUTPUT_JSONL_PATH
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_benchmark_renderer_fixture_v1_2026-06-05.md"
)


def build_fixture_rows(contract_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Build renderer-only fixture rows from boundary/benchmark contract rows."""

    return [
        _to_fixture_row(row)
        for row in contract_rows
        if row["target_mechanism"] == "benchmark_convention_renderer_v0"
    ]


def build_rows_and_summary(
    contract_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = build_fixture_rows(contract_rows)
    return rows, summarize_fixture_rows(rows)


def summarize_fixture_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize renderer-only preservation and benchmark-rule visibility."""

    clinical_state_preserved_rows = sum(
        row["clinical_state_preserved"] is True for row in rows
    )
    exact_evidence_rows = sum(row["exact_evidence"] is True for row in rows)
    contract_matched_rows = sum(row["contract_matched"] is True for row in rows)
    format_only_rows = sum(row["format_only_change"] is True for row in rows)
    renderer_rule_id_rows = sum(
        bool(row["benchmark_format_rule_id"])
        and row["benchmark_format_rule_id"] != "none_boundary_state_only"
        for row in rows
    )
    sentinel_visibility_rows = sum(
        isinstance(row.get("scorer_sentinel_used"), bool) for row in rows
    )
    sentinel_used_rows = sum(row["scorer_sentinel_used"] is True for row in rows)
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    passed = (
        bool(rows)
        and clinical_state_preserved_rows == len(rows)
        and exact_evidence_rows == len(rows)
        and contract_matched_rows == len(rows)
        and format_only_rows == len(rows)
        and renderer_rule_id_rows == len(rows)
        and sentinel_visibility_rows == len(rows)
        and sentinel_used_rows > 0
        and not final_policy_connected
    )
    return {
        "artifact_kind": "gan2026_benchmark_renderer_fixture_v1_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "clinical_state_preserved_rows": clinical_state_preserved_rows,
        "format_only_rows": format_only_rows,
        "renderer_rule_id_rows": renderer_rule_id_rows,
        "sentinel_visibility_rows": sentinel_visibility_rows,
        "scorer_sentinel_used_rows": sentinel_used_rows,
        "exact_evidence_rows": exact_evidence_rows,
        "contract_matched_rows": contract_matched_rows,
        "final_label_policy_connected": final_policy_connected,
        "benchmark_rule_counts": dict(
            sorted(Counter(str(row["benchmark_format_rule_id"]) for row in rows).items())
        ),
        "clinical_state_counts": dict(
            sorted(Counter(str(row["input_clinical_state"]) for row in rows).items())
        ),
        "gan_rendered_label_counts": dict(
            sorted(Counter(str(row["gan_rendered_label"]) for row in rows).items())
        ),
        "claim_boundary": (
            "Synthetic benchmark_renderer_fixture_v1. It freezes input clinical "
            "state, exercises benchmark-only rendering, exposes renderer rule ids "
            "and scorer-sentinel use, and keeps final-label policy disconnected. "
            "It is not validation or holdout evidence."
        ),
        "decision": (
            "benchmark_renderer_fixture_v1_passed"
            if passed
            else "benchmark_renderer_fixture_v1_failed"
        ),
        "recommended_next_step": (
            "Run boundary_renderer_component_ablation_v1 as validation diagnostics "
            "with benchmark-only gains separated from clinical-state changes."
        ),
    }


def materialize_renderer_fixture(
    *,
    panel_jsonl_path: Path = DEFAULT_PANEL_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    if panel_jsonl_path.exists():
        panel_rows = load_jsonl_rows(panel_jsonl_path)
    else:
        panel_rows = boundary_benchmark_seed_panel.build_seed_panel_rows()
    contract_rows = boundary_benchmark_contract.build_contract_rows(panel_rows)
    rows, summary = build_rows_and_summary(contract_rows)
    summary = {
        **summary,
        "source_panel_artifact": str(panel_jsonl_path),
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
        "split": "synthetic_hard_control",
        "split_manifest": boundary_benchmark_seed_panel.PANEL_NAME,
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
        "# Gan 2026 Benchmark Renderer Fixture v1",
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
        f"| clinical-state preserved rows | {summary['clinical_state_preserved_rows']} |",
        f"| format-only rows | {summary['format_only_rows']} |",
        f"| renderer rule-id rows | {summary['renderer_rule_id_rows']} |",
        f"| sentinel visibility rows | {summary['sentinel_visibility_rows']} |",
        f"| scorer-sentinel used rows | {summary['scorer_sentinel_used_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| contract-matched rows | {summary['contract_matched_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        "",
        "## Renderer Rules",
        "",
        "| Rule | Rows |",
        "| --- | ---: |",
    ]
    for rule_id, count in summary["benchmark_rule_counts"].items():
        lines.append(f"| `{rule_id}` | {count} |")
    lines.extend(
        [
            "",
            "## Next Step",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Fixture JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _to_fixture_row(row: Mapping[str, Any]) -> dict[str, Any]:
    input_clinical_state = str(row["expected_clinical_final_state"])
    output_clinical_state = str(row["clinical_final_state"])
    return {
        "artifact_kind": "gan2026_benchmark_renderer_fixture_v1_row",
        "policy_name": POLICY_NAME,
        "source_row_index": row["source_row_index"],
        "split": row["split"],
        "split_manifest": row["split_manifest"],
        "hypothesis_ids": row.get("hypothesis_ids", []),
        "pair_id": row["pair_id"],
        "pair_variant": row["pair_variant"],
        "panel_role": row["panel_role"],
        "target_family": row["target_family"],
        "target_mechanism": row["target_mechanism"],
        "component_owner": "benchmark_renderer",
        "input_clinical_state": input_clinical_state,
        "output_clinical_state": output_clinical_state,
        "clinical_state_preserved": input_clinical_state == output_clinical_state,
        "gan_rendered_label": row["gan_rendered_label"],
        "benchmark_policy_id": "gan2026_benchmark_renderer_policy_v1",
        "benchmark_format_rule_id": row["benchmark_format_rule_id"],
        "format_only_change": row["format_only_change"],
        "scorer_sentinel_used": row["scorer_sentinel_used"],
        "evidence": row["evidence"],
        "exact_evidence": row["exact_evidence"],
        "contract_matched": row["contract_matched"],
        "final_label_policy_connected": False,
        "promotion_scope": "synthetic_renderer_fixture_no_final_label_promotion",
        "claim_boundary": "synthetic_development_only_no_holdout_use",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_renderer_fixture(
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
