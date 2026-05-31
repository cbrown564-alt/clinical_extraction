from __future__ import annotations

import argparse
import csv
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.error_analysis import (
    RowErrorRecord,
    build_row_error_table,
    summarize_row_errors,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    evaluate_frequency_records,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    Gan2026PipelineV1,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    RuleGroup,
)

CHANGED_ROW_FIELDNAMES = (
    "condition",
    "source_row_index",
    "baseline_correct",
    "ablated_correct",
    "baseline_prediction_label",
    "ablated_prediction_label",
    "gold_label",
    "baseline_prediction_category",
    "ablated_prediction_category",
    "gold_category",
    "baseline_error_type",
    "ablated_error_type",
    "baseline_selected_evidence_type",
    "ablated_selected_evidence_type",
)


@dataclass(frozen=True)
class ConditionResult:
    name: str
    disabled_group: RuleGroup | None
    rows: list[RowErrorRecord]
    summary: dict[str, Any]


def run_ablation_analysis(
    *,
    split: str = "validation",
    data_path: Path = DEFAULT_DATA_PATH,
    manifest_path: Path = DEFAULT_SPLIT_MANIFEST_PATH,
) -> list[ConditionResult]:
    records = load_records_for_split(split, data_path, manifest_path)
    baseline_rows = build_row_error_table(records, pipeline=Gan2026PipelineV1())
    results = [
        ConditionResult(
            name="baseline_all_groups",
            disabled_group=None,
            rows=baseline_rows,
            summary=summarize_row_errors(baseline_rows),
        )
    ]

    for group in RuleGroup:
        enabled_groups = frozenset(candidate for candidate in RuleGroup if candidate is not group)
        ablated_rows = build_row_error_table(
            records,
            pipeline=Gan2026PipelineV1(
                ablation_config=AblationConfig(enabled_groups=enabled_groups)
            ),
        )
        results.append(
            ConditionResult(
                name=f"disable_{group.value}",
                disabled_group=group,
                rows=ablated_rows,
                summary=summarize_row_errors(ablated_rows),
            )
        )
    return results


def write_changed_rows_csv(results: Sequence[ConditionResult], path: Path) -> None:
    baseline = results[0]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CHANGED_ROW_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for result in results[1:]:
            for row in changed_rows(baseline.rows, result.rows):
                writer.writerow(
                    {
                        "condition": result.name,
                        "source_row_index": row["ablated"].source_row_index,
                        "baseline_correct": row["baseline"].correct,
                        "ablated_correct": row["ablated"].correct,
                        "baseline_prediction_label": row["baseline"].prediction_label,
                        "ablated_prediction_label": row["ablated"].prediction_label,
                        "gold_label": row["ablated"].gold_label,
                        "baseline_prediction_category": row["baseline"].prediction_category,
                        "ablated_prediction_category": row["ablated"].prediction_category,
                        "gold_category": row["ablated"].gold_category,
                        "baseline_error_type": row["baseline"].error_type,
                        "ablated_error_type": row["ablated"].error_type,
                        "baseline_selected_evidence_type": row[
                            "baseline"
                        ].selected_evidence_type,
                        "ablated_selected_evidence_type": row["ablated"].selected_evidence_type,
                    }
                )


def changed_rows(
    baseline_rows: Sequence[RowErrorRecord],
    ablated_rows: Sequence[RowErrorRecord],
) -> list[dict[str, RowErrorRecord]]:
    changes: list[dict[str, RowErrorRecord]] = []
    for baseline, ablated in zip(baseline_rows, ablated_rows, strict=True):
        if (
            baseline.prediction_label != ablated.prediction_label
            or baseline.prediction_category != ablated.prediction_category
            or baseline.correct != ablated.correct
            or baseline.selected_evidence != ablated.selected_evidence
        ):
            changes.append({"baseline": baseline, "ablated": ablated})
    return sorted(
        changes,
        key=lambda row: (
            row["baseline"].correct == row["ablated"].correct,
            row["baseline"].correct,
            row["ablated"].source_row_index,
        ),
    )


def write_markdown_report(
    results: Sequence[ConditionResult],
    path: Path,
    *,
    split: str,
    manifest_path: Path,
    changed_rows_csv: Path,
) -> None:
    manifest = load_split_manifest(manifest_path)
    manifest_version = str(manifest.get("manifest_version", "gan2026_split_v1"))
    baseline = results[0]
    lines = [
        f"# Gan 2026 V1 {split.title()} Deterministic Rule Ablation",
        "",
        "Date: 2026-05-31",
        "",
        "This is a validation-split development artifact, not a held-out benchmark result.",
        "The frozen deterministic V1 test holdout remains 0.7600 Purist micro F1/accuracy "
        "and is included only as prior context.",
        "",
        f"Split manifest: `{manifest_path}` (`{manifest_version}`)",
        f"Changed-row CSV: `{changed_rows_csv}`",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: disabling clinically portable and dataset-specific deterministic rule groups "
        "will expose which parts of V1 validation performance depend on each rule family.",
        "",
        "Minimal change: run the frozen V1 extractor on validation with one `RuleGroup` disabled "
        "at a time. No deterministic recall rules, scorer policy, split policy, or test rows are "
        "changed.",
        "",
        "Data surface: Gan 2026 `validation` split; `row_ok=False` rows included per "
        "project policy.",
        "",
        "Scorer: Gan-compatible Purist micro F1 as the primary metric, Pragmatic micro F1 as "
        "a side-car. Evidence validity is exact selected-evidence substring validity.",
        "",
        "## Ablation Table",
        "",
        "| Condition | Disabled group | Changed rows | Correct | Evidence valid | Purist micro "
        "F1 | Pragmatic micro F1 | Unknown/no-reference predictions |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        changed_count = 0 if result is baseline else len(changed_rows(baseline.rows, result.rows))
        purist = result.summary["metrics"]["micro"]["f1"]
        pragmatic = _pragmatic_micro_f1(result.rows)
        unknown_count = _prediction_kind_count(result.rows, "unknown")
        no_reference_count = _prediction_kind_count(result.rows, "no_reference")
        disabled_group = result.disabled_group.value if result.disabled_group else "none"
        lines.append(
            f"| {result.name} | {disabled_group} | {changed_count} | "
            f"{result.summary['correct_count']} / {result.summary['row_count']} | "
            f"{result.summary['evidence_valid_count']} / {result.summary['row_count']} | "
            f"{purist:.4f} | {pragmatic:.4f} | {unknown_count + no_reference_count} |"
        )

    lines.extend(
        [
            "",
            "## Prediction State Distribution",
            "",
            "| Condition | Frequency | Seizure-free | Unknown | No-reference | Unresolved "
            "multiple |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for result in results:
        counts = Counter(row.prediction_kind for row in result.rows)
        lines.append(
            f"| {result.name} | {counts['frequency']} | {counts['seizure_free']} | "
            f"{counts['unknown']} | {counts['no_reference']} | {counts['unresolved_multiple']} |"
        )

    lines.extend(["", "## Top Changed Rows", ""])
    for result in results[1:]:
        changes = changed_rows(baseline.rows, result.rows)
        lines.extend(
            [
                f"### {result.name}",
                "",
                f"Changed rows: {len(changes)}",
                "",
                "| Row | Baseline correct | Ablated correct | Gold category | Baseline "
                "prediction | Ablated prediction |",
                "| ---: | --- | --- | --- | --- | --- |",
            ]
        )
        for change in changes[:12]:
            baseline_row = change["baseline"]
            ablated_row = change["ablated"]
            lines.append(
                f"| {ablated_row.source_row_index} | {baseline_row.correct} | "
                f"{ablated_row.correct} | {ablated_row.gold_category} | "
                f"{baseline_row.prediction_category} / {baseline_row.prediction_label} | "
                f"{ablated_row.prediction_category} / {ablated_row.prediction_label} |"
            )
        if not changes:
            lines.append("| - | - | - | - | - | - |")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _pragmatic_micro_f1(rows: Sequence[RowErrorRecord]) -> float:
    scored_rows = [
        {
            "gold_monthly_frequency": row.gold_monthly_frequency,
            "prediction": row.prediction_monthly_frequency,
        }
        for row in rows
    ]
    return evaluate_frequency_records(scored_rows, prediction_key="prediction", method="pragmatic")[
        "micro"
    ]["f1"]


def _prediction_kind_count(rows: Sequence[RowErrorRecord], kind: str) -> int:
    return sum(row.prediction_kind == kind for row in rows)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Generate Gan 2026 validation deterministic-rule ablation report."
    )
    parser.add_argument("--split", default="validation", choices=("train", "validation"))
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_SPLIT_MANIFEST_PATH)
    parser.add_argument(
        "--markdown",
        type=Path,
        default=Path("experiments/gan2026_v1_validation_ablation_2026-05-31.md"),
    )
    parser.add_argument(
        "--changed-rows-csv",
        type=Path,
        default=Path("experiments/gan2026_v1_validation_ablation_changed_rows_2026-05-31.csv"),
    )
    args = parser.parse_args(argv)

    results = run_ablation_analysis(
        split=args.split,
        data_path=args.data_path,
        manifest_path=args.manifest_path,
    )
    write_changed_rows_csv(results, args.changed_rows_csv)
    write_markdown_report(
        results,
        args.markdown,
        split=args.split,
        manifest_path=args.manifest_path,
        changed_rows_csv=args.changed_rows_csv,
    )


if __name__ == "__main__":
    main()
