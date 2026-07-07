"""Event-completion reasoner over saved Gan 2026 structured events.

This is a V7-style candidate from the test-0.85 plan. The model may keep the
original structured-event final or create one completed event from exact raw-note
evidence when the saved event table omitted the clinically decisive fact.
Deterministic code validates schema, performs format-only label repair, checks
evidence substrings, and scores after the model-owned decision.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    llm_event_reasoner,
    structured_event_verifier,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.run_driver import (
    AgenticSplitHooks,
    RegisteredAgenticStage,
    SplitRunParams,
    StructuredEventSplitContext,
    dispatch_registered_split,
    register_agentic_stage,
)
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
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_event_completion_reasoner_v0_3"
PIPELINE_FAMILY = "event_completion_reasoner"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = structured_event_verifier.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
DEFAULT_JSONL_PATH = Path("experiments/gan2026_event_completion_reasoner_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_event_completion_reasoner_validation.md")
STAGE_ID = "event_completion_reasoner"

register_agentic_stage(
    RegisteredAgenticStage(
        stage_id=STAGE_ID,
        dispatch_kind="structured_event",
        module=__name__,
        description="V7 event-completion reasoner over saved structured events",
    )
)

CompletionAction = Literal[
    "keep_original_structured_event_final",
    "create_completed_event_final",
]
COMPLETION_ACTION_VALUES = (
    "keep_original_structured_event_final",
    "create_completed_event_final",
)


class CompletedEvent(BaseModel):
    """Model-owned completed event when saved structured events omitted a fact."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    kind: str
    raw_value: str
    evidence: str
    rationale: str


class EventCompletionDecision(BaseModel):
    """Prediction schema for V7 event completion."""

    model_config = ConfigDict(extra="forbid")

    action: CompletionAction
    final_label: str
    final_kind: llm_event_reasoner.DecisionKind
    selected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    rejected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    boundary_profile: tuple[str, ...] = Field(default_factory=tuple)
    calculation_trace: str | None = None
    clinical_rationale: str
    uncertainty: llm_event_reasoner.Uncertainty
    tool_calls: tuple[llm_event_reasoner.ToolTrace, ...] = Field(default_factory=tuple)
    attribution: llm_event_reasoner.DecisionAttribution
    completed_event: CompletedEvent | None = None


class ParsedCompletionDecision(BaseModel):
    """Raw, format-only, and action-rendered views of one completion output."""

    model_config = ConfigDict(extra="forbid")

    raw_completion_decision: EventCompletionDecision | None
    raw_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    format_only_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    final_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    completed_event: CompletedEvent | None = None
    parse_errors: list[str] = Field(default_factory=list)
    format_repair_events: list[dict[str, Any]] = Field(default_factory=list)
    action_render_events: list[str] = Field(default_factory=list)


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
    """Run or prompt-smoke event completion over saved SE rows."""

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
            "artifact_kind": "gan2026_event_completion_reasoner_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": PROMPT_VERSION,
            "structured_event_source_role": (
                "pure structured-event V0 comparator and completion substrate; "
                "the model owns any created completed event"
            ),
            "claim_boundary": (
                "validation-development V7 event-completion scaffold; no holdout "
                "use, no row-level test inspection, and no benchmark claim"
            ),
        },
        build_row=_build_row,
        summarize_rows=summarize_rows,
        gate_interpretation=structured_event_verifier.gate_interpretation,
        write_report=write_report,
        progress_fields=("final_purist_correct", "net_purist_gain_vs_v0"),
    )
    structured_event_context = StructuredEventSplitContext(
        default_structured_event_jsonl_path=DEFAULT_STRUCTURED_EVENT_JSONL_PATH,
        structured_event_jsonl_path=structured_event_jsonl_path,
        structured_event_rows=structured_event_rows,
        structured_event_source_path=source_path,
        rows_by_source_index=llm_event_reasoner._rows_by_source_index,
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
    *,
    note_excerpt_chars: int = 6000,
) -> str:
    """Build a model-facing completion payload without IDs, gold, split, or rules top."""

    structured_input = llm_event_reasoner.inspect_structured_events(structured_event_row)
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 structured-event completion reasoning",
        "variant": "V7_event_completion_reasoner",
        "instructions": [
            (
                "Decide whether the saved structured-event table omitted one "
                "clinically decisive seizure-frequency event from the raw note."
            ),
            (
                "Use keep_original_structured_event_final when the issue is only "
                "selecting among existing normalized events, or when the raw note "
                "does not clearly contain an omitted final-answer fact."
            ),
            (
                "Only create a completed event when exact raw-note evidence contains "
                "a missing current/recent frequency, cluster burden, seizure-free "
                "duration, or multi-semiology burden that is not represented in the "
                "event table."
            ),
            (
                "Do not use outside final-answer sources, row IDs, split membership, "
                "scoring metadata, deterministic rules, or deterministic top labels."
            ),
            (
                "Do not recompute a better answer from already extracted events; "
                "that was the verifier/router task. This task is for event omissions."
            ),
            (
                "For anchored one-off counts, last-event-only dates, uncertain spells, "
                "or vague review windows, keep original unless the raw text itself "
                "also states a recurring cadence or unambiguous boundary state."
            ),
            (
                "For seizure-free completion, require exact absence-since or no-events "
                "duration evidence and no conflicting current/recent frequency in the excerpt."
            ),
            (
                "For cluster completion, preserve the cluster axis. If events per "
                "cluster is vague, use an unresolved-multiple cluster-compatible label "
                "rather than pretending a simple cadence is the full burden."
            ),
            (
                "completed_event.event_id must be completed_event_1 when action is "
                "create_completed_event_final; selected_event_ids must include it."
            ),
            "Evidence entries should be exact substrings from the note.",
            (
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(COMPLETION_ACTION_VALUES),
            "final_label": "Gan-style label string",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": "original event IDs for keep; completed_event_1 for create",
            "rejected_event_ids": "list of saved event IDs rejected",
            "evidence": "list of exact evidence substrings supporting the final choice",
            "boundary_profile": "list such as event_completion:cluster_axis",
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief clinical rationale",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for this v0.1 completion reasoner",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
            "completed_event": (
                "null for keep_original_structured_event_final; for "
                "create_completed_event_final only, an object with keys "
                "event_id, kind, raw_value, evidence, rationale"
            ),
        },
        "structured_event_input": structured_input,
        "raw_evidence_contexts": llm_event_reasoner._evidence_contexts(
            record.note_text,
            structured_event_row,
        ),
        "raw_note_excerpt": record.note_text[:note_excerpt_chars],
        "excerpt_truncated": len(record.note_text) > note_excerpt_chars,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_completion_decision_json(
    raw_output: str,
    structured_event_row: Mapping[str, Any] | None,
) -> ParsedCompletionDecision:
    """Parse a completion decision and render keep/create actions."""

    parse_errors: list[str] = []
    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
            llm_event_reasoner._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return ParsedCompletionDecision(
            raw_completion_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=[f"invalid_json: {exc.msg}"],
        )
    parse_errors.extend(dialect_notes)
    payload, shape_notes = _repair_completion_shape(repair_decision_payload(raw_payload))
    payload = _filter_completion_payload(payload)
    parse_errors.extend(shape_notes)
    try:
        raw_completion = EventCompletionDecision.model_validate(payload)
    except ValidationError as exc:
        return ParsedCompletionDecision(
            raw_completion_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=[*parse_errors, f"schema_validation_error: {exc.errors()[0]['msg']}"],
        )

    raw_common = _common_decision_from_completion(raw_completion)
    format_decision, repair_events, format_notes = _format_only_decision(raw_common)
    parse_errors.extend(format_notes)
    final_decision, action_events, action_errors = _render_completion_action(
        raw_completion,
        format_decision,
        structured_event_row,
    )
    parse_errors.extend(action_errors)
    return ParsedCompletionDecision(
        raw_completion_decision=raw_completion,
        raw_decision=raw_common,
        format_only_decision=format_decision,
        final_decision=final_decision,
        completed_event=raw_completion.completed_event,
        parse_errors=parse_errors,
        format_repair_events=repair_events,
        action_render_events=action_events,
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize completion rows across raw, format-only, final, and V0 layers."""

    summary = structured_event_verifier.summarize_rows(rows)
    summary["completed_event_actions"] = 0
    profiles: Counter[str] = Counter()
    for row in rows:
        decision = dict(row.get("completion_decision_record") or {})
        if decision.get("action") == "create_completed_event_final":
            summary["completed_event_actions"] += 1
        for profile in decision.get("boundary_profile") or []:
            profiles[str(profile)] += 1
    summary["completion_profiles"] = dict(sorted(profiles.items()))
    return summary


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
        "# Gan 2026 Event-Completion Reasoner",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation-development V7 event-completion artifact.",
        "The model may create one completed event from exact raw-note evidence.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: V7 event-completion reasoner over saved structured events.",
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
        f"- Completed-event actions: {summary.get('completed_event_actions', 0)}",
        f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
        (f"- V0 Purist: {summary.get('v0_purist_correct', 0)}/{summary.get('rows', 0)}"),
        (f"- Final Purist: {summary.get('final_purist_correct', 0)}/{summary.get('rows', 0)}"),
        f"- Net Purist gain vs V0: {summary.get('net_purist_gain_vs_v0', 0)}",
        (f"- Changed-label precision vs V0: {summary.get('changed_label_precision_vs_v0')}"),
        f"- Completion profiles: `{summary.get('completion_profiles', {})}`",
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
        "| Row | Action | Profiles | V0 | Final | Transition | Evidence exact | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        layers = dict(row.get("score_layers") or {})
        completion_record = dict(row.get("completion_decision_record") or {})
        notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        lines.append(
            f"| {row.get('source_row_index')} | "
            f"`{completion_record.get('action')}` | "
            f"`{completion_record.get('boundary_profile')}` | "
            f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
            f"`{dict(layers.get('final') or {}).get('final_label')}` | "
            f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
            f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


class EventCompletionSignature(dspy.Signature):
    """Complete one missing event if exact raw-note evidence supports it."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with sanitized structured events and bounded raw-note excerpt."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching EventCompletionDecision."
    )


class DspyEventCompletionCaller(dspy.Module):
    """DSPy caller for the V7 event-completion reasoner."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(EventCompletionSignature)

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
        parse_completion_decision_json(raw_output, structured_event_row)
        if raw_output
        else ParsedCompletionDecision(
            raw_completion_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=["not_run"],
        )
    )
    final_decision = parsed.final_decision
    v0_reference = llm_event_reasoner._v0_reference(structured_event_row)
    score_layers = {
        "raw_model": llm_event_reasoner._score_layer(record, parsed.raw_decision),
        "format_only": llm_event_reasoner._score_layer(
            record,
            parsed.format_only_decision,
        ),
        "final": llm_event_reasoner._score_layer(record, final_decision),
    }
    evidence_valid = llm_event_reasoner._decision_evidence_valid(
        record.note_text,
        final_decision,
    )
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
        "action_render_events": parsed.action_render_events,
        "completion_decision_record": (
            parsed.raw_completion_decision.model_dump(mode="json")
            if parsed.raw_completion_decision
            else None
        ),
        "completed_event_record": (
            parsed.completed_event.model_dump(mode="json") if parsed.completed_event else None
        ),
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
        "transition_vs_v0": llm_event_reasoner._transition_vs_v0(
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
    prediction = DspyEventCompletionCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


def _filter_completion_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    allowed = set(EventCompletionDecision.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def _repair_completion_shape(payload: Any) -> tuple[Any, list[str]]:
    if not isinstance(payload, dict):
        return payload, []
    repaired = dict(payload)
    notes: list[str] = []
    if "clinical_rationale" not in repaired and "rationale" in repaired:
        repaired["clinical_rationale"] = str(repaired["rationale"])
        notes.append("decision_field_shape_repaired:clinical_rationale_alias")
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
        ("action", COMPLETION_ACTION_VALUES),
        ("uncertainty", llm_event_reasoner.UNCERTAINTY_VALUES),
        ("attribution", llm_event_reasoner.DECISION_ATTRIBUTION_VALUES),
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
    if (
        repaired.get("action") == "keep_original_structured_event_final"
        and repaired.get("completed_event") is not None
    ):
        repaired["completed_event"] = None
        notes.append("decision_field_shape_repaired:completed_event_ignored_for_keep")
    return repaired, notes


def _common_decision_from_completion(
    decision: EventCompletionDecision,
) -> llm_event_reasoner.ReasonedFrequencyDecision:
    return llm_event_reasoner.ReasonedFrequencyDecision(
        final_label=decision.final_label,
        final_kind=decision.final_kind,
        selected_event_ids=decision.selected_event_ids,
        rejected_event_ids=decision.rejected_event_ids,
        evidence=decision.evidence,
        boundary_profile=decision.boundary_profile,
        calculation_trace=decision.calculation_trace,
        clinical_rationale=decision.clinical_rationale,
        uncertainty=decision.uncertainty,
        tool_calls=decision.tool_calls,
        attribution=decision.attribution,
    )


def _format_only_decision(
    raw_decision: llm_event_reasoner.ReasonedFrequencyDecision,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision, list[dict[str, Any]], list[str]]:
    parse_notes: list[str] = []
    repair_trace = repair_prediction_label_format_preserving_with_trace(raw_decision.final_label)
    repair_events = [
        llm_event_reasoner._repair_event_to_dict(event) for event in repair_trace.events
    ]
    format_decision = raw_decision
    if repair_trace.final_label != raw_decision.final_label:
        parse_notes.append(
            "final_label_format_repaired: "
            f"{raw_decision.final_label!r} -> {repair_trace.final_label!r}"
        )
        format_decision = raw_decision.model_copy(
            update={
                "final_label": repair_trace.final_label,
                "attribution": "llm_selected_format_repaired",
            }
        )
    return format_decision, repair_events, parse_notes


def _render_completion_action(
    raw_completion: EventCompletionDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, list[str], list[str]]:
    if raw_completion.action == "keep_original_structured_event_final":
        decision, error = _render_keep_original_action(format_decision, structured_event_row)
        if error:
            return None, [], [error]
        return (
            decision,
            ["completion_action_rendered:keep_original_structured_event_final"],
            [],
        )
    errors: list[str] = []
    if raw_completion.completed_event is None:
        errors.append("action_render_error: missing_completed_event")
    elif raw_completion.completed_event.event_id != "completed_event_1":
        errors.append("action_render_error: completed_event_id_must_be_completed_event_1")
    if "completed_event_1" not in format_decision.selected_event_ids:
        errors.append("action_render_error: selected_event_ids_missing_completed_event_1")
    try:
        label_to_frequency_record(format_decision.final_label)
    except ValueError as exc:
        errors.append(f"action_render_error: completed_label_unscorable: {exc}")
    if errors:
        return None, [], errors
    return (
        format_decision.model_copy(update={"attribution": format_decision.attribution}),
        ["completion_action_rendered:create_completed_event_final"],
        [],
    )


def _render_keep_original_action(
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, str | None]:
    selection = _structured_selection(structured_event_row)
    label = _as_optional_str(selection.get("final_label"))
    if label is None:
        return None, "action_render_error: missing_original_final_label"
    try:
        label_record = label_to_frequency_record(label)
    except ValueError as exc:
        return None, f"action_render_error: original_final_label_unscorable: {exc}"
    selected_ids = _string_tuple(selection.get("selected_event_ids"))
    evidence = _evidence_tuple(selection.get("evidence")) or format_decision.evidence
    return (
        format_decision.model_copy(
            update={
                "final_label": label_record.normalized_label,
                "final_kind": str(label_record.kind),
                "selected_event_ids": selected_ids,
                "evidence": evidence,
                "attribution": "llm_original_structured_event_kept",
            }
        ),
        None,
    )


def _structured_selection(structured_event_row: Mapping[str, Any] | None) -> dict[str, Any]:
    if structured_event_row is None:
        return {}
    return dict(dict(structured_event_row.get("structured_record") or {}).get("selection") or {})


def _evidence_tuple(value: Any) -> tuple[str, ...]:
    return tuple(item for item in _string_tuple(value) if item)


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(str(item) for item in value)
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    return (str(value),)


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
