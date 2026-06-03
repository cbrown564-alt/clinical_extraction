"""LLM-only direct-labeler Gan 2026 seizure-frequency extraction experiments."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.replay_io import (
    load_raw_outputs_by_source_index,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    llm_model_metadata_lines,
    write_markdown_report,
)

PROMPT_VERSION = "gan2026_llm_only_direct_labeler_v0.1"
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_direct_labeler_validation_gpt41mini_2026-05-31.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_direct_labeler_validation_gpt41mini_2026-05-31.md"
)


class LlmOnlyDirectLabelerDecisionRecord(BaseModel):
    """Traceable note-to-label decision emitted by the LLM-only direct-labeler extractor."""

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
    selected_seizure_type: str
    time_window: str
    confidence: Literal["low", "medium", "high"]
    rationale: str


class Gan2026LlmOnlyDirectLabelerExtractorSignature(dspy.Signature):
    """Extract the Gan 2026 seizure-frequency answer directly from one note.

    Return exactly one JSON object with these keys: final_label, evidence,
    answer_kind, selected_seizure_type, time_window, confidence, and rationale.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical note, task instructions, and output fields."
    )
    decision_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object. final_label must be a normalized label such as "
            "'2 per month', '2 to 3 per week', 'multiple per day', "
            "'seizure free for multiple month', 'unknown', or "
            "'no seizure frequency reference'."
        )
    )


class DspyLlmOnlyDirectLabelerExtractor(dspy.Module):
    """DSPy note-to-label extractor with no deterministic candidate inputs."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026LlmOnlyDirectLabelerExtractorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def build_prompt_input(record: GanFrequencyRecord) -> str:
    """Build the LLM-only direct-labeler prompt payload, excluding gold labels."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": "Gan 2026 seizure-frequency LLM-only direct-labeler extraction",
        "source_row_index": record.source_row_index,
        "instructions": [
            "Read the full clinical note and extract the current seizure-frequency answer.",
            (
                "Return final_label as one normalized string using count, range, or "
                "multiple over a day/week/month/year denominator; seizure-free duration; "
                "unknown; or no seizure frequency reference."
            ),
            (
                "Allowed frequency forms include 1 per day, "
                "2 to 3 per month, multiple per week, 1 cluster per week, 2 to 3 per cluster, "
                "seizure free for 6 month, unknown, no seizure frequency reference."
            ),
            (
                "Preserve explicit count-and-window labels when possible instead of converting "
                "a stated multi-period count to a vague monthly bucket."
            ),
            (
                "If several current seizure types are present, select the highest current "
                "seizure burden across seizure types."
            ),
            (
                "Plural daily seizures/events should map to multiple per day unless the note "
                "clearly says exactly one per day."
            ),
            (
                "Use unknown when seizures or seizure-like events are discussed but current "
                "frequency cannot be converted to a normalized rate."
            ),
            (
                "Use no seizure frequency reference only when the note contains no usable "
                "seizure-frequency evidence."
            ),
            (
                "Use seizure-free only when the note asserts no seizures/events for a current "
                "duration; do not use seizure-free for a single semiology if other current "
                "seizure-like events remain."
            ),
            (
                "For trigger-conditioned or provoked-only events, report the stated frequency "
                "if countable; otherwise use unknown rather than seizure-free."
            ),
            (
                "For cluster labels, include both cluster rate and events per cluster when both "
                "are stated."
            ),
            "Evidence must be an exact substring from the note when possible.",
            "Return exactly one JSON object with no markdown.",
        ],
        "allowed_decision_fields": [
            "final_label",
            "evidence",
            "answer_kind",
            "selected_seizure_type",
            "time_window",
            "confidence",
            "rationale",
        ],
        "note_text": record.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_decision_json(
    raw_output: str,
) -> tuple[LlmOnlyDirectLabelerDecisionRecord | None, list[str]]:
    errors: list[str] = []
    try:
        payload = _filter_decision_payload(
            repair_decision_payload(json.loads(_extract_json_object(raw_output)))
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]

    try:
        decision = LlmOnlyDirectLabelerDecisionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    repaired_label = repair_prediction_label_with_evidence(
        decision.final_label,
        decision.evidence,
    )
    if repaired_label != decision.final_label:
        errors.append(f"final_label_repaired: {decision.final_label!r} -> {repaired_label!r}")
        decision = decision.model_copy(update={"final_label": repaired_label})

    try:
        label_to_frequency_record(decision.final_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")

    return decision, errors


def _filter_decision_payload(payload: Any) -> Any:
    """Keep shared adjudicator repair fields out of direct-labeler validation."""

    if not isinstance(payload, dict):
        return payload
    allowed = set(LlmOnlyDirectLabelerDecisionRecord.model_fields)
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
    program = DspyLlmOnlyDirectLabelerExtractor()
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

        decision, parse_errors = (
            parse_decision_json(raw_output) if raw_output else (None, ["not_run"])
        )
        evidence_valid = (
            evidence_is_substring(record.note_text, decision.evidence)
            if decision and decision.evidence
            else False
        )
        comparison = _compare_to_gold(record, decision) if decision else None
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
                "evidence_valid": evidence_valid,
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
    evidence_valid = sum(bool(row.get("evidence_valid")) for row in rows)
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
        "evidence_valid": evidence_valid,
        "purist_correct": purist_correct,
        "purist_accuracy": round(purist_correct / len(rows), 4) if rows else 0.0,
        "pragmatic_correct": pragmatic_correct,
        "pragmatic_accuracy": round(pragmatic_correct / len(rows), 4) if rows else 0.0,
        "final_labels": dict(sorted(final_labels.items())),
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
    lines = [
        "# Gan 2026 LLM-First Validation Run",
        "",
        f"Date: {metadata['date']}",
        "",
        "This is a validation development result on `gan2026_split_v1`. It is not a final "
        "holdout or benchmark result.",
        "",
        "## Experiment Unit",
        "",
        "Hypothesis: a note-only DSPy extractor can produce the prediction-bearing Gan "
        "seizure-frequency interpretation, while deterministic code is limited to label "
        "repair, evidence validation, and scoring.",
        "",
        "Minimal change: add an LLM-only direct-labeler runner. No deterministic V1 "
        "candidate diagnostics are provided to the model.",
        "",
        f"Data surface: `{metadata['split']}` split, `{metadata['split_manifest']}`, "
        f"{summary['examples']} rows.",
        (
            f"Rare full-validation reason: {metadata['escalation_reason']}"
            if metadata.get("escalation_reason")
            else "Rare full-validation reason: not applicable for this run size."
        ),
        "Scorer policy: Gan-compatible Purist categories first, Pragmatic categories as a "
        "side-car.",
        "",
        "## Model And Prompt Metadata",
        "",
        *llm_model_metadata_lines(
            metadata,
            jsonl_path,
            model_role="LLM-only direct-labeler note-to-label extractor",
            deterministic_rule_configuration=(
                "none before prediction; deterministic code only repairs labels, "
                "validates evidence, and scores."
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
        f"- Exact evidence substrings: {summary['evidence_valid']} / {summary['examples']}",
        f"- Purist validation accuracy/micro F1 proxy: {summary['purist_accuracy']:.4f} "
        f"({summary['purist_correct']} / {summary['examples']})",
        f"- Pragmatic validation accuracy/micro F1 proxy: {summary['pragmatic_accuracy']:.4f} "
        f"({summary['pragmatic_correct']} / {summary['examples']})",
        "",
        "## Rows",
        "",
        "| Row | Final | Gold | Purist | Notes |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        decision = row.get("decision_record") or {}
        comparison = row.get("comparison") or {}
        notes = "; ".join(row.get("parse_errors") or [])
        if row.get("call_error"):
            notes = f"{notes}; {row['call_error']}" if notes else str(row["call_error"])
        if not row.get("evidence_valid"):
            evidence_note = "evidence_not_exact_substring"
            notes = f"{notes}; {evidence_note}" if notes else evidence_note
        lines.append(
            f"| {row['source_row_index']} | {decision.get('final_label', '')} | "
            f"{row['reference']['gold_label']} | "
            f"{'yes' if comparison.get('purist_correct') else 'no'} | {notes} |"
        )
    write_markdown_report(path, lines)


def _compare_to_gold(
    record: GanFrequencyRecord,
    decision: LlmOnlyDirectLabelerDecisionRecord,
) -> dict[str, Any]:
    predicted_record = label_to_frequency_record(decision.final_label)
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


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            (
                "invalid_json:",
                "schema_validation_error:",
                "unscorable_final_label:",
                "not_run",
            )
        )
        for error in errors or []
    )


def _has_repair_note(errors: Any) -> bool:
    return any(str(error).startswith("final_label_repaired:") for error in errors or [])


def _extract_json_object(raw_output: str) -> str:
    text = raw_output.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text


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
