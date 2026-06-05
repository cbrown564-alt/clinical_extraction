"""Boundary event contract v1 with final-label policy disconnected."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
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

POLICY_NAME = "gan2026_boundary_event_contract_v1"
DEFAULT_PANEL_JSONL_PATH = boundary_benchmark_seed_panel.DEFAULT_OUTPUT_JSONL_PATH
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_boundary_event_contract_v1_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_boundary_event_contract_v1_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_boundary_event_contract_v1_2026-06-05.md"
)


def build_contract_rows(panel_rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Run the v1 typed-event contract over synthetic panel rows."""

    return [build_contract_row(row) for row in panel_rows]


def build_contract_row(panel_row: Mapping[str, Any]) -> dict[str, Any]:
    """Build one v1 typed event contract row."""

    base_row = boundary_benchmark_contract.build_contract_row(panel_row)
    clinical_event = _clinical_event(base_row)
    projection_policy = _projection_policy(base_row)
    issues = list(base_row["contract_issues"])
    if not _clinical_event_complete(clinical_event):
        issues.append("clinical_event_incomplete")
    if not _projection_policy_complete(projection_policy):
        issues.append("projection_policy_incomplete")
    return {
        "artifact_kind": "gan2026_boundary_event_contract_v1_row",
        "policy_name": POLICY_NAME,
        "source_row_index": base_row["source_row_index"],
        "split": base_row["split"],
        "split_manifest": base_row["split_manifest"],
        "hypothesis_ids": base_row.get("hypothesis_ids", []),
        "pair_id": base_row["pair_id"],
        "pair_variant": base_row["pair_variant"],
        "panel_role": base_row["panel_role"],
        "target_family": base_row["target_family"],
        "target_mechanism": base_row["target_mechanism"],
        "clinical_event": clinical_event,
        "boundary_state": base_row["boundary_state"],
        "selected_frequency_state": base_row["clinical_final_state"],
        "projection_policy": projection_policy,
        "gan_rendered_label": base_row["gan_rendered_label"],
        "evidence": base_row["evidence"],
        "exact_evidence": base_row["exact_evidence"],
        "expected_boundary_state": base_row["expected_boundary_state"],
        "expected_selected_frequency_state": base_row[
            "expected_clinical_final_state"
        ],
        "expected_gan_rendered_label": base_row["expected_gan_rendered_label"],
        "contract_matched": not issues,
        "contract_issues": issues,
        "final_label_policy_connected": False,
        "claim_boundary": (
            "synthetic_typed_event_contract_only_no_final_label_promotion"
        ),
    }


def summarize_contract_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize typed event completeness and pair consistency."""

    pair_rows = _rows_by_pair(rows)
    invariant_pairs = sum(
        _pair_selected_state_invariant(pair) for pair in pair_rows.values()
    )
    contract_matched_rows = sum(row["contract_matched"] is True for row in rows)
    exact_evidence_rows = sum(row["exact_evidence"] is True for row in rows)
    typed_event_complete_rows = sum(
        _clinical_event_complete(row["clinical_event"]) for row in rows
    )
    projection_policy_complete_rows = sum(
        _projection_policy_complete(row["projection_policy"]) for row in rows
    )
    issue_counts = Counter(
        issue for row in rows for issue in row.get("contract_issues", [])
    )
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    passed = (
        bool(rows)
        and contract_matched_rows == len(rows)
        and exact_evidence_rows == len(rows)
        and invariant_pairs == len(pair_rows)
        and typed_event_complete_rows == len(rows)
        and projection_policy_complete_rows == len(rows)
        and not final_policy_connected
    )
    return {
        "artifact_kind": "gan2026_boundary_event_contract_v1_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "pair_count": len(pair_rows),
        "clinical_state_invariant_pairs": invariant_pairs,
        "contract_matched_rows": contract_matched_rows,
        "contract_issue_counts": dict(sorted(issue_counts.items())),
        "exact_evidence_rows": exact_evidence_rows,
        "typed_event_complete_rows": typed_event_complete_rows,
        "projection_policy_complete_rows": projection_policy_complete_rows,
        "target_mechanism_counts": dict(
            sorted(Counter(str(row["target_mechanism"]) for row in rows).items())
        ),
        "event_kind_counts": dict(
            sorted(
                Counter(str(row["clinical_event"]["event_kind"]) for row in rows).items()
            )
        ),
        "projection_owner_counts": dict(
            sorted(
                Counter(
                    str(row["projection_policy"]["projection_owner"]) for row in rows
                ).items()
            )
        ),
        "final_label_policy_connected": final_policy_connected,
        "claim_boundary": (
            "Synthetic boundary_event_contract_v1 mechanism smoke. It exposes "
            "clinical_event, boundary_state, selected_frequency_state, "
            "projection_policy, and gan_rendered_label while keeping final-label "
            "policy disconnected. It is not validation or holdout evidence."
        ),
        "decision": (
            "boundary_event_contract_v1_passed"
            if passed
            else "boundary_event_contract_v1_failed"
        ),
        "recommended_next_step": (
            "Run boundary_event_validation_panel_v1 on validation hard/control "
            "rows with final policy disconnected, exact evidence required, and "
            "unsupported candidates suppressed."
        ),
    }


def materialize_contract_smoke(
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
        "# Gan 2026 Boundary Event Contract v1",
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
        f"| pairs | {summary['pair_count']} |",
        f"| clinical-state invariant pairs | {summary['clinical_state_invariant_pairs']} |",
        f"| contract-matched rows | {summary['contract_matched_rows']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| typed-event complete rows | {summary['typed_event_complete_rows']} |",
        f"| projection-policy complete rows | {summary['projection_policy_complete_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        "",
        "## Event Kinds",
        "",
        "| Event kind | Rows |",
        "| --- | ---: |",
    ]
    for event_kind, count in summary["event_kind_counts"].items():
        lines.append(f"| `{event_kind}` | {count} |")
    lines.extend(
        [
            "",
            "## Projection Owners",
            "",
            "| Owner | Rows |",
            "| --- | ---: |",
        ]
    )
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
            f"- Contract JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source panel JSONL: `{summary['source_panel_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _clinical_event(row: Mapping[str, Any]) -> dict[str, str]:
    if row["component_owner"] == "benchmark_renderer":
        event_kind = "benchmark_format_convention"
    else:
        event_kind = str(row["clinical_final_state"])
    return {
        "event_target": "seizure",
        "event_kind": event_kind,
        "event_state": str(row["clinical_final_state"]),
        "component_owner": str(row["component_owner"]),
    }


def _projection_policy(row: Mapping[str, Any]) -> dict[str, str]:
    if row["component_owner"] == "benchmark_renderer":
        policy_id = "gan2026_benchmark_renderer_policy_v1"
        owner = "benchmark_renderer"
        stage = "benchmark_format_rendering"
    else:
        policy_id = "gan2026_boundary_projection_policy_v1"
        owner = "boundary_projection_policy"
        stage = "clinical_event_to_benchmark_label"
    return {
        "projection_policy_id": policy_id,
        "projection_owner": owner,
        "projection_stage": stage,
        "benchmark_format_rule_id": str(row["benchmark_format_rule_id"]),
    }


def _clinical_event_complete(clinical_event: Mapping[str, Any]) -> bool:
    return all(
        bool(clinical_event.get(field))
        for field in ("event_target", "event_kind", "event_state", "component_owner")
    )


def _projection_policy_complete(projection_policy: Mapping[str, Any]) -> bool:
    return all(
        bool(projection_policy.get(field))
        for field in (
            "projection_policy_id",
            "projection_owner",
            "projection_stage",
            "benchmark_format_rule_id",
        )
    )


def _rows_by_pair(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    pairs: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        pairs[str(row["pair_id"])].append(row)
    return pairs


def _pair_selected_state_invariant(rows: Sequence[Mapping[str, Any]]) -> bool:
    return len({str(row["selected_frequency_state"]) for row in rows}) == 1


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-jsonl-path", type=Path, default=DEFAULT_PANEL_JSONL_PATH)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_contract_smoke(
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
