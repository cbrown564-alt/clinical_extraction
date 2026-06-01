"""Markdown report writers for Gan 2026 hybrid adjudicator runs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    llm_model_metadata_lines,
    write_markdown_report,
)


def write_hybrid_rules_candidates_llm_adjudicator_report(
    records: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Hybrid Rules-Candidates LLM Adjudicator",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation development artifact unless the split is explicitly `test` "
        "and the candidate was frozen before evaluation. It is not a benchmark claim.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: deterministic V1 can serve as a high-recall candidate generator, "
        "while an LLM adjudicator makes the prediction-bearing semantic selection.",
        "",
        "Prediction-bearing component: LLM final-selection adjudicator over unscored "
        "deterministic candidate evidence. Deterministic code generates candidate labels, "
        "validates output shape, applies existing label repair, and scores.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} rows.",
        (
            f"Escalation reason: {metadata['escalation_reason']}"
            if metadata.get("escalation_reason")
            else "Escalation reason: not applicable for this run size."
        ),
        "",
        "## Model And Prompt Metadata",
        "",
        *llm_model_metadata_lines(
            metadata,
            jsonl_path,
            model_role="final-selection adjudicator",
            deterministic_rule_configuration=(
                "frozen V1 candidate generator before LLM adjudication."
            ),
            summary=summary,
            leading_lines=[
                f"- Architecture: `{metadata['architecture']}`",
                f"- Claim type: `{metadata['claim_type']}`",
            ],
        ),
        "",
        "## Summary",
        "",
        f"- Decision records: {summary['decision_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Candidate-set Purist recall proxy: {summary['candidate_purist_recall_rate']:.4f} "
        f"({summary['candidate_purist_recall']} / {summary['examples']})",
        f"- Deterministic top Purist: {summary['deterministic_purist_accuracy']:.4f} "
        f"({summary['deterministic_purist_correct']} / {summary['examples']})",
        f"- Deterministic top Pragmatic: {summary['deterministic_pragmatic_accuracy']:.4f} "
        f"({summary['deterministic_pragmatic_correct']} / {summary['examples']})",
        f"- Adjudicator Purist: {summary['adjudicator_purist_accuracy']:.4f} "
        f"({summary['adjudicator_purist_correct']} / {summary['examples']})",
        f"- Adjudicator Pragmatic: {summary['adjudicator_pragmatic_accuracy']:.4f} "
        f"({summary['adjudicator_pragmatic_correct']} / {summary['examples']})",
        f"- Changed final labels: {summary['changed_final_labels']}",
        "- Deterministic-wrong to adjudicator-correct: "
        f"{summary['deterministic_wrong_to_adjudicator_correct']}",
        "- Deterministic-correct to adjudicator-wrong: "
        f"{summary['deterministic_correct_to_adjudicator_wrong']}",
        "",
        "## Rows",
        "",
        "| Row | Candidate recall | Deterministic | Adjudicator | Gold | "
        "Det Purist | Adj Purist | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        deterministic = (record.get("scores") or {}).get("deterministic_top") or {}
        adjudicator = (record.get("scores") or {}).get("adjudicator") or {}
        recall = (record.get("candidate_recall") or {}).get("purist_category_recalled")
        notes = "; ".join(str(error) for error in record.get("parse_errors") or [])
        if record.get("call_error"):
            notes = f"{notes}; {record['call_error']}" if notes else str(record["call_error"])
        lines.append(
            f"| {record['source_row_index']} | {_yes_no(recall)} | "
            f"{deterministic.get('final_label', '')} | "
            f"{adjudicator.get('final_label', '') if adjudicator else ''} | "
            f"{record['reference']['gold_label']} | "
            f"{_yes_no(deterministic.get('purist_correct'))} | "
            f"{_yes_no(adjudicator.get('purist_correct')) if adjudicator else ''} | "
            f"{notes} |"
        )
    write_markdown_report(path, lines)


def write_adjudicator_report(
    records: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    devset_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 DSPy Final-Selection Adjudicator Dev-Set Run",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation-only prompt/adjudicator development run over the 16-example "
        "dev set mined from validation ablations. It is not a benchmark result and does "
        "not inspect locked test-row failures.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: a DSPy final-selection adjudicator can use deterministic V1 candidate "
        "diagnostics to reject unsupported high-priority candidates while preserving "
        "necessary deterministic evidence.",
        "",
        "Minimal change: add the adjudicator program and run harness only. Deterministic "
        "candidate extraction, normalization, scoring, split policy, and repair rules are "
        "unchanged.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} examples from `{devset_path}`.",
        "Scorer policy: compare final labels to carried gold labels with Gan-compatible "
        "Purist categories first, Pragmatic categories as a side-car.",
        "",
        "## Model And Prompt Metadata",
        "",
        *llm_model_metadata_lines(
            metadata,
            jsonl_path,
            model_role="final-selection adjudicator",
            deterministic_rule_configuration="frozen V1 diagnostics from the dev-set JSONL",
        ),
        "",
        "## Summary",
        "",
        f"- Decision records: {summary['decision_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Deterministic repair notes: {summary['repair_notes']}",
        f"- Purist dev-set accuracy: {summary['purist_accuracy']:.4f} "
        f"({summary['purist_correct']} / {summary['examples']})",
        f"- Pragmatic dev-set accuracy: {summary['pragmatic_accuracy']:.4f} "
        f"({summary['pragmatic_correct']} / {summary['examples']})",
        "",
        "## Rows",
        "",
        "| Row | Lesson | Condition | Final | Gold | Purist | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        decision = record.get("decision_record") or {}
        comparison = record.get("comparison") or {}
        notes = "; ".join(record.get("parse_errors") or [])
        if record.get("call_error"):
            notes = f"{notes}; {record['call_error']}" if notes else str(record["call_error"])
        lines.append(
            f"| {record['source_row_index']} | {record['lesson_type']} | "
            f"{record['ablation_condition']} | {decision.get('final_label', '')} | "
            f"{record['reference']['gold_label']} | "
            f"{'yes' if comparison.get('purist_correct') else 'no'} | {notes} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            _interpret_run(summary),
        ]
    )
    write_markdown_report(path, lines)


def _yes_no(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return ""


def _interpret_run(summary: Mapping[str, Any]) -> str:
    if summary["decision_records"] == 0:
        return (
            "The run exported prompt inputs but did not execute live model calls. Use the JSONL "
            "artifact to inspect prompt payloads before running a live comparison."
        )
    if summary["parse_or_validation_failures"]:
        return (
            "The first priority is output robustness: repair the prompt/schema contract before "
            "drawing quality conclusions from the dev-set labels."
        )
    if summary["purist_accuracy"] < 0.5:
        return (
            "The first live adjudicator is diagnostic rather than promotable; inspect row-level "
            "rationales before any broader validation pass."
        )
    return (
        "The dev-set behavior is interpretable enough to inspect row-level successes and "
        "failures before deciding whether to revise the prompt or run a broader validation pass."
    )
