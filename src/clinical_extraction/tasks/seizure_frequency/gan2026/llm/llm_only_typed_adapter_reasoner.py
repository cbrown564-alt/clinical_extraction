"""Typed DSPy JSONAdapter reasoner for Gan 2026 adapter smoke experiments."""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.repair_modes import (
    repair_mode_layers,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_heavy_clinical_frequency_reasoner as heavy_reasoner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "gan2026_llm_only_typed_adapter_reasoner_v0"
PIPELINE_FAMILY = "llm_only_typed_adapter_reasoner"
TYPED_OUTPUT_SCHEMA_VERSION = "typed_adapter_v0"
SCORE_LAYER_NAMES = (
    "raw_llm",
    "format_only",
    "selected_evidence_arithmetic",
    "benchmark_aligned",
    "oracle_format_upper_bound",
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_typed_adapter_reasoner_validation25_gpt41mini_v0_2026-06-02.md"
)


class TypedClinicalFrequencyEvent(BaseModel):
    """Typed model-owned seizure-frequency fact."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    ]
    applies_to: str | None = None
    raw_phrase: str
    evidence: str
    assertion_status: Literal["asserted", "negated", "hypothetical", "uncertain"]
    temporality: Literal["current", "recent", "historical", "unclear"]
    certainty: Literal["high", "medium", "low"]
    clinical_quantity: heavy_reasoner.ClinicalQuantity
    model_normalized_clinical_label: str | None = None
    notes: str = ""


class TypedClinicalSelection(BaseModel):
    """Typed model-owned final event selection."""

    model_config = ConfigDict(extra="forbid")

    selected_event_ids: list[str]
    rejected_event_ids: list[str] = Field(default_factory=list)
    final_clinical_state: Literal[
        "frequency",
        "seizure_free",
        "unknown_frequency",
        "no_reference",
        "unresolved_multiple",
    ]
    aggregation_strategy: Literal[
        "highest_current_frequency",
        "recent_window",
        "seizure_free_over_current_event",
        "cluster_total_rate",
        "unknown_boundary",
        "no_reference_boundary",
        "other",
    ]
    final_clinical_label: str
    rationale: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)


class TypedGanFinalAnswer(BaseModel):
    """Typed parser-facing model-owned Gan answer."""

    model_config = ConfigDict(extra="forbid")

    raw_clinical_summary: str = ""
    raw_llm_final_label: str
    raw_llm_final_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    raw_llm_monthly_frequency: float | None = None
    selected_evidence: str
    selected_event_ids: list[str]
    supporting_event_ids: list[str] = Field(default_factory=list)
    combined_rationale: str = ""
    rendering_operands: heavy_reasoner.ClinicalQuantity | None = None
    arithmetic_trace: str = ""
    final_rationale: str = ""


class TypedAdapterExtractionRecord(BaseModel):
    """Full typed-adapter extraction record."""

    model_config = ConfigDict(extra="forbid")

    events: list[TypedClinicalFrequencyEvent]
    selection: TypedClinicalSelection
    final_answer: TypedGanFinalAnswer


class Gan2026TypedAdapterReasonerSignature(dspy.Signature):
    """Extract Gan 2026 seizure frequency with typed DSPy JSON output fields."""

    note_text: str = dspy.InputField(desc="Full Gan 2026 note text.")
    task_instructions: list[str] = dspy.InputField(
        desc="Short clinical extraction and rendering instructions."
    )
    output_contract: dict[str, Any] = dspy.InputField(
        desc="Typed output contract and allowed clinical enum values."
    )
    events: list[TypedClinicalFrequencyEvent] = dspy.OutputField(
        desc="Source-near seizure-frequency facts with exact evidence substrings."
    )
    selection: TypedClinicalSelection = dspy.OutputField(
        desc="Model-owned event selection and clinical aggregation decision."
    )
    final_answer: TypedGanFinalAnswer = dspy.OutputField(
        desc="Parser-ready model-owned final Gan label and selected evidence."
    )


class DspyTypedAdapterReasoner(dspy.Module):
    """DSPy typed-output program for the adapter-specific architecture."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026TypedAdapterReasonerSignature)

    def forward(
        self,
        *,
        note_text: str,
        task_instructions: list[str],
        output_contract: dict[str, Any],
    ) -> dspy.Prediction:
        return self.predict(
            note_text=note_text,
            task_instructions=task_instructions,
            output_contract=output_contract,
        )


def build_typed_adapter_inputs(record: GanFrequencyRecord) -> dict[str, Any]:
    """Build typed DSPy inputs without gold labels or deterministic candidates."""

    return {
        "note_text": record.note_text,
        "task_instructions": [
            "Extract source-near seizure-frequency facts only from the note.",
            "Copy every evidence string as an exact substring from the note.",
            "Select the prediction-bearing current/recent clinical frequency state.",
            "Render raw_llm_final_label as a parser-ready Gan label owned by the model.",
            "Keep deterministic selected-evidence arithmetic as a side-car, not a rescue.",
            "Return typed fields, not an opaque JSON string payload.",
        ],
        "output_contract": {
            "prompt_version": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "typed_output_schema_version": TYPED_OUTPUT_SCHEMA_VERSION,
            "top_level_outputs": ["events", "selection", "final_answer"],
            "event_kinds": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
            ],
            "final_label_examples": [
                "4 per day",
                "1 per 7 to 9 day",
                "2 to 4 per year",
                "multiple per week",
                "seizure free for 6 month",
                "unknown",
                "no seizure frequency reference",
            ],
            "selected_event_trace_rule": (
                "final_answer.selected_event_ids must exactly equal "
                "selection.selected_event_ids"
            ),
        },
    }


def prediction_to_extraction(
    prediction: Any,
) -> tuple[TypedAdapterExtractionRecord | None, list[str]]:
    """Validate a DSPy typed prediction into the local typed extraction record."""

    try:
        extraction = TypedAdapterExtractionRecord.model_validate(
            {
                "events": prediction.events,
                "selection": prediction.selection,
                "final_answer": prediction.final_answer,
            }
        )
    except (AttributeError, TypeError, ValidationError) as exc:
        return None, [f"adapter_parse_or_validation_error: {exc}"]
    return extraction, []


def validate_typed_extraction(
    extraction: TypedAdapterExtractionRecord | None,
    *,
    note_text: str | None = None,
) -> list[str]:
    """Run source, trace, and evidence validations after typed adapter parsing."""

    if extraction is None:
        return []
    errors: list[str] = []
    event_ids = {event.event_id for event in extraction.events}
    if not extraction.events:
        errors.append("event_extraction: no events")
    missing_selection_ids = [
        event_id
        for event_id in extraction.selection.selected_event_ids
        if event_id not in event_ids
    ]
    missing_final_ids = [
        event_id
        for event_id in extraction.final_answer.selected_event_ids
        if event_id not in event_ids
    ]
    if missing_selection_ids:
        errors.append(f"selection: unknown selected_event_ids {missing_selection_ids!r}")
    if missing_final_ids:
        errors.append(f"final_answer: unknown selected_event_ids {missing_final_ids!r}")
    if extraction.final_answer.selected_event_ids != extraction.selection.selected_event_ids:
        errors.append("selected_event_trace: final_answer ids differ from selection ids")
    selected_event_evidence = {
        event.evidence
        for event in extraction.events
        if event.event_id in extraction.final_answer.selected_event_ids
    }
    if extraction.final_answer.selected_evidence not in selected_event_evidence:
        errors.append("evidence: selected evidence is not one selected event evidence value")
    if note_text is not None:
        invalid_events = [
            event.event_id
            for event in extraction.events
            if not evidence_is_substring(note_text, event.evidence)
        ]
        if invalid_events:
            errors.append(f"evidence: invalid event evidence for {invalid_events!r}")
        if not evidence_is_substring(note_text, extraction.final_answer.selected_evidence):
            errors.append("evidence: invalid selected evidence")
    return errors


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
    escalation_reason: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the typed-adapter reasoner over a validation smoke surface."""

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
    metadata["escalation_reason"] = escalation_reason
    metadata["repair_mode_layers"] = repair_mode_layers(SCORE_LAYER_NAMES)
    program = DspyTypedAdapterReasoner()
    lm = None
    adapter = None
    if mode == "live":
        lm = build_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=dspy_cache,
            api_base=api_base,
        )
        adapter = dspy.JSONAdapter()

    rows: list[dict[str, Any]] = []
    for record in records:
        typed_inputs = build_typed_adapter_inputs(record)
        call_error: str | None = None
        prediction: Any | None = None
        if mode == "live":
            try:
                with dspy.context(lm=lm, adapter=adapter):
                    prediction = program(**typed_inputs)
            except Exception as exc:  # pragma: no cover - exercised only with live APIs.
                call_error = f"{type(exc).__name__}: {exc}"
        extraction, adapter_errors = (
            prediction_to_extraction(prediction) if prediction is not None else (None, ["not_run"])
        )
        parse_errors = [
            *adapter_errors,
            *validate_typed_extraction(extraction, note_text=record.note_text),
        ]
        structured_record = extraction.model_dump() if extraction else None
        evidence_summary = heavy_reasoner._evidence_summary(record.note_text, extraction)
        score_layers = heavy_reasoner._score_layers(record, extraction)
        repair_changes = heavy_reasoner._repair_changes(score_layers)
        component_status = _component_status(
            extraction=extraction,
            parse_errors=parse_errors,
            evidence_summary=evidence_summary,
            score_layers=score_layers,
            call_error=call_error,
        )
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "split": split,
                "split_manifest": split_manifest,
                "pipeline_family": PIPELINE_FAMILY,
                "pipeline_name": PROMPT_VERSION,
                "prompt_version": PROMPT_VERSION,
                "typed_input": typed_inputs,
                "raw_output": _raw_output_from_extraction(extraction),
                "reused_raw_output": False,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "structured_record": structured_record,
                "component_status": component_status,
                "evidence_summary": evidence_summary,
                "score_layers": score_layers,
                "repair_changes": repair_changes,
                "repair_mode_layers": repair_mode_layers(SCORE_LAYER_NAMES),
                "reference": {
                    "gold_label": record.gold_label,
                    "gold_normalized_label": record.gold_normalized_label,
                    "gold_label_kind": str(record.gold_label_kind),
                    "gold_monthly_frequency": record.gold_monthly_frequency,
                    "row_ok": record.row_ok,
                },
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


def summarize_records(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize typed adapter smoke rows."""

    component_failures = Counter(
        component
        for row in rows
        for component, status in (row.get("component_status") or {}).items()
        if status != "ok"
    )
    summary: dict[str, Any] = {
        "examples": len(rows),
        "structured_records": sum(bool(row.get("structured_record")) for row in rows),
        "call_failures": sum(bool(row.get("call_error")) for row in rows),
        "reused_raw_outputs": sum(bool(row.get("reused_raw_output")) for row in rows),
        "adapter_parse_failures": sum(
            any(
                str(error).startswith("adapter_parse_or_validation_error:")
                for error in row.get("parse_errors") or []
            )
            for row in rows
        ),
        "parse_or_validation_failures": sum(
            heavy_reasoner._has_blocking_parse_issue(row.get("parse_errors")) for row in rows
        ),
        "event_evidence_valid": sum(
            int((row.get("evidence_summary") or {}).get("event_evidence_valid", 0)) for row in rows
        ),
        "event_evidence_total": sum(
            int((row.get("evidence_summary") or {}).get("event_evidence_total", 0)) for row in rows
        ),
        "selected_evidence_valid": sum(
            int(bool((row.get("evidence_summary") or {}).get("selected_evidence_valid")))
            for row in rows
        ),
        "selected_event_trace_mismatches": sum(
            any(
                str(error).startswith("selected_event_trace:")
                for error in row.get("parse_errors") or []
            )
            for row in rows
        ),
        "rendering_operands_present": sum(
            int(heavy_reasoner._has_rendering_operands(row.get("structured_record")))
            for row in rows
        ),
        "arithmetic_trace_present": sum(
            int(heavy_reasoner._has_arithmetic_trace(row.get("structured_record")))
            for row in rows
        ),
        "component_failures": dict(sorted(component_failures.items())),
        "repair_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
    }
    for layer in SCORE_LAYER_NAMES:
        layer_summary = heavy_reasoner._layer_summary(rows, layer)
        for key, value in layer_summary.items():
            summary[f"{layer}_{key}"] = value
    summary.update(heavy_reasoner._side_car_deltas(rows))
    summary["typed_adapter_outcome"] = _typed_adapter_outcome(summary)
    return summary


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    /,
    *,
    jsonl_path: Path,
) -> None:
    """Write a compact Markdown typed-adapter smoke report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    outcome = str(summary.get("typed_adapter_outcome", "revise"))
    lines = [
        "# Gan 2026 LLM-Only Typed Adapter Reasoner V0",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Architecture: `{PIPELINE_FAMILY}`",
        "- Claim language: typed-adapter LLM-only architecture.",
        f"- Prompt/program version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Typed output schema version: `{metadata.get('typed_output_schema_version')}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Rows: {summary.get('examples', 0)}",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- DSPy adapter: `{metadata.get('dspy_adapter')}`",
        (
            "- Deterministic selected-evidence arithmetic, benchmark alignment, and "
            "full-stack repairs are side-car diagnostics."
        ),
        f"- Typed-adapter outcome: `{outcome}`",
        "",
        "## Predeclared Smoke",
        "",
        "- Surface: `validation25` under `gan2026_split_v1`.",
        (
            "- Primary question: can typed DSPy output plus scoped JSONAdapter reduce "
            "schema/parser/rendering failures while preserving LLM-owned clinical "
            "interpretation?"
        ),
        "- Stop rule: do not escalate beyond this smoke from this artifact.",
        "",
        "## Smoke Summary",
        "",
        (
            f"- Structured records: {summary.get('structured_records', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- Adapter parse failures: {summary.get('adapter_parse_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_or_validation_failures', 0)}",
        (
            f"- Selected evidence valid: {summary.get('selected_evidence_valid', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        (
            f"- Rendering operands present: {summary.get('rendering_operands_present', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        (
            f"- Arithmetic/rendering traces present: "
            f"{summary.get('arithmetic_trace_present', 0)}/{summary.get('examples', 0)}"
        ),
        (
            f"- Event evidence valid: {summary.get('event_evidence_valid', 0)}/"
            f"{summary.get('event_evidence_total', 0)}"
        ),
        f"- Selected-event trace mismatches: {summary.get('selected_event_trace_mismatches', 0)}",
        "",
        "## Score Layers",
        "",
    ]
    for layer in SCORE_LAYER_NAMES:
        lines.append(
            f"- `{layer}`: scorable {summary.get(f'{layer}_scorable', 0)}, "
            f"Purist {summary.get(f'{layer}_purist_correct', 0)}/{summary.get('examples', 0)} "
            f"({summary.get(f'{layer}_purist_accuracy', 0.0):.4f}), "
            f"Pragmatic {summary.get(f'{layer}_pragmatic_correct', 0)}/"
            f"{summary.get('examples', 0)} "
            f"({summary.get(f'{layer}_pragmatic_accuracy', 0.0):.4f})"
        )
    lines.extend(
        [
            "",
            "## Adapter Gate",
            "",
            (
                f"- Structured adapter outputs: {summary.get('structured_records', 0)}/"
                f"{summary.get('examples', 0)}"
            ),
            (
                f"- Raw parser-compatible labels: {summary.get('raw_llm_scorable', 0)}/"
                f"{summary.get('examples', 0)}"
            ),
            (
                f"- Raw model-owned Purist: {summary.get('raw_llm_purist_correct', 0)}/"
                f"{summary.get('examples', 0)}"
            ),
            "- Deterministic selected-evidence arithmetic raw-wrong to correct: "
            f"{summary.get('selected_evidence_arithmetic_raw_wrong_to_correct', 0)}",
            "- Deterministic selected-evidence arithmetic raw-correct to wrong: "
            f"{summary.get('selected_evidence_arithmetic_raw_correct_to_wrong', 0)}",
            "",
            "## Row Review",
            "",
            *_row_review_lines(rows),
            "",
            "## Failure Taxonomy",
            "",
            *_failure_taxonomy_lines(rows),
            "",
            "## Interpretation",
            "",
            _interpretation_text(outcome),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _component_status(
    *,
    extraction: TypedAdapterExtractionRecord | None,
    parse_errors: Sequence[str],
    evidence_summary: Mapping[str, Any],
    score_layers: Mapping[str, Mapping[str, Any]],
    call_error: str | None,
) -> dict[str, str]:
    status = {
        "typed_adapter_parse": "ok",
        "event_extraction": "ok",
        "clinical_selection": "ok",
        "final_schema_rendering": "ok",
        "parse_schema": "ok",
        "evidence_exactness": "ok",
        "scorer_format": "ok",
        "selected_event_trace": "ok",
    }
    if call_error or heavy_reasoner._has_blocking_parse_issue(parse_errors):
        status["parse_schema"] = "fail"
    if any(str(error).startswith("adapter_parse_or_validation_error:") for error in parse_errors):
        status["typed_adapter_parse"] = "fail"
    if extraction is None:
        status["event_extraction"] = "fail"
        status["clinical_selection"] = "fail"
        status["final_schema_rendering"] = "fail"
        status["scorer_format"] = "fail"
        return status
    if not extraction.events or any(
        str(error).startswith("event_extraction:") for error in parse_errors
    ):
        status["event_extraction"] = "fail"
    if any(str(error).startswith("selection:") for error in parse_errors):
        status["clinical_selection"] = "fail"
    if any(str(error).startswith("final_answer:") for error in parse_errors):
        status["final_schema_rendering"] = "fail"
    if any(str(error).startswith("selected_event_trace:") for error in parse_errors):
        status["selected_event_trace"] = "fail"
    if evidence_summary.get("event_evidence_valid") != evidence_summary.get("event_evidence_total"):
        status["event_extraction"] = "fail"
        status["evidence_exactness"] = "fail"
    if not evidence_summary.get("selected_evidence_valid"):
        status["final_schema_rendering"] = "fail"
        status["evidence_exactness"] = "fail"
    if not evidence_summary.get("selected_event_evidence_valid"):
        status["final_schema_rendering"] = "fail"
        status["evidence_exactness"] = "fail"
    if not score_layers["raw_llm"].get("scorable"):
        status["scorer_format"] = "fail"
    if (
        extraction.final_answer.rendering_operands is None
        or not extraction.final_answer.arithmetic_trace
    ):
        status["final_schema_rendering"] = "fail"
    return status


def _raw_output_from_extraction(extraction: TypedAdapterExtractionRecord | None) -> str:
    if extraction is None:
        return ""
    return json.dumps(extraction.model_dump(), sort_keys=True)


def _typed_adapter_outcome(summary: Mapping[str, Any]) -> str:
    examples = int(summary.get("examples", 0))
    if examples == 0:
        return "reject"
    blocking_reject = any(
        (
            int(summary.get("structured_records", 0)) < examples,
            int(summary.get("raw_llm_scorable", 0)) < 24,
            int(summary.get("selected_evidence_valid", 0)) < 23,
            int(summary.get("selected_event_trace_mismatches", 0)) > 0,
            int(summary.get("selected_evidence_arithmetic_raw_wrong_to_correct", 0)) > 5,
        )
    )
    if blocking_reject:
        return "reject"
    if int(summary.get("raw_llm_purist_correct", 0)) >= 20:
        return "promote_to_validation50_allowed_by_gate"
    return "revise"


def _row_review_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for row in rows:
        layers = row.get("score_layers") or {}
        raw = layers.get("raw_llm") or {}
        arithmetic = layers.get("selected_evidence_arithmetic") or {}
        if raw.get("purist_correct") and arithmetic.get("purist_correct"):
            continue
        if raw.get("purist_correct") and not arithmetic.get("purist_correct"):
            status = "side-car regression"
        elif not raw.get("purist_correct") and arithmetic.get("purist_correct"):
            status = "side-car correction"
        else:
            status = "raw miss"
        lines.append(
            "- "
            f"{row.get('source_row_index')}: {status}; "
            f"gold `{((row.get('reference') or {}).get('gold_normalized_label'))}`; "
            f"raw `{raw.get('final_label')}`; "
            f"selected-evidence arithmetic `{arithmetic.get('final_label')}`; "
            f"taxonomy `{heavy_reasoner._failure_family(row)}`"
        )
    if not lines:
        return ["- No raw misses or selected-evidence side-car regressions."]
    return lines


def _failure_taxonomy_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    counts = Counter(heavy_reasoner._failure_family(row) for row in rows)
    return [f"- `{family}`: {count}" for family, count in sorted(counts.items())]


def _interpretation_text(outcome: str) -> str:
    if outcome == "promote_to_validation50_allowed_by_gate":
        return (
            "This validation25 typed-adapter smoke passes the architecture gate. "
            "Escalation may be considered only as a separately predeclared validation50 run."
        )
    if outcome == "reject":
        return (
            "This validation25 typed-adapter smoke fails at least one hard adapter or "
            "attribution gate. Do not escalate this artifact."
        )
    return (
        "This validation25 typed-adapter smoke is interpretable but not promotable. "
        "Revise typed fields, adapter policy, or prompt compactness before validation50."
    )


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
        "adapter_parse_failures": metadata["summary"]["adapter_parse_failures"],
        "raw_llm_scorable": metadata["summary"]["raw_llm_scorable"],
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


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
        extra={
            "architecture": PIPELINE_FAMILY,
            "claim_type": PIPELINE_FAMILY,
            "pipeline_name": PROMPT_VERSION,
            "pipeline_family": "llm_only",
            "score_layers_to_report": list(SCORE_LAYER_NAMES),
            "dspy_adapter": "JSONAdapter",
            "dspy_adapter_native_function_calling": True,
            "response_format_mode": "scoped_dspy_context_json_adapter",
            "typed_output_schema_version": TYPED_OUTPUT_SCHEMA_VERSION,
            "raw_model_owned_score_layer": "raw_llm",
            "side_car_score_layers": [
                "format_only",
                "selected_evidence_arithmetic",
                "benchmark_aligned",
                "oracle_format_upper_bound",
            ],
            "schema_smoke_stop_rule": {
                "surface": "validation25 under gan2026_split_v1",
                "adapter_parseable_outputs_minimum": "25/25",
                "raw_parser_compatible_minimum": "24/25",
                "selected_evidence_exactness_minimum": "23/25",
                "selected_event_trace_mismatches_maximum": "0/25",
                "deterministic_arithmetic_gap_maximum": "5 rows",
            },
        },
    )
