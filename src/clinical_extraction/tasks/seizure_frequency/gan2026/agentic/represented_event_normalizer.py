"""Represented-event normalization reasoner for Gan 2026 structured events.

This V8 candidate targets rows where a useful event is already represented in
the saved structured-event table, but its normalized candidate or final
selection is wrong. The model may keep the original structured-event final,
select an existing normalized event, or render a recomputed Gan label from
selected existing event evidence. Deterministic code validates schema, label
format, selected event membership, evidence substrings, and scoring only.
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
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_represented_event_normalizer_v0_2"
PIPELINE_FAMILY = "represented_event_normalizer"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = (
    structured_event_verifier.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_represented_event_normalizer_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_represented_event_normalizer_validation.md")

ACTION_VALUES = (
    "keep_original_structured_event_final",
    "replace_with_recomputed_fact_from_selected_evidence",
)


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
    """Run or prompt-smoke represented-event normalization over saved SE rows."""

    del escalation_reason, candidate_set_jsonl_path
    source_path = (
        structured_event_source_path
        or structured_event_jsonl_path
        or DEFAULT_STRUCTURED_EVENT_JSONL_PATH
    )
    if structured_event_rows is None:
        structured_event_rows = load_jsonl_rows(source_path)
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

    structured_rows_by_index = llm_event_reasoner._rows_by_source_index(
        structured_event_rows
    )
    metadata = build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version="none",
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
    )
    metadata.update(
        {
            "artifact_kind": "gan2026_represented_event_normalizer_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": PROMPT_VERSION,
            "structured_event_source_path": str(source_path),
            "structured_event_source_role": (
                "pure structured-event V0 comparator and represented-event "
                "normalization substrate; the model owns any recomputed label"
            ),
            "claim_boundary": (
                "validation-development V8 represented-event normalizer; no "
                "holdout use, no row-level test inspection, and no benchmark claim"
            ),
            "dspy_cache": dspy_cache,
        }
    )

    rows: list[dict[str, Any]] = []
    for record in records:
        rows.append(
            _build_row(
                record,
                structured_event_row=structured_rows_by_index.get(
                    record.source_row_index
                ),
                split=split,
                split_manifest=split_manifest,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                mode=mode,
            )
        )
        if progress_every and len(rows) % progress_every == 0:
            _emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_rows(rows)
    metadata["gate"] = structured_event_verifier.gate_interpretation(metadata["summary"])
    return rows, metadata


def build_prompt_input(
    record: GanFrequencyRecord,
    structured_event_row: Mapping[str, Any] | None,
) -> str:
    """Build a model-facing normalizer payload without IDs, gold, or split."""

    structured_input = llm_event_reasoner.inspect_structured_events(
        structured_event_row
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 represented-event normalization reasoning",
        "variant": "V8_represented_event_normalizer",
        "instructions": [
            (
                "Decide whether the original structured-event final answer should "
                "be kept or recomputed from a selected existing event's evidence."
            ),
            (
                "Use only the event table and raw evidence contexts below. Do not "
                "use outside final-answer sources, row IDs, split membership, gold "
                "labels, scoring metadata, deterministic rules, or deterministic "
                "top labels."
            ),
            (
                "Use replace_with_recomputed_fact_from_selected_evidence only when "
                "a selected existing event has exact evidence for a source-near "
                "frequency, denominator, range, cluster burden, seizure-free "
                "duration, unknown state, or no-reference state that its "
                "normalized_candidate failed to render correctly."
            ),
            (
                "For recompute, selected_event_ids must name one or more existing "
                "event IDs from the table, evidence must be exact note substrings, "
                "and final_label must be the Gan-style label you derive from that "
                "selected existing event evidence."
            ),
            (
                "Use keep_original_structured_event_final when no selected existing "
                "event clearly supports a different renderable label."
            ),
            (
                "Do not use replace_with_existing_event in this run. Existing-event "
                "replacement was tested separately; this candidate only tests "
                "represented-event recomputation."
            ),
            (
                "Do not create new events. If the decisive fact is absent from the "
                "event table, keep original; that was the event-completion task."
            ),
            (
                "Do not compute from broad raw-note context alone. The recomputed "
                "label must be anchored to selected_event_ids."
            ),
            (
                "For cluster rows, separate cluster cadence from events per cluster "
                "and render a cluster label only when both axes are supported by "
                "selected event evidence."
            ),
            (
                "For denominator/range rows, state the numerator, denominator, and "
                "time unit in calculation_trace before returning a new label."
            ),
            (
                "For unknown/no-reference rows, use unknown when frequency evidence "
                "exists but is not renderable; use no seizure frequency reference "
                "only when the evidence supports absence of frequency information."
            ),
            (
                "For seizure-free rows, require exact no-events-since or "
                "seizure-free duration evidence and no conflicting current/recent "
                "frequency event in the selected evidence."
            ),
            "Prefer keep_original when the correction is uncertain or stylistic.",
            (
                "final_label must be a valid Gan label only: unknown, no seizure "
                "frequency reference, seizure free, multiple per day/week/month/year, "
                "a numeric/range per day/week/month/year label, or a cluster label."
            ),
            (
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(ACTION_VALUES),
            "final_label": "Gan-style label string owned by the selected action",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": "list of existing event IDs selected from the event table",
            "rejected_event_ids": "list of event IDs explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the action",
            "contradiction_profile": (
                "list such as represented_rate_denominator, represented_cluster_axis, "
                "represented_sentinel_boundary, represented_multi_semiology"
            ),
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief clinical rationale for the action",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for this v0.1 normalizer",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "disabled_actions_for_this_run": [
            "replace_with_existing_event",
            "abstain_unrenderable",
        ],
        "structured_event_input": structured_input,
        "raw_evidence_contexts": llm_event_reasoner._evidence_contexts(
            record.note_text,
            structured_event_row,
        ),
        "raw_note_excerpt": record.note_text[:6000],
        "excerpt_truncated": len(record.note_text) > 6000,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_normalizer_decision_json(
    raw_output: str,
    structured_event_row: Mapping[str, Any] | None,
) -> structured_event_verifier.ParsedVerifierDecision:
    """Parse and validate a represented-event normalizer decision."""

    parsed = structured_event_verifier.parse_verifier_decision_json(
        raw_output,
        structured_event_row,
    )
    decision = parsed.raw_verifier_decision
    if decision is not None and decision.action == "replace_with_existing_event":
        return parsed.model_copy(
            update={
                "final_decision": None,
                "parse_errors": [
                    *parsed.parse_errors,
                    (
                        "action_render_error: "
                        "replace_existing_disabled_for_represented_event_normalizer"
                    ),
                ],
                "action_render_events": [],
            }
        )
    if (
        decision is None
        or decision.action != "replace_with_recomputed_fact_from_selected_evidence"
        or parsed.final_decision is None
    ):
        return parsed

    validation_errors = _recomputed_action_errors(decision, structured_event_row)
    if validation_errors:
        return parsed.model_copy(
            update={
                "final_decision": None,
                "parse_errors": [*parsed.parse_errors, *validation_errors],
                "action_render_events": [
                    event
                    for event in parsed.action_render_events
                    if "replace_with_recomputed_fact_from_selected_evidence" not in event
                ],
            }
        )
    return parsed.model_copy(
        update={
            "action_render_events": [
                *parsed.action_render_events,
                (
                    "normalizer_action_validated:"
                    "replace_with_recomputed_fact_from_selected_evidence"
                ),
            ]
        }
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize represented-event normalizer rows."""

    summary = structured_event_verifier.summarize_rows(rows)
    summary["recomputed_fact_actions"] = 0
    profiles: Counter[str] = Counter()
    for row in rows:
        decision = dict(row.get("normalizer_decision_record") or {})
        if decision.get("action") == "replace_with_recomputed_fact_from_selected_evidence":
            summary["recomputed_fact_actions"] += 1
        for profile in decision.get("contradiction_profile") or []:
            profiles[str(profile)] += 1
    summary["normalizer_profiles"] = dict(sorted(profiles.items()))
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
        "# Gan 2026 Represented-Event Normalizer",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation-development V8 represented-event normalization artifact.",
        "The model may recompute a Gan label only from selected existing event evidence.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: V8 represented-event normalizer over saved structured events.",
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
        f"- Action-render failures: {summary.get('action_render_failures', 0)}",
        f"- Recomputed-fact actions: {summary.get('recomputed_fact_actions', 0)}",
        f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
        f"- V0 Purist: {summary.get('v0_purist_correct', 0)}/{summary.get('rows', 0)}",
        (
            f"- Final Purist: {summary.get('final_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        f"- Net Purist gain vs V0: {summary.get('net_purist_gain_vs_v0', 0)}",
        (
            "- Changed-label precision vs V0: "
            f"{summary.get('changed_label_precision_vs_v0')}"
        ),
        f"- Actions: `{summary.get('verifier_actions', {})}`",
        f"- Profiles: `{summary.get('normalizer_profiles', {})}`",
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
        normalizer_record = dict(row.get("normalizer_decision_record") or {})
        notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        lines.append(
            f"| {row.get('source_row_index')} | "
            f"`{normalizer_record.get('action')}` | "
            f"`{normalizer_record.get('contradiction_profile')}` | "
            f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
            f"`{dict(layers.get('final') or {}).get('final_label')}` | "
            f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
            f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


class RepresentedEventNormalizerSignature(dspy.Signature):
    """Reason over represented events and emit one JSON decision."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with sanitized structured events and evidence contexts."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching StructuredEventVerifierDecision."
    )


class DspyRepresentedEventNormalizerCaller(dspy.Module):
    """DSPy caller for V8 represented-event normalization."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(RepresentedEventNormalizerSignature)

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
        parse_normalizer_decision_json(raw_output, structured_event_row)
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
    decision_record = (
        parsed.raw_verifier_decision.model_dump(mode="json")
        if parsed.raw_verifier_decision
        else None
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
        "normalizer_decision_record": decision_record,
        "verifier_decision_record": decision_record,
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
    prediction = DspyRepresentedEventNormalizerCaller()(
        prompt_input_json=prompt_input_json
    )
    return str(prediction.decision_json)


def _recomputed_action_errors(
    decision: structured_event_verifier.StructuredEventVerifierDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> list[str]:
    event_ids = _existing_event_ids(structured_event_row)
    errors: list[str] = []
    selected_ids = tuple(str(event_id) for event_id in decision.selected_event_ids)
    if not selected_ids:
        errors.append("action_render_error: recomputed_selected_event_missing")
    missing = sorted(event_id for event_id in selected_ids if event_id not in event_ids)
    if missing:
        errors.append(
            "action_render_error: recomputed_selected_event_missing:"
            + ",".join(missing)
        )
    return errors


def _existing_event_ids(structured_event_row: Mapping[str, Any] | None) -> set[str]:
    if structured_event_row is None:
        return set()
    structured_record = dict(structured_event_row.get("structured_record") or {})
    return {
        str(event.get("event_id") or "")
        for event in structured_record.get("events") or []
        if isinstance(event, Mapping) and event.get("event_id") is not None
    }


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    checkpoint_metadata = dict(metadata)
    checkpoint_metadata["summary"] = summarize_rows(rows)
    checkpoint_metadata["progress"] = {"completed_rows": len(rows), "total_rows": total}
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None:
        write_report(rows, checkpoint_metadata, report_path, jsonl_path=jsonl_path or Path(""))
