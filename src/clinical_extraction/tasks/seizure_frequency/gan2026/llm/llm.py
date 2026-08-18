"""LLM-only canonical-pipeline Gan 2026 seizure-frequency extraction experiments.

This is the "purest form" fully-LLM comparator named in the three-way
architecture comparison plan: a single-shot configuration that collapses
extract -> select -> normalize -> project -> render into one LLM call, with
the now-mature deterministic rule taxonomy (cluster-axis ambiguity,
seizure-free conflict, same-window additive frequency, and similar named
families) embedded as prompt instructions rather than pre/post processing.
It is the retained one-call LLM-only comparator alongside the retained
`hybrid_structured_events` path.

Because this architecture produces one free-text decision rather than a
`CandidateSet` with source ids, it reports a distinct evidence
text-containment metric (does the LLM's free-text evidence string appear in
the source note) rather than the formal `CandidateSet` source-id validity
rate the deterministic/hybrid configurations support.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_decision_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import prompt_llm_only
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    extract_json_object as _extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    has_blocking_parse_issue as _has_blocking_parse_issue,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    has_repair_note as _has_repair_note,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_only import (
    build_llm_only_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline.replay_io import (
    load_raw_outputs_by_source_index,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    llm_model_metadata_lines,
    write_markdown_report,
)

GAN_LLM_ONLY = "gan_llm_only"
PROMPT_VERSION_V0_8 = "gan2026_llm_only_canonical_pipeline_v0.8"
PROMPT_VERSION = GAN_LLM_ONLY
LLM_ONLY_AUTHORED_KEYS = prompt_llm_only.LLM_ONLY_AUTHORED_KEYS
ROW_TRACE_SCHEMA_VERSION = "gan2026.row_trace.v1"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_canonical_pipeline_validation_gpt41mini_2026-06-07.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_canonical_pipeline_validation_gpt41mini_2026-06-07.md"
)


class CanonicalLlmDecisionRecord(BaseModel):
    """Single-shot note-to-label decision for the canonical fully-LLM pipeline."""

    model_config = ConfigDict(extra="forbid")

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
    applied_rule_families: list[str]
    confidence: Literal["low", "medium", "high"]
    rationale: str


class Gan2026CanonicalLlmExtractorSignature(dspy.Signature):
    """Read a clinical note and decide the patient's current seizure frequency.

    Provide a complete answer that adheres to the instructions below.
    Return exactly one JSON object with these keys: final_label,
    evidence, answer_kind, selected_seizure_type, time_window,
    applied_rule_families, confidence, and rationale.
    """

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one clinical note, guidance on how to reason "
            "about tricky cases, and the fields your answer must contain."
        )
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object. final_label must already be your "
            "complete, final answer in plain form, such as '2 per month', "
            "'2 to 3 per week', 'multiple per day', '1 cluster per week', "
            "'2 to 3 per cluster', 'seizure free for 6 month', 'unknown', or "
            "'no seizure frequency reference'."
        )
    )


class DspyCanonicalLlmExtractor(dspy.Module):
    """DSPy single-shot extractor that owns the full extract-to-render chain."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026CanonicalLlmExtractorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the Gan LLM-only paper payload."""

    return build_llm_only_prompt_input(record)


def parse_decision_json(
    raw_output: str,
) -> tuple[CanonicalLlmDecisionRecord | None, list[str]]:
    decision, errors, _ = parse_decision_json_with_trace(raw_output)
    return decision, errors


def parse_decision_json_with_trace(
    raw_output: str,
) -> tuple[CanonicalLlmDecisionRecord | None, list[str], dict[str, Any]]:
    """Parse one model decision while retaining the pre-adapter prediction boundary."""

    errors: list[str] = []
    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
            _extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        errors = [f"invalid_json: {exc.msg}"]
        return None, errors, _llm_only_row_trace(
            model_decision=None,
            schema_payload_changed=False,
            format_events=errors,
            adapter_events=[],
        )
    errors.extend(dialect_notes)
    payload = _coerce_rationale_key_typo(raw_payload)
    payload = _filter_decision_payload(repair_decision_payload(payload))
    payload = _coerce_applied_rule_families(payload)
    schema_payload_changed = payload != raw_payload

    try:
        model_decision = CanonicalLlmDecisionRecord.model_validate(payload)
    except ValidationError as exc:
        errors.append(f"schema_validation_error: {exc.errors()[0]['msg']}")
        return None, errors, _llm_only_row_trace(
            model_decision=None,
            schema_payload_changed=schema_payload_changed,
            format_events=errors,
            adapter_events=[],
        )

    repaired_label = repair_prediction_label_with_evidence(
        model_decision.final_label,
        model_decision.evidence,
    )
    adapter_events: list[str] = []
    if repaired_label != model_decision.final_label:
        event = f"final_label_repaired: {model_decision.final_label!r} -> {repaired_label!r}"
        errors.append(event)
        adapter_events.append(event)
    decision = model_decision.model_copy(update={"final_label": repaired_label})

    try:
        label_to_frequency_record(decision.final_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")

    return decision, errors, _llm_only_row_trace(
        model_decision=model_decision,
        schema_payload_changed=schema_payload_changed,
        format_events=list(dialect_notes),
        adapter_events=adapter_events,
        scored_decision=decision,
    )


def _llm_only_row_trace(
    *,
    model_decision: CanonicalLlmDecisionRecord | None,
    schema_payload_changed: bool,
    format_events: Sequence[str],
    adapter_events: Sequence[str],
    scored_decision: CanonicalLlmDecisionRecord | None = None,
) -> dict[str, Any]:
    before_label = model_decision.final_label if model_decision else None
    final_decision = scored_decision or model_decision
    return {
        "schema_version": ROW_TRACE_SCHEMA_VERSION,
        "method": "llm_only",
        "model_prediction": {
            "raw_output_field": "raw_output",
            "record": model_decision.model_dump() if model_decision else None,
        },
        "format_repair": {
            "schema_payload_changed": schema_payload_changed,
            "events": list(format_events),
        },
        "deterministic_adapter": {
            "rule_category": "benchmark_format",
            "before_label": before_label,
            "after_label": final_decision.final_label if final_decision else None,
            "events": list(adapter_events),
        },
        "evidence_validation": None,
        "scoring": None,
    }


def _coerce_rationale_key_typo(payload: Any) -> Any:
    """Tolerate the observed local-model typo `ration` for the `rationale` field."""

    if not isinstance(payload, dict) or "rationale" in payload or "ration" not in payload:
        return payload
    repaired = dict(payload)
    repaired["rationale"] = repaired.pop("ration")
    return repaired


def _coerce_applied_rule_families(payload: Any) -> Any:
    """Tolerate a missing or scalar `applied_rule_families` field from the model."""

    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    families = repaired.get("applied_rule_families")
    if families is None:
        repaired["applied_rule_families"] = []
    elif isinstance(families, str):
        repaired["applied_rule_families"] = [families] if families else []
    return repaired


def _filter_decision_payload(payload: Any) -> Any:
    """Keep shared adjudicator repair fields out of canonical-pipeline validation."""

    if not isinstance(payload, dict):
        return payload
    allowed = set(CanonicalLlmDecisionRecord.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compatibility facade; prediction order lives in orchestration.llm."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.llm import (
        run_split as canonical_run_split,
    )

    return canonical_run_split(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        dspy_cache=dspy_cache,
        api_base=api_base,
        reuse_raw_outputs=reuse_raw_outputs,
        reuse_source=reuse_source,
        escalation_reason=escalation_reason,
        progress_every=progress_every,
        checkpoint_jsonl_path=checkpoint_jsonl_path,
        checkpoint_report_path=checkpoint_report_path,
    )


def _legacy_run_split(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    reuse_raw_outputs: Mapping[int, str] | None = None,
    reuse_source: str | None = None,
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reuse_raw_outputs = reuse_raw_outputs or {}
    metadata = _run_metadata(
        records,
        split=split,
        split_manifest=split_manifest,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode=mode,
        api_base=api_base,
    )
    metadata["dspy_cache"] = dspy_cache
    metadata["reuse_source"] = reuse_source
    metadata["escalation_reason"] = escalation_reason
    program = DspyCanonicalLlmExtractor()
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

    rows: list[dict[str, Any]] = []
    for record in records:
        prompt_input_json = build_prompt_input(record)
        raw_output = reuse_raw_outputs.get(record.source_row_index, "")
        call_error: str | None = None
        reused_raw_output = raw_output != ""
        if mode == "live" and not reused_raw_output:
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.decision_json)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"

        decision, parse_errors, row_trace = (
            parse_decision_json_with_trace(raw_output)
            if raw_output
            else (
                None,
                ["not_run"],
                _llm_only_row_trace(
                    model_decision=None,
                    schema_payload_changed=False,
                    format_events=["not_run"],
                    adapter_events=[],
                ),
            )
        )
        evidence_text_contained = (
            evidence_is_substring(record.note_text, decision.evidence)
            if decision and decision.evidence
            else False
        )
        comparison = _compare_to_gold(record, decision) if decision else None
        row_trace["evidence_validation"] = {
            "evidence": decision.evidence if decision else "",
            "exact_substring": evidence_text_contained,
        }
        row_trace["scoring"] = comparison
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "prompt_version": PROMPT_VERSION,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "reused_raw_output": reused_raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "decision_record": decision.model_dump() if decision else None,
                "evidence_text_contained": evidence_text_contained,
                "row_trace": row_trace,
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
                "comparison": comparison,
            }
        )
        if progress_every and len(rows) % progress_every == 0:
            _emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
            )

    metadata["summary"] = summarize_records(rows)
    return rows, metadata


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    metadata["summary"] = summarize_records(rows)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    progress = {
        "processed": len(rows),
        "total": total,
        "call_failures": metadata["summary"]["call_failures"],
        "parse_or_validation_failures": metadata["summary"]["parse_or_validation_failures"],
        "purist_accuracy_so_far": metadata["summary"]["purist_accuracy"],
        "pragmatic_accuracy_so_far": metadata["summary"]["pragmatic_accuracy"],
        "reused_raw_outputs": metadata["summary"]["reused_raw_outputs"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    decision_rows = [row for row in rows if row.get("decision_record")]
    call_failures = sum(bool(row.get("call_error")) for row in rows)
    reused_raw_outputs = sum(bool(row.get("reused_raw_output")) for row in rows)
    parse_failures = sum(_has_blocking_parse_issue(row.get("parse_errors")) for row in rows)
    repair_notes = sum(_has_repair_note(row.get("parse_errors")) for row in rows)
    purist_correct = sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in rows)
    pragmatic_correct = sum(
        bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in rows
    )
    evidence_text_contained = sum(bool(row.get("evidence_text_contained")) for row in rows)
    applied_rule_families = Counter(
        family
        for row in rows
        for family in (row.get("decision_record") or {}).get("applied_rule_families") or []
    )
    final_labels = Counter(
        row["decision_record"]["final_label"] for row in rows if row.get("decision_record")
    )
    return {
        "examples": len(rows),
        "decision_records": len(decision_rows),
        "call_failures": call_failures,
        "reused_raw_outputs": reused_raw_outputs,
        "parse_or_validation_failures": parse_failures,
        "repair_notes": repair_notes,
        "evidence_text_contained": evidence_text_contained,
        "evidence_text_containment_rate": (
            round(evidence_text_contained / len(rows), 4) if rows else 0.0
        ),
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
        "final_labels": dict(sorted(final_labels.items())),
        "applied_rule_family_counts": dict(sorted(applied_rule_families.items())),
    }


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def load_reusable_raw_outputs(path: Path) -> dict[int, str]:
    """Load reusable raw model outputs from a prior JSONL artifact."""

    return load_raw_outputs_by_source_index(path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata["summary"]
    is_holdout = metadata.get("split") == "test"
    title = (
        "# Gan 2026 LLM-Only Canonical-Pipeline Holdout Aggregate"
        if is_holdout
        else "# Gan 2026 LLM-Only Canonical-Pipeline Validation Run"
    )
    boundary = (
        "This is an aggregate-only locked-holdout result on `gan2026_split_v1`. "
        "No row-level result is included in this report."
        if is_holdout
        else (
            "This is a validation development result on `gan2026_split_v1`. It is not a "
            "final holdout or benchmark result."
        )
    )
    score_scope = "holdout" if is_holdout else "validation"
    lines = [
        title,
        "",
        f"Date: {metadata['date']}",
        "",
        boundary,
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: the 'purest form' fully-LLM comparator — a single DSPy call that "
        "collapses extract/select/normalize/project/render into one pass, with the "
        "now-mature deterministic/hybrid clinical-reasoning rule taxonomy embedded as "
        "prompt instructions rather than pre/post processing — can produce a directly "
        "scorable, fully rendered label without any deterministic normalization or "
        "projection stage downstream.",
        "",
        "Minimal change: add the `llm` runner alongside "
        "`hybrid_structured_events`. No "
        "deterministic `CandidateSet` is built or consumed; final_label is the model's "
        "directly rendered answer.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} rows.",
        (
            f"Rare full-validation reason: {metadata['escalation_reason']}"
            if metadata.get("escalation_reason")
            else "Rare full-validation reason: not applicable for this run size."
        ),
        "Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as "
        "a side-car.",
        "",
        "## Model And Prompt Metadata",
        "",
        *llm_model_metadata_lines(
            metadata,
            jsonl_path,
            model_role=(
                "LLM-only canonical-pipeline single-shot extract/select/normalize/"
                "project/render extractor"
            ),
            deterministic_rule_configuration=(
                "none as pre/post processing; the deterministic/hybrid rule taxonomy "
                "is embedded as prompt instructions only, and deterministic code is "
                "limited to label repair, evidence text-containment checking, and "
                "scoring."
            ),
            summary=summary,
        ),
        "",
        "## Summary",
        "",
        f"- Decision records: {summary['decision_records']} / {summary['examples']}",
        f"- Call failures: {summary['call_failures']}",
        f"- Parse/schema/label issues: {summary['parse_or_validation_failures']}",
        f"- Deterministic repair notes: {summary['repair_notes']}",
        (
            "- Evidence text-containment (free-text evidence found verbatim in note, "
            f"the comparator-appropriate metric in place of `CandidateSet` source-id "
            f"validity rate): {summary['evidence_text_contained']} / {summary['examples']} "
            f"({summary['evidence_text_containment_rate']:.4f})"
        ),
        f"- Purist {score_scope} accuracy/micro F1 proxy: {summary['purist_accuracy']:.4f} "
        f"({summary['purist_correct']} / {summary['examples']})",
        f"- Pragmatic {score_scope} accuracy/micro F1 proxy: {summary['pragmatic_accuracy']:.4f} "
        f"({summary['pragmatic_correct']} / {summary['examples']})",
        "",
        "## Applied Rule-Taxonomy Families (Self-Reported)",
        "",
        "These counts reflect which embedded rule-taxonomy families the model itself "
        "reported as shaping its answer (`applied_rule_families`); they are a prompt-"
        "compliance signal, not a verified trace.",
        "",
    ]
    if summary["applied_rule_family_counts"]:
        for family, count in summary["applied_rule_family_counts"].items():
            lines.append(f"- `{family}`: {count}")
    else:
        lines.append("- (none reported)")
    if is_holdout:
        write_markdown_report(path, lines)
        return
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| Row | Final | Gold | Purist | Notes |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        decision = row.get("decision_record") or {}
        comparison = row.get("comparison") or {}
        notes = "; ".join(row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        if not row.get("evidence_text_contained"):
            note = "evidence_not_text_contained"
            notes = f"{notes}; {note}" if notes else note
        lines.append(
            f"| {row['source_row_index']} | {decision.get('final_label', '')} | "
            f"{row['reference']['gold_label']} | "
            f"{'yes' if comparison.get('purist_correct') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


def _compare_to_gold(
    record: GanFrequencyRecord,
    decision: CanonicalLlmDecisionRecord,
) -> dict[str, Any]:
    try:
        predicted_record = label_to_frequency_record(decision.final_label)
    except ValueError:
        return {}
    gold_purist = str(map_purist(record.gold_monthly_frequency))
    predicted_purist = str(map_purist(predicted_record.monthly_frequency))
    gold_pragmatic = str(map_pragmatic(record.gold_monthly_frequency))
    predicted_pragmatic = str(map_pragmatic(predicted_record.monthly_frequency))
    return {
        "predicted_monthly_frequency": predicted_record.monthly_frequency,
        "gold_monthly_frequency": record.gold_monthly_frequency,
        "predicted_purist_category": predicted_purist,
        "gold_purist_category": gold_purist,
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": predicted_pragmatic,
        "gold_pragmatic_category": gold_pragmatic,
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


def _run_metadata(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    api_base: str | None = None,
) -> dict[str, Any]:
    return build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=PROMPT_VERSION,
        dspy_version=getattr(dspy, "__version__", "unknown"),
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
    )
