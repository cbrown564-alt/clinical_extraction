"""Markdown report writer for Gan 2026 LLM claim-table selector runs."""

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
    version = metadata["prompt_version"].rsplit("_", 1)[-1].upper()
    lines = [
        f"# Gan 2026 LLM-Only Claim Table Selector {version}",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation development result on `gan2026_split_v1`. It is not a final "
        "holdout or benchmark result.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: a flat section-and-claim table can expose temporal, conflict, and "
        "evidence-state failures before the model collapses them into one final label.",
        "",
        "Prediction-bearing component: model-produced claim rows plus model final query. "
        "Deterministic code validates structure and evidence, runs strict scorer-format "
        "repair and frozen clean scorer-facing policy, and scores each layer.",
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
            model_role="LLM-only direct-labeler claim extractor and final query selector",
            deterministic_rule_configuration=(
                "none before prediction; deterministic code only validates, performs "
                "strict/frozen clean scorer-facing repair, and scores."
            ),
            summary=summary,
            leading_lines=[f"- Pipeline: `{metadata['pipeline_name']}`"],
            extra_before_deterministic=[
                "- Prompt policy taxonomy: "
                + ", ".join(f"`{policy_id}`" for policy_id in metadata["prompt_policy_ids"]),
                "- Required ablations before 25/50/250 ladder runs: "
                + ", ".join(
                    f"`{name}`"
                    for name in metadata.get("required_ablations_before_ladder_runs", ())
                ),
            ],
        ),
        "",
        "## Summary",
        "",
        f"- Structured claim-table records: {summary['structured_records']} / "
        f"{summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Exact claim evidence substrings: {summary['claim_evidence_valid']} / "
        f"{summary['claim_evidence_total']}",
        f"- Exact selected final evidence substrings: {summary['selected_evidence_valid']} / "
        f"{summary['examples']}",
        f"- raw final-query score: Purist {summary['raw_purist_accuracy']:.4f} "
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
        "",
        "## Component Failure Slices",
        "",
        "| Component | Failures |",
        "| --- | ---: |",
    ]
    component_failures = summary["component_failures"]
    for component in [
        "segmentation_sectioning",
        "claim_extraction",
        "temporality_conflict",
        "final_query",
        "parse_schema",
        "scorer_format",
    ]:
        lines.append(f"| {component} | {component_failures.get(component, 0)} |")

    lines.extend(
        [
            "",
            "## Reviewable Failure Details",
            "",
            "| Row | Evidence issues | Raw scorer-format issue | Parse/schema issue |",
            "| ---: | --- | --- | --- |",
        ]
    )
    for row in rows:
        evidence_issue = _format_evidence_issue(row.get("evidence_summary") or {})
        raw_issue = _format_raw_scorer_issue((row.get("score_layers") or {}).get("raw") or {})
        parse_issue = "; ".join(
            str(error)
            for error in row.get("parse_errors") or []
            if _has_blocking_parse_issue([error])
        )
        if evidence_issue or raw_issue or parse_issue:
            lines.append(
                f"| {row['source_row_index']} | {evidence_issue} | {raw_issue} | {parse_issue} |"
            )

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Raw | Strict | Clean | Gold | Raw Purist | Clean Purist | Notes |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        raw = (row.get("score_layers") or {}).get("raw") or {}
        strict = (row.get("score_layers") or {}).get("strict_format") or {}
        clean = (row.get("score_layers") or {}).get("clean_scorer_facing") or {}
        notes = "; ".join(row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        bad_components = [
            name for name, status in (row.get("component_status") or {}).items() if status != "ok"
        ]
        if bad_components:
            joined = ",".join(bad_components)
            notes = f"{notes}; {joined}" if notes else joined
        lines.append(
            f"| {row['source_row_index']} | {raw.get('final_label', '')} | "
            f"{strict.get('final_label', '')} | {clean.get('final_label', '')} | "
            f"{row['reference']['gold_label']} | {_yes_no(raw.get('purist_correct'))} | "
            f"{_yes_no(clean.get('purist_correct'))} | {notes} |"
        )
    write_markdown_report(path, lines)


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            (
                "invalid_json:",
                "schema_validation_error:",
                "not_run",
            )
        )
        for error in errors or []
    )


def _yes_no(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return ""


def _format_evidence_issue(evidence_summary: Mapping[str, Any]) -> str:
    issues: list[str] = []
    invalid_claims = evidence_summary.get("claim_evidence_invalid") or []
    if invalid_claims:
        issue_text = ", ".join(
            f"{item.get('claim_id')}: {_markdown_table_cell(item.get('evidence'))}"
            for item in invalid_claims
        )
        issues.append(f"claim evidence not exact ({issue_text})")
    if evidence_summary.get("selected_evidence_valid") is False and evidence_summary.get(
        "selected_evidence"
    ):
        issues.append(
            "selected evidence not exact "
            f"({_markdown_table_cell(evidence_summary.get('selected_evidence'))})"
        )
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


def _markdown_table_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()
