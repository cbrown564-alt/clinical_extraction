"""H7 minimal-pair robustness panel for typed boundary events."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_seed_panel,
    boundary_event_contract,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

POLICY_NAME = "gan2026_h7_minimal_pair_panel_v1"
DEFAULT_CONTRACT_JSONL_PATH = boundary_event_contract.DEFAULT_OUTPUT_JSONL_PATH
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_h7_minimal_pair_panel_v1_2026-06-05.md"
)

PAIR_AXIS_BY_ID = {
    "sf_asserted_interval": "wording",
    "last_event_only": "wording",
    "residual_active_semiology": "order_semiology",
    "unresolved_cluster_burden": "order",
    "unknown_no_reference_sentinel": "sentinel_boundary",
    "vague_multiple_frequency": "wording",
    "sf_asserted_interval_generated": "wording_time_anchor",
    "last_event_only_generated": "wording_time_anchor",
    "conditional_trigger_only": "distractor_trigger_context",
    "non_epileptic_current_events": "wording_semiology",
    "residual_active_semiology_generated": "order_semiology",
    "no_boundary_evidence": "section_distractor",
    "conditional_trigger_ordering": "order_distractor",
    "cluster_generated_interval": "order",
    "vague_multiple_generated_week": "wording",
    "unknown_generated_sentinel": "wording",
    "non_epileptic_renderer_projection": "wording_semiology",
    "cluster_generated_week": "order",
}


def build_minimal_pair_rows(
    contract_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Convert boundary contract rows into H7 robustness rows."""

    pair_counts = Counter(str(row["pair_id"]) for row in contract_rows)
    return [
        _to_h7_row(row, pair_size=pair_counts[str(row["pair_id"])])
        for row in contract_rows
    ]


def build_rows_and_summary(
    contract_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = build_minimal_pair_rows(contract_rows)
    return rows, summarize_minimal_pair_rows(rows)


def summarize_minimal_pair_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize pair consistency across perturbation axes."""

    pair_rows = _rows_by_pair(rows)
    invariant_pairs = sum(_pair_invariant(pair) for pair in pair_rows.values())
    pair_complete_count = sum(_pair_complete(pair) for pair in pair_rows.values())
    exact_evidence_rows = sum(row["exact_evidence"] is True for row in rows)
    final_policy_connected = any(row.get("final_label_policy_connected") for row in rows)
    inconsistent_pairs = [
        pair_id for pair_id, pair in pair_rows.items() if not _pair_invariant(pair)
    ]
    axis_counts = Counter(str(row["perturbation_axis"]) for row in rows)
    axis_pair_counts = Counter(
        str(pair[0]["perturbation_axis"]) for pair in pair_rows.values()
    )
    axis_invariant_pair_counts = Counter(
        str(pair[0]["perturbation_axis"])
        for pair in pair_rows.values()
        if _pair_invariant(pair)
    )
    passed = (
        bool(rows)
        and pair_complete_count == len(pair_rows)
        and invariant_pairs == len(pair_rows)
        and exact_evidence_rows == len(rows)
        and not final_policy_connected
    )
    return {
        "artifact_kind": "gan2026_h7_minimal_pair_panel_v1_summary",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "pair_count": len(pair_rows),
        "complete_pairs": pair_complete_count,
        "clinical_state_invariant_pairs": invariant_pairs,
        "inconsistent_pair_ids": sorted(inconsistent_pairs),
        "exact_evidence_rows": exact_evidence_rows,
        "final_label_policy_connected": final_policy_connected,
        "perturbation_axis_counts": dict(sorted(axis_counts.items())),
        "perturbation_axis_pair_counts": dict(sorted(axis_pair_counts.items())),
        "perturbation_axis_invariant_pair_counts": dict(
            sorted(axis_invariant_pair_counts.items())
        ),
        "selected_frequency_state_counts": dict(
            sorted(Counter(str(row["selected_frequency_state"]) for row in rows).items())
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
        "claim_boundary": (
            "Synthetic H7 minimal-pair robustness panel. It reuses "
            "boundary_event_contract_v1 rows to test whether typed mechanism state "
            "is preserved across wording, order, section, distractor, semiology, "
            "and time-anchor perturbations. It is not validation or holdout "
            "evidence and does not connect final-label policy."
        ),
        "decision": (
            "h7_minimal_pair_panel_v1_passed"
            if passed
            else "h7_minimal_pair_panel_v1_failed"
        ),
        "recommended_next_step": (
            "Add benchmark_renderer_fixture_v1 with clinical state frozen and "
            "renderer effects explicit before boundary_renderer_component_ablation_v1."
        ),
    }


def materialize_minimal_pair_panel(
    *,
    contract_jsonl_path: Path = DEFAULT_CONTRACT_JSONL_PATH,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
) -> dict[str, Any]:
    if contract_jsonl_path.exists():
        contract_rows = load_jsonl_rows(contract_jsonl_path)
    else:
        contract_rows = boundary_event_contract.build_contract_rows(
            boundary_benchmark_seed_panel.build_seed_panel_rows()
        )
    rows, summary = build_rows_and_summary(contract_rows)
    summary = {
        **summary,
        "source_contract_artifact": str(contract_jsonl_path),
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
        "# Gan 2026 H7 Minimal Pair Panel v1",
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
        f"| complete pairs | {summary['complete_pairs']} |",
        f"| clinical-state invariant pairs | {summary['clinical_state_invariant_pairs']} |",
        f"| exact evidence rows | {summary['exact_evidence_rows']} |",
        f"| final-label policy connected | {summary['final_label_policy_connected']} |",
        "",
        "## Perturbation Axes",
        "",
        "| Axis | Pairs | Invariant pairs | Rows |",
        "| --- | ---: | ---: | ---: |",
    ]
    axis_pairs = summary["perturbation_axis_pair_counts"]
    axis_invariant = summary["perturbation_axis_invariant_pair_counts"]
    axis_rows = summary["perturbation_axis_counts"]
    for axis in sorted(axis_rows):
        lines.append(
            f"| `{axis}` | {axis_pairs.get(axis, 0)} | "
            f"{axis_invariant.get(axis, 0)} | {axis_rows[axis]} |"
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
            f"- Panel JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source contract JSONL: `{summary['source_contract_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _to_h7_row(row: Mapping[str, Any], *, pair_size: int) -> dict[str, Any]:
    pair_id = str(row["pair_id"])
    return {
        "artifact_kind": "gan2026_h7_minimal_pair_panel_v1_row",
        "policy_name": POLICY_NAME,
        "source_row_index": row["source_row_index"],
        "split": row["split"],
        "split_manifest": row["split_manifest"],
        "hypothesis_ids": row.get("hypothesis_ids", []),
        "pair_id": pair_id,
        "pair_variant": row["pair_variant"],
        "pair_size": pair_size,
        "perturbation_axis": PAIR_AXIS_BY_ID.get(pair_id, "unclassified"),
        "panel_role": row["panel_role"],
        "target_family": row["target_family"],
        "target_mechanism": row["target_mechanism"],
        "clinical_event": row["clinical_event"],
        "boundary_state": row["boundary_state"],
        "selected_frequency_state": row["selected_frequency_state"],
        "projection_policy": row["projection_policy"],
        "gan_rendered_label": row["gan_rendered_label"],
        "evidence": row["evidence"],
        "exact_evidence": row["exact_evidence"],
        "contract_matched": row["contract_matched"],
        "final_label_policy_connected": False,
        "promotion_scope": "synthetic_h7_minimal_pair_no_final_label_promotion",
        "claim_boundary": "synthetic_development_only_no_holdout_use",
    }


def _rows_by_pair(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    pairs: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        pairs[str(row["pair_id"])].append(row)
    return pairs


def _pair_complete(rows: Sequence[Mapping[str, Any]]) -> bool:
    return len(rows) >= 2 and all(int(row["pair_size"]) == len(rows) for row in rows)


def _pair_invariant(rows: Sequence[Mapping[str, Any]]) -> bool:
    return (
        _pair_complete(rows)
        and len({str(row["selected_frequency_state"]) for row in rows}) == 1
        and len({str(row["clinical_event"]["event_state"]) for row in rows}) == 1
        and len({str(row["gan_rendered_label"]) for row in rows}) == 1
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract-jsonl-path",
        type=Path,
        default=DEFAULT_CONTRACT_JSONL_PATH,
    )
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    args = parser.parse_args(argv)
    summary = materialize_minimal_pair_panel(
        contract_jsonl_path=args.contract_jsonl_path,
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
    )
    print(
        json.dumps(
            {
                "decision": summary["decision"],
                "pair_count": summary["pair_count"],
                "row_count": summary["row_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
