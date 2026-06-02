"""Decision 0007 LLM-heavy evidence selection with mechanical adapters."""

from __future__ import annotations

import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
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
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
    repair_prediction_label_format_preserving,
)

PROMPT_VERSION = "gan2026_llm_heavy_evidence_selection_deterministic_adapters_v0"
PIPELINE_FAMILY = "llm_heavy_evidence_selection_with_deterministic_adapters"
TYPED_OUTPUT_SCHEMA_VERSION = "selected_fact_operands_v0"
SCORE_LAYER_NAMES = (
    "raw_model_parser_label",
    "raw_model_clinical_selection",
    "format_only_repair",
    "mechanical_adapter_label",
    "benchmark_convention_adapter",
)
PRIMARY_SCORE_LAYER = "mechanical_adapter_label"
DEFAULT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_"
    "gpt41mini_v0_2026-06-02.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/"
    "gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_"
    "gpt41mini_v0_2026-06-02.md"
)


class SelectedClinicalFact(BaseModel):
    """Model-owned clinical fact and exact evidence packet."""

    model_config = ConfigDict(extra="forbid")

    fact_id: str
    clinical_kind: Literal[
        "frequency",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
        "unresolved_multiple",
    ]
    applies_to: str | None = None
    evidence: str
    raw_value: str
    temporality: Literal["current", "recent", "historical", "unclear"]
    assertion_status: Literal["asserted", "negated", "hypothetical", "uncertain"]
    competing_fact_summary: str = ""
    rationale: str = ""
    benchmark_caveat_flags: list[
        Literal[
            "bimonthly",
            "biweekly",
            "vague_count",
            "compact_interval",
            "total_window_statement",
            "cluster_axis",
            "duration_calculation",
        ]
    ] = Field(default_factory=list)


class FrequencyOperands(BaseModel):
    """Typed frequency operands selected by the model."""

    model_config = ConfigDict(extra="forbid")

    occurrences_low: float | None = None
    occurrences_high: float | None = None
    denominator_low: float | None = None
    denominator_high: float | None = None
    denominator_unit: Literal["day", "week", "month", "year"] | None = None
    vague_count: Literal["multiple", "rare", "occasional", "frequent"] | None = None


class ClusterOperands(BaseModel):
    """Typed cluster operands selected by the model."""

    model_config = ConfigDict(extra="forbid")

    clusters_low: float | None = None
    clusters_high: float | None = None
    cluster_period_low: float | None = None
    cluster_period_high: float | None = None
    cluster_period_unit: Literal["day", "week", "month", "year"] | None = None
    events_per_cluster_low: float | None = None
    events_per_cluster_high: float | None = None
    cluster_answer_axis: Literal["cluster_cadence", "event_burden"] = "cluster_cadence"


class SeizureFreeOperands(BaseModel):
    """Typed seizure-free operands selected by the model."""

    model_config = ConfigDict(extra="forbid")

    seizure_free_evidence: str | None = None
    last_event_evidence: str | None = None
    clinic_or_reference_date: str | None = None
    duration_low: float | None = None
    duration_high: float | None = None
    duration_unit: Literal["day", "week", "month", "year"] | None = None


class SelectedOperands(BaseModel):
    """All mechanical adapter operands emitted by the model."""

    model_config = ConfigDict(extra="forbid")

    frequency: FrequencyOperands | None = None
    cluster: ClusterOperands | None = None
    seizure_free: SeizureFreeOperands | None = None


class RawModelClinicalAnswer(BaseModel):
    """Diagnostic raw model parser-facing answer."""

    model_config = ConfigDict(extra="forbid")

    raw_model_parser_label: str
    raw_model_final_kind: Literal[
        "frequency",
        "cluster_frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    selected_evidence: str
    confidence: Literal["high", "medium", "low"]
    clinical_rationale: str = ""


class LlmHeavyEvidenceSelectionRecord(BaseModel):
    """Full typed Decision 0007 output."""

    model_config = ConfigDict(extra="forbid")

    selected_fact: SelectedClinicalFact
    operands: SelectedOperands
    raw_model_answer: RawModelClinicalAnswer


@dataclass(frozen=True)
class MechanicalAdapterResult:
    final_label: str | None
    adapter_families: tuple[str, ...]
    operand_complete: bool
    error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "final_label": self.final_label,
            "adapter_families": list(self.adapter_families),
            "operand_complete": self.operand_complete,
            "error": self.error,
        }


class Gan2026LlmHeavyEvidenceSelectionSignature(dspy.Signature):
    """Select the clinical fact and operands with typed DSPy JSON output fields."""

    note_text: str = dspy.InputField(desc="Full Gan 2026 note text.")
    task_instructions: list[str] = dspy.InputField(
        desc="Decision 0007 clinical-selection and operand-exposure instructions."
    )
    output_contract: dict[str, Any] = dspy.InputField(
        desc="Typed selected-fact, evidence, and operand contract."
    )
    selected_fact: SelectedClinicalFact = dspy.OutputField(
        desc="Model-owned selected clinical fact packet with exact evidence."
    )
    operands: SelectedOperands = dspy.OutputField(
        desc="Typed operands used by deterministic mechanical adapters."
    )
    raw_model_answer: RawModelClinicalAnswer = dspy.OutputField(
        desc="Diagnostic raw parser-facing model label and selected evidence."
    )


class DspyLlmHeavyEvidenceSelectionReasoner(dspy.Module):
    """DSPy typed-output program for the Decision 0007 smoke."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026LlmHeavyEvidenceSelectionSignature)

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


def build_typed_inputs(record: GanFrequencyRecord) -> dict[str, Any]:
    """Build typed DSPy inputs without gold labels or deterministic candidates."""

    return {
        "note_text": record.note_text,
        "task_instructions": [
            "Read only the clinical note; do not use deterministic candidates or gold labels.",
            (
                "Decision 0007 boundary: the model selects the clinical fact, exact "
                "evidence, temporal state, assertion status, competing fact summary, "
                "and operands."
            ),
            (
                "Deterministic code will only render parser-ready labels from those "
                "selected operands. It must not choose a different clinical fact."
            ),
            "Copy selected_fact.evidence and raw_model_answer.selected_evidence exactly.",
            (
                "Expose frequency operands for count/range over a denominator; cluster "
                "operands for cluster cadence and events per cluster; seizure-free "
                "operands for duration rendering."
            ),
            "Return typed fields, not an opaque JSON string payload.",
        ],
        "output_contract": {
            "prompt_version": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "typed_output_schema_version": TYPED_OUTPUT_SCHEMA_VERSION,
            "top_level_outputs": ["selected_fact", "operands", "raw_model_answer"],
            "clinical_kinds": [
                "frequency",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
                "unresolved_multiple",
            ],
            "adapter_families": [
                "parser_ready_label_grammar",
                "arithmetic_from_selected_operands",
                "total_window_rendering",
                "seizure_free_duration",
                "cluster_syntax_rendering",
                "benchmark_convention_adapter",
            ],
            "selected_fact_trace_rule": (
                "raw_model_answer.selected_evidence must equal selected_fact.evidence"
            ),
        },
    }


def prediction_to_extraction(
    prediction: Any,
) -> tuple[LlmHeavyEvidenceSelectionRecord | None, list[str]]:
    """Validate a DSPy typed prediction into the local extraction record."""

    try:
        extraction = LlmHeavyEvidenceSelectionRecord.model_validate(
            {
                "selected_fact": prediction.selected_fact,
                "operands": prediction.operands,
                "raw_model_answer": prediction.raw_model_answer,
            }
        )
    except (AttributeError, TypeError, ValidationError) as exc:
        return None, [f"adapter_parse_or_validation_error: {exc}"]
    return extraction, []


def validate_typed_extraction(
    extraction: LlmHeavyEvidenceSelectionRecord | None,
    *,
    note_text: str | None = None,
) -> list[str]:
    """Validate selected evidence exactness and selected-fact trace integrity."""

    if extraction is None:
        return []
    errors: list[str] = []
    if extraction.raw_model_answer.selected_evidence != extraction.selected_fact.evidence:
        errors.append("selected_fact_trace: raw_model_answer evidence differs from selected_fact")
    if note_text is not None:
        if not evidence_is_substring(note_text, extraction.selected_fact.evidence):
            errors.append("evidence: invalid selected_fact evidence")
        if not evidence_is_substring(note_text, extraction.raw_model_answer.selected_evidence):
            errors.append("evidence: invalid raw_model_answer selected evidence")
        sf_operands = extraction.operands.seizure_free
        if sf_operands is not None:
            if sf_operands.seizure_free_evidence and not evidence_is_substring(
                note_text, sf_operands.seizure_free_evidence
            ):
                errors.append("evidence: invalid seizure_free operand evidence")
            if sf_operands.last_event_evidence and not evidence_is_substring(
                note_text, sf_operands.last_event_evidence
            ):
                errors.append("evidence: invalid last_event operand evidence")
    return errors


def mechanical_adapter_label(
    extraction: LlmHeavyEvidenceSelectionRecord | None,
) -> MechanicalAdapterResult:
    """Render the primary adapted label only from model-selected operands."""

    if extraction is None:
        return MechanicalAdapterResult(None, (), False, "missing_extraction")
    kind = extraction.selected_fact.clinical_kind
    if kind == "frequency":
        return _frequency_adapter(extraction.operands.frequency)
    if kind == "cluster_frequency":
        return _cluster_adapter(extraction.operands.cluster)
    if kind in {"seizure_free", "last_event_only"}:
        return _seizure_free_adapter(extraction.operands.seizure_free)
    if kind in {"unknown_frequency", "unresolved_multiple"}:
        return MechanicalAdapterResult("unknown", ("parser_ready_label_grammar",), True)
    if kind == "no_reference":
        return MechanicalAdapterResult(
            "no seizure frequency reference",
            ("parser_ready_label_grammar",),
            True,
        )
    return MechanicalAdapterResult(None, (), False, f"unsupported_kind:{kind}")


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
    """Run the Decision 0007 LLM-heavy validation smoke surface."""

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
    program = DspyLlmHeavyEvidenceSelectionReasoner()
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
        typed_inputs = build_typed_inputs(record)
        call_error: str | None = None
        prediction: Any | None = None
        if mode == "live":
            try:
                with dspy.context(lm=lm, adapter=adapter):
                    prediction = program(**typed_inputs)
            except Exception as exc:  # pragma: no cover - live API path.
                call_error = f"{type(exc).__name__}: {exc}"
        extraction, adapter_errors = (
            prediction_to_extraction(prediction) if prediction is not None else (None, ["not_run"])
        )
        parse_errors = [
            *adapter_errors,
            *validate_typed_extraction(extraction, note_text=record.note_text),
        ]
        mechanical = mechanical_adapter_label(extraction)
        score_layers = _score_layers(record, extraction, mechanical)
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
                "evidence_summary": _evidence_summary(record.note_text, extraction),
                "mechanical_adapter": mechanical.as_dict(),
                "component_status": _component_status(
                    extraction=extraction,
                    parse_errors=parse_errors,
                    mechanical=mechanical,
                    score_layers=score_layers,
                    call_error=call_error,
                ),
                "score_layers": score_layers,
                "repair_changes": _repair_changes(score_layers),
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
    """Summarize the Decision 0007 validation smoke."""

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
        "selected_evidence_valid": sum(
            int(bool((row.get("evidence_summary") or {}).get("selected_evidence_valid")))
            for row in rows
        ),
        "selected_fact_trace_mismatches": sum(
            any(
                str(error).startswith("selected_fact_trace:")
                for error in row.get("parse_errors") or []
            )
            for row in rows
        ),
        "operand_complete_rows": sum(
            int(bool((row.get("mechanical_adapter") or {}).get("operand_complete")))
            for row in rows
        ),
        "component_failures": dict(sorted(component_failures.items())),
        "repair_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
    }
    for layer in SCORE_LAYER_NAMES:
        layer_summary = heavy_reasoner._layer_summary(rows, layer)
        for key, value in layer_summary.items():
            summary[f"{layer}_{key}"] = value
    summary.update(_adapter_deltas(rows))
    summary["decision_0007_outcome"] = _decision_0007_outcome(summary)
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
    """Write a compact Markdown Decision 0007 validation25 report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    outcome = str(summary.get("decision_0007_outcome", "revise"))
    lines = [
        "# Gan 2026 LLM-Heavy Evidence Selection With Deterministic Adapters",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Architecture: `{PIPELINE_FAMILY}`",
        "- Claim language: LLM-heavy clinical selection with deterministic mechanical adapters.",
        f"- Prompt/program version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Typed output schema version: `{metadata.get('typed_output_schema_version')}`",
        f"- Split: `{metadata.get('split')}` / `{metadata.get('split_manifest')}`",
        f"- Rows: {summary.get('examples', 0)}",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Primary adapted layer: `{PRIMARY_SCORE_LAYER}`",
        f"- Decision 0007 outcome: `{outcome}`",
        "",
        "## Predeclared Smoke",
        "",
        "- Surface: `validation25` under `gan2026_split_v1`.",
        (
            "- Primary question: can typed selected fact/evidence/operand output support "
            "mechanical adapters without deterministic clinical replacement?"
        ),
        "- Stop rule: promotion requires the Decision 0007 validation25 gate.",
        "",
        "## Smoke Summary",
        "",
        (
            f"- Structured typed outputs: {summary.get('structured_records', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- Adapter parse failures: {summary.get('adapter_parse_failures', 0)}",
        (
            f"- Selected evidence exact: {summary.get('selected_evidence_valid', 0)}/"
            f"{summary.get('examples', 0)}"
        ),
        f"- Selected fact trace mismatches: {summary.get('selected_fact_trace_mismatches', 0)}",
        (
            f"- Selected operand completeness: {summary.get('operand_complete_rows', 0)}/"
            f"{summary.get('examples', 0)}"
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
    lines.extend(
        [
            "",
            "## Adapter Gate",
            "",
            (
                f"- Adapted-label Purist: "
                f"{summary.get('mechanical_adapter_label_purist_correct', 0)}/"
                f"{summary.get('examples', 0)}"
            ),
            (
                "- Adapter raw-wrong to correct: "
                f"{summary.get('mechanical_adapter_raw_wrong_to_correct', 0)}"
            ),
            (
                "- Adapter raw-correct to wrong: "
                f"{summary.get('mechanical_adapter_raw_correct_to_wrong', 0)}"
            ),
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


def _frequency_adapter(operands: FrequencyOperands | None) -> MechanicalAdapterResult:
    if operands is None:
        return MechanicalAdapterResult(None, (), False, "missing_frequency_operands")
    if operands.vague_count and operands.denominator_unit:
        if operands.vague_count == "multiple":
            period = _period_label(
                operands.denominator_low,
                operands.denominator_high,
                operands.denominator_unit,
            )
            return MechanicalAdapterResult(
                f"multiple per {period}",
                ("arithmetic_from_selected_operands",),
                True,
            )
    if (
        operands.occurrences_low is None
        or operands.denominator_low is None
        or operands.denominator_unit is None
    ):
        return MechanicalAdapterResult(None, (), False, "incomplete_frequency_operands")
    count = _range_label(operands.occurrences_low, operands.occurrences_high)
    period = _period_label(
        operands.denominator_low,
        operands.denominator_high,
        operands.denominator_unit,
    )
    return MechanicalAdapterResult(
        f"{count} per {period}",
        ("arithmetic_from_selected_operands",),
        True,
    )


def _cluster_adapter(operands: ClusterOperands | None) -> MechanicalAdapterResult:
    if operands is None:
        return MechanicalAdapterResult(None, (), False, "missing_cluster_operands")
    if (
        operands.clusters_low is None
        or operands.cluster_period_low is None
        or operands.cluster_period_unit is None
    ):
        return MechanicalAdapterResult(None, (), False, "incomplete_cluster_operands")
    clusters = _range_label(operands.clusters_low, operands.clusters_high)
    period = _period_label(
        operands.cluster_period_low,
        operands.cluster_period_high,
        operands.cluster_period_unit,
    )
    if operands.events_per_cluster_low is None:
        per_cluster = "multiple"
    else:
        per_cluster = _range_label(
            operands.events_per_cluster_low,
            operands.events_per_cluster_high,
        )
    return MechanicalAdapterResult(
        f"{clusters} cluster per {period}, {per_cluster} per cluster",
        ("cluster_syntax_rendering",),
        True,
    )


def _seizure_free_adapter(operands: SeizureFreeOperands | None) -> MechanicalAdapterResult:
    if operands is None:
        return MechanicalAdapterResult(None, (), False, "missing_seizure_free_operands")
    if operands.duration_low is None or operands.duration_unit is None:
        return MechanicalAdapterResult(None, (), False, "incomplete_seizure_free_operands")
    duration = _period_label(operands.duration_low, operands.duration_high, operands.duration_unit)
    return MechanicalAdapterResult(
        f"seizure free for {duration}",
        ("seizure_free_duration",),
        True,
    )


def _score_layers(
    record: GanFrequencyRecord,
    extraction: LlmHeavyEvidenceSelectionRecord | None,
    mechanical: MechanicalAdapterResult,
) -> dict[str, dict[str, Any]]:
    raw_label = _raw_model_label(extraction)
    format_label = repair_prediction_label_format_preserving(raw_label) if raw_label else None
    mechanical_label = mechanical.final_label
    benchmark_label = repair_prediction_label(mechanical_label) if mechanical_label else None
    return {
        "raw_model_parser_label": heavy_reasoner._score_label(
            record,
            raw_label,
            repair_mode="raw_model_parser_label",
        ),
        "raw_model_clinical_selection": heavy_reasoner._score_label(
            record,
            raw_label,
            repair_mode="raw_model_clinical_selection",
        ),
        "format_only_repair": heavy_reasoner._score_label(
            record,
            format_label,
            repair_mode="format_only_repair",
        ),
        "mechanical_adapter_label": heavy_reasoner._score_label(
            record,
            mechanical_label,
            repair_mode="mechanical_adapter_label",
        ),
        "benchmark_convention_adapter": heavy_reasoner._score_label(
            record,
            benchmark_label,
            repair_mode="benchmark_convention_adapter",
        ),
    }


def _repair_changes(score_layers: Mapping[str, Mapping[str, Any]]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    raw_label = score_layers["raw_model_parser_label"].get("final_label")
    for layer in SCORE_LAYER_NAMES[1:]:
        current = score_layers[layer].get("final_label")
        if isinstance(raw_label, str) and isinstance(current, str) and current != raw_label:
            changes.append({"layer": layer, "before": raw_label, "after": current})
    return changes


def _raw_model_label(extraction: LlmHeavyEvidenceSelectionRecord | None) -> str | None:
    if extraction is None:
        return None
    label = extraction.raw_model_answer.raw_model_parser_label
    if label:
        return label
    kind = extraction.raw_model_answer.raw_model_final_kind
    if kind == "unknown":
        return "unknown"
    if kind == "no_reference":
        return "no seizure frequency reference"
    return None


def _evidence_summary(
    note_text: str,
    extraction: LlmHeavyEvidenceSelectionRecord | None,
) -> dict[str, Any]:
    if extraction is None:
        return {
            "selected_evidence_valid": False,
            "selected_fact_evidence": None,
            "raw_model_selected_evidence": None,
        }
    selected_valid = evidence_is_substring(note_text, extraction.selected_fact.evidence)
    raw_selected_valid = evidence_is_substring(
        note_text,
        extraction.raw_model_answer.selected_evidence,
    )
    return {
        "selected_evidence_valid": selected_valid and raw_selected_valid,
        "selected_fact_evidence": extraction.selected_fact.evidence,
        "raw_model_selected_evidence": extraction.raw_model_answer.selected_evidence,
    }


def _component_status(
    *,
    extraction: LlmHeavyEvidenceSelectionRecord | None,
    parse_errors: Sequence[str],
    mechanical: MechanicalAdapterResult,
    score_layers: Mapping[str, Mapping[str, Any]],
    call_error: str | None,
) -> dict[str, str]:
    status = {
        "typed_selected_fact_parse": "ok",
        "clinical_selection": "ok",
        "evidence_exactness": "ok",
        "selected_fact_trace": "ok",
        "selected_operand_completeness": "ok",
        "mechanical_adapter_rendering": "ok",
        "raw_parser_label": "ok",
    }
    if call_error or heavy_reasoner._has_blocking_parse_issue(parse_errors):
        status["typed_selected_fact_parse"] = "fail"
    if extraction is None:
        status["clinical_selection"] = "fail"
        status["selected_operand_completeness"] = "fail"
        status["mechanical_adapter_rendering"] = "fail"
        status["raw_parser_label"] = "fail"
        return status
    if any(str(error).startswith("selected_fact_trace:") for error in parse_errors):
        status["selected_fact_trace"] = "fail"
    if any(str(error).startswith("evidence:") for error in parse_errors):
        status["evidence_exactness"] = "fail"
    if not mechanical.operand_complete:
        status["selected_operand_completeness"] = "fail"
    if mechanical.final_label is None or not score_layers["mechanical_adapter_label"].get(
        "scorable"
    ):
        status["mechanical_adapter_rendering"] = "fail"
    if not score_layers["raw_model_parser_label"].get("scorable"):
        status["raw_parser_label"] = "fail"
    return status


def _adapter_deltas(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    raw_wrong_to_correct = 0
    raw_correct_to_wrong = 0
    for row in rows:
        layers = row.get("score_layers") or {}
        raw = layers.get("raw_model_parser_label") or {}
        adapted = layers.get("mechanical_adapter_label") or {}
        raw_correct = bool(raw.get("purist_correct"))
        adapted_correct = bool(adapted.get("purist_correct"))
        if not raw_correct and adapted_correct:
            raw_wrong_to_correct += 1
        if raw_correct and not adapted_correct:
            raw_correct_to_wrong += 1
    return {
        "mechanical_adapter_raw_wrong_to_correct": raw_wrong_to_correct,
        "mechanical_adapter_raw_correct_to_wrong": raw_correct_to_wrong,
    }


def _decision_0007_outcome(summary: Mapping[str, Any]) -> str:
    examples = int(summary.get("examples", 0))
    if examples == 0:
        return "reject"
    blocking_reject = any(
        (
            int(summary.get("structured_records", 0)) < examples,
            int(summary.get("call_failures", 0)) > 0,
            int(summary.get("adapter_parse_failures", 0)) > 1,
            int(summary.get("selected_evidence_valid", 0)) < min(23, examples),
            int(summary.get("selected_fact_trace_mismatches", 0)) > 0,
            int(summary.get("operand_complete_rows", 0)) < min(23, examples),
            int(summary.get("mechanical_adapter_raw_correct_to_wrong", 0)) > 1,
        )
    )
    if blocking_reject:
        return "reject"
    if int(summary.get("mechanical_adapter_label_purist_correct", 0)) >= min(22, examples):
        return "promote_to_validation50_allowed_by_gate"
    return "revise"


def _row_review_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    lines: list[str] = []
    for row in rows:
        layers = row.get("score_layers") or {}
        raw = layers.get("raw_model_parser_label") or {}
        adapted = layers.get("mechanical_adapter_label") or {}
        if raw.get("purist_correct") and adapted.get("purist_correct"):
            continue
        if raw.get("purist_correct") and not adapted.get("purist_correct"):
            status = "adapter regression"
        elif not raw.get("purist_correct") and adapted.get("purist_correct"):
            status = "mechanical adapter gain"
        else:
            status = "raw and adapted miss"
        lines.append(
            "- "
            f"{row.get('source_row_index')}: {status}; "
            f"gold `{((row.get('reference') or {}).get('gold_normalized_label'))}`; "
            f"raw `{raw.get('final_label')}`; "
            f"adapted `{adapted.get('final_label')}`; "
            f"taxonomy `{_failure_family(row)}`"
        )
    if not lines:
        return ["- No raw misses or mechanical-adapter regressions."]
    return lines


def _failure_taxonomy_lines(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    counts = Counter(_failure_family(row) for row in rows)
    return [f"- `{family}`: {count}" for family, count in sorted(counts.items())]


def _failure_family(row: Mapping[str, Any]) -> str:
    if row.get("call_error"):
        return "call_failure"
    errors = row.get("parse_errors") or []
    if any(str(error).startswith("adapter_parse_or_validation_error:") for error in errors):
        return "typed_schema_parse_failure"
    if any(str(error).startswith("selected_fact_trace:") for error in errors):
        return "selected_fact_trace_mismatch"
    if any(str(error).startswith("evidence:") for error in errors):
        return "exact_evidence_failure"
    mechanical = row.get("mechanical_adapter") or {}
    if not mechanical.get("operand_complete"):
        return "missing_selected_operands"
    layers = row.get("score_layers") or {}
    adapted = layers.get("mechanical_adapter_label") or {}
    if not adapted.get("scorable"):
        return "adapter_rendering_failure"
    if not adapted.get("purist_correct"):
        return "wrong_selected_clinical_fact_or_operand"
    return "ok"


def _interpretation_text(outcome: str) -> str:
    if outcome == "promote_to_validation50_allowed_by_gate":
        return (
            "This validation25 Decision 0007 smoke passes the typed-output and "
            "mechanical-adapter gate. Escalation may be considered only as a separately "
            "predeclared validation50 run."
        )
    if outcome == "reject":
        return (
            "This validation25 Decision 0007 smoke fails at least one hard selected-fact, "
            "evidence, operand, or adapter gate. Do not escalate this artifact."
        )
    return (
        "This validation25 Decision 0007 smoke is interpretable but not promotable. "
        "Triage wrong selected fact, evidence exactness, missing operands, then adapter rendering."
    )


def _raw_output_from_extraction(extraction: LlmHeavyEvidenceSelectionRecord | None) -> str:
    if extraction is None:
        return ""
    return json.dumps(extraction.model_dump(), sort_keys=True)


def _range_label(low: float, high: float | None) -> str:
    low_text = _number_label(low)
    if high is None or high == low:
        return low_text
    return f"{low_text} to {_number_label(high)}"


def _period_label(low: float | None, high: float | None, unit: str) -> str:
    if low is None:
        return unit
    return f"{_range_label(low, high)} {unit}"


def _number_label(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


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
        "mechanical_adapter_scorable": metadata["summary"]["mechanical_adapter_label_scorable"],
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
            "claim_type": "llm_heavy_clinical_selection_with_deterministic_adapters",
            "pipeline_name": PROMPT_VERSION,
            "pipeline_family": "llm_heavy",
            "score_layers_to_report": list(SCORE_LAYER_NAMES),
            "primary_score_layer": PRIMARY_SCORE_LAYER,
            "dspy_adapter": "JSONAdapter",
            "response_format_mode": "scoped_dspy_context_json_adapter",
            "typed_output_schema_version": TYPED_OUTPUT_SCHEMA_VERSION,
            "model_role": "LLM-owned clinical fact, evidence, temporal state, and operands",
            "deterministic_role": "mechanical rendering from model-selected operands only",
            "schema_smoke_stop_rule": {
                "surface": "validation25 under gan2026_split_v1",
                "call_success_minimum": "25/25",
                "typed_structured_outputs_minimum": "25/25",
                "selected_evidence_exactness_minimum": "23/25",
                "selected_operand_completeness_minimum": "23/25",
                "selected_fact_trace_mismatches_maximum": "0/25",
                "adapted_label_purist_minimum": "22/25",
                "raw_correct_to_adapter_wrong_maximum": "1/25",
            },
        },
    )
