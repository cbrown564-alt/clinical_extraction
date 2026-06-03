"""LLM-only simplified selected-state reasoner for Gan 2026 ablation A1."""

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

PROMPT_VERSION = "gan2026_llm_only_simplified_selected_state_reasoner_v0"
PIPELINE_FAMILY = "llm_only_simplified_selected_state_reasoner"
SIMPLIFIED_OUTPUT_SCHEMA_VERSION = "simplified_selected_state_v0"
SCORE_LAYER_NAMES = (
    "raw_llm",
    "format_only",
    "selected_evidence_arithmetic",
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_llm_only_simplified_selected_state_reasoner_validation25_gpt41mini_v0_2026-06-03.jsonl"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_llm_only_simplified_selected_state_reasoner_validation25_gpt41mini_v0_2026-06-03.md"
)


class SimplifiedSelectedState(BaseModel):
    """One model-owned clinical state plus its exact source evidence."""

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
    selection_reason: str = ""
    uncertainty_flags: list[str] = Field(default_factory=list)


class SimplifiedSelectedStateExtractionRecord(BaseModel):
    """Full A1 selection-only extraction returned by DSPy JSONAdapter."""

    model_config = ConfigDict(extra="forbid")

    selected_state: SimplifiedSelectedState


class Gan2026SimplifiedSelectedStateReasonerSignature(dspy.Signature):
    """Select one source-grounded seizure-frequency state."""

    note_text: str = dspy.InputField(desc="Full clinical note text.")
    task_instructions: list[str] = dspy.InputField(
        desc="Short selection-only clinical state instructions."
    )
    output_contract: dict[str, Any] = dspy.InputField(
        desc="Minimal selected-state output contract and enum values."
    )
    selected_state: SimplifiedSelectedState = dspy.OutputField(
        desc="One selected clinical state with exact evidence and no graph projection."
    )


class DspySimplifiedSelectedStateReasoner(dspy.Module):
    """DSPy typed-output program for the A1 selection-only lane."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(Gan2026SimplifiedSelectedStateReasonerSignature)

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


def build_selected_state_inputs(record: GanFrequencyRecord) -> dict[str, Any]:
    """Build model-facing A1 inputs without labels, candidates, or graph hints."""

    return {
        "note_text": record.note_text,
        "task_instructions": [
            "Read the full clinical note.",
            (
                "Choose exactly one current or clinically relevant seizure-frequency "
                "state for the note."
            ),
            (
                "Copy selected_evidence as an exact non-empty substring from the note. "
                "Do not paraphrase, normalize symbols, or copy administrative boilerplate."
            ),
            (
                "Use raw_source_phrase for the source-near selected phrase from that "
                "same evidence."
            ),
            (
                "Use raw_llm_final_label for your scorer-facing final label proposal, "
                "such as 4 per day, 1 per 7 to 9 day, multiple per month, seizure "
                "free for 6 month, unknown, or no seizure frequency reference."
            ),
            (
                "Keep frequency, seizure_free, unknown, no_reference, and "
                "unresolved_multiple states distinct."
            ),
            (
                "Prefer current/recent seizure-frequency evidence over historical, "
                "hypothetical, medication-use, rescue-medication, or proxy-only rates."
            ),
            "Return typed fields, not a string payload.",
            "Do not add any top-level outputs other than selected_state.",
            "This ablation has one selected clinical state and no graph projection.",
        ],
        "output_contract": {
            "prompt_version": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "typed_output_schema_version": SIMPLIFIED_OUTPUT_SCHEMA_VERSION,
            "top_level_outputs": ["selected_state"],
            "selected_state_fields": [
                "final_kind",
                "raw_llm_final_label",
                "selected_evidence",
                "raw_source_phrase",
                "selection_reason",
                "uncertainty_flags",
            ],
            "final_kind_values": [
                "frequency",
                "seizure_free",
                "unknown",
                "no_reference",
                "unresolved_multiple",
            ],
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
            "projection_rule": "No graph projection or operation matrix is used in A1.",
            "forbidden_inputs": [
                "gold annotations",
                "reference answers",
                "deterministic candidate lists",
                "state graph nodes",
            ],
        },
    }


def prediction_to_extraction(
    prediction: Any,
    *,
    note_text: str | None = None,
) -> tuple[SimplifiedSelectedStateExtractionRecord | None, list[str]]:
    """Validate a DSPy typed prediction into the local selected-state record."""

    try:
        extraction = SimplifiedSelectedStateExtractionRecord.model_validate(
            {"selected_state": prediction.selected_state}
        )
    except (AttributeError, TypeError, ValidationError) as exc:
        return None, [f"simplified_selected_state_parse_or_validation_error: {exc}"]
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


def validate_selected_state_extraction(
    extraction: SimplifiedSelectedStateExtractionRecord | None,
    *,
    note_text: str | None = None,
) -> list[str]:
    """Run selection-only source and trace validations."""

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
    """Run the A1 simplified selected-state reasoner over a split surface."""

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
    program = DspySimplifiedSelectedStateReasoner()
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
        selected_state_inputs = build_selected_state_inputs(record)
        call_error: str | None = None
        prediction: Any | None = None
        if mode == "live":
            try:
                with dspy.context(lm=lm, adapter=adapter):
                    prediction = program(**selected_state_inputs)
            except Exception as exc:  # pragma: no cover - live API only.
                call_error = f"{type(exc).__name__}: {exc}"
        extraction, adapter_errors = (
            prediction_to_extraction(prediction, note_text=record.note_text)
            if prediction is not None
            else (None, ["not_run"])
        )
        parse_errors = [
            *adapter_errors,
            *validate_selected_state_extraction(extraction, note_text=record.note_text),
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
                "typed_input": selected_state_inputs,
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
    """Summarize A1 selected-state smoke rows."""

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
        "component_failures": dict(sorted(component_failures.items())),
        "repair_changed_rows": sum(bool(row.get("repair_changes")) for row in rows),
    }
    for layer in SCORE_LAYER_NAMES:
        layer_summary = heavy_reasoner._layer_summary(rows, layer)
        for key, value in layer_summary.items():
            summary[f"{layer}_{key}"] = value
    summary.update(_selected_evidence_adapter_deltas(rows))
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
    """Write a compact Markdown A1 report."""

    path.parent.mkdir(parents=True, exist_ok=True)
    summary = metadata.get("summary") or summarize_records(rows)
    lines = [
        "# Gan 2026 LLM-Only Simplified Selected State Reasoner V0",
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
            "- Claim language: LLM-only selection-only validation development result; "
            "format-only and selected-evidence arithmetic are deterministic adapter layers."
        ),
        "",
        "## A1 Target",
        "",
        "- one selected clinical state.",
        "- Exact selected evidence.",
        "- No graph projection.",
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
                "- Selected-evidence arithmetic raw-wrong to correct: "
                f"{summary.get('selected_evidence_arithmetic_raw_wrong_to_correct', 0)}"
            ),
            (
                "- Selected-evidence arithmetic raw-correct to wrong: "
                f"{summary.get('selected_evidence_arithmetic_raw_correct_to_wrong', 0)}"
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
    extraction: SimplifiedSelectedStateExtractionRecord | None,
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
    }


def _raw_final_label(extraction: SimplifiedSelectedStateExtractionRecord | None) -> str | None:
    if extraction is None:
        return None
    state = extraction.selected_state
    if state.final_kind == "unknown" and not state.raw_llm_final_label.strip():
        return "unknown"
    if state.final_kind == "no_reference" and not state.raw_llm_final_label.strip():
        return "no seizure frequency reference"
    return state.raw_llm_final_label


def _evidence_summary(
    note_text: str,
    extraction: SimplifiedSelectedStateExtractionRecord | None,
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
    extraction: SimplifiedSelectedStateExtractionRecord | None,
    parse_errors: Sequence[str],
    evidence_summary: Mapping[str, Any],
    score_layers: Mapping[str, Mapping[str, Any]],
    call_error: str | None,
) -> dict[str, str]:
    status = {
        "simplified_selected_state_parse": "ok",
        "selected_state_selection": "ok",
        "parse_schema": "ok",
        "evidence_exactness": "ok",
        "selected_state_trace": "ok",
        "scorer_format": "ok",
    }
    if call_error or heavy_reasoner._has_blocking_parse_issue(parse_errors):
        status["parse_schema"] = "fail"
    if any(
        str(error).startswith("simplified_selected_state_parse_or_validation_error:")
        for error in parse_errors
    ):
        status["simplified_selected_state_parse"] = "fail"
    if extraction is None:
        status["selected_state_selection"] = "fail"
        status["scorer_format"] = "fail"
        return status
    if any(str(error).startswith("selected_state:") for error in parse_errors):
        status["selected_state_selection"] = "fail"
    if any(str(error).startswith("selected_state_trace:") for error in parse_errors):
        status["selected_state_trace"] = "fail"
    if not evidence_summary.get("selected_evidence_valid"):
        status["evidence_exactness"] = "fail"
    if not score_layers["raw_llm"].get("scorable"):
        status["scorer_format"] = "fail"
    return status


def _raw_output_from_extraction(
    extraction: SimplifiedSelectedStateExtractionRecord | None,
) -> str:
    if extraction is None:
        return ""
    return json.dumps(extraction.model_dump(), sort_keys=True)


def _selected_evidence_adapter_deltas(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "selected_evidence_arithmetic_raw_wrong_to_correct": sum(
            (not bool((row.get("score_layers") or {}).get("raw_llm", {}).get("purist_correct")))
            and bool(
                (row.get("score_layers") or {})
                .get("selected_evidence_arithmetic", {})
                .get("purist_correct")
            )
            for row in rows
        ),
        "selected_evidence_arithmetic_raw_correct_to_wrong": sum(
            bool((row.get("score_layers") or {}).get("raw_llm", {}).get("purist_correct"))
            and not bool(
                (row.get("score_layers") or {})
                .get("selected_evidence_arithmetic", {})
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
        selected = layers.get("selected_evidence_arithmetic") or {}
        if raw.get("purist_correct") and selected.get("purist_correct"):
            continue
        lines.append(
            "- "
            f"{row.get('source_row_index')}: "
            f"gold `{((row.get('reference') or {}).get('gold_normalized_label'))}`; "
            f"raw `{raw.get('final_label')}`; "
            f"selected-evidence `{selected.get('final_label')}`"
        )
    if not lines:
        return ["- No raw misses or selected-evidence adapter regressions."]
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
        "selected_evidence_arithmetic_scorable": metadata["summary"][
            "selected_evidence_arithmetic_scorable"
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
            "typed_output_schema_version": SIMPLIFIED_OUTPUT_SCHEMA_VERSION,
            "raw_model_owned_score_layer": "raw_llm",
            "side_car_score_layers": [
                "format_only",
                "selected_evidence_arithmetic",
            ],
            "graph_projection_enabled": False,
        },
    )
