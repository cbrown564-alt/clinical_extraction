"""D2 direct-plus-boundary-critic rescue-only runner for Gan 2026 hard slices.

Migrated to :mod:`stage_protocol` (prompt builders + decision schemas + postprocess
policy + thin ``run_split``).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.stage_protocol import (
    AgenticStage,
    DEFAULT_BLOCKING_PARSE_PREFIXES,
    DEFAULT_REPAIR_NOTE_PREFIXES,
    ParsedStageResponse,
    build_markdown_report_skeleton,
    build_stage_metadata,
    configure_dspy_for_stage,
    emit_progress_checkpoint,
    extract_json_object,
    has_blocking_parse_issue,
    has_repair_note,
    parse_response,
    write_stage_jsonl,
    write_stage_markdown_report,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tools import (
    read_boundary_guide,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_decision_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler import (
    LlmOnlyDirectLabelerDecisionRecord,
    parse_decision_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
)

PROMPT_VERSION = "gan2026_agentic_direct_boundary_critic_rescue_v1"
CONDITION = "direct_boundary_critic_rescue"
REFERENCE_CONDITION = "single_self_consistency_temperature"
DIRECT_CALL_ROLE = "direct_no_tool_final_label"
CRITIC_CALL_ROLE = "boundary_critic_rescue"
PANEL_SOURCE_ROW_INDICES: tuple[int, ...] = (
    6368,
    7615,
    10677,
    10996,
    5534,
    6131,
    15193,
    15834,
    3356,
    4690,
    9955,
    12422,
)
FIXED_BOUNDARY_GUIDE_IDS: tuple[str, ...] = (
    "multiple_current_events_aggregation",
    "seizure_free_event_conflict",
    "cluster_frequency_vs_incidental_clustering",
    "unknown_frequency_vs_no_reference",
    "current_vs_historical_window",
    "different_semiology_burdens",
)

DirectDecisionRecord = LlmOnlyDirectLabelerDecisionRecord
CriticAction = Literal[
    "keep",
    "restore_cluster_burden",
    "raise_current_burden",
    "block_boundary_demotion",
    "abstain",
]


class BoundaryCriticDecisionRecord(BaseModel):
    """Constrained critic action over a direct answer."""

    model_config = ConfigDict(extra="forbid")

    action: CriticAction
    proposed_final_label: str | None = None
    evidence: str
    cluster_cadence_evidence: str | None = None
    events_per_cluster_evidence: str | None = None
    higher_current_burden_evidence: str | None = None
    boundary_demotion_hazard: str | None = None
    confidence: Literal["low", "medium", "high"]
    rationale: str


class DirectDecisionSignature(dspy.Signature):
    """Extract one Gan 2026 seizure-frequency decision as strict JSON."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with one note and no tool context."
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "Strict JSON object with final_label, evidence, answer_kind, "
            "selected_seizure_type, time_window, confidence, and rationale."
        )
    )


class BoundaryCriticSignature(dspy.Signature):
    """Emit one conservative rescue action over a direct Gan 2026 answer."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with one note, one direct answer, and boundary guides."
    )
    critic_json: str = dspy.OutputField(
        desc=(
            "Strict JSON object with action, proposed_final_label, evidence, "
            "cluster_cadence_evidence, events_per_cluster_evidence, "
            "higher_current_burden_evidence, boundary_demotion_hazard, confidence, "
            "and rationale."
        )
    )


class DspyDirectDecisionCaller(dspy.Module):
    """DSPy wrapper for the D2 direct no-tool call."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(DirectDecisionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


class DspyBoundaryCriticCaller(dspy.Module):
    """DSPy wrapper for the D2 boundary critic call."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(BoundaryCriticSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


_CRITIC_BLOCKING_PREFIXES: tuple[str, ...] = (
    *DEFAULT_BLOCKING_PARSE_PREFIXES,
    "unscorable_proposed_final_label:",
)
_CRITIC_REPAIR_PREFIXES: tuple[str, ...] = (
    *DEFAULT_REPAIR_NOTE_PREFIXES,
    "proposed_final_label_repaired:",
)


class DirectDecisionStage(AgenticStage[DirectDecisionRecord]):
    """D2 direct no-tool prompt builder + parse policy."""

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_prompt_input(self, record: GanFrequencyRecord, **_: object) -> str:
        return _build_direct_prompt_input(record)

    def parse_response(
        self,
        raw_output: str,
        **_: object,
    ) -> ParsedStageResponse[DirectDecisionRecord]:
        decision, errors = parse_decision_json(raw_output)
        return ParsedStageResponse(decision, parse_errors=errors)


class BoundaryCriticStage(AgenticStage[BoundaryCriticDecisionRecord]):
    """D2 boundary critic prompt builder + parse/postprocess policy."""

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_prompt_input(
        self,
        record: GanFrequencyRecord,
        *,
        direct_call: Mapping[str, Any],
        guide_results: Sequence[Mapping[str, Any]],
        **_: object,
    ) -> str:
        return _build_critic_prompt_input(
            record,
            direct_call=direct_call,
            guide_results=guide_results,
        )

    def parse_response(
        self,
        raw_output: str,
        **_: object,
    ) -> ParsedStageResponse[BoundaryCriticDecisionRecord]:
        parsed = parse_response(
            raw_output,
            decision_model=BoundaryCriticDecisionRecord,
            payload_filter=_filter_critic_payload,
            shape_repair=_repair_critic_payload_shape,
            label_field="proposed_final_label",
            evidence_field="evidence",
            label_repair="none",
            require_scorable_label=False,
        )
        if parsed.decision is None:
            return parsed
        decision, repair_notes = self.postprocess_decision(parsed.decision)
        return ParsedStageResponse(
            decision,
            parse_errors=[*parsed.parse_errors, *repair_notes],
            format_repair_events=parsed.format_repair_events,
            raw_final_label=parsed.raw_final_label,
        )

    def postprocess_decision(
        self,
        decision: BoundaryCriticDecisionRecord,
        *,
        note_text: str = "",
        **_: object,
    ) -> tuple[BoundaryCriticDecisionRecord, list[str]]:
        del note_text
        errors: list[str] = []
        if not decision.proposed_final_label:
            return decision, errors
        format_label = repair_prediction_label_format_preserving(decision.proposed_final_label)
        if _label_kind(format_label) in {"seizure_free", "unknown", "no_reference"}:
            repaired_label = format_label
        else:
            repaired_label = repair_prediction_label_with_evidence(
                decision.proposed_final_label,
                decision.evidence,
            )
        if repaired_label != decision.proposed_final_label:
            errors.append(
                "proposed_final_label_repaired: "
                f"{decision.proposed_final_label!r} -> {repaired_label!r}"
            )
            decision = decision.model_copy(update={"proposed_final_label": repaired_label})
        try:
            label_to_frequency_record(decision.proposed_final_label)
        except ValueError as exc:
            errors.append(f"unscorable_proposed_final_label: {exc}")
        return decision, errors


DIRECT_STAGE = DirectDecisionStage()
CRITIC_STAGE = BoundaryCriticStage()


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    reference_rows: Sequence[Mapping[str, Any]],
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only", "reuse"],
    dspy_cache: bool,
    api_base: str | None,
    reuse_raw_outputs: Mapping[int, Mapping[str, str]] | None = None,
    reuse_source: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    surface: Literal["panel", "hard50"] = "panel",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run D2 over the predeclared panel or fixed validation hard50 slice."""

    if mode == "live":
        configure_dspy_for_stage(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=dspy_cache,
            api_base=api_base,
        )
    reuse_raw_outputs = reuse_raw_outputs or {}
    reference_labels = _reference_labels(reference_rows)
    metadata = _metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
    )
    metadata["reuse_source"] = reuse_source
    metadata["surface"] = surface
    if surface == "hard50":
        metadata["artifact_kind"] = "gan2026_agentic_direct_boundary_critic_rescue_hard50"
        metadata["claim_boundary"] = (
            "validation-development D2 hard50 only; direct no-tool answer plus "
            "boundary critic, parser candidates disabled as prompt context, no "
            "holdout use, no row-level test inspection, and no benchmark claim"
        )
    rows: list[dict[str, Any]] = []
    for record in records:
        reuse_pair = reuse_raw_outputs.get(record.source_row_index, {})
        rows.append(
            _build_row(
                record,
                reference_label=reference_labels.get(record.source_row_index),
                split=split,
                split_manifest=split_manifest,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                mode=mode,
                reuse_direct_raw_output=reuse_pair.get("direct"),
                reuse_critic_raw_output=reuse_pair.get("critic"),
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
    metadata["gate"] = gate_interpretation(metadata["summary"], surface=surface)
    return rows, metadata


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    purist_correct = 0
    pragmatic_correct = 0
    direct_purist_correct = 0
    critic_raw_purist_correct = 0
    wins = 0
    losses = 0
    changed_labels = 0
    call_failures = 0
    reused_raw_outputs = 0
    direct_decision_records = 0
    critic_decision_records = 0
    parse_failures = 0
    repair_rows = 0
    evidence_exact = 0
    accepted_rescue_correct = 0
    accepted_action_regressions = 0
    accepted_boundary_demotions = 0
    final_labels = Counter()
    direct_labels = Counter()
    critic_labels = Counter()
    action_counts = Counter()
    blocked_reasons = Counter()
    for row in rows:
        comparison = dict(row.get("comparison") or {})
        direct_comparison = dict(row.get("direct_comparison") or {})
        critic_comparison = dict(row.get("raw_critic_proposed_comparison") or {})
        reference_comparison = dict(row.get("reference_comparison") or {})
        direct_call = dict(row.get("direct_call") or {})
        critic_call = dict(row.get("critic_call") or {})
        action_policy = dict(row.get("action_policy") or {})

        purist_correct += int(bool(comparison.get("purist_correct")))
        pragmatic_correct += int(bool(comparison.get("pragmatic_correct")))
        direct_purist_correct += int(bool(direct_comparison.get("purist_correct")))
        critic_raw_purist_correct += int(bool(critic_comparison.get("purist_correct")))
        wins += int(
            bool(comparison.get("purist_correct"))
            and not bool(reference_comparison.get("purist_correct"))
        )
        losses += int(
            bool(reference_comparison.get("purist_correct"))
            and not bool(comparison.get("purist_correct"))
        )
        changed_labels += int(
            _normalized_label(row.get("final_label"))
            != _normalized_label(row.get("reference_label"))
        )
        call_failures += int(direct_call.get("call_error") is not None)
        call_failures += int(critic_call.get("call_error") is not None)
        reused_raw_outputs += int(bool(direct_call.get("reused_raw_output")))
        reused_raw_outputs += int(bool(critic_call.get("reused_raw_output")))
        direct_decision_records += int(direct_call.get("decision_record") is not None)
        critic_decision_records += int(critic_call.get("decision_record") is not None)
        parse_failures += int(
            has_blocking_parse_issue(
                direct_call.get("parse_errors"),
                blocking_prefixes=_CRITIC_BLOCKING_PREFIXES,
            )
        )
        parse_failures += int(
            has_blocking_parse_issue(
                critic_call.get("parse_errors"),
                blocking_prefixes=_CRITIC_BLOCKING_PREFIXES,
            )
        )
        repair_rows += int(
            has_repair_note(
                direct_call.get("parse_errors"),
                repair_prefixes=_CRITIC_REPAIR_PREFIXES,
            )
        )
        repair_rows += int(
            has_repair_note(
                critic_call.get("parse_errors"),
                repair_prefixes=_CRITIC_REPAIR_PREFIXES,
            )
        )
        evidence_exact += int(bool(direct_call.get("evidence_valid")))
        evidence_exact += int(bool(critic_call.get("evidence_valid")))
        accepted_rescue_correct += int(
            row.get("accepted_action") != "fallback"
            and bool(comparison.get("purist_correct"))
            and not bool(direct_comparison.get("purist_correct"))
        )
        accepted_action_regressions += int(
            row.get("accepted_action") != "fallback"
            and bool(direct_comparison.get("purist_correct"))
            and not bool(comparison.get("purist_correct"))
        )
        accepted_boundary_demotions += int(
            row.get("accepted_action") != "fallback"
            and _label_kind(row.get("final_label"))
            in {"seizure_free", "unknown", "no_reference"}
            and _is_frequency_or_cluster_label(row.get("direct_label"))
        )
        final_label = row.get("final_label")
        if final_label is not None:
            final_labels[str(final_label)] += 1
        direct_label = row.get("direct_label")
        if direct_label is not None:
            direct_labels[str(direct_label)] += 1
        critic_label = row.get("raw_critic_proposed_label")
        if critic_label is not None:
            critic_labels[str(critic_label)] += 1
        action_counts[str(row.get("accepted_action"))] += 1
        blocked_reason = action_policy.get("blocked_reason")
        if blocked_reason:
            blocked_reasons[str(blocked_reason)] += 1
    return {
        "rows": len(rows),
        "condition": CONDITION,
        "reference_condition": REFERENCE_CONDITION,
        "model_calls_attempted": len(rows) * 2,
        "direct_decision_records": direct_decision_records,
        "critic_decision_records": critic_decision_records,
        "call_failures": call_failures,
        "reused_raw_outputs": reused_raw_outputs,
        "parse_or_validation_failures": parse_failures,
        "schema_or_label_repair_rows": repair_rows,
        "evidence_exact_substrings": evidence_exact,
        "direct_purist_correct": direct_purist_correct,
        "raw_critic_proposed_purist_correct": critic_raw_purist_correct,
        "purist_correct": purist_correct,
        "pragmatic_correct": pragmatic_correct,
        "wins_vs_reference": wins,
        "losses_vs_reference": losses,
        "changed_labels_vs_reference": changed_labels,
        "changed_label_precision": round(wins / changed_labels, 4)
        if changed_labels
        else None,
        "accepted_rescue_correct": accepted_rescue_correct,
        "accepted_action_regressions": accepted_action_regressions,
        "accepted_boundary_demotions": accepted_boundary_demotions,
        "fallback_rate": round(action_counts["fallback"] / len(rows), 4)
        if rows
        else 0.0,
        "accepted_action_counts": dict(sorted(action_counts.items())),
        "blocked_reasons": dict(sorted(blocked_reasons.items())),
        "parser_context_disabled": True,
        "fixed_boundary_guide_ids": list(FIXED_BOUNDARY_GUIDE_IDS),
        "direct_final_labels": dict(sorted(direct_labels.items())),
        "raw_critic_proposed_labels": dict(sorted(critic_labels.items())),
        "final_labels": dict(sorted(final_labels.items())),
    }


def gate_interpretation(
    summary: Mapping[str, Any],
    *,
    surface: Literal["panel", "hard50"] = "panel",
) -> dict[str, Any]:
    parse_failures = int(summary.get("parse_or_validation_failures", 0))
    if surface == "hard50":
        wins = int(summary.get("wins_vs_reference", 0))
        losses = int(summary.get("losses_vs_reference", 0))
        precision = summary.get("changed_label_precision")
        if (
            parse_failures == 0
            and wins >= 5
            and losses <= 1
            and precision is not None
            and float(precision) >= 0.70
        ):
            status = "pass_hard50_gate"
            interpretation = (
                "Direct plus boundary critic passed the hard50 rescue gate; "
                "D3 may be considered, while validation250 still needs a separate "
                "written escalation reason."
            )
        else:
            status = "reject_or_revise_after_hard50"
            interpretation = (
                "Direct plus boundary critic did not satisfy the hard50 gate; do "
                "not escalate to D3 or validation250 from this condition."
            )
        return {
            "status": status,
            "surface": surface,
            "wins_vs_reference": wins,
            "losses_vs_reference": losses,
            "required_wins": 5,
            "max_losses": 1,
            "changed_label_precision": precision,
            "required_changed_label_precision": 0.70,
            "parse_or_validation_failures": parse_failures,
            "interpretation": interpretation,
        }

    accepted_rescue_correct = int(summary.get("accepted_rescue_correct", 0))
    accepted_boundary_demotions = int(summary.get("accepted_boundary_demotions", 0))
    if (
        parse_failures == 0
        and accepted_boundary_demotions == 0
        and accepted_rescue_correct >= 4
    ):
        status = "pass_panel_gate"
        interpretation = (
            "Direct plus boundary critic passed the predeclared micro-panel gate; "
            "fixed hard50 is permitted as the next D2 surface."
        )
    else:
        status = "reject_or_revise_before_hard50"
        interpretation = (
            "Direct plus boundary critic did not satisfy the micro-panel gate; do "
            "not run D2 hard50 without revising or stopping the live branch."
        )
    return {
        "status": status,
        "surface": surface,
        "accepted_rescue_correct": accepted_rescue_correct,
        "required_accepted_rescue_correct": 4,
        "accepted_boundary_demotions": accepted_boundary_demotions,
        "max_accepted_boundary_demotions": 0,
        "parse_or_validation_failures": parse_failures,
        "interpretation": interpretation,
    }


def apply_action_policy(
    record: GanFrequencyRecord,
    direct_decision: DirectDecisionRecord | None,
    critic_decision: BoundaryCriticDecisionRecord | None,
) -> dict[str, Any]:
    """Apply the D2 conservative rescue-only gate to a direct answer and critic."""

    if direct_decision is None:
        return {
            "final_label": None,
            "accepted_action": "fallback",
            "blocked_reason": "no_direct_decision",
            "changed_label_attribution": "no_prediction",
        }
    direct_label = direct_decision.final_label
    if critic_decision is None:
        return {
            "final_label": direct_label,
            "accepted_action": "fallback",
            "blocked_reason": "no_critic_decision",
            "changed_label_attribution": "direct_model",
        }
    action = critic_decision.action
    proposed_label = critic_decision.proposed_final_label
    if action in {"keep", "block_boundary_demotion", "abstain"}:
        return {
            "final_label": direct_label,
            "accepted_action": "fallback",
            "blocked_reason": f"fallback_action:{action}",
            "changed_label_attribution": "direct_model",
        }
    if not proposed_label:
        return {
            "final_label": direct_label,
            "accepted_action": "fallback",
            "blocked_reason": "missing_proposed_label",
            "changed_label_attribution": "direct_model",
        }
    if _label_kind(proposed_label) in {"seizure_free", "unknown", "no_reference"}:
        return {
            "final_label": direct_label,
            "accepted_action": "fallback",
            "blocked_reason": "boundary_label_override_blocked",
            "changed_label_attribution": "direct_model",
        }
    if action == "restore_cluster_burden":
        return _apply_restore_cluster_policy(record, direct_label, critic_decision)
    if action == "raise_current_burden":
        return _apply_raise_burden_policy(record, direct_label, critic_decision)
    return {
        "final_label": direct_label,
        "accepted_action": "fallback",
        "blocked_reason": f"unknown_action:{action}",
        "changed_label_attribution": "direct_model",
    }


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
    surface = str(metadata.get("surface", "panel"))
    surface_label = "Hard50" if surface == "hard50" else "Panel"
    lines = build_markdown_report_skeleton(
        title=f"Gan 2026 Agentic Direct Boundary Critic Rescue {surface_label}",
        metadata=metadata,
        summary=summary,
        gate=gate,
        jsonl_path=jsonl_path,
        experiment_unit_lines=[
            f"- Work class: D2 validation {surface} direct-plus-boundary-critic rescue-only.",
            (
                "- Hypothesis: boundary reasoning is useful as a constrained critic over "
                "a direct answer, not as a replacement labeler."
            ),
            "- Minimal change: one direct no-tool call plus one boundary critic call.",
            f"- Rows: {summary.get('rows', 0)}",
            f"- Condition: `{CONDITION}`",
            f"- Reference condition: `{REFERENCE_CONDITION}`",
            "- Split: `validation`, manifest `gan2026_split_v1`.",
            f"- Surface: predeclared D2 `{surface}`.",
            f"- Mode: `{metadata.get('mode')}`",
            f"- Model: `{metadata.get('model')}`",
            f"- Prompt version: `{metadata.get('prompt_version')}`",
            "- Parser context: disabled; fixed boundary-guide set used by the critic.",
        ],
        summary_lines=[
            f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
            f"- Direct decision records: {summary.get('direct_decision_records', 0)}",
            f"- Critic decision records: {summary.get('critic_decision_records', 0)}",
            f"- Call failures: {summary.get('call_failures', 0)}",
            f"- Reused raw outputs: {summary.get('reused_raw_outputs', 0)}",
            f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
            f"- Schema/label repair rows: {summary.get('schema_or_label_repair_rows', 0)}",
            f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
            f"- Direct Purist: {summary.get('direct_purist_correct', 0)}/{summary.get('rows', 0)}",
            (
                "- Raw critic proposed-label Purist: "
                f"{summary.get('raw_critic_proposed_purist_correct', 0)}/"
                f"{summary.get('rows', 0)}"
            ),
            f"- Gated-final Purist: {summary.get('purist_correct', 0)}/{summary.get('rows', 0)}",
            (
                "- Gated-final Pragmatic: "
                f"{summary.get('pragmatic_correct', 0)}/{summary.get('rows', 0)}"
            ),
            f"- Wins vs reference: {summary.get('wins_vs_reference', 0)}",
            f"- Losses vs reference: {summary.get('losses_vs_reference', 0)}",
            f"- Changed labels vs reference: {summary.get('changed_labels_vs_reference', 0)}",
            f"- Changed-label precision: {summary.get('changed_label_precision')}",
            f"- Accepted rescue correct: {summary.get('accepted_rescue_correct', 0)}",
            f"- Accepted action regressions: {summary.get('accepted_action_regressions', 0)}",
            f"- Accepted boundary demotions: {summary.get('accepted_boundary_demotions', 0)}",
            f"- Fallback rate: {summary.get('fallback_rate', 0.0)}",
            f"- Accepted action counts: `{summary.get('accepted_action_counts', {})}`",
            f"- Blocked reasons: `{summary.get('blocked_reasons', {})}`",
        ],
        row_table_header=(
            "| Row | Direct | Critic proposed | Final | Accepted action | "
            "Reference | Gold | Purist | Direct Purist | Reference Purist | Notes |"
        ),
        row_table_rows=[_report_row_line(row) for row in rows],
        row_table_separator=(
            "| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"
        ),
    )
    write_stage_markdown_report(path, lines)


def _report_row_line(row: Mapping[str, Any]) -> str:
    comparison = dict(row.get("comparison") or {})
    direct_comparison = dict(row.get("direct_comparison") or {})
    reference_comparison = dict(row.get("reference_comparison") or {})
    notes = _row_notes(row)
    return (
        f"| {row.get('source_row_index')} | `{row.get('direct_label')}` | "
        f"`{row.get('raw_critic_proposed_label')}` | `{row.get('final_label')}` | "
        f"`{row.get('accepted_action')}` | `{row.get('reference_label')}` | "
        f"`{dict(row.get('reference') or {}).get('gold_label')}` | "
        f"{'yes' if comparison.get('purist_correct') else 'no'} | "
        f"{'yes' if direct_comparison.get('purist_correct') else 'no'} | "
        f"{'yes' if reference_comparison.get('purist_correct') else 'no'} | "
        f"{notes} |"
    )


def parse_critic_decision_json(
    raw_output: str,
) -> tuple[BoundaryCriticDecisionRecord | None, list[str]]:
    parsed = CRITIC_STAGE.parse_response(raw_output)
    if parsed.decision is None:
        return None, parsed.parse_errors
    return parsed.decision, parsed.parse_errors


def _build_row(
    record: GanFrequencyRecord,
    *,
    reference_label: str | None,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only", "reuse"],
    reuse_direct_raw_output: str | None,
    reuse_critic_raw_output: str | None,
) -> dict[str, Any]:
    guide_results = _fixed_boundary_guides()
    direct_call = _execute_direct_call(
        record,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        reuse_raw_output=reuse_direct_raw_output,
    )
    critic_call = _execute_critic_call(
        record,
        direct_call=direct_call,
        guide_results=guide_results,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        reuse_raw_output=reuse_critic_raw_output,
    )
    direct_decision = _direct_decision_from_call(direct_call)
    critic_decision = _critic_decision_from_call(critic_call)
    action_policy = apply_action_policy(record, direct_decision, critic_decision)
    final_label = action_policy["final_label"]
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": mode,
        "condition": CONDITION,
        "reference_condition": REFERENCE_CONDITION,
        "reference_label": reference_label,
        "reference_comparison": _compare_label_to_gold(record, reference_label),
        "direct_call": direct_call,
        "critic_call": critic_call,
        "tool_calls": [
            {
                "tool_name": "read_boundary_guide",
                "status": "context_included",
                "result": guide_result,
                "attribution": "fixed_split_neutral_guidance_retrieval",
            }
            for guide_result in guide_results
        ],
        "direct_label": direct_decision.final_label if direct_decision else None,
        "raw_critic_proposed_label": (
            critic_decision.proposed_final_label if critic_decision else None
        ),
        "final_label": final_label,
        "accepted_action": action_policy["accepted_action"],
        "action_policy": action_policy,
        "direct_comparison": _compare_label_to_gold(
            record,
            direct_decision.final_label if direct_decision else None,
        ),
        "raw_critic_proposed_comparison": _compare_label_to_gold(
            record,
            critic_decision.proposed_final_label if critic_decision else None,
        ),
        "comparison": _compare_label_to_gold(record, final_label),
        "reference": {
            "gold_label": record.gold_label,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "row_ok": record.row_ok,
        },
        "parser_context_disabled": True,
        "fixed_boundary_guide_ids": list(FIXED_BOUNDARY_GUIDE_IDS),
        "attribution_layer": action_policy["changed_label_attribution"],
    }


def _execute_direct_call(
    record: GanFrequencyRecord,
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only", "reuse"],
    reuse_raw_output: str | None,
) -> dict[str, Any]:
    prompt_input_json = DIRECT_STAGE.build_prompt_input(record)
    raw_output = reuse_raw_output or ""
    call_error: str | None = None
    if mode == "live" and not raw_output:
        try:
            raw_output = _run_model_call(
                prompt_input_json,
                call_role=DIRECT_CALL_ROLE,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - live transport only.
            call_error = f"{type(exc).__name__}: {exc}"
    parsed = (
        DIRECT_STAGE.parse_response(raw_output) if raw_output else ParsedStageResponse(None, ["not_run"])
    )
    decision = parsed.decision
    parse_errors = parsed.parse_errors
    evidence_valid = (
        evidence_is_substring(record.note_text, decision.evidence)
        if decision and decision.evidence
        else False
    )
    return {
        "call_index": 1,
        "call_role": DIRECT_CALL_ROLE,
        "model": model,
        "temperature": temperature,
        "prompt_version": PROMPT_VERSION,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "reused_raw_output": bool(reuse_raw_output),
        "raw_model_final_label": _extract_raw_label_from_direct_output(raw_output)
        if raw_output
        else None,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "decision_record": decision.model_dump() if decision else None,
        "evidence_valid": evidence_valid,
        "attribution": "raw_direct_model" if decision else "no_prediction",
    }


def _execute_critic_call(
    record: GanFrequencyRecord,
    *,
    direct_call: Mapping[str, Any],
    guide_results: Sequence[Mapping[str, Any]],
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only", "reuse"],
    reuse_raw_output: str | None,
) -> dict[str, Any]:
    prompt_input_json = CRITIC_STAGE.build_prompt_input(
        record,
        direct_call=direct_call,
        guide_results=guide_results,
    )
    raw_output = reuse_raw_output or ""
    call_error: str | None = None
    if mode == "live" and not raw_output:
        try:
            raw_output = _run_model_call(
                prompt_input_json,
                call_role=CRITIC_CALL_ROLE,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - live transport only.
            call_error = f"{type(exc).__name__}: {exc}"
    parsed = (
        CRITIC_STAGE.parse_response(raw_output) if raw_output else ParsedStageResponse(None, ["not_run"])
    )
    decision = parsed.decision
    parse_errors = parsed.parse_errors
    evidence_valid = (
        evidence_is_substring(record.note_text, decision.evidence)
        if decision and decision.evidence
        else False
    )
    return {
        "call_index": 2,
        "call_role": CRITIC_CALL_ROLE,
        "model": model,
        "temperature": temperature,
        "prompt_version": PROMPT_VERSION,
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "reused_raw_output": bool(reuse_raw_output),
        "raw_critic_proposed_label": _extract_raw_critic_proposed_label(raw_output)
        if raw_output
        else None,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "decision_record": decision.model_dump() if decision else None,
        "evidence_valid": evidence_valid,
        "attribution": "raw_boundary_critic_model" if decision else "no_prediction",
    }


def _run_model_call(
    prompt_input_json: str,
    *,
    call_role: str,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    del model, temperature, max_tokens
    if call_role == DIRECT_CALL_ROLE:
        prediction = DspyDirectDecisionCaller()(prompt_input_json=prompt_input_json)
        return str(prediction.decision_json)
    if call_role == CRITIC_CALL_ROLE:
        prediction = DspyBoundaryCriticCaller()(prompt_input_json=prompt_input_json)
        return str(prediction.critic_json)
    raise ValueError(f"Unknown D2 call_role: {call_role}")


def _build_direct_prompt_input(record: GanFrequencyRecord) -> str:
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency D2 direct no-tool extraction",
        "condition": CONDITION,
        "call_role": DIRECT_CALL_ROLE,
        "instructions": [
            "Read the clinical note and extract the current seizure-frequency answer.",
            "Return exactly one strict JSON object with no markdown.",
            (
                "final_label must be a normalized Gan-style seizure-frequency label, "
                "a seizure-free duration, unknown, or no seizure frequency reference."
            ),
            (
                "Use unknown when seizure-frequency evidence exists but cannot be "
                "converted; use no seizure frequency reference only when no usable "
                "frequency evidence exists."
            ),
            (
                "Prefer current frequency-bearing evidence over seizure-free or "
                "historical statements when both are present."
            ),
            (
                "When multiple current semiologies have different burdens, select "
                "the higher current burden."
            ),
            (
                "For recurring clusters, preserve cluster cadence and events-per-cluster "
                "burden when the note states both."
            ),
            (
                "Write frequency labels with spaces, not underscores: use "
                "'multiple per day' rather than 'multiple_per_day'."
            ),
            "Evidence should be copied as an exact source substring when possible.",
            (
                "Do not mention gold labels, split membership, row-level scoring, "
                "or benchmark answers."
            ),
        ],
        "required_output_fields": [
            "final_label",
            "evidence",
            "answer_kind",
            "selected_seizure_type",
            "time_window",
            "confidence",
            "rationale",
        ],
        "allowed_answer_kind_values": [
            "frequency",
            "seizure_free",
            "unknown",
            "no_reference",
            "unresolved_multiple",
        ],
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _build_critic_prompt_input(
    record: GanFrequencyRecord,
    *,
    direct_call: Mapping[str, Any],
    guide_results: Sequence[Mapping[str, Any]],
) -> str:
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency D2 boundary critic rescue-only action",
        "condition": CONDITION,
        "call_role": CRITIC_CALL_ROLE,
        "instructions": [
            "Read the clinical note, the direct answer, and the boundary guides.",
            "Emit exactly one action: keep, restore_cluster_burden, raise_current_burden, "
            "block_boundary_demotion, or abstain.",
            "This critic is rescue-only. It is not a replacement final-labeler.",
            (
                "Use restore_cluster_burden only when the note states both cluster cadence "
                "and events-per-cluster burden."
            ),
            (
                "Use raise_current_burden only when the note states a current "
                "higher-burden frequency-bearing event than the direct answer selected."
            ),
            (
                "Use block_boundary_demotion when seizure-free, unknown, or no-reference "
                "would erase a frequency-bearing direct answer."
            ),
            (
                "Do not introduce seizure-free, unknown, or no seizure frequency reference "
                "as an override in this v1 critic."
            ),
            (
                "If no conservative rescue is justified, use keep or abstain and leave "
                "proposed_final_label as null."
            ),
            "Return exactly one strict JSON object with no markdown.",
            "Copy evidence fields as exact source substrings when possible.",
            "Do not mention gold labels, split membership, row-level scoring, or row ids.",
        ],
        "required_output_fields": [
            "action",
            "proposed_final_label",
            "evidence",
            "cluster_cadence_evidence",
            "events_per_cluster_evidence",
            "higher_current_burden_evidence",
            "boundary_demotion_hazard",
            "confidence",
            "rationale",
        ],
        "allowed_action_values": [
            "keep",
            "restore_cluster_burden",
            "raise_current_burden",
            "block_boundary_demotion",
            "abstain",
        ],
        "note_text": record.note_text,
        "tool_context": {
            "direct_answer": {
                "decision_record": direct_call.get("decision_record"),
                "raw_model_final_label": direct_call.get("raw_model_final_label"),
                "parse_errors": direct_call.get("parse_errors"),
            },
            "boundary_guides": list(guide_results),
            "tool_attribution_boundary": (
                "Boundary guides are fixed split-neutral retrieval context. "
                "No parser candidates, parser-derived guide selection, gold labels, "
                "or row-family tags are included."
            ),
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _apply_restore_cluster_policy(
    record: GanFrequencyRecord,
    direct_label: str,
    critic_decision: BoundaryCriticDecisionRecord,
) -> dict[str, Any]:
    proposed_label = str(critic_decision.proposed_final_label)
    if not _has_cluster_burden(proposed_label):
        return _blocked(direct_label, "proposed_label_not_cluster_burden")
    if _has_cluster_burden(direct_label):
        return _blocked(direct_label, "direct_already_has_cluster_burden")
    if not (
        _evidence_text_present(record, critic_decision.cluster_cadence_evidence)
        and _evidence_text_present(record, critic_decision.events_per_cluster_evidence)
    ):
        return _blocked(direct_label, "missing_cluster_cadence_or_burden_evidence")
    return _accepted(proposed_label, "restore_cluster_burden")


def _apply_raise_burden_policy(
    record: GanFrequencyRecord,
    direct_label: str,
    critic_decision: BoundaryCriticDecisionRecord,
) -> dict[str, Any]:
    proposed_label = str(critic_decision.proposed_final_label)
    if not (
        _is_frequency_or_cluster_label(direct_label)
        and _is_frequency_or_cluster_label(proposed_label)
    ):
        return _blocked(direct_label, "raise_burden_requires_frequency_labels")
    if not _evidence_text_present(record, critic_decision.higher_current_burden_evidence):
        return _blocked(direct_label, "missing_higher_current_burden_evidence")
    if _monthly_frequency(proposed_label) <= _monthly_frequency(direct_label):
        return _blocked(direct_label, "proposed_burden_not_strictly_higher")
    return _accepted(proposed_label, "raise_current_burden")


def _accepted(final_label: str, action: str) -> dict[str, Any]:
    return {
        "final_label": final_label,
        "accepted_action": action,
        "blocked_reason": None,
        "changed_label_attribution": "boundary_critic_model_plus_deterministic_gate",
    }


def _blocked(final_label: str, reason: str) -> dict[str, Any]:
    return {
        "final_label": final_label,
        "accepted_action": "fallback",
        "blocked_reason": reason,
        "changed_label_attribution": "direct_model",
    }


def _filter_critic_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    allowed = set(BoundaryCriticDecisionRecord.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def _repair_critic_payload_shape(payload: Any) -> tuple[Any, list[str]]:
    """Coerce critic audit fields without changing action or label semantics."""

    if not isinstance(payload, dict):
        return payload, []
    repaired = dict(payload)
    notes: list[str] = []
    optional_text_fields = (
        "proposed_final_label",
        "cluster_cadence_evidence",
        "events_per_cluster_evidence",
        "higher_current_burden_evidence",
        "boundary_demotion_hazard",
    )
    for field_name in optional_text_fields:
        value = repaired.get(field_name)
        if value == "":
            repaired[field_name] = None
            notes.append(f"critic_field_shape_repaired:{field_name}")
        elif value is not None and not isinstance(value, str):
            repaired[field_name] = _stringify_critic_value(value)
            notes.append(f"critic_field_shape_repaired:{field_name}")
    evidence = repaired.get("evidence")
    if evidence is None:
        repaired["evidence"] = ""
        notes.append("critic_field_shape_repaired:evidence")
    elif not isinstance(evidence, str):
        repaired["evidence"] = _stringify_critic_value(evidence)
        notes.append("critic_field_shape_repaired:evidence")
    confidence = repaired.get("confidence")
    if isinstance(confidence, int | float) and not isinstance(confidence, bool):
        repaired["confidence"] = _confidence_from_number(float(confidence))
        notes.append("critic_field_shape_repaired:confidence")
    elif confidence not in {None, "low", "medium", "high"}:
        repaired["confidence"] = str(confidence).strip().lower()
        notes.append("critic_field_shape_repaired:confidence")
    return repaired, notes


def _confidence_from_number(value: float) -> Literal["low", "medium", "high"]:
    if value >= 0.75:
        return "high"
    if value >= 0.4:
        return "medium"
    return "low"


def _stringify_critic_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return str(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _fixed_boundary_guides() -> list[dict[str, Any]]:
    return [
        read_boundary_guide(guide_id).model_dump(mode="json")
        for guide_id in FIXED_BOUNDARY_GUIDE_IDS
    ]


def _direct_decision_from_call(call: Mapping[str, Any]) -> DirectDecisionRecord | None:
    payload = call.get("decision_record")
    if payload is None:
        return None
    return DirectDecisionRecord.model_validate(payload)


def _critic_decision_from_call(
    call: Mapping[str, Any],
) -> BoundaryCriticDecisionRecord | None:
    payload = call.get("decision_record")
    if payload is None:
        return None
    return BoundaryCriticDecisionRecord.model_validate(payload)


def _compare_label_to_gold(
    record: GanFrequencyRecord,
    label: str | None,
) -> dict[str, Any]:
    if label is None:
        return {
            "predicted_monthly_frequency": None,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "predicted_purist_category": None,
            "gold_purist_category": str(map_purist(record.gold_monthly_frequency)),
            "purist_correct": False,
            "predicted_pragmatic_category": None,
            "gold_pragmatic_category": str(map_pragmatic(record.gold_monthly_frequency)),
            "pragmatic_correct": False,
        }
    try:
        predicted_record = label_to_frequency_record(str(label))
    except ValueError:
        return {
            "predicted_monthly_frequency": None,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "predicted_purist_category": None,
            "gold_purist_category": str(map_purist(record.gold_monthly_frequency)),
            "purist_correct": False,
            "predicted_pragmatic_category": None,
            "gold_pragmatic_category": str(map_pragmatic(record.gold_monthly_frequency)),
            "pragmatic_correct": False,
        }
    predicted_monthly = predicted_record.monthly_frequency
    return {
        "predicted_monthly_frequency": predicted_monthly,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "predicted_purist_category": str(map_purist(predicted_monthly)),
        "gold_purist_category": str(map_purist(record.gold_monthly_frequency)),
        "purist_correct": map_purist(predicted_monthly)
        == map_purist(record.gold_monthly_frequency),
        "predicted_pragmatic_category": str(map_pragmatic(predicted_monthly)),
        "gold_pragmatic_category": str(map_pragmatic(record.gold_monthly_frequency)),
        "pragmatic_correct": map_pragmatic(predicted_monthly)
        == map_pragmatic(record.gold_monthly_frequency),
    }


def _reference_labels(reference_rows: Sequence[Mapping[str, Any]]) -> dict[int, str]:
    labels: dict[int, str] = {}
    for row in reference_rows:
        source_row_index = row.get("source_row_index")
        if source_row_index is None:
            continue
        trace = dict(
            dict(row.get("condition_traces") or {}).get(REFERENCE_CONDITION) or {}
        )
        label = trace.get("final_label")
        if label is not None:
            labels[int(source_row_index)] = str(label)
    return labels


def _extract_raw_label_from_direct_output(raw_output: str) -> str | None:
    try:
        payload, _dialect_notes = parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except Exception:
        return None
    repaired_payload = repair_decision_payload(payload)
    if not isinstance(repaired_payload, Mapping):
        return None
    final_label = repaired_payload.get("final_label")
    return str(final_label) if final_label is not None else None


def _extract_raw_critic_proposed_label(raw_output: str) -> str | None:
    try:
        payload, _dialect_notes = parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except Exception:
        return None
    repaired_payload = repair_decision_payload(payload)
    if not isinstance(repaired_payload, Mapping):
        return None
    final_label = repaired_payload.get("proposed_final_label")
    return str(final_label) if final_label is not None else None


def _label_kind(label: str | None) -> str:
    if label is None:
        return "no_prediction"
    try:
        return str(label_to_frequency_record(str(label)).kind)
    except ValueError:
        return "unparseable"


def _normalized_label(label: str | None) -> str | None:
    if label is None:
        return None
    try:
        return str(label_to_frequency_record(str(label)).normalized_label)
    except ValueError:
        return " ".join(str(label).strip().lower().split())


def _has_cluster_burden(label: str | None) -> bool:
    if label is None:
        return False
    normalized = " ".join(str(label).strip().lower().split())
    return "cluster" in normalized and "per cluster" in normalized


def _is_frequency_or_cluster_label(label: str | None) -> bool:
    if _has_cluster_burden(label):
        return True
    return _label_kind(label) == "frequency"


def _monthly_frequency(label: str) -> float:
    return float(label_to_frequency_record(label).monthly_frequency)


def _evidence_text_present(record: GanFrequencyRecord, evidence_text: str | None) -> bool:
    return bool(evidence_text and evidence_is_substring(record.note_text, evidence_text))


def _metadata(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    dspy_cache: bool,
    api_base: str | None,
) -> dict[str, Any]:
    return build_stage_metadata(
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
            "artifact_kind": "gan2026_agentic_direct_boundary_critic_rescue_panel",
            "pipeline_family": "agentic_direct_boundary_critic_rescue",
            "pipeline_version": "gan2026_agentic_d2_direct_boundary_critic_rescue_v1",
            "panel_source_row_indices": list(PANEL_SOURCE_ROW_INDICES),
            "fixed_boundary_guide_ids": list(FIXED_BOUNDARY_GUIDE_IDS),
            "claim_boundary": (
                "validation-development D2 micro-panel only; direct no-tool answer "
                "plus boundary critic, parser candidates disabled as prompt context, "
                "no holdout use, no row-level test inspection, and no benchmark claim"
            ),
        },
    )


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    surface = metadata.get("surface", "panel")
    emit_progress_checkpoint(
        rows,
        metadata,
        total=total,
        summarize_rows=summarize_rows,
        gate_interpretation=lambda summary: gate_interpretation(
            summary,
            surface="hard50" if surface == "hard50" else "panel",
        ),
        jsonl_path=jsonl_path,
        report_path=report_path,
        write_report=write_report,
        progress_fields=(
            "call_failures",
            "parse_or_validation_failures",
            "purist_correct",
            "accepted_rescue_correct",
        ),
    )


def _filter_records_by_source_indices(
    records: Sequence[GanFrequencyRecord],
    source_row_indices: Sequence[int],
) -> list[GanFrequencyRecord]:
    by_index = {record.source_row_index: record for record in records}
    missing = [index for index in source_row_indices if index not in by_index]
    if missing:
        raise ValueError(f"source_row_index values not present in split: {missing[:10]}")
    return [by_index[index] for index in source_row_indices]


def _load_hard50_indices(path: Path) -> list[int]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [int(index) for index in payload["source_row_indices"]]


def _raw_outputs_by_source_index(path: Path) -> dict[int, dict[str, str]]:
    rows = load_jsonl_rows(path)
    outputs: dict[int, dict[str, str]] = {}
    for row in rows:
        source_row_index = row.get("source_row_index")
        if source_row_index is None:
            continue
        direct_raw = dict(row.get("direct_call") or {}).get("raw_output")
        critic_raw = dict(row.get("critic_call") or {}).get("raw_output")
        row_outputs: dict[str, str] = {}
        if direct_raw:
            row_outputs["direct"] = str(direct_raw)
        if critic_raw:
            row_outputs["critic"] = str(critic_raw)
        if row_outputs:
            outputs[int(source_row_index)] = row_outputs
    return outputs


def _row_notes(row: Mapping[str, Any]) -> str:
    notes: list[str] = []
    direct_call = dict(row.get("direct_call") or {})
    critic_call = dict(row.get("critic_call") or {})
    notes.extend(f"direct:{error}" for error in direct_call.get("parse_errors") or [])
    notes.extend(f"critic:{error}" for error in critic_call.get("parse_errors") or [])
    if direct_call.get("call_error"):
        notes.append(f"direct:{direct_call['call_error']}")
    if critic_call.get("call_error"):
        notes.append(f"critic:{critic_call['call_error']}")
    blocked_reason = dict(row.get("action_policy") or {}).get("blocked_reason")
    if blocked_reason:
        notes.append(str(blocked_reason))
    if not direct_call.get("evidence_valid"):
        notes.append("direct_evidence_not_exact")
    if not critic_call.get("evidence_valid"):
        notes.append("critic_evidence_not_exact")
    return "; ".join(notes)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run D2 direct-plus-boundary-critic rescue on panel or hard50."
    )
    parser.add_argument("--reference-jsonl", type=Path, required=True)
    parser.add_argument("--jsonl", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--surface", choices=("panel", "hard50"), default="panel")
    parser.add_argument("--manifest-json", type=Path, default=None)
    parser.add_argument("--split", choices=("validation", "train", "test"), default="validation")
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--api-base", default=None)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--mode", choices=("live", "prompt-only", "reuse"), default="live")
    parser.add_argument("--reuse-jsonl", type=Path, default=None)
    parser.add_argument("--disable-dspy-cache", action="store_true")
    parser.add_argument("--progress-every", type=int, default=3)
    parser.add_argument("--overwrite-existing", action="store_true")
    args = parser.parse_args(argv)
    if not args.overwrite_existing:
        existing = [path for path in (args.jsonl, args.markdown) if path.exists()]
        if existing:
            parser.error(
                "output artifact already exists; use --overwrite-existing to replace: "
                + ", ".join(str(path) for path in existing)
            )
    if args.surface == "hard50" and args.manifest_json is None:
        parser.error("--manifest-json is required for --surface hard50")
    source_row_indices = (
        _load_hard50_indices(args.manifest_json)
        if args.surface == "hard50"
        else list(PANEL_SOURCE_ROW_INDICES)
    )
    records = _filter_records_by_source_indices(
        load_records_for_split(args.split),
        source_row_indices,
    )
    manifest = load_split_manifest()
    split_manifest = str(manifest.get("manifest_version", "gan2026_split_v1"))
    rows, metadata = run_split(
        records,
        reference_rows=load_jsonl_rows(args.reference_jsonl),
        split=args.split,
        split_manifest=split_manifest,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        mode=args.mode,
        dspy_cache=not args.disable_dspy_cache,
        api_base=args.api_base,
        reuse_raw_outputs=_raw_outputs_by_source_index(args.reuse_jsonl)
        if args.reuse_jsonl
        else None,
        reuse_source=str(args.reuse_jsonl) if args.reuse_jsonl else None,
        progress_every=args.progress_every if args.progress_every > 0 else None,
        checkpoint_jsonl_path=args.jsonl,
        checkpoint_report_path=args.markdown,
        surface=args.surface,
    )
    metadata["reference_jsonl_path"] = str(args.reference_jsonl)
    if args.manifest_json is not None:
        metadata["hard50_manifest_path"] = str(args.manifest_json)
    write_jsonl(rows, args.jsonl)
    write_report(rows, metadata, args.markdown, jsonl_path=args.jsonl)
    print(json.dumps(metadata["gate"], sort_keys=True))


if __name__ == "__main__":
    main()
