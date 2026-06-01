"""Markdown report writer for Gan 2026 minimal evidence-selector runs."""

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
    lines = [
        "# Gan 2026 LLM-Only Minimal Evidence Selector V0",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation development result on `gan2026_split_v1`. It is not a final "
        "holdout or benchmark result.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: a minimal model-boundary schema can capture the prediction-bearing "
        "answer and exact evidence while deterministic sidecars recover rich diagnostics.",
        "",
        "Prediction-bearing component: model-produced `answer` object. Deterministic code "
        "validates structure and evidence, runs strict scorer-format repair and frozen "
        "clean scorer-facing policy, derives diagnostic state, and scores each layer.",
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
            model_role="LLM-only minimal evidence selector",
            deterministic_rule_configuration=(
                "none before prediction; deterministic code validates, performs "
                "strict/frozen clean scorer-facing repair, derives diagnostics, and scores."
            ),
            summary=summary,
            leading_lines=[f"- Pipeline: `{metadata['pipeline_name']}`"],
            extra_before_deterministic=[
                "- Prompt policy taxonomy: "
                + ", ".join(f"`{policy_id}`" for policy_id in metadata["prompt_policy_ids"]),
                f"- Schema contract: `{metadata['schema_contract']}`",
            ],
        ),
        "",
        "## Summary",
        "",
        f"- Minimal evidence records: {summary['minimal_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Invalid JSON failures: {summary['invalid_json_failures']}",
        f"- Schema failures: {summary['schema_failures']}",
        f"- Parse/schema issues: {summary['parse_or_validation_failures']}",
        f"- Exact answer evidence substrings: {summary['answer_evidence_valid']} / "
        f"{summary['examples']}",
        f"- Exact supporting-fact evidence substrings: "
        f"{summary['supporting_fact_evidence_valid']} / "
        f"{summary['supporting_fact_evidence_total']}",
        f"- Raw minimal-answer score: Purist {summary['raw_purist_accuracy']:.4f} "
        f"({summary['raw_purist_correct']} / {summary['examples']}), Pragmatic "
        f"{summary['raw_pragmatic_accuracy']:.4f} "
        f"({summary['raw_pragmatic_correct']} / {summary['examples']})",
        f"- Strict-format score: Purist {summary['strict_format_purist_accuracy']:.4f} "
        f"({summary['strict_format_purist_correct']} / {summary['examples']}), Pragmatic "
        f"{summary['strict_format_pragmatic_accuracy']:.4f} "
        f"({summary['strict_format_pragmatic_correct']} / {summary['examples']})",
        f"- Frozen clean scorer-facing score: Purist "
        f"{summary['clean_scorer_facing_purist_accuracy']:.4f} "
        f"({summary['clean_scorer_facing_purist_correct']} / {summary['examples']}), "
        f"Pragmatic {summary['clean_scorer_facing_pragmatic_accuracy']:.4f} "
        f"({summary['clean_scorer_facing_pragmatic_correct']} / {summary['examples']})",
        f"- Rows changed by downstream repair layers: {summary['repair_changed_rows']}",
        f"- Answer states: {summary['answer_states']}",
        "",
        "## Contract And Evidence Issues",
        "",
        "| Row | Contract issues | Evidence issues | Raw scorer-format issue |",
        "| ---: | --- | --- | --- |",
    ]
    for row in rows:
        contract_issue = _format_contract_issue(row)
        evidence_issue = _format_evidence_issue(row.get("evidence_summary") or {})
        raw_issue = _format_raw_scorer_issue((row.get("score_layers") or {}).get("raw") or {})
        if contract_issue or evidence_issue or raw_issue:
            lines.append(
                f"| {row['source_row_index']} | {contract_issue} | {evidence_issue} | "
                f"{raw_issue} |"
            )

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | State | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        raw = (row.get("score_layers") or {}).get("raw") or {}
        strict = (row.get("score_layers") or {}).get("strict_format") or {}
        clean = (row.get("score_layers") or {}).get("clean_scorer_facing") or {}
        minimal = row.get("minimal_record") or {}
        state = (minimal.get("answer") or {}).get("state", "")
        notes = "; ".join(row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        derived = (row.get("derived_diagnostics") or {}).get("derived_state") or {}
        if derived:
            notes = (
                f"{notes}; cluster_axis={derived.get('cluster_axis')}; "
                f"boundary_state={derived.get('boundary_state')}"
                if notes
                else (
                    f"cluster_axis={derived.get('cluster_axis')}; "
                    f"boundary_state={derived.get('boundary_state')}"
                )
            )
        lines.append(
            f"| {row['source_row_index']} | {state} | {raw.get('final_label', '')} | "
            f"{strict.get('final_label', '')} | {clean.get('final_label', '')} | "
            f"{row['reference']['gold_label']} | {_yes_no(raw.get('purist_correct'))} | "
            f"{_yes_no(clean.get('purist_correct'))} | {notes} |"
        )
    write_markdown_report(path, lines)


def _format_contract_issue(row: Mapping[str, Any]) -> str:
    issues = [
        str(error)
        for error in row.get("parse_errors") or []
        if str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
    ]
    diagnostics = row.get("contract_diagnostics") or {}
    extra = diagnostics.get("extra_fields_seen") or []
    if extra:
        issues.append("extra fields: " + ", ".join(map(str, extra)))
    if diagnostics.get("repair_applied"):
        issues.append(f"repair: {diagnostics.get('repair_policy')}")
    return "; ".join(issues)


def _format_evidence_issue(evidence_summary: Mapping[str, Any]) -> str:
    issues: list[str] = []
    if evidence_summary.get("answer_evidence_valid") is False and evidence_summary.get(
        "answer_evidence"
    ):
        issues.append(
            "answer evidence not exact "
            f"({_markdown_table_cell(evidence_summary.get('answer_evidence'))})"
        )
    invalid_facts = evidence_summary.get("supporting_fact_evidence_invalid") or []
    if invalid_facts:
        issue_text = ", ".join(
            f"{item.get('fact_id')}: {_markdown_table_cell(item.get('evidence'))}"
            for item in invalid_facts
        )
        issues.append(f"supporting fact evidence not exact ({issue_text})")
    return "; ".join(issues)


def _format_raw_scorer_issue(raw_layer: Mapping[str, Any]) -> str:
    if raw_layer.get("scorable"):
        return ""
    error = raw_layer.get("error")
    label = raw_layer.get("final_label")
    if not error:
        return ""
    if label:
        return f"unparsable_label: {_markdown_table_cell(label)} ({error})"
    return str(error)


def _yes_no(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return ""


def _markdown_table_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()
