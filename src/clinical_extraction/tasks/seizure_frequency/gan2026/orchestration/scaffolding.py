"""Shared orchestrator scaffolding for Gan 2026 LLM pipelines."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.contracts import (
    GanRecordResult,
    GanStageEvent,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)


def configure_live_lm(config: PipelineConfiguration) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.runners.lm import configure_lm

    configure_lm(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        dspy_cache=config.dspy_cache,
        api_base=config.api_base,
        api_key=config.api_key,
        timeout=config.timeout,
    )


def configure_split_lm(
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    dspy_cache: bool,
    api_base: str | None,
) -> None:
    import dspy

    from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

    dspy.configure(
        lm=build_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=dspy_cache,
            api_base=api_base,
        )
    )


def common_split_metadata_updates(
    *,
    dspy_cache: bool,
    reuse_source: str | None,
    escalation_reason: str | None,
) -> dict[str, Any]:
    return {
        "dspy_cache": dspy_cache,
        "reuse_source": reuse_source,
        "escalation_reason": escalation_reason,
    }


def envelope_model_call_error(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def first_prediction_changing_owner(
    stage_events: Sequence[GanStageEvent],
) -> str | None:
    return next(
        (
            event.owner
            for event in stage_events
            if event.changed and event.effect_class == "clinical_meaning"
        ),
        None,
    )


def attach_row_scoring(
    result: GanRecordResult,
    *,
    record: GanFrequencyRecord,
    compare_fn: Callable[..., Any],
    parsed: Any,
) -> dict[str, Any]:
    row_trace = dict(result.diagnostics["row_trace"])
    comparison = compare_fn(record, parsed) if parsed else None
    row_trace["scoring"] = comparison
    return row_trace


def maybe_emit_progress_checkpoint(
    rows: list[dict[str, Any]],
    metadata: dict[str, Any],
    *,
    total: int,
    progress_every: int | None,
    jsonl_path: Path | None,
    report_path: Path | None,
    emit_fn: Callable[..., None],
) -> None:
    if progress_every and len(rows) % progress_every == 0:
        emit_fn(
            rows,
            metadata,
            total=total,
            jsonl_path=jsonl_path,
            report_path=report_path,
        )


def finalize_split_metadata(
    rows: list[dict[str, Any]],
    metadata: Mapping[str, Any],
    summarize_fn: Callable[[list[dict[str, Any]]], Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    finalized = dict(metadata)
    finalized["summary"] = summarize_fn(rows)
    return rows, finalized
