"""Fresh-evidence reasoner over saved Gan structured-event agents.

This V12 candidate is broader than a saved-output selector but narrower than a
free direct labeler. The model may keep the GPT structured-event final answer or
replace it with a newly reasoned final label from exact raw-note evidence after
reviewing GPT, Qwen, and DeepSeek structured-event traces. Deterministic code
only validates JSON, performs format-only label repair, validates cited evidence
as source substrings, renders keep/fallback actions from the original GPT
structured-event final, and scores after the decision.
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
    cross_model_structured_event_adjudicator as cross_model_base,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    event_completion_reasoner,
    family_transitions,
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

PROMPT_VERSION = "gan2026_fresh_evidence_reasoner_v0_4"
SAFETY_GATE_VERSION = "gan2026_fresh_evidence_safety_gate_v0_3"
PIPELINE_FAMILY = "fresh_evidence_reasoner"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = llm_event_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH = (
    cross_model_base.DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH
)
DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH = (
    cross_model_base.DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH
)
TEST_GPT_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_test450_phase4_frozen_audit_hybrid_structured_events_"
    "gpt41mini_2026-06-09.jsonl"
)
TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_agentic_structured_event_patch_recent_unresolved_burden_"
    "test450_qwen3635b_2026-06-13.jsonl"
)
TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/gan2026_missing_deepseek_test450_structured_events.jsonl"
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_fresh_evidence_reasoner_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_fresh_evidence_reasoner_validation.md")

FreshEvidenceAction = Literal[
    "keep_original_structured_event_final",
    "replace_with_fresh_evidence_final",
]
FRESH_EVIDENCE_ACTION_VALUES = (
    "keep_original_structured_event_final",
    "replace_with_fresh_evidence_final",
)


class FreshEvidenceDecision(BaseModel):
    """Prediction schema for V12 fresh-evidence replacement."""

    model_config = ConfigDict(extra="forbid")

    action: FreshEvidenceAction
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


class ParsedFreshEvidenceDecision(BaseModel):
    """Raw, format-only, and evidence-gated views of one V12 output."""

    model_config = ConfigDict(extra="forbid")

    raw_fresh_decision: FreshEvidenceDecision | None
    raw_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
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
    """Run or prompt-smoke the fresh-evidence reasoner."""

    del escalation_reason, candidate_set_jsonl_path
    source_path = _gpt_structured_event_source_path(
        split,
        structured_event_source_path
        or structured_event_jsonl_path
        or DEFAULT_STRUCTURED_EVENT_JSONL_PATH,
    )
    agent_sources = _structured_event_source_paths_for_split(split, source_path)
    if structured_event_rows is None:
        structured_event_rows = load_jsonl_rows(source_path)
    loaded_agent_rows = cross_model_base._load_agent_rows(
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
            "artifact_kind": "gan2026_fresh_evidence_reasoner_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": f"{PROMPT_VERSION}+{SAFETY_GATE_VERSION}",
            "safety_gate_version": SAFETY_GATE_VERSION,
            "agent_source_paths": {
                agent_id: str(path) for agent_id, path in agent_sources.items()
            },
            "structured_event_source_role": (
                "GPT, Qwen, and DeepSeek saved LLM structured-event traces are "
                "evidence scaffolds. The prediction-bearing replacement, when "
                "made, is a fresh model-owned interpretation from exact raw-note "
                "evidence. Deterministic top labels are not shown or used."
            ),
            "claim_boundary": _claim_boundary_for_split(split),
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
                    for agent_id in cross_model_base.AGENT_IDS
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

    metadata["summary"] = summarize_rows(rows, split=split)
    if split != "test":
        # Per-family breakdown is a validation-only instrument; the holdout
        # protocol is aggregate-only, so it is not attached for `test`.
        metadata["summary_by_family"] = (
            family_transitions.summarize_transitions_by_family(
                rows, **family_transitions.FRESH_EVIDENCE_PATHS
            )
        )
    metadata["gate"] = llm_event_reasoner.gate_interpretation(metadata["summary"])
    return rows, metadata


def _gpt_structured_event_source_path(
    split: str,
    requested_path: Path,
) -> Path:
    if split == "test" and requested_path == DEFAULT_STRUCTURED_EVENT_JSONL_PATH:
        return TEST_GPT_STRUCTURED_EVENT_JSONL_PATH
    return requested_path


def _structured_event_source_paths_for_split(
    split: str,
    gpt_source_path: Path,
) -> dict[str, Path]:
    if split == "test":
        return {
            "gpt": gpt_source_path,
            "qwen": TEST_QWEN_STRUCTURED_EVENT_JSONL_PATH,
            "deepseek": TEST_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH,
        }
    return {
        "gpt": gpt_source_path,
        "qwen": DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH,
        "deepseek": DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH,
    }


def build_prompt_input(
    record: GanFrequencyRecord,
    agent_rows: Mapping[str, Mapping[str, Any] | None],
    *,
    note_excerpt_chars: int = 7000,
) -> str:
    """Build a split-neutral fresh-evidence payload."""

    agent_inputs = [
        cross_model_base._agent_prompt_summary(agent_id, agent_rows.get(agent_id))
        for agent_id in cross_model_base.AGENT_IDS
    ]
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 fresh-evidence seizure-frequency reasoning",
        "variant": "V12_fresh_evidence_reasoner",
        "instructions": [
            (
                "Decide whether to keep the GPT structured-event final answer or "
                "replace it with one freshly reasoned Gan label from exact raw-note evidence."
            ),
            (
                "Use the three saved LLM structured-event traces as scaffolding, not "
                "as a vote. If a peer trace seems right, cite the raw evidence and "
                "produce the replacement yourself."
            ),
            (
                "Use keep_original_structured_event_final unless exact raw-note "
                "evidence proves a better current seizure-frequency interpretation."
            ),
            (
                "Replacement is for represented-evidence or clinical-selection misses: "
                "current/recent frequency, denominator/window, cluster burden, "
                "seizure-free conflict, unknown/no-reference boundary, or highest "
                "active semiology."
            ),
            (
                "Do not use outside final-answer sources, row IDs, split membership, "
                "gold labels, scoring metadata, deterministic rules, deterministic "
                "top labels, or benchmark feedback."
            ),
            (
                "For frequency labels, state the numerator, denominator, and window "
                "in calculation_trace. Do not turn one-off since-last-review counts "
                "into rates unless the interval length or recurring cadence is explicit."
            ),
            (
                "Do not replace explicit numeric or range frequency evidence such as "
                "'twice per week' with 'multiple per week'; render the numeric/range "
                "frequency or keep the original structured-event final."
            ),
            (
                "For unknown, require evidence that seizure-frequency information "
                "exists but cannot be converted to a current recurring rate."
            ),
            (
                "For no_reference, require positive absence of seizure-frequency "
                "evidence; do not use it when awkward but usable frequency evidence exists."
            ),
            (
                "For seizure_free, require exact no-events-since or absence-duration "
                "evidence and no conflicting current/recent frequency evidence."
            ),
            (
                "Do not replace an original seizure-free structured-event final with "
                "unknown or no_reference merely because the note discusses non-epileptic "
                "spells, medication status, or qualitative improvement."
            ),
            (
                "Do not output bare 'seizure free'. If the duration is not explicit "
                "enough to render a Gan seizure-free label with a duration, keep the "
                "original structured-event final."
            ),
            (
                "Do not replace a frequency original with seizure_free for only "
                "days, weeks, or about one month after a recent last event; keep the "
                "frequency original on that short last-event-only boundary."
            ),
            (
                "For clusters, keep cluster cadence separate from events per cluster; "
                "only multiply or render cluster labels when both axes are supported."
            ),
            (
                "For multiple active semiologies, select the highest current clinically "
                "active burden, not the first-mentioned or most severe seizure type."
            ),
            "Evidence entries must be exact substrings copied from the note.",
            (
                "final_label must be a valid Gan label only: unknown, no seizure "
                "frequency reference, seizure free, multiple per day/week/month/year, "
                "or '<number> [to <number>] per day/week/month/year'."
            ),
            (
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(FRESH_EVIDENCE_ACTION_VALUES),
            "final_label": "Gan-style label string",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": (
                "saved event IDs or fresh_evidence_1 when replacement comes from raw text"
            ),
            "rejected_event_ids": "saved event IDs or agent finals explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the final choice",
            "boundary_profile": "list of targeted profile keys driving the choice",
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief clinical rationale",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list for this V12 scaffold",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "saved_structured_event_agents": agent_inputs,
        "raw_note_excerpt": record.note_text[:note_excerpt_chars],
        "excerpt_truncated": len(record.note_text) > note_excerpt_chars,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_fresh_evidence_decision_json(
    raw_output: str,
    *,
    note_text: str,
    structured_event_row: Mapping[str, Any] | None,
) -> ParsedFreshEvidenceDecision:
    """Parse a fresh-evidence decision and apply the evidence gate."""

    parse_errors: list[str] = []
    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
            llm_event_reasoner._extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return ParsedFreshEvidenceDecision(
            raw_fresh_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=[f"invalid_json: {exc.msg}"],
        )
    parse_errors.extend(dialect_notes)
    payload, shape_notes = _repair_fresh_shape(repair_decision_payload(raw_payload))
    payload = _filter_fresh_payload(payload)
    parse_errors.extend(shape_notes)
    try:
        raw_fresh = FreshEvidenceDecision.model_validate(payload)
    except ValidationError as exc:
        return ParsedFreshEvidenceDecision(
            raw_fresh_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=[
                *parse_errors,
                f"schema_validation_error: {exc.errors()[0]['msg']}",
            ],
        )

    raw_common = _common_decision_from_fresh(raw_fresh)
    format_decision, repair_events, format_notes = _format_only_decision(raw_common)
    parse_errors.extend(format_notes)
    final_decision, action_events, action_notes = _render_fresh_action(
        raw_fresh,
        format_decision,
        note_text=note_text,
        structured_event_row=structured_event_row,
    )
    parse_errors.extend(action_notes)
    return ParsedFreshEvidenceDecision(
        raw_fresh_decision=raw_fresh,
        raw_decision=raw_common,
        format_only_decision=format_decision,
        final_decision=final_decision,
        parse_errors=parse_errors,
        format_repair_events=repair_events,
        action_render_events=action_events,
    )


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    split: str | None = None,
) -> dict[str, Any]:
    """Summarize V12 rows across raw, format-only, final, and V0 layers."""

    summary = llm_event_reasoner.summarize_rows(rows)
    summary["fresh_evidence_replace_actions"] = 0
    summary["fresh_evidence_gate_fallbacks"] = 0
    profiles: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    for row in rows:
        decision = dict(row.get("fresh_evidence_decision_record") or {})
        action = str(decision.get("action") or "")
        if action:
            actions[action] += 1
        if action == "replace_with_fresh_evidence_final":
            summary["fresh_evidence_replace_actions"] += 1
        if any(
            str(event).startswith("fresh_evidence_gate_fallback:")
            for event in row.get("action_render_events") or []
        ):
            summary["fresh_evidence_gate_fallbacks"] += 1
        for profile in decision.get("boundary_profile") or []:
            profiles[str(profile)] += 1
    summary["fresh_evidence_actions"] = dict(sorted(actions.items()))
    summary["fresh_evidence_profiles"] = dict(sorted(profiles.items()))
    if split == "test":
        _redact_holdout_summary(summary)
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
    split = str(metadata.get("split") or "validation")
    split_manifest = str(metadata.get("split_manifest") or "gan2026_split_v1")
    is_test_split = split == "test"
    artifact_kind = (
        "This is a frozen aggregate-only V12 fresh-evidence holdout audit artifact."
        if is_test_split
        else "This is a validation-development V12 fresh-evidence reasoning artifact."
    )
    lines = [
        "# Gan 2026 Fresh-Evidence Reasoner",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        artifact_kind,
        "The model may replace the GPT structured-event final only from exact raw-note evidence.",
        "",
        "## Experiment Unit",
        "",
        "- Work class: V12 fresh-evidence reasoner over saved structured events.",
        f"- Rows: {summary.get('rows', 0)}",
        f"- Split: `{split}`, manifest `{split_manifest}`.",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- JSONL artifact: `{jsonl_path}`",
        "",
        "## Summary",
        "",
        f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
        f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
        f"- Fresh-evidence replace actions: {summary.get('fresh_evidence_replace_actions', 0)}",
        f"- Evidence-gate fallbacks: {summary.get('fresh_evidence_gate_fallbacks', 0)}",
        f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
        (
            f"- V0 Purist: {summary.get('v0_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- V0 Pragmatic: {summary.get('v0_pragmatic_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Raw model Purist: {summary.get('raw_model_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Raw model Pragmatic: {summary.get('raw_model_pragmatic_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Format-only Purist: {summary.get('format_only_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            "- Format-only Pragmatic: "
            f"{summary.get('format_only_pragmatic_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Final Purist: {summary.get('final_purist_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        (
            f"- Final Pragmatic: {summary.get('final_pragmatic_correct', 0)}/"
            f"{summary.get('rows', 0)}"
        ),
        f"- Net Purist gain vs V0: {summary.get('net_purist_gain_vs_v0', 0)}",
        (
            "- Changed-label precision vs V0: "
            f"{summary.get('changed_label_precision_vs_v0')}"
        ),
        f"- Actions: `{summary.get('fresh_evidence_actions', {})}`",
        (
            "- Profiles: omitted from the test report to keep the first readout "
            "aggregate-only."
            if is_test_split
            else f"- Profiles: `{summary.get('fresh_evidence_profiles', {})}`"
        ),
        "",
        "## Gate",
        "",
        f"- Status: `{gate.get('status')}`",
        f"- Interpretation: {gate.get('interpretation')}",
        "",
        "## Claim Boundary",
        "",
        str(metadata.get("claim_boundary", "")),
    ]
    if is_test_split:
        lines.extend(
            [
                "",
                "## Aggregate-Only Holdout Readout",
                "",
                (
                    "Row-level test details are intentionally omitted from this Markdown "
                    "report. Do not inspect the JSONL or row-level failures before "
                    "starting a separately authorized validation-only follow-up cycle."
                ),
            ]
        )
        write_markdown_report(path, lines)
        return

    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Action | Profiles | V0 | Raw | Final | Transition | Evidence exact | Notes |",
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        layers = dict(row.get("score_layers") or {})
        fresh_record = dict(row.get("fresh_evidence_decision_record") or {})
        notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
        render_events = "; ".join(
            str(event) for event in row.get("action_render_events") or []
        )
        if render_events:
            notes = f"{notes}; {render_events}" if notes else render_events
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        lines.append(
            f"| {row.get('source_row_index')} | "
            f"`{fresh_record.get('action')}` | "
            f"`{fresh_record.get('boundary_profile')}` | "
            f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
            f"`{dict(layers.get('raw_model') or {}).get('final_label')}` | "
            f"`{dict(layers.get('final') or {}).get('final_label')}` | "
            f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
            f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


def _claim_boundary_for_split(split: str) -> str:
    if split == "test":
        return (
            "frozen aggregate-only V12 test450 audit; first readout is aggregate "
            "Purist/Pragmatic and health metrics only; no row-level test inspection, "
            "post-test tuning, or benchmark-comparable claim without separate review"
        )
    return (
        "validation-development V12 fresh-evidence reasoner; no holdout use, "
        "no row-level test inspection, and no benchmark claim"
    )


def _redact_holdout_summary(summary: dict[str, Any]) -> None:
    """Keep locked-test stdout/report summaries inside the first-readout policy."""

    omitted_fields = []
    for field_name in ("final_labels", "fresh_evidence_profiles"):
        if field_name in summary:
            summary.pop(field_name)
            omitted_fields.append(field_name)
    if omitted_fields:
        summary["aggregate_only_omitted_fields"] = sorted(omitted_fields)


class FreshEvidenceSignature(dspy.Signature):
    """Reason from raw evidence and emit one keep-or-replace JSON decision."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with saved structured-event traces and a raw-note excerpt."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching FreshEvidenceDecision."
    )


class DspyFreshEvidenceCaller(dspy.Module):
    """DSPy caller for the V12 fresh-evidence reasoner."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(FreshEvidenceSignature)

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
    gpt_row = agent_rows.get("gpt")
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
        parse_fresh_evidence_decision_json(
            raw_output,
            note_text=record.note_text,
            structured_event_row=gpt_row,
        )
        if raw_output
        else ParsedFreshEvidenceDecision(
            raw_fresh_decision=None,
            raw_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=["not_run"],
        )
    )
    final_decision = parsed.final_decision
    v0_reference = llm_event_reasoner._v0_reference(gpt_row)
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
        "structured_event_input_available": gpt_row is not None,
        "agent_input_available": {
            agent_id: agent_rows.get(agent_id) is not None
            for agent_id in cross_model_base.AGENT_IDS
        },
        "v0_reference": v0_reference,
        "hidden_families": list(
            family_transitions.tag_hidden_families(
                note_text=record.note_text,
                gold_label=record.gold_label,
                baseline_label=dict(v0_reference.get("comparison") or {}).get(
                    "final_label"
                ),
            )
        ),
        "model_call_attempted": model_call_attempted,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "call_error": call_error,
        "parse_errors": parsed.parse_errors,
        "format_repair_events": parsed.format_repair_events,
        "action_render_events": parsed.action_render_events,
        "fresh_evidence_decision_record": (
            parsed.raw_fresh_decision.model_dump(mode="json")
            if parsed.raw_fresh_decision
            else None
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
        "trace_warnings": (
            ["prompt_only_no_prediction"] if mode == "prompt-only" else []
        )
        + (["missing_structured_event_row"] if gpt_row is None else []),
    }


def _run_model_call(
    prompt_input_json: str,
    *,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    del model, temperature, max_tokens
    prediction = DspyFreshEvidenceCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


def _filter_fresh_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    allowed = set(FreshEvidenceDecision.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def _repair_fresh_shape(payload: Any) -> tuple[Any, list[str]]:
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
        normalized = event_completion_reasoner._string_tuple(value)
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
        ("action", FRESH_EVIDENCE_ACTION_VALUES),
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
    return repaired, notes


def _common_decision_from_fresh(
    decision: FreshEvidenceDecision,
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
    repair_trace = repair_prediction_label_format_preserving_with_trace(
        raw_decision.final_label
    )
    repair_events = [
        llm_event_reasoner._repair_event_to_dict(event)
        for event in repair_trace.events
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


def _render_fresh_action(
    raw_fresh: FreshEvidenceDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    *,
    note_text: str,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, list[str], list[str]]:
    if raw_fresh.action == "keep_original_structured_event_final":
        decision, error = event_completion_reasoner._render_keep_original_action(
            format_decision,
            structured_event_row,
        )
        if error:
            return None, [], [error]
        return (
            decision,
            ["fresh_evidence_action_rendered:keep_original_structured_event_final"],
            [],
        )

    original_reference = llm_event_reasoner._v0_reference(structured_event_row)
    safety_reason = _fresh_evidence_safety_gate_reason(
        raw_fresh,
        format_decision,
        original_reference=original_reference,
    )
    if safety_reason is not None:
        return _fallback_to_original(
            format_decision,
            structured_event_row,
            safety_reason,
        )

    render_notes: list[str] = []
    try:
        label_to_frequency_record(format_decision.final_label)
    except ValueError as exc:
        return _fallback_to_original(
            format_decision,
            structured_event_row,
            f"fresh_evidence_gate_fallback: unscorable_fresh_label: {exc}",
        )
    exact_evidence = tuple(
        evidence
        for evidence in format_decision.evidence
        if evidence_is_substring(note_text, evidence)
    )
    if not exact_evidence:
        return _fallback_to_original(
            format_decision,
            structured_event_row,
            "fresh_evidence_gate_fallback: evidence_not_exact",
        )
    if exact_evidence != format_decision.evidence:
        format_decision = format_decision.model_copy(
            update={"evidence": exact_evidence}
        )
        render_notes.append("fresh_evidence_shape_repaired:filtered_non_exact_evidence")
    if not format_decision.selected_event_ids:
        format_decision = format_decision.model_copy(
            update={"selected_event_ids": ("fresh_evidence_1",)}
        )
        render_notes.append("fresh_evidence_shape_repaired:selected_event_ids")
    return (
        format_decision,
        [
            *render_notes,
            "fresh_evidence_action_rendered:replace_with_fresh_evidence_final",
        ],
        [],
    )


def _fallback_to_original(
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    structured_event_row: Mapping[str, Any] | None,
    reason: str,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, list[str], list[str]]:
    decision, error = event_completion_reasoner._render_keep_original_action(
        format_decision,
        structured_event_row,
    )
    if error:
        return None, [], [error]
    return (
        decision,
        [reason, "fresh_evidence_action_rendered:fallback_original_structured_event_final"],
        [reason],
    )


def _fresh_evidence_safety_gate_reason(
    raw_fresh: FreshEvidenceDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    *,
    original_reference: Mapping[str, Any],
) -> str | None:
    raw_label = raw_fresh.final_label.strip().lower()
    if raw_fresh.final_kind == "seizure_free" and raw_label == "seizure free":
        return "fresh_evidence_gate_fallback: bare_seizure_free_replacement"

    original_kind = str(original_reference.get("final_kind") or "")
    original_label = str(original_reference.get("final_label") or "")
    original_is_seizure_free = (
        original_kind == "seizure_free"
        or original_label.strip().lower().startswith("seizure free")
    )
    replacement_is_boundary_state = format_decision.final_kind in {
        "unknown",
        "no_reference",
    }
    if original_is_seizure_free and replacement_is_boundary_state:
        return (
            "fresh_evidence_gate_fallback: "
            "original_seizure_free_to_unknown_or_no_reference"
        )
    if raw_fresh.final_kind == "seizure_free" and original_kind == "frequency":
        decision_text = " ".join(
            (
                raw_label,
                raw_fresh.calculation_trace or "",
                raw_fresh.clinical_rationale,
                " ".join(raw_fresh.evidence),
            )
        ).lower()
        short_last_event_boundary = (
            "week" in decision_text
            or "for 1 month" in decision_text
            or "for one month" in decision_text
        )
        if short_last_event_boundary:
            return (
                "fresh_evidence_gate_fallback: "
                "short_seizure_free_replacement_from_frequency_original"
            )
    if format_decision.final_label.strip().lower().startswith("multiple per"):
        decision_text = " ".join(
            (
                raw_label,
                raw_fresh.calculation_trace or "",
                raw_fresh.clinical_rationale,
                " ".join(raw_fresh.evidence),
            )
        ).lower()
        explicit_numeric_boundary = (
            "twice per" in decision_text
            or "<=2 per" in decision_text
            or "<= 2 per" in decision_text
            or "≤2 per" in decision_text
            or "≤ 2 per" in decision_text
        )
        if explicit_numeric_boundary:
            return (
                "fresh_evidence_gate_fallback: "
                "multiple_label_for_explicit_numeric_frequency"
            )
    return None


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    checkpoint_metadata = dict(metadata)
    checkpoint_metadata["summary"] = summarize_rows(
        rows,
        split=str(metadata.get("split") or ""),
    )
    checkpoint_metadata["progress"] = {"completed_rows": len(rows), "total_rows": total}
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None:
        write_report(rows, checkpoint_metadata, report_path, jsonl_path=jsonl_path or Path(""))
