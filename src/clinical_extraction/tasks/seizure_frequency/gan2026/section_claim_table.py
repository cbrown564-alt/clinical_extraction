"""Section-and-claim-table Gan 2026 LLM-first diagnostic pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_structured import (
    _extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
    repair_prediction_label_clean_scorer_facing,
    repair_prediction_label_format_preserving,
)

PROMPT_VERSION = "gan2026_section_claim_table_v3"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_section_claim_table_validation25_gpt41mini_v3_2026-06-01.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_section_claim_table_validation25_gpt41mini_v3_2026-06-01.md"
)


class SectionClaimRecord(BaseModel):
    """One source-near claim from a note section or local text zone."""

    model_config = ConfigDict(extra="forbid")

    claim_id: str
    section: str | None = None
    claim_type: Literal[
        "frequency",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
        "non_seizure_event",
    ]
    evidence: str
    anchor_text: str | None = None
    raw_frequency: str | None = None
    temporality: Literal["current", "recent", "historical", "future", "unclear"]
    assertion_status: Literal["asserted", "negated", "historical", "hypothetical", "unknown"]
    semiology: str | None = None
    uncertainty: Literal["low", "medium", "high"]


class SectionClaimFinalQueryRecord(BaseModel):
    """Model query over claim rows that chooses the Gan-facing answer."""

    model_config = ConfigDict(extra="forbid")

    selected_claim_ids: list[str]
    answer_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    final_label: str | None = None
    raw_selected_frequency: str | None = None
    conversion_note: str | None = None
    evidence: str
    confidence: Literal["low", "medium", "high"]
    rationale: str


class SectionClaimTableExtractionRecord(BaseModel):
    """Full section-claim-table extraction returned by the LLM."""

    model_config = ConfigDict(extra="forbid")

    claims: list[SectionClaimRecord]
    final_query: SectionClaimFinalQueryRecord


class Gan2026SectionClaimTableSignature(dspy.Signature):
    """Extract section-local seizure-frequency claims, then answer from the table."""

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one clinical note and task instructions. It intentionally omits "
            "gold labels and deterministic candidate diagnostics."
        )
    )
    section_claim_table_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object with claims and final_query. Claims are source-near "
            "section-local facts; final_query selects the Gan-facing answer from them."
        )
    )


class DspySectionClaimTableExtractor(dspy.Module):
    """DSPy section-claim-table extractor with no deterministic candidate inputs."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026SectionClaimTableSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the claim-table prompt payload, excluding gold labels."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 section-and-claim-table LLM-first diagnostic extraction",
        "source_row_index": record.source_row_index,
        "instructions": [
            "Read the full clinical note and make a flat table of seizure-frequency claims.",
            "Do not use deterministic rule candidates; this input contains only the note.",
            (
                "Each claim should stay source-near: preserve its local section or text zone, "
                "evidence substring, temporality, assertion status, semiology, and uncertainty."
            ),
            (
                "For claim_type, temporality, assertion_status, uncertainty, answer_kind, "
                "and confidence, return one scalar string from the schema enum, not a list. "
                "If two enum values seem plausible, choose the best primary value and explain "
                "the ambiguity in rationale."
            ),
            (
                "Keep current/recent, historical, negated, no-reference, seizure-free, "
                "last-event-only, and unclear-frequency statements as separate claim rows."
            ),
            (
                "After producing claim rows, run a final query over the table and select the "
                "Gan-facing answer. Record selected_claim_ids and a concise rationale."
            ),
            (
                "Keep raw_selected_frequency source-near, but make final_label a parser-ready "
                "Gan-compatible label such as 1 per day, 2 to 3 per month, "
                "multiple per week, 1 per 2 day, 1 per 7 to 10 day, "
                "2 per 2 week, 1 per 2 month, seizure free for 6 month, unknown, "
                "or no seizure frequency reference."
            ),
            (
                "Do not put inequality symbols, prose such as daily/yearly/bimonthly, "
                "or phrases like every other week in final_label. Convert them to the "
                "closest Gan label while preserving the selected clinical fact."
            ),
            (
                "Preserve explicit intervals in final_label instead of rounding them: "
                "every 3 to 4 weeks -> 1 per 3 to 4 week; twice every two weeks -> "
                "2 per 2 week; once every seven to ten days -> 1 per 7 to 10 day."
            ),
            (
                "Preserve explicit counted ranges even when wording uses alternatives: "
                "5 or 7 focal onset seizures in three weeks -> 5 to 7 per 3 week. "
                "Do not soften a counted range to multiple."
            ),
            (
                "Convert twice per ordinary calendar unit directly: twice a month -> "
                "2 per month; twice a week -> 2 per week. Do not turn twice a month "
                "into every two months."
            ),
            (
                "In these Gan synthetic letters, bimonthly means every two months "
                "unless the text explicitly says twice per month; use 1 per 2 month."
            ),
            (
                "Do not emit a cluster final_label unless the selected claim truly states "
                "cluster frequency with both cluster cadence and event burden. Vague "
                "clustering around an ordinary rate should stay an ordinary frequency."
            ),
            (
                "Cluster cadence can be the ordinary Gan-facing frequency when a cluster "
                "statement gives only timing, such as every seven to nine days -> "
                "1 per 7 to 9 day. Use unknown only when the current cadence cannot be "
                "converted."
            ),
            (
                "An explicit current cluster cadence normally outranks an isolated lower-burden "
                "recent subtype count with an assumed denominator. For example, if events tend "
                "to cluster every seven to nine days and the note separately mentions two "
                "recent nocturnal tonic-clonic seizures, choose 1 per 7 to 9 day unless the "
                "note says the cadence is non-epileptic, historical, or not the Gan target."
            ),
            (
                "When a recent quantified event burden is followed by a short seizure-free "
                "span, prefer the quantified recent burden for Gan-facing final_label unless "
                "the note explicitly frames the patient as currently seizure-free overall."
            ),
            (
                "For Gan-style labels, a short subsequent seizure-free span does not by itself "
                "erase a counted recent event range in the same current clinical interval. "
                "Keep the counted range, such as 5 or 7 focal onset seizures in three weeks -> "
                "5 to 7 per 3 week, unless the whole letter clearly makes seizure freedom the "
                "overall current answer."
            ),
            (
                "For vague but recurring monthly burden, use accepted category wording in "
                "final_label: several events across most months -> multiple per month. Keep "
                "phrases like several per month in raw_selected_frequency, not final_label."
            ),
            (
                "If multiple current seizure semiologies are active, select the highest "
                "current or recent seizure burden unless the note gives an overall count."
            ),
            (
                "Use unknown when seizures or seizure-like events are discussed but current "
                "frequency cannot be converted to a Gan-compatible rate."
            ),
            (
                "Use no seizure frequency reference only when the note contains no usable "
                "seizure-frequency evidence."
            ),
            "Every evidence value must be an exact substring from the note when possible.",
            (
                "The final_query evidence must also be an exact substring from the note. "
                "Copy the evidence field verbatim from one selected claim row instead of "
                "paraphrasing it."
            ),
            "Return exactly one JSON object with no markdown.",
        ],
        "claim_schema": {
            "claim_id": "stable string such as c1",
            "section": "source section or local zone, or null",
            "claim_type": [
                "frequency",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
                "non_seizure_event",
            ],
            "evidence": "exact note substring supporting this claim",
            "anchor_text": "short local anchor text, or null",
            "raw_frequency": "source-near frequency expression, or null",
            "temporality": ["current", "recent", "historical", "future", "unclear"],
            "assertion_status": [
                "asserted",
                "negated",
                "historical",
                "hypothetical",
                "unknown",
            ],
            "semiology": "seizure type or clinical target, or null",
            "uncertainty": ["low", "medium", "high"],
        },
        "final_query_schema": {
            "selected_claim_ids": "claim IDs used to select the answer",
            "answer_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "raw_selected_frequency": (
                "source-near selected frequency text before Gan label conversion, or null"
            ),
            "final_label": (
                "Gan-compatible label, or null if answer_kind implies unknown/no_reference"
            ),
            "conversion_note": (
                "brief explanation of any source-near to Gan-compatible label conversion"
            ),
            "evidence": "exact note substring supporting the final answer",
            "confidence": ["low", "medium", "high"],
            "rationale": "brief reason for choosing these claim rows",
        },
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_section_claim_table_json(
    raw_output: str,
    *,
    note_text: str | None = None,
) -> tuple[SectionClaimTableExtractionRecord | None, list[str]]:
    """Parse and validate one raw section-claim-table model output."""

    del note_text
    try:
        payload = _repair_section_claim_table_payload(json.loads(_extract_json_object(raw_output)))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    try:
        extraction = SectionClaimTableExtractionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    errors: list[str] = []
    if not extraction.claims:
        errors.append("claim_extraction: no claim rows")
    claim_ids = {claim.claim_id for claim in extraction.claims}
    missing = [
        claim_id
        for claim_id in extraction.final_query.selected_claim_ids
        if claim_id not in claim_ids
    ]
    if missing:
        errors.append(f"final_query: selected unknown claim IDs {missing}")
    return extraction, errors


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reuse_raw_outputs = reuse_raw_outputs or {}
    metadata = _run_metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
    )
    metadata["dspy_cache"] = dspy_cache
    metadata["reuse_source"] = reuse_source
    metadata["escalation_reason"] = escalation_reason
    program = DspySectionClaimTableExtractor()
    if mode == "live":
        dspy.configure(
            lm=dspy.LM(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                num_retries=2,
            )
        )

    rows: list[dict[str, Any]] = []
    for record in records:
        prompt_input_json = build_prompt_input(record)
        raw_output = reuse_raw_outputs.get(record.source_row_index, "")
        call_error: str | None = None
        reused_raw_output = raw_output != ""
        if mode == "live" and not reused_raw_output:
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.section_claim_table_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_section_claim_table_json(raw_output, note_text=record.note_text)
            if raw_output
            else (None, ["not_run"])
        )
        evidence_summary = (
            _evidence_summary(record.note_text, extraction)
            if extraction
            else _empty_evidence_summary()
        )
        score_layers = _score_layers(record, extraction)
        repair_changes = _repair_changes(score_layers)
        component_status = _component_status(
            extraction=extraction,
            parse_errors=parse_errors,
            evidence_summary=evidence_summary,
            score_layers=score_layers,
            call_error=call_error,
        )
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "pipeline_name": PROMPT_VERSION,
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "structured_record": extraction.model_dump() if extraction else None,
                "component_status": component_status,
                "evidence_summary": evidence_summary,
                "score_layers": score_layers,
                "repair_changes": repair_changes,
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_normalized_label": record.gold_normalized_label,
                    "gold_label_kind": str(record.gold_label_kind),
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
            }
        )
        if progress_every and len(rows) % progress_every == 0:
            _emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_records(rows)
    return rows, metadata


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    claim_evidence_valid = sum(
        int((row.get("evidence_summary") or {}).get("claim_evidence_valid", 0))
        for row in rows
    )
    claim_evidence_total = sum(
        int((row.get("evidence_summary") or {}).get("claim_evidence_total", 0))
        for row in rows
    )
    selected_evidence_valid = sum(
        int(bool((row.get("evidence_summary") or {}).get("selected_evidence_valid")))
        for row in rows
    )
    raw = _layer_summary(rows, "raw")
    strict = _layer_summary(rows, "strict_format")
    clean = _layer_summary(rows, "clean_scorer_facing")
    component_failures = Counter(
        component
        for row in rows
        for component, status in (row.get("component_status") or {}).items()
        if status != "ok"
    )
    return {
        "examples": count,
        "structured_records": sum(bool(row.get("structured_record")) for row in rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "reused_raw_outputs": sum(bool(row.get("reused_raw_output")) for row in rows),
        "parse_or_validation_failures": sum(
            _has_blocking_parse_issue(row.get("parse_errors")) for row in rows
        ),
        "claim_evidence_valid": claim_evidence_valid,
        "claim_evidence_total": claim_evidence_total,
        "selected_evidence_valid": selected_evidence_valid,
        "raw_scorable": raw["scorable"],
        "raw_purist_correct": raw["purist_correct"],
        "raw_purist_accuracy": raw["purist_accuracy"],
        "raw_pragmatic_correct": raw["pragmatic_correct"],
        "raw_pragmatic_accuracy": raw["pragmatic_accuracy"],
        "strict_format_scorable": strict["scorable"],
        "strict_format_purist_correct": strict["purist_correct"],
        "strict_format_purist_accuracy": strict["purist_accuracy"],
        "strict_format_pragmatic_correct": strict["pragmatic_correct"],
        "strict_format_pragmatic_accuracy": strict["pragmatic_accuracy"],
        "clean_scorer_facing_scorable": clean["scorable"],
        "clean_scorer_facing_purist_correct": clean["purist_correct"],
        "clean_scorer_facing_purist_accuracy": clean["purist_accuracy"],
        "clean_scorer_facing_pragmatic_correct": clean["pragmatic_correct"],
        "clean_scorer_facing_pragmatic_accuracy": clean["pragmatic_accuracy"],
        "component_failures": dict(sorted(component_failures.items())),
        "repair_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    reusable: dict[int, str] = {}
    if not path.exists():
        return reusable
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        raw_output = row.get("raw_output")
        source_row_index = row.get("source_row_index")
        if isinstance(source_row_index, int) and isinstance(raw_output, str) and raw_output:
            reusable[source_row_index] = raw_output
    return reusable


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata["summary"]
    lines = [
        f"# Gan 2026 Section Claim Table {metadata['prompt_version'].rsplit('_', 1)[-1].upper()}",
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
        f"- Pipeline: `{metadata['pipeline_name']}`",
        f"- DSPy version: `{metadata['dspy_version']}`",
        f"- Runtime model display/API identifier: `{metadata['model']}`",
        "- Provider/execution: hosted OpenAI via DSPy/LiteLLM",
        "- Model role: LLM-first claim extractor and final query selector",
        f"- Prompt/program version: `{metadata['prompt_version']}`",
        f"- Temperature: `{metadata['temperature']}`",
        f"- Max tokens: `{metadata['max_tokens']}`",
        f"- Mode: `{metadata['mode']}`",
        f"- DSPy cache enabled: `{metadata.get('dspy_cache')}`",
        f"- Reused raw model outputs: `{summary['reused_raw_outputs']}`",
        f"- Reuse source: `{metadata.get('reuse_source') or 'none'}`",
        "- Optimizer: none",
        "- Deterministic rule configuration: none before prediction; deterministic code only "
        "validates, performs strict/frozen clean scorer-facing repair, and scores.",
        f"- Git commit: `{metadata['git_commit']}`",
        f"- Working tree note: `{metadata['working_tree_note']}`",
        f"- JSONL artifact: `{jsonl_path}`",
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
                f"| {row['source_row_index']} | {evidence_issue} | {raw_issue} | "
                f"{parse_issue} |"
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _score_layers(
    record: GanFrequencyRecord,
    extraction: SectionClaimTableExtractionRecord | None,
) -> dict[str, dict[str, Any]]:
    raw_label = _raw_final_label(extraction)
    strict_label = repair_prediction_label_format_preserving(raw_label) if raw_label else None
    clean_label = repair_prediction_label_clean_scorer_facing(raw_label) if raw_label else None
    return {
        "raw": _score_label(record, raw_label),
        "strict_format": _score_label(record, strict_label),
        "clean_scorer_facing": _score_label(record, clean_label),
    }


def _raw_final_label(extraction: SectionClaimTableExtractionRecord | None) -> str | None:
    if extraction is None:
        return None
    if extraction.final_query.final_label:
        return extraction.final_query.final_label
    if extraction.final_query.answer_kind == "unknown":
        return "unknown"
    if extraction.final_query.answer_kind == "no_reference":
        return "no seizure frequency reference"
    return None


def _score_label(record: GanFrequencyRecord, label: str | None) -> dict[str, Any]:
    result: dict[str, Any] = {"final_label": label, "scorable": False}
    if not label:
        result["error"] = "missing_final_label"
        return result
    try:
        predicted_record = label_to_frequency_record(label)
    except ValueError as exc:
        result["error"] = str(exc)
        return result
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    result.update(
        {
            "scorable": True,
            "predicted_monthly_frequency": predicted_record.monthly_frequency,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "predicted_purist_category": predicted_purist,
            "gold_purist_category": gold_purist,
            "purist_correct": predicted_purist == gold_purist,
            "predicted_pragmatic_category": predicted_pragmatic,
            "gold_pragmatic_category": gold_pragmatic,
            "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
        }
    )
    return result


def _repair_section_claim_table_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    claims = repaired.get("claims")
    if isinstance(claims, list):
        repaired["claims"] = [
            _repair_claim_payload(claim) if isinstance(claim, dict) else claim
            for claim in claims
        ]
    final_query = repaired.get("final_query")
    if isinstance(final_query, dict):
        repaired["final_query"] = _repair_final_query_payload(final_query)
    return repaired


def _repair_claim_payload(claim: Mapping[str, Any]) -> dict[str, Any]:
    repaired = dict(claim)
    repaired["claim_type"] = _repair_enum_alias(
        repaired.get("claim_type"),
        {
            "frequency",
            "cluster_frequency",
            "seizure_free",
            "last_event_only",
            "unknown_frequency",
            "no_reference",
            "non_seizure_event",
        },
    )
    repaired["temporality"] = _repair_enum_alias(
        repaired.get("temporality"),
        {"current", "recent", "historical", "future", "unclear"},
    )
    repaired["assertion_status"] = _repair_enum_alias(
        repaired.get("assertion_status"),
        {"asserted", "negated", "historical", "hypothetical", "unknown"},
    )
    repaired["uncertainty"] = _repair_enum_alias(
        repaired.get("uncertainty"),
        {"low", "medium", "high"},
    )
    return repaired


def _repair_final_query_payload(final_query: Mapping[str, Any]) -> dict[str, Any]:
    repaired = dict(final_query)
    selected_claim_ids = repaired.get("selected_claim_ids")
    if isinstance(selected_claim_ids, str):
        repaired["selected_claim_ids"] = [
            claim_id.strip()
            for claim_id in selected_claim_ids.split(",")
            if claim_id.strip()
        ]
    elif isinstance(selected_claim_ids, list):
        repaired["selected_claim_ids"] = [
            str(_unwrap_singleton(claim_id)).strip()
            for claim_id in selected_claim_ids
            if str(_unwrap_singleton(claim_id)).strip()
        ]
    repaired["answer_kind"] = _repair_enum_alias(
        repaired.get("answer_kind"),
        {
            "frequency",
            "seizure_free",
            "unknown",
            "no_reference",
            "unresolved_multiple",
        },
    )
    repaired["confidence"] = _repair_enum_alias(
        repaired.get("confidence"),
        {"low", "medium", "high"},
    )
    if not repaired.get("rationale") and isinstance(repaired.get("evidence"), str):
        repaired["rationale"] = repaired["evidence"]
        repaired["conversion_note"] = _append_conversion_note(
            repaired.get("conversion_note"),
            (
                "Non-semantic schema repair: final_query.rationale was omitted, "
                "so it was copied from final_query.evidence."
            ),
        )
    return repaired


def _append_conversion_note(existing: Any, note: str) -> str:
    if isinstance(existing, str) and existing.strip():
        return f"{existing.strip()} {note}"
    return note


def _unwrap_singleton(value: Any) -> Any:
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


def _repair_enum_alias(value: Any, allowed: set[str]) -> Any:
    if isinstance(value, list):
        for item in value:
            unwrapped = _unwrap_singleton(item)
            if isinstance(unwrapped, str) and unwrapped in allowed:
                return unwrapped
        return _unwrap_singleton(value)
    return _unwrap_singleton(value)


def _repair_changes(score_layers: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    previous_layer = "raw"
    previous = score_layers["raw"].get("final_label")
    for layer in ["strict_format", "clean_scorer_facing"]:
        current = score_layers[layer].get("final_label")
        if isinstance(previous, str) and isinstance(current, str) and current != previous:
            changes.append({"layer": layer, "before": previous, "after": current})
        previous_layer = layer
        previous = score_layers[previous_layer].get("final_label")
    return changes


def _evidence_summary(
    note_text: str,
    extraction: SectionClaimTableExtractionRecord | None,
) -> dict[str, Any]:
    if extraction is None:
        return _empty_evidence_summary()
    claim_validity = []
    invalid_claim_evidence = []
    for claim in extraction.claims:
        valid = evidence_is_substring(note_text, claim.evidence)
        claim_validity.append(valid)
        if not valid:
            invalid_claim_evidence.append(
                {
                    "claim_id": claim.claim_id,
                    "evidence": claim.evidence,
                }
            )
    selected_valid = evidence_is_substring(note_text, extraction.final_query.evidence)
    summary: dict[str, Any] = {
        "claim_evidence_valid": sum(claim_validity),
        "claim_evidence_total": len(claim_validity),
        "claim_evidence_invalid": invalid_claim_evidence,
        "selected_evidence_valid": selected_valid,
        "selected_evidence": extraction.final_query.evidence,
    }
    return summary


def _empty_evidence_summary() -> dict[str, Any]:
    return {
        "claim_evidence_valid": 0,
        "claim_evidence_total": 0,
        "claim_evidence_invalid": [],
        "selected_evidence_valid": False,
        "selected_evidence": None,
    }


def _component_status(
    *,
    extraction: SectionClaimTableExtractionRecord | None,
    parse_errors: Sequence[str],
    evidence_summary: Mapping[str, Any],
    score_layers: Mapping[str, Mapping[str, Any]],
    call_error: str | None,
) -> dict[str, str]:
    status = {
        "segmentation_sectioning": "ok",
        "claim_extraction": "ok",
        "temporality_conflict": "ok",
        "final_query": "ok",
        "parse_schema": "ok",
        "scorer_format": "ok",
    }
    if call_error or _has_blocking_parse_issue(parse_errors):
        status["parse_schema"] = "fail"
    if extraction is None:
        status["claim_extraction"] = "fail"
        status["final_query"] = "fail"
        status["scorer_format"] = "fail"
        return status
    if not extraction.claims or any(
        error.startswith("claim_extraction:") for error in parse_errors
    ):
        status["claim_extraction"] = "fail"
    if not any(claim.section for claim in extraction.claims):
        status["segmentation_sectioning"] = "fail"
    if any(error.startswith("final_query:") for error in parse_errors):
        status["final_query"] = "fail"
    selected_ids = set(extraction.final_query.selected_claim_ids)
    selected_claims = [claim for claim in extraction.claims if claim.claim_id in selected_ids]
    if selected_claims and all(
        claim.temporality in {"historical", "future"} for claim in selected_claims
    ):
        status["temporality_conflict"] = "fail"
    if evidence_summary.get("claim_evidence_valid") != evidence_summary.get(
        "claim_evidence_total"
    ):
        status["claim_extraction"] = "fail"
    if not evidence_summary.get("selected_evidence_valid"):
        status["final_query"] = "fail"
    if not score_layers["raw"].get("scorable"):
        status["scorer_format"] = "fail"
    return status


def _layer_summary(rows: Sequence[Mapping[str, Any]], layer: str) -> dict[str, Any]:
    count = len(rows)
    layer_rows = [
        (row.get("score_layers") or {}).get(layer) or {}
        for row in rows
    ]
    scorable = sum(bool(row.get("scorable")) for row in layer_rows)
    purist = sum(bool(row.get("purist_correct")) for row in layer_rows)
    pragmatic = sum(bool(row.get("pragmatic_correct")) for row in layer_rows)
    return {
        "scorable": scorable,
        "purist_correct": purist,
        "purist_accuracy": round(purist / count, 4) if count else 0.0,
        "pragmatic_correct": pragmatic,
        "pragmatic_accuracy": round(pragmatic / count, 4) if count else 0.0,
    }


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


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    metadata["summary"] = summarize_records(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    progress = {
        "processed": len(rows),
        "total": total,
        "call_failures": metadata["summary"]["call_failures"],
        "clean_purist_accuracy_so_far": metadata["summary"][
            "clean_scorer_facing_purist_accuracy"
        ],
        "raw_scorable": metadata["summary"]["raw_scorable"],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def _run_metadata(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
) -> dict[str, Any]:
    return {
        "date": datetime.now(UTC).date().isoformat(),
        "created_at_utc": datetime.now(UTC).isoformat(),
        "mode": mode,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "pipeline_name": PROMPT_VERSION,
        "prompt_version": PROMPT_VERSION,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
        "split": split,
        "split_manifest": split_manifest,
        "row_count": len(records),
        "git_commit": _git_output(["git", "rev-parse", "--short", "HEAD"]),
        "working_tree_note": _working_tree_note(),
        "python": sys.version.split()[0],
    }


def _working_tree_note() -> str:
    status = _git_output(["git", "status", "--short"])
    return "clean" if status == "" else "dirty/uncommitted local changes"


def _git_output(args: Sequence[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


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
