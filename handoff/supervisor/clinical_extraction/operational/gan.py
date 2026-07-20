"""Operational wrapper for the selected Gan LLM-with-rules pipeline."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from clinical_extraction.operational.io import InputNote
from clinical_extraction.operational.runtime import RuntimeConfig
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def run_gan_notes(notes: Sequence[InputNote], runtime: RuntimeConfig) -> list[dict[str, Any]]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners import (
        hybrid_structured_events as runner,
    )

    hybrid_structured_events.set_active_prompt_version(
        hybrid_structured_events.PROMPT_VERSION_V0_5
    )
    config = PipelineConfiguration(
        architecture="hybrid_structured_events",
        dspy_cache=False,
        model=runtime.model,
        temperature=runtime.temperature,
        max_tokens=runtime.max_tokens,
        api_base=runtime.base_url,
        api_key=runtime.api_key,
        timeout=int(runtime.timeout_seconds),
    )
    empty_label = label_to_frequency_record("unknown")
    output: list[dict[str, Any]] = []
    for index, note in enumerate(notes):
        record = GanFrequencyRecord(
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
        try:
            result = runner.run_item(record, config)
            output.append(
                {
                    "id": note.note_id,
                    "task": "gan",
                    "status": "ok",
                    "model": runtime.api_model,
                    "pipeline": "llm_with_rules",
                    "prompt_version": hybrid_structured_events.PROMPT_VERSION_V0_5,
                    "prediction": {
                        "seizure_frequency": result.output.final_value,
                        "evidence": result.output.evidence,
                        "rationale": result.output.rationale,
                    },
                    "parse_errors": result.diagnostics.get("parse_errors", []),
                    "structured_record": result.diagnostics.get("structured_record"),
                }
            )
        except Exception as exc:
            output.append(_error_row(note.note_id, runtime.api_model, exc))
    return output


def _error_row(note_id: str, model: str, exc: Exception) -> dict[str, Any]:
    return {
        "id": note_id,
        "task": "gan",
        "status": "error",
        "model": model,
        "pipeline": "llm_with_rules",
        "error": {"type": type(exc).__name__, "message": str(exc)},
    }
