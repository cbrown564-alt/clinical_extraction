"""LLM-only structured-events Gan 2026 seizure-frequency extraction experiments."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026 import llm_structured_temporal
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_structured_monthly_diary import (
    monthly_diary_label_from_events as _monthly_diary_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
    repair_prediction_label_clean_scorer_facing,
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports import (
    llm_model_metadata_lines,
    write_markdown_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.schema_repair import (
    repair_structured_extraction_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence_derivation import (
    evidence_describes_current_non_epileptic_events,
)

_clinic_date = llm_structured_temporal.clinic_date
_clinic_month_year = llm_structured_temporal.clinic_month_year
_duration_from_event_dates = llm_structured_temporal.duration_from_event_dates
_duration_from_events = llm_structured_temporal.duration_from_events
_duration_from_text = llm_structured_temporal.duration_from_text
_elapsed_months = llm_structured_temporal.elapsed_months
_elapsed_months_from_nearest_event_date = (
    llm_structured_temporal.elapsed_months_from_nearest_event_date
)
_elapsed_months_from_nearest_event_date_precise = (
    llm_structured_temporal.elapsed_months_from_nearest_event_date_precise
)
_event_month_year = llm_structured_temporal.event_month_year
_event_text = llm_structured_temporal.event_text
_month_number = llm_structured_temporal.month_number
_nearest_event_date = llm_structured_temporal.nearest_event_date
_nearest_event_month_year = llm_structured_temporal.nearest_event_month_year
_small_number_words_to_digits = llm_structured_temporal.small_number_words_to_digits

PROMPT_VERSION = "gan2026_llm_only_structured_events_v0.5"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_structured_events_validation_gpt41mini_2026-06-01.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_structured_events_validation_gpt41mini_2026-06-01.md"
)
StructuredRepairMode = Literal[
    "raw_model",
    "strict_format",
    "clean_scorer_facing",
    "selected_evidence_derivation",
    "hybrid_full_stack",
    "custom",
]


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

    repair_mode: StructuredRepairMode | None = None
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

    @classmethod
    def for_mode(cls, mode: StructuredRepairMode) -> StructuredRepairConfig:
        """Build one of the named repair modes used in run metadata and reports."""

        if mode == "raw_model":
            return cls(
                repair_mode=mode,
                basic_label_repair=False,
                basic_label_repair_format_only=False,
                clean_scorer_facing_gold_policy=False,
                selected_evidence_repair=False,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "strict_format":
            return cls(
                repair_mode=mode,
                basic_label_repair=True,
                basic_label_repair_format_only=True,
                clean_scorer_facing_gold_policy=False,
                selected_evidence_repair=False,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "clean_scorer_facing":
            return cls(
                repair_mode=mode,
                basic_label_repair=True,
                basic_label_repair_format_only=True,
                clean_scorer_facing_gold_policy=True,
                selected_evidence_repair=False,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "selected_evidence_derivation":
            return cls(
                repair_mode=mode,
                basic_label_repair=True,
                basic_label_repair_format_only=False,
                clean_scorer_facing_gold_policy=False,
                selected_evidence_repair=True,
                monthly_diary_repair=False,
                usual_interval_repair=False,
                breakthrough_repair=False,
                non_epileptic_repair=False,
                residual_jerk_repair=False,
                post_change_burst_repair=False,
                dated_sequence_repair=False,
                elapsed_anchor_repair=False,
            )
        if mode == "hybrid_full_stack":
            return cls(repair_mode=mode)
        return cls(repair_mode=mode)

    @property
    def resolved_repair_mode(self) -> StructuredRepairMode:
        """Return the named mode when flags match one; otherwise mark it custom."""

        flags = self._flags()
        for mode in (
            "raw_model",
            "strict_format",
            "clean_scorer_facing",
            "selected_evidence_derivation",
            "hybrid_full_stack",
        ):
            if flags == StructuredRepairConfig.for_mode(mode)._flags():
                return mode
        return "custom"

    def _flags(self) -> dict[str, bool]:
        return {
            "basic_label_repair": self.basic_label_repair,
            "basic_label_repair_format_only": self.basic_label_repair_format_only,
            "clean_scorer_facing_gold_policy": self.clean_scorer_facing_gold_policy,
            "selected_evidence_repair": self.selected_evidence_repair,
            "monthly_diary_repair": self.monthly_diary_repair,
            "usual_interval_repair": self.usual_interval_repair,
            "breakthrough_repair": self.breakthrough_repair,
            "non_epileptic_repair": self.non_epileptic_repair,
            "residual_jerk_repair": self.residual_jerk_repair,
            "post_change_burst_repair": self.post_change_burst_repair,
            "dated_sequence_repair": self.dated_sequence_repair,
            "elapsed_anchor_repair": self.elapsed_anchor_repair,
        }


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
    metadata["repair_mode"] = repair_config.resolved_repair_mode
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
    repair_mode = str(metadata.get("repair_mode") or "custom")
    repair_config = metadata.get("repair_config") or {}
    repair_config_items = ", ".join(
        f"`{key}={value}`" for key, value in sorted(repair_config.items())
    )
    repair_policy = _repair_policy_description(repair_mode)
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
    write_markdown_report(path, lines)


def _repair_policy_description(repair_mode: str) -> str:
    descriptions = {
        "raw_model": "raw structured model selection with no deterministic final-label repair",
        "strict_format": (
            "raw structured model selection plus strict format-preserving basic label repair only"
        ),
        "clean_scorer_facing": (
            "raw structured model selection plus clean scorer-facing Gan gold-normalization policy"
        ),
        "selected_evidence_derivation": (
            "structured model selection plus selected-evidence derivation only"
        ),
        "hybrid_full_stack": (
            "hybrid full deterministic repair stack after structured model selection"
        ),
    }
    return descriptions.get(
        repair_mode,
        "custom deterministic repair families after structured model selection",
    )


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
    return build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version=getattr(dspy, "__version__", "unknown"),
        split=split,
        split_manifest=split_manifest,
        row_count=len(records),
    )
