from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.ablation_analysis import (
    CHANGED_ROW_FIELDNAMES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import Gan2026PipelineV1

DEFAULT_CHANGED_ROWS_PATH = Path(
    "experiments/gan2026_v1_validation_ablation_changed_rows_2026-05-31.csv"
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.jsonl")
DEFAULT_MARKDOWN_PATH = Path("experiments/gan2026_v1_prompt_adjudicator_devset_2026-05-31.md")


class AblationChangedRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    condition: str
    source_row_index: int
    baseline_correct: bool
    ablated_correct: bool
    baseline_prediction_label: str
    ablated_prediction_label: str
    gold_label: str
    baseline_prediction_category: str
    ablated_prediction_category: str
    gold_category: str
    baseline_error_type: str
    ablated_error_type: str
    baseline_selected_evidence_type: str
    ablated_selected_evidence_type: str


def load_changed_rows(path: Path) -> list[AblationChangedRow]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_fields = set(CHANGED_ROW_FIELDNAMES) - set(reader.fieldnames or ())
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"Changed-row CSV is missing required fields: {missing}")
        return [_changed_row_from_csv(row) for row in reader]


def select_development_rows(
    rows: Sequence[AblationChangedRow],
    *,
    max_examples: int = 16,
    max_per_condition: int = 5,
) -> list[AblationChangedRow]:
    """Select compact adjudicator examples from changed rows.

    Baseline-wrong/ablation-correct rows expose deterministic overreach and are
    the primary prompt-development target. Baseline-correct/ablation-wrong rows
    are included as controls so a future adjudicator does not simply suppress
    every deterministic rule family that appears in an overreach example.
    """

    selected: list[AblationChangedRow] = []
    condition_counts: Counter[str] = Counter()
    seen_keys: set[tuple[str, str, str, str]] = set()

    for group in (
        _sorted_candidate_rows(_overreach_rows(rows)),
        _sorted_candidate_rows(_support_rows(rows)),
    ):
        for row in group:
            if len(selected) >= max_examples:
                break
            if condition_counts[row.condition] >= max_per_condition:
                continue
            diversity_key = (
                row.condition,
                row.baseline_error_type,
                row.gold_category,
                row.baseline_selected_evidence_type,
            )
            if diversity_key in seen_keys:
                continue
            selected.append(row)
            condition_counts[row.condition] += 1
            seen_keys.add(diversity_key)
        if len(selected) >= max_examples:
            break

    if len(selected) < max_examples:
        selected_ids = {(row.condition, row.source_row_index) for row in selected}
        for row in _sorted_candidate_rows(rows):
            if len(selected) >= max_examples:
                break
            if condition_counts[row.condition] >= max_per_condition:
                continue
            row_id = (row.condition, row.source_row_index)
            if row_id in selected_ids:
                continue
            selected.append(row)
            condition_counts[row.condition] += 1
            selected_ids.add(row_id)

    return selected


def build_development_examples(
    selected_rows: Sequence[AblationChangedRow],
    *,
    split: str = "validation",
    data_path: Path = DEFAULT_DATA_PATH,
    manifest_path: Path = DEFAULT_SPLIT_MANIFEST_PATH,
) -> list[dict[str, Any]]:
    records = {
        record.source_row_index: record
        for record in load_records_for_split(
            split,
            data_path=data_path,
            manifest_path=manifest_path,
        )
    }
    manifest = load_split_manifest(manifest_path)
    manifest_version = str(manifest.get("manifest_version", "gan2026_split_v1"))
    pipeline = Gan2026PipelineV1()

    examples: list[dict[str, Any]] = []
    for row in selected_rows:
        record = records[row.source_row_index]
        result = pipeline.run(record)
        diagnostics = result.diagnostics
        examples.append(
            {
                "example_id": f"gan2026-{split}-{row.source_row_index}-{row.condition}",
                "task": "final_selection_adjudication",
                "split": split,
                "split_manifest": manifest_version,
                "source_row_index": row.source_row_index,
                "lesson_type": _lesson_type(row),
                "ablation_condition": row.condition,
                "row_ok": record.row_ok,
                "input": {
                    "note_text": record.note_text,
                    "candidate_events": _candidate_events(diagnostics),
                    "normalized_events": _normalized_events(diagnostics),
                    "deterministic_final_selection": diagnostics["final_selection"],
                },
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_category": row.gold_category,
                    "gold_reference": _compact_text(record.gold_reference),
                    "baseline_prediction_label": row.baseline_prediction_label,
                    "baseline_prediction_category": row.baseline_prediction_category,
                    "ablated_prediction_label": row.ablated_prediction_label,
                    "ablated_prediction_category": row.ablated_prediction_category,
                    "baseline_correct": row.baseline_correct,
                    "ablated_correct": row.ablated_correct,
                    "baseline_error_type": row.baseline_error_type,
                    "ablated_error_type": row.ablated_error_type,
                },
                "adjudicator_target": {
                    "decision_record_fields": [
                        "assertion_status",
                        "temporality",
                        "seizure_or_event_target",
                        "window",
                        "normalized_rate",
                        "uncertainty",
                        "selected_event_ids",
                        "final_label",
                    ],
                    "development_question": _development_question(row),
                },
            }
        )
    return examples


def write_jsonl(examples: Sequence[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(json.dumps(example, ensure_ascii=False, sort_keys=True) + "\n")


def write_markdown_report(
    examples: Sequence[dict[str, Any]],
    path: Path,
    *,
    changed_rows_path: Path,
    jsonl_path: Path,
    split: str,
    manifest_path: Path,
) -> None:
    manifest = load_split_manifest(manifest_path)
    manifest_version = str(manifest.get("manifest_version", "gan2026_split_v1"))
    lesson_counts = Counter(example["lesson_type"] for example in examples)
    condition_counts = Counter(example["ablation_condition"] for example in examples)
    lines = [
        "# Gan 2026 V1 Prompt Adjudicator Development Set",
        "",
        "Date: 2026-05-31",
        "",
        "This is a validation-only development artifact. It must not be treated as a held-out "
        "benchmark result and does not inspect locked test-row failures.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: deterministic V1 errors that become correct when a rule family is disabled "
        "are useful seed examples for an LLM/DSPy final-selection adjudicator. The adjudicator "
        "should explain assertion status, temporality, seizure/event target, window, normalized "
        "rate, and uncertainty before accepting or overriding the deterministic final choice.",
        "",
        "Minimal change: no scoring, rules, normalization, or prompts are changed. This step only "
        "mines existing validation ablation rows and packages deterministic V1 candidate "
        "diagnostics as prompt-development examples.",
        "",
        f"Data surface: Gan 2026 `{split}` split using `{manifest_version}`.",
        "Scorer policy: Gan-compatible Purist categories are carried through from the existing "
        "ablation artifact; no new evaluation is performed.",
        "",
        f"Source changed rows: `{changed_rows_path}`",
        f"Development JSONL: `{jsonl_path}`",
        "",
        "## Selection Policy",
        "",
        "- Prioritize rows where deterministic V1 is wrong but an ablated condition is correct.",
        "- Add support/control rows where deterministic V1 is correct but an ablation breaks it.",
        "- Cap examples per ablation condition and diversify by error type, gold category, and "
        "selected-evidence type.",
        "",
        "## Set Summary",
        "",
        f"- Examples: {len(examples)}",
        f"- Lesson types: {_format_counter(lesson_counts)}",
        f"- Conditions: {_format_counter(condition_counts)}",
        "",
        "## Rows",
        "",
        "| Row | Lesson | Condition | Baseline | Ablated | Gold | Question |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for example in examples:
        reference = example["reference"]
        question = example["adjudicator_target"]["development_question"]
        lines.append(
            f"| {example['source_row_index']} | {example['lesson_type']} | "
            f"{example['ablation_condition']} | "
            f"{reference['baseline_prediction_category']} / "
            f"{reference['baseline_prediction_label']} | "
            f"{reference['ablated_prediction_category']} / "
            f"{reference['ablated_prediction_label']} | "
            f"{reference['gold_category']} / {reference['gold_label']} | {question} |"
        )
    lines.extend(
        [
            "",
            "## First Reasoning Experiment Scaffold",
            "",
            "Use each JSONL record as one DSPy/example input. A first adjudicator can receive "
            "`candidate_events`, `normalized_events`, and `deterministic_final_selection`, then "
            "produce the decision-record fields listed in `adjudicator_target` plus a "
            "Gan-compatible `final_label`. Compare the adjudicated label to `reference.gold_label` "
            "on this development set only before running any broader validation pass.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _changed_row_from_csv(row: dict[str, str]) -> AblationChangedRow:
    return AblationChangedRow(
        condition=row["condition"],
        source_row_index=int(row["source_row_index"]),
        baseline_correct=_parse_bool(row["baseline_correct"]),
        ablated_correct=_parse_bool(row["ablated_correct"]),
        baseline_prediction_label=row["baseline_prediction_label"],
        ablated_prediction_label=row["ablated_prediction_label"],
        gold_label=row["gold_label"],
        baseline_prediction_category=row["baseline_prediction_category"],
        ablated_prediction_category=row["ablated_prediction_category"],
        gold_category=row["gold_category"],
        baseline_error_type=row["baseline_error_type"],
        ablated_error_type=row["ablated_error_type"],
        baseline_selected_evidence_type=row["baseline_selected_evidence_type"],
        ablated_selected_evidence_type=row["ablated_selected_evidence_type"],
    )


def _parse_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"Expected boolean string, got {value!r}")


def _overreach_rows(rows: Iterable[AblationChangedRow]) -> list[AblationChangedRow]:
    return [row for row in rows if not row.baseline_correct and row.ablated_correct]


def _support_rows(rows: Iterable[AblationChangedRow]) -> list[AblationChangedRow]:
    return [row for row in rows if row.baseline_correct and not row.ablated_correct]


def _sorted_candidate_rows(rows: Iterable[AblationChangedRow]) -> list[AblationChangedRow]:
    return sorted(
        rows,
        key=lambda row: (
            row.condition,
            row.baseline_error_type,
            row.gold_category,
            row.source_row_index,
        ),
    )


def _lesson_type(row: AblationChangedRow) -> str:
    if not row.baseline_correct and row.ablated_correct:
        return "deterministic_overreach"
    if row.baseline_correct and not row.ablated_correct:
        return "deterministic_support_control"
    return "behavior_change"


def _candidate_events(diagnostics: Mapping[str, Any]) -> list[dict[str, Any]]:
    normalized_by_id = {
        event["event_id"]: event for event in diagnostics.get("normalized_events", [])
    }
    events = []
    for event in diagnostics.get("candidate_events", []):
        normalized = normalized_by_id.get(event.get("event_id"), {})
        events.append(
            {
                "event_id": event.get("event_id"),
                "kind": event.get("kind"),
                "raw_value": event.get("raw_value"),
                "evidence": _compact_text(str(event.get("evidence", ""))),
                "rule_id": event.get("rule_id"),
                "rule_group": event.get("rule_group"),
                "portability": event.get("portability"),
                "normalized_label": normalized.get("normalized_label"),
                "semantic_kind": normalized.get("semantic_kind"),
                "monthly_frequency": normalized.get("monthly_frequency"),
            }
        )
    return events


def _normalized_events(diagnostics: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "event_id": event.get("event_id"),
            "normalized_label": event.get("normalized_label"),
            "semantic_kind": event.get("semantic_kind"),
            "monthly_frequency": event.get("monthly_frequency"),
            "validation_errors": event.get("validation_errors", []),
        }
        for event in diagnostics.get("normalized_events", [])
    ]


def _development_question(row: AblationChangedRow) -> str:
    if row.baseline_error_type == "wrong_frequency_bucket":
        return (
            "Which candidate is the clinically current seizure-frequency rate, and which rate "
            "should be rejected as a distractor or lower-priority window?"
        )
    if row.baseline_error_type == "overpredicted_frequency":
        return (
            "Does the selected frequency evidence actually describe the patient's current "
            "seizures, or should the answer remain unknown/no-reference?"
        )
    if row.ablated_error_type == "missed_frequency_evidence":
        return (
            "Why is the deterministic frequency candidate necessary, and what evidence supports "
            "keeping it?"
        )
    if row.ablated_error_type == "frequency_predicted_seizure_free":
        return (
            "How should a seizure-free assertion be reconciled against explicit current "
            "frequency evidence?"
        )
    return (
        "Should the deterministic final selection be accepted or overridden after reviewing "
        "assertion, temporality, target, window, rate, and uncertainty?"
    )


def _compact_text(value: str) -> str:
    return " ".join(value.split())


def _format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"{key}={counter[key]}" for key in sorted(counter))


def summarize_selection(rows: Sequence[AblationChangedRow]) -> dict[str, dict[str, int]]:
    buckets: dict[str, defaultdict[str, int]] = {
        "lesson_type": defaultdict(int),
        "condition": defaultdict(int),
        "baseline_error_type": defaultdict(int),
    }
    for row in rows:
        buckets["lesson_type"][_lesson_type(row)] += 1
        buckets["condition"][row.condition] += 1
        buckets["baseline_error_type"][row.baseline_error_type] += 1
    return {name: dict(values) for name, values in buckets.items()}


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Mine Gan 2026 validation ablation rows into prompt/adjudicator examples."
    )
    parser.add_argument("--split", default="validation", choices=("train", "validation"))
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_SPLIT_MANIFEST_PATH)
    parser.add_argument("--changed-rows", type=Path, default=DEFAULT_CHANGED_ROWS_PATH)
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MARKDOWN_PATH)
    parser.add_argument("--max-examples", type=int, default=16)
    parser.add_argument("--max-per-condition", type=int, default=5)
    args = parser.parse_args(argv)

    changed_rows = load_changed_rows(args.changed_rows)
    selected_rows = select_development_rows(
        changed_rows,
        max_examples=args.max_examples,
        max_per_condition=args.max_per_condition,
    )
    examples = build_development_examples(
        selected_rows,
        split=args.split,
        data_path=args.data_path,
        manifest_path=args.manifest_path,
    )
    write_jsonl(examples, args.jsonl)
    write_markdown_report(
        examples,
        args.markdown,
        changed_rows_path=args.changed_rows,
        jsonl_path=args.jsonl,
        split=args.split,
        manifest_path=args.manifest_path,
    )


if __name__ == "__main__":
    main()
