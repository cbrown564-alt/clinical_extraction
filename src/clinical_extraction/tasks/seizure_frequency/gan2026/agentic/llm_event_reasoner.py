"""LLM-owned reasoning pass over saved Gan 2026 structured events.

This is the Stage 1 scaffold for the test-0.85 plan. The prediction-bearing
component is the second-pass LLM decision. Deterministic code only prepares a
sanitized structured-event prompt, performs format-only label repair, validates
evidence substrings, and scores against validation gold after the model answer.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import locate_evidence, score_evidence_set
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_decision_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_llm_event_reasoner_v1_3"
PIPELINE_FAMILY = "llm_event_reasoner"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_three_way_comparison_validation750_hybrid_structured_events_"
    "gpt41mini_2026-06-07.jsonl"
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_llm_event_reasoner_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_llm_event_reasoner_validation.md")
STAGE_ID = "llm_event_reasoner"

DecisionKind = Literal[
    "frequency",
    "seizure_free",
    "unknown",
    "no_reference",
    "unresolved_multiple",
]
Uncertainty = Literal["low", "medium", "high"]
UNCERTAINTY_VALUES = ("low", "medium", "high")
DecisionAttribution = Literal[
    "llm_selected_tool_rendered",
    "llm_selected_format_repaired",
    "llm_original_structured_event_kept",
]
DECISION_ATTRIBUTION_VALUES = (
    "llm_selected_tool_rendered",
    "llm_selected_format_repaired",
    "llm_original_structured_event_kept",
)


class ToolTrace(BaseModel):
    """Optional model-reported tool trace for V2-compatible decisions."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str
    status: str
    input_summary: str | None = None
    output_summary: str | None = None


class ReasonedFrequencyDecision(BaseModel):
    """Common prediction schema from the test-0.85 plan."""

    model_config = ConfigDict(extra="forbid")

    final_label: str
    final_kind: DecisionKind
    selected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    rejected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    boundary_profile: tuple[str, ...] = Field(default_factory=tuple)
    calculation_trace: str | None = None
    clinical_rationale: str
    uncertainty: Uncertainty
    tool_calls: tuple[ToolTrace, ...] = Field(default_factory=tuple)
    attribution: DecisionAttribution


class ParsedReasonedDecision(BaseModel):
    """Raw, format-only, and final views of one model output."""

    model_config = ConfigDict(extra="forbid")

    raw_decision: ReasonedFrequencyDecision | None
    format_only_decision: ReasonedFrequencyDecision | None
    final_decision: ReasonedFrequencyDecision | None
    parse_errors: list[str] = Field(default_factory=list)
    format_repair_events: list[dict[str, Any]] = Field(default_factory=list)


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool,
    api_base: str | None,
    escalation_reason: str | None,
    progress_every: int | None,
    checkpoint_jsonl_path: Path | None,
    checkpoint_report_path: Path | None,
    candidate_set_jsonl_path: Path | None = None,
    structured_event_jsonl_path: Path | None = None,
    structured_event_rows: Sequence[Mapping[str, Any]] | None = None,
    structured_event_source_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run or prompt-smoke a second-pass LLM reasoner over saved SE rows."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
        AgenticSplitHooks,
        SplitRunParams,
        StructuredEventSplitContext,
        dispatch_registered_split,
    )

    del escalation_reason, candidate_set_jsonl_path
    source_path = (
        structured_event_source_path
        or structured_event_jsonl_path
        or DEFAULT_STRUCTURED_EVENT_JSONL_PATH
    )
    params = SplitRunParams(
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
    )
    hooks = AgenticSplitHooks(
        prompt_version=PROMPT_VERSION,
        metadata_extra={
            "artifact_kind": "gan2026_llm_event_reasoner_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": PROMPT_VERSION,
            "structured_event_source_role": (
                "pure structured-event V0 comparator and input substrate; not "
                "a deterministic final-label floor"
            ),
            "claim_boundary": (
                "validation-development Stage 1 scaffold; no holdout use, no "
                "row-level test inspection, and no benchmark claim"
            ),
        },
        build_row=_build_row,
        summarize_rows=summarize_rows,
        gate_interpretation=gate_interpretation,
        write_report=write_report,
        progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
    )
    structured_event_context = StructuredEventSplitContext(
        default_structured_event_jsonl_path=DEFAULT_STRUCTURED_EVENT_JSONL_PATH,
        structured_event_jsonl_path=structured_event_jsonl_path,
        structured_event_rows=structured_event_rows,
        structured_event_source_path=source_path,
        rows_by_source_index=_rows_by_source_index,
    )
    return dispatch_registered_split(
        STAGE_ID,
        records,
        params=params,
        hooks=hooks,
        structured_event_context=structured_event_context,
    )


def build_prompt_input(
    record: GanFrequencyRecord,
    structured_event_row: Mapping[str, Any] | None,
) -> str:
    """Build a model-facing payload without row IDs, gold labels, split, or rules top."""

    structured_input = inspect_structured_events(structured_event_row)
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 structured-event clinical frequency reasoning",
        "variant": "V1_single_llm_event_reasoner",
        "instructions": [
            "Select the final current seizure-frequency interpretation from the structured events.",
            "The original structured-event final answer is an LLM answer you may keep if correct.",
            (
                "Use only the event table and evidence contexts below; do not use "
                "outside final-answer sources, row IDs, split membership, or scoring metadata."
            ),
            "Return exactly one strict JSON object matching the ReasonedFrequencyDecision schema.",
            (
                "The LLM owns final_kind, selected_event_ids, rejected_event_ids, "
                "and clinical_rationale."
            ),
            "Use frequency when current or recent recurring countable evidence is present.",
            "Use unknown when seizure-frequency evidence exists but cannot be converted.",
            "Use no_reference only when no usable seizure-frequency evidence exists.",
            (
                "For seizure-free claims, require absence-since evidence and no "
                "conflicting current frequency."
            ),
            (
                "For clusters, separate cluster cadence from events per cluster before "
                "choosing a label."
            ),
            "For multiple active semiologies, choose the highest current clinically active burden.",
            "Evidence entries should be exact substrings from the note when possible.",
            "Use spaces in labels, for example 'multiple per day', not underscores.",
            ("Copy evidence with exact capitalization and punctuation from the note."),
            (
                "final_label must be a valid Gan label only: unknown, no seizure "
                "frequency reference, seizure free, multiple per day/week/month/year, "
                "or '<number> [to <number>] per day/week/month/year'. Do not include "
                "seizure type, diagnosis, dates, or phrases such as 'since last review'."
            ),
            (
                "If the selected event has a renderable normalized_candidate label, "
                "prefer that normalized_label unless your calculation_trace gives a "
                "different renderable frequency from exact evidence."
            ),
            (
                "Keep original_final.final_label when it is renderable and supported "
                "by one or more selected events; replace it only when the event table "
                "and exact evidence clearly support a better Gan label."
            ),
            (
                "Preserve cluster labels when the selected event contains both cluster "
                "cadence and events-per-cluster burden; do not collapse a cluster "
                "label to cadence alone."
            ),
            (
                "Absence-since evidence is renderable as seizure_free when it states "
                "no seizures/events since a date or duration and no current/recent "
                "frequency evidence conflicts with it. Do not change such a supported "
                "seizure_free label to unknown merely because it is not a recurring "
                "cadence."
            ),
            (
                "Do not select seizure_free when any asserted current or recent "
                "frequency event remains active, unless that frequency is explicitly "
                "historical or resolved before the absence-since period."
            ),
            (
                "Counts over vague intervals such as 'since last review' are not "
                "renderable final labels unless the interval length is explicit; use a "
                "recurring cadence when present, otherwise use unknown."
            ),
            (
                "final_kind, uncertainty, and attribution must each be one string, "
                "not an array of options."
            ),
        ],
        "required_output_schema": {
            "final_label": "Gan-style label string",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": "list of event IDs selected from the event table",
            "rejected_event_ids": "list of event IDs explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the final choice",
            "boundary_profile": "list of targeted profile keys, such as freq_category_shift",
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief clinical rationale",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for V1 unless a tool was actually called",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "structured_event_input": structured_input,
        "raw_evidence_contexts": _evidence_contexts(record.note_text, structured_event_row),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def inspect_structured_events(
    structured_event_row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return compact V0 event information without gold or deterministic-top labels."""

    if structured_event_row is None:
        return {
            "event_table": [],
            "original_final": None,
            "input_warnings": ["missing_structured_event_row"],
        }
    structured_record = dict(structured_event_row.get("structured_record") or {})
    events = [
        _event_table_row(event, structured_event_row)
        for event in structured_record.get("events") or []
        if isinstance(event, Mapping)
    ]
    selection = dict(structured_record.get("selection") or {})
    original_final = {
        "final_label": selection.get("final_label"),
        "final_kind": selection.get("final_kind"),
        "selected_event_ids": list(selection.get("selected_event_ids") or []),
        "evidence": selection.get("evidence"),
        "confidence": selection.get("confidence"),
        "rationale": selection.get("rationale"),
    }
    return {
        "event_table": events,
        "original_final": original_final,
        "input_warnings": [],
    }


def parse_reasoned_decision_json(raw_output: str) -> ParsedReasonedDecision:
    """Parse a model decision and expose raw versus format-only repair layers."""

    parse_errors: list[str] = []
    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
            _extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return ParsedReasonedDecision(
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=[f"invalid_json: {exc.msg}"],
        )
    parse_errors.extend(dialect_notes)
    payload = _filter_decision_payload(repair_decision_payload(raw_payload))
    payload, shape_notes = _repair_decision_shape(payload)
    parse_errors.extend(shape_notes)
    try:
        raw_decision = ReasonedFrequencyDecision.model_validate(payload)
    except ValidationError as exc:
        return ParsedReasonedDecision(
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=[*parse_errors, f"schema_validation_error: {exc.errors()[0]['msg']}"],
        )

    repair_trace = repair_prediction_label_format_preserving_with_trace(raw_decision.final_label)
    repair_events = [_repair_event_to_dict(event) for event in repair_trace.events]
    format_decision = raw_decision
    if repair_trace.final_label != raw_decision.final_label:
        parse_errors.append(
            "final_label_format_repaired: "
            f"{raw_decision.final_label!r} -> {repair_trace.final_label!r}"
        )
        format_decision = raw_decision.model_copy(
            update={
                "final_label": repair_trace.final_label,
                "attribution": "llm_selected_format_repaired",
            }
        )
    try:
        label_to_frequency_record(format_decision.final_label)
    except ValueError as exc:
        parse_errors.append(f"unscorable_final_label: {exc}")
    return ParsedReasonedDecision(
        raw_decision=raw_decision,
        format_only_decision=format_decision,
        final_decision=format_decision,
        parse_errors=parse_errors,
        format_repair_events=repair_events,
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize V1 rows across raw, format-only, final, and V0 layers."""

    summary: dict[str, Any] = {
        "rows": len(rows),
        "prediction_bearing_rows": 0,
        "model_calls_attempted": 0,
        "call_failures": 0,
        "parse_or_validation_failures": 0,
        "evidence_exact_substrings": 0,
        "v0_purist_correct": 0,
        "v0_pragmatic_correct": 0,
        "raw_model_purist_correct": 0,
        "raw_model_pragmatic_correct": 0,
        "format_only_purist_correct": 0,
        "format_only_pragmatic_correct": 0,
        "final_purist_correct": 0,
        "final_pragmatic_correct": 0,
        "format_repair_rows": 0,
        "wrong_to_correct_vs_v0": 0,
        "correct_to_wrong_vs_v0": 0,
        "changed_labels_vs_v0": 0,
    }
    final_labels: Counter[str] = Counter()
    for row in rows:
        summary["prediction_bearing_rows"] += int(row.get("decision_record") is not None)
        summary["model_calls_attempted"] += int(row.get("model_call_attempted") is True)
        summary["call_failures"] += int(row.get("call_error") is not None)
        summary["parse_or_validation_failures"] += int(
            _has_blocking_parse_issue(row.get("parse_errors"))
        )
        summary["evidence_exact_substrings"] += int(bool(row.get("evidence_valid")))
        v0_comparison = dict(dict(row.get("v0_reference") or {}).get("comparison") or {})
        summary["v0_purist_correct"] += int(bool(v0_comparison.get("purist_correct")))
        summary["v0_pragmatic_correct"] += int(bool(v0_comparison.get("pragmatic_correct")))
        for layer_name, summary_prefix in (
            ("raw_model", "raw_model"),
            ("format_only", "format_only"),
            ("final", "final"),
        ):
            comparison = dict(
                dict(dict(row.get("score_layers") or {}).get(layer_name) or {}).get("comparison")
                or {}
            )
            summary[f"{summary_prefix}_purist_correct"] += int(
                bool(comparison.get("purist_correct"))
            )
            summary[f"{summary_prefix}_pragmatic_correct"] += int(
                bool(comparison.get("pragmatic_correct"))
            )
        transition = dict(row.get("transition_vs_v0") or {})
        summary["wrong_to_correct_vs_v0"] += int(
            transition.get("purist_transition") == "wrong_to_correct"
        )
        summary["correct_to_wrong_vs_v0"] += int(
            transition.get("purist_transition") == "correct_to_wrong"
        )
        summary["changed_labels_vs_v0"] += int(bool(transition.get("label_changed")))
        summary["format_repair_rows"] += int(bool(row.get("format_repair_events")))
        final_label = dict(dict(row.get("score_layers") or {}).get("final") or {}).get(
            "final_label"
        )
        if final_label is not None:
            final_labels[str(final_label)] += 1
    summary["net_purist_gain_vs_v0"] = (
        summary["wrong_to_correct_vs_v0"] - summary["correct_to_wrong_vs_v0"]
    )
    summary["changed_label_precision_vs_v0"] = (
        round(summary["wrong_to_correct_vs_v0"] / summary["changed_labels_vs_v0"], 4)
        if summary["changed_labels_vs_v0"]
        else None
    )
    summary["final_labels"] = dict(sorted(final_labels.items()))
    return summary


def gate_interpretation(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Interpret the Stage 1 contract gate without promoting a model score."""

    rows = int(summary.get("rows", 0))
    prediction_bearing_rows = int(summary.get("prediction_bearing_rows", 0))
    if rows > 0 and prediction_bearing_rows == 0:
        return {
            "status": "prompt_only_no_prediction",
            "rows": rows,
            "parse_or_validation_failure_rate": 0.0,
            "max_parse_or_validation_failure_rate": 0.04,
            "evidence_exact_rate": 0.0,
            "min_evidence_exact_rate": 0.90,
            "interpretation": (
                "Prompt-only scaffold generated without model calls; run live "
                "validation25 before applying contract promotion gates."
            ),
        }
    parse_failures = int(summary.get("parse_or_validation_failures", 0))
    evidence_exact = int(summary.get("evidence_exact_substrings", 0))
    parse_rate = parse_failures / rows if rows else 0.0
    evidence_rate = evidence_exact / rows if rows else 0.0
    passes_contract = rows > 0 and parse_rate <= 0.04 and evidence_rate >= 0.90
    return {
        "status": "pass_contract_smoke" if passes_contract else "needs_contract_work",
        "rows": rows,
        "parse_or_validation_failure_rate": round(parse_rate, 4),
        "max_parse_or_validation_failure_rate": 0.04,
        "evidence_exact_rate": round(evidence_rate, 4),
        "min_evidence_exact_rate": 0.90,
        "interpretation": (
            "Contract smoke passes; evaluate against hard-slice gates next."
            if passes_contract
            else "Do not promote; fix schema/evidence contract before hard-slice claims."
        ),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = dict(metadata.get("summary") or {})
    gate = dict(metadata.get("gate") or {})
    lines = [
        "# Gan 2026 LLM Event Reasoner",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation-development Stage 1 structured-event reasoning artifact.",
        "The model sees saved LLM structured events, not deterministic final-label candidates.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: V1 single LLM event reasoner scaffold.",
        f"- Rows: {summary.get('rows', 0)}",
        "- Split: `validation`, manifest `gan2026_split_v1`.",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Structured-event source: `{metadata.get('structured_event_source_path')}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
        f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
        f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
        (f"- V0 Purist: {summary.get('v0_purist_correct', 0)}/{summary.get('rows', 0)}"),
        (
            f"- Raw model Purist: {summary.get('raw_model_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Format-only Purist: {summary.get('format_only_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (f"- Final Purist: {summary.get('final_purist_correct', 0)}/{summary.get('rows', 0)}"),
        f"- Net Purist gain vs V0: {summary.get('net_purist_gain_vs_v0', 0)}",
        (f"- Changed-label precision vs V0: {summary.get('changed_label_precision_vs_v0')}"),
        "",
        "## Gate",
        "",
        f"- Status: `{gate.get('status')}`",
        f"- Interpretation: {gate.get('interpretation')}",
        "",
        "## Claim Boundary",
        "",
        str(metadata.get("claim_boundary", "")),
        "",
        "## Rows",
        "",
        "| Row | V0 | Raw | Format-only | Final | Transition | Evidence exact | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        layers = dict(row.get("score_layers") or {})
        notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        lines.append(
            f"| {row.get('source_row_index')} | "
            f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
            f"`{dict(layers.get('raw_model') or {}).get('final_label')}` | "
            f"`{dict(layers.get('format_only') or {}).get('final_label')}` | "
            f"`{dict(layers.get('final') or {}).get('final_label')}` | "
            f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
            f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


class EventReasonerSignature(dspy.Signature):
    """Reason over saved structured events and emit one JSON decision."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with one sanitized structured-event record and evidence contexts."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching ReasonedFrequencyDecision."
    )


class DspyEventReasonerCaller(dspy.Module):
    """DSPy caller for V1 event reasoning."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(EventReasonerSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def _build_row(
    record: GanFrequencyRecord,
    *,
    structured_event_row: Mapping[str, Any] | None,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
) -> dict[str, Any]:
    prompt_input_json = build_prompt_input(record, structured_event_row)
    raw_output = ""
    call_error: str | None = None
    model_call_attempted = False
    if mode == "live":
        model_call_attempted = True
        try:
            raw_output = _run_model_call(
                prompt_input_json,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - live transport only.
            call_error = f"{type(exc).__name__}: {exc}"
    parsed = (
        parse_reasoned_decision_json(raw_output)
        if raw_output
        else ParsedReasonedDecision(
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=["not_run"],
        )
    )
    final_decision = parsed.final_decision
    v0_reference = _v0_reference(structured_event_row)
    score_layers = {
        "raw_model": _score_layer(record, parsed.raw_decision),
        "format_only": _score_layer(record, parsed.format_only_decision),
        "final": _score_layer(record, final_decision),
    }
    evidence_valid = _decision_evidence_valid(record.note_text, final_decision)
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": mode,
        "pipeline_family": PIPELINE_FAMILY,
        "prompt_version": PROMPT_VERSION,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "structured_event_input_available": structured_event_row is not None,
        "v0_reference": v0_reference,
        "model_call_attempted": model_call_attempted,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "call_error": call_error,
        "parse_errors": parsed.parse_errors,
        "format_repair_events": parsed.format_repair_events,
        "raw_decision_record": (
            parsed.raw_decision.model_dump(mode="json") if parsed.raw_decision else None
        ),
        "format_only_decision_record": (
            parsed.format_only_decision.model_dump(mode="json")
            if parsed.format_only_decision
            else None
        ),
        "decision_record": final_decision.model_dump(mode="json") if final_decision else None,
        "evidence_valid": evidence_valid,
        "score_layers": score_layers,
        "transition_vs_v0": _transition_vs_v0(
            v0_reference=v0_reference,
            final_layer=score_layers["final"],
        ),
        "reference": {
            "gold_label": record.gold_label,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "row_ok": record.row_ok,
        },
        "trace_warnings": (["prompt_only_no_prediction"] if mode == "prompt-only" else [])
        + (["missing_structured_event_row"] if structured_event_row is None else []),
    }


def _run_model_call(
    prompt_input_json: str,
    *,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    del model, temperature, max_tokens
    prediction = DspyEventReasonerCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


def _event_table_row(
    event: Mapping[str, Any],
    structured_event_row: Mapping[str, Any],
) -> dict[str, Any]:
    event_id = str(event.get("event_id") or "")
    normalized = _normalized_event_by_id(structured_event_row).get(event_id)
    return {
        "event_id": event_id,
        "kind": event.get("kind"),
        "temporality": event.get("temporality"),
        "assertion_status": event.get("assertion_status"),
        "certainty": event.get("certainty"),
        "applies_to": event.get("applies_to"),
        "raw_value": event.get("raw_value"),
        "time_window": event.get("time_window"),
        "evidence": event.get("evidence"),
        "normalized_candidate": _normalized_candidate_summary(normalized),
    }


def _normalized_candidate_summary(
    normalized: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if normalized is None:
        return None
    return {
        "normalized_label": normalized.get("normalized_label"),
        "semantic_kind": normalized.get("semantic_kind"),
        "monthly_frequency": normalized.get("monthly_frequency"),
        "validation_errors": list(normalized.get("validation_errors") or []),
    }


def _normalized_event_by_id(row: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(event.get("event_id")): event
        for event in row.get("normalized_events") or []
        if isinstance(event, Mapping) and event.get("event_id") is not None
    }


def _evidence_contexts(
    note_text: str,
    structured_event_row: Mapping[str, Any] | None,
    *,
    window: int = 180,
) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    if structured_event_row is None:
        return contexts
    structured_record = dict(structured_event_row.get("structured_record") or {})
    for event in structured_record.get("events") or []:
        if not isinstance(event, Mapping):
            continue
        event_id = event.get("event_id")
        evidence = event.get("evidence")
        if not isinstance(evidence, str) or not evidence:
            continue
        span = locate_evidence(note_text, evidence)
        if span is None:
            context = evidence
            start_char = None
            end_char = None
        else:
            start_char, end_char = span
            start = max(0, start_char - window)
            end = min(len(note_text), end_char + window)
            context = note_text[start:end]
        contexts.append(
            {
                "event_id": event_id,
                "evidence": evidence,
                "context": context,
                "start_char": start_char,
                "end_char": end_char,
            }
        )
    return contexts


def _filter_decision_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    allowed = set(ReasonedFrequencyDecision.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def _repair_decision_shape(payload: Any) -> tuple[Any, list[str]]:
    if not isinstance(payload, dict):
        return payload, []
    repaired = dict(payload)
    notes: list[str] = []
    for field_name in (
        "selected_event_ids",
        "rejected_event_ids",
        "evidence",
        "boundary_profile",
    ):
        value = repaired.get(field_name)
        normalized = _string_tuple(value)
        if normalized != value:
            repaired[field_name] = normalized
            notes.append(f"decision_field_shape_repaired:{field_name}")
    tool_calls = repaired.get("tool_calls")
    if tool_calls is None:
        repaired["tool_calls"] = []
    elif isinstance(tool_calls, dict):
        repaired["tool_calls"] = [tool_calls]
        notes.append("decision_field_shape_repaired:tool_calls")
    for field_name, allowed_values in (
        ("uncertainty", UNCERTAINTY_VALUES),
        ("attribution", DECISION_ATTRIBUTION_VALUES),
    ):
        value = repaired.get(field_name)
        if isinstance(value, (list, tuple)):
            selected_value = next(
                (str(item) for item in value if str(item) in allowed_values),
                None,
            )
            if selected_value is not None:
                repaired[field_name] = selected_value
                notes.append(f"decision_enum_shape_repaired:{field_name}")
    calculation_trace = repaired.get("calculation_trace")
    if calculation_trace is not None and not isinstance(calculation_trace, str):
        repaired["calculation_trace"] = json.dumps(
            calculation_trace,
            ensure_ascii=False,
            sort_keys=True,
        )
        notes.append("decision_field_shape_repaired:calculation_trace")
    return repaired, notes


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(str(item) for item in value)
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),)


def _repair_event_to_dict(event: Any) -> dict[str, Any]:
    return {
        "rule_id": event.rule_id,
        "group": str(event.group),
        "portability": str(event.portability),
        "before": event.before,
        "after": event.after,
    }


def _score_layer(
    record: GanFrequencyRecord,
    decision: ReasonedFrequencyDecision | None,
) -> dict[str, Any]:
    label = decision.final_label if decision else None
    return {
        "final_label": label,
        "final_kind": decision.final_kind if decision else None,
        "attribution": decision.attribution if decision else "no_prediction",
        "comparison": _compare_label_to_gold(record, label),
    }


def _compare_label_to_gold(record: GanFrequencyRecord, label: str | None) -> dict[str, Any]:
    gold_monthly = record.gold_monthly_frequency
    if label is None:
        return _empty_comparison(gold_monthly, error="missing_label")
    try:
        predicted_record = label_to_frequency_record(str(label))
    except ValueError as exc:
        comparison = _empty_comparison(gold_monthly, error=str(exc))
        comparison["final_label"] = label
        return comparison
    predicted_monthly = predicted_record.monthly_frequency
    predicted_purist = map_purist(predicted_monthly)
    gold_purist = map_purist(gold_monthly)
    predicted_pragmatic = map_pragmatic(predicted_monthly)
    gold_pragmatic = map_pragmatic(gold_monthly)
    return {
        "final_label": predicted_record.normalized_label,
        "predicted_monthly_frequency": predicted_monthly,
        "gold_monthly_frequency": gold_monthly,
        "predicted_purist_category": str(predicted_purist),
        "gold_purist_category": str(gold_purist),
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": str(predicted_pragmatic),
        "gold_pragmatic_category": str(gold_pragmatic),
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


def _empty_comparison(gold_monthly: float, *, error: str) -> dict[str, Any]:
    return {
        "predicted_monthly_frequency": None,
        "gold_monthly_frequency": gold_monthly,
        "predicted_purist_category": None,
        "gold_purist_category": str(map_purist(gold_monthly)),
        "purist_correct": False,
        "predicted_pragmatic_category": None,
        "gold_pragmatic_category": str(map_pragmatic(gold_monthly)),
        "pragmatic_correct": False,
        "error": error,
    }


def _decision_evidence_valid(
    note_text: str,
    decision: ReasonedFrequencyDecision | None,
) -> bool:
    if decision is None or not decision.evidence:
        return False
    scored = score_evidence_set(note_text, decision.evidence)
    return scored.total > 0 and scored.grounded == scored.total


def _v0_reference(structured_event_row: Mapping[str, Any] | None) -> dict[str, Any]:
    if structured_event_row is None:
        return {
            "final_label": None,
            "final_kind": None,
            "selected_event_ids": [],
            "comparison": {},
        }
    selection = dict(
        dict(structured_event_row.get("structured_record") or {}).get("selection") or {}
    )
    return {
        "final_label": selection.get("final_label"),
        "final_kind": selection.get("final_kind"),
        "selected_event_ids": list(selection.get("selected_event_ids") or []),
        "comparison": dict(structured_event_row.get("comparison") or {}),
        "evidence_valid": structured_event_row.get("evidence_valid"),
    }


def _transition_vs_v0(
    *,
    v0_reference: Mapping[str, Any],
    final_layer: Mapping[str, Any],
) -> dict[str, Any]:
    if final_layer.get("final_label") is None:
        return {
            "purist_transition": "unscored",
            "label_changed": False,
        }
    v0_comparison = dict(v0_reference.get("comparison") or {})
    final_comparison = dict(final_layer.get("comparison") or {})
    v0_correct = v0_comparison.get("purist_correct")
    final_correct = final_comparison.get("purist_correct")
    if v0_correct is True and final_correct is True:
        transition = "correct_to_correct"
    elif v0_correct is True and final_correct is False:
        transition = "correct_to_wrong"
    elif v0_correct is False and final_correct is True:
        transition = "wrong_to_correct"
    elif v0_correct is False and final_correct is False:
        transition = "wrong_to_wrong"
    else:
        transition = "unscored"
    return {
        "purist_transition": transition,
        "label_changed": v0_reference.get("final_label") != final_layer.get("final_label"),
    }


def _rows_by_source_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    return {
        int(row["source_row_index"]): row for row in rows if row.get("source_row_index") is not None
    }


def _extract_json_object(raw_output: str) -> str:
    text = raw_output.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end >= start:
        return text[start : end + 1]
    return text


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            (
                "invalid_json:",
                "schema_validation_error:",
                "unscorable_final_label:",
            )
        )
        for error in (errors or [])
    )
