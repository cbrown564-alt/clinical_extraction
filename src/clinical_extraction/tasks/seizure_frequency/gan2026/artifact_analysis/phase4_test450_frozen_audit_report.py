"""Phase 4 frozen test450 aggregate audit report (4 architectures, gpt-4.1-mini).

Authorized 2026-06-09 (docs/research/gan2026_three_way_architecture_comparison_and_
cross_pollination_plan_2026-06-07.md, Section 6, Phase 4): one-shot frozen aggregate
read of the locked `test450` split for four of the six PipelineArchitecture configs --
`deterministic_canonical_pipeline`, `hybrid` (v5 prompt), `hybrid_structured_events`,
`llm_only_canonical_pipeline` (v0.5 prompt). `deterministic` and
`llm_only_direct_labeler` are intentionally excluded (DCP is numerically identical to
deterministic; DL consistently underperforms CP -- see plan Section 6 rationale).

This module makes no model calls and performs no re-run. It reuses the shared
per-architecture summary helpers from `three_way_comparison_report` (single-shot
summary rows for DCP/SE/CP, deep-replay summary+appendix for hybrid) but reports
against the four authorized architectures and the `test` split's gold records.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.three_way_comparison_report import (
    EVIDENCE_TRACE_FOOTNOTE,
    SE_ARCHITECTURE_FOOTNOTE,
    _hybrid_data_source_footnote,
    _hybrid_summary_row,
    _single_shot_summary_row,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import write_markdown_report

PHASE4_ARCHITECTURES: tuple[str, ...] = (
    "deterministic_canonical_pipeline",
    "hybrid",
    "hybrid_structured_events",
    "llm_only_canonical_pipeline",
)

DEFAULT_ARTIFACT_JSONL_PATHS: dict[str, Path] = {
    "deterministic_canonical_pipeline": Path(
        "experiments/gan2026_test450_phase4_frozen_audit"
        "_deterministic_canonical_pipeline_gpt41mini_2026-06-09.jsonl"
    ),
    "hybrid": Path(
        "experiments/gan2026_test450_phase4_frozen_audit_hybrid_gpt41mini_2026-06-09.jsonl"
    ),
    "hybrid_structured_events": Path(
        "experiments/gan2026_test450_phase4_frozen_audit"
        "_hybrid_structured_events_gpt41mini_2026-06-09.jsonl"
    ),
    "llm_only_canonical_pipeline": Path(
        "experiments/gan2026_test450_phase4_frozen_audit"
        "_llm_only_canonical_pipeline_gpt41mini_2026-06-09.jsonl"
    ),
}

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.md"
)


def _claim_boundary(model: str) -> str:
    return (
        f"Phase 4 frozen test450 aggregate audit, {model} pass. One-shot frozen "
        "aggregate read of the locked test450 split for four of the six "
        "PipelineArchitecture configs (deterministic_canonical_pipeline, hybrid v5 "
        "prompt, hybrid_structured_events, llm_only_canonical_pipeline v0.5 prompt); "
        "deterministic and llm_only_direct_labeler are intentionally excluded "
        "(plan Section 6 rationale: DCP is numerically identical to deterministic, "
        "DL consistently underperforms CP). No row-level holdout tuning and no "
        "re-runs based on these results (plan Section 7 guardrails). Compares the "
        "four architectures on the axes that are universally meaningful "
        "(rendered/null disposition, Purist/Pragmatic-correct of rendered rows, "
        "evidence-trace validity, final-answer distribution); hybrid additionally "
        "carries a routing-taxonomy appendix that no other architecture has an "
        "analogous surface for."
    )


def build_phase4_test450_report(
    architecture_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    gold_records: Mapping[int, GanFrequencyRecord],
    model: str = "openai/gpt-4.1-mini",
    split: str = "test",
    hybrid_fallback_candidate_set_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    missing = [name for name in PHASE4_ARCHITECTURES if name not in architecture_rows]
    if missing:
        raise ValueError(f"missing architecture rows for: {missing}")

    summary_rows: list[dict[str, Any]] = []
    hybrid_appendix: dict[str, Any] = {}
    for architecture in PHASE4_ARCHITECTURES:
        rows = architecture_rows[architecture]
        if architecture == "hybrid":
            summary_row, hybrid_appendix = _hybrid_summary_row(
                rows,
                gold_records=gold_records,
                fallback_candidate_set_path=hybrid_fallback_candidate_set_path,
            )
        else:
            summary_row = _single_shot_summary_row(architecture, rows)
        summary_rows.append(summary_row)

    metadata = {
        "artifact_kind": "gan2026_phase4_test450_frozen_audit_report",
        "claim_boundary": _claim_boundary(model),
        "model": model,
        "split": split,
        "row_counts": {row["architecture"]: row["examples"] for row in summary_rows},
        "evidence_trace_footnote": EVIDENCE_TRACE_FOOTNOTE,
        "se_architecture_footnote": SE_ARCHITECTURE_FOOTNOTE,
        "hybrid_data_source_footnote": _hybrid_data_source_footnote(
            hybrid_fallback_candidate_set_path is not None
        ),
        "hybrid_routing_appendix": hybrid_appendix,
    }
    return summary_rows, metadata


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        f"# Gan 2026 Phase 4 Frozen test450 Aggregate Audit ({metadata['model']})",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Comparison JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Model: `{metadata['model']}`",
        f"- Split: `{metadata['split']}` (locked `test450`, `gan2026_split_v1`)",
        "",
        "## Shared Comparison Table",
        "",
        "| Architecture | Examples | Rendered | Null | Routed | "
        "Purist-correct (of rendered) | Pragmatic-correct (of rendered) | "
        "Evidence-trace valid | Source |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        routed = "N/A" if row["routed_rows"] is None else str(row["routed_rows"])
        lines.append(
            f"| `{row['architecture']}` | {row['examples']} | {row['rendered_rows']} | "
            f"{row['null_rows']} | {routed} | "
            f"{row['purist_correct_of_rendered']} "
            f"({row['purist_correct_rate_of_rendered']:.3f}) | "
            f"{row['pragmatic_correct_of_rendered']} "
            f"({row['pragmatic_correct_rate_of_rendered']:.3f}) | "
            f"{row['evidence_trace_valid_rows']} ({row['evidence_trace_valid_rate']:.3f}) | "
            f"`{row['data_source']}` |"
        )
    lines.extend(
        [
            "",
            "Footnotes:",
            "",
            f"- {metadata['evidence_trace_footnote']}",
            f"- {metadata['se_architecture_footnote']}",
            f"- {metadata['hybrid_data_source_footnote']}",
            "",
            "### Evidence-Trace Metric By Architecture",
            "",
            "| Architecture | Metric reported |",
            "| --- | --- |",
        ]
    )
    for row in rows:
        lines.append(f"| `{row['architecture']}` | `{row['evidence_trace_metric']}` |")
    lines.extend(["", "### Final-Answer Distribution (top entries)", ""])
    for row in rows:
        lines.append(f"- `{row['architecture']}`: {row['final_label_distribution']}")

    appendix = dict(metadata.get("hybrid_routing_appendix") or {})
    lines.extend(
        [
            "",
            "## Hybrid-Only Routing Appendix",
            "",
            (
                "No other architecture in this comparison has a routing stage; this "
                "appendix exists to characterize what `hybrid` does with the rows it "
                "doesn't render directly, not to provide a column the other three could "
                "also fill. Drawn from the same deep-replay artifact that supplies "
                "hybrid's shared-table row above."
            ),
            "",
            f"- Routed rows: {appendix.get('routed_rows', 0)} "
            f"({appendix.get('routed_rate_of_rendered', 0.0):.3f} of rendered)",
            f"- Unrouted rows: {appendix.get('unrouted_rows', 0)}",
            "",
            "### Route Family Counts",
            "",
        ]
    )
    family_counts = appendix.get("route_family_counts") or {}
    if not family_counts:
        lines.append("- None.")
    for family, count in family_counts.items():
        lines.append(f"- `{family}`: {count}")
    lines.extend(["", "### Verification Decision Action Counts", ""])
    action_counts = appendix.get("action_counts") or {}
    if not action_counts:
        lines.append("- None.")
    for action, count in action_counts.items():
        lines.append(f"- `{action}`: {count}")
    lines.extend(
        [
            "",
            "## What This Report Does Not Claim",
            "",
            "- This is a one-shot frozen `test450` aggregate read for four "
            "architectures only (deterministic and llm_only_direct_labeler are "
            "excluded by design -- see claim boundary above).",
            "- No row-level holdout tuning was performed and no re-runs are planned "
            "based on these results (plan Section 7 guardrails).",
            "- Evidence-trace metrics are not uniform across architectures (see "
            "footnote and per-architecture metric table above) -- they measure "
            "different things and must not be compared as if they were one accuracy "
            "number.",
            "- hybrid's shared-table numbers come from deep-replay, not its raw "
            "`run_split` output (see footnote above); the other three architectures' "
            "numbers come directly from their `run_split` output.",
            "",
        ]
    )
    write_markdown_report(path, lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for architecture in PHASE4_ARCHITECTURES:
        parser.add_argument(
            f"--{architecture.replace('_', '-')}-jsonl",
            type=Path,
            default=DEFAULT_ARTIFACT_JSONL_PATHS[architecture],
        )
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--hybrid-candidate-set-path", type=Path, default=None)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    architecture_rows = {
        architecture: load_jsonl_rows(getattr(args, f"{architecture}_jsonl"))
        for architecture in PHASE4_ARCHITECTURES
    }
    gold_records = {record.source_row_index: record for record in load_records_for_split("test")}
    rows, metadata = build_phase4_test450_report(
        architecture_rows,
        gold_records=gold_records,
        model=args.model,
        hybrid_fallback_candidate_set_path=args.hybrid_candidate_set_path,
    )
    write_jsonl(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps({"row_counts": metadata["row_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
