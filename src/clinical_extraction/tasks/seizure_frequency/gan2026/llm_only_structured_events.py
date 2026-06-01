"""LLM-only structured-events Gan 2026 seizure-frequency extraction experiments."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    evidence_describes_current_non_epileptic_events,
    label_to_frequency_record,
    monthly_diary_label_from_text,
    repair_prediction_label,
    repair_prediction_label_clean_scorer_facing,
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.schema_repair import (
    repair_structured_extraction_payload,
)

PROMPT_VERSION = "gan2026_llm_only_structured_events_v0.5"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_structured_events_validation_gpt41mini_2026-06-01.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_structured_events_validation_gpt41mini_2026-06-01.md"
)
MonthlyDiaryMonthKey = tuple[int, int | None]


class StructuredEventRecord(BaseModel):
    """Slim source-near event fact extracted by the LLM."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    ]
    raw_value: str | None = None
    applies_to: str | None = None
    time_window: str | None = None
    temporality: Literal["current", "recent", "historical", "future", "unclear"]
    assertion_status: Literal["asserted", "negated", "historical", "hypothetical", "unknown"]
    evidence: str
    notes: str | None = None


class StructuredSelectionRecord(BaseModel):
    """LLM clinical selection over the source-near events."""

    model_config = ConfigDict(extra="forbid")

    selected_event_ids: list[str]
    final_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    final_label: str | None = None
    evidence: str
    confidence: Literal["low", "medium", "high"]
    rationale: str


class StructuredExtractionRecord(BaseModel):
    """Full structured extraction returned by the LLM."""

    model_config = ConfigDict(extra="forbid")

    events: list[StructuredEventRecord]
    selection: StructuredSelectionRecord


class NormalizedEventRecord(BaseModel):
    """Deterministic Gan normalization attached after LLM event extraction."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    normalized_label: str | None
    semantic_kind: str | None
    monthly_frequency: float | None
    yearly_bounds: tuple[float, float] | None
    repair_applied: bool
    validation_errors: list[str]


@dataclass(frozen=True)
class StructuredRepairConfig:
    """Controls deterministic repair families applied after LLM-only structured-events output."""

    basic_label_repair: bool = True
    basic_label_repair_format_only: bool = False
    clean_scorer_facing_gold_policy: bool = False
    selected_evidence_repair: bool = True
    monthly_diary_repair: bool = True
    usual_interval_repair: bool = True
    breakthrough_repair: bool = True
    non_epileptic_repair: bool = True
    residual_jerk_repair: bool = True
    post_change_burst_repair: bool = True
    dated_sequence_repair: bool = True
    elapsed_anchor_repair: bool = True


class Gan2026StructuredExtractorSignature(dspy.Signature):
    """Extract source-near seizure-frequency events and choose a final answer.

    Return exactly one JSON object with two keys: events and selection.
    """

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one clinical note and task instructions. It intentionally omits "
            "gold labels and deterministic candidate diagnostics."
        )
    )
    structured_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object with events and selection. Events are source-near facts; "
            "selection chooses the clinically appropriate Gan answer from those events."
        )
    )


class DspyStructuredExtractor(dspy.Module):
    """DSPy structured extractor with no deterministic candidate inputs."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026StructuredExtractorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the LLM-only structured-events prompt payload, excluding gold labels."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 LLM-only structured-events extraction and clinical selection",
        "source_row_index": record.source_row_index,
        "instructions": [
            "Read the full clinical note and extract source-near seizure-frequency facts.",
            "Do not use deterministic rule candidates; this input contains only the note.",
            (
                "Return events as slim clinical facts, not fully normalized benchmark records. "
                "Use raw_value for the text's stated rate, duration, last-event statement, or "
                "unknown/no-reference cue."
            ),
            (
                "Event kind must be one of frequency_rate, cluster_frequency, seizure_free, "
                "last_event_only, unknown_frequency, or no_reference."
            ),
            (
                "Use one no_reference event only when the note contains no usable "
                "seizure-frequency evidence. Do not use no_reference when seizures are "
                "discussed but frequency is unclear; use unknown_frequency instead."
            ),
            (
                "Keep seizure-free statements separate from unknown or last-event-only "
                "statements. Do not select seizure-free if other current seizure-like events "
                "remain active."
            ),
            (
                "Selection must choose the highest current or recent seizure burden across "
                "semiologies when several current seizure types are present."
            ),
            (
                "If the note gives an overall current seizure count plus a breakdown by "
                "seizure type, select the overall count for final_label rather than only the "
                "clinically most severe subtype count."
            ),
            (
                "Selection final_label may be a Gan-compatible label such as 1 per day, "
                "2 to 3 per month, multiple per week, 1 cluster per week, "
                "seizure free for 6 month, unknown, or no seizure frequency reference."
            ),
            (
                "If the selected event has a countable raw_value, prefer putting the source "
                "expression in raw_value and a concise Gan-compatible label in final_label."
            ),
            (
                "When the note says a last event occurred on a date and the patient has "
                "been well, stable, or seizure-free since, still extract the dated last-event "
                "fact as its own event even if the selection is seizure-free."
            ),
            (
                "When the note says a count such as 3 or 4 jerks occurred since a dated "
                "last tonic-clonic seizure, keep the source count and the dated anchor "
                "available in the event list."
            ),
            "Every evidence value must be an exact substring from the note when possible.",
            "Return exactly one JSON object with no markdown.",
        ],
        "event_schema": {
            "event_id": "stable string such as e1",
            "kind": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
            ],
            "raw_value": "source-near expression or null",
            "applies_to": "seizure type or clinical target, or null",
            "time_window": "source-near current/recent/historical window, or null",
            "temporality": ["current", "recent", "historical", "future", "unclear"],
            "assertion_status": [
                "asserted",
                "negated",
                "historical",
                "hypothetical",
                "unknown",
            ],
            "evidence": "exact note substring",
            "notes": "optional short note or null",
        },
        "selection_schema": {
            "selected_event_ids": "list of selected event_id strings",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "final_label": "Gan-compatible label, or null if not directly countable",
            "evidence": "exact note substring supporting the final selection",
            "confidence": ["low", "medium", "high"],
            "rationale": "brief clinical reason for selecting these events",
        },
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_structured_json(
    raw_output: str,
    *,
    note_text: str | None = None,
    repair_config: StructuredRepairConfig | None = None,
) -> tuple[StructuredExtractionRecord | None, list[NormalizedEventRecord], list[str]]:
    repair_config = repair_config or StructuredRepairConfig()
    errors: list[str] = []
    try:
        payload = _filter_structured_payload(
            repair_structured_extraction_payload(json.loads(_extract_json_object(raw_output)))
        )
    except json.JSONDecodeError as exc:
        return None, [], [f"invalid_json: {exc.msg}"]

    try:
        extraction = StructuredExtractionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [], [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    normalized_events = [
        _normalize_event(event, note_text=note_text) for event in extraction.events
    ]
    final_label = _resolve_final_label(extraction, normalized_events)
    if final_label is None:
        errors.append("unscorable_final_label: no selected event normalized to a Gan label")
        return extraction, normalized_events, errors

    repaired_label = final_label
    if repair_config.basic_label_repair and not repair_config.selected_evidence_repair:
        basic_repair = (
            repair_prediction_label_clean_scorer_facing
            if repair_config.clean_scorer_facing_gold_policy
            else repair_prediction_label_format_preserving
            if repair_config.basic_label_repair_format_only
            else repair_prediction_label
        )
        repaired_label = _replace_repaired_label(
            errors,
            repaired_label,
            basic_repair(repaired_label),
        )
    if repair_config.selected_evidence_repair:
        repaired_label = _replace_repaired_label(
            errors,
            repaired_label,
            repair_prediction_label_with_evidence(
                repaired_label,
                extraction.selection.evidence,
                context_text=note_text,
            ),
        )
    if repair_config.monthly_diary_repair:
        monthly_diary_label = _monthly_diary_label_from_events(
            extraction,
            note_text=note_text,
        )
        if monthly_diary_label:
            repaired_label = _replace_repaired_label(
                errors, repaired_label, monthly_diary_label
            )
    if repair_config.usual_interval_repair:
        usual_interval_label = _usual_interval_label_from_events(extraction, repaired_label)
        if usual_interval_label:
            repaired_label = _replace_repaired_label(
                errors, repaired_label, usual_interval_label
            )
    if repair_config.breakthrough_repair:
        breakthrough_label = _breakthrough_label_from_events(extraction, repaired_label)
        if breakthrough_label:
            repaired_label = _replace_repaired_label(
                errors, repaired_label, breakthrough_label
            )
    if repair_config.non_epileptic_repair:
        non_epileptic_label = _non_epileptic_label_from_events(extraction, repaired_label)
        if non_epileptic_label:
            repaired_label = _replace_repaired_label(
                errors, repaired_label, non_epileptic_label
            )
    if repair_config.residual_jerk_repair:
        residual_jerk_label = _residual_jerk_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        )
        if residual_jerk_label:
            repaired_label = _replace_repaired_label(
                errors, repaired_label, residual_jerk_label
            )
    if repair_config.post_change_burst_repair:
        post_change_label = _post_change_burst_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        )
        if post_change_label:
            repaired_label = _replace_repaired_label(errors, repaired_label, post_change_label)
    if repair_config.dated_sequence_repair:
        dated_sequence_label = _dated_sequence_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        )
        if dated_sequence_label:
            repaired_label = _replace_repaired_label(
                errors, repaired_label, dated_sequence_label
            )
    if repair_config.elapsed_anchor_repair:
        elapsed_window_label = _elapsed_since_anchor_label_from_events(
            extraction,
            repaired_label,
            note_text=note_text,
        )
        if elapsed_window_label:
            repaired_label = _replace_repaired_label(
                errors, repaired_label, elapsed_window_label
            )
    try:
        label_to_frequency_record(repaired_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")
    if repaired_label != extraction.selection.final_label:
        extraction = extraction.model_copy(
            update={
                "selection": extraction.selection.model_copy(
                    update={"final_label": repaired_label}
                )
            }
        )
    return extraction, normalized_events, errors


def _filter_structured_payload(payload: Any) -> Any:
    """Keep shared adjudicator repair fields out of structured-events validation."""

    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    event_fields = set(StructuredEventRecord.model_fields)
    selection_fields = set(StructuredSelectionRecord.model_fields)
    events = repaired.get("events")
    if isinstance(events, list):
        repaired["events"] = [
            {key: value for key, value in event.items() if key in event_fields}
            if isinstance(event, dict)
            else event
            for event in events
        ]
    selection = repaired.get("selection")
    if isinstance(selection, dict):
        repaired["selection"] = {
            key: value for key, value in selection.items() if key in selection_fields
        }
    return repaired


def _replace_repaired_label(errors: list[str], old_label: str, new_label: str) -> str:
    if new_label != old_label:
        errors.append(f"final_label_repaired: {old_label!r} -> {new_label!r}")
    return new_label


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
    repair_config: StructuredRepairConfig | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    repair_config = repair_config or StructuredRepairConfig()
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
    metadata["repair_config"] = asdict(repair_config)
    program = DspyStructuredExtractor()
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
                raw_output = str(prediction.structured_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, normalized_events, parse_errors = (
            parse_structured_json(
                raw_output,
                note_text=record.note_text,
                repair_config=repair_config,
            )
            if raw_output
            else (None, [], ["not_run"])
        )
        evidence_valid = (
            evidence_is_substring(record.note_text, extraction.selection.evidence)
            if extraction and extraction.selection.evidence
            else False
        )
        comparison = _compare_to_gold(record, extraction) if extraction else None
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "structured_record": extraction.model_dump() if extraction else None,
                "normalized_events": [event.model_dump() for event in normalized_events],
                "evidence_valid": evidence_valid,
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_normalized_label": record.gold_normalized_label,
                    "gold_label_kind": str(record.gold_label_kind),
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
                "comparison": comparison,
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
    structured_rows = [row for row in rows if row.get("structured_record")]
    call_failures = sum(bool(row.get("call_error")) for row in rows)
    reused_raw_outputs = sum(bool(row.get("reused_raw_output")) for row in rows)
    parse_failures = sum(_has_blocking_parse_issue(row.get("parse_errors")) for row in rows)
    repair_notes = sum(_has_repair_note(row.get("parse_errors")) for row in rows)
    purist_correct = sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in rows)
    pragmatic_correct = sum(
        bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in rows
    )
    evidence_valid = sum(bool(row.get("evidence_valid")) for row in rows)
    final_labels = Counter(
        final_label
        for row in rows
        if row.get("structured_record")
        for final_label in [row["structured_record"]["selection"].get("final_label")]
        if isinstance(final_label, str)
    )
    return {
        "examples": len(rows),
        "structured_records": len(structured_rows),
        "call_failures": call_failures,
        "reused_raw_outputs": reused_raw_outputs,
        "parse_or_validation_failures": parse_failures,
        "repair_notes": repair_notes,
        "evidence_valid": evidence_valid,
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
        "final_labels": dict(sorted(final_labels.items())),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    """Load reusable raw model outputs from a prior JSONL artifact."""

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
    repair_config = metadata.get("repair_config") or {}
    repair_config_items = ", ".join(
        f"`{key}={value}`" for key, value in sorted(repair_config.items())
    )
    repair_policy = (
        "raw structured model selection plus clean scorer-facing Gan gold-normalization policy"
        if repair_config.get("basic_label_repair")
        and repair_config.get("clean_scorer_facing_gold_policy")
        and not repair_config.get("selected_evidence_repair")
        else (
        "raw structured model selection plus strict format-preserving basic label repair only"
        if repair_config.get("basic_label_repair")
        and repair_config.get("basic_label_repair_format_only")
        and not repair_config.get("selected_evidence_repair")
        else "configured deterministic repair families after structured model selection"
        )
    )
    lines = [
        "# Gan 2026 LLM-Structured Validation Run",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation development result on `gan2026_split_v1`. It is not a final "
        "holdout or benchmark result.",
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
        f"- DSPy version: `{metadata['dspy_version']}`",
        f"- Runtime model display/API identifier: `{metadata['model']}`",
        "- Provider/execution: hosted OpenAI via DSPy/LiteLLM",
        "- Model role: LLM-only structured-events extractor and clinical selector",
        f"- Prompt/program version: `{metadata['prompt_version']}`",
        f"- Temperature: `{metadata['temperature']}`",
        f"- Max tokens: `{metadata['max_tokens']}`",
        f"- Mode: `{metadata['mode']}`",
        f"- DSPy cache enabled: `{metadata.get('dspy_cache')}`",
        f"- Reused raw model outputs: `{summary['reused_raw_outputs']}`",
        f"- Reuse source: `{metadata.get('reuse_source') or 'none'}`",
        "- Optimizer: none",
        "- Deterministic rule configuration: none before prediction; deterministic code only "
        "repairs labels selected by the LLM, validates evidence, and scores.",
        f"- Repair policy: {repair_policy}.",
        (
            f"- Repair config: {repair_config_items}"
            if repair_config_items
            else "- Repair config: none"
        ),
        f"- Git commit: `{metadata['git_commit']}`",
        f"- Working tree note: `{metadata['working_tree_note']}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Structured records: {summary['structured_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Deterministic repair notes: {summary['repair_notes']}",
        f"- Exact selection evidence substrings: {summary['evidence_valid']} / "
        f"{summary['examples']}",
        f"- Purist validation accuracy/micro F1 proxy: {summary['purist_accuracy']:.4f} "
        f"({summary['purist_correct']} / {summary['examples']})",
        f"- Pragmatic validation accuracy/micro F1 proxy: {summary['pragmatic_accuracy']:.4f} "
        f"({summary['pragmatic_correct']} / {summary['examples']})",
        "",
        "## Rows",
        "",
        "| Row | Final | Gold | Purist | Notes |",
        "| ---: | --- | --- | --- | --- |",
    ]
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalize_event(
    event: StructuredEventRecord,
    *,
    note_text: str | None = None,
) -> NormalizedEventRecord:
    raw_label = _event_raw_label(event)
    if raw_label is None:
        return NormalizedEventRecord(
            event_id=event.event_id,
            normalized_label=None,
            semantic_kind=None,
            monthly_frequency=None,
            yearly_bounds=None,
            repair_applied=False,
            validation_errors=["no_normalizable_event_label"],
        )
    repaired = repair_prediction_label_with_evidence(
        raw_label,
        event.evidence,
        context_text=note_text,
    )
    try:
        frequency = label_to_frequency_record(repaired)
    except ValueError as exc:
        return NormalizedEventRecord(
            event_id=event.event_id,
            normalized_label=repaired,
            semantic_kind=None,
            monthly_frequency=None,
            yearly_bounds=None,
            repair_applied=repaired != raw_label,
            validation_errors=[str(exc)],
        )
    return NormalizedEventRecord(
        event_id=event.event_id,
        normalized_label=frequency.normalized_label,
        semantic_kind=str(frequency.kind),
        monthly_frequency=frequency.monthly_frequency,
        yearly_bounds=frequency.yearly_bounds,
        repair_applied=repaired != raw_label,
        validation_errors=[],
    )


def _event_raw_label(event: StructuredEventRecord) -> str | None:
    if event.kind == "no_reference":
        return "no seizure frequency reference"
    if event.kind in {"unknown_frequency", "last_event_only"}:
        return "unknown"
    if event.kind == "seizure_free" and event.raw_value:
        return event.raw_value
    if event.kind in {"frequency_rate", "cluster_frequency"} and event.raw_value:
        return event.raw_value
    return None


def _resolve_final_label(
    extraction: StructuredExtractionRecord,
    normalized_events: Sequence[NormalizedEventRecord],
) -> str | None:
    if extraction.selection.final_label:
        return extraction.selection.final_label
    normalized_by_id = {event.event_id: event for event in normalized_events}
    for event_id in extraction.selection.selected_event_ids:
        normalized = normalized_by_id.get(event_id)
        if normalized and normalized.normalized_label and not normalized.validation_errors:
            return normalized.normalized_label
    return _default_label_for_final_kind(extraction.selection.final_kind)


def _monthly_diary_label_from_events(
    extraction: StructuredExtractionRecord,
    *,
    note_text: str | None,
) -> str | None:
    counts_by_month: dict[MonthlyDiaryMonthKey, int] = {}
    for event in extraction.events:
        if event.kind not in {
            "frequency_rate",
            "cluster_frequency",
            "seizure_free",
            "last_event_only",
        }:
            continue
        if event.assertion_status not in {"asserted", "historical"}:
            continue
        for month_key, count in _monthly_diary_event_counts(event, note_text=note_text).items():
            counts_by_month.setdefault(month_key, count)

    if len(counts_by_month) >= 2:
        total = sum(counts_by_month.values())
        months = _monthly_diary_span_months(counts_by_month)
        return f"{total} per {months} month"

    for event in extraction.events:
        if event.kind not in {
            "frequency_rate",
            "cluster_frequency",
            "seizure_free",
            "last_event_only",
        }:
            continue
        text = _event_text(event)
        label = monthly_diary_label_from_text(text)
        if label:
            return label
    return None


def _monthly_diary_event_counts(
    event: StructuredEventRecord,
    *,
    note_text: str | None,
) -> dict[MonthlyDiaryMonthKey, int]:
    text = _small_number_words_to_digits(
        next(
            (
                part
                for part in (event.evidence, event.raw_value, event.notes)
                if part and _monthly_diary_event_month_text(part)
            ),
            " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part),
        ).lower()
    )
    state_count = _monthly_diary_state_count(text)
    month_key = _monthly_diary_event_month(event)
    if state_count is not None and month_key is not None:
        return {month_key: state_count}

    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?"
    )
    count_terms = r"\d+|no|zero|a|an"
    counts: dict[MonthlyDiaryMonthKey, int] = {}

    for match in re.finditer(
        rf"\b(?P<count>{count_terms})\s+"
        r"(?:(?:[a-z]+(?:-[a-z]+)?\s+){0,4}(?:seizures?|events?|convulsions?)\s+)?"
        rf"in\s+(?:early|mid|late)?\s*(?P<month>{month_pattern})"
        rf"(?:\s+(?P<year>\d{{4}}))?\b",
        text,
    ):
        count = _monthly_diary_count_value(match.group("count"))
        if count <= 100:
            counts.setdefault(
                _monthly_diary_month_key(match.group("month"), match.group("year"), event),
                count,
            )
    for match in re.finditer(
        rf"\bin\s+(?:early|mid|late)?\s*(?P<month>{month_pattern})"
        rf"(?:\s+(?P<year>\d{{4}}))?\b[^.;]*?\b"
        rf"(?P<count>{count_terms})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizures?|events?|convulsions?|absences?|attacks?|jerks?)\b",
        text,
    ):
        count = _monthly_diary_count_value(match.group("count"))
        if count <= 100:
            counts.setdefault(
                _monthly_diary_month_key(match.group("month"), match.group("year"), event),
                count,
            )
    for match in re.finditer(
        rf"\b(?P<count>{count_terms})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizures?|events?|convulsions?|absences?|attacks?|jerks?)\s+"
        rf"(?:in\s+)?(?:early|mid|late)?\s*(?P<month>{month_pattern})"
        rf"(?:\s+(?P<year>\d{{4}}))?\b",
        text,
    ):
        count = _monthly_diary_count_value(match.group("count"))
        if count <= 100:
            counts.setdefault(
                _monthly_diary_month_key(match.group("month"), match.group("year"), event),
                count,
            )

    this_month_count = _monthly_diary_this_month_count(text)
    if this_month_count is not None:
        month_key = _monthly_diary_this_month_key(note_text, counts)
        if month_key is not None:
            counts.setdefault(month_key, this_month_count)

    if counts:
        return counts

    month_key = _monthly_diary_event_month(event)
    event_count = _monthly_diary_event_count(event)
    if month_key is not None and event_count is not None:
        return {month_key: event_count}
    return {}


def _monthly_diary_month_key(
    month_text: str,
    year_text: str | None,
    event: StructuredEventRecord,
) -> MonthlyDiaryMonthKey:
    month = _month_number(month_text)
    if year_text:
        return month, int(year_text)
    inferred = _monthly_diary_event_month(event)
    if inferred and inferred[0] == month and inferred[1] is not None:
        return month, inferred[1]
    return month, None


def _monthly_diary_this_month_count(text: str) -> int | None:
    match = re.search(
        r"\b(?:(?:this\s+month|as\s+of\s+this\s+month)\b[^.;]*?\b"
        r"(?P<count1>\d+|no|zero|a|an)\s+(?:seizures?|events?|convulsions?)|"
        r"(?P<count2>\d+|no|zero|a|an)\s+(?:seizures?|events?|convulsions?)"
        r"\s+so\s+far\s+this\s+month)\b",
        text,
    )
    if not match:
        return None
    return _monthly_diary_count_value(match.group("count1") or match.group("count2"))


def _monthly_diary_this_month_key(
    note_text: str | None,
    existing_counts: Mapping[MonthlyDiaryMonthKey, int],
) -> MonthlyDiaryMonthKey | None:
    clinic = _clinic_month_year(note_text or "")
    if clinic is not None:
        return clinic
    dated = [(month, year) for month, year in existing_counts if year is not None]
    if dated:
        latest_month, latest_year = max(dated, key=lambda item: item[1] * 12 + item[0])
        next_month = latest_month + 1
        next_year = latest_year
        if next_month > 12:
            next_month = 1
            next_year += 1
        return next_month, next_year
    month_only = [month for month, _ in existing_counts]
    if month_only:
        next_month = max(month_only) + 1
        return (1 if next_month > 12 else next_month), None
    return None


def _usual_interval_label_from_events(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
) -> str | None:
    selected_text = " ".join(
        part
        for part in (
            extraction.selection.evidence,
            extraction.selection.rationale,
            extraction.selection.final_label,
        )
        if part
    ).lower()
    selected_is_brief_daily = (
        repaired_label in {"1 per day", "multiple per day", "unknown"}
        and re.search(r"\b(?:occasionally|brief periods?|periods? of)\b", selected_text)
        and re.search(r"\bdaily\b", selected_text)
    )
    for event in extraction.events:
        label = _interval_label_from_event_text(_event_text(event))
        if not label:
            continue
        if repaired_label in {"unknown", "no seizure frequency reference"}:
            return label
        if selected_is_brief_daily:
            return label
    return None


def _interval_label_from_event_text(text: str) -> str | None:
    normalized = _small_number_words_to_digits(text.lower())
    interval = r"\d+(?:\s*(?:to|-|–|—)\s*\d+)?|multiple|several"
    match = (
        re.search(
            rf"\b(?:approximately\s+|about\s+|around\s+)?every\s+"
            rf"(?P<interval>{interval})\s+days?\b",
            normalized,
        )
        or re.search(
            rf"\b(?:spaced|spacing)\s+(?P<interval>{interval})\s+days?\s+apart\b",
            normalized,
        )
        or re.search(
            rf"\b(?P<interval>{interval})\s+days?\s+apart\b",
            normalized,
        )
    )
    if not match:
        return None
    interval_text = re.sub(r"\s*(?:-|–|—)\s*", " to ", match.group("interval"))
    interval_text = "multiple" if interval_text == "several" else interval_text
    return f"1 per {interval_text} day"


def _monthly_diary_event_month(
    event: StructuredEventRecord,
) -> tuple[int, int | None] | None:
    text = " ".join(part for part in (event.time_window, event.evidence, event.raw_value) if part)
    match = re.search(
        r"\b(?P<month>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
        r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
        r"nov(?:ember)?|dec(?:ember)?)(?:\s+(?P<year>\d{4}))?\b",
        text.lower(),
    )
    if not match:
        return None
    month = _month_number(match.group("month"))
    year = int(match.group("year")) if match.group("year") else None
    return month, year


def _monthly_diary_event_count(event: StructuredEventRecord) -> int | None:
    candidates = [
        part
        for part in (event.evidence, event.raw_value, event.notes)
        if part and _monthly_diary_event_month_text(part)
    ]
    candidates.append(
        " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part)
    )
    for candidate in candidates:
        text = _small_number_words_to_digits(candidate.lower())
        state_count = _monthly_diary_state_count(text)
        if state_count is not None:
            return state_count
        event_count = re.search(
            r"\b(?P<count>\d+|a|an|no|zero)\s+"
            r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
            r"(?:seizures?|events?|convulsions?|absences?|attacks?|jerks?)\b",
            text,
        )
        if event_count:
            count = _monthly_diary_count_value(event_count.group("count"))
            return count if count <= 100 else None
    return None


def _monthly_diary_state_count(text: str) -> int | None:
    state_terms = r"sleep|asleep|night|nocturnal|awake|waking|daytime|day"
    count_terms = r"\d+|no|zero|a|an"
    counts: list[int] = []
    for pattern in (
        rf"\b(?P<count>{count_terms})\s+(?!in\s+)(?:\w+\s+){{0,3}}(?:{state_terms})\b",
        rf"\b(?P<count>{count_terms})\s+in\s+(?:{state_terms})\b",
    ):
        for match in re.finditer(pattern, text):
            count = _monthly_diary_count_value(match.group("count"))
            if count <= 100:
                counts.append(count)
    if counts:
        return sum(counts)
    return None


def _monthly_diary_event_month_text(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
            r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|"
            r"nov(?:ember)?|dec(?:ember)?)\b",
            text.lower(),
        )
    )


def _monthly_diary_count_value(count_text: str) -> int:
    if count_text in {"a", "an"}:
        return 1
    if count_text in {"no", "zero"}:
        return 0
    return int(count_text)


def _monthly_diary_span_months(
    counts_by_month: Mapping[MonthlyDiaryMonthKey, int],
) -> int:
    keys = list(counts_by_month)
    if all(year is not None for _, year in keys):
        ordinals = [year * 12 + month for month, year in keys if year is not None]
        return max(ordinals) - min(ordinals) + 1
    months = sorted({month for month, _ in keys})
    if not months:
        return 0
    linear_span = max(months) - min(months) + 1
    if linear_span > 6:
        return (12 - max(months)) + min(months) + 1
    return linear_span


def _breakthrough_label_from_events(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
) -> str | None:
    if repaired_label not in {"unknown", "no seizure frequency reference"}:
        return None
    joined_text = " ".join(
        _event_text(event) for event in extraction.events
    )
    if re.search(r"\b(?:perimenstrual|catamenial|outside this window)\b", joined_text):
        return None
    duration = _seizure_free_duration_from_events(extraction.events)
    if duration is None:
        return None
    count = _recent_breakthrough_count(extraction)
    if count is None:
        return None
    return f"{count} per {duration}"


def _non_epileptic_label_from_events(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
) -> str | None:
    if repaired_label not in {"unknown", "no seizure frequency reference"}:
        return None
    selected_ids = set(extraction.selection.selected_event_ids)
    texts = [
        extraction.selection.evidence,
        extraction.selection.rationale,
        *(
            " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part)
            for event in extraction.events
            if not selected_ids or event.event_id in selected_ids
        ),
        *(
            " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part)
            for event in extraction.events
            if event.temporality in {"current", "recent"}
        ),
    ]
    if any(
        evidence_describes_current_non_epileptic_events(text.lower())
        for text in texts
        if text
    ):
        return "seizure free for multiple year"
    return None


def _residual_jerk_label_from_events(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
    *,
    note_text: str | None,
) -> str | None:
    if repaired_label not in {
        "unknown",
        "no seizure frequency reference",
        "multiple per month",
        "multiple per week",
    } and not re.search(r"\bper\s+(?:day|month)\b", repaired_label):
        return None
    clinic = _clinic_date(note_text or "")
    clinic_month_year = _clinic_month_year(note_text or "")
    if clinic is None and clinic_month_year is None:
        return None
    anchor = (
        _nearest_event_date(
            extraction.events,
            clinic=clinic,
            event_kinds={"last_event_only", "seizure_free"},
            max_months=240,
        )
        if clinic is not None
        else None
    )
    month_anchor = (
        _nearest_event_month_year(
            extraction.events,
            clinic=clinic_month_year,
            event_kinds={"last_event_only", "seizure_free"},
            max_months=240,
        )
        if clinic_month_year is not None
        else None
    )
    if anchor is None and month_anchor is None:
        return None
    months = (
        _elapsed_months(month_anchor, clinic_month_year)
        if month_anchor is not None and clinic_month_year is not None
        else None
    )
    if months is None and anchor is not None and clinic is not None:
        months = max(1, ((clinic - anchor).days + 29) // 30)
    if months is None:
        return None
    selected_ids = set(extraction.selection.selected_event_ids)
    for event in extraction.events:
        if event.kind not in {"frequency_rate", "cluster_frequency"}:
            continue
        if selected_ids and event.event_id not in selected_ids:
            continue
        text = _event_text(event)
        if not re.search(r"\b(?:jerks?|myoclonic)\b", text):
            continue
        if not re.search(r"\b(?:remain|persist|persisting|since then)\b", text):
            continue
        if "cluster" in text:
            return f"multiple cluster per {months} month, multiple per cluster"
        count = _count_from_event_text(text)
        if count:
            return f"{count} per {months} month"
    return None


def _post_change_burst_label_from_events(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
    *,
    note_text: str | None = None,
) -> str | None:
    if "seizure free" not in repaired_label and not re.search(
        r"\bper\s+(?:week|day)\b",
        repaired_label,
    ):
        return None
    selection_text = " ".join(
        part
        for part in (
            extraction.selection.final_label,
            extraction.selection.evidence,
            extraction.selection.rationale,
        )
        if part
    ).lower()
    marker_text = " ".join(
        [
            selection_text,
            *(
                " ".join(part for part in (event.evidence, event.raw_value, event.notes) if part)
                for event in extraction.events
                if event.kind == "seizure_free"
            ),
        ]
    )
    if not re.search(
        r"\b(?:since then|no further|not had any further|had no seizures since|"
        r"without seizures since|remained seizure-free since|remained stable without)\b",
        marker_text,
    ):
        return None
    duration = (
        _duration_from_text(selection_text)
        or _duration_from_events(extraction.events)
        or _duration_from_event_dates(extraction.events, note_text)
    )
    if duration is None:
        return None
    count = _post_change_burst_count(extraction.events)
    if count is None:
        return None
    return f"{count} per {duration}"


def _post_change_burst_count(events: Sequence[StructuredEventRecord]) -> str | None:
    for event in events:
        text = " ".join(
            part
            for part in (event.evidence, event.raw_value, event.time_window, event.notes)
            if part
        ).lower()
        if event.kind not in {"frequency_rate", "cluster_frequency"}:
            continue
        if not re.search(
            r"\b(?:shortly afterwards?|soon afterwards?|following week|around that period|"
            r"at that time|then)\b",
            text,
        ):
            continue
        text = _small_number_words_to_digits(text)
        range_match = re.search(r"\b(?P<low>\d+)\s*(?:to|-|–|—)\s*(?P<high>\d+)\b", text)
        if range_match:
            return f"{range_match.group('low')} to {range_match.group('high')}"
        count_match = re.search(
            r"\b(?P<count>\d+)\s+(?:[a-z-]+\s+){0,4}"
            r"(?:seizures?|events?|attacks?|convulsions?)\b",
            text,
        )
        if count_match:
            return count_match.group("count")
        if re.search(r"\b(?:several|multiple|many)\s+(?:seizures?|events?|attacks?)\b", text):
            return "multiple"
    return None


def _elapsed_since_anchor_label_from_events(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
    *,
    note_text: str | None = None,
) -> str | None:
    clinic = _clinic_month_year(note_text or "")
    if clinic is None:
        return None
    count_label = _since_anchor_count_label(extraction, clinic)
    if count_label:
        return count_label
    if "seizure free" not in repaired_label:
        return None
    if not _has_benchmark_last_event_context(extraction.events, note_text=note_text):
        return None
    marker_text = " ".join(
        part
        for part in (
            extraction.selection.evidence,
            extraction.selection.rationale,
            extraction.selection.final_label,
            *(
                event.evidence
                for event in extraction.events
                if event.kind in {"seizure_free", "last_event_only"}
            ),
        )
        if part
    ).lower()
    if not re.search(
        r"\b(?:last|most recent)\s+(?:event|episode|seizure)|"
        r"\b(?:remained|been|has been)\s+(?:well|stable|seizure-free)|"
        r"\bno further\b",
        marker_text,
    ):
        return None
    months = _elapsed_months_from_nearest_event_date_precise(
        extraction.events,
        note_text=note_text,
        event_kinds={"last_event_only", "seizure_free"},
        max_months=18,
    ) or _elapsed_months_from_nearest_event_date(
        extraction.events,
        clinic=clinic,
        event_kinds={"last_event_only", "seizure_free"},
        max_months=18,
    )
    if months is None:
        return None
    return f"1 per {months} month"


def _has_benchmark_last_event_context(
    events: Sequence[StructuredEventRecord],
    *,
    note_text: str | None,
) -> bool:
    text = " ".join(_event_text(event) for event in events)
    if _has_treatment_improvement_context(text):
        return True
    return bool(note_text and _has_treatment_improvement_context(note_text.lower()))


def _has_treatment_improvement_context(text: str) -> bool:
    return bool(
        re.search(
            r"\babsences?\b.{0,80}\b(?:improved|reduced|diminished|settled|became less frequent)\b",
            text,
        )
        or re.search(
            r"\b(?:following|after|with)\b.{0,80}"
            r"\b(?:medication|treatment|dose|lamotrigine|levetiracetam|supportive care|"
            r"prescribed medication)\b",
            text,
        )
        or re.search(
            r"\b(?:medication|treatment|dose|lamotrigine|levetiracetam|supportive care|"
            r"prescribed medication)\b.{0,80}"
            r"\b(?:improved|reduced|diminished|settled|became less frequent)\b",
            text,
        )
    )


def _since_anchor_count_label(
    extraction: StructuredExtractionRecord,
    clinic: tuple[int, int],
) -> str | None:
    selected_ids = set(extraction.selection.selected_event_ids)
    candidate_events = [
        event
        for event in extraction.events
        if event.kind in {"frequency_rate", "cluster_frequency"}
        and event.assertion_status == "asserted"
        and (not selected_ids or event.event_id in selected_ids)
    ]
    if extraction.selection.final_kind in {"unknown", "no_reference", "seizure_free"}:
        candidate_events.extend(
            event
            for event in extraction.events
            if event.kind in {"frequency_rate", "cluster_frequency"}
            and event.assertion_status == "asserted"
            and event.event_id not in selected_ids
        )
    for event in candidate_events:
        text = _event_text(event)
        if not re.search(r"\bsince\b", text):
            continue
        if not re.search(r"\bjerks?\b", text):
            continue
        if not re.search(
            r"\bsince\s+(?:then|\d|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
            text,
        ):
            continue
        count = _count_from_event_text(text)
        if count is None:
            continue
        anchor = _event_month_year(text, clinic_year=clinic[1])
        if anchor is None:
            anchor = _nearest_event_month_year(
                extraction.events,
                clinic=clinic,
                event_kinds={"last_event_only"},
                max_months=18,
            )
        if anchor is None:
            continue
        months = _elapsed_months(anchor, clinic)
        if months is None or months <= 0 or months > 18:
            continue
        return f"{count} per {months} month"
    return None


def _count_from_event_text(text: str) -> str | None:
    text = _small_number_words_to_digits(text.lower())
    count = r"\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?"
    match = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z-]+\s+){{0,4}}"
        r"(?:jerks?|seizures?|events?|episodes?|attacks?|convulsions?)\b",
        text,
    )
    if not match:
        return None
    return re.sub(r"\s*(?:-|–|—|or)\s*", " to ", match.group("count"))


def _elapsed_months_from_nearest_event_date(
    events: Sequence[StructuredEventRecord],
    *,
    clinic: tuple[int, int],
    event_kinds: set[str],
    max_months: int,
) -> int | None:
    anchor = _nearest_event_month_year(
        events,
        clinic=clinic,
        event_kinds=event_kinds,
        max_months=max_months,
    )
    if anchor is None:
        return None
    return _elapsed_months(anchor, clinic)


def _elapsed_months_from_nearest_event_date_precise(
    events: Sequence[StructuredEventRecord],
    *,
    note_text: str | None,
    event_kinds: set[str],
    max_months: int,
) -> int | None:
    clinic = _clinic_date(note_text or "")
    if clinic is None:
        return None
    nearest = _nearest_event_date(
        events,
        clinic=clinic,
        event_kinds=event_kinds,
        max_months=max_months,
    )
    if nearest is None:
        return None
    days = (clinic - nearest).days
    if days <= 0:
        return None
    return max(1, (days + 29) // 30)


def _nearest_event_date(
    events: Sequence[StructuredEventRecord],
    *,
    clinic: date,
    event_kinds: set[str],
    max_months: int,
) -> date | None:
    dates = [
        event_date
        for event in events
        if event.kind in event_kinds
        for event_date in [_event_date(_event_text(event), clinic=clinic)]
        if event_date is not None
        and 0 <= (clinic - event_date).days <= max_months * 31
    ]
    if not dates:
        return None
    return min(dates, key=lambda event_date: (clinic - event_date).days)


def _nearest_event_month_year(
    events: Sequence[StructuredEventRecord],
    *,
    clinic: tuple[int, int],
    event_kinds: set[str],
    max_months: int,
) -> tuple[int, int] | None:
    clinic_month, clinic_year = clinic
    dated = [
        event_month_year
        for event in events
        if event.kind in event_kinds
        for event_month_year in [
            _event_month_year(_event_text(event), clinic_year=clinic_year)
        ]
        if event_month_year is not None
        and 0 <= (clinic_year - event_month_year[1]) * 12 + (clinic_month - event_month_year[0])
        <= max_months
    ]
    if not dated:
        return None
    return min(
        dated,
        key=lambda item: (clinic_year - item[1]) * 12 + (clinic_month - item[0]),
    )


def _elapsed_months(
    anchor: tuple[int, int],
    clinic: tuple[int, int],
) -> int | None:
    anchor_month, anchor_year = anchor
    clinic_month, clinic_year = clinic
    months = (clinic_year - anchor_year) * 12 + (clinic_month - anchor_month)
    return months if months > 0 else None


def _event_text(event: StructuredEventRecord) -> str:
    return " ".join(
        part
        for part in (event.evidence, event.raw_value, event.time_window, event.notes)
        if part
    ).lower()


def _dated_sequence_label_from_events(
    extraction: StructuredExtractionRecord,
    repaired_label: str,
    *,
    note_text: str | None = None,
) -> str | None:
    texts = [
        " ".join(part for part in (event.evidence, event.raw_value, event.time_window) if part)
        for event in extraction.events
    ]
    raw_joined = " ".join(texts).lower()
    if "prior to this improvement" in raw_joined:
        return None
    explicit = re.search(
        r"\b(?P<count>\d+)\s+seizures?\s+in\s+(?P<months>\d+)\s+months?\b",
        _small_number_words_to_digits(raw_joined),
    )
    if explicit:
        if not _dated_sequence_can_override(repaired_label, int(explicit.group("months"))):
            return None
        return f"{explicit.group('count')} per {explicit.group('months')} month"

    dated_events: list[tuple[int, int, int]] = []
    for text in texts:
        dated_events.extend(_dated_event_mentions(text))
    if len(dated_events) < 2:
        return None
    first_month, first_year, _ = min(dated_events, key=lambda item: item[1] * 12 + item[0])
    last_month, last_year, max_count = max(
        dated_events,
        key=lambda item: (item[1] * 12 + item[0], item[2]),
    )
    months = (last_year - first_year) * 12 + (last_month - first_month)
    if months <= 0:
        return None
    if not _dated_sequence_can_override(repaired_label, months):
        return None
    if "seizure free" in repaired_label and not _dated_sequence_is_near_clinic(
        last_month,
        last_year,
        note_text,
    ):
        return None
    return f"{max_count} per {months} month"


def _dated_sequence_can_override(repaired_label: str, months: int) -> bool:
    if repaired_label in {"unknown", "no seizure frequency reference"}:
        return True
    if "seizure free" in repaired_label:
        return True
    if re.search(r"\bper\s+(?:\d+(?:\s+to\s+\d+)?\s+)?(?:day|week)\b", repaired_label):
        return False
    if re.search(r"\bper\s+(?:\d+(?:\s+to\s+\d+)?\s+)?(?:month|year)\b", repaired_label):
        return months > 1
    return False


def _dated_sequence_is_near_clinic(
    last_month: int,
    last_year: int,
    note_text: str | None,
) -> bool:
    clinic = _clinic_month_year(note_text or "")
    if clinic is None:
        return False
    clinic_month, clinic_year = clinic
    elapsed = (clinic_year - last_year) * 12 + (clinic_month - last_month)
    return 0 <= elapsed <= 18


def _dated_event_mentions(text: str) -> list[tuple[int, int, int]]:
    text = _small_number_words_to_digits(text.lower())
    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    )
    ordinal_count = {
        "initial": 1,
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
    }
    mentions: list[tuple[int, int, int]] = []
    last_year: int | None = None
    for match in re.finditer(
        rf"\b(?P<ordinal>initial|first|second|third|fourth|fifth)(?:\s+and\s+"
        rf"(?P<ordinal2>second|third|fourth|fifth))?\s+"
        rf"(?:seizure|event)\w*.*?\b(?P<month>{month_pattern})\s+(?P<year>\d{{4}})?",
        text,
    ):
        year = int(match.group("year")) if match.group("year") else last_year
        if year is None:
            continue
        last_year = year
        count = ordinal_count[match.group("ordinal2") or match.group("ordinal")]
        mentions.append((_month_number(match.group("month")), year, count))
    for match in re.finditer(
        rf"\bnext\s+(?P<additional>\d+)\s+(?:seizure|event)\w*.*?"
        rf"\b(?P<month>{month_pattern})\s+(?P<year>\d{{4}})?",
        text,
    ):
        year = int(match.group("year")) if match.group("year") else last_year
        if year is None:
            continue
        last_year = year
        mentions.append(
            (_month_number(match.group("month")), year, 1 + int(match.group("additional")))
        )
    return mentions


def _month_number(month_text: str) -> int:
    month_key = month_text[:3].lower()
    return {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }[month_key]


def _duration_from_events(events: Sequence[StructuredEventRecord]) -> str | None:
    for event in events:
        text = " ".join(part for part in (event.time_window, event.notes) if part)
        duration = _duration_from_text(text)
        if duration:
            return duration
    return None


def _duration_from_text(text: str) -> str | None:
    text = _small_number_words_to_digits(text.lower())
    match = re.search(r"\b(?P<count>\d+)\s*(?:-|\s+)?(?P<unit>week|month|year)s?\b", text)
    if match:
        return f"{match.group('count')} {match.group('unit')}"
    return None


def _duration_from_event_dates(
    events: Sequence[StructuredEventRecord],
    note_text: str | None,
) -> str | None:
    clinic_month_year = _clinic_month_year(note_text or "")
    if clinic_month_year is None:
        return None
    clinic_month, clinic_year = clinic_month_year
    event_month_years = [
        event_month_year
        for event in events
        for event_month_year in [
            _event_month_year(
                " ".join(
                    part
                    for part in (event.evidence, event.raw_value, event.time_window, event.notes)
                    if part
                ),
                clinic_year=clinic_year,
            )
        ]
        if event_month_year is not None
    ]
    if not event_month_years:
        return None
    event_month, event_year = min(
        event_month_years,
        key=lambda item: abs((clinic_year - item[1]) * 12 + (clinic_month - item[0])),
    )
    months = (clinic_year - event_year) * 12 + (clinic_month - event_month)
    if months <= 0:
        return None
    return f"{months} month"


def _clinic_month_year(note_text: str) -> tuple[int, int] | None:
    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    )
    match = re.search(
        rf"\bclinic date:\s*\d{{1,2}}\s+(?P<month>{month_pattern})\s+(?P<year>\d{{4}})",
        note_text.lower(),
    )
    if not match:
        match = re.search(
            rf"\bsent:\s*\d{{1,2}}\s+(?P<month>{month_pattern})\s+(?P<year>\d{{4}})",
            note_text.lower(),
        )
    if not match:
        match = re.search(
            rf"\bdate:\s*\d{{1,2}}\s+(?P<month>{month_pattern})\s+(?P<year>\d{{4}})",
            note_text.lower(),
        )
    if not match:
        return None
    return _month_number(match.group("month")), int(match.group("year"))


def _clinic_date(note_text: str) -> date | None:
    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    )
    match = re.search(
        rf"\bclinic date:\s*(?P<day>\d{{1,2}})\s+"
        rf"(?P<month>{month_pattern})\s+(?P<year>\d{{4}})",
        note_text.lower(),
    )
    if not match:
        match = re.search(
            rf"\bsent:\s*(?P<day>\d{{1,2}})\s+"
            rf"(?P<month>{month_pattern})\s+(?P<year>\d{{4}})",
            note_text.lower(),
        )
    if not match:
        match = re.search(
            rf"\bdate:\s*(?P<day>\d{{1,2}})\s+"
            rf"(?P<month>{month_pattern})\s+(?P<year>\d{{4}})",
            note_text.lower(),
        )
    if not match:
        return None
    return date(
        int(match.group("year")),
        _month_number(match.group("month")),
        int(match.group("day")),
    )


def _event_date(text: str, *, clinic: date) -> date | None:
    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    )
    normalized = text.lower()
    candidates: list[date] = []
    for numeric in re.finditer(
        r"\b(?P<day>\d{1,2})[-/](?P<month>\d{1,2})(?:[-/](?P<year>\d{2,4}))?\b",
        normalized,
    ):
        year = _event_year_from_optional_text(
            numeric.group("year"),
            month=int(numeric.group("month")),
            clinic=clinic,
        )
        candidates.append(date(year, int(numeric.group("month")), int(numeric.group("day"))))
    for named in re.finditer(
        rf"\b(?P<day>\d{{1,2}})[-/ ](?P<month>{month_pattern})"
        rf"(?:[-/ ](?P<year>\d{{2,4}}))?\b",
        normalized,
    ):
        month = _month_number(named.group("month"))
        year = _event_year_from_optional_text(named.group("year"), month=month, clinic=clinic)
        candidates.append(date(year, month, int(named.group("day"))))
    candidates = [candidate for candidate in candidates if candidate <= clinic]
    if not candidates:
        return None
    return min(candidates, key=lambda candidate: (clinic - candidate).days)


def _event_year_from_optional_text(
    year_text: str | None,
    *,
    month: int,
    clinic: date,
) -> int:
    if year_text:
        year = int(year_text)
        return year + 2000 if year < 100 else year
    return clinic.year - 1 if month > clinic.month else clinic.year


def _event_month_year(text: str, *, clinic_year: int) -> tuple[int, int] | None:
    month_pattern = (
        r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|"
        r"jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    )
    normalized = text.lower()
    month_year = re.search(
        r"\b(?P<month>\d{1,2})\s*[-/]\s*(?P<year>\d{4})\b",
        normalized,
    )
    if month_year:
        month = int(month_year.group("month"))
        if 1 <= month <= 12:
            return month, int(month_year.group("year"))
    named_month_year = re.search(
        rf"\b(?P<month>{month_pattern})\s*[-/]\s*(?P<year>\d{{4}})\b",
        normalized,
    )
    if named_month_year:
        return _month_number(named_month_year.group("month")), int(
            named_month_year.group("year")
        )
    numeric = re.search(r"\b\d{1,2}[-/](?P<month>\d{1,2})(?:[-/](?P<year>\d{2,4}))?\b", normalized)
    if numeric:
        month = int(numeric.group("month"))
        year_text = numeric.group("year")
        year = clinic_year if year_text is None else int(year_text)
        if year < 100:
            year += 2000
        return month, year
    named = re.search(
        rf"\b(?:early|mid|late)?\s*(?P<month>{month_pattern})(?:\s+(?P<year>\d{{4}}))?\b",
        normalized,
    )
    if named:
        return _month_number(named.group("month")), int(named.group("year") or clinic_year)
    return None


def _seizure_free_duration_from_events(
    events: Sequence[StructuredEventRecord],
) -> str | None:
    for event in events:
        text = " ".join(
            part
            for part in (event.raw_value, event.evidence, event.time_window)
            if part
        ).lower()
        if (
            event.kind != "seizure_free"
            and "seizure-free" not in text
            and "seizure free" not in text
        ):
            continue
        text = _small_number_words_to_digits(text)
        match = re.search(r"\b(?:for\s+)?(?P<count>\d+)\s+(?P<unit>month|year)s?\b", text)
        if match:
            return f"{match.group('count')} {match.group('unit')}"
        if re.search(r"\b(?:nearly|almost|about|around)?\s*a\s+year\b", text):
            return "1 year"
    return None


def _recent_breakthrough_count(extraction: StructuredExtractionRecord) -> str | None:
    text = " ".join(
        part
        for part in (
            extraction.selection.final_label,
            extraction.selection.evidence,
            extraction.selection.rationale,
            *(
                event.evidence
                for event in extraction.events
                if event.event_id in set(extraction.selection.selected_event_ids)
            ),
        )
        if part
    ).lower()
    text = _small_number_words_to_digits(text)
    range_match = re.search(r"\b(?P<low>\d+)\s*(?:to|-|–|—)\s*(?P<high>\d+)\b", text)
    if range_match:
        return f"{range_match.group('low')} to {range_match.group('high')}"
    count_match = re.search(
        r"\b(?P<count>\d+)\s+(?:tonic|generalised|generalized|focal|seizures?|events?)",
        text,
    )
    if count_match:
        return count_match.group("count")
    if re.search(r"\bcluster\b", text) and re.search(r"\b(?:preceded|plus|and)\b", text):
        return "2"
    if re.search(r"\b(?:a|single|1)\s+(?:focal|generalised|generalized|tonic|event|seizure)", text):
        return "1"
    return None


def _small_number_words_to_digits(text: str) -> str:
    replacements = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
    }
    for word, digit in replacements.items():
        text = re.sub(rf"\b{word}\b", digit, text)
    return text


def _default_label_for_final_kind(final_kind: str) -> str | None:
    if final_kind == "unknown":
        return "unknown"
    if final_kind == "no_reference":
        return "no seizure frequency reference"
    return None


def _compare_to_gold(
    record: GanFrequencyRecord,
    extraction: StructuredExtractionRecord,
) -> dict[str, Any]:
    if extraction.selection.final_label is None:
        return {}
    try:
        predicted_record = label_to_frequency_record(extraction.selection.final_label)
    except ValueError:
        return {}
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    return {
        "predicted_monthly_frequency": predicted_record.monthly_frequency,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "predicted_purist_category": predicted_purist,
        "gold_purist_category": gold_purist,
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": predicted_pragmatic,
        "gold_pragmatic_category": gold_pragmatic,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


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
        "parse_or_validation_failures": metadata["summary"]["parse_or_validation_failures"],
        "purist_accuracy_so_far": metadata["summary"]["purist_accuracy"],
        "pragmatic_accuracy_so_far": metadata["summary"]["pragmatic_accuracy"],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            (
                "invalid_json:",
                "schema_validation_error:",
                "unscorable_final_label:",
                "not_run",
            )
        )
        for error in errors or []
    )


def _has_repair_note(errors: Any) -> bool:
    return any(str(error).startswith("final_label_repaired:") for error in errors or [])


def _extract_json_object(raw_output: str) -> str:
    text = raw_output.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text


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
