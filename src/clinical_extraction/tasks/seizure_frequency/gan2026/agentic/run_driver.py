"""Shared split-run driver for legacy Gan 2026 agentic stage modules.

Unmigrated agentic monoliths duplicate row loops, metadata assembly, DSPy
configuration, and progress checkpointing. This module extracts that ceremony
so stages can supply only ``build_row`` and summary/gate hooks.

Migrated stages using :class:`stage_protocol.AgenticStage` should prefer
``stage_protocol`` helpers directly; use this driver when migrating legacy
inline ``run_split`` implementations incrementally (see P3-1).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.stage_protocol import (
    build_stage_metadata,
    configure_dspy_for_stage,
    emit_progress_checkpoint,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)


@dataclass(frozen=True)
class SplitRunParams:
    """Common Gan 2026 split-run parameters shared across agentic stages."""

    split: str
    split_manifest: str
    model: str
    temperature: float
    max_tokens: int
    mode: Literal["live", "prompt-only"]
    dspy_cache: bool
    api_base: str | None
    progress_every: int | None = None
    checkpoint_jsonl_path: Path | None = None
    checkpoint_report_path: Path | None = None


RowBuilder = Callable[..., dict[str, Any]]
SummarizeRows = Callable[[Sequence[Mapping[str, Any]]], dict[str, Any]]
GateInterpretation = Callable[[Mapping[str, Any]], dict[str, Any]]
WriteReport = Callable[..., None]
RowsBySourceIndex = Callable[[Sequence[Mapping[str, Any]]], Mapping[int, Mapping[str, Any]]]


def run_standard_split(
    records: Sequence[GanFrequencyRecord],
    *,
    params: SplitRunParams,
    prompt_version: str,
    metadata_extra: Mapping[str, Any],
    build_row: RowBuilder,
    summarize_rows: SummarizeRows,
    gate_interpretation: GateInterpretation | None = None,
    write_report: WriteReport | None = None,
    progress_fields: Sequence[str] = (
        "call_failures",
        "parse_or_validation_failures",
        "purist_correct",
    ),
    row_kwargs: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run a standard per-record split loop with shared metadata and checkpoints."""
    if params.mode == "live":
        configure_dspy_for_stage(
            model=params.model,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            cache=params.dspy_cache,
            api_base=params.api_base,
        )

    metadata = build_stage_metadata(
        records,
        split=params.split,
        split_manifest=params.split_manifest,
        model=params.model,
        temperature=params.temperature,
        max_tokens=params.max_tokens,
        mode=params.mode,
        prompt_version=prompt_version,
        dspy_cache=params.dspy_cache,
        api_base=params.api_base,
        extra=metadata_extra,
    )

    shared_row_kwargs = {
        "split": params.split,
        "split_manifest": params.split_manifest,
        "model": params.model,
        "temperature": params.temperature,
        "max_tokens": params.max_tokens,
        "mode": params.mode,
        **dict(row_kwargs or {}),
    }

    rows: list[dict[str, Any]] = []
    for record in records:
        rows.append(build_row(record, **shared_row_kwargs))
        if params.progress_every and len(rows) % params.progress_every == 0:
            emit_progress_checkpoint(
                rows,
                metadata,
                total=len(records),
                summarize_rows=summarize_rows,
                gate_interpretation=gate_interpretation,
                jsonl_path=params.checkpoint_jsonl_path,
                report_path=params.checkpoint_report_path,
                write_report=write_report,
                progress_fields=progress_fields,
            )

    metadata["summary"] = summarize_rows(rows)
    if gate_interpretation is not None:
        metadata["gate"] = gate_interpretation(metadata["summary"])
    return rows, metadata


def run_structured_event_split(
    records: Sequence[GanFrequencyRecord],
    *,
    params: SplitRunParams,
    prompt_version: str,
    metadata_extra: Mapping[str, Any],
    build_row: RowBuilder,
    summarize_rows: SummarizeRows,
    gate_interpretation: GateInterpretation | None = None,
    write_report: WriteReport | None = None,
    default_structured_event_jsonl_path: Path,
    structured_event_jsonl_path: Path | None = None,
    structured_event_rows: Sequence[Mapping[str, Any]] | None = None,
    structured_event_source_path: Path | None = None,
    rows_by_source_index: RowsBySourceIndex | None = None,
    progress_fields: Sequence[str] = (
        "call_failures",
        "parse_or_validation_failures",
        "purist_correct",
    ),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run a split over records with a saved structured-event JSONL substrate."""
    source_path = (
        structured_event_source_path
        or structured_event_jsonl_path
        or default_structured_event_jsonl_path
    )
    if structured_event_rows is None:
        structured_event_rows = load_jsonl_rows(source_path)

    indexer = rows_by_source_index or _default_rows_by_source_index
    structured_rows_by_index = indexer(structured_event_rows)

    extra = dict(metadata_extra)
    extra.setdefault("structured_event_source_path", str(source_path))

    def build_row_with_substrate(record: GanFrequencyRecord, **row_kwargs: Any) -> dict[str, Any]:
        return build_row(
            record,
            structured_event_row=structured_rows_by_index.get(record.source_row_index),
            **row_kwargs,
        )

    return run_standard_split(
        records,
        params=params,
        prompt_version=prompt_version,
        metadata_extra=extra,
        build_row=build_row_with_substrate,
        summarize_rows=summarize_rows,
        gate_interpretation=gate_interpretation,
        write_report=write_report,
        progress_fields=progress_fields,
    )


def _default_rows_by_source_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    indexed: dict[int, Mapping[str, Any]] = {}
    for row in rows:
        source_row_index = row.get("source_row_index")
        if isinstance(source_row_index, int):
            indexed[source_row_index] = row
    return indexed
