"""Shared scaffold for Gan 2026 agentic DSPy stage runners.

Migrated stages implement :class:`AgenticStage` with stage-local prompt builders,
decision schemas, and postprocess policies. Shared helpers cover JSON parsing via
``contract.schema_repair``, format-only label repair, evidence substring checks,
run metadata, JSONL I/O, and markdown report skeletons.

Unmigrated modules under ``agentic/`` still use the legacy inline-runner pattern;
see ``agentic/README.md``.
"""

from __future__ import annotations

import json
import re
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Generic, Literal, TypeVar

import dspy
from pydantic import BaseModel, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
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
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import (
    write_markdown_report,
)

TDecision = TypeVar("TDecision", bound=BaseModel)

DEFAULT_BLOCKING_PARSE_PREFIXES: tuple[str, ...] = (
    "invalid_json:",
    "schema_validation_error:",
    "unscorable_final_label:",
    "not_run",
)

DEFAULT_REPAIR_NOTE_PREFIXES: tuple[str, ...] = (
    "final_label_repaired:",
    "final_label_format_repaired:",
    "json_dialect_repaired:",
)


@dataclass(frozen=True)
class ParsedStageResponse(Generic[TDecision]):
    """Normalized parse outcome for one model response."""

    decision: TDecision | None
    parse_errors: list[str] = field(default_factory=list)
    format_repair_events: list[dict[str, Any]] = field(default_factory=list)
    raw_final_label: str | None = None


@dataclass(frozen=True)
class DspyCallSpec:
    """DSPy signature wiring for a one-shot JSON stage call."""

    signature_class: type[dspy.Signature]
    input_field: str = "prompt_input_json"
    output_field: str = "decision_json"


class AgenticStage(ABC, Generic[TDecision]):
    """Contract for agentic stages: prompt + schema + parse/postprocess policy."""

    @property
    @abstractmethod
    def prompt_version(self) -> str:
        """Stage prompt version stamped into artifacts."""

    @abstractmethod
    def build_prompt_input(self, record: GanFrequencyRecord, **context: Any) -> str:
        """Serialize one model-facing prompt payload."""

    @abstractmethod
    def parse_response(self, raw_output: str, **context: Any) -> ParsedStageResponse[TDecision]:
        """Parse and postprocess one raw model response."""

    def postprocess_decision(
        self,
        decision: TDecision,
        *,
        note_text: str,
        **context: Any,
    ) -> tuple[TDecision, list[str]]:
        """Optional hook after schema validation; default is identity."""

        del note_text, context
        return decision, []


def extract_json_object(raw_output: str) -> str:
    """Pull the first JSON object from fenced or free-form model text."""

    text = raw_output.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text


def filter_payload_to_model(payload: Any, model: type[BaseModel]) -> Any:
    """Drop unknown keys before Pydantic validation."""

    if not isinstance(payload, dict):
        return payload
    allowed = set(model.model_fields)
    return {key: value for key, value in payload.items() if key in allowed}


def parse_response(
    raw_output: str,
    *,
    decision_model: type[TDecision],
    payload_filter: Callable[[Any], Any] | None = None,
    shape_repair: Callable[[Any], tuple[Any, list[str]]] | None = None,
    label_field: str = "final_label",
    evidence_field: str | None = "evidence",
    label_repair: Literal["none", "format_only", "with_evidence"] = "format_only",
    require_scorable_label: bool = True,
) -> ParsedStageResponse[TDecision]:
    """Parse a labeled decision JSON object with shared schema-repair policy."""

    parse_errors: list[str] = []
    format_repair_events: list[dict[str, Any]] = []
    raw_final_label: str | None = None
    if not raw_output or not raw_output.strip():
        return ParsedStageResponse(None, parse_errors=["empty_output"])

    try:
        raw_payload, dialect_notes = parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return ParsedStageResponse(None, parse_errors=[f"invalid_json: {exc.msg}"])

    parse_errors.extend(dialect_notes)
    payload = repair_decision_payload(raw_payload)
    if payload_filter is not None:
        payload = payload_filter(payload)
    if shape_repair is not None:
        payload, shape_notes = shape_repair(payload)
        parse_errors.extend(shape_notes)

    if isinstance(payload, dict) and label_field in payload:
        raw_final_label = str(payload[label_field])

    try:
        decision = decision_model.model_validate(payload)
    except ValidationError as exc:
        return ParsedStageResponse(
            None,
            parse_errors=[*parse_errors, f"schema_validation_error: {exc.errors()[0]['msg']}"],
            raw_final_label=raw_final_label,
        )

    decision, repair_notes, repair_events = _apply_label_repair_policy(
        decision,
        label_field=label_field,
        evidence_field=evidence_field,
        label_repair=label_repair,
    )
    parse_errors.extend(repair_notes)
    format_repair_events.extend(repair_events)

    if require_scorable_label and isinstance(getattr(decision, label_field, None), str):
        try:
            label_to_frequency_record(str(getattr(decision, label_field)))
        except ValueError as exc:
            parse_errors.append(f"unscorable_final_label: {exc}")

    return ParsedStageResponse(
        decision,
        parse_errors=parse_errors,
        format_repair_events=format_repair_events,
        raw_final_label=raw_final_label,
    )


def apply_format_only_label_repair(label: str) -> tuple[str, list[dict[str, Any]], list[str]]:
    """Repair scorer-format issues without semantic remapping."""

    trace = repair_prediction_label_format_preserving_with_trace(label)
    notes: list[str] = []
    if trace.final_label != label:
        notes.append(f"final_label_format_repaired: {label!r} -> {trace.final_label!r}")
    events = [
        {
            "rule_id": event.rule_id,
            "before": event.before,
            "after": event.after,
        }
        for event in trace.events
    ]
    return trace.final_label, events, notes


def apply_evidence_label_repair(label: str, evidence: str) -> tuple[str, list[str]]:
    """Repair label formatting using the cited evidence substring."""

    repaired = repair_prediction_label_with_evidence(label, evidence)
    notes: list[str] = []
    if repaired != label:
        notes.append(f"final_label_repaired: {label!r} -> {repaired!r}")
    return repaired, notes


def validate_evidence_substring(note_text: str, evidence: str | None) -> bool:
    """Return whether one evidence span is an exact note substring."""

    if not evidence:
        return False
    return evidence_is_substring(note_text, evidence)


def validate_evidence_substrings(note_text: str, evidence_items: Sequence[str]) -> bool:
    """Return whether every non-empty evidence span is an exact note substring."""

    spans = [item for item in evidence_items if item]
    if not spans:
        return False
    return all(evidence_is_substring(note_text, span) for span in spans)


def build_stage_metadata(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    prompt_version: str,
    dspy_cache: bool,
    api_base: str | None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build common Gan 2026 agentic run metadata."""

    metadata = build_run_metadata(
        mode=mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_version=prompt_version,
        dspy_version=getattr(dspy, "__version__", "unknown"),
        split=split,
        split_manifest=split_manifest,
        api_base=api_base,
        row_count=len(records),
    )
    metadata["dspy_cache"] = dspy_cache
    if extra:
        metadata.update(dict(extra))
    return metadata


def configure_dspy_for_stage(
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    cache: bool,
    api_base: str | None,
) -> None:
    """Configure the process-global DSPy LM for a live agentic split."""

    dspy.configure(
        lm=build_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=cache,
            api_base=api_base,
        )
    )


def build_isolated_dspy_lm(
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    api_base: str | None,
    cache: bool = False,
    num_retries: int = 2,
    timeout: int = 60,
) -> dspy.LM:
    """Build a dedicated LM for shadow stages that must not disturb host config."""

    return build_dspy_lm(
        model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache=cache,
        api_base=api_base,
        num_retries=num_retries,
        timeout=timeout,
    )


def write_stage_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    """Write stage rows to JSONL."""

    write_jsonl_rows(rows, path)


def load_stage_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load stage rows from JSONL."""

    return load_jsonl_rows(path)


def write_stage_markdown_report(path: Path, lines: Sequence[str]) -> None:
    """Write a markdown report from pre-built lines."""

    write_markdown_report(path, list(lines))


def build_markdown_report_skeleton(
    *,
    title: str,
    metadata: Mapping[str, Any],
    summary: Mapping[str, Any],
    gate: Mapping[str, Any],
    jsonl_path: Path,
    experiment_unit_lines: Sequence[str],
    summary_lines: Sequence[str],
    row_table_header: str,
    row_table_rows: Sequence[str],
    extra_sections: Sequence[str] = (),
    row_table_separator: str | None = None,
) -> list[str]:
    """Assemble a standard Gan 2026 agentic markdown report."""

    lines = [
        f"# {title}",
        "",
        f"Date: {metadata.get('date', 'unknown')}",
        "",
        "## Experiment Unit",
        "",
        *experiment_unit_lines,
        "",
        "## Summary",
        "",
        *summary_lines,
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
        f"- JSONL artifact: `{jsonl_path}`",
        "",
    ]
    if extra_sections:
        lines.extend(extra_sections)
        if not extra_sections[-1]:
            lines.append("")
    column_count = row_table_header.count("|") - 1
    separator = row_table_separator or (
        "| " + " | ".join(["---:" if index == 0 else "---" for index in range(column_count)]) + " |"
    )
    lines.extend(
        [
            "## Rows",
            "",
            row_table_header,
            separator,
            *row_table_rows,
        ]
    )
    return lines


def has_blocking_parse_issue(
    errors: Any,
    *,
    blocking_prefixes: Sequence[str] = DEFAULT_BLOCKING_PARSE_PREFIXES,
) -> bool:
    """Return whether parse errors contain a blocking failure."""

    return any(
        str(error).startswith(tuple(blocking_prefixes))
        for error in (errors or [])
    )


def has_repair_note(
    errors: Any,
    *,
    repair_prefixes: Sequence[str] = DEFAULT_REPAIR_NOTE_PREFIXES,
) -> bool:
    """Return whether parse errors contain a repair/dialect note."""

    return any(
        str(error).startswith(tuple(repair_prefixes)) or "shape_repaired:" in str(error)
        for error in (errors or [])
    )


def emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    summarize_rows: Callable[[Sequence[Mapping[str, Any]]], dict[str, Any]],
    gate_interpretation: Callable[[Mapping[str, Any]], dict[str, Any]] | None = None,
    finalize_metadata: Callable[[Sequence[Mapping[str, Any]], dict[str, Any]], None]
    | None = None,
    jsonl_path: Path | None = None,
    report_path: Path | None = None,
    write_report: Callable[..., None] | None = None,
    progress_fields: Sequence[str] = ("call_failures", "parse_or_validation_failures", "purist_correct"),
) -> None:
    """Write optional checkpoint artifacts and emit a stderr progress line."""

    metadata["summary"] = summarize_rows(rows)
    if finalize_metadata is not None:
        finalize_metadata(rows, metadata)
    elif gate_interpretation is not None:
        metadata["gate"] = gate_interpretation(metadata["summary"])
    if jsonl_path is not None:
        write_stage_jsonl(rows, jsonl_path)
    if report_path is not None and write_report is not None and jsonl_path is not None:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path)
    payload = {"processed": len(rows), "total": total}
    summary = dict(metadata.get("summary") or {})
    for field_name in progress_fields:
        if field_name in summary:
            payload[field_name] = summary[field_name]
    print(json.dumps(payload, sort_keys=True), file=sys.stderr, flush=True)


def make_dspy_predictor(spec: DspyCallSpec) -> dspy.Predict:
    """Construct a DSPy predictor for a stage signature."""

    return dspy.Predict(spec.signature_class)


def run_dspy_json_call(
    predictor: dspy.Predict,
    *,
    lm: dspy.LM,
    input_field: str,
    output_field: str,
    prompt_input_json: str,
) -> str:
    """Run one JSON-emitting DSPy call under an isolated LM context."""

    with dspy.context(lm=lm):
        prediction = predictor(**{input_field: prompt_input_json})
    return str(getattr(prediction, output_field))


def _apply_label_repair_policy(
    decision: TDecision,
    *,
    label_field: str,
    evidence_field: str | None,
    label_repair: Literal["none", "format_only", "with_evidence"],
) -> tuple[TDecision, list[str], list[dict[str, Any]]]:
    if label_repair == "none":
        return decision, [], []
    label_value = getattr(decision, label_field, None)
    if not isinstance(label_value, str):
        return decision, [], []

    parse_notes: list[str] = []
    repair_events: list[dict[str, Any]] = []
    repaired_label = label_value
    if label_repair == "format_only":
        repaired_label, repair_events, parse_notes = apply_format_only_label_repair(label_value)
    elif label_repair == "with_evidence" and evidence_field is not None:
        evidence_value = getattr(decision, evidence_field, None)
        if isinstance(evidence_value, str):
            repaired_label, parse_notes = apply_evidence_label_repair(label_value, evidence_value)

    if repaired_label == label_value:
        return decision, parse_notes, repair_events
    return decision.model_copy(update={label_field: repaired_label}), parse_notes, repair_events
