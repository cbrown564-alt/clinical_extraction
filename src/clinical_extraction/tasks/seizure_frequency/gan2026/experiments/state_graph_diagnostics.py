"""State-graph diagnostic runner for Gan 2026 validation-cycle work."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    evaluate_predictions,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    synthetic_hard_cases as hard_cases,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    OracleCoverageSummary,
    build_state_graph,
    graph_node_labels,
    oracle_coverage_summary,
    project_graph_to_gan,
)

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_clinical_frequency_state_graph_validation50_diagnostics_2026-06-02.md"
)


def run_state_graph_diagnostics(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    surface_note: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build graph/projection rows and corpus-level diagnostic metadata."""

    rows = [
        _diagnostic_row(record, split=split, split_manifest=split_manifest)
        for record in records
    ]
    coverage = oracle_coverage_summary(records)
    summary = _summary(rows, coverage=coverage)
    metadata = {
        "artifact_kind": "gan2026_clinical_frequency_state_graph_diagnostics",
        "date": "2026-06-02",
        "pipeline_family": "hybrid_clinical_frequency_state_graph",
        "split": split,
        "split_manifest": split_manifest,
        "row_count": len(rows),
        "surface_note": surface_note,
        "graph_builder": "deterministic_oracle_span_harvester_v0",
        "projection_policy": "gan2026_state_graph_projection_v0",
        "claim_language": (
            "Architecture/diagnostic development result only. Oracle coverage, "
            "projection F1, and graph errors are separate signals; this is not a "
            "benchmark result and does not change scorer or holdout policy."
        ),
        "summary": summary,
    }
    return rows, metadata


def write_state_graph_json(metadata: Mapping[str, Any], path: Path) -> None:
    """Write the corpus-level diagnostic summary as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_state_graph_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    """Write a compact human-facing state-graph diagnostic report."""

    summary = metadata["summary"]
    coverage = summary["oracle_coverage"]
    projection = summary["projection"]
    lines = [
        "# Gan 2026 Clinical Frequency State Graph Diagnostics",
        "",
        "This is architecture and diagnostic work, not a benchmark result.",
        "",
        f"- Split: `{metadata['split']}`",
        f"- Split manifest: `{metadata['split_manifest']}`",
        f"- Rows: {metadata['row_count']}",
        f"- JSONL artifact: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Surface policy: {metadata['surface_note']}",
        "",
        "## Oracle Coverage",
        "",
        f"- Representable: {coverage['representable_count']}/{coverage['row_count']} "
        f"= {coverage['representable_rate']:.4f}",
        f"- Missing gold representability: {coverage['missing_count']}",
        "",
        "| Gold kind | Rows | Representable | Rate |",
        "| --- | ---: | ---: | ---: |",
    ]
    for kind, kind_summary in coverage["by_gold_kind"].items():
        lines.append(
            f"| {kind} | {kind_summary['total']} | {kind_summary['representable']} | "
            f"{kind_summary['representable_rate']:.4f} |"
        )
    lines.extend(
        [
            "",
            "## Projection Diagnostics",
            "",
            f"- Purist accuracy/F1: {projection['purist_accuracy']:.4f} / "
            f"{projection['purist_f1']:.4f}",
            f"- Pragmatic accuracy/F1: {projection['pragmatic_accuracy']:.4f} / "
            f"{projection['pragmatic_f1']:.4f}",
            f"- Exact normalized label matches: {projection['exact_label_matches']}/"
            f"{metadata['row_count']}",
            f"- Rows with graph errors: {projection['rows_with_graph_errors']}",
            f"- Rows with competing hypotheses: {projection['rows_with_competing_hypotheses']}",
            "",
            "## Missing Representability by Gold Kind",
            "",
            "| Gold kind | Missing rows |",
            "| --- | ---: |",
        ]
    )
    for kind, count in sorted(summary["missing_by_gold_kind"].items()):
        lines.append(f"| {kind} | {count} |")
    lines.extend(
        [
            "",
            "## Top Projection Misses",
            "",
            "| Source row | Gold | Projected | Gold kind | Node labels |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in _projection_misses(rows)[:12]:
        labels = ", ".join(label or kind for kind, label in row["graph_node_labels"])
        lines.append(
            f"| {row['source_row_index']} | {row['gold_normalized_label']} | "
            f"{row['projection']['final_label']} | {row['gold_label_kind']} | {labels} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _diagnostic_row(
    record: GanFrequencyRecord,
    *,
    split: str,
    split_manifest: str,
) -> dict[str, Any]:
    graph = build_state_graph(
        record.note_text,
        source_row_index=record.source_row_index,
        include_no_reference_fallback=True,
    )
    projection = project_graph_to_gan(graph)
    graph_errors = tuple(error for node in graph.nodes for error in node.graph_errors)
    representable = _gold_is_representable(record, graph_node_labels(graph))
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "row_ok": record.row_ok,
        "gold_label": record.gold_label,
        "gold_normalized_label": record.gold_normalized_label,
        "gold_label_kind": record.gold_label_kind.value,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "oracle_representable": representable,
        "graph": graph.model_dump(mode="json"),
        "graph_node_labels": [
            [kind.value, label] for kind, label in graph_node_labels(graph)
        ],
        "graph_errors": list(graph_errors),
        "projection": projection.model_dump(mode="json"),
        "projection_monthly_frequency": projection.monthly_frequency,
        "projection_exact_label_match": (
            projection.final_label == record.gold_normalized_label
        ),
    }


def _summary(
    rows: Sequence[Mapping[str, Any]],
    *,
    coverage: OracleCoverageSummary,
) -> dict[str, Any]:
    y_true = [float(row["gold_monthly_frequency"]) for row in rows]
    y_pred = [float(row["projection_monthly_frequency"]) for row in rows]
    purist = evaluate_predictions(y_true, y_pred, method="purist")
    pragmatic = evaluate_predictions(y_true, y_pred, method="pragmatic")
    missing_by_kind = Counter(
        str(row["gold_label_kind"]) for row in rows if not row["oracle_representable"]
    )
    return {
        "oracle_coverage": {
            **coverage.model_dump(mode="json"),
            "missing_count": len(coverage.missing_source_row_indices),
        },
        "missing_by_gold_kind": dict(sorted(missing_by_kind.items())),
        "projection": {
            "purist_accuracy": purist["micro"]["accuracy"],
            "purist_f1": purist["micro"]["f1"],
            "pragmatic_accuracy": pragmatic["micro"]["accuracy"],
            "pragmatic_f1": pragmatic["micro"]["f1"],
            "exact_label_matches": sum(
                bool(row["projection_exact_label_match"]) for row in rows
            ),
            "rows_with_graph_errors": sum(bool(row["graph_errors"]) for row in rows),
            "rows_with_competing_hypotheses": sum(
                bool(row["graph"]["competing_hypothesis_node_ids"]) for row in rows
            ),
        },
    }


def _projection_misses(rows: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [
        row
        for row in rows
        if row["projection"]["final_label"] != row["gold_normalized_label"]
    ]


def _gold_is_representable(
    record: GanFrequencyRecord,
    node_labels: Sequence[tuple[Any, str | None]],
) -> bool:
    if record.gold_label_kind.value in {"unknown", "no_reference", "seizure_free"}:
        return any(kind is record.gold_label_kind for kind, _label in node_labels)
    return any(label == record.gold_normalized_label for _kind, label in node_labels)


def _load_surface_records(args: argparse.Namespace) -> tuple[list[GanFrequencyRecord], str, str]:
    if args.surface == hard_cases.SYNTHETIC_SPLIT_NAME:
        cases = hard_cases.load_synthetic_hard_cases(args.hard_cases_jsonl)
        records = hard_cases.synthetic_records_from_cases(cases)
        return (
            records,
            hard_cases.SYNTHETIC_SPLIT_NAME,
            hard_cases.SYNTHETIC_SPLIT_MANIFEST,
        )

    records = load_records_for_split(args.split)
    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    return records, args.split, split_manifest


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run deterministic Gan 2026 clinical-frequency state-graph diagnostics."
    )
    parser.add_argument(
        "--surface",
        choices=("validation", hard_cases.SYNTHETIC_SPLIT_NAME),
        default="validation",
    )
    parser.add_argument("--split", choices=("validation",), default="validation")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--hard-cases-jsonl",
        type=Path,
        default=hard_cases.DEFAULT_HARD_CASES_JSONL_PATH,
    )
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    records, split, split_manifest = _load_surface_records(args)
    if args.limit is not None:
        records = records[: args.limit]
    surface_note = _surface_note(surface=args.surface, limit=args.limit)
    rows, metadata = run_state_graph_diagnostics(
        records,
        split=split,
        split_manifest=split_manifest,
        surface_note=surface_note,
    )
    write_jsonl_rows(rows, args.jsonl)
    write_state_graph_json(metadata, args.json)
    write_state_graph_report(
        rows,
        metadata,
        args.markdown,
        jsonl_path=args.jsonl,
        json_path=args.json,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))


def _surface_note(*, surface: str, limit: int | None) -> str:
    if surface == hard_cases.SYNTHETIC_SPLIT_NAME:
        return "Reviewed synthetic hard-case development panel; not validation or holdout."
    if limit in {25, 50}:
        return f"Validation prefix of {limit} rows for state-graph coverage diagnostics."
    return "Validation-only state-graph diagnostic surface."


if __name__ == "__main__":
    main()
