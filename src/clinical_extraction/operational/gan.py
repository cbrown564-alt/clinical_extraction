"""Operational wrapper for cited Gan cell 3 and cell 5."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from clinical_extraction.operational.io import InputNote
from clinical_extraction.operational.runtime import RuntimeConfig
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    DspyStructuredExtractor,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    GAN_LLM_EXTRACT,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_select import (
    GAN_LLM_SELECT_POLICY_EXAMPLES,
    build_llm_select_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.select_from_extract import (
    GAN_LLM_SELECT_FROM_EXTRACT,
    apply_llm_select,
    extract_events_as_select_ledger,
    parse_extract_ledger,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)

GanOperationalMethod = Literal["llm_extract", "llm_select"]
DEFAULT_GAN_METHOD: GanOperationalMethod = "llm_extract"


def complete_structured_prompt(prompt_input_json: str) -> str:
    prediction = DspyStructuredExtractor()(prompt_input_json=prompt_input_json)
    return str(prediction.structured_json)


def run_gan_notes(
    notes: Sequence[InputNote],
    runtime: RuntimeConfig,
    *,
    method: GanOperationalMethod = DEFAULT_GAN_METHOD,
) -> list[dict[str, Any]]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
        llm_with_rules,
    )

    if method not in ("llm_extract", "llm_select"):
        raise ValueError(f"unsupported Gan method: {method}")
    config = PipelineConfiguration(
        architecture="rules",
        dspy_cache=False,
        model=runtime.model,
        temperature=runtime.temperature,
        max_tokens=runtime.max_tokens,
        api_base=runtime.base_url,
        api_key=runtime.api_key,
        timeout=int(runtime.timeout_seconds),
        prompt_version=GAN_LLM_EXTRACT,
        repair_mode="raw_model" if method == "llm_select" else None,
    )
    pipeline = (
        GAN_LLM_SELECT_FROM_EXTRACT if method == "llm_select" else GAN_LLM_EXTRACT
    )
    prompt_version = (
        GAN_LLM_SELECT_POLICY_EXAMPLES if method == "llm_select" else GAN_LLM_EXTRACT
    )
    output: list[dict[str, Any]] = []
    for index, note in enumerate(notes):
        record = _note_record(index, note)
        try:
            result = llm_with_rules.run_record(record, config)
            if method == "llm_select":
                output.append(
                    _select_row(note, runtime, result, pipeline, prompt_version)
                )
            else:
                output.append(
                    _extract_row(note, runtime, result, pipeline, prompt_version)
                )
        except Exception as exc:
            output.append(_error_row(note.note_id, runtime.api_model, pipeline, exc))
    return output


def score_projection(final_label: str | None) -> dict[str, Any] | None:
    """Project a predicted Gan label into scorer categories without gold comparison."""

    if not final_label:
        return None
    try:
        record = label_to_frequency_record(final_label)
    except ValueError:
        return None
    return {
        "normalized_label": record.normalized_label,
        "kind": str(record.kind),
        "monthly_frequency": record.monthly_frequency,
        "yearly_bounds": (
            list(record.yearly_bounds) if record.yearly_bounds is not None else None
        ),
        "purist_category": str(map_purist(record.monthly_frequency)),
        "pragmatic_category": str(map_pragmatic(record.monthly_frequency)),
    }


def _note_record(index: int, note: InputNote) -> GanFrequencyRecord:
    empty_label = label_to_frequency_record("unknown")
    return GanFrequencyRecord(
        source_row_index=index,
        note_text=note.text,
        gold_label="unknown",
        gold_reference="",
        labels_match_all_categories=False,
        quotes_ok_all_categories=False,
        row_ok=True,
        raw={"id": note.note_id},
        gold_normalized_label=empty_label.normalized_label,
        gold_label_kind=empty_label.kind,
        gold_yearly_bounds=empty_label.yearly_bounds,
        gold_monthly_frequency=empty_label.monthly_frequency,
    )


def _extract_row(
    note: InputNote,
    runtime: RuntimeConfig,
    result: Any,
    pipeline: str,
    prompt_version: str,
) -> dict[str, Any]:
    return {
        "id": note.note_id,
        "task": "gan",
        "status": "ok",
        "model": runtime.api_model,
        "pipeline": pipeline,
        "prompt_version": prompt_version,
        "prediction": {
            "seizure_frequency": result.output.final_value,
            "evidence": result.output.evidence,
            "rationale": result.output.rationale,
        },
        "parse_errors": result.diagnostics.get("parse_errors", []),
        "structured_record": result.diagnostics.get("structured_record"),
        "score_projection": score_projection(result.output.final_value),
    }


def _select_row(
    note: InputNote,
    runtime: RuntimeConfig,
    result: Any,
    pipeline: str,
    prompt_version: str,
) -> dict[str, Any]:
    raw_output = str(result.diagnostics.get("raw_output") or "")
    extract = parse_extract_ledger(raw_output, note_text=note.text)
    encoded_events = extract_events_as_select_ledger(extract)
    select_raw = complete_structured_prompt(
        build_llm_select_prompt_input(
            encoded_events,
            extract_selected_event_ids=extract.selection.selected_event_ids,
            extract_label=extract.selection.final_label,
        )
    )
    submitted = apply_llm_select(extract, select_raw, encoded_events)
    final_label = submitted.selection.final_label
    return {
        "id": note.note_id,
        "task": "gan",
        "status": "ok",
        "model": runtime.api_model,
        "pipeline": pipeline,
        "prompt_version": prompt_version,
        "prediction": {
            "seizure_frequency": final_label,
            "evidence": submitted.selection.evidence,
            "rationale": submitted.selection.rationale,
        },
        "parse_errors": result.diagnostics.get("parse_errors", []),
        "structured_record": submitted.model_dump(),
        "score_projection": score_projection(final_label),
    }


def _error_row(
    note_id: str, model: str, pipeline: str, exc: Exception
) -> dict[str, Any]:
    return {
        "id": note_id,
        "task": "gan",
        "status": "error",
        "model": model,
        "pipeline": pipeline,
        "error": {"type": type(exc).__name__, "message": str(exc)},
    }
