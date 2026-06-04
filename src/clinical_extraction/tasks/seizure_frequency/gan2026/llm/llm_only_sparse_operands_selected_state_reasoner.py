"""LLM-only selected-state reasoner with sparse numeric details."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.core.evidence import (
    evidence_is_substring,
    repair_evidence_text_if_source_exact,
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

PROMPT_VERSION = "gan2026_llm_only_sparse_operands_selected_state_reasoner_v1_boundaryfix"
PIPELINE_FAMILY = "llm_only_sparse_operands_selected_state_reasoner"
SPARSE_OPERANDS_SCHEMA_VERSION = "sparse_operands_selected_state_v0"
SCORE_LAYER_NAMES = (
    "raw_llm",
    "format_only",
    "selected_evidence_arithmetic",
    "sparse_operand_adapter",
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_sparse_operands_selected_state_reasoner_validation25_gpt41mini_v1_boundaryfix_2026-06-03.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_sparse_operands_selected_state_reasoner_validation25_gpt41mini_v1_boundaryfix_2026-06-03.md"
)


class SparseSelectedOperands(BaseModel):
    """Nullable numeric details for the single selected state."""

    model_config = ConfigDict(extra="forbid")

    count_low: int | None = None
    count_high: int | None = None
    period_count_low: int | None = None
    period_count_high: int | None = None
    period_unit: Literal["day", "week", "month", "year"] | None = None
    cluster_count: int | None = None
    seizures_per_cluster_low: int | None = None
    seizures_per_cluster_high: int | None = None
    seizure_free_duration_count: int | None = None
    seizure_free_duration_unit: Literal["day", "week", "month", "year"] | None = None
    abstain_reason: str = ""


class SparseOperandsSelectedState(BaseModel):
    """One model-owned clinical state plus exact evidence and numeric details."""

    model_config = ConfigDict(extra="forbid")

    final_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    raw_llm_final_label: str
    selected_evidence: str
    raw_source_phrase: str
    selected_operation_kind: Literal[
        "frequency_rate",
        "cluster_frequency",
        "seizure_free",
        "unknown_frequency",
        "no_reference",
    ]
    operands: SparseSelectedOperands = Field(default_factory=SparseSelectedOperands)
    selection_reason: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)


class SparseOperandsSelectedStateExtractionRecord(BaseModel):
    """Full A2 extraction returned by DSPy JSONAdapter."""

    model_config = ConfigDict(extra="forbid")

    selected_state: SparseOperandsSelectedState


class Gan2026SparseOperandsSelectedStateReasonerSignature(dspy.Signature):
    """Select one source-grounded seizure-frequency state with sparse operands."""

    note_text: str = dspy.InputField(desc="Full clinical note text.")
    task_instructions: list[str] = dspy.InputField(
        desc="Clinical state selection instructions."
    )
    output_contract: dict[str, Any] = dspy.InputField(
        desc="Selected-state output contract with nullable numeric details."
    )
    selected_state: SparseOperandsSelectedState = dspy.OutputField(
        desc="One selected clinical state with exact evidence and numeric details."
    )


class DspySparseOperandsSelectedStateReasoner(dspy.Module):
    """DSPy typed-output program for the A2 sparse-operands lane."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026SparseOperandsSelectedStateReasonerSignature)

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


def build_sparse_operands_inputs(record: GanFrequencyRecord) -> dict[str, Any]:
    """Build model-facing inputs without labels, candidates, or graph hints."""

    return {
        "note_text": record.note_text,
        "task_instructions": [
            "Read the full clinical note.",
            "Choose exactly one current or clinically relevant seizure-frequency state.",
            (
                "Copy selected_evidence as an exact non-empty substring from the note. "
                "Do not paraphrase, normalize symbols, or copy administrative boilerplate."
            ),
            "Use raw_source_phrase for the selected phrase copied from that evidence.",
            (
                "Use raw_llm_final_label for your seizure-frequency answer, such as 4 per "
                "day, 1 per 7 to 9 day, multiple per month, seizure free for 6 month, "
                "unknown, or no seizure frequency reference."
            ),
            (
                "Fill numeric detail fields only when the selected evidence directly states "
                "the count, interval, cluster, or seizure-free duration."
            ),
            (
                "Leave numeric detail fields null and write abstain_reason when a numeric "
                "answer would be unsafe, unclear, historical, medication-use only, or based "
                "only on indirect context."
            ),
            (
                "Do not render vague multiple wording as a numeric count. If the selected "
                "state is multiple per day/week/month/year, keep count fields null and "
                "preserve the multiple label."
            ),
            (
                "For cluster wording, fill count and period fields only for explicit "
                "cluster cadence. Do not use cluster duration such as over 1-2 days as "
                "seizure count; leave event-count fields null unless the evidence states "
                "events per cluster."
            ),
            (
                "For unknown or no-reference states, keep numeric detail fields null; do "
                "not force a number from tempting but unsafe text."
            ),
            "Return typed fields, not a string payload.",
            "Do not add any top-level outputs other than selected_state.",
        ],
        "output_contract": {
            "top_level_outputs": ["selected_state"],
            "selected_state_fields": [
                "final_kind",
                "raw_llm_final_label",
                "selected_evidence",
                "raw_source_phrase",
                "selected_operation_kind",
                "operands",
                "selection_reason",
                "uncertainty_flags",
            ],
            "field_descriptions": {
                "final_kind": "Broad answer type for the selected state.",
                "raw_llm_final_label": (
                    "Seizure-frequency answer written from the selected evidence."
                ),
                "selected_evidence": "Exact note substring that supports the answer.",
                "raw_source_phrase": "Short phrase copied from selected_evidence.",
                "selected_operation_kind": "Type of clinical statement selected from the note.",
                "operands": (
                    "Numeric details such as count, timeframe, cluster size, or "
                    "seizure-free duration."
                ),
                "selection_reason": "Brief reason for choosing this state.",
                "uncertainty_flags": "Short notes about uncertainty, or an empty list.",
            },
            "final_kind_values": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
            "selected_operation_kind_values": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "unknown_frequency",
                "no_reference",
            ],
            "numeric_detail_fields": [
                "count_low",
                "count_high",
                "period_count_low",
                "period_count_high",
                "period_unit",
                "cluster_count",
                "seizures_per_cluster_low",
                "seizures_per_cluster_high",
                "seizure_free_duration_count",
                "seizure_free_duration_unit",
                "abstain_reason",
            ],
            "numeric_detail_field_descriptions": {
                "count_low": "Lowest stated seizure count.",
                "count_high": "Highest stated seizure count, if a range is given.",
                "period_count_low": "Lowest stated timeframe count.",
                "period_count_high": "Highest stated timeframe count, if a range is given.",
                "period_unit": "Time unit for the stated rate.",
                "cluster_count": "Number of clusters, if stated.",
                "seizures_per_cluster_low": "Lowest stated seizures per cluster.",
                "seizures_per_cluster_high": "Highest stated seizures per cluster.",
                "seizure_free_duration_count": "Duration count for seizure-free statements.",
                "seizure_free_duration_unit": "Time unit for seizure-free duration.",
                "abstain_reason": "Reason numeric details were left blank.",
            },
            "evidence_copy_rule": {
                "required": "selected_evidence must be an exact non-empty note substring",
                "forbidden": [
                    "paraphrase",
                    "normalized mathematical symbols",
                    "HTML entities",
                    "escaped Unicode",
                    "control characters",
                ],
            },
            "selection_rule": "Numeric details may only describe the selected state.",
            "forbidden_inputs": [
                "reference annotations",
                "reference answers",
                "candidate lists",
                "state nodes",
            ],
        },
    }


def prediction_to_extraction(
    prediction: Any,
    *,
    note_text: str | None = None,
) -> tuple[SparseOperandsSelectedStateExtractionRecord | None, list[str]]:
    """Validate a DSPy typed prediction into the local A2 record."""

    try:
        extraction = SparseOperandsSelectedStateExtractionRecord.model_validate(
            {"selected_state": prediction.selected_state}
        )
    except (AttributeError, TypeError, ValidationError) as exc:
        return None, [f"sparse_operands_parse_or_validation_error: {exc}"]
    if note_text is not None:
        state = extraction.selected_state
        extraction = extraction.model_copy(
            update={
                "selected_state": state.model_copy(
                    update={
                        "selected_evidence": repair_evidence_text_if_source_exact(
                            state.selected_evidence,
                            note_text,
                        ),
                        "raw_source_phrase": repair_evidence_text_if_source_exact(
                            state.raw_source_phrase,
                            note_text,
                        ),
                    }
                )
            }
        )
    return extraction, []


def validate_sparse_operands_extraction(
    extraction: SparseOperandsSelectedStateExtractionRecord | None,
    *,
    note_text: str | None = None,
) -> list[str]:
    """Run A2 source, trace, and operand-boundary validations."""

    if extraction is None:
        return []
    errors: list[str] = []
    state = extraction.selected_state
    selected_evidence_valid = True
    if not state.selected_evidence.strip():
        errors.append("evidence: missing selected evidence")
        selected_evidence_valid = False
    if note_text is not None and not evidence_is_substring(note_text, state.selected_evidence):
        errors.append("evidence: invalid selected evidence")
        selected_evidence_valid = False
    if (
        selected_evidence_valid
        and state.raw_source_phrase
        and state.raw_source_phrase not in state.selected_evidence
    ):
        errors.append("selected_state_trace: raw_source_phrase not in selected_evidence")
    if not state.raw_llm_final_label.strip():
        errors.append("selected_state: missing raw_llm_final_label")
    if state.final_kind in {"unknown", "no_reference"} and _operands_have_numeric_value(
        state.operands
    ):
        errors.append("sparse_operands_boundary: numeric operands on sentinel state")
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
    """Run the A2 sparse-operands reasoner over a split surface."""

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
    program = DspySparseOperandsSelectedStateReasoner()
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
        typed_inputs = build_sparse_operands_inputs(record)
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
            *validate_sparse_operands_extraction(extraction, note_text=record.note_text),
        ]
        evidence_summary = _evidence_summary(record.note_text, extraction)
        score_layers = _score_layers(record, extraction)
        repair_changes = _repair_changes(score_layers)
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
                "structured_record": extraction.model_dump() if extraction else None,
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
    """Summarize A2 sparse-operands rows."""

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
        "selected_evidence_valid": sum(
            int(bool((row.get("evidence_summary") or {}).get("selected_evidence_valid")))
            for row in rows
        ),
        "selected_state_trace_mismatches": sum(
            any(
                str(error).startswith("selected_state_trace:")
                for error in row.get("parse_errors") or []
            )
            for row in rows
        ),
        "sparse_operand_boundary_failures": sum(
            any(
                str(error).startswith("sparse_operands_boundary:")
                for error in row.get("parse_errors") or []
            )
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
    """Write a compact Markdown A2 report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    lines = [
        "# Gan 2026 LLM-Only Sparse Operands Selected State Reasoner",
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
            "- Claim language: LLM-only sparse-operands validation development "
            "result; format, selected-evidence, and operand rendering are "
            "separate adapter layers."
        ),
        "",
        "## A2 Target",
        "",
        "- one selected clinical state.",
        "- Exact selected evidence.",
        "- Sparse nullable operands for selected count, interval, cluster, or duration.",
        "- No operation graph projection.",
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
            "- Selected-state trace mismatches: "
            f"{summary.get('selected_state_trace_mismatches', 0)}"
        ),
        (
            "- Sparse operand boundary failures: "
            f"{summary.get('sparse_operand_boundary_failures', 0)}"
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
            "## Adapter Delta",
            "",
            (
                "- Sparse operand adapter selected-evidence wrong to correct: "
                f"{summary.get('sparse_operand_adapter_selected_wrong_to_correct', 0)}"
            ),
            (
                "- Sparse operand adapter selected-evidence correct to wrong: "
                f"{summary.get('sparse_operand_adapter_selected_correct_to_wrong', 0)}"
            ),
            "",
            "## Row Review",
            "",
            *_row_review_lines(rows),
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _score_layers(
    record: GanFrequencyRecord,
    extraction: SparseOperandsSelectedStateExtractionRecord | None,
) -> dict[str, dict[str, Any]]:
    raw_label = _raw_final_label(extraction)
    format_label = repair_prediction_label_format_preserving(raw_label) if raw_label else None
    selected_evidence_label = (
        repair_prediction_label_with_evidence(
            format_label,
            extraction.selected_state.selected_evidence,
            context_text=record.note_text,
        )
        if extraction and format_label
        else None
    )
    sparse_operand_label = (
        _sparse_operand_adapter_label(extraction, selected_evidence_label)
        or selected_evidence_label
    )
    return {
        "raw_llm": heavy_reasoner._score_label(record, raw_label, repair_mode="raw_llm"),
        "format_only": heavy_reasoner._score_label(
            record, format_label, repair_mode="format_only"
        ),
        "selected_evidence_arithmetic": heavy_reasoner._score_label(
            record,
            selected_evidence_label,
            repair_mode="selected_evidence_arithmetic",
        ),
        "sparse_operand_adapter": heavy_reasoner._score_label(
            record,
            sparse_operand_label,
            repair_mode="sparse_operand_adapter",
        ),
    }


def _raw_final_label(
    extraction: SparseOperandsSelectedStateExtractionRecord | None,
) -> str | None:
    if extraction is None:
        return None
    state = extraction.selected_state
    if state.final_kind == "unknown" and not state.raw_llm_final_label.strip():
        return "unknown"
    if state.final_kind == "no_reference" and not state.raw_llm_final_label.strip():
        return "no seizure frequency reference"
    return state.raw_llm_final_label


def _state_should_defer_to_arithmetic(state: SparseOperandsSelectedState) -> bool:
    text = " ".join(
        (
            state.raw_llm_final_label,
            state.selected_evidence,
            state.raw_source_phrase,
        )
    ).lower()

    if "bimonthly" in text:
        return True
    if "perimenstrual" in text or "menstrual" in text or "cyclical" in text:
        return True
    if "every other" in text:
        return True

    import re
    if re.search(r"\bq[a-z0-9\-]+", text):
        return True
    if "hour" in text or "/h" in text:
        return True

    return False


def _sparse_operand_adapter_label(
    extraction: SparseOperandsSelectedStateExtractionRecord | None,
    selected_evidence_label: str | None = None,
) -> str | None:
    if extraction is None:
        return None
    state = extraction.selected_state
    operands = state.operands
    if state.final_kind == "unknown":
        if selected_evidence_label and selected_evidence_label not in {
            "unknown",
            "no seizure frequency reference",
        }:
            return None
        return "unknown"
    if state.final_kind == "no_reference":
        if selected_evidence_label and selected_evidence_label not in {
            "unknown",
            "no seizure frequency reference",
        }:
            return None
        return "no seizure frequency reference"
    if state.final_kind == "seizure_free":
        if operands.seizure_free_duration_count and operands.seizure_free_duration_unit:
            return (
                f"seizure free for {operands.seizure_free_duration_count} "
                f"{operands.seizure_free_duration_unit}"
            )
        return None
    if state.final_kind != "frequency":
        return None
    if _state_mentions_unresolved_multiple(state):
        return None
    if _state_should_defer_to_arithmetic(state):
        return None
    if state.selected_operation_kind == "cluster_frequency":
        return None
    if (
        operands.count_low is None
        or operands.period_count_low is None
        or operands.period_unit is None
    ):
        return None
    count = _render_range(operands.count_low, operands.count_high)
    period = _render_range(operands.period_count_low, operands.period_count_high)
    return f"{count} per {period} {operands.period_unit}"


def _render_range(low: int, high: int | None) -> str:
    if high is None or high == low:
        return str(low)
    return f"{low} to {high}"


def _state_mentions_unresolved_multiple(state: SparseOperandsSelectedState) -> bool:
    text = " ".join(
        (
            state.raw_llm_final_label,
            state.selected_evidence,
            state.raw_source_phrase,
        )
    ).lower()
    return "multiple" in text


def _evidence_summary(
    note_text: str,
    extraction: SparseOperandsSelectedStateExtractionRecord | None,
) -> dict[str, Any]:
    if extraction is None:
        return {
            "selected_evidence_valid": False,
            "selected_evidence": None,
        }
    evidence = extraction.selected_state.selected_evidence
    return {
        "selected_evidence_valid": bool(evidence.strip())
        and evidence_is_substring(note_text, evidence),
        "selected_evidence": evidence,
    }


def _component_status(
    *,
    extraction: SparseOperandsSelectedStateExtractionRecord | None,
    parse_errors: Sequence[str],
    evidence_summary: Mapping[str, Any],
    score_layers: Mapping[str, Mapping[str, Any]],
    call_error: str | None,
) -> dict[str, str]:
    status = {
        "sparse_operands_parse": "ok",
        "selected_state_selection": "ok",
        "parse_schema": "ok",
        "evidence_exactness": "ok",
        "selected_state_trace": "ok",
        "sparse_operands_boundary": "ok",
        "scorer_format": "ok",
    }
    if call_error or heavy_reasoner._has_blocking_parse_issue(parse_errors):
        status["parse_schema"] = "fail"
    if any(
        str(error).startswith("sparse_operands_parse_or_validation_error:")
        for error in parse_errors
    ):
        status["sparse_operands_parse"] = "fail"
    if extraction is None:
        status["selected_state_selection"] = "fail"
        status["scorer_format"] = "fail"
        return status
    if any(str(error).startswith("selected_state:") for error in parse_errors):
        status["selected_state_selection"] = "fail"
    if any(str(error).startswith("selected_state_trace:") for error in parse_errors):
        status["selected_state_trace"] = "fail"
    if any(str(error).startswith("sparse_operands_boundary:") for error in parse_errors):
        status["sparse_operands_boundary"] = "fail"
    if not evidence_summary.get("selected_evidence_valid"):
        status["evidence_exactness"] = "fail"
    if not score_layers["raw_llm"].get("scorable"):
        status["scorer_format"] = "fail"
    return status


def _raw_output_from_extraction(
    extraction: SparseOperandsSelectedStateExtractionRecord | None,
) -> str:
    if extraction is None:
        return ""
    return json.dumps(extraction.model_dump(), sort_keys=True)


def _adapter_deltas(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "sparse_operand_adapter_selected_wrong_to_correct": sum(
            (
                not bool(
                    (row.get("score_layers") or {})
                    .get("selected_evidence_arithmetic", {})
                    .get("purist_correct")
                )
            )
            and bool(
                (row.get("score_layers") or {})
                .get("sparse_operand_adapter", {})
                .get("purist_correct")
            )
            for row in rows
        ),
        "sparse_operand_adapter_selected_correct_to_wrong": sum(
            bool(
                (row.get("score_layers") or {})
                .get("selected_evidence_arithmetic", {})
                .get("purist_correct")
            )
            and not bool(
                (row.get("score_layers") or {})
                .get("sparse_operand_adapter", {})
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
        selected = layers.get("selected_evidence_arithmetic") or {}
        sparse = layers.get("sparse_operand_adapter") or {}
        if selected.get("purist_correct") and sparse.get("purist_correct"):
            continue
        lines.append(
            "- "
            f"{row.get('source_row_index')}: "
            f"gold `{((row.get('reference') or {}).get('gold_normalized_label'))}`; "
            f"selected-evidence `{selected.get('final_label')}`; "
            f"sparse-operands `{sparse.get('final_label')}`"
        )
    if not lines:
        return ["- No selected-evidence misses or sparse-operand adapter regressions."]
    return lines


def _emit_progress_checkpoint(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
) -> None:
    checkpoint_metadata = dict(metadata)
    checkpoint_metadata["summary"] = summarize_records(rows)
    checkpoint_metadata["checkpoint"] = {
        "completed_rows": len(rows),
        "total_rows": total,
    }
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None:
        write_report(rows, checkpoint_metadata, report_path, jsonl_path=jsonl_path or Path(""))
    print(
        json.dumps(
            {
                "pipeline": PIPELINE_FAMILY,
                "completed_rows": len(rows),
                "total_rows": total,
                "summary": checkpoint_metadata["summary"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


def _run_metadata(
    records: Sequence[GanFrequencyRecord],
    *,
    split: str,
    split_manifest: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: str,
    api_base: str | None,
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
            "typed_output_schema_version": SPARSE_OPERANDS_SCHEMA_VERSION,
            "raw_model_owned_score_layer": "raw_llm",
            "side_car_score_layers": [
                "format_only",
                "selected_evidence_arithmetic",
                "sparse_operand_adapter",
            ],
            "graph_projection_enabled": False,
            "ablation": "A2_sparse_operands_selected_state",
        },
    )


def _operands_have_numeric_value(operands: SparseSelectedOperands) -> bool:
    return any(
        value is not None
        for value in (
            operands.count_low,
            operands.count_high,
            operands.period_count_low,
            operands.period_count_high,
            operands.cluster_count,
            operands.seizures_per_cluster_low,
            operands.seizures_per_cluster_high,
            operands.seizure_free_duration_count,
        )
    )
