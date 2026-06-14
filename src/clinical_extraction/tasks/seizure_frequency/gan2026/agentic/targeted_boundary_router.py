"""Targeted boundary router over saved Gan 2026 structured events.

This is a V3-style candidate from the test-0.85 plan. The model routes each
row to a named specialist profile or keeps the original structured-event final.
When it acts, deterministic code only renders the selected existing normalized
structured-event candidate and scores after the model-owned selection.
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

PROMPT_VERSION = "gan2026_targeted_boundary_router_v0_4"
PIPELINE_FAMILY = "targeted_boundary_router"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = (
    structured_event_verifier.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_targeted_boundary_router_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_targeted_boundary_router_validation.md")

ROUTER_PROFILES = {
    "sentinel_boundary": (
        "Use for unknown/no_reference/last-event-only boundaries. Act when the "
        "original final computed a frequency or seizure-free state from anchored, "
        "one-off, nonrecurring, last-event, uncertain, or no-reference evidence, "
        "and an existing event normalized_candidate is unknown, no_reference, or "
        "unresolved_multiple."
    ),
    "rate_denominator": (
        "Use for denominator/range/current-cadence errors. Act when the original "
        "final uses a broad elapsed-window total, lower current burden, or boundary "
        "state while another current event has a clearer recurring frequency "
        "normalized_candidate."
    ),
    "cluster_burden": (
        "Use for cluster-axis errors. Act only when an existing event explicitly "
        "represents the clinically relevant cluster cadence or events-per-cluster "
        "burden better than original_final."
    ),
    "multi_semiology_burden": (
        "Use when several active semiologies are extracted and another current "
        "event has a higher active burden than the original selected event."
    ),
}

ACTION_VALUES = (
    "keep_original_structured_event_final",
    "replace_with_existing_event",
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
    """Run or prompt-smoke a targeted router over saved SE rows."""

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
            "artifact_kind": "gan2026_targeted_boundary_router_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": PROMPT_VERSION,
            "structured_event_source_path": str(source_path),
            "structured_event_source_role": (
                "pure structured-event V0 comparator and router substrate; "
                "the router action owns any selected replacement event"
            ),
            "claim_boundary": (
                "validation-development V3 targeted router scaffold; no holdout "
                "use, no row-level test inspection, and no benchmark claim"
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
    """Build a model-facing targeted-router payload without IDs, gold, or split."""

    structured_input = llm_event_reasoner.inspect_structured_events(
        structured_event_row
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 targeted structured-event boundary routing",
        "variant": "targeted_boundary_router",
        "instructions": [
            (
                "Route first, then either keep the original structured-event "
                "final or select one existing event."
            ),
            (
                "The original structured-event final answer is an LLM answer. "
                "Use keep_original_structured_event_final when no named profile "
                "is clearly triggered."
            ),
            (
                "Use only the event table and evidence contexts below; do not use "
                "outside final-answer sources, row IDs, split membership, scoring "
                "metadata, deterministic rules, or deterministic top labels."
            ),
            (
                "router_hints are split-neutral diagnostics over the structured-event "
                "table. They may suggest where to inspect, but they do not choose the "
                "clinical answer. Verify the evidence before acting."
            ),
            (
                "If you act, selected_event_ids must contain exactly one event ID "
                "from the event table and the final label will be rendered from "
                "that event's normalized_candidate.normalized_label."
            ),
            (
                "Do not recompute durations, rates, or seizure-free labels from "
                "scratch. If the better answer is not already an existing "
                "normalized_candidate label, keep original_final."
            ),
            (
                "Do not replace a numeric/range frequency with seizure_free in "
                "this router. Seizure-free rescue needs a separate temporal "
                "specialist."
            ),
            (
                "Before returning replace_with_existing_event, inspect the selected "
                "event normalized_candidate.semantic_kind. If it is seizure_free "
                "and original_final.final_kind is not seizure_free, stop and return "
                "keep_original_structured_event_final."
            ),
            (
                "Do not change unknown to no seizure frequency reference, or no "
                "seizure frequency reference to unknown. Boundary-to-boundary churn "
                "is not useful on this surface; keep original_final."
            ),
            (
                "Preserve cluster labels. If original_final.final_label contains "
                "cluster, do not replace it with a non-cluster normalized_candidate. "
                "Use cluster_burden only for a better existing cluster candidate or "
                "a clearly higher unresolved_multiple burden."
            ),
            (
                "Anchored numeric mentions are not recurring cadences: isolated "
                "recent events, named calendar months, latest-on-date summaries, "
                "counts since starting treatment, and vague review windows should "
                "route to sentinel_boundary when an existing unknown/no_reference "
                "candidate is available."
            ),
            (
                "Allowed sentinel_boundary action A: original_final is a numeric "
                "frequency derived from anchored or one-off evidence, and the "
                "selected existing event normalized_candidate is unknown, "
                "no_reference, or unresolved_multiple."
            ),
            (
                "Allowed sentinel_boundary action B: original_final is seizure_free "
                "but the selected existing event normalized_candidate is unknown or "
                "no_reference, and the evidence is last-event-only, negated "
                "non-target semiology, uncertain, or otherwise not a current "
                "seizure-free duration. Do not use this action when the selected "
                "event normalized_candidate is seizure_free."
            ),
            (
                "Explicit recurring cadences such as monthly, weekly, daily, every "
                "few weeks, or every four to five weeks are stronger than broad "
                "elapsed-window totals such as so far this year; route these to "
                "rate_denominator when an existing current cadence event is available."
            ),
            (
                "For clusters, keep cluster cadence separate from events per "
                "cluster. Act only if an existing cluster event already carries "
                "the better normalized candidate."
            ),
            (
                "For multiple active semiologies, act only if another current "
                "event's normalized candidate is a clearly higher active burden "
                "than the original selected event."
            ),
            "Evidence entries should be exact substrings from the note when possible.",
            (
                "Put the routed specialist profile in contradiction_profile as "
                "one string prefixed with router:, for example router:sentinel_boundary."
            ),
            (
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "router_profiles": ROUTER_PROFILES,
        "router_hints": _router_hints(structured_event_row),
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
            "contradiction_profile": "list containing router:<profile> when acting",
            "calculation_trace": "short boundary trace, or null",
            "clinical_rationale": "brief specialist rationale for the action",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for this v0.1 router",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "structured_event_input": structured_input,
        "raw_evidence_contexts": llm_event_reasoner._evidence_contexts(
            record.note_text,
            structured_event_row,
        ),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize router rows and routed specialist profiles."""

    summary = structured_event_verifier.summarize_rows(rows)
    profiles: Counter[str] = Counter()
    for row in rows:
        decision = dict(row.get("verifier_decision_record") or {})
        for profile in decision.get("contradiction_profile") or []:
            text = str(profile)
            if text.startswith("router:"):
                profiles[text] += 1
    summary["router_profiles"] = dict(sorted(profiles.items()))
    return summary


def _router_hints(structured_event_row: Mapping[str, Any] | None) -> dict[str, Any]:
    if structured_event_row is None:
        return {"possible_profiles": [], "risk_checks": ["missing_structured_event_row"]}
    selection = dict(
        dict(structured_event_row.get("structured_record") or {}).get("selection") or {}
    )
    original_label = str(selection.get("final_label") or "")
    original_kind = str(selection.get("final_kind") or "")
    selected_ids = [str(event_id) for event_id in selection.get("selected_event_ids") or []]
    normalized_by_id = llm_event_reasoner._normalized_event_by_id(structured_event_row)
    structured_record = dict(structured_event_row.get("structured_record") or {})
    event_by_id = {
        str(event.get("event_id") or ""): event
        for event in structured_record.get("events") or []
        if isinstance(event, Mapping)
    }
    possible_profiles: list[dict[str, Any]] = []
    risk_checks: list[str] = []
    boundary_candidate_ids = _candidate_ids_by_semantic_kind(
        normalized_by_id,
        {"unknown", "no_reference", "unresolved_multiple"},
        excluded_ids=set(selected_ids),
    )
    frequency_candidate_ids = _candidate_ids_by_semantic_kind(
        normalized_by_id,
        {"frequency"},
        excluded_ids=set(selected_ids),
    )
    if original_kind in {"unknown", "no_reference"}:
        risk_checks.append("boundary_to_boundary_churn")
    if "cluster" in original_label.lower():
        risk_checks.append("preserve_original_cluster_label")
    if original_kind != "seizure_free" and _candidate_ids_by_semantic_kind(
        normalized_by_id,
        {"seizure_free"},
        excluded_ids=set(selected_ids),
    ):
        risk_checks.append("selected_seizure_free_replacement_disallowed")
    selected_evidence = " ".join(
        str(event_by_id.get(event_id, {}).get("evidence") or "")
        for event_id in selected_ids
    )
    if (
        original_kind == "frequency"
        and boundary_candidate_ids
        and _looks_anchored_or_nonrecurring(selected_evidence)
    ):
        possible_profiles.append(
            {
                "profile": "sentinel_boundary",
                "candidate_event_ids": boundary_candidate_ids,
                "trigger": "original_frequency_from_anchored_or_nonrecurring_evidence",
            }
        )
    if original_kind == "seizure_free" and boundary_candidate_ids:
        possible_profiles.append(
            {
                "profile": "sentinel_boundary",
                "candidate_event_ids": boundary_candidate_ids,
                "trigger": "original_seizure_free_with_existing_boundary_event",
            }
        )
    if original_kind in {"frequency", "unknown", "no_reference"} and frequency_candidate_ids:
        clearer_cadence_ids = [
            event_id
            for event_id in frequency_candidate_ids
            if _looks_like_recurring_cadence(
                str(event_by_id.get(event_id, {}).get("evidence") or "")
            )
        ]
        if clearer_cadence_ids:
            possible_profiles.append(
                {
                    "profile": "rate_denominator",
                    "candidate_event_ids": clearer_cadence_ids,
                    "trigger": "alternate_current_recurring_cadence_candidate",
                }
            )
    return {
        "possible_profiles": possible_profiles,
        "risk_checks": risk_checks,
    }


def _candidate_ids_by_semantic_kind(
    normalized_by_id: Mapping[str, Mapping[str, Any]],
    semantic_kinds: set[str],
    *,
    excluded_ids: set[str],
) -> list[str]:
    return [
        event_id
        for event_id, normalized in normalized_by_id.items()
        if event_id not in excluded_ids
        and str(normalized.get("semantic_kind") or "") in semantic_kinds
        and normalized.get("normalized_label") is not None
    ]


def _looks_anchored_or_nonrecurring(text: str) -> bool:
    lowered = text.lower()
    markers = (
        "occasion",
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
        "latest",
        "last ",
        "since starting",
        "since commencing",
        "so far",
        "this year",
        "past six weeks",
        "past 6 weeks",
        "recent",
    )
    return any(marker in lowered for marker in markers)


def _looks_like_recurring_cadence(text: str) -> bool:
    lowered = text.lower()
    markers = (
        "monthly",
        "per month",
        "weekly",
        "per week",
        "daily",
        "per day",
        "every",
        "roughly",
        "approximately",
        "typical pattern",
    )
    return any(marker in lowered for marker in markers)


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
        "# Gan 2026 Targeted Boundary Router",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation-development V3 targeted router artifact.",
        "The model routes named boundary profiles over saved LLM structured events.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: V3 targeted boundary router with one in-prompt specialist.",
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
        f"- Router profiles: `{summary.get('router_profiles', {})}`",
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


class TargetedBoundaryRouterSignature(dspy.Signature):
    """Route one saved structured-event record and emit one JSON action."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with one sanitized structured-event record and evidence contexts."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching StructuredEventVerifierDecision."
    )


class DspyTargetedBoundaryRouterCaller(dspy.Module):
    """DSPy caller for the V3 targeted boundary router."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(TargetedBoundaryRouterSignature)

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
        structured_event_verifier.parse_verifier_decision_json(
            raw_output,
            structured_event_row,
        )
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
    prediction = DspyTargetedBoundaryRouterCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


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
