"""LLM-only typed operation extractor with model-derived graph projection."""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import (
    clean_semantically_neutral_text_artifacts,
    evidence_is_substring,
    locate_evidence,
    repair_evidence_text_if_source_exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
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
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.state_graph import (
    ClinicalFrequencyStateGraph,
    EvidenceSpan,
    GraphNodeKind,
    StateGraphNode,
    project_graph_to_gan,
)

PROMPT_VERSION = "gan2026_llm_only_typed_operations_reasoner_v0_contractfix"
PIPELINE_FAMILY = "llm_only_typed_operations_reasoner"
TYPED_OUTPUT_SCHEMA_VERSION = "typed_operations_v0"
SCORE_LAYER_NAMES = (
    "raw_llm",
    "format_only",
    "selected_evidence_arithmetic",
    "typed_operation_graph_projection",
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v0_contractfix_2026-06-03.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_typed_operations_reasoner_validation25_gpt41mini_v0_contractfix_2026-06-03.md"
)


class TypedOperationOperands(BaseModel):
    """Model-extracted operands for transparent frequency/state operations."""

    model_config = ConfigDict(extra="forbid")

    event_count_low: float | None = None
    event_count_high: float | None = None
    time_window_low: float | None = None
    time_window_high: float | None = None
    time_window_unit: Literal["day", "week", "month", "year", "window"] | None = None
    denominator_count: float | None = None
    denominator_unit: Literal["day", "week", "month", "year", "window", "cluster"] | None = None
    cluster_size_low: float | None = None
    cluster_size_high: float | None = None
    seizure_free_duration_low: float | None = None
    seizure_free_duration_high: float | None = None
    seizure_free_duration_unit: Literal["day", "week", "month", "year"] | None = None
    temporal_anchor: str | None = None
    semiology_grouping: str | None = None
    uncertainty_type: Literal[
        "none",
        "range",
        "vague_count",
        "approximate",
        "conflicting",
        "unclear_window",
        "unclear_semiology",
        "negated_or_historical",
        "other",
    ] = "none"
    selected_evidence_id: str


class TypedOperationRecord(BaseModel):
    """One model-owned source-near typed operation."""

    model_config = ConfigDict(extra="forbid")

    operation_id: str
    operation_kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
    ]
    evidence_id: str
    evidence: str
    raw_phrase: str
    temporality: Literal["current", "recent", "historical", "future", "unclear"]
    assertion_status: Literal["asserted", "negated", "hypothetical", "uncertain"]
    certainty: Literal["high", "medium", "low"]
    operands: TypedOperationOperands
    model_normalized_clinical_label: str | None = None
    clinical_note: str = ""


class TypedOperationSelection(BaseModel):
    """Model-owned operation selection for a target policy or clinical clarity."""

    model_config = ConfigDict(extra="forbid")

    selected_operation_ids: list[str]
    rejected_operation_ids: list[str] = Field(default_factory=list)
    target_policy: Literal["target_scoring_policy", "clinical_clarity"]
    final_clinical_state: Literal[
        "frequency",
        "seizure_free",
        "unknown_frequency",
        "no_reference",
        "unresolved_multiple",
    ]
    selection_strategy: Literal[
        "current_highest_burden",
        "overall_count",
        "recent_window",
        "cluster_total_rate",
        "seizure_free_state",
        "uncertainty_boundary",
        "no_reference_boundary",
        "clinical_clarity",
        "other",
    ]
    selected_evidence_id: str
    selected_evidence: str
    rationale: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)


class TypedOperationFinalAnswer(BaseModel):
    """Model-rendered answer plus selected operation trace."""

    model_config = ConfigDict(extra="forbid")

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
    rendering_operands: TypedOperationOperands | None = None
    arithmetic_trace: str = ""
    raw_clinical_summary: str = ""
    combined_rationale: str = ""
    final_rationale: str = ""


class TypedOperationsExtractionRecord(BaseModel):
    """Full typed-operations extraction returned by DSPy JSONAdapter."""

    model_config = ConfigDict(extra="forbid")

    operations: list[TypedOperationRecord]
    selection: TypedOperationSelection
    final_answer: TypedOperationFinalAnswer


class Gan2026TypedOperationsReasonerSignature(dspy.Signature):
    """Extract typed seizure-frequency operations with typed DSPy outputs."""

    note_text: str = dspy.InputField(desc="Full clinical note text.")
    task_instructions: list[str] = dspy.InputField(
        desc="Short operation extraction and selection instructions."
    )
    output_contract: dict[str, Any] = dspy.InputField(
        desc="Typed output contract and enum values."
    )
    operations: list[TypedOperationRecord] = dspy.OutputField(
        desc="Typed operation facts with exact evidence substrings."
    )
    selection: TypedOperationSelection = dspy.OutputField(
        desc="Selected operation ids and selection policy."
    )
    final_answer: TypedOperationFinalAnswer = dspy.OutputField(
        desc="Final label, selected evidence, and selected operation ids."
    )


class DspyTypedOperationsReasoner(dspy.Module):
    """DSPy typed-output program for the typed-operations lane."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026TypedOperationsReasonerSignature)

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


def build_typed_operations_inputs(record: GanFrequencyRecord) -> dict[str, Any]:
    """Build model-facing typed-operation inputs without labels or candidate rows."""

    return {
        "note_text": record.note_text,
        "task_instructions": [
            "Extract seizure-frequency facts from the note.",
            "Copy each evidence value as an exact substring from the note.",
            (
                "Record numeric details for event counts, timeframes, rate time basis, "
                "clusters, seizure freedom, anchors, semiology, and uncertainty."
            ),
            (
                "Select the operation set that best answers the requested policy while "
                "preserving clinical clarity."
            ),
            (
                "Keep frequency, seizure-free, unclear-frequency, no-reference, and "
                "unresolved-multiple states distinct."
            ),
            "Return typed fields, not a string payload.",
            "Do not add any keys other than operations, selection, and final_answer.",
            (
                "Do not copy note headers, patient identifiers, DOB fields, hospital "
                "numbers, NHS numbers, or letter boilerplate into typed output keys."
            ),
            (
                "Copy evidence using the exact visible characters from the note; do "
                "not emit escaped Unicode, HTML entities, backslash escapes, or control "
                "characters inside evidence strings."
            ),
            (
                "If final_answer includes numeric details, include the same "
                "selected_evidence_id field required on the selected fact."
            ),
        ],
        "output_contract": {
            "top_level_outputs": ["operations", "selection", "final_answer"],
            "operation_kinds": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
            ],
            "field_descriptions": {
                "operations": "Facts copied from the note that may describe seizure frequency.",
                "selection": "Which extracted facts answer the current seizure-frequency question.",
                "final_answer": "Seizure-frequency answer supported by the selected facts.",
                "operation_id": "Stable identifier for one extracted fact.",
                "operation_kind": "Type of seizure-frequency fact.",
                "evidence_id": "Stable identifier for the evidence text.",
                "evidence": "Exact note substring supporting the fact.",
                "raw_phrase": "Short phrase copied from the evidence.",
                "operands": "Numeric details such as count, timeframe, cluster size, or duration.",
                "raw_llm_final_label": (
                    "Seizure-frequency answer written from the selected evidence."
                ),
                "rendering_operands": "Optional numeric details used in the answer.",
            },
            "operation_operand_fields": [
                "event_count_low",
                "event_count_high",
                "time_window_low",
                "time_window_high",
                "time_window_unit",
                "denominator_count",
                "denominator_unit",
                "cluster_size_low",
                "cluster_size_high",
                "seizure_free_duration_low",
                "seizure_free_duration_high",
                "seizure_free_duration_unit",
                "temporal_anchor",
                "semiology_grouping",
                "uncertainty_type",
                "selected_evidence_id",
            ],
            "operation_operand_field_descriptions": {
                "event_count_low": "Lowest stated seizure count.",
                "event_count_high": "Highest stated seizure count, if a range is given.",
                "time_window_low": "Lowest stated timeframe count.",
                "time_window_high": "Highest stated timeframe count, if a range is given.",
                "time_window_unit": "Time unit for the stated timeframe.",
                "denominator_count": "Count for the time unit in a rate.",
                "denominator_unit": "Time unit in a rate, or cluster when the rate is per cluster.",
                "cluster_size_low": "Lowest stated seizures per cluster.",
                "cluster_size_high": "Highest stated seizures per cluster.",
                "seizure_free_duration_low": "Lowest stated seizure-free duration.",
                "seizure_free_duration_high": "Highest stated seizure-free duration.",
                "seizure_free_duration_unit": "Time unit for seizure-free duration.",
                "temporal_anchor": "Text describing when the fact applies.",
                "semiology_grouping": "Text naming which seizure type the fact applies to.",
                "uncertainty_type": "Type of uncertainty, or none.",
                "selected_evidence_id": "Evidence identifier this numeric detail describes.",
            },
            "final_label_examples": [
                "4 per day",
                "1 per 7 to 9 day",
                "3 per 6 week",
                "multiple per month",
                "seizure free for 6 month",
                "unknown",
                "no seizure frequency reference",
            ],
            "trace_rule": (
                "final_answer.selected_event_ids must equal selection.selected_operation_ids; "
                "selection.selected_evidence_id must name one selected operation evidence_id"
            ),
            "top_level_output_rule": (
                "Do not add any keys other than operations, selection, and final_answer."
            ),
            "forbidden_extra_keys": [
                "DOB",
                "Hospital No",
                "NHS No",
                "No",
                "clinic_date",
                "patient_name",
                "letter_text",
            ],
            "evidence_copy_rule": {
                "required": "copy exact visible substrings from note_text",
                "forbidden": [
                    "\\u",
                    "\\x",
                    "HTML entities",
                    "control characters",
                    "normalized mathematical symbols",
                ],
            },
            "rendering_operands_rule": (
                "When final_answer.rendering_operands is non-null, it must include "
                "selected_evidence_id and that value must match a selected operation evidence_id."
            ),
        },
    }


def prediction_to_extraction(
    prediction: Any,
    *,
    note_text: str | None = None,
) -> tuple[TypedOperationsExtractionRecord | None, list[str]]:
    """Validate a DSPy typed prediction into the local extraction record."""

    try:
        extraction = TypedOperationsExtractionRecord.model_validate(
            {
                "operations": prediction.operations,
                "selection": prediction.selection,
                "final_answer": prediction.final_answer,
            }
        )
    except (AttributeError, TypeError, ValidationError) as exc:
        return None, [f"typed_operations_parse_or_validation_error: {exc}"]
    if note_text is not None:
        extraction = _repair_typed_operations_evidence_copy(extraction, note_text)
    return extraction, []


def validate_typed_operations_extraction(
    extraction: TypedOperationsExtractionRecord | None,
    *,
    note_text: str | None = None,
) -> list[str]:
    """Run source, trace, and operand validations."""

    if extraction is None:
        return []
    errors: list[str] = []
    operation_ids = {operation.operation_id for operation in extraction.operations}
    if not extraction.operations:
        errors.append("operation_extraction: no operations")
    missing_selection_ids = [
        operation_id
        for operation_id in extraction.selection.selected_operation_ids
        if operation_id not in operation_ids
    ]
    missing_final_ids = [
        operation_id
        for operation_id in extraction.final_answer.selected_event_ids
        if operation_id not in operation_ids
    ]
    if missing_selection_ids:
        errors.append(f"selection: unknown selected_operation_ids {missing_selection_ids!r}")
    if missing_final_ids:
        errors.append(f"final_answer: unknown selected_event_ids {missing_final_ids!r}")
    if extraction.final_answer.selected_event_ids != extraction.selection.selected_operation_ids:
        errors.append("selected_operation_trace: final_answer ids differ from selection ids")
    selected_operations = [
        operation
        for operation in extraction.operations
        if operation.operation_id in extraction.selection.selected_operation_ids
    ]
    selected_evidence_ids = {operation.evidence_id for operation in selected_operations}
    if extraction.selection.selected_evidence_id not in selected_evidence_ids:
        errors.append("selection: selected_evidence_id is not selected operation evidence_id")
    for operation in extraction.operations:
        if operation.operands.selected_evidence_id != operation.evidence_id:
            errors.append(
                f"operation:{operation.operation_id}: operands selected_evidence_id mismatch"
            )
    selected_event_evidence = {operation.evidence for operation in selected_operations}
    if extraction.final_answer.selected_evidence not in selected_event_evidence:
        errors.append("evidence: selected evidence is not one selected operation evidence value")
    if note_text is not None:
        invalid_operations = [
            operation.operation_id
            for operation in extraction.operations
            if not evidence_is_substring(note_text, operation.evidence)
        ]
        if invalid_operations:
            errors.append(f"evidence: invalid operation evidence for {invalid_operations!r}")
        if not evidence_is_substring(note_text, extraction.final_answer.selected_evidence):
            errors.append("evidence: invalid selected evidence")
    return errors


def _repair_typed_operations_evidence_copy(
    extraction: TypedOperationsExtractionRecord,
    note_text: str,
) -> TypedOperationsExtractionRecord:
    operation_updates = [
        operation.model_copy(
            update={
                "evidence": repair_evidence_text_if_source_exact(operation.evidence, note_text)
            }
        )
        for operation in extraction.operations
    ]
    selection = extraction.selection.model_copy(
        update={
            "selected_evidence": repair_evidence_text_if_source_exact(
                extraction.selection.selected_evidence,
                note_text,
            )
        }
    )
    final_answer = extraction.final_answer.model_copy(
        update={
            "selected_evidence": repair_evidence_text_if_source_exact(
                extraction.final_answer.selected_evidence,
                note_text,
            )
        }
    )
    return extraction.model_copy(
        update={
            "operations": operation_updates,
            "selection": selection,
            "final_answer": final_answer,
        }
    )


def typed_operation_graph_overlay(
    extraction: TypedOperationsExtractionRecord | None,
    *,
    source_row_index: int | None = None,
    note_text: str = "",
) -> dict[str, Any]:
    """Project a state-node graph built only from model-extracted operations."""

    graph = _build_graph_from_typed_operations(
        extraction, source_row_index=source_row_index, note_text=note_text
    )
    projection = project_graph_to_gan(graph)
    return {
        "graph_builder": graph.graph_builder,
        "projection": projection.model_dump(mode="json"),
        "nodes": [_operation_node_row(node, extraction) for node in graph.nodes],
        "missing_variable_flags": graph.missing_variable_flags,
        "competing_hypothesis_node_ids": graph.competing_hypothesis_node_ids,
    }


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
    """Run the typed-operations reasoner over a smoke surface."""

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
    program = DspyTypedOperationsReasoner()
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
        typed_inputs = build_typed_operations_inputs(record)
        call_error: str | None = None
        prediction: Any | None = None
        if mode == "live":
            try:
                with dspy.context(lm=lm, adapter=adapter):
                    prediction = program(**typed_inputs)
            except Exception as exc:  # pragma: no cover - live API only.
                call_error = f"{type(exc).__name__}: {exc}"
        extraction, adapter_errors = (
            prediction_to_extraction(prediction, note_text=record.note_text)
            if prediction is not None
            else (None, ["not_run"])
        )
        parse_errors = [
            *adapter_errors,
            *validate_typed_operations_extraction(extraction, note_text=record.note_text),
        ]
        graph_overlay = typed_operation_graph_overlay(
            extraction, source_row_index=record.source_row_index, note_text=record.note_text
        )
        evidence_summary = _evidence_summary(record.note_text, extraction)
        score_layers = _score_layers(record, extraction, graph_overlay)
        repair_changes = _repair_changes(score_layers)
        component_status = _component_status(
            extraction=extraction,
            parse_errors=parse_errors,
            evidence_summary=evidence_summary,
            score_layers=score_layers,
            graph_overlay=graph_overlay,
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
                "structured_record": extraction.model_dump() if extraction else None,
                "typed_operation_graph": graph_overlay,
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
    """Summarize typed-operation smoke rows."""

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
        "selected_operation_trace_mismatches": sum(
            any(
                str(error).startswith("selected_operation_trace:")
                for error in row.get("parse_errors") or []
            )
            for row in rows
        ),
        "operation_graph_nodes": sum(
            len((row.get("typed_operation_graph") or {}).get("nodes") or []) for row in rows
        ),
        "component_failures": dict(sorted(component_failures.items())),
        "repair_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
    }
    for layer in SCORE_LAYER_NAMES:
        layer_summary = heavy_reasoner._layer_summary(rows, layer)
        for key, value in layer_summary.items():
            summary[f"{layer}_{key}"] = value
    summary.update(_graph_projection_deltas(rows))
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
    """Write a compact Markdown typed-operations report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    lines = [
        "# Gan 2026 LLM-Only Typed Operations Reasoner V0",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Architecture: `{PIPELINE_FAMILY}`",
        f"- Prompt/program version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Typed output schema version: `{metadata.get('typed_output_schema_version')}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Rows: {summary.get('examples', 0)}",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        (
            "- Claim language: LLM-heavy typed-operation extraction; graph projection is "
            "over model-extracted operation nodes."
        ),
        "",
        "## Typed Target",
        "",
        (
            "- Required operands: event count, time window, denominator, cluster size, "
            "seizure-free duration, temporal anchor, semiology grouping, uncertainty type, "
            "and selected evidence ID."
        ),
        "",
        "## Smoke Summary",
        "",
        (
            f"- Structured records: {summary.get('structured_records', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- Parse/schema failures: {summary.get('parse_or_validation_failures', 0)}",
        (
            f"- Selected evidence valid: {summary.get('selected_evidence_valid', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        (
            f"- Operation graph nodes: {summary.get('operation_graph_nodes', 0)}"
        ),
        (
            "- Selected-operation trace mismatches: "
            f"{summary.get('selected_operation_trace_mismatches', 0)}"
        ),
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
    lines.extend(["", "## Row Review", "", *_row_review_lines(rows), ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _build_graph_from_typed_operations(
    extraction: TypedOperationsExtractionRecord | None,
    *,
    source_row_index: int | None,
    note_text: str,
) -> ClinicalFrequencyStateGraph:
    nodes: list[StateGraphNode] = []
    if extraction is not None:
        for index, operation in enumerate(extraction.operations, start=1):
            selected_projection_label = _selected_projection_label(
                extraction,
                operation,
                note_text=note_text,
            )
            node = _node_from_operation(
                index,
                operation,
                note_text=note_text,
                selected_projection_label=selected_projection_label,
                is_selected=operation.operation_id
                in extraction.final_answer.selected_event_ids,
            )
            if node is not None:
                nodes.append(node)
    return ClinicalFrequencyStateGraph(
        source_row_index=source_row_index,
        nodes=tuple(nodes),
        competing_hypothesis_node_ids=tuple(node.node_id for node in nodes if len(nodes) > 1),
        missing_variable_flags=tuple(_missing_operation_variables(extraction)),
        graph_builder="llm_typed_operation_graph_overlay_v0",
        metadata={"operation_count": len(extraction.operations) if extraction else 0},
    )


def _node_from_operation(
    index: int,
    operation: TypedOperationRecord,
    *,
    note_text: str,
    selected_projection_label: str | None = None,
    is_selected: bool = False,
) -> StateGraphNode | None:
    label = _operation_label(
        operation,
        note_text=note_text,
        selected_projection_label=selected_projection_label,
    )
    if not label:
        return None
    try:
        frequency_record = label_to_frequency_record(label)
    except ValueError:
        return None
    span = locate_evidence(note_text, operation.evidence)
    start_char = span[0] if span is not None else None
    end_char = span[1] if span is not None else None
    return StateGraphNode(
        node_id=f"op:{operation.operation_id}",
        kind=_graph_node_kind(operation.operation_kind),
        normalized_label=frequency_record.normalized_label,
        semantic_kind=frequency_record.kind,
        monthly_frequency=frequency_record.monthly_frequency,
        evidence=EvidenceSpan(
            text=operation.evidence,
            start_char=start_char,
            end_char=end_char,
        ),
        assertion_status=operation.assertion_status,
        temporality=_graph_temporality(operation, is_selected=is_selected),
        certainty=operation.certainty,
        applies_to=operation.operands.semiology_grouping,
        rule_id=f"llm_typed_operation.{index}",
    )


def _operation_label(
    operation: TypedOperationRecord,
    *,
    note_text: str,
    selected_projection_label: str | None = None,
) -> str | None:
    raw_label_candidates = [
        selected_projection_label,
        _label_from_frequency_operands(operation),
        operation.raw_phrase,
        operation.model_normalized_clinical_label,
    ]
    sentinel_label: str | None = None
    for raw_label in raw_label_candidates:
        if not raw_label:
            continue
        raw_label = clean_semantically_neutral_text_artifacts(raw_label)
        label = repair_prediction_label_with_evidence(
            raw_label,
            operation.evidence,
            context_text=note_text,
        )
        if not _is_scorable_label(label):
            continue
        if _is_sentinel_fallback_for_operation(label, operation):
            sentinel_label = sentinel_label or label
            continue
        return label
    if sentinel_label is not None:
        return sentinel_label
    if selected_projection_label:
        selected_projection_label = clean_semantically_neutral_text_artifacts(
            selected_projection_label
        )
        if _is_scorable_label(selected_projection_label):
            return selected_projection_label
    if operation.model_normalized_clinical_label:
        return repair_prediction_label_format_preserving(
            clean_semantically_neutral_text_artifacts(operation.model_normalized_clinical_label)
        )
    if operation.operation_kind == "unknown_frequency":
        return "unknown"
    if operation.operation_kind == "no_reference":
        return "no seizure frequency reference"
    return None


def _label_from_frequency_operands(operation: TypedOperationRecord) -> str | None:
    if operation.operation_kind not in {"frequency_rate", "cluster_frequency"}:
        return None
    operands = operation.operands
    count = _operand_count_label(operands.event_count_low, operands.event_count_high)
    if count is None:
        return None
    period = _operand_period_label(
        operands.denominator_count,
        operands.denominator_unit,
        operands.time_window_low,
        operands.time_window_high,
        operands.time_window_unit,
    )
    if period is None:
        return None
    return f"{count} per {period}"


def _operand_count_label(low: float | None, high: float | None) -> str | None:
    if low is None and high is None:
        return None
    if low is None or low == 0:
        return _format_operand_number(high)
    if high is None or high == low:
        return _format_operand_number(low)
    return f"{_format_operand_number(low)} to {_format_operand_number(high)}"


def _operand_period_label(
    denominator_count: float | None,
    denominator_unit: str | None,
    time_window_low: float | None,
    time_window_high: float | None,
    time_window_unit: str | None,
) -> str | None:
    if denominator_unit and denominator_unit != "window":
        count = denominator_count if denominator_count not in (None, 0) else 1
        unit = _format_operand_unit(denominator_unit)
        if unit is None:
            return None
        if count == 1:
            return unit
        return f"{_format_operand_number(count)} {unit}"
    if time_window_unit and time_window_unit != "window":
        low = time_window_low
        high = time_window_high
        unit = _format_operand_unit(time_window_unit)
        if low is None or unit is None:
            return None
        if high is None or high == low:
            count = _format_operand_number(low)
        else:
            count = f"{_format_operand_number(low)} to {_format_operand_number(high)}"
        if count == "1":
            return unit
        return f"{count} {unit}"
    return None


def _format_operand_unit(unit: str | None) -> str | None:
    if unit in {"day", "week", "month", "year"}:
        return unit
    return None


def _format_operand_number(value: float | None) -> str | None:
    if value is None:
        return None
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def _selected_projection_label(
    extraction: TypedOperationsExtractionRecord,
    operation: TypedOperationRecord,
    *,
    note_text: str,
) -> str | None:
    if operation.operation_id not in extraction.final_answer.selected_event_ids:
        return None
    raw_label = extraction.final_answer.raw_llm_final_label
    if not raw_label:
        return None
    format_label = repair_prediction_label_format_preserving(raw_label)
    return repair_prediction_label_with_evidence(
        format_label,
        extraction.final_answer.selected_evidence,
        context_text=note_text,
    )


def _is_scorable_label(label: str | None) -> bool:
    if not label:
        return False
    try:
        label_to_frequency_record(label)
    except ValueError:
        return False
    return True


def _is_sentinel_fallback_for_operation(
    label: str,
    operation: TypedOperationRecord,
) -> bool:
    try:
        frequency_record = label_to_frequency_record(label)
    except ValueError:
        return False
    if operation.operation_kind == "unknown_frequency":
        return False
    if operation.operation_kind == "no_reference":
        return False
    return frequency_record.kind in {
        FrequencyLabelKind.UNKNOWN,
        FrequencyLabelKind.NO_REFERENCE,
    }


def _graph_temporality(operation: TypedOperationRecord, *, is_selected: bool) -> str:
    if (
        is_selected
        and operation.operation_kind in {"frequency_rate", "cluster_frequency"}
        and operation.temporality in {"current", "recent"}
    ):
        return "current"
    return operation.temporality


def _graph_node_kind(operation_kind: str) -> GraphNodeKind:
    return {
        "frequency_rate": GraphNodeKind.FREQUENCY_RATE,
        "cluster_frequency": GraphNodeKind.CLUSTER_FREQUENCY,
        "seizure_free": GraphNodeKind.SEIZURE_FREE,
        "last_event_only": GraphNodeKind.LAST_EVENT_ONLY,
        "unknown_frequency": GraphNodeKind.UNKNOWN_FREQUENCY,
        "no_reference": GraphNodeKind.NO_REFERENCE,
    }[operation_kind]


def _operation_node_row(
    node: StateGraphNode,
    extraction: TypedOperationsExtractionRecord | None,
) -> dict[str, Any]:
    operation = None
    if extraction is not None:
        operation = next(
            (
                candidate
                for candidate in extraction.operations
                if f"op:{candidate.operation_id}" == node.node_id
            ),
            None,
        )
    return {
        "node_id": node.node_id,
        "source_id": node.node_id,
        "kind": node.kind.value,
        "normalized_label": node.normalized_label,
        "semantic_kind": node.semantic_kind.value,
        "monthly_frequency": node.monthly_frequency,
        "evidence": node.evidence.text,
        "assertion_status": node.assertion_status,
        "temporality": node.temporality,
        "certainty": node.certainty,
        "applies_to": node.applies_to,
        "rule_id": node.rule_id,
        "selected_evidence_id": operation.evidence_id if operation else None,
        "operands": operation.operands.model_dump() if operation else None,
    }


def _missing_operation_variables(
    extraction: TypedOperationsExtractionRecord | None,
) -> list[str]:
    if extraction is None:
        return ["no_typed_operations"]
    missing: set[str] = set()
    for operation in extraction.operations:
        operands = operation.operands
        if operation.operation_kind in {"frequency_rate", "cluster_frequency"}:
            if operands.event_count_low is None and operands.event_count_high is None:
                missing.add("event_count")
            if operands.time_window_low is None and operands.denominator_unit is None:
                missing.add("time_window_or_denominator")
        if operation.operation_kind == "cluster_frequency" and operands.cluster_size_low is None:
            missing.add("cluster_size")
        if (
            operation.operation_kind == "seizure_free"
            and operands.seizure_free_duration_low is None
        ):
            missing.add("seizure_free_duration")
        if not operands.temporal_anchor:
            missing.add("temporal_anchor")
        if not operands.semiology_grouping:
            missing.add("semiology_grouping")
    return sorted(missing)


def _score_layers(
    record: GanFrequencyRecord,
    extraction: TypedOperationsExtractionRecord | None,
    graph_overlay: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    raw_label = heavy_reasoner._raw_final_label(extraction)
    format_label = repair_prediction_label_format_preserving(raw_label) if raw_label else None
    arithmetic_label = (
        repair_prediction_label_with_evidence(
            format_label,
            extraction.final_answer.selected_evidence,
        )
        if extraction and format_label
        else None
    )
    graph_label = (graph_overlay.get("projection") or {}).get("final_label")
    return {
        "raw_llm": heavy_reasoner._score_label(record, raw_label, repair_mode="raw_llm"),
        "format_only": heavy_reasoner._score_label(
            record, format_label, repair_mode="format_only"
        ),
        "selected_evidence_arithmetic": heavy_reasoner._score_label(
            record,
            arithmetic_label,
            repair_mode="selected_evidence_arithmetic",
        ),
        "typed_operation_graph_projection": heavy_reasoner._score_label(
            record,
            graph_label,
            repair_mode="typed_operation_graph_projection",
        ),
    }


def _evidence_summary(
    note_text: str,
    extraction: TypedOperationsExtractionRecord | None,
) -> dict[str, Any]:
    if extraction is None:
        return heavy_reasoner._empty_evidence_summary()
    invalid_operations = [
        {"event_id": operation.operation_id, "evidence": operation.evidence}
        for operation in extraction.operations
        if not evidence_is_substring(note_text, operation.evidence)
    ]
    selected_valid = evidence_is_substring(note_text, extraction.final_answer.selected_evidence)
    selected_operation_evidence_valid = extraction.final_answer.selected_evidence in {
        operation.evidence
        for operation in extraction.operations
        if operation.operation_id in extraction.final_answer.selected_event_ids
    }
    return {
        "event_evidence_valid": len(extraction.operations) - len(invalid_operations),
        "event_evidence_total": len(extraction.operations),
        "event_evidence_invalid": invalid_operations,
        "selected_evidence_valid": selected_valid,
        "selected_event_evidence_valid": selected_operation_evidence_valid,
        "selected_evidence": extraction.final_answer.selected_evidence,
    }


def _component_status(
    *,
    extraction: TypedOperationsExtractionRecord | None,
    parse_errors: Sequence[str],
    evidence_summary: Mapping[str, Any],
    score_layers: Mapping[str, Mapping[str, Any]],
    graph_overlay: Mapping[str, Any],
    call_error: str | None,
) -> dict[str, str]:
    status = {
        "typed_operations_parse": "ok",
        "operation_extraction": "ok",
        "operation_selection": "ok",
        "final_schema_rendering": "ok",
        "operation_graph_projection": "ok",
        "parse_schema": "ok",
        "evidence_exactness": "ok",
        "selected_operation_trace": "ok",
        "scorer_format": "ok",
    }
    if call_error or heavy_reasoner._has_blocking_parse_issue(parse_errors):
        status["parse_schema"] = "fail"
    if any(
        str(error).startswith("typed_operations_parse_or_validation_error:")
        for error in parse_errors
    ):
        status["typed_operations_parse"] = "fail"
    if extraction is None:
        status["operation_extraction"] = "fail"
        status["operation_selection"] = "fail"
        status["final_schema_rendering"] = "fail"
        status["operation_graph_projection"] = "fail"
        status["scorer_format"] = "fail"
        return status
    if not extraction.operations or any(
        str(error).startswith("operation_extraction:") for error in parse_errors
    ):
        status["operation_extraction"] = "fail"
    if any(str(error).startswith("selection:") for error in parse_errors):
        status["operation_selection"] = "fail"
    if any(str(error).startswith("final_answer:") for error in parse_errors):
        status["final_schema_rendering"] = "fail"
    if any(str(error).startswith("selected_operation_trace:") for error in parse_errors):
        status["selected_operation_trace"] = "fail"
    if evidence_summary.get("event_evidence_valid") != evidence_summary.get("event_evidence_total"):
        status["operation_extraction"] = "fail"
        status["evidence_exactness"] = "fail"
    if not evidence_summary.get("selected_evidence_valid"):
        status["final_schema_rendering"] = "fail"
        status["evidence_exactness"] = "fail"
    if not (graph_overlay.get("nodes") or []):
        status["operation_graph_projection"] = "fail"
    if not score_layers["raw_llm"].get("scorable"):
        status["scorer_format"] = "fail"
    return status


def _raw_output_from_extraction(extraction: TypedOperationsExtractionRecord | None) -> str:
    if extraction is None:
        return ""
    return json.dumps(extraction.model_dump(), sort_keys=True)


def _graph_projection_deltas(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "typed_graph_raw_wrong_to_correct": sum(
            (not bool((row.get("score_layers") or {}).get("raw_llm", {}).get("purist_correct")))
            and bool(
                (row.get("score_layers") or {})
                .get("typed_operation_graph_projection", {})
                .get("purist_correct")
            )
            for row in rows
        ),
        "typed_graph_raw_correct_to_wrong": sum(
            bool((row.get("score_layers") or {}).get("raw_llm", {}).get("purist_correct"))
            and not bool(
                (row.get("score_layers") or {})
                .get("typed_operation_graph_projection", {})
                .get("purist_correct")
            )
            for row in rows
        ),
    }


def _repair_changes(score_layers: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    raw_label = score_layers["raw_llm"].get("final_label")
    for layer in SCORE_LAYER_NAMES[1:]:
        current = score_layers[layer].get("final_label")
        if current != raw_label:
            changes.append(
                {
                    "layer": layer,
                    "from": str(raw_label),
                    "to": str(current),
                }
            )
    return changes


def _row_review_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for row in rows:
        layers = row.get("score_layers") or {}
        raw = layers.get("raw_llm") or {}
        graph = layers.get("typed_operation_graph_projection") or {}
        if raw.get("purist_correct") and graph.get("purist_correct"):
            continue
        lines.append(
            "- "
            f"{row.get('source_row_index')}: "
            f"gold `{((row.get('reference') or {}).get('gold_normalized_label'))}`; "
            f"raw `{raw.get('final_label')}`; "
            f"typed graph `{graph.get('final_label')}`"
        )
    if not lines:
        return ["- No raw misses or typed-graph projection regressions."]
    return lines


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
        "typed_operation_graph_projection_scorable": metadata["summary"][
            "typed_operation_graph_projection_scorable"
        ],
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
            "response_format_mode": (
                "scoped_dspy_context_json_adapter" if mode == "live" else "prompt_only_no_call"
            ),
            "typed_output_schema_version": TYPED_OUTPUT_SCHEMA_VERSION,
            "raw_model_owned_score_layer": "raw_llm",
            "side_car_score_layers": [
                "format_only",
                "selected_evidence_arithmetic",
                "typed_operation_graph_projection",
            ],
        },
    )
