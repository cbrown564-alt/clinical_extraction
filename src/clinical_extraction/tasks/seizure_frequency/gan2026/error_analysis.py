from __future__ import annotations

import argparse
import csv
from collections import Counter
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.pipeline import PipelineResult
from clinical_extraction.core.schemas import FinalExtraction
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    convert_to_categories,
    evaluate_frequency_records,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1


class ErrorSlice(BaseModel):
    name: str
    count: int
    notes: str = ""


class RowErrorRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_row_index: int
    row_ok: bool
    correct: bool
    error_type: str
    gold_label: str
    gold_kind: str
    gold_category: str
    gold_monthly_frequency: float
    prediction_label: str
    prediction_kind: str
    prediction_category: str
    prediction_monthly_frequency: float
    evidence_valid: bool
    candidate_count: int
    selected_evidence: str
    gold_reference: str
    rationale: str


ROW_ERROR_FIELDNAMES = tuple(RowErrorRecord.model_fields)


def build_row_error_table(
    records: Sequence[GanFrequencyRecord],
    pipeline: Gan2026PipelineV1 | None = None,
    method: str = "purist",
) -> list[RowErrorRecord]:
    extractor = pipeline or Gan2026PipelineV1()
    rows: list[RowErrorRecord] = []
    for record in records:
        result = extractor.run(record)
        rows.append(build_row_error_record(record, result, method=method))
    return rows


def build_row_error_record(
    record: GanFrequencyRecord,
    result: PipelineResult[FinalExtraction],
    method: str = "purist",
) -> RowErrorRecord:
    final_selection = _final_selection(result)
    candidate_count = len(result.diagnostics.get("candidate_events", []))
    gold_category = convert_to_categories([record.gold_monthly_frequency], method=method)[0]
    prediction_monthly_frequency = float(final_selection["monthly_frequency"])
    prediction_category = convert_to_categories([prediction_monthly_frequency], method=method)[0]
    prediction_kind = str(final_selection["final_kind"])
    correct = gold_category == prediction_category

    return RowErrorRecord(
        source_row_index=record.source_row_index,
        row_ok=record.row_ok,
        correct=correct,
        error_type=_classify_error(
            correct=correct,
            gold_kind=str(record.gold_label_kind),
            prediction_kind=prediction_kind,
            gold_category=gold_category,
            prediction_category=prediction_category,
        ),
        gold_label=record.gold_label,
        gold_kind=str(record.gold_label_kind),
        gold_category=gold_category,
        gold_monthly_frequency=record.gold_monthly_frequency,
        prediction_label=str(final_selection["final_label"]),
        prediction_kind=prediction_kind,
        prediction_category=prediction_category,
        prediction_monthly_frequency=prediction_monthly_frequency,
        evidence_valid=bool(result.diagnostics.get("evidence_valid", False)),
        candidate_count=candidate_count,
        selected_evidence=str(final_selection["evidence"]),
        gold_reference=record.gold_reference,
        rationale=str(final_selection["rationale"]),
    )


def summarize_row_errors(rows: Sequence[RowErrorRecord]) -> dict[str, Any]:
    scored_rows = [
        {
            "gold_monthly_frequency": row.gold_monthly_frequency,
            "prediction": row.prediction_monthly_frequency,
        }
        for row in rows
    ]
    return {
        "row_count": len(rows),
        "correct_count": sum(row.correct for row in rows),
        "evidence_valid_count": sum(row.evidence_valid for row in rows),
        "metrics": evaluate_frequency_records(scored_rows, prediction_key="prediction"),
        "error_type_counts": Counter(row.error_type for row in rows),
        "gold_kind_counts": Counter(row.gold_kind for row in rows),
        "prediction_kind_counts": Counter(row.prediction_kind for row in rows),
        "confusion_counts": Counter(
            (row.gold_category, row.prediction_category) for row in rows if not row.correct
        ),
    }


def write_row_error_csv(rows: Sequence[RowErrorRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROW_ERROR_FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow(_csv_row(row))


def write_row_error_markdown(
    rows: Sequence[RowErrorRecord],
    path: Path,
    *,
    split: str,
    csv_path: Path,
) -> None:
    summary = summarize_row_errors(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        _markdown_report(rows, summary, split=split, csv_path=csv_path),
        encoding="utf-8",
    )


def _classify_error(
    *,
    correct: bool,
    gold_kind: str,
    prediction_kind: str,
    gold_category: str,
    prediction_category: str,
) -> str:
    if correct and gold_kind != prediction_kind:
        return "scorer_correct_semantic_mismatch"
    if correct:
        return "correct"
    if gold_kind == "frequency" and prediction_kind in {"no_reference", "unknown"}:
        return "missed_frequency_evidence"
    if gold_kind == "seizure_free" and prediction_kind in {"no_reference", "unknown"}:
        return "missed_seizure_free_evidence"
    if gold_kind == "frequency" and prediction_kind == "seizure_free":
        return "frequency_predicted_seizure_free"
    if gold_kind != "frequency" and prediction_kind == "frequency":
        return "overpredicted_frequency"
    if gold_category != prediction_category:
        return "wrong_frequency_bucket"
    return "other"


def _final_selection(result: PipelineResult[FinalExtraction]) -> dict[str, Any]:
    final_selection = result.diagnostics.get("final_selection")
    if not isinstance(final_selection, dict):
        raise ValueError("Pipeline diagnostics did not include final_selection")
    return final_selection


def _csv_row(row: RowErrorRecord) -> dict[str, Any]:
    values = row.model_dump(mode="json")
    for field in ("selected_evidence", "gold_reference", "rationale"):
        values[field] = " ".join(str(values[field]).split())
    return values


def _markdown_report(
    rows: Sequence[RowErrorRecord],
    summary: dict[str, Any],
    *,
    split: str,
    csv_path: Path,
) -> str:
    metrics = summary["metrics"]
    lines = [
        f"# Gan 2026 V1 {split.title()} Error Analysis",
        "",
        "Date: 2026-05-31",
        "",
        "This is a validation-split development artifact, not a held-out benchmark result.",
        "",
        f"CSV: `{csv_path}`",
        "",
        "## Metrics",
        "",
        f"Rows: {summary['row_count']}",
        "",
        "| Average | Precision | Recall | F1 | Accuracy |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for average in ("micro", "macro", "weighted"):
        metric = metrics[average]
        lines.append(
            f"| {average} | {metric['precision']:.4f} | {metric['recall']:.4f} | "
            f"{metric['f1']:.4f} | {metric['accuracy']:.4f} |"
        )

    lines.extend(
        [
            "",
            f"Evidence validity: {summary['evidence_valid_count']} / {summary['row_count']}",
            "",
            "## Error Types",
            "",
            "| Error type | Count |",
            "| --- | ---: |",
        ]
    )
    lines.extend(_counter_rows(summary["error_type_counts"]))
    lines.extend(
        [
            "",
            "## Gold Kinds",
            "",
            "| Gold kind | Count |",
            "| --- | ---: |",
        ]
    )
    lines.extend(_counter_rows(summary["gold_kind_counts"]))
    lines.extend(
        [
            "",
            "## Prediction Kinds",
            "",
            "| Prediction kind | Count |",
            "| --- | ---: |",
        ]
    )
    lines.extend(_counter_rows(summary["prediction_kind_counts"]))
    lines.extend(
        [
            "",
            "## Top Incorrect Category Pairs",
            "",
            "| Gold category | Prediction category | Count |",
            "| --- | --- | ---: |",
        ]
    )
    for (gold_category, prediction_category), count in summary["confusion_counts"].most_common(12):
        lines.append(f"| {gold_category} | {prediction_category} | {count} |")

    lines.extend(
        [
            "",
            "## First High-Priority Rows",
            "",
            "| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in _priority_rows(rows)[:20]:
        lines.append(
            f"| {row.source_row_index} | {row.error_type} | {row.gold_kind} | "
            f"{row.prediction_kind} | {row.gold_category} | {row.prediction_category} |"
        )
    lines.append("")
    return "\n".join(lines)


def _counter_rows(counter: Counter[str]) -> list[str]:
    return [f"| {name} | {count} |" for name, count in counter.most_common()]


def _priority_rows(rows: Iterable[RowErrorRecord]) -> list[RowErrorRecord]:
    priorities = {
        "missed_frequency_evidence": 0,
        "missed_seizure_free_evidence": 1,
        "frequency_predicted_seizure_free": 2,
        "wrong_frequency_bucket": 3,
    }
    return sorted(
        (row for row in rows if row.error_type != "correct"),
        key=lambda row: (priorities.get(row.error_type, 99), row.source_row_index),
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Gan 2026 row-level error analysis.")
    parser.add_argument("--split", default="validation", choices=("train", "validation", "test"))
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_SPLIT_MANIFEST_PATH)
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--markdown", type=Path, default=None)
    args = parser.parse_args(argv)

    csv_path = args.csv or Path(f"experiments/gan2026_v1_{args.split}_error_rows_2026-05-31.csv")
    markdown_path = args.markdown or Path(
        f"experiments/gan2026_v1_{args.split}_error_analysis_2026-05-31.md"
    )
    records = load_records_for_split(args.split, args.data_path, args.manifest_path)
    rows = build_row_error_table(records)
    write_row_error_csv(rows, csv_path)
    write_row_error_markdown(rows, markdown_path, split=args.split, csv_path=csv_path)


if __name__ == "__main__":
    main()
