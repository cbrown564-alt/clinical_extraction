"""Cross-model structured-event adjudicator for Gan 2026.

This V10 candidate asks one LLM coordinator to choose among saved structured
event finals from GPT, Qwen, and DeepSeek. The coordinator owns only the agent
selection. Deterministic code renders the chosen agent's existing final label,
performs format-only repair if needed, validates evidence substrings, and
scores the result against validation gold after the fact.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    llm_event_reasoner,
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
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_cross_model_structured_event_adjudicator_v0_3"
SAFETY_GATE_VERSION = "gan2026_cross_model_peer_selection_gate_v0_2"
PIPELINE_FAMILY = "cross_model_structured_event_adjudicator"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = llm_event_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl"
)
DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_cross_model_structured_event_adjudicator_validation.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_cross_model_structured_event_adjudicator_validation.md"
)

AgentId = Literal["gpt", "qwen", "deepseek"]
CrossModelAction = Literal[
    "keep_gpt_final",
    "select_qwen_final",
    "select_deepseek_final",
]
AGENT_IDS: tuple[AgentId, ...] = ("gpt", "qwen", "deepseek")
ACTION_TO_AGENT: dict[str, AgentId] = {
    "keep_gpt_final": "gpt",
    "select_qwen_final": "qwen",
    "select_deepseek_final": "deepseek",
}
PROMPT_ACTION_VALUES = tuple(ACTION_TO_AGENT)
DECISION_KIND_VALUES = {
    "frequency",
    "seizure_free",
    "unknown",
    "no_reference",
    "unresolved_multiple",
}


class CrossModelAdjudicatorDecision(BaseModel):
    """One coordinator decision over saved structured-event agents."""

    model_config = ConfigDict(extra="forbid")

    action: CrossModelAction
    selected_agent_id: AgentId
    final_label: str
    final_kind: llm_event_reasoner.DecisionKind
    selected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    rejected_agent_ids: tuple[AgentId, ...] = Field(default_factory=tuple)
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    comparison_profile: tuple[str, ...] = Field(default_factory=tuple)
    calculation_trace: str | None = None
    clinical_rationale: str
    uncertainty: llm_event_reasoner.Uncertainty
    attribution: llm_event_reasoner.DecisionAttribution


class ParsedCrossModelDecision(BaseModel):
    """Raw, format-only, and selected-agent rendered views."""

    model_config = ConfigDict(extra="forbid")

    raw_decision: CrossModelAdjudicatorDecision | None
    raw_common_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    format_only_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    final_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
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
    agent_rows_by_id: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run or prompt-smoke a live coordinator over saved structured-event agents."""

    del escalation_reason, candidate_set_jsonl_path
    source_path = (
        structured_event_source_path
        or structured_event_jsonl_path
        or DEFAULT_STRUCTURED_EVENT_JSONL_PATH
    )
    agent_sources = {
        "gpt": source_path,
        "qwen": DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH,
        "deepseek": DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH,
    }
    if structured_event_rows is None:
        structured_event_rows = load_jsonl_rows(source_path)
    loaded_agent_rows = _load_agent_rows(
        gpt_rows=structured_event_rows,
        agent_sources=agent_sources,
        agent_rows_by_id=agent_rows_by_id,
    )
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

    rows_by_agent = {
        agent_id: llm_event_reasoner._rows_by_source_index(rows)
        for agent_id, rows in loaded_agent_rows.items()
    }
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
            "artifact_kind": "gan2026_cross_model_structured_event_adjudicator_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": f"{PROMPT_VERSION}+{SAFETY_GATE_VERSION}",
            "safety_gate_version": SAFETY_GATE_VERSION,
            "agent_source_paths": {
                agent_id: str(path) for agent_id, path in agent_sources.items()
            },
            "structured_event_source_role": (
                "GPT is the LLM structured-event fallback; Qwen and DeepSeek are "
                "peer LLM structured-event candidates. Deterministic top labels "
                "are not provided to the model or used as fallback."
            ),
            "claim_boundary": (
                "validation-development V10 cross-model structured-event "
                "adjudicator; no holdout use, no row-level test inspection, and "
                "no benchmark claim"
            ),
            "dspy_cache": dspy_cache,
        }
    )

    rows: list[dict[str, Any]] = []
    for record in records:
        rows.append(
            _build_row(
                record,
                agent_rows={
                    agent_id: rows_by_agent.get(agent_id, {}).get(
                        record.source_row_index
                    )
                    for agent_id in AGENT_IDS
                },
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
    metadata["gate"] = llm_event_reasoner.gate_interpretation(metadata["summary"])
    return rows, metadata


def build_prompt_input(
    record: GanFrequencyRecord,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
) -> str:
    """Build a split-neutral coordinator payload over three LLM agents."""

    agent_inputs = [
        _agent_prompt_summary(agent_id, agent_rows.get(agent_id))
        for agent_id in AGENT_IDS
    ]
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 cross-model structured-event final selection",
        "variant": "V10_cross_model_structured_event_adjudicator",
        "instructions": [
            (
                "Choose exactly one saved structured-event agent final as the "
                "current seizure-frequency answer: keep GPT, select Qwen, or "
                "select DeepSeek."
            ),
            (
                "Do not invent, recompute, average, majority-vote blindly, or "
                "use outside final-answer sources. The final answer will be "
                "rendered from the selected agent's original_final.final_label."
            ),
            (
                "Use only the agent event tables, agent rationales, exact "
                "evidence contexts, and note excerpt below. Do not use row IDs, "
                "split membership, gold labels, scoring metadata, deterministic "
                "rules, or deterministic top labels."
            ),
            (
                "Prefer GPT unless a peer agent has clearer source-grounded "
                "evidence for a current frequency, seizure-free state, unknown/"
                "no-reference boundary, cluster burden, or multi-semiology burden."
            ),
            (
                "Select a peer only when its selected event evidence resolves a "
                "clinical contradiction in GPT's selected final, not merely "
                "because two agents share the same exact label."
            ),
            (
                "High-precision peer action for this run: select Qwen or "
                "DeepSeek only for frequency-vs-frequency recurring-cadence "
                "rescues where GPT selected a broad elapsed-window total such as "
                "'so far this year' and both peers expose a clearer current "
                "typical cadence such as monthly, weekly, daily, or every N weeks."
            ),
            (
                "Keep GPT for peer seizure-free replacements, GPT unknown/"
                "no-reference to peer numeric frequency, or multi-semiology/"
                "cluster disagreements that are not one of the high-precision "
                "rescues named here."
            ),
            (
                "Secondary high-precision peer action: select a peer unknown or "
                "no-reference final only when GPT rendered a numeric frequency "
                "from isolated last-event, anchored, vague, or duration evidence "
                "rather than a true cadence. This boundary action never applies "
                "to peer seizure-free finals."
            ),
            (
                "When selecting a peer, final_label must copy that peer's "
                "original_final.final_label exactly and selected_event_ids should "
                "copy that peer's original_final.selected_event_ids."
            ),
            (
                "For keep_gpt_final, selected_agent_id must be gpt. For "
                "select_qwen_final, selected_agent_id must be qwen. For "
                "select_deepseek_final, selected_agent_id must be deepseek."
            ),
            "Evidence entries should be exact substrings from the note when possible.",
            (
                "final_kind, uncertainty, attribution, action, and selected_agent_id "
                "must each be one string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(PROMPT_ACTION_VALUES),
            "selected_agent_id": list(AGENT_IDS),
            "final_label": "copy of selected agent original_final.final_label",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": "selected event IDs from the chosen agent",
            "rejected_agent_ids": "agent IDs explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the choice",
            "comparison_profile": "list of disagreement profiles driving the choice",
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief rationale for why this agent wins",
            "uncertainty": "one string: low | medium | high",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "agent_inputs": agent_inputs,
        "agreement_features": _agreement_features(agent_inputs),
        "adjudicator_hints": _adjudicator_hints(agent_rows),
        "raw_evidence_contexts": _combined_evidence_contexts(
            record.note_text,
            agent_rows,
        ),
        "raw_note_excerpt": record.note_text[:6000],
        "excerpt_truncated": len(record.note_text) > 6000,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_cross_model_decision_json(
    raw_output: str,
    *,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    note_text: str,
    safety_policy: Literal["high_precision", "none"] = "high_precision",
) -> ParsedCrossModelDecision:
    """Parse one coordinator output and render the selected agent final."""

    parse_errors: list[str] = []
    extracted = llm_event_reasoner._extract_json_object(raw_output)
    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
            extracted
        )
    except json.JSONDecodeError as exc:
        repaired_extracted = extracted.replace('\\"', '"')
        if repaired_extracted != extracted:
            try:
                raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
                    repaired_extracted
                )
                dialect_notes = [
                    *dialect_notes,
                    "json_dialect_repaired: escaped_list_item_quotes",
                ]
            except json.JSONDecodeError:
                return _fallback_parse_result(
                    agent_rows=agent_rows,
                    note_text=note_text,
                    reason=f"invalid_json:{exc.msg}",
                )
        else:
            return _fallback_parse_result(
                agent_rows=agent_rows,
                note_text=note_text,
                reason=f"invalid_json:{exc.msg}",
            )
    parse_errors.extend(dialect_notes)
    payload = _filter_decision_payload(repair_decision_payload(raw_payload))
    payload, shape_notes = _repair_decision_shape(payload)
    parse_errors.extend(shape_notes)
    try:
        raw_decision = CrossModelAdjudicatorDecision.model_validate(payload)
    except ValidationError as exc:
        return _fallback_parse_result(
            agent_rows=agent_rows,
            note_text=note_text,
            reason=f"schema_validation_error:{exc.errors()[0]['msg']}",
            parse_errors=parse_errors,
        )

    raw_common = _common_decision_from_adjudicator(raw_decision)
    format_common = raw_common
    repair_trace = repair_prediction_label_format_preserving_with_trace(
        raw_decision.final_label
    )
    repair_events = [
        llm_event_reasoner._repair_event_to_dict(event)
        for event in repair_trace.events
    ]
    if repair_trace.final_label != raw_decision.final_label:
        parse_errors.append(
            "final_label_format_repaired: "
            f"{raw_decision.final_label!r} -> {repair_trace.final_label!r}"
        )
        format_common = raw_common.model_copy(
            update={
                "final_label": repair_trace.final_label,
                "attribution": "llm_selected_format_repaired",
            }
        )
    try:
        label_to_frequency_record(format_common.final_label)
    except ValueError as exc:
        parse_errors.append(f"unscorable_final_label: {exc}")

    expected_agent = ACTION_TO_AGENT.get(raw_decision.action)
    if expected_agent != raw_decision.selected_agent_id:
        fallback = _fallback_parse_result(
            agent_rows=agent_rows,
            note_text=note_text,
            reason="action_agent_mismatch",
            parse_errors=parse_errors,
        )
        return fallback.model_copy(
            update={
                "raw_decision": raw_decision,
                "raw_common_decision": raw_common,
                "format_only_decision": format_common,
                "format_repair_events": repair_events,
            }
        )

    rendered_decision, render_events, render_error = _render_agent_final(
        raw_decision.selected_agent_id,
        raw_decision=raw_decision,
        agent_rows=agent_rows,
        note_text=note_text,
    )
    if render_error:
        fallback = _fallback_parse_result(
            agent_rows=agent_rows,
            note_text=note_text,
            reason=render_error,
            parse_errors=parse_errors,
        )
        return fallback.model_copy(
            update={
                "raw_decision": raw_decision,
                "raw_common_decision": raw_common,
                "format_only_decision": format_common,
                "format_repair_events": repair_events,
            }
        )
    safety_keep_reason = (
        _peer_selection_safety_keep_reason(raw_decision, agent_rows)
        if safety_policy == "high_precision"
        else None
    )
    if safety_keep_reason is not None:
        keep_decision, keep_events, keep_error = _render_agent_final(
            "gpt",
            raw_decision=None,
            agent_rows=agent_rows,
            note_text=note_text,
        )
        if keep_error:
            parse_errors.append(f"action_render_error:{keep_error}")
            keep_decision = None
            keep_events = []
        return ParsedCrossModelDecision(
            raw_decision=raw_decision,
            raw_common_decision=raw_common,
            format_only_decision=format_common,
            final_decision=keep_decision,
            parse_errors=parse_errors,
            format_repair_events=repair_events,
            action_render_events=[
                f"peer_selection_safety_gate_kept_gpt:{safety_keep_reason}",
                *keep_events,
            ],
        )
    return ParsedCrossModelDecision(
        raw_decision=raw_decision,
        raw_common_decision=raw_common,
        format_only_decision=format_common,
        final_decision=rendered_decision,
        parse_errors=parse_errors,
        format_repair_events=repair_events,
        action_render_events=render_events,
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize coordinator performance versus GPT structured-event V0."""

    summary = llm_event_reasoner.summarize_rows(rows)
    selected_agents: Counter[str] = Counter()
    action_events: Counter[str] = Counter()
    label_mismatches = 0
    for row in rows:
        decision = dict(row.get("cross_model_decision_record") or {})
        selected = decision.get("selected_agent_id")
        if selected is None:
            final_record = dict(row.get("decision_record") or {})
            selected = final_record.get("selected_agent_id")
        if selected:
            selected_agents[str(selected)] += 1
        for event in row.get("action_render_events") or []:
            text = str(event)
            action_events[text] += 1
            if text.startswith("selected_agent_label_mismatch"):
                label_mismatches += 1
    summary["selected_agent_counts"] = dict(sorted(selected_agents.items()))
    summary["action_render_events"] = dict(sorted(action_events.items()))
    summary["action_render_fallbacks"] = sum(
        count
        for event, count in action_events.items()
        if event.startswith("action_render_fallback_kept_gpt")
    )
    summary["selected_agent_label_mismatches"] = label_mismatches
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
        "# Gan 2026 Cross-Model Structured-Event Adjudicator",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "This is a validation-development V10 coordinator over saved LLM agents.",
        (
            "The model may keep GPT or select Qwen/DeepSeek; deterministic code "
            "renders the selected agent final."
        ),
        "",
        "## Experiment Unit",
        "",
        "- Work class: V10 cross-model structured-event adjudicator.",
        f"- Rows: {summary.get('rows', 0)}",
        "- Split: `validation`, manifest `gan2026_split_v1`.",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Safety gate version: `{metadata.get('safety_gate_version')}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
        f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
        f"- Action-render fallbacks: {summary.get('action_render_fallbacks', 0)}",
        f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
        f"- GPT V0 Purist: {summary.get('v0_purist_correct', 0)}/{summary.get('rows', 0)}",
        (
            f"- Raw declared Purist: {summary.get('raw_model_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Format-only declared Purist: "
            f"{summary.get('format_only_purist_correct', 0)}/{summary.get('rows', 0)}"
        ),
        f"- Final Purist: {summary.get('final_purist_correct', 0)}/{summary.get('rows', 0)}",
        f"- Net Purist gain vs GPT V0: {summary.get('net_purist_gain_vs_v0', 0)}",
        (
            "- Changed-label precision vs GPT V0: "
            f"{summary.get('changed_label_precision_vs_v0')}"
        ),
        f"- Selected agents: `{summary.get('selected_agent_counts', {})}`",
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
        "| Row | Selected | GPT | Raw | Final | Transition | Evidence exact | Notes |",
        "| ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        layers = dict(row.get("score_layers") or {})
        decision = dict(row.get("cross_model_decision_record") or {})
        notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        lines.append(
            f"| {row.get('source_row_index')} | "
            f"`{decision.get('selected_agent_id')}` | "
            f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
            f"`{dict(layers.get('raw_model') or {}).get('final_label')}` | "
            f"`{dict(layers.get('final') or {}).get('final_label')}` | "
            f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
            f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


class CrossModelAdjudicatorSignature(dspy.Signature):
    """Select one saved structured-event agent final and emit JSON."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with sanitized GPT, Qwen, and DeepSeek structured-event rows."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching CrossModelAdjudicatorDecision."
    )


class DspyCrossModelAdjudicatorCaller(dspy.Module):
    """DSPy caller for V10 cross-model structured-event adjudicator."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(CrossModelAdjudicatorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def _build_row(
    record: GanFrequencyRecord,
    *,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
) -> dict[str, Any]:
    prompt_input_json = build_prompt_input(record, agent_rows)
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
        parse_cross_model_decision_json(
            raw_output,
            agent_rows=agent_rows,
            note_text=record.note_text,
        )
        if raw_output
        else ParsedCrossModelDecision(
            raw_decision=None,
            raw_common_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=["not_run"],
        )
    )
    final_decision = parsed.final_decision
    gpt_reference = llm_event_reasoner._v0_reference(agent_rows.get("gpt"))
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
        "agent_inputs_available": {
            agent_id: agent_rows.get(agent_id) is not None for agent_id in AGENT_IDS
        },
        "agent_references": {
            agent_id: _agent_reference(agent_rows.get(agent_id))
            for agent_id in AGENT_IDS
        },
        "v0_reference": gpt_reference,
        "model_call_attempted": model_call_attempted,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "call_error": call_error,
        "parse_errors": parsed.parse_errors,
        "format_repair_events": parsed.format_repair_events,
        "action_render_events": parsed.action_render_events,
        "cross_model_decision_record": (
            parsed.raw_decision.model_dump(mode="json") if parsed.raw_decision else None
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
            v0_reference=gpt_reference,
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
        + [
            f"missing_{agent_id}_structured_event_row"
            for agent_id in AGENT_IDS
            if agent_rows.get(agent_id) is None
        ],
    }


def _run_model_call(
    prompt_input_json: str,
    *,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    del model, temperature, max_tokens
    prediction = DspyCrossModelAdjudicatorCaller()(
        prompt_input_json=prompt_input_json
    )
    return str(prediction.decision_json)


def _load_agent_rows(
    *,
    gpt_rows: Sequence[Mapping[str, Any]],
    agent_sources: Mapping[str, Path],
    agent_rows_by_id: Mapping[str, Sequence[Mapping[str, Any]]] | None,
) -> dict[str, Sequence[Mapping[str, Any]]]:
    if agent_rows_by_id is not None:
        return {
            "gpt": tuple(agent_rows_by_id.get("gpt", gpt_rows)),
            "qwen": tuple(agent_rows_by_id.get("qwen", ())),
            "deepseek": tuple(agent_rows_by_id.get("deepseek", ())),
        }
    rows: dict[str, Sequence[Mapping[str, Any]]] = {"gpt": tuple(gpt_rows)}
    for agent_id in ("qwen", "deepseek"):
        source_path = agent_sources[agent_id]
        rows[agent_id] = tuple(load_jsonl_rows(source_path)) if source_path.exists() else ()
    return rows


def _agent_prompt_summary(
    agent_id: AgentId,
    row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    inspected = llm_event_reasoner.inspect_structured_events(row)
    return {
        "agent_id": agent_id,
        "agent_prompt_version": row.get("prompt_version") if row else None,
        "structured_event_input": inspected,
    }


def _agreement_features(agent_inputs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    labels_by_agent: dict[str, str | None] = {}
    for agent_input in agent_inputs:
        agent_id = str(agent_input.get("agent_id") or "")
        structured_input = dict(agent_input.get("structured_event_input") or {})
        original_final = dict(structured_input.get("original_final") or {})
        label = original_final.get("final_label")
        labels_by_agent[agent_id] = str(label) if label is not None else None
    label_counts: Counter[str] = Counter(
        label for label in labels_by_agent.values() if label is not None
    )
    gpt_label = labels_by_agent.get("gpt")
    return {
        "labels_by_agent": labels_by_agent,
        "unique_final_labels": sorted(label_counts),
        "label_counts": dict(sorted(label_counts.items())),
        "exact_unanimous": len(label_counts) == 1 and len(labels_by_agent) == len(AGENT_IDS),
        "exact_majority_label": _majority_label(label_counts),
        "agents_matching_gpt": sorted(
            agent_id
            for agent_id, label in labels_by_agent.items()
            if label is not None and label == gpt_label
        ),
        "peer_disagreement_with_gpt": sorted(
            agent_id
            for agent_id, label in labels_by_agent.items()
            if agent_id != "gpt" and label is not None and label != gpt_label
        ),
    }


def _majority_label(label_counts: Counter[str]) -> str | None:
    if not label_counts:
        return None
    [(label, count), *rest] = label_counts.most_common()
    if count >= 2 and (not rest or rest[0][1] < count):
        return label
    return None


def _adjudicator_hints(
    agent_rows: Mapping[str, Mapping[str, Any] | None],
) -> dict[str, Any]:
    peer_profiles: list[dict[str, Any]] = []
    for peer_id in ("qwen", "deepseek"):
        row = agent_rows.get(peer_id)
        if row is None:
            continue
        profiles: list[str] = []
        if _is_high_precision_recurring_cadence_peer_rescue(
            selected_agent_id=peer_id,
            agent_rows=agent_rows,
        ):
            profiles.append("recurring_cadence_peer_rescue")
        if _is_high_precision_boundary_peer_rescue(
            selected_agent_id=peer_id,
            agent_rows=agent_rows,
        ):
            profiles.append("boundary_peer_rescue")
        if profiles:
            peer_profiles.append(
                {
                    "peer_agent_id": peer_id,
                    "eligible_profiles": profiles,
                    "gpt_final_label": _selection_label(agent_rows.get("gpt")),
                    "peer_final_label": _selection_label(row),
                    "gpt_selected_event_flags": sorted(
                        _selected_event_flags(agent_rows["gpt"])
                        if agent_rows.get("gpt") is not None
                        else ()
                    ),
                    "peer_selected_event_flags": sorted(_selected_event_flags(row)),
                }
            )
    return {
        "high_precision_peer_profiles": peer_profiles,
        "risk_checks": [
            "peer_seizure_free_replacements_are_not_high_precision",
            "gpt_unknown_or_no_reference_to_peer_numeric_is_not_high_precision",
            "cluster_or_multi_semiology_disagreement_requires_keep_gpt_in_this_run",
        ],
    }


def _combined_evidence_contexts(
    note_text: str,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for agent_id in AGENT_IDS:
        for context in llm_event_reasoner._evidence_contexts(
            note_text,
            agent_rows.get(agent_id),
        ):
            event_id = str(context.get("event_id") or "")
            evidence = str(context.get("evidence") or "")
            key = (agent_id, evidence)
            if key in seen:
                continue
            seen.add(key)
            contexts.append({**context, "agent_id": agent_id, "event_id": event_id})
    return contexts


def _filter_decision_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    if "comparison_profile" not in repaired and "boundary_profile" in repaired:
        repaired["comparison_profile"] = repaired["boundary_profile"]
    allowed = set(CrossModelAdjudicatorDecision.model_fields)
    return {key: value for key, value in repaired.items() if key in allowed}


def _repair_decision_shape(payload: Any) -> tuple[Any, list[str]]:
    if not isinstance(payload, dict):
        return payload, []
    repaired = dict(payload)
    notes: list[str] = []
    selected_agent = _normalize_agent_id(repaired.get("selected_agent_id"))
    if selected_agent is not None and repaired.get("selected_agent_id") != selected_agent:
        repaired["selected_agent_id"] = selected_agent
        notes.append("decision_enum_shape_repaired:selected_agent_id")
    action = _normalize_action(repaired.get("action"), selected_agent=selected_agent)
    if action is not None and repaired.get("action") != action:
        repaired["action"] = action
        notes.append("decision_enum_shape_repaired:action")
    if "attribution" not in repaired and selected_agent is not None:
        repaired["attribution"] = (
            "llm_original_structured_event_kept"
            if selected_agent == "gpt"
            else "llm_selected_tool_rendered"
        )
        notes.append("decision_field_defaulted:attribution")
    for field_name in (
        "selected_event_ids",
        "evidence",
        "comparison_profile",
    ):
        value = repaired.get(field_name)
        normalized = llm_event_reasoner._string_tuple(value)
        if normalized != value:
            repaired[field_name] = normalized
            notes.append(f"decision_field_shape_repaired:{field_name}")
    rejected_agent_ids = _agent_id_tuple(repaired.get("rejected_agent_ids"))
    if rejected_agent_ids != repaired.get("rejected_agent_ids"):
        repaired["rejected_agent_ids"] = rejected_agent_ids
        notes.append("decision_field_shape_repaired:rejected_agent_ids")
    for field_name, allowed_values in (
        ("uncertainty", llm_event_reasoner.UNCERTAINTY_VALUES),
        ("attribution", llm_event_reasoner.DECISION_ATTRIBUTION_VALUES),
        ("action", PROMPT_ACTION_VALUES),
        ("selected_agent_id", AGENT_IDS),
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


def _normalize_agent_id(value: Any) -> AgentId | None:
    if isinstance(value, (list, tuple)):
        value = next((item for item in value if item is not None), None)
    if value is None:
        return None
    text = str(value).strip().lower()
    if "deepseek" in text:
        return "deepseek"
    if "qwen" in text:
        return "qwen"
    if "gpt" in text or text in {"primary", "baseline"}:
        return "gpt"
    return None


def _normalize_action(value: Any, *, selected_agent: AgentId | None) -> CrossModelAction | None:
    if isinstance(value, (list, tuple)):
        value = next((item for item in value if item is not None), None)
    if value is None:
        return _action_for_agent(selected_agent)
    text = str(value).strip().lower().replace("-", "_").replace(" ", "_")
    if text in ACTION_TO_AGENT:
        return text  # type: ignore[return-value]
    if "deepseek" in text:
        return "select_deepseek_final"
    if "qwen" in text:
        return "select_qwen_final"
    if "gpt" in text or "keep" in text:
        return "keep_gpt_final"
    return _action_for_agent(selected_agent)


def _action_for_agent(agent_id: AgentId | None) -> CrossModelAction | None:
    if agent_id == "gpt":
        return "keep_gpt_final"
    if agent_id == "qwen":
        return "select_qwen_final"
    if agent_id == "deepseek":
        return "select_deepseek_final"
    return None


def _agent_id_tuple(value: Any) -> tuple[AgentId, ...]:
    if value is None:
        return ()
    raw_items: Sequence[Any]
    if isinstance(value, str):
        raw_items = tuple(
            part.strip()
            for part in value.replace(";", ",").split(",")
            if part.strip()
        )
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        expanded: list[Any] = []
        for item in value:
            if isinstance(item, str) and "," in item:
                expanded.extend(part.strip() for part in item.split(",") if part.strip())
            else:
                expanded.append(item)
        raw_items = tuple(expanded)
    else:
        raw_items = (value,)
    normalized = [
        agent_id
        for agent_id in (_normalize_agent_id(item) for item in raw_items)
        if agent_id is not None
    ]
    return tuple(dict.fromkeys(normalized))


def _common_decision_from_adjudicator(
    decision: CrossModelAdjudicatorDecision,
) -> llm_event_reasoner.ReasonedFrequencyDecision:
    selected_event_ids = tuple(
        f"{decision.selected_agent_id}:{event_id}"
        for event_id in decision.selected_event_ids
    )
    return llm_event_reasoner.ReasonedFrequencyDecision(
        final_label=decision.final_label,
        final_kind=decision.final_kind,
        selected_event_ids=selected_event_ids,
        rejected_event_ids=tuple(decision.rejected_agent_ids),
        evidence=decision.evidence,
        boundary_profile=decision.comparison_profile,
        calculation_trace=decision.calculation_trace,
        clinical_rationale=decision.clinical_rationale,
        uncertainty=decision.uncertainty,
        tool_calls=(),
        attribution=decision.attribution,
    )


def _peer_selection_safety_keep_reason(
    decision: CrossModelAdjudicatorDecision,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
) -> str | None:
    selected_agent_id = decision.selected_agent_id
    if selected_agent_id == "gpt":
        return None
    gpt_row = agent_rows.get("gpt")
    selected_row = agent_rows.get(selected_agent_id)
    if gpt_row is None or selected_row is None:
        return "missing_agent_for_peer_gate"
    gpt_label = _selection_label(gpt_row)
    selected_label = _selection_label(selected_row)
    if _labels_equivalent(gpt_label, selected_label):
        return None
    if _is_high_precision_recurring_cadence_peer_rescue(
        selected_agent_id=selected_agent_id,
        agent_rows=agent_rows,
    ):
        return None
    if _is_high_precision_boundary_peer_rescue(
        selected_agent_id=selected_agent_id,
        agent_rows=agent_rows,
    ):
        return None
    return "peer_selection_not_in_high_precision_gate"


def _is_high_precision_recurring_cadence_peer_rescue(
    *,
    selected_agent_id: AgentId,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
) -> bool:
    gpt_row = agent_rows.get("gpt")
    selected_row = agent_rows.get(selected_agent_id)
    if gpt_row is None or selected_row is None:
        return False
    if _selection_kind(gpt_row) != "frequency" or _selection_kind(selected_row) != "frequency":
        return False
    selected_label = _selection_label(selected_row)
    if not selected_label or not _other_peer_agrees(selected_agent_id, selected_label, agent_rows):
        return False
    gpt_flags = _selected_event_flags(gpt_row)
    selected_flags = _selected_event_flags(selected_row)
    return (
        "broad_elapsed_window_total" in gpt_flags
        and "explicit_recurring_cadence" in selected_flags
    )


def _is_high_precision_boundary_peer_rescue(
    *,
    selected_agent_id: AgentId,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
) -> bool:
    gpt_row = agent_rows.get("gpt")
    selected_row = agent_rows.get(selected_agent_id)
    if gpt_row is None or selected_row is None:
        return False
    if not _looks_numeric_frequency_label(_selection_label(gpt_row)):
        return False
    if _semantic_kind_from_label(_selection_label(selected_row)) not in {
        "unknown",
        "no_reference",
    }:
        return False
    gpt_flags = _selected_event_flags(gpt_row)
    selected_flags = _selected_event_flags(selected_row)
    return bool(
        (gpt_flags | selected_flags)
        & {"last_or_anchored", "vague_or_uncertain_frequency"}
    )


def _other_peer_agrees(
    selected_agent_id: AgentId,
    selected_label: str,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
) -> bool:
    for peer_id in ("qwen", "deepseek"):
        if peer_id == selected_agent_id:
            continue
        peer_row = agent_rows.get(peer_id)
        if peer_row is not None and _labels_equivalent(_selection_label(peer_row), selected_label):
            return True
    return False


def _selection_label(row: Mapping[str, Any] | None) -> str:
    label = _structured_selection(row).get("final_label")
    return str(label) if label is not None else ""


def _selection_kind(row: Mapping[str, Any] | None) -> str:
    kind = _structured_selection(row).get("final_kind")
    return str(kind) if kind is not None else ""


def _selected_event_flags(row: Mapping[str, Any]) -> set[str]:
    selection = _structured_selection(row)
    selected_ids = {
        str(event_id) for event_id in selection.get("selected_event_ids") or ()
    }
    texts: list[str] = [
        str(selection.get("final_label") or ""),
        str(selection.get("evidence") or ""),
        str(selection.get("rationale") or ""),
    ]
    structured_record = dict(row.get("structured_record") or {})
    for event in structured_record.get("events") or []:
        if not isinstance(event, Mapping):
            continue
        if str(event.get("event_id") or "") in selected_ids:
            texts.extend(
                str(event.get(key) or "")
                for key in (
                    "kind",
                    "raw_value",
                    "temporality",
                    "time_window",
                    "evidence",
                    "notes",
                )
            )
    return _marker_flags(" ".join(texts))


def _marker_flags(text: str) -> set[str]:
    lowered = text.lower()
    flags: set[str] = set()
    if _has_any(
        lowered,
        "ago",
        "last event",
        "last seizure",
        "most recent",
        "latest",
        "fortnight",
        "last month",
        "first such occurrence",
        "not captured",
    ):
        flags.add("last_or_anchored")
    if _has_any(lowered, "minute", "minutes", "second", "seconds", "lasting"):
        flags.add("duration_or_episode_length")
    if _has_any(
        lowered,
        "infrequent",
        "unclear",
        "possibly",
        "vague",
        "approximate",
        "clustering around",
    ):
        flags.add("vague_or_uncertain_frequency")
    if _has_any(
        lowered,
        "so far this year",
        "year to date",
        "year-to-date",
        "this year",
        "annual count",
    ):
        flags.add("broad_elapsed_window_total")
    if _has_any(
        lowered,
        "typical pattern",
        "monthly",
        "weekly",
        "daily",
        "every ",
        "per month",
        "per week",
        "per day",
    ):
        flags.add("explicit_recurring_cadence")
    return flags


def _semantic_kind_from_label(label: str) -> str:
    lowered = label.lower()
    if lowered == "unknown":
        return "unknown"
    if lowered == "no seizure frequency reference":
        return "no_reference"
    if lowered.startswith("seizure free"):
        return "seizure_free"
    return "frequency"


def _looks_numeric_frequency_label(label: str) -> bool:
    lowered = label.lower()
    return " per " in lowered and any(ch.isdigit() for ch in lowered)


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


def _has_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def _fallback_parse_result(
    *,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    note_text: str,
    reason: str,
    parse_errors: Sequence[str] = (),
) -> ParsedCrossModelDecision:
    rendered, render_events, render_error = _render_agent_final(
        "gpt",
        raw_decision=None,
        agent_rows=agent_rows,
        note_text=note_text,
    )
    errors = [*parse_errors, f"action_render_error:{reason}"]
    events = [f"action_render_fallback_kept_gpt:{reason}", *render_events]
    if render_error:
        errors.append(f"action_render_error:{render_error}")
    return ParsedCrossModelDecision(
        raw_decision=None,
        raw_common_decision=None,
        format_only_decision=None,
        final_decision=rendered,
        parse_errors=errors,
        action_render_events=events,
    )


def _render_agent_final(
    agent_id: AgentId,
    *,
    raw_decision: CrossModelAdjudicatorDecision | None,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    note_text: str,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, list[str], str | None]:
    row = agent_rows.get(agent_id)
    if row is None:
        return None, [], f"missing_selected_agent:{agent_id}"
    selection = _structured_selection(row)
    final_label = selection.get("final_label")
    if final_label is None:
        return None, [], f"missing_selected_agent_final:{agent_id}"
    final_kind = _safe_final_kind(selection.get("final_kind"), str(final_label))
    repair_trace = repair_prediction_label_format_preserving_with_trace(str(final_label))
    rendered_label = repair_trace.final_label
    render_events = [f"rendered_selected_agent_final:{agent_id}"]
    if rendered_label != final_label:
        render_events.append(
            f"selected_agent_final_label_format_repaired:{final_label!r}->{rendered_label!r}"
        )
    if raw_decision is not None:
        copied_label = raw_decision.final_label
        try:
            copied_label = label_to_frequency_record(copied_label).normalized_label
        except ValueError:
            pass
        if copied_label != rendered_label:
            render_events.append(
                "selected_agent_label_mismatch:"
                f"{raw_decision.selected_agent_id}:{raw_decision.final_label!r}"
                f"!={rendered_label!r}"
            )
    selected_event_ids = tuple(
        f"{agent_id}:{event_id}"
        for event_id in selection.get("selected_event_ids") or ()
    )
    evidence = _best_evidence(note_text, row, raw_decision)
    attribution = (
        "llm_original_structured_event_kept"
        if agent_id == "gpt"
        else "llm_selected_tool_rendered"
    )
    if rendered_label != final_label:
        attribution = "llm_selected_format_repaired"
    return (
        llm_event_reasoner.ReasonedFrequencyDecision(
            final_label=rendered_label,
            final_kind=final_kind,
            selected_event_ids=selected_event_ids,
            rejected_event_ids=tuple(raw_decision.rejected_agent_ids)
            if raw_decision
            else (),
            evidence=evidence,
            boundary_profile=raw_decision.comparison_profile if raw_decision else (),
            calculation_trace=raw_decision.calculation_trace if raw_decision else None,
            clinical_rationale=_rendered_rationale(agent_id, selection, raw_decision),
            uncertainty=raw_decision.uncertainty if raw_decision else "high",
            tool_calls=(),
            attribution=attribution,
        ),
        render_events,
        None,
    )


def _structured_selection(row: Mapping[str, Any] | None) -> dict[str, Any]:
    if row is None:
        return {}
    return dict(dict(row.get("structured_record") or {}).get("selection") or {})


def _safe_final_kind(value: Any, final_label: str) -> llm_event_reasoner.DecisionKind:
    text = str(value or "")
    if text in DECISION_KIND_VALUES:
        return text  # type: ignore[return-value]
    lowered = final_label.lower()
    if lowered == "unknown":
        return "unknown"
    if lowered == "no seizure frequency reference":
        return "no_reference"
    if lowered.startswith("seizure free"):
        return "seizure_free"
    if lowered == "multiple":
        return "unresolved_multiple"
    return "frequency"


def _best_evidence(
    note_text: str,
    row: Mapping[str, Any],
    raw_decision: CrossModelAdjudicatorDecision | None,
) -> tuple[str, ...]:
    candidates: list[str] = []
    selection = _structured_selection(row)
    _append_evidence(candidates, selection.get("evidence"))
    selected_ids = {
        str(event_id) for event_id in selection.get("selected_event_ids") or ()
    }
    structured_record = dict(row.get("structured_record") or {})
    for event in structured_record.get("events") or []:
        if not isinstance(event, Mapping):
            continue
        if str(event.get("event_id") or "") in selected_ids:
            _append_evidence(candidates, event.get("evidence"))
    if raw_decision is not None:
        _append_evidence(candidates, raw_decision.evidence)
    exact = [
        evidence
        for evidence in dict.fromkeys(candidates)
        if evidence_is_substring(note_text, evidence)
    ]
    if exact:
        return tuple(exact)
    return tuple(dict.fromkeys(candidates[:1]))


def _append_evidence(target: list[str], value: Any) -> None:
    if value is None:
        return
    if isinstance(value, str):
        if value:
            target.append(value)
        return
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for item in value:
            if isinstance(item, str) and item:
                target.append(item)


def _rendered_rationale(
    agent_id: AgentId,
    selection: Mapping[str, Any],
    raw_decision: CrossModelAdjudicatorDecision | None,
) -> str:
    if raw_decision is not None:
        return raw_decision.clinical_rationale
    rationale = selection.get("rationale")
    if isinstance(rationale, str) and rationale:
        return f"Fallback kept {agent_id} structured-event final: {rationale}"
    return f"Fallback kept {agent_id} structured-event final."


def _agent_reference(row: Mapping[str, Any] | None) -> dict[str, Any]:
    if row is None:
        return {
            "final_label": None,
            "final_kind": None,
            "selected_event_ids": [],
            "comparison": {},
            "evidence_valid": None,
        }
    return llm_event_reasoner._v0_reference(row)


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    summary = summarize_rows(rows)
    print(
        json.dumps(
            {
                "pipeline": PIPELINE_FAMILY,
                "completed": len(rows),
                "total": total,
                "final_purist_correct": summary.get("final_purist_correct"),
                "net_purist_gain_vs_v0": summary.get("net_purist_gain_vs_v0"),
            },
            sort_keys=True,
        )
    )
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None:
        checkpoint_metadata = dict(metadata)
        checkpoint_metadata["summary"] = summary
        checkpoint_metadata["gate"] = llm_event_reasoner.gate_interpretation(summary)
        write_report(rows, checkpoint_metadata, report_path, jsonl_path=jsonl_path or Path(""))
