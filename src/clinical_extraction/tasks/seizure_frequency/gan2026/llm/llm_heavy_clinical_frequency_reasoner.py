"""LLM-heavy clinical frequency reasoner for Gan 2026 smoke experiments."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.replay_io import (
    load_raw_outputs_by_source_index,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    repair_decision_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.repair_modes import (
    repair_mode_layers,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
)

PROMPT_VERSION = "gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact"
PIPELINE_FAMILY = "llm_heavy_clinical_frequency_reasoner"
SCORE_LAYER_NAMES = (
    "raw_llm",
    "format_only",
    "selected_evidence_arithmetic",
    "benchmark_aligned",
    "oracle_format_upper_bound",
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.md"
)


class ClinicalQuantity(BaseModel):
    """Model-proposed structured clinical quantity for one event."""

    model_config = ConfigDict(extra="forbid")

    occurrences_low: float | None = None
    occurrences_high: float | None = None
    period_low: float | None = None
    period_high: float | None = None
    period_unit: Literal["day", "week", "month", "year"] | None = None
    vague_count: Literal["multiple", "rare", "occasional", "frequent"] | None = None
    clusters_low: float | None = None
    clusters_high: float | None = None
    cluster_period_unit: Literal["day", "week", "month", "year"] | None = None
    events_per_cluster_low: float | None = None
    events_per_cluster_high: float | None = None
    seizure_free_duration_low: float | None = None
    seizure_free_duration_high: float | None = None
    seizure_free_duration_unit: Literal["day", "week", "month", "year"] | None = None


class LlmHeavyEventRecord(BaseModel):
    """LLM-owned seizure-frequency event."""

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
    applies_to: str | None = None
    raw_phrase: str
    evidence: str
    assertion_status: Literal["asserted", "negated", "hypothetical", "uncertain"]
    temporality: Literal["current", "recent", "historical", "unclear"]
    certainty: Literal["high", "medium", "low"]
    clinical_quantity: ClinicalQuantity
    model_normalized_clinical_label: str | None = None
    notes: str


class LlmHeavySelectionRecord(BaseModel):
    """LLM-owned aggregation and clinical selection."""

    model_config = ConfigDict(extra="forbid")

    selected_event_ids: list[str]
    rejected_event_ids: list[str]
    final_clinical_state: Literal[
        "frequency",
        "seizure_free",
        "unknown_frequency",
        "no_reference",
        "unresolved_multiple",
    ]
    aggregation_strategy: Literal[
        "highest_current_frequency",
        "recent_window",
        "seizure_free_over_current_event",
        "cluster_total_rate",
        "unknown_boundary",
        "no_reference_boundary",
        "other",
    ]
    final_clinical_label: str
    rationale: str
    uncertainty_flags: list[str]


class LlmHeavyFinalAnswerRecord(BaseModel):
    """LLM-rendered scoring-facing answer."""

    model_config = ConfigDict(extra="forbid")

    raw_clinical_summary: str = ""
    raw_llm_final_label: str
    raw_llm_final_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    raw_llm_monthly_frequency: float | None = None
    selected_evidence: str
    selected_event_ids: list[str]
    supporting_event_ids: list[str] = Field(default_factory=list)
    combined_rationale: str = ""
    rendering_operands: ClinicalQuantity | None = None
    arithmetic_trace: str = ""
    final_rationale: str = ""


class LlmHeavyExtractionRecord(BaseModel):
    """Full LLM-heavy reasoner output."""

    model_config = ConfigDict(extra="forbid")

    events: list[LlmHeavyEventRecord]
    selection: LlmHeavySelectionRecord
    final_answer: LlmHeavyFinalAnswerRecord


class Gan2026LlmHeavyReasonerSignature(dspy.Signature):
    """Run an LLM-heavy three-stage clinical frequency reasoner."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical note, task instructions, and output schemas."
    )
    llm_heavy_reasoner_json: str = dspy.OutputField(
        desc="One strict JSON object with events, selection, and final_answer."
    )


class DspyLlmHeavyReasoner(dspy.Module):
    """DSPy program wrapper for the LLM-heavy reasoner."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026LlmHeavyReasonerSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the LLM-heavy prompt payload."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "task": "Clinical seizure-frequency reasoner",
        "source_row_index": record.source_row_index,
        "instructions": [
            "Read the full note.",
            (
                "Stage 1: extract all clinically relevant seizure-frequency events as "
                "source-near records. Omit administrative, medication, plan, and "
                "no-reference events unless they are necessary for the final answer."
            ),
            (
                "Stage 2: select the event or combination that determines the final clinical "
                "seizure-frequency state."
            ),
            (
                "Stage 3: render your selected answer into the requested schema and "
                "show the operands you used for the final label."
            ),
            (
                "The model owns extraction, clinical normalization proposal, aggregation, "
                "selection, and final schema rendering."
            ),
            (
                "Keep unknown_frequency, no_reference, seizure_free, and unresolved_multiple "
                "as distinct states."
            ),
            (
                "For every event, copy evidence as an exact substring from the note. For "
                "final_answer.selected_evidence, copy exactly one selected event evidence "
                "value; do not concatenate, paraphrase, or merge evidence strings."
            ),
            (
                "Keep the output compact: no long rationales, no duplicate administrative "
                "events, and no event whose evidence cannot be copied exactly from the note."
            ),
            (
                "Render raw_llm_final_label as a normalized label using forms like "
                "4 per day, 1 per 7 to 9 day, 2 to 4 per year, multiple per week, "
                "seizure free for 6 month, unknown, or no seizure frequency reference."
            ),
            (
                "The final label must be your own rendering of the selected evidence. Fill "
                "final_answer.rendering_operands with the count, period, cluster, vague-count, "
                "or seizure-free duration operands that justify raw_llm_final_label, and fill "
                "final_answer.arithmetic_trace with a short source-near calculation."
            ),
            (
                "Always include final_answer.selected_event_ids. It must exactly equal "
                "selection.selected_event_ids, even when only one event is selected."
            ),
            (
                "Render raw_llm_final_label directly from the selected evidence; do not rely "
                "on a later field to reinterpret the selected fact."
            ),
            (
                "Convert upper bounds and inequalities into the selected count without "
                "inequality symbols while preserving the selected denominator."
            ),
            (
                "When a current quantified non-tonic-clonic seizure frequency is selected, "
                "do not let a seizure-free tonic-clonic distractor overwrite the final label."
            ),
            (
                "Do not let raw_llm_final_label hide cluster cadence, per-cluster burden, "
                "seizure-free duration, or unresolved ambiguity."
            ),
            (
                "Cluster cadence is not events-per-cluster. If selected evidence gives only "
                "cluster timing, render one cluster occurrence per stated interval unless the "
                "same selected evidence states the number of events within each cluster."
            ),
            (
                "Return exactly one JSON object with top-level keys events, selection, and "
                "final_answer. Do not use markdown."
            ),
        ],
        "event_schema": {
            "event_id": "stable string such as sf-1",
            "kind": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
            ],
            "applies_to": "seizure type or clinical target, or null",
            "raw_phrase": "source-near phrase for the event",
            "evidence": "exact note substring supporting this event",
            "assertion_status": ["asserted", "negated", "hypothetical", "uncertain"],
            "temporality": ["current", "recent", "historical", "unclear"],
            "certainty": ["high", "medium", "low"],
            "clinical_quantity": {
                "occurrences_low": "number or null",
                "occurrences_high": "number or null",
                "period_low": "number or null",
                "period_high": "number or null",
                "period_unit": ["day", "week", "month", "year", None],
                "vague_count": ["multiple", "rare", "occasional", "frequent", None],
                "clusters_low": "number or null",
                "clusters_high": "number or null",
                "cluster_period_unit": ["day", "week", "month", "year", None],
                "events_per_cluster_low": "number or null",
                "events_per_cluster_high": "number or null",
                "seizure_free_duration_low": "number or null",
                "seizure_free_duration_high": "number or null",
                "seizure_free_duration_unit": ["day", "week", "month", "year", None],
            },
            "model_normalized_clinical_label": "model-owned clinical label, or null",
            "notes": "short note, or empty string",
        },
        "selection_schema": {
            "selected_event_ids": "list of selected event ids",
            "rejected_event_ids": "list of rejected event ids",
            "final_clinical_state": [
                "frequency",
                "seizure_free",
                "unknown_frequency",
                "no_reference",
                "unresolved_multiple",
            ],
            "aggregation_strategy": [
                "highest_current_frequency",
                "recent_window",
                "seizure_free_over_current_event",
                "cluster_total_rate",
                "unknown_boundary",
                "no_reference_boundary",
                "other",
            ],
            "final_clinical_label": "source-near model-selected clinical answer",
            "rationale": "brief clinical reason for the selection",
            "uncertainty_flags": "list of short uncertainty flags",
        },
        "final_answer_schema": {
            "raw_llm_final_label": (
                "normalized model-rendered label, unknown, or "
                "no seizure frequency reference; no prose, inequality symbols, semiology, "
                "cluster modifiers, or explanatory clauses"
            ),
            "raw_llm_final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "raw_llm_monthly_frequency": "model-estimated monthly frequency or null",
            "selected_evidence": (
                "exact copy of one selected event evidence value supporting the final answer; "
                "if multiple events are selected, choose the prediction-bearing event here"
            ),
            "selected_event_ids": (
                "required; exact copy of selection.selected_event_ids; never omit"
            ),
            "rendering_operands": (
                "same shape as clinical_quantity; the final-answer operands the model used "
                "to render raw_llm_final_label from selected_evidence"
            ),
            "arithmetic_trace": (
                "brief source-near arithmetic/rendering trace linking selected_evidence to "
                "raw_llm_final_label"
            ),
            "raw_clinical_summary": "optional short source-near summary; use empty string",
            "final_rationale": "optional short rationale; use empty string",
        },
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_llm_heavy_reasoner_json(
    raw_output: str,
    *,
    note_text: str | None = None,
) -> tuple[LlmHeavyExtractionRecord | None, list[str]]:
    """Parse and validate one LLM-heavy reasoner output."""

    try:
        payload = json.loads(_extract_json_object(raw_output))
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    payload = _repair_payload_shape(payload)
    try:
        extraction = LlmHeavyExtractionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    errors: list[str] = []
    event_ids = {event.event_id for event in extraction.events}
    if not extraction.events:
        errors.append("event_extraction: no events")
    missing_selection_ids = [
        event_id
        for event_id in extraction.selection.selected_event_ids
        if event_id not in event_ids
    ]
    missing_final_ids = [
        event_id
        for event_id in extraction.final_answer.selected_event_ids
        if event_id not in event_ids
    ]
    if missing_selection_ids:
        errors.append(f"selection: unknown selected_event_ids {missing_selection_ids!r}")
    if missing_final_ids:
        errors.append(f"final_answer: unknown selected_event_ids {missing_final_ids!r}")
    if extraction.final_answer.selected_event_ids != extraction.selection.selected_event_ids:
        errors.append("selected_event_trace: final_answer ids differ from selection ids")
    selected_event_evidence = {
        event.evidence
        for event in extraction.events
        if event.event_id in extraction.final_answer.selected_event_ids
    }
    if extraction.final_answer.selected_evidence not in selected_event_evidence:
        errors.append("evidence: selected evidence is not one selected event evidence value")
    if note_text is not None:
        invalid_events = [
            event.event_id
            for event in extraction.events
            if not evidence_is_substring(note_text, event.evidence)
        ]
        if invalid_events:
            errors.append(f"evidence: invalid event evidence for {invalid_events!r}")
        if not evidence_is_substring(note_text, extraction.final_answer.selected_evidence):
            errors.append("evidence: invalid selected evidence")
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
    api_base: str | None = None,
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the LLM-heavy reasoner over a split or prompt-only smoke surface."""

    reuse_raw_outputs = reuse_raw_outputs or {}
    metadata = _run_metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        api_base=api_base,
    )
    metadata["dspy_cache"] = dspy_cache
    metadata["reuse_source"] = reuse_source
    metadata["escalation_reason"] = escalation_reason
    metadata["repair_mode_layers"] = repair_mode_layers(SCORE_LAYER_NAMES)
    program = DspyLlmHeavyReasoner()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
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
                raw_output = str(prediction.llm_heavy_reasoner_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_llm_heavy_reasoner_json(raw_output, note_text=record.note_text)
            if raw_output
            else (None, ["not_run"])
        )
        evidence_summary = _evidence_summary(record.note_text, extraction)
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
                "pipeline_family": PIPELINE_FAMILY,
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
                "repair_mode_layers": repair_mode_layers(SCORE_LAYER_NAMES),
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
    """Summarize LLM-heavy schema smoke rows."""

    component_failures = Counter(
        component
        for row in rows
        for component, status in (row.get("component_status") or {}).items()
        if status != "ok"
    )
    summary: dict[str, Any] = {
        "examples": len(rows),
        "structured_records": sum(bool(row.get("structured_record")) for row in rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "reused_raw_outputs": sum(bool(row.get("reused_raw_output")) for row in rows),
        "parse_or_validation_failures": sum(
            _has_blocking_parse_issue(row.get("parse_errors")) for row in rows
        ),
        "event_evidence_valid": sum(
            int((row.get("evidence_summary") or {}).get("event_evidence_valid", 0)) for row in rows
        ),
        "event_evidence_total": sum(
            int((row.get("evidence_summary") or {}).get("event_evidence_total", 0)) for row in rows
        ),
        "selected_evidence_valid": sum(
            int(bool((row.get("evidence_summary") or {}).get("selected_evidence_valid")))
            for row in rows
        ),
        "selected_event_trace_mismatches": sum(
            any(
                str(error).startswith("selected_event_trace:")
                for error in row.get("parse_errors") or []
            )
            for row in rows
        ),
        "rendering_operands_present": sum(
            int(_has_rendering_operands(row.get("structured_record"))) for row in rows
        ),
        "arithmetic_trace_present": sum(
            int(_has_arithmetic_trace(row.get("structured_record"))) for row in rows
        ),
        "component_failures": dict(sorted(component_failures.items())),
        "repair_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
    }
    for layer in SCORE_LAYER_NAMES:
        layer_summary = _layer_summary(rows, layer)
        for key, value in layer_summary.items():
            summary[f"{layer}_{key}"] = value
    side_car_deltas = _side_car_deltas(rows)
    summary.update(side_car_deltas)
    summary["decision_0006_outcome"] = _decision_0006_outcome(summary)
    return summary


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    return load_raw_outputs_by_source_index(path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    /,
    *,
    jsonl_path: Path,
) -> None:
    """Write a compact Markdown smoke report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    outcome = str(summary.get("decision_0006_outcome", "revise"))
    prompt_label = _prompt_display_label()
    lines = [
        f"# Gan 2026 LLM-Heavy Clinical Frequency Reasoner {prompt_label}",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Pipeline family: `{PIPELINE_FAMILY}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Rows: {summary.get('examples', 0)}",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        (
            "- Claim language: LLM-heavy validation development result; deterministic "
            "selected-evidence arithmetic and benchmark-aligned layers are side-cars."
        ),
        f"- Decision 0006 outcome: `{outcome}`",
        "",
        "## Smoke Summary",
        "",
        (
            f"- Structured records: {summary.get('structured_records', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- Parse/schema failures: {summary.get('parse_or_validation_failures', 0)}",
        (
            f"- Selected evidence valid: {summary.get('selected_evidence_valid', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        (
            f"- Rendering operands present: {summary.get('rendering_operands_present', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        (
            f"- Arithmetic/rendering traces present: {summary.get('arithmetic_trace_present', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        (
            f"- Event evidence valid: {summary.get('event_evidence_valid', 0)}/"
            f"{summary.get('event_evidence_total', 0)}"
        ),
        f"- Selected-event trace mismatches: {summary.get('selected_event_trace_mismatches', 0)}",
        "",
        "## Score Layers",
        "",
    ]
    for layer in SCORE_LAYER_NAMES:
        lines.append(
            f"- `{layer}`: scorable {summary.get(f'{layer}_scorable', 0)}, "
            f"Purist {summary.get(f'{layer}_purist_correct', 0)}/{summary.get('examples', 0)} "
            f"({summary.get(f'{layer}_purist_accuracy', 0.0):.4f}), "
            f"Pragmatic {summary.get(f'{layer}_pragmatic_correct', 0)}/"
            f"{summary.get('examples', 0)} "
            f"({summary.get(f'{layer}_pragmatic_accuracy', 0.0):.4f})"
        )
    lines.extend(
        [
            "",
            "## Decision 0006 Stop Rules",
            "",
            (
                f"- Raw parser-compatible labels: {summary.get('raw_llm_scorable', 0)}/"
                f"{summary.get('examples', 0)}"
            ),
            (
                f"- Raw model-owned Purist: {summary.get('raw_llm_purist_correct', 0)}/"
                f"{summary.get('examples', 0)}"
            ),
            (
                "- Deterministic selected-evidence arithmetic raw-wrong to correct: "
                f"{summary.get('selected_evidence_arithmetic_raw_wrong_to_correct', 0)}"
            ),
            (
                "- Deterministic selected-evidence arithmetic raw-correct to wrong: "
                f"{summary.get('selected_evidence_arithmetic_raw_correct_to_wrong', 0)}"
            ),
            "",
            "## Row Review",
            "",
            *_row_review_lines(rows),
            "",
            "## Failure Taxonomy",
            "",
            *_failure_taxonomy_lines(rows),
            "",
            "## Interpretation",
            "",
            _interpretation_text(outcome),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _score_layers(
    record: GanFrequencyRecord,
    extraction: LlmHeavyExtractionRecord | None,
) -> dict[str, dict[str, Any]]:
    raw_label = _raw_final_label(extraction)
    format_label = repair_prediction_label_format_preserving(raw_label) if raw_label else None
    arithmetic_label = (
        repair_prediction_label_with_evidence(
            format_label,
            extraction.final_answer.selected_evidence,
        )
        if extraction and format_label
        else None
    )
    benchmark_label = repair_prediction_label(raw_label) if raw_label else None
    oracle_label = _oracle_format_upper_bound_label(extraction, format_label)
    return {
        "raw_llm": _score_label(record, raw_label, repair_mode="raw_llm"),
        "format_only": _score_label(record, format_label, repair_mode="format_only"),
        "selected_evidence_arithmetic": _score_label(
            record,
            arithmetic_label,
            repair_mode="selected_evidence_arithmetic",
        ),
        "benchmark_aligned": _score_label(
            record,
            benchmark_label,
            repair_mode="benchmark_aligned",
        ),
        "oracle_format_upper_bound": _score_label(
            record,
            oracle_label,
            repair_mode="oracle_format_upper_bound",
        ),
    }


def _raw_final_label(extraction: LlmHeavyExtractionRecord | None) -> str | None:
    if extraction is None:
        return None
    label = extraction.final_answer.raw_llm_final_label
    if label:
        return label
    if extraction.final_answer.raw_llm_final_kind == "unknown":
        return "unknown"
    if extraction.final_answer.raw_llm_final_kind == "no_reference":
        return "no seizure frequency reference"
    return None


def _oracle_format_upper_bound_label(
    extraction: LlmHeavyExtractionRecord | None,
    format_label: str | None,
) -> str | None:
    if extraction is None:
        return None
    if format_label:
        return format_label
    state = extraction.selection.final_clinical_state
    if state == "unknown_frequency" or state == "unresolved_multiple":
        return "unknown"
    if state == "no_reference":
        return "no seizure frequency reference"
    return repair_prediction_label_format_preserving(extraction.selection.final_clinical_label)


def _score_label(
    record: GanFrequencyRecord,
    label: str | None,
    *,
    repair_mode: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "final_label": label,
        "scorable": False,
        "repair_mode_metadata": repair_mode_layers((repair_mode,))[repair_mode],
    }
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


def _repair_changes(score_layers: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    raw_label = score_layers["raw_llm"].get("final_label")
    for layer in SCORE_LAYER_NAMES[1:]:
        current = score_layers[layer].get("final_label")
        if isinstance(raw_label, str) and isinstance(current, str) and current != raw_label:
            changes.append({"layer": layer, "before": raw_label, "after": current})
    return changes


def _evidence_summary(
    note_text: str,
    extraction: LlmHeavyExtractionRecord | None,
) -> dict[str, Any]:
    if extraction is None:
        return _empty_evidence_summary()
    invalid_events = [
        {"event_id": event.event_id, "evidence": event.evidence}
        for event in extraction.events
        if not evidence_is_substring(note_text, event.evidence)
    ]
    selected_valid = evidence_is_substring(note_text, extraction.final_answer.selected_evidence)
    selected_event_evidence_valid = extraction.final_answer.selected_evidence in {
        event.evidence
        for event in extraction.events
        if event.event_id in extraction.final_answer.selected_event_ids
    }
    return {
        "event_evidence_valid": len(extraction.events) - len(invalid_events),
        "event_evidence_total": len(extraction.events),
        "event_evidence_invalid": invalid_events,
        "selected_evidence_valid": selected_valid,
        "selected_event_evidence_valid": selected_event_evidence_valid,
        "selected_evidence": extraction.final_answer.selected_evidence,
    }


def _empty_evidence_summary() -> dict[str, Any]:
    return {
        "event_evidence_valid": 0,
        "event_evidence_total": 0,
        "event_evidence_invalid": [],
        "selected_evidence_valid": False,
        "selected_event_evidence_valid": False,
        "selected_evidence": None,
    }


def _component_status(
    *,
    extraction: LlmHeavyExtractionRecord | None,
    parse_errors: Sequence[str],
    evidence_summary: Mapping[str, Any],
    score_layers: Mapping[str, Mapping[str, Any]],
    call_error: str | None,
) -> dict[str, str]:
    status = {
        "event_extraction": "ok",
        "clinical_selection": "ok",
        "final_schema_rendering": "ok",
        "parse_schema": "ok",
        "evidence_exactness": "ok",
        "scorer_format": "ok",
        "selected_event_trace": "ok",
    }
    if call_error or _has_blocking_parse_issue(parse_errors):
        status["parse_schema"] = "fail"
    if extraction is None:
        status["event_extraction"] = "fail"
        status["clinical_selection"] = "fail"
        status["final_schema_rendering"] = "fail"
        status["scorer_format"] = "fail"
        return status
    if not extraction.events or any(
        str(error).startswith("event_extraction:") for error in parse_errors
    ):
        status["event_extraction"] = "fail"
    if any(str(error).startswith("selection:") for error in parse_errors):
        status["clinical_selection"] = "fail"
    if any(str(error).startswith("final_answer:") for error in parse_errors):
        status["final_schema_rendering"] = "fail"
    if any(str(error).startswith("selected_event_trace:") for error in parse_errors):
        status["selected_event_trace"] = "fail"
    if evidence_summary.get("event_evidence_valid") != evidence_summary.get("event_evidence_total"):
        status["event_extraction"] = "fail"
        status["evidence_exactness"] = "fail"
    if not evidence_summary.get("selected_evidence_valid"):
        status["final_schema_rendering"] = "fail"
        status["evidence_exactness"] = "fail"
    if not evidence_summary.get("selected_event_evidence_valid"):
        status["final_schema_rendering"] = "fail"
        status["evidence_exactness"] = "fail"
    if not score_layers["raw_llm"].get("scorable"):
        status["scorer_format"] = "fail"
    if (
        extraction.final_answer.rendering_operands is None
        or not extraction.final_answer.arithmetic_trace
    ):
        status["final_schema_rendering"] = "fail"
    return status


def _has_rendering_operands(structured_record: Any) -> bool:
    if not isinstance(structured_record, Mapping):
        return False
    final_answer = structured_record.get("final_answer")
    if not isinstance(final_answer, Mapping):
        return False
    operands = final_answer.get("rendering_operands")
    if not isinstance(operands, Mapping):
        return False
    return any(value is not None for value in operands.values())


def _has_arithmetic_trace(structured_record: Any) -> bool:
    if not isinstance(structured_record, Mapping):
        return False
    final_answer = structured_record.get("final_answer")
    if not isinstance(final_answer, Mapping):
        return False
    trace = final_answer.get("arithmetic_trace")
    return isinstance(trace, str) and bool(trace.strip())


def _side_car_deltas(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    raw_wrong_to_correct = 0
    raw_correct_to_wrong = 0
    for row in rows:
        layers = row.get("score_layers") or {}
        raw = layers.get("raw_llm") or {}
        arithmetic = layers.get("selected_evidence_arithmetic") or {}
        raw_correct = bool(raw.get("purist_correct"))
        arithmetic_correct = bool(arithmetic.get("purist_correct"))
        if not raw_correct and arithmetic_correct:
            raw_wrong_to_correct += 1
        if raw_correct and not arithmetic_correct:
            raw_correct_to_wrong += 1
    return {
        "selected_evidence_arithmetic_raw_wrong_to_correct": raw_wrong_to_correct,
        "selected_evidence_arithmetic_raw_correct_to_wrong": raw_correct_to_wrong,
    }


def _decision_0006_outcome(summary: Mapping[str, Any]) -> str:
    examples = int(summary.get("examples", 0))
    if examples == 0:
        return "reject"
    blocking_reject = any(
        (
            int(summary.get("structured_records", 0)) < examples,
            int(summary.get("raw_llm_scorable", 0)) < 24,
            int(summary.get("selected_evidence_valid", 0)) < 23,
            int(summary.get("selected_event_trace_mismatches", 0)) > 0,
            int(summary.get("selected_evidence_arithmetic_raw_wrong_to_correct", 0)) > 5,
            int(summary.get("rendering_operands_present", 0)) < examples,
            int(summary.get("arithmetic_trace_present", 0)) < examples,
        )
    )
    if blocking_reject:
        return "reject"
    if int(summary.get("raw_llm_purist_correct", 0)) >= 20:
        return "promote_to_50"
    return "revise"


def _row_review_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for row in rows:
        layers = row.get("score_layers") or {}
        raw = layers.get("raw_llm") or {}
        arithmetic = layers.get("selected_evidence_arithmetic") or {}
        if raw.get("purist_correct") and arithmetic.get("purist_correct"):
            continue
        if raw.get("purist_correct") and not arithmetic.get("purist_correct"):
            status = "side-car regression"
        elif not raw.get("purist_correct") and arithmetic.get("purist_correct"):
            status = "side-car correction"
        else:
            status = "raw miss"
        lines.append(
            "- "
            f"{row.get('source_row_index')}: {status}; "
            f"gold `{((row.get('reference') or {}).get('gold_normalized_label'))}`; "
            f"raw `{raw.get('final_label')}`; "
            f"selected-evidence arithmetic `{arithmetic.get('final_label')}`; "
            f"taxonomy `{_failure_family(row)}`"
        )
    if not lines:
        return ["- No raw misses or selected-evidence side-car regressions."]
    return lines


def _failure_taxonomy_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    counts = Counter(_failure_family(row) for row in rows)
    return [f"- `{family}`: {count}" for family, count in sorted(counts.items())]


def _failure_family(row: Mapping[str, Any]) -> str:
    if _has_blocking_parse_issue(row.get("parse_errors")):
        return "parser/schema issue"
    evidence_summary = row.get("evidence_summary") or {}
    if not evidence_summary.get("selected_evidence_valid"):
        return "wrong selected fact"
    if any(
        str(error).startswith("selected_event_trace:") for error in row.get("parse_errors") or []
    ):
        return "wrong selected fact"
    layers = row.get("score_layers") or {}
    raw = layers.get("raw_llm") or {}
    arithmetic = layers.get("selected_evidence_arithmetic") or {}
    benchmark = layers.get("benchmark_aligned") or {}
    if not raw.get("scorable"):
        return "parser/schema issue"
    if not raw.get("purist_correct") and arithmetic.get("purist_correct"):
        return "wrong arithmetic/rendering"
    if not raw.get("purist_correct") and benchmark.get("purist_correct"):
        return "benchmark-format convention"
    if not raw.get("purist_correct"):
        return "wrong selected fact"
    if raw.get("purist_correct") and not arithmetic.get("purist_correct"):
        return "side-car regression"
    return "no raw failure"


def _interpretation_text(outcome: str) -> str:
    if outcome == "promote_to_50":
        return (
            "The decision-0006 validation25 smoke passes its predeclared stop rules. "
            "Escalation to validation50 is allowed, with deterministic arithmetic still "
            "reported only as a side-car."
        )
    if outcome == "reject":
        return (
            "The decision-0006 validation25 smoke fails at least one hard stop rule. "
            "Do not escalate this v2 prompt to validation50; revise the prompt/schema or "
            "keep selected-evidence arithmetic as an explicit deterministic component."
        )
    return (
        "The decision-0006 validation25 smoke is interpretable but not promotable. "
        "Revise before validation50 unless row review shows that all raw misses are "
        "predeclared benchmark-format conventions rather than arithmetic/rendering failures."
    )


def _prompt_display_label() -> str:
    prefix = "gan2026_llm_heavy_clinical_frequency_reasoner_"
    label = PROMPT_VERSION.removeprefix(prefix)
    return label.upper().replace("_", " ")


def _layer_summary(rows: Sequence[Mapping[str, Any]], layer: str) -> dict[str, Any]:
    count = len(rows)
    layer_rows = [(row.get("score_layers") or {}).get(layer) or {} for row in rows]
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


def _repair_payload_shape(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    if "final_answer" not in repaired and isinstance(repaired.get("scoring_schema"), dict):
        repaired["final_answer"] = repaired["scoring_schema"]
    events = repaired.get("events")
    if isinstance(events, list):
        repaired["events"] = [_repair_event_payload(event) for event in events]
    selection = repaired.get("selection")
    if isinstance(selection, dict):
        repaired["selection"] = _repair_selection_payload(selection)
    final_answer = repaired.get("final_answer")
    if isinstance(final_answer, dict):
        repaired["final_answer"] = _repair_final_answer_payload(final_answer)
    return repaired


def _repair_event_payload(event: Any) -> Any:
    if not isinstance(event, dict):
        return event
    original_certainty = event.get("certainty")
    repaired = repair_decision_payload(dict(event))
    for key in ("kind", "assertion_status", "temporality", "certainty"):
        _repair_scalar_list_alias(repaired, key)
    if "raw_phrase" not in repaired and isinstance(repaired.get("raw_value"), str):
        repaired["raw_phrase"] = repaired["raw_value"]
    repaired.setdefault("raw_phrase", repaired.get("evidence", ""))
    repaired.setdefault("notes", "")
    if original_certainty in {"high", "medium", "low"}:
        repaired["certainty"] = original_certainty
    else:
        repaired.setdefault("certainty", repaired.pop("confidence", "medium"))
    repaired.setdefault("clinical_quantity", {})
    if isinstance(repaired["clinical_quantity"], dict):
        repaired["clinical_quantity"] = _repair_clinical_quantity_payload(
            repaired["clinical_quantity"]
        )
    if repaired.get("assertion_status") == "unknown":
        repaired["assertion_status"] = "uncertain"
    return {
        key: value for key, value in repaired.items() if key in LlmHeavyEventRecord.model_fields
    }


def _repair_selection_payload(selection: Any) -> Any:
    repaired = dict(selection)
    _repair_scalar_list_alias(repaired, "final_clinical_state")
    _repair_scalar_list_alias(repaired, "aggregation_strategy")
    if "final_clinical_state" not in repaired and "final_kind" in repaired:
        repaired["final_clinical_state"] = repaired["final_kind"]
    if repaired.get("final_clinical_state") == "unknown":
        repaired["final_clinical_state"] = "unknown_frequency"
    if "final_clinical_label" not in repaired and "final_label" in repaired:
        repaired["final_clinical_label"] = repaired["final_label"]
    repaired.setdefault("rejected_event_ids", [])
    repaired.setdefault("aggregation_strategy", "other")
    repaired.setdefault("rationale", "")
    repaired.setdefault("uncertainty_flags", [])
    return {
        key: value for key, value in repaired.items() if key in LlmHeavySelectionRecord.model_fields
    }


def _repair_final_answer_payload(final_answer: Any) -> Any:
    repaired = dict(final_answer)
    repaired = repair_decision_payload(repaired)
    _repair_scalar_list_alias(repaired, "raw_llm_final_kind")
    if repaired.get("raw_llm_final_kind") == "cluster_frequency":
        repaired["raw_llm_final_kind"] = "frequency"
    if "raw_llm_final_label" not in repaired and "final_label" in repaired:
        repaired["raw_llm_final_label"] = repaired["final_label"]
    if "raw_llm_final_kind" not in repaired and "final_kind" in repaired:
        repaired["raw_llm_final_kind"] = repaired["final_kind"]
    if "selected_evidence" not in repaired and "evidence" in repaired:
        repaired["selected_evidence"] = repaired["evidence"]
    repaired.setdefault("raw_clinical_summary", repaired.get("clinical_summary", ""))
    repaired.setdefault("raw_llm_monthly_frequency", None)
    repaired.setdefault("supporting_event_ids", [])
    repaired.setdefault("combined_rationale", "")
    if isinstance(repaired.get("rendering_operands"), dict):
        repaired["rendering_operands"] = _repair_clinical_quantity_payload(
            repaired["rendering_operands"]
        )
    if "rendering_operands" not in repaired:
        repaired["rendering_operands"] = None
    repaired.setdefault("arithmetic_trace", "")
    repaired.setdefault("final_rationale", repaired.get("rationale", ""))
    return {
        key: value
        for key, value in repaired.items()
        if key in LlmHeavyFinalAnswerRecord.model_fields
    }


def _repair_clinical_quantity_payload(quantity: dict[str, Any]) -> dict[str, Any]:
    repaired = dict(quantity)
    for key in ("period_unit", "cluster_period_unit", "seizure_free_duration_unit", "vague_count"):
        _repair_scalar_list_alias(repaired, key)
    for key in ("period_unit", "cluster_period_unit", "seizure_free_duration_unit"):
        if repaired.get(key) not in {"day", "week", "month", "year", None}:
            repaired[key] = None
    if repaired.get("vague_count") == "many":
        repaired["vague_count"] = "multiple"
    if repaired.get("vague_count") in {"most days", "several"}:
        repaired["vague_count"] = "multiple"
    return repaired


def _repair_scalar_list_alias(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if isinstance(value, list) and value:
        payload[key] = value[0]


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for error in errors or []
    )


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
        "raw_llm_scorable": metadata["summary"]["raw_llm_scorable"],
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
    api_base: str | None = None,
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
        api_base=api_base,
        row_count=len(records),
        extra={
            "pipeline_name": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "score_layers_to_report": list(SCORE_LAYER_NAMES),
            "schema_smoke_stop_rule": {
                "schema_valid_rows_minimum": "25/25",
                "raw_parser_compatible_minimum": "24/25",
                "selected_evidence_exactness_minimum": "23/25",
                "selected_event_trace_mismatches_maximum": "0/25",
                "raw_model_owned_purist_minimum": "20/25",
                "deterministic_arithmetic_gap_maximum": "5 rows",
            },
        },
    )
