"""Verifier-first correction pass over saved Gan 2026 structured events.

This is the V4 scaffold from the test-0.85 plan. The model owns an explicit
verifier action. Deterministic code only renders that model-owned action against
the saved LLM structured-event artifact, performs format-only label repair where
needed, validates exact evidence substrings, and scores after the model answer.

Migrated to :mod:`stage_protocol` (prompt builder + decision schema + postprocess
policy + thin ``run_split``).
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, cast

import dspy
from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    llm_event_reasoner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.stage_protocol import (
    AgenticStage,
    ParsedStageResponse,
    build_markdown_report_skeleton,
    build_stage_metadata,
    configure_dspy_for_stage,
    has_blocking_parse_issue,
    parse_response,
    write_stage_jsonl,
    write_stage_markdown_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving_with_trace,
)

PROMPT_VERSION = "gan2026_structured_event_verifier_v0_5"
PIPELINE_FAMILY = "structured_event_verifier"
DEFAULT_STRUCTURED_EVENT_JSONL_PATH = llm_event_reasoner.DEFAULT_STRUCTURED_EVENT_JSONL_PATH
DEFAULT_JSONL_PATH = Path("experiments/gan2026_structured_event_verifier_validation.jsonl")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_structured_event_verifier_validation.md")

VerifierAction = Literal[
    "keep_original_structured_event_final",
    "replace_with_existing_event",
    "replace_with_recomputed_fact_from_selected_evidence",
    "abstain_unrenderable",
]
VERIFIER_ACTION_VALUES = (
    "keep_original_structured_event_final",
    "replace_with_existing_event",
    "replace_with_recomputed_fact_from_selected_evidence",
    "abstain_unrenderable",
)
PROMPT_ACTION_VALUES = (
    "keep_original_structured_event_final",
    "replace_with_existing_event",
)


class StructuredEventVerifierDecision(BaseModel):
    """Verifier action plus model rationale for one structured-event row."""

    model_config = ConfigDict(extra="forbid")

    action: VerifierAction
    final_label: str
    final_kind: llm_event_reasoner.DecisionKind
    selected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    rejected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    contradiction_profile: tuple[str, ...] = Field(default_factory=tuple)
    calculation_trace: str | None = None
    clinical_rationale: str
    uncertainty: llm_event_reasoner.Uncertainty
    tool_calls: tuple[llm_event_reasoner.ToolTrace, ...] = Field(default_factory=tuple)
    attribution: llm_event_reasoner.DecisionAttribution


class ParsedVerifierDecision(BaseModel):
    """Raw, format-only, and action-rendered views of one verifier output."""

    model_config = ConfigDict(extra="forbid")

    raw_verifier_decision: StructuredEventVerifierDecision | None
    raw_common_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    format_only_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    final_decision: llm_event_reasoner.ReasonedFrequencyDecision | None
    parse_errors: list[str] = Field(default_factory=list)
    format_repair_events: list[dict[str, Any]] = Field(default_factory=list)
    action_render_events: list[str] = Field(default_factory=list)


class StructuredEventVerifierStage(AgenticStage[StructuredEventVerifierDecision]):
    """V4 verifier prompt builder + raw decision parse policy."""

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_prompt_input(
        self,
        record: GanFrequencyRecord,
        *,
        structured_event_row: Mapping[str, Any] | None = None,
        **_: object,
    ) -> str:
        return _build_verifier_prompt_input(record, structured_event_row)

    def parse_response(
        self,
        raw_output: str,
        **_: object,
    ) -> ParsedStageResponse[StructuredEventVerifierDecision]:
        return parse_response(
            raw_output,
            decision_model=StructuredEventVerifierDecision,
            payload_filter=_filter_verifier_payload,
            shape_repair=_repair_verifier_decision_shape,
            label_repair="none",
            require_scorable_label=False,
        )


STAGE = StructuredEventVerifierStage()


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
    """Run or prompt-smoke a verifier over saved pure structured-event rows."""

    del escalation_reason, candidate_set_jsonl_path
    source_path = (
        structured_event_source_path
        or structured_event_jsonl_path
        or DEFAULT_STRUCTURED_EVENT_JSONL_PATH
    )
    if structured_event_rows is None:
        structured_event_rows = load_jsonl_rows(source_path)
    if mode == "live":
        configure_dspy_for_stage(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=dspy_cache,
            api_base=api_base,
        )

    structured_rows_by_index = llm_event_reasoner._rows_by_source_index(structured_event_rows)
    metadata = build_stage_metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        prompt_version=PROMPT_VERSION,
        dspy_cache=dspy_cache,
        api_base=api_base,
        extra={
            "artifact_kind": "gan2026_structured_event_verifier_trace",
            "pipeline_family": PIPELINE_FAMILY,
            "pipeline_version": PROMPT_VERSION,
            "structured_event_source_path": str(source_path),
            "structured_event_source_role": (
                "pure structured-event V0 comparator and verifier substrate; "
                "the verifier action owns any rendered final label"
            ),
            "claim_boundary": (
                "validation-development V4 verifier scaffold; no holdout use, "
                "no row-level test inspection, and no benchmark claim"
            ),
        },
    )

    rows: list[dict[str, Any]] = []
    for record in records:
        rows.append(
            _build_row(
                record,
                structured_event_row=structured_rows_by_index.get(record.source_row_index),
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
    metadata["gate"] = gate_interpretation(metadata["summary"])
    return rows, metadata


def build_prompt_input(
    record: GanFrequencyRecord,
    structured_event_row: Mapping[str, Any] | None,
) -> str:
    """Build a model-facing verifier payload without IDs, gold, split, or rules top."""

    return STAGE.build_prompt_input(record, structured_event_row=structured_event_row)


def _build_verifier_prompt_input(
    record: GanFrequencyRecord,
    structured_event_row: Mapping[str, Any] | None,
) -> str:
    """Build a model-facing verifier payload without IDs, gold, split, or rules top."""

    structured_input = llm_event_reasoner.inspect_structured_events(structured_event_row)
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 structured-event final-answer verification",
        "variant": "V4_verifier_first_structured_event_correction",
        "instructions": [
            "Verify the original structured-event final answer and choose exactly one action.",
            (
                "The original structured-event final answer is an LLM answer you may "
                "keep; treating it as correct requires the action "
                "keep_original_structured_event_final."
            ),
            (
                "Only override original_final when event evidence proves a boundary, "
                "burden, temporality, or renderability contradiction and the better "
                "label already appears as a normalized_candidate.normalized_label "
                "on a specific event."
            ),
            (
                "Use only the event table and evidence contexts below; do not use "
                "outside final-answer sources, row IDs, split membership, or scoring metadata."
            ),
            (
                "The action owns the final rendered label: keep_original renders "
                "original_final.final_label; replace_with_existing_event renders the "
                "selected event normalized_candidate.normalized_label."
            ),
            (
                "This v0.2 high-precision run disables free recomputation: do not "
                "use replace_with_recomputed_fact_from_selected_evidence or "
                "abstain_unrenderable. If the correction is not already an existing "
                "normalized_candidate label, keep original_final."
            ),
            (
                "For keep_original_structured_event_final, cite the original selected "
                "events unless a missing event table makes that impossible."
            ),
            (
                "For replace_with_existing_event, select exactly one event ID whose "
                "normalized_candidate is renderable and whose evidence supports the "
                "correction."
            ),
            (
                "This v0.5 run does not allow seizure-free replacement corrections. "
                "If the better-looking event has normalized_candidate.semantic_kind "
                "seizure_free and original_final is not already seizure_free, keep "
                "original_final."
            ),
            (
                "Before returning replace_with_existing_event, inspect the selected "
                "event normalized_candidate.semantic_kind. If it is seizure_free, "
                "stop and return keep_original_structured_event_final."
            ),
            "Prefer keep_original when the correction is uncertain or merely stylistic.",
            (
                "Do not replace an original numeric/range frequency with seizure_free "
                "in this run, even when a selected event has a seizure_free "
                "normalized_candidate. These cases are reserved for a later duration "
                "specialist."
            ),
            (
                "Do not replace original seizure_free with unknown just because the "
                "note mentions non-epileptic, less intrusive, or noncountable episodes; "
                "replace only when an existing selected event normalized_candidate is "
                "unknown and directly contradicts the original seizure-free evidence."
            ),
            (
                "Use replace_with_existing_event for unknown/no_reference boundary "
                "corrections only when the original selected a numeric frequency from "
                "a one-off, anchored, or nonrecurring mention rather than a recurring "
                "cadence, and a specific event already has normalized_candidate "
                "unknown or no seizure frequency reference."
            ),
            (
                "Anchored/nonrecurring numeric mentions include isolated recent "
                "events, named calendar months, counts since starting a treatment, "
                "latest-on-date summaries, and vague review windows. They are not "
                "the same as explicit recurring cadences like monthly, weekly, daily, "
                "or every four to five weeks."
            ),
            (
                "Use replace_with_existing_event for one safe burden correction class: "
                "the original final is a broad total count over an elapsed window "
                "such as 'so far this year', while a specific current event already "
                "has a clearer recurring cadence normalized_candidate such as "
                "'1 per month', 'per week', or 'per day'."
            ),
            "Evidence entries should be exact substrings from the note when possible.",
            "Use spaces in labels, for example 'multiple per day', not underscores.",
            (
                "final_label must be a valid Gan label only: unknown, no seizure "
                "frequency reference, seizure free, multiple per day/week/month/year, "
                "or '<number> [to <number>] per day/week/month/year'. Do not include "
                "seizure type, diagnosis, dates, or phrases such as 'since last review'."
            ),
            (
                "Preserve cluster labels when the selected event contains both cluster "
                "cadence and events-per-cluster burden; do not collapse a cluster "
                "label to cadence alone."
            ),
            (
                "Do not change supported absence-since evidence to unknown merely "
                "because it is not a recurring cadence."
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
                "action, final_kind, uncertainty, and attribution must each be one "
                "string, not an array of options."
            ),
        ],
        "required_output_schema": {
            "action": list(PROMPT_ACTION_VALUES),
            "final_label": "Gan-style label string owned by action semantics",
            "final_kind": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_event_ids": "list of event IDs selected from the event table",
            "rejected_event_ids": "list of event IDs explicitly rejected",
            "evidence": "list of exact evidence substrings supporting the action",
            "contradiction_profile": (
                "list of targeted profile keys, such as higher_current_burden"
            ),
            "calculation_trace": "short arithmetic or boundary trace, or null",
            "clinical_rationale": "brief clinical rationale for the action",
            "uncertainty": "one string: low | medium | high",
            "tool_calls": "empty list unless a verifier tool was actually called",
            "attribution": (
                "one string: llm_selected_tool_rendered | "
                "llm_selected_format_repaired | llm_original_structured_event_kept"
            ),
        },
        "disabled_actions_for_this_run": [
            "replace_with_recomputed_fact_from_selected_evidence",
            "abstain_unrenderable",
        ],
        "boundary_guide": {
            "higher_current_burden": (
                "Prefer the highest active current burden when multiple semiologies "
                "or rates are concurrently asserted."
            ),
            "cluster_axis": (
                "Separate cluster cadence from seizures per cluster before rendering "
                "the final burden."
            ),
            "seizure_free_conflict": (
                "A current asserted frequency conflicts with seizure-free unless it "
                "is historical, resolved, or before the absence-since interval."
            ),
            "unknown_no_reference_boundary": (
                "Use unknown when frequency evidence exists but is unrenderable; use "
                "no seizure frequency reference only when no usable frequency evidence exists."
            ),
            "denominator_range": (
                "Convert explicit denominators or ranges only when the time window is "
                "stated; vague intervals are unrenderable unless a cadence is also present."
            ),
        },
        "structured_event_input": structured_input,
        "raw_evidence_contexts": llm_event_reasoner._evidence_contexts(
            record.note_text,
            structured_event_row,
        ),
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_verifier_decision_json(
    raw_output: str,
    structured_event_row: Mapping[str, Any] | None,
) -> ParsedVerifierDecision:
    """Parse a verifier decision and render the model-owned action."""

    parsed = STAGE.parse_response(raw_output)
    parse_errors: list[str] = list(parsed.parse_errors)
    raw_verifier_decision = parsed.decision
    if raw_verifier_decision is None:
        return ParsedVerifierDecision(
            raw_verifier_decision=None,
            raw_common_decision=None,
            format_only_decision=None,
            final_decision=None,
            parse_errors=parse_errors,
        )

    raw_common_decision = _common_decision_from_verifier(raw_verifier_decision)
    format_decision, repair_events, format_notes = _format_only_decision(raw_common_decision)
    parse_errors.extend(format_notes)
    try:
        label_to_frequency_record(format_decision.final_label)
    except ValueError as exc:
        parse_errors.append(f"raw_unscorable_final_label: {exc}")
    final_decision, action_events, action_errors = _render_verifier_action(
        raw_verifier_decision,
        format_decision,
        structured_event_row,
    )
    parse_errors.extend(action_errors)
    return ParsedVerifierDecision(
        raw_verifier_decision=raw_verifier_decision,
        raw_common_decision=raw_common_decision,
        format_only_decision=format_decision,
        final_decision=final_decision,
        parse_errors=parse_errors,
        format_repair_events=repair_events,
        action_render_events=action_events,
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize verifier rows across raw, format-only, final, and V0 layers."""

    summary: dict[str, Any] = {
        "rows": len(rows),
        "prediction_bearing_rows": 0,
        "model_calls_attempted": 0,
        "call_failures": 0,
        "parse_or_validation_failures": 0,
        "action_render_failures": 0,
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
        "action_rendered_rows": 0,
        "wrong_to_correct_vs_v0": 0,
        "correct_to_wrong_vs_v0": 0,
        "changed_labels_vs_v0": 0,
    }
    final_labels: Counter[str] = Counter()
    verifier_actions: Counter[str] = Counter()
    for row in rows:
        summary["prediction_bearing_rows"] += int(row.get("decision_record") is not None)
        summary["model_calls_attempted"] += int(row.get("model_call_attempted") is True)
        summary["call_failures"] += int(row.get("call_error") is not None)
        summary["parse_or_validation_failures"] += int(
            has_blocking_parse_issue(
                row.get("parse_errors"),
                blocking_prefixes=(
                    "invalid_json:",
                    "schema_validation_error:",
                    "action_render_error:",
                ),
            )
        )
        summary["action_render_failures"] += int(
            any(
                str(error).startswith("action_render_error:")
                for error in row.get("parse_errors") or []
            )
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
        summary["action_rendered_rows"] += int(bool(row.get("action_render_events")))
        verifier_record = dict(row.get("verifier_decision_record") or {})
        if verifier_record.get("action") is not None:
            verifier_actions[str(verifier_record["action"])] += 1
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
    summary["verifier_actions"] = dict(sorted(verifier_actions.items()))
    summary["final_labels"] = dict(sorted(final_labels.items()))
    return summary


def gate_interpretation(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Interpret the verifier contract gate without promoting a benchmark score."""

    return llm_event_reasoner.gate_interpretation(summary)


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_stage_jsonl(rows, path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = dict(metadata.get("summary") or {})
    gate = dict(metadata.get("gate") or {})
    lines = build_markdown_report_skeleton(
        title="Gan 2026 Structured-Event Verifier",
        metadata=metadata,
        summary=summary,
        gate=gate,
        jsonl_path=jsonl_path,
        extra_sections=[
            "This is a validation-development V4 verifier-first structured-event artifact.",
            "The model chooses an explicit verifier action over saved LLM structured events.",
            "",
        ],
        experiment_unit_lines=[
            "- Work class: V4 verifier-first structured-event correction.",
            f"- Rows: {summary.get('rows', 0)}",
            "- Split: `validation`, manifest `gan2026_split_v1`.",
            f"- Mode: `{metadata.get('mode')}`",
            f"- Model: `{metadata.get('model')}`",
            f"- Prompt version: `{metadata.get('prompt_version')}`",
            f"- Structured-event source: `{metadata.get('structured_event_source_path')}`",
        ],
        summary_lines=[
            f"- Prediction-bearing rows: {summary.get('prediction_bearing_rows', 0)}",
            f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
            f"- Call failures: {summary.get('call_failures', 0)}",
            f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
            f"- Action-render failures: {summary.get('action_render_failures', 0)}",
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
            f"- Verifier actions: `{summary.get('verifier_actions', {})}`",
        ],
        row_table_header=(
            "| Row | Action | V0 | Raw | Format-only | Final | Transition | "
            "Evidence exact | Notes |"
        ),
        row_table_rows=[_report_row_line(row) for row in rows],
    )
    write_stage_markdown_report(path, lines)


def _report_row_line(row: Mapping[str, Any]) -> str:
    layers = dict(row.get("score_layers") or {})
    verifier_record = dict(row.get("verifier_decision_record") or {})
    notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
    if row.get("call_error"):
        notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
    return (
        f"| {row.get('source_row_index')} | "
        f"`{verifier_record.get('action')}` | "
        f"`{dict(row.get('v0_reference') or {}).get('final_label')}` | "
        f"`{dict(layers.get('raw_model') or {}).get('final_label')}` | "
        f"`{dict(layers.get('format_only') or {}).get('final_label')}` | "
        f"`{dict(layers.get('final') or {}).get('final_label')}` | "
        f"`{dict(row.get('transition_vs_v0') or {}).get('purist_transition')}` | "
        f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
    )


class StructuredEventVerifierSignature(dspy.Signature):
    """Verify one saved structured-event record and emit one JSON action."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON payload with one sanitized structured-event record and evidence contexts."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object matching StructuredEventVerifierDecision."
    )


class DspyStructuredEventVerifierCaller(dspy.Module):
    """DSPy caller for the V4 structured-event verifier."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(StructuredEventVerifierSignature)

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
        parse_verifier_decision_json(raw_output, structured_event_row)
        if raw_output
        else ParsedVerifierDecision(
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
    prediction = DspyStructuredEventVerifierCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


def _filter_verifier_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    allowed = set(StructuredEventVerifierDecision.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def _repair_verifier_decision_shape(payload: Any) -> tuple[Any, list[str]]:
    if not isinstance(payload, dict):
        return payload, []
    repaired = dict(payload)
    notes: list[str] = []
    if "contradiction_profile" not in repaired and "boundary_profile" in repaired:
        repaired["contradiction_profile"] = repaired["boundary_profile"]
        notes.append("decision_field_alias_repaired:boundary_profile")
    for field_name in (
        "selected_event_ids",
        "rejected_event_ids",
        "evidence",
        "contradiction_profile",
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
        ("action", VERIFIER_ACTION_VALUES),
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


def _common_decision_from_verifier(
    decision: StructuredEventVerifierDecision,
) -> llm_event_reasoner.ReasonedFrequencyDecision:
    return llm_event_reasoner.ReasonedFrequencyDecision(
        final_label=decision.final_label,
        final_kind=decision.final_kind,
        selected_event_ids=decision.selected_event_ids,
        rejected_event_ids=decision.rejected_event_ids,
        evidence=decision.evidence,
        boundary_profile=decision.contradiction_profile,
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


def _render_verifier_action(
    raw_verifier_decision: StructuredEventVerifierDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, list[str], list[str]]:
    action = raw_verifier_decision.action
    render_events: list[str] = []
    render_errors: list[str] = []
    if action == "keep_original_structured_event_final":
        final_decision, error = _render_keep_original_action(
            raw_verifier_decision,
            format_decision,
            structured_event_row,
        )
        if error:
            render_errors.append(error)
            return None, render_events, render_errors
        render_events.append("verifier_action_rendered:keep_original_structured_event_final")
        return final_decision, render_events, render_errors
    if action == "replace_with_existing_event":
        final_decision, event_id, error = _render_existing_event_action(
            raw_verifier_decision,
            format_decision,
            structured_event_row,
        )
        if error:
            render_errors.append(error)
            return None, render_events, render_errors
        render_events.append(f"verifier_action_rendered:replace_with_existing_event:{event_id}")
        return final_decision, render_events, render_errors
    if action == "replace_with_recomputed_fact_from_selected_evidence":
        final_decision, error = _render_recomputed_action(
            raw_verifier_decision,
            format_decision,
        )
        if error:
            render_errors.append(error)
            return None, render_events, render_errors
        render_events.append(
            "verifier_action_rendered:replace_with_recomputed_fact_from_selected_evidence"
        )
        return final_decision, render_events, render_errors
    final_decision = format_decision.model_copy(
        update={
            "final_label": "unknown",
            "final_kind": "unknown",
            "attribution": "llm_selected_tool_rendered",
        }
    )
    render_events.append("verifier_action_rendered:abstain_unrenderable")
    return final_decision, render_events, render_errors


def _render_keep_original_action(
    raw_verifier_decision: StructuredEventVerifierDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, str | None]:
    selection = _structured_selection(structured_event_row)
    label = _as_optional_str(selection.get("final_label"))
    if label is None:
        return None, "action_render_error: missing_original_final_label"
    label_record, error = _label_record(label)
    if error or label_record is None:
        return None, f"action_render_error: original_final_label_unscorable: {error}"
    selected_ids = _string_tuple(selection.get("selected_event_ids"))
    evidence = _evidence_tuple(selection.get("evidence")) or raw_verifier_decision.evidence
    return (
        format_decision.model_copy(
            update={
                "final_label": label_record.normalized_label,
                "final_kind": _decision_kind_for_label_record(label_record),
                "selected_event_ids": selected_ids,
                "evidence": evidence,
                "attribution": "llm_original_structured_event_kept",
            }
        ),
        None,
    )


def _render_existing_event_action(
    raw_verifier_decision: StructuredEventVerifierDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
    structured_event_row: Mapping[str, Any] | None,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, str | None, str | None]:
    event_id = (
        raw_verifier_decision.selected_event_ids[0]
        if raw_verifier_decision.selected_event_ids
        else None
    )
    if event_id is None:
        return None, None, "action_render_error: replace_existing_event_missing_selected_event"
    normalized = llm_event_reasoner._normalized_event_by_id(structured_event_row or {}).get(
        event_id
    )
    if normalized is None:
        return None, event_id, f"action_render_error: selected_event_not_normalized:{event_id}"
    label = _as_optional_str(normalized.get("normalized_label"))
    if label is None:
        return None, event_id, f"action_render_error: selected_event_missing_label:{event_id}"
    label_record, error = _label_record(label)
    if error or label_record is None:
        return (
            None,
            event_id,
            f"action_render_error: selected_event_label_unscorable:{event_id}: {error}",
        )
    evidence = raw_verifier_decision.evidence or _event_evidence_tuple(
        structured_event_row,
        event_id,
    )
    return (
        format_decision.model_copy(
            update={
                "final_label": label_record.normalized_label,
                "final_kind": _decision_kind_for_label_record(label_record),
                "selected_event_ids": (event_id,),
                "evidence": evidence,
                "attribution": "llm_selected_tool_rendered",
            }
        ),
        event_id,
        None,
    )


def _render_recomputed_action(
    raw_verifier_decision: StructuredEventVerifierDecision,
    format_decision: llm_event_reasoner.ReasonedFrequencyDecision,
) -> tuple[llm_event_reasoner.ReasonedFrequencyDecision | None, str | None]:
    label_record, error = _label_record(format_decision.final_label)
    if error or label_record is None:
        return None, f"action_render_error: recomputed_label_unscorable: {error}"
    attribution = (
        "llm_selected_format_repaired"
        if format_decision.final_label != raw_verifier_decision.final_label
        else "llm_selected_tool_rendered"
    )
    return (
        format_decision.model_copy(
            update={
                "final_label": label_record.normalized_label,
                "final_kind": _decision_kind_for_label_record(label_record),
                "attribution": attribution,
            }
        ),
        None,
    )


def _structured_selection(structured_event_row: Mapping[str, Any] | None) -> dict[str, Any]:
    if structured_event_row is None:
        return {}
    return dict(dict(structured_event_row.get("structured_record") or {}).get("selection") or {})


def _event_evidence_tuple(
    structured_event_row: Mapping[str, Any] | None,
    event_id: str,
) -> tuple[str, ...]:
    if structured_event_row is None:
        return ()
    structured_record = dict(structured_event_row.get("structured_record") or {})
    for event in structured_record.get("events") or []:
        if not isinstance(event, Mapping):
            continue
        if str(event.get("event_id") or "") != event_id:
            continue
        return _evidence_tuple(event.get("evidence"))
    return ()


def _evidence_tuple(value: Any) -> tuple[str, ...]:
    return tuple(item for item in _string_tuple(value) if item)


def _label_record(label: str) -> tuple[Any | None, str | None]:
    try:
        return label_to_frequency_record(label), None
    except ValueError as exc:
        return None, str(exc)


def _decision_kind_for_label_record(label_record: Any) -> llm_event_reasoner.DecisionKind:
    return cast(llm_event_reasoner.DecisionKind, str(label_record.kind))


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


def _has_blocking_parse_issue(errors: Any) -> bool:
    return has_blocking_parse_issue(
        errors,
        blocking_prefixes=(
            "invalid_json:",
            "schema_validation_error:",
            "action_render_error:",
        ),
    )


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
