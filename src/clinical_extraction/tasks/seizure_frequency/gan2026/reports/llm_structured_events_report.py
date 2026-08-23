"""Markdown report writer for Gan 2026 LLM structured-events runs."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    llm_model_metadata_lines,
    write_markdown_report,
)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata["summary"]
    repair_mode = str(metadata.get("repair_mode") or "custom")
    repair_config = metadata.get("repair_config") or {}
    repair_config_items = ", ".join(
        f"`{key}={value}`" for key, value in sorted(repair_config.items())
    )
    repair_policy = _repair_policy_description(repair_mode)
    is_holdout = metadata.get("split") == "test"
    title = (
        "# Gan 2026 LLM-Structured Holdout Aggregate"
        if is_holdout
        else "# Gan 2026 LLM-Structured Validation Run"
    )
    boundary = (
        "This is an aggregate-only locked-holdout result on `gan2026_split_v1`. "
        "No row-level result is included in this report."
        if is_holdout
        else "This is a validation development result on `gan2026_split_v1`. It is not a "
        "final holdout or benchmark result."
    )
    score_scope = "holdout" if is_holdout else "validation"
    lines = [
        title,
        "",
        f"Date: {metadata['date']}",
        "",
        boundary,
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: a slim source-near event schema plus LLM clinical selection can reduce "
        "direct note-to-label schema burden while keeping deterministic code limited to "
        "Gan normalization, evidence validation, and scoring.",
        "",
        "Minimal change: add an LLM-only structured-events extractor and selector. No "
        "deterministic V1 candidate diagnostics are provided to the model.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} rows.",
        (
            f"Rare full-validation reason: {metadata['escalation_reason']}"
            if metadata.get("escalation_reason")
            else "Rare full-validation reason: not applicable for this run size."
        ),
        "Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a "
        "side-car.",
        "",
        "## Model And Prompt Metadata",
        "",
        *llm_model_metadata_lines(
            metadata,
            jsonl_path,
            model_role="LLM-only structured-events extractor and clinical selector",
            deterministic_rule_configuration=(
                "none before prediction; deterministic code only repairs labels selected "
                "by the LLM, validates evidence, and scores."
            ),
            summary=summary,
            extra_lines=[
                f"- Repair mode: `{repair_mode}`",
                f"- Repair policy: {repair_policy}.",
                (
                    f"- Repair config: {repair_config_items}"
                    if repair_config_items
                    else "- Repair config: none"
                ),
            ],
        ),
        "",
        "## Summary",
        "",
        f"- Structured records: {summary['structured_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        "- Initial parse/schema/label issues: "
        f"{summary.get('initial_parse_or_validation_failures', 0)}",
        f"- Format retries applied: {summary.get('format_retries_applied', 0)}",
        f"- Format retries rejected: {summary.get('format_retries_rejected', 0)}",
        f"- JSON dialect repairs: {summary.get('json_dialect_repairs', 0)}",
        f"- Deterministic repair notes: {summary['repair_notes']}",
        f"- Exact selection evidence substrings: {summary['evidence_valid']} / "
        f"{summary['examples']}",
        f"- Purist {score_scope} accuracy/micro F1 proxy: {summary['purist_accuracy']:.4f} "
        f"({summary['purist_correct']} / {summary['examples']})",
        f"- Pragmatic {score_scope} accuracy/micro F1 proxy: {summary['pragmatic_accuracy']:.4f} "
        f"({summary['pragmatic_correct']} / {summary['examples']})",
    ]
    if is_holdout:
        write_markdown_report(path, lines)
        return
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Final | Gold | Purist | Notes |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        record = row.get("structured_record") or {}
        selection = record.get("selection") or {}
        comparison = row.get("comparison") or {}
        notes = "; ".join(row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        if not row.get("evidence_valid"):
            evidence_note = "evidence_not_exact_substring"
            notes = f"{notes}; {evidence_note}" if notes else evidence_note
        lines.append(
            f"| {row['source_row_index']} | {selection.get('final_label', '')} | "
            f"{row['reference']['gold_label']} | "
            f"{'yes' if comparison.get('purist_correct') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


def _repair_policy_description(repair_mode: str) -> str:
    descriptions = {
        "strict_json_raw_model": "strict JSON parsing only, with no dialect or final-label repair",
        "json_dialect_only": (
            "raw structured model selection plus Python-literal JSON dialect repair only"
        ),
        "raw_model": "raw structured model selection with no deterministic final-label repair",
        "llm_encode": (
            "structured model selection plus selected-evidence derivation only"
        ),
        "llm_select": (
            "hybrid full deterministic repair stack after structured model selection"
        ),
        "llm_revise": (
            "hybrid full deterministic repair stack after structured model selection"
        ),
        # Sealed / legacy names still resolve via normalize_repair_mode callers.
        "selected_evidence_derivation": (
            "structured model selection plus selected-evidence derivation only"
        ),
        "hybrid_full_stack": (
            "hybrid full deterministic repair stack after structured model selection"
        ),
    }
    from clinical_extraction.paper.cells import normalize_repair_mode

    return descriptions.get(
        normalize_repair_mode(repair_mode),
        descriptions.get(
            repair_mode,
            "custom deterministic repair families after structured model selection",
        ),
    )
