"""Temporal/sentinel specialist over saved Gan 2026 structured events.

This V9 candidate targets the failure family where the original structured
event final over-renders anchored, last-event-only, duration, treatment-anchor,
or misleading absence-since evidence. The model owns a keep-or-replace action.
Deterministic code only validates schema/action constraints, renders a selected
existing normalized event, performs format-only repair, and scores after the
model-owned action.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

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
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_temporal_sentinel_specialist_v0_1"
SAFETY_GATE_VERSION = "gan2026_temporal_sentinel_safety_gate_v0_2"
PIPELINE_FAMILY = "temporal_sentinel_specialist"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = (
    structured_event_verifier.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_temporal_sentinel_specialist_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_temporal_sentinel_specialist_validation.md")
STAGE_ID = "temporal_sentinel_specialist"

register_agentic_stage(
    RegisteredAgenticStage(
        stage_id=STAGE_ID,
        dispatch_kind="structured_event",
        module=__name__,
        description="V9 temporal/sentinel specialist over saved structured events",
    )
)

ACTION_VALUES = (
    "keep_original_structured_event_final",
    "replace_with_existing_event",
)
DISABLED_ACTIONS = (
    "replace_with_recomputed_fact_from_selected_evidence",
    "abstain_unrenderable",
)

BOUNDARY_KINDS = {"unknown", "no_reference", "unresolved_multiple"}


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
    """Run or prompt-smoke the temporal/sentinel specialist over saved SE rows."""

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
            "artifact_kind": "gan2026_temporal_sentinel_specialist_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": f"{PROMPT_VERSION}+{SAFETY_GATE_VERSION}",
            "safety_gate_version": SAFETY_GATE_VERSION,
            "structured_event_source_role": (
                "pure structured-event V0 comparator and temporal/sentinel "
                "specialist substrate; the specialist action owns any selected "
                "replacement event"
            ),
            "claim_boundary": (
                "validation-development V9 temporal/sentinel specialist; no "
                "holdout use, no row-level test inspection, and no benchmark claim"
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
) -> str:
    """Build a model-facing specialist payload without IDs, gold, or split."""

    structured_input = llm_event_reasoner.inspect_structured_events(
        structured_event_row
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 temporal and sentinel boundary adjudication",
        "variant": "V9_temporal_sentinel_specialist",
        "instructions": [
            (
                "Choose exactly one action: keep the original structured-event "
                "final, or select one existing event whose normalized_candidate "
                "should replace the original final."
            ),
            (
                "Use only the event table, specialist hints, raw evidence "
                "contexts, and note excerpt below. Do not use outside final-answer "
                "sources, row IDs, split membership, scoring metadata, "
                "deterministic rules, or deterministic top labels."
            ),
            (
                "specialist_hints are split-neutral review aids over the event "
                "table. They do not choose the answer. Verify the clinical "
                "evidence before acting."
            ),
            (
                "If you act, selected_event_ids must contain exactly one existing "
                "event ID. The final label will be rendered from that event's "
                "normalized_candidate.normalized_label; do not invent or recompute "
                "a label."
            ),
            (
                "High-priority sentinel action: replace an original numeric "
                "frequency when its selected event is really last-event-only, an "
                "isolated dated event, a treatment-anchor count, duration text, "
                "or vague/uncertain frequency, and an existing selected or "
                "alternative event already has normalized_candidate unknown, "
                "no_reference, or unresolved_multiple."
            ),
            (
                "High-priority duration action: if original_final.final_kind is "
                "unknown or boundary-like but original_final.final_label is a "
                "numeric per-year/month label derived from minutes, duration, or "
                "episode length evidence, select the existing unknown/no_reference "
                "candidate from that same event."
            ),
            (
                "High-priority cadence action: when the original selected a broad "
                "elapsed-window total such as 'so far this year' but another "
                "current event for the same target gives a typical recurring "
                "cadence such as monthly, weekly, daily, or every N weeks, select "
                "the recurring-cadence event."
            ),
            (
                "Seizure-free boundary action: replace original seizure_free only "
                "when the supposed absence-since evidence is merely last-event-only, "
                "non-target negation, resolved/historical provoked events, or the "
                "selected event's own normalized_candidate is unknown/no_reference. "
                "Do not replace well-supported current target seizure freedom."
            ),
            (
                "Keep original when it is supported by an explicit recurring "
                "cadence, an explicit count over a defined recent assessment "
                "window, a total across active semiologies, or a valid cluster "
                "label. Do not churn from unknown to no_reference or no_reference "
                "to unknown."
            ),
            (
                "Keep original for bounded recent counts such as 'three in "
                "September and two in early October' when that count is the "
                "structured selection and there is no clearer current cadence."
            ),
            (
                "Do not replace a numeric/range frequency with seizure_free in "
                "this specialist. A seizure-free normalized_candidate may be "
                "selected only when original_final is already seizure_free."
            ),
            (
                "Preserve cluster labels. If original_final.final_label contains "
                "cluster, do not replace it with a non-cluster candidate."
            ),
            (
                "Put the active specialist profile in contradiction_profile as "
                "one string prefixed with temporal_sentinel:, for example "
                "temporal_sentinel:last_event_only_boundary."
            ),
            "Evidence entries should be exact substrings from the note when possible.",
            (
                "final_label must be a valid Gan label only. For "
                "replace_with_existing_event, it should match the selected event "
                "normalized_candidate.normalized_label."
            ),
            (
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "specialist_profiles": {
            "last_event_only_boundary": (
                "Original numeric frequency comes from a single dated/last event "
                "or isolated event description rather than a recurring cadence."
            ),
            "duration_or_episode_length_boundary": (
                "A duration such as minutes or episode length was rendered as a "
                "frequency label."
            ),
            "treatment_anchor_boundary": (
                "A count since starting/changing treatment is not enough to define "
                "a standing seizure frequency when the event table already marks "
                "the same evidence unknown/no_reference."
            ),
            "recurring_cadence_preferred": (
                "A typical recurring cadence is clinically preferable to a broad "
                "elapsed-window total for the same current target."
            ),
            "seizure_free_sentinel_boundary": (
                "Original seizure_free is actually last-event-only, non-target "
                "negation, or historical/resolved context."
            ),
        },
        "specialist_hints": _specialist_hints(structured_event_row),
        "required_output_schema": {
            "action": list(ACTION_VALUES),
            "final_label": (
                "Gan-style label string; for replace_with_existing_event it should "
                "match the selected event normalized_candidate.normalized_label"
            ),
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": "empty for keep; exactly one event ID for replace",
            "rejected_event_ids": "list of event IDs explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the action",
            "contradiction_profile": (
                "list containing temporal_sentinel:<profile> when acting"
            ),
            "calculation_trace": "short boundary/cadence trace, or null",
            "clinical_rationale": "brief specialist rationale for the action",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for this specialist",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "disabled_actions_for_this_run": list(DISABLED_ACTIONS),
        "structured_event_input": structured_input,
        "raw_evidence_contexts": llm_event_reasoner._evidence_contexts(
            record.note_text,
            structured_event_row,
        ),
        "raw_note_excerpt": record.note_text[:6000],
        "excerpt_truncated": len(record.note_text) > 6000,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_specialist_decision_json(
    raw_output: str,
    structured_event_row: Mapping[str, Any] | None,
) -> structured_event_verifier.ParsedVerifierDecision:
    """Parse, render, and guard one temporal/sentinel specialist decision."""

    parsed = structured_event_verifier.parse_verifier_decision_json(
        raw_output,
        structured_event_row,
    )
    decision = parsed.raw_verifier_decision
    if decision is None:
        return parsed

    fatal_errors = _fatal_action_errors(decision, structured_event_row)
    if fatal_errors:
        return parsed.model_copy(
            update={
                "final_decision": None,
                "parse_errors": [*parsed.parse_errors, *fatal_errors],
                "action_render_events": [
                    event
                    for event in parsed.action_render_events
                    if "replace_with_existing_event" not in event
                    and "replace_with_recomputed_fact_from_selected_evidence" not in event
                    and "abstain_unrenderable" not in event
                ],
            }
        )

    safety_keep_reason = _safety_keep_reason(decision, structured_event_row)
    if safety_keep_reason is None:
        return parsed

    keep_decision, keep_error = _guarded_keep_original_decision(
        decision,
        parsed.format_only_decision,
        structured_event_row,
    )
    if keep_error:
        return parsed.model_copy(
            update={
                "final_decision": None,
                "parse_errors": [*parsed.parse_errors, keep_error],
                "action_render_events": [
                    event
                    for event in parsed.action_render_events
                    if "replace_with_existing_event" not in event
                ],
            }
        )
    return parsed.model_copy(
        update={
            "final_decision": keep_decision,
            "action_render_events": [
                event
                for event in parsed.action_render_events
                if "replace_with_existing_event" not in event
            ]
            + [f"specialist_safety_gate_kept_original:{safety_keep_reason}"],
        }
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize specialist rows and profile usage."""

    summary = structured_event_verifier.summarize_rows(rows)
    profiles: Counter[str] = Counter()
    for row in rows:
        decision = dict(row.get("verifier_decision_record") or {})
        for profile in decision.get("contradiction_profile") or []:
            text = str(profile)
            if text.startswith("temporal_sentinel:"):
                profiles[text] += 1
    summary["temporal_sentinel_profiles"] = dict(sorted(profiles.items()))
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
        "# Gan 2026 Temporal/Sentinel Specialist",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation-development V9 temporal/sentinel specialist artifact.",
        "The model may keep V0 or select one existing normalized structured event.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: V9 temporal/sentinel specialist over saved structured events.",
        f"- Rows: {summary.get('rows', 0)}",
        "- Split: `validation`, manifest `gan2026_split_v1`.",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Safety gate version: `{metadata.get('safety_gate_version')}`",
        f"- Structured-event source: `{metadata.get('structured_event_source_path')}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
        f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
        f"- Action-render failures: {summary.get('action_render_failures', 0)}",
        f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
        (
            f"- V0 Purist: {summary.get('v0_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Final Purist: {summary.get('final_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        f"- Net Purist gain vs V0: {summary.get('net_purist_gain_vs_v0', 0)}",
        (
            "- Changed-label precision vs V0: "
            f"{summary.get('changed_label_precision_vs_v0')}"
        ),
        f"- Verifier actions: `{summary.get('verifier_actions', {})}`",
        f"- Specialist profiles: `{summary.get('temporal_sentinel_profiles', {})}`",
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
        verifier_record = dict(row.get("verifier_decision_record") or {})
        notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        lines.append(
            f"| {row.get('source_row_index')} | "
            f"`{verifier_record.get('action')}` | "
            f"`{verifier_record.get('contradiction_profile')}` | "
            f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
            f"`{dict(layers.get('final') or {}).get('final_label')}` | "
            f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
            f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


class TemporalSentinelSpecialistSignature(dspy.Signature):
    """Adjudicate one saved structured-event record and emit one JSON action."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with sanitized structured events and temporal hints."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching StructuredEventVerifierDecision."
    )


class DspyTemporalSentinelSpecialistCaller(dspy.Module):
    """DSPy caller for V9 temporal/sentinel specialist."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(TemporalSentinelSpecialistSignature)

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
        parse_specialist_decision_json(raw_output, structured_event_row)
        if raw_output
        else structured_event_verifier.ParsedVerifierDecision(
            raw_verifier_decision=None,
            raw_common_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=["not_run"],
        )
    )
    final_decision = parsed.final_decision
    v0_reference = llm_event_reasoner._v0_reference(structured_event_row)
    score_layers = {
        "raw_model": llm_event_reasoner._score_layer(
            record,
            parsed.raw_common_decision,
        ),
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
        "safety_gate_version": SAFETY_GATE_VERSION,
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
        "verifier_decision_record": (
            parsed.raw_verifier_decision.model_dump(mode="json")
            if parsed.raw_verifier_decision
            else None
        ),
        "raw_decision_record": (
            parsed.raw_common_decision.model_dump(mode="json")
            if parsed.raw_common_decision
            else None
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
        "trace_warnings": (
            ["prompt_only_no_prediction"] if mode == "prompt-only" else []
        )
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
    prediction = DspyTemporalSentinelSpecialistCaller()(
        prompt_input_json=prompt_input_json
    )
    return str(prediction.decision_json)


def _fatal_action_errors(
    decision: structured_event_verifier.StructuredEventVerifierDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> list[str]:
    errors: list[str] = []
    if decision.action in DISABLED_ACTIONS:
        errors.append(f"action_render_error: disabled_action:{decision.action}")
        return errors
    if decision.action != "replace_with_existing_event":
        return errors
    event_id = decision.selected_event_ids[0] if decision.selected_event_ids else None
    if event_id is None:
        return errors
    selected_label = _normalized_label_for_event(structured_event_row, event_id)
    selection = _structured_selection(structured_event_row)
    original_label = str(selection.get("final_label") or "")
    if "cluster" in original_label.lower() and "cluster" not in selected_label.lower():
        errors.append("action_render_error: cluster_label_replacement_disallowed")
    return errors


def _safety_keep_reason(
    decision: structured_event_verifier.StructuredEventVerifierDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> str | None:
    if decision.action != "replace_with_existing_event":
        return None
    event_id = decision.selected_event_ids[0] if decision.selected_event_ids else None
    if event_id is None:
        return None
    normalized = llm_event_reasoner._normalized_event_by_id(
        structured_event_row or {}
    ).get(event_id)
    selection = _structured_selection(structured_event_row)
    original_kind = str(selection.get("final_kind") or "")
    original_label = str(selection.get("final_label") or "")
    selected_kind = str((normalized or {}).get("semantic_kind") or "")
    selected_label = str((normalized or {}).get("normalized_label") or "")
    if _labels_equivalent(original_label, selected_label):
        return None
    original_is_seizure_free = (
        original_kind == "seizure_free" or "seizure free" in original_label.lower()
    )
    if selected_kind == "seizure_free" and not original_is_seizure_free:
        return "seizure_free_replacement_disallowed"
    if original_is_seizure_free and selected_kind in BOUNDARY_KINDS:
        return "seizure_free_boundary_demoter_not_high_precision"
    if (
        original_kind in {"unknown", "no_reference"}
        and selected_kind in {"unknown", "no_reference"}
        and selected_label != original_label
    ):
        return "boundary_to_boundary_churn_disallowed"

    hints = _specialist_hints(structured_event_row)
    selected_reviews = list(hints.get("selected_event_review") or [])
    candidate_reviews = list(hints.get("candidate_event_reviews") or [])
    chosen_review = next(
        (
            dict(review)
            for review in candidate_reviews
            if str(review.get("event_id") or "") == str(event_id)
        ),
        {},
    )
    if _is_safe_recurring_cadence_replacement(
        decision=decision,
        original_kind=original_kind,
        selected_reviews=selected_reviews,
        chosen_review=chosen_review,
    ):
        return None
    if _is_safe_boundary_replacement(
        decision=decision,
        original_label=original_label,
        original_kind=original_kind,
        selected_kind=selected_kind,
        selected_reviews=selected_reviews,
    ):
        return None
    return "replacement_not_in_high_precision_gate"


def _guarded_keep_original_decision(
    decision: structured_event_verifier.StructuredEventVerifierDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision | None,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, str | None]:
    if format_decision is None:
        return None, "action_render_error: safety_gate_missing_format_decision"
    return structured_event_verifier._render_keep_original_action(
        decision,
        format_decision,
        structured_event_row,
    )


def _is_safe_recurring_cadence_replacement(
    *,
    decision: structured_event_verifier.StructuredEventVerifierDecision,
    original_kind: str,
    selected_reviews: Sequence[Mapping[str, Any]],
    chosen_review: Mapping[str, Any],
) -> bool:
    if "recurring_cadence_preferred" not in _profile_names(decision):
        return False
    if original_kind != "frequency":
        return False
    selected_flags = _review_flags(selected_reviews)
    chosen_flags = set(chosen_review.get("review_flags") or [])
    return (
        "broad_elapsed_window_total" in selected_flags
        and chosen_review.get("semantic_kind") == "frequency"
        and chosen_review.get("event_kind") == "frequency_rate"
        and "explicit_recurring_cadence" in chosen_flags
    )


def _is_safe_boundary_replacement(
    *,
    decision: structured_event_verifier.StructuredEventVerifierDecision,
    original_label: str,
    original_kind: str,
    selected_kind: str,
    selected_reviews: Sequence[Mapping[str, Any]],
) -> bool:
    profiles = _profile_names(decision)
    if not profiles & {"last_event_only_boundary", "treatment_anchor_boundary"}:
        return False
    if original_kind != "frequency" or not _looks_numeric_frequency_label(original_label):
        return False
    if selected_kind not in BOUNDARY_KINDS:
        return False
    if not any(
        str(review.get("semantic_kind") or "") in BOUNDARY_KINDS
        for review in selected_reviews
    ):
        return False
    selected_flags = _review_flags(selected_reviews)
    return bool(
        selected_flags
        & {
            "last_event_only_or_latest_event",
            "anchored_or_isolated_event",
            "treatment_anchor",
            "vague_or_uncertain_frequency",
        }
    )


def _profile_names(
    decision: structured_event_verifier.StructuredEventVerifierDecision,
) -> set[str]:
    names = set()
    for profile in decision.contradiction_profile:
        text = str(profile)
        names.add(text.split(":", 1)[-1])
    return names


def _review_flags(reviews: Sequence[Mapping[str, Any]]) -> set[str]:
    flags: set[str] = set()
    for review in reviews:
        flags.update(str(flag) for flag in review.get("review_flags") or [])
    return flags


def _normalized_label_for_event(
    structured_event_row: Mapping[str, Any] | None,
    event_id: str,
) -> str:
    normalized = llm_event_reasoner._normalized_event_by_id(
        structured_event_row or {}
    ).get(event_id)
    return str((normalized or {}).get("normalized_label") or "")


def _labels_equivalent(left: str, right: str) -> bool:
    if left == right:
        return True
    try:
        return (
            label_to_frequency_record(left).normalized_label
            == label_to_frequency_record(right).normalized_label
        )
    except ValueError:
        return False


def _specialist_hints(
    structured_event_row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if structured_event_row is None:
        return {
            "possible_profiles": [],
            "selected_event_review": [],
            "candidate_event_reviews": [],
            "risk_checks": ["missing_structured_event_row"],
        }
    structured_record = dict(structured_event_row.get("structured_record") or {})
    selection = dict(structured_record.get("selection") or {})
    selected_ids = [str(event_id) for event_id in selection.get("selected_event_ids") or []]
    original_label = str(selection.get("final_label") or "")
    original_kind = str(selection.get("final_kind") or "")
    normalized_by_id = llm_event_reasoner._normalized_event_by_id(structured_event_row)
    event_by_id = {
        str(event.get("event_id") or ""): event
        for event in structured_record.get("events") or []
        if isinstance(event, Mapping)
    }
    reviews = [
        _event_review(
            event_id,
            event,
            normalized_by_id.get(event_id),
            selected=event_id in selected_ids,
            original_label=original_label,
        )
        for event_id, event in event_by_id.items()
    ]
    selected_reviews = [review for review in reviews if review["is_original_selected"]]
    possible_profiles = _possible_profiles(
        original_label=original_label,
        original_kind=original_kind,
        selected_reviews=selected_reviews,
        candidate_reviews=reviews,
    )
    return {
        "possible_profiles": possible_profiles,
        "selected_event_review": selected_reviews,
        "candidate_event_reviews": reviews,
        "risk_checks": _risk_checks(
            original_label=original_label,
            original_kind=original_kind,
            selected_reviews=selected_reviews,
            candidate_reviews=reviews,
        ),
    }


def _event_review(
    event_id: str,
    event: Mapping[str, Any],
    normalized: Mapping[str, Any] | None,
    *,
    selected: bool,
    original_label: str,
) -> dict[str, Any]:
    normalized_label = str((normalized or {}).get("normalized_label") or "")
    semantic_kind = str((normalized or {}).get("semantic_kind") or "")
    text = " ".join(
        str(event.get(key) or "")
        for key in (
            "kind",
            "raw_value",
            "temporality",
            "assertion_status",
            "applies_to",
            "time_window",
            "evidence",
            "notes",
        )
    )
    flags = _marker_flags(text)
    if selected and normalized_label and normalized_label != original_label:
        flags.append("selected_event_candidate_differs_from_original_final")
    return {
        "event_id": event_id,
        "is_original_selected": selected,
        "event_kind": event.get("kind"),
        "temporality": event.get("temporality"),
        "assertion_status": event.get("assertion_status"),
        "applies_to": event.get("applies_to"),
        "time_window": event.get("time_window"),
        "evidence": event.get("evidence"),
        "normalized_label": normalized_label or None,
        "semantic_kind": semantic_kind or None,
        "review_flags": tuple(dict.fromkeys(flags)),
    }


def _marker_flags(text: str) -> list[str]:
    lowered = text.lower()
    flags: list[str] = []
    if _has_any(lowered, "last event", "last seizure", "most recent event", "latest"):
        flags.append("last_event_only_or_latest_event")
    if _has_any(lowered, "ago", "occasion", "january", "february", "march"):
        flags.append("anchored_or_isolated_event")
    if _has_any(lowered, "april", "may", "june", "july", "august", "september"):
        flags.append("anchored_or_isolated_event")
    if _has_any(lowered, "october", "november", "december", "10-jan"):
        flags.append("anchored_or_isolated_event")
    if _has_any(lowered, "since starting", "since commencing", "therapy", "diet"):
        flags.append("treatment_anchor")
    if _has_any(lowered, "minute", "minutes", "second", "seconds", "lasting"):
        flags.append("duration_or_episode_length")
    if _has_any(lowered, "unclear", "unquantified", "possibly", "infrequent"):
        flags.append("vague_or_uncertain_frequency")
    if _has_any(lowered, "current pattern", "typical pattern", "monthly", "weekly"):
        flags.append("explicit_recurring_cadence")
    if _has_any(lowered, "daily", "per month", "per week", "per day", "every "):
        flags.append("explicit_recurring_cadence")
    if _has_any(lowered, "so far this year", "this year", "year to date"):
        flags.append("broad_elapsed_window_total")
    if _has_any(lowered, "past six", "past 6", "past four", "past 4"):
        flags.append("defined_recent_assessment_window")
    if _has_any(lowered, "clusters", "cluster", "per cluster"):
        flags.append("cluster_axis_present")
    if _has_any(lowered, "historical", "prior to", "in the past", "resolved"):
        flags.append("historical_or_resolved_context")
    if _has_any(lowered, "no further events", "no subsequent events", "seizure free"):
        flags.append("absence_since_statement")
    return flags


def _possible_profiles(
    *,
    original_label: str,
    original_kind: str,
    selected_reviews: Sequence[Mapping[str, Any]],
    candidate_reviews: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    selected_boundary_ids = [
        str(review["event_id"])
        for review in selected_reviews
        if str(review.get("semantic_kind") or "") in BOUNDARY_KINDS
    ]
    selected_flags = set().union(
        *(set(review.get("review_flags") or []) for review in selected_reviews)
    )
    boundary_candidate_ids = [
        str(review["event_id"])
        for review in candidate_reviews
        if str(review.get("semantic_kind") or "") in BOUNDARY_KINDS
    ]
    recurring_frequency_ids = [
        str(review["event_id"])
        for review in candidate_reviews
        if review.get("semantic_kind") == "frequency"
        and "explicit_recurring_cadence" in set(review.get("review_flags") or [])
    ]
    if (
        selected_boundary_ids
        and original_kind in {"frequency", "unknown"}
        and selected_flags
        & {
            "last_event_only_or_latest_event",
            "anchored_or_isolated_event",
            "duration_or_episode_length",
            "treatment_anchor",
            "vague_or_uncertain_frequency",
        }
    ):
        profiles.append(
            {
                "profile": "last_event_only_boundary",
                "candidate_event_ids": selected_boundary_ids,
                "trigger": "selected_event_boundary_candidate_conflicts_with_original_final",
            }
        )
    if (
        selected_boundary_ids
        and "duration_or_episode_length" in selected_flags
        and _looks_numeric_frequency_label(original_label)
    ):
        profiles.append(
            {
                "profile": "duration_or_episode_length_boundary",
                "candidate_event_ids": selected_boundary_ids,
                "trigger": "duration_text_rendered_as_frequency_label",
            }
        )
    if (
        selected_boundary_ids
        and "treatment_anchor" in selected_flags
        and original_kind == "frequency"
    ):
        profiles.append(
            {
                "profile": "treatment_anchor_boundary",
                "candidate_event_ids": selected_boundary_ids,
                "trigger": "count_since_treatment_anchor_has_boundary_candidate",
            }
        )
    if (
        original_kind == "frequency"
        and recurring_frequency_ids
        and "broad_elapsed_window_total" in selected_flags
    ):
        profiles.append(
            {
                "profile": "recurring_cadence_preferred",
                "candidate_event_ids": recurring_frequency_ids,
                "trigger": "current_recurring_cadence_vs_elapsed_total",
            }
        )
    if original_kind == "seizure_free" and boundary_candidate_ids:
        profiles.append(
            {
                "profile": "seizure_free_sentinel_boundary",
                "candidate_event_ids": boundary_candidate_ids,
                "trigger": "seizure_free_original_with_boundary_candidate",
            }
        )
    return profiles


def _risk_checks(
    *,
    original_label: str,
    original_kind: str,
    selected_reviews: Sequence[Mapping[str, Any]],
    candidate_reviews: Sequence[Mapping[str, Any]],
) -> list[str]:
    checks: list[str] = []
    if original_kind in {"unknown", "no_reference"}:
        checks.append("boundary_to_boundary_churn_disallowed")
    if "cluster" in original_label.lower():
        checks.append("preserve_original_cluster_label")
    if original_kind != "seizure_free" and any(
        review.get("semantic_kind") == "seizure_free" for review in candidate_reviews
    ):
        checks.append("seizure_free_replacement_disallowed")
    selected_flags = set().union(
        *(set(review.get("review_flags") or []) for review in selected_reviews)
    )
    if "defined_recent_assessment_window" in selected_flags:
        checks.append("bounded_recent_count_may_be_valid")
    return checks


def _structured_selection(structured_event_row: Mapping[str, Any] | None) -> dict[str, Any]:
    if structured_event_row is None:
        return {}
    return dict(
        dict(structured_event_row.get("structured_record") or {}).get("selection") or {}
    )


def _looks_numeric_frequency_label(label: str) -> bool:
    lowered = label.lower()
    return " per " in lowered and any(ch.isdigit() for ch in lowered)


def _has_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)
