"""D1 boundary-audit prompt v2 panel for Gan 2026 agentic hard-slice work.

Migrated to :mod:`stage_protocol` (prompt builder + decision schema + postprocess policy
+ thin ``run_split``).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.stage_protocol import (
    AgenticStage,
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

PROMPT_VERSION = "gan2026_agentic_boundary_audit_prompt_v2"
CONDITION = "boundary_audit_prompt_v2"
REFERENCE_CONDITION = "single_self_consistency_temperature"
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
E2_LOSS_SENTINELS = {5534, 6131}
FIXED_BOUNDARY_GUIDE_IDS: tuple[str, ...] = (
    "multiple_current_events_aggregation",
    "seizure_free_event_conflict",
    "cluster_frequency_vs_incidental_clustering",
    "unknown_frequency_vs_no_reference",
    "current_vs_historical_window",
    "different_semiology_burdens",
)


class BoundaryAuditDecisionRecord(BaseModel):
    """Structured D1 audit plus one Gan-compatible final label."""

    model_config = ConfigDict(extra="forbid")

    current_frequency_evidence: list[str] = Field(default_factory=list)
    active_semiologies_and_burdens: list[str] = Field(default_factory=list)
    cluster_cadence_and_burden: str | None = None
    boundary_hazards: list[str] = Field(default_factory=list)
    rejected_lower_burden_or_historical_alternatives: list[str] = Field(default_factory=list)
    final_label: str
    evidence: str
    answer_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    selected_seizure_type: str | None = None
    time_window: str | None = None
    confidence: Literal["low", "medium", "high"]
    rationale: str


class BoundaryAuditStage(AgenticStage[BoundaryAuditDecisionRecord]):
    """D1 boundary-audit prompt builder + parse/postprocess policy."""

    @property
    def prompt_version(self) -> str:
        return PROMPT_VERSION

    def build_prompt_input(
        self,
        record: GanFrequencyRecord,
        *,
        guide_results: Sequence[Mapping[str, Any]] | None = None,
        **_: object,
    ) -> str:
        guides = list(guide_results) if guide_results is not None else _fixed_boundary_guides()
        return _build_prompt_input(record, guide_results=guides)

    def parse_response(
        self,
        raw_output: str,
        **_: object,
    ) -> ParsedStageResponse[BoundaryAuditDecisionRecord]:
        parsed = parse_response(
            raw_output,
            decision_model=BoundaryAuditDecisionRecord,
            payload_filter=_filter_audit_payload,
            shape_repair=_repair_audit_payload_shape,
            label_repair="with_evidence",
            evidence_field="evidence",
            require_scorable_label=True,
        )
        return parsed


STAGE = BoundaryAuditStage()


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
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    surface: Literal["panel", "hard50"] = "panel",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run D1 over the predeclared validation micro-panel."""

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
        metadata["artifact_kind"] = "gan2026_agentic_boundary_audit_prompt_v2_hard50"
        metadata["claim_boundary"] = (
            "validation-development D1 hard50 only; parser candidates disabled "
            "as prompt context, no holdout use, no row-level test inspection, "
            "and no benchmark claim"
        )
    rows: list[dict[str, Any]] = []
    for record in records:
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
                reuse_raw_output=reuse_raw_outputs.get(record.source_row_index),
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
    wins = 0
    losses = 0
    call_failures = 0
    reused_raw_outputs = 0
    decision_records = 0
    parse_failures = 0
    schema_or_label_repairs = 0
    evidence_exact = 0
    boundary_demotion_count = 0
    sentinel_regressions = 0
    cluster_burden_preserved = 0
    changed_labels = 0
    raw_final_labels = Counter()
    final_labels = Counter()
    for row in rows:
        comparison = dict(row.get("comparison") or {})
        reference_comparison = dict(row.get("reference_comparison") or {})
        purist_correct += int(bool(comparison.get("purist_correct")))
        pragmatic_correct += int(bool(comparison.get("pragmatic_correct")))
        wins += int(
            bool(comparison.get("purist_correct"))
            and not bool(reference_comparison.get("purist_correct"))
        )
        losses += int(
            bool(reference_comparison.get("purist_correct"))
            and not bool(comparison.get("purist_correct"))
        )
        call_failures += int(row.get("call_error") is not None)
        reused_raw_outputs += int(bool(row.get("reused_raw_output")))
        decision_records += int(row.get("decision_record") is not None)
        parse_failures += int(has_blocking_parse_issue(row.get("parse_errors")))
        schema_or_label_repairs += int(has_repair_note(row.get("parse_errors")))
        evidence_exact += int(bool(row.get("evidence_valid")))
        boundary_demotion_count += int(
            _introduces_boundary_demotion(
                dict(row.get("decision_record") or {}).get("final_label"),
                row.get("reference_label"),
            )
        )
        changed_labels += int(
            _normalized_label(dict(row.get("decision_record") or {}).get("final_label"))
            != _normalized_label(row.get("reference_label"))
        )
        sentinel_regressions += int(
            int(row["source_row_index"]) in E2_LOSS_SENTINELS
            and bool(reference_comparison.get("purist_correct"))
            and not bool(comparison.get("purist_correct"))
        )
        cluster_burden_preserved += int(
            _has_cluster_burden(dict(row.get("decision_record") or {}).get("final_label"))
            and _has_cluster_burden(dict(row.get("reference") or {}).get("gold_label"))
        )
        raw_label = row.get("raw_model_final_label")
        if raw_label is not None:
            raw_final_labels[str(raw_label)] += 1
        decision_label = dict(row.get("decision_record") or {}).get("final_label")
        if decision_label is not None:
            final_labels[str(decision_label)] += 1
    return {
        "rows": len(rows),
        "condition": CONDITION,
        "reference_condition": REFERENCE_CONDITION,
        "model_calls_attempted": len(rows),
        "decision_records": decision_records,
        "call_failures": call_failures,
        "reused_raw_outputs": reused_raw_outputs,
        "parse_or_validation_failures": parse_failures,
        "schema_or_label_repair_rows": schema_or_label_repairs,
        "evidence_exact_substrings": evidence_exact,
        "purist_correct": purist_correct,
        "pragmatic_correct": pragmatic_correct,
        "wins_vs_reference": wins,
        "losses_vs_reference": losses,
        "changed_labels_vs_reference": changed_labels,
        "changed_label_precision": round(wins / changed_labels, 4)
        if changed_labels
        else None,
        "boundary_demotion_count": boundary_demotion_count,
        "e2_loss_sentinel_regressions": sentinel_regressions,
        "cluster_burden_preservation_count": cluster_burden_preserved,
        "parser_context_disabled": True,
        "fixed_boundary_guide_ids": list(FIXED_BOUNDARY_GUIDE_IDS),
        "raw_model_final_labels": dict(sorted(raw_final_labels.items())),
        "final_labels": dict(sorted(final_labels.items())),
    }


def gate_interpretation(
    summary: Mapping[str, Any],
    *,
    surface: Literal["panel", "hard50"] = "panel",
) -> dict[str, Any]:
    purist = int(summary.get("purist_correct", 0))
    wins = int(summary.get("wins_vs_reference", 0))
    losses = int(summary.get("losses_vs_reference", 0))
    precision = summary.get("changed_label_precision")
    sentinel_regressions = int(summary.get("e2_loss_sentinel_regressions", 0))
    parse_failures = int(summary.get("parse_or_validation_failures", 0))
    parser_context_disabled = bool(summary.get("parser_context_disabled"))
    if surface == "hard50":
        passes_win_loss_gate = wins >= 5 and losses <= 1
        passes_precision_gate = (
            precision is not None and float(precision) >= 0.70 and losses <= 1
        )
        if (
            parse_failures == 0
            and parser_context_disabled
            and (passes_win_loss_gate or passes_precision_gate)
        ):
            status = "pass_hard50_gate"
            interpretation = (
                "Boundary audit prompt v2 passed the hard50 gate; it may be "
                "considered for the next D-series decision, without holdout or "
                "validation250 escalation by default."
            )
        else:
            status = "reject_or_revise_after_hard50"
            interpretation = (
                "Boundary audit prompt v2 did not satisfy the hard50 gate; do "
                "not escalate to validation250 or D3 from this condition."
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
            "parser_context_disabled": parser_context_disabled,
            "interpretation": interpretation,
        }
    if (
        purist >= 9
        and sentinel_regressions == 0
        and parse_failures == 0
        and parser_context_disabled
    ):
        status = "pass_panel_gate"
        interpretation = (
            "Boundary audit prompt v2 passed the predeclared micro-panel gate; "
            "hard50 is permitted as the next D1 surface."
        )
    else:
        status = "reject_or_revise_before_hard50"
        interpretation = (
            "Boundary audit prompt v2 did not satisfy the micro-panel gate; do "
            "not run D1 hard50 without revising or stopping the live branch."
        )
    return {
        "status": status,
        "surface": surface,
        "purist_correct": purist,
        "required_purist_correct": 9,
        "e2_loss_sentinel_regressions": sentinel_regressions,
        "parse_or_validation_failures": parse_failures,
        "parser_context_disabled": parser_context_disabled,
        "interpretation": interpretation,
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
        title=f"Gan 2026 Agentic Boundary Audit Prompt V2 {surface_label}",
        metadata=metadata,
        summary=summary,
        gate=gate,
        jsonl_path=jsonl_path,
        experiment_unit_lines=[
            f"- Work class: D1 validation {surface} boundary-audit prompt.",
            f"- Rows: {summary.get('rows', 0)}",
            f"- Condition: `{CONDITION}`",
            f"- Reference condition: `{REFERENCE_CONDITION}`",
            "- Split: `validation`, manifest `gan2026_split_v1`.",
            f"- Surface: predeclared D1 `{surface}`.",
            f"- Mode: `{metadata.get('mode')}`",
            f"- Model: `{metadata.get('model')}`",
            f"- Prompt version: `{metadata.get('prompt_version')}`",
            "- Parser context: disabled; fixed boundary-guide set used for every row.",
        ],
        summary_lines=[
            f"- Model calls attempted: {summary.get('model_calls_attempted', 0)}",
            f"- Decision records: {summary.get('decision_records', 0)}",
            f"- Call failures: {summary.get('call_failures', 0)}",
            f"- Reused raw outputs: {summary.get('reused_raw_outputs', 0)}",
            f"- Parse/schema/label failures: {summary.get('parse_or_validation_failures', 0)}",
            f"- Schema/label repair rows: {summary.get('schema_or_label_repair_rows', 0)}",
            f"- Exact evidence substrings: {summary.get('evidence_exact_substrings', 0)}",
            f"- Purist: {summary.get('purist_correct', 0)}/{summary.get('rows', 0)}",
            f"- Pragmatic: {summary.get('pragmatic_correct', 0)}/{summary.get('rows', 0)}",
            f"- Wins vs reference: {summary.get('wins_vs_reference', 0)}",
            f"- Losses vs reference: {summary.get('losses_vs_reference', 0)}",
            f"- Changed labels vs reference: {summary.get('changed_labels_vs_reference', 0)}",
            f"- Changed-label precision: {summary.get('changed_label_precision')}",
            f"- Boundary demotions: {summary.get('boundary_demotion_count', 0)}",
            (
                "- E2 loss sentinel regressions: "
                f"{summary.get('e2_loss_sentinel_regressions', 0)}"
            ),
            (
                "- Cluster-burden preservation count: "
                f"{summary.get('cluster_burden_preservation_count', 0)}"
            ),
        ],
        row_table_header=(
            "| Row | Final | Raw final | Reference | Gold | Purist | "
            "Reference Purist | Evidence exact | Notes |"
        ),
        row_table_rows=[_report_row_line(row) for row in rows],
    )
    write_stage_markdown_report(path, lines)


def _report_row_line(row: Mapping[str, Any]) -> str:
    comparison = dict(row.get("comparison") or {})
    reference_comparison = dict(row.get("reference_comparison") or {})
    decision = dict(row.get("decision_record") or {})
    notes = "; ".join(str(error) for error in row.get("parse_errors") or [])
    if row.get("call_error"):
        notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
    return (
        f"| {row.get('source_row_index')} | `{decision.get('final_label')}` | "
        f"`{row.get('raw_model_final_label')}` | `{row.get('reference_label')}` | "
        f"`{dict(row.get('reference') or {}).get('gold_label')}` | "
        f"{'yes' if comparison.get('purist_correct') else 'no'} | "
        f"{'yes' if reference_comparison.get('purist_correct') else 'no'} | "
        f"{'yes' if row.get('evidence_valid') else 'no'} | {notes} |"
    )


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
    reuse_raw_output: str | None,
) -> dict[str, Any]:
    guide_results = _fixed_boundary_guides()
    plan = {
        "call_index": 1,
        "call_role": CONDITION,
        "model": model,
        "temperature": temperature,
        "prompt_version": PROMPT_VERSION,
        "input_note_chars": len(record.note_text),
    }
    prompt_input_json = _build_prompt_input(record, guide_results=guide_results)
    raw_output = reuse_raw_output or ""
    call_error: str | None = None
    if mode == "live" and not raw_output:
        try:
            raw_output = _run_model_call(
                prompt_input_json,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - live transport only.
            call_error = f"{type(exc).__name__}: {exc}"
    decision, parse_errors = (
        parse_audit_decision_json(raw_output) if raw_output else (None, ["not_run"])
    )
    evidence_valid = (
        evidence_is_substring(record.note_text, decision.evidence)
        if decision and decision.evidence
        else False
    )
    return {
        "source_row_index": record.source_row_index,
        "split": split,
        "split_manifest": split_manifest,
        "artifact_mode": mode,
        "condition": CONDITION,
        "reference_condition": REFERENCE_CONDITION,
        "reference_label": reference_label,
        "reference_comparison": _compare_label_to_gold(record, reference_label),
        "model_call_plan": plan,
        "tool_calls": [
            {
                "tool_name": "read_boundary_guide",
                "status": "context_included",
                "result": guide_result,
                "attribution": "fixed_split_neutral_guidance_retrieval",
            }
            for guide_result in guide_results
        ],
        "prompt_input_json": prompt_input_json,
        "raw_output": raw_output,
        "reused_raw_output": bool(reuse_raw_output),
        "raw_model_final_label": _extract_raw_model_final_label(raw_output)
        if raw_output
        else None,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "decision_record": decision.model_dump() if decision else None,
        "evidence_valid": evidence_valid,
        "comparison": _compare_to_gold(record, decision) if decision else None,
        "reference": {
            "gold_label": record.gold_label,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "row_ok": record.row_ok,
        },
        "parser_context_disabled": True,
        "fixed_boundary_guide_ids": list(FIXED_BOUNDARY_GUIDE_IDS),
    }


def _build_prompt_input(
    record: GanFrequencyRecord,
    *,
    guide_results: Sequence[Mapping[str, Any]],
) -> str:
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency boundary audit prompt v2",
        "condition": CONDITION,
        "call_role": CONDITION,
        "instructions": [
            "Read the clinical note and extract the current seizure-frequency answer.",
            "Use the boundary guides only as split-neutral decision reminders.",
            "Do not infer from row ids, gold labels, split membership, or benchmark scoring.",
            "Return exactly one strict JSON object with no markdown.",
            "Before final_label, complete the requested audit fields.",
            (
                "current_frequency_evidence: list exact or near-exact phrases that "
                "support current frequency-bearing evidence."
            ),
            (
                "active_semiologies_and_burdens: list active seizure types and their "
                "relative current burdens when stated."
            ),
            (
                "cluster_cadence_and_burden: state cluster cadence and events per "
                "cluster if present; otherwise use null."
            ),
            (
                "boundary_hazards: list seizure-free, unknown, no-reference, negation, "
                "historical-window, or lower-burden hazards that could mislead selection."
            ),
            (
                "rejected_lower_burden_or_historical_alternatives: list alternatives "
                "you are explicitly not selecting."
            ),
            (
                "final_label must be a normalized Gan-style seizure-frequency label, "
                "a seizure-free duration, unknown, or no seizure frequency reference."
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
                "Do not introduce seizure-free, unknown, or no-reference over a "
                "frequency-bearing current answer in this v2 panel unless the note "
                "clearly lacks any usable current frequency-bearing evidence."
            ),
            (
                "Write frequency labels with spaces, not underscores: use "
                "'multiple per day' rather than 'multiple_per_day'."
            ),
            "Evidence should be copied as an exact source substring when possible.",
        ],
        "required_output_fields": [
            "current_frequency_evidence",
            "active_semiologies_and_burdens",
            "cluster_cadence_and_burden",
            "boundary_hazards",
            "rejected_lower_burden_or_historical_alternatives",
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
        "tool_context": {
            "boundary_guides": list(guide_results),
            "tool_attribution_boundary": (
                "Boundary guides are fixed split-neutral retrieval context. "
                "No parser candidates or parser-selected guide signal are included."
            ),
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


class BoundaryAuditSignature(dspy.Signature):
    """Extract one Gan 2026 seizure-frequency decision with a structured audit."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON prompt payload with one note and fixed boundary-guide context."
    )
    decision_json: str = dspy.OutputField(
        desc="Strict JSON object with audit fields plus final_label and evidence."
    )


class DspyBoundaryAuditCaller(dspy.Module):
    """DSPy caller for the D1 boundary-audit prompt."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(BoundaryAuditSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def _run_model_call(
    prompt_input_json: str,
    *,
    model: str,
    temperature: float,
    max_tokens: int,
) -> str:
    del model, temperature, max_tokens
    prediction = DspyBoundaryAuditCaller()(prompt_input_json=prompt_input_json)
    return str(prediction.decision_json)


def parse_audit_decision_json(
    raw_output: str,
) -> tuple[BoundaryAuditDecisionRecord | None, list[str]]:
    parsed = STAGE.parse_response(raw_output)
    if parsed.decision is None:
        return None, parsed.parse_errors
    return parsed.decision, parsed.parse_errors


def _filter_audit_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    allowed = set(BoundaryAuditDecisionRecord.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def _repair_audit_payload_shape(payload: Any) -> tuple[Any, list[str]]:
    """Coerce audit-only structure to strings without changing final label semantics."""

    if not isinstance(payload, dict):
        return payload, []
    repaired = dict(payload)
    notes: list[str] = []
    for field_name in (
        "current_frequency_evidence",
        "active_semiologies_and_burdens",
        "boundary_hazards",
        "rejected_lower_burden_or_historical_alternatives",
    ):
        value = repaired.get(field_name)
        normalized = _string_list(value)
        if normalized != value:
            repaired[field_name] = normalized
            notes.append(f"audit_field_shape_repaired:{field_name}")
    cluster_value = repaired.get("cluster_cadence_and_burden")
    if cluster_value is not None and not isinstance(cluster_value, str):
        repaired["cluster_cadence_and_burden"] = _stringify_audit_value(cluster_value)
        notes.append("audit_field_shape_repaired:cluster_cadence_and_burden")
    return repaired, notes


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [_stringify_audit_value(item) for item in value]
    return [_stringify_audit_value(value)]


def _stringify_audit_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _fixed_boundary_guides() -> list[dict[str, Any]]:
    return [
        read_boundary_guide(guide_id).model_dump(mode="json")
        for guide_id in FIXED_BOUNDARY_GUIDE_IDS
    ]


def _compare_to_gold(
    record: GanFrequencyRecord,
    decision: BoundaryAuditDecisionRecord,
) -> dict[str, Any]:
    return _compare_label_to_gold(record, decision.final_label)


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
    predicted_record = label_to_frequency_record(str(label))
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


def _extract_raw_model_final_label(raw_output: str) -> str | None:
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


def _introduces_boundary_demotion(
    candidate_label: str | None,
    reference_label: str | None,
) -> bool:
    return (
        _label_kind(candidate_label) in {"seizure_free", "unknown", "no_reference"}
        and _is_frequency_or_cluster_label(reference_label)
    )


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
            "artifact_kind": "gan2026_agentic_boundary_audit_prompt_v2_panel",
            "pipeline_family": "agentic_boundary_audit_prompt_v2",
            "pipeline_version": "gan2026_agentic_d1_boundary_audit_prompt_v2",
            "panel_source_row_indices": list(PANEL_SOURCE_ROW_INDICES),
            "e2_loss_sentinels": sorted(E2_LOSS_SENTINELS),
            "fixed_boundary_guide_ids": list(FIXED_BOUNDARY_GUIDE_IDS),
            "claim_boundary": (
                "validation-development D1 micro-panel only; parser candidates "
                "disabled as prompt context, no holdout use, no row-level test "
                "inspection, and no benchmark claim"
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


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run D1 boundary audit prompt v2 on panel or hard50."
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


def _raw_outputs_by_source_index(path: Path) -> dict[int, str]:
    rows = load_jsonl_rows(path)
    return {
        int(row["source_row_index"]): str(row.get("raw_output") or "")
        for row in rows
        if row.get("source_row_index") is not None and row.get("raw_output")
    }


if __name__ == "__main__":
    main()
