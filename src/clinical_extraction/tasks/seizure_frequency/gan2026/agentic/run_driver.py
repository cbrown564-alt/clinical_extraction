"""Split runner for the retained Gan V12 fresh-evidence ceiling."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    structured_event_traces,
)
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
    """Common parameters for one V12 split run."""

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
MetadataFinalizer = Callable[[Sequence[Mapping[str, Any]], dict[str, Any]], None]
WriteReport = Callable[..., None]


def run_standard_split(
    records: Sequence[GanFrequencyRecord],
    *,
    params: SplitRunParams,
    prompt_version: str,
    metadata_extra: Mapping[str, Any],
    build_row: RowBuilder,
    summarize_rows: SummarizeRows,
    gate_interpretation: GateInterpretation | None = None,
    finalize_metadata: MetadataFinalizer | None = None,
    write_report: WriteReport | None = None,
    progress_fields: Sequence[str] = (
        "call_failures",
        "parse_or_validation_failures",
        "purist_correct",
    ),
    row_kwargs: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the per-record loop with shared metadata and checkpoints."""

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
                finalize_metadata=finalize_metadata,
                jsonl_path=params.checkpoint_jsonl_path,
                report_path=params.checkpoint_report_path,
                write_report=write_report,
                progress_fields=progress_fields,
            )
    metadata["summary"] = summarize_rows(rows)
    if finalize_metadata is not None:
        finalize_metadata(rows, metadata)
    elif gate_interpretation is not None:
        metadata["gate"] = gate_interpretation(metadata["summary"])
    return rows, metadata


def run_cross_model_structured_event_split(
    records: Sequence[GanFrequencyRecord],
    *,
    params: SplitRunParams,
    prompt_version: str,
    metadata_extra: Mapping[str, Any],
    build_row: RowBuilder,
    summarize_rows: SummarizeRows,
    gpt_structured_event_source_path: Path,
    agent_source_paths: Mapping[str, Path],
    agent_ids: Sequence[str] = structured_event_traces.AGENT_IDS,
    gpt_structured_event_rows: Sequence[Mapping[str, Any]] | None = None,
    agent_rows_by_id: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
    gate_interpretation: GateInterpretation | None = None,
    write_report: WriteReport | None = None,
    progress_fields: Sequence[str] = (
        "call_failures",
        "parse_or_validation_failures",
        "purist_correct",
    ),
    row_kwargs: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run V12 over saved GPT, Qwen, and DeepSeek structured-event traces."""

    if gpt_structured_event_rows is None:
        gpt_structured_event_rows = load_jsonl_rows(gpt_structured_event_source_path)
    loaded_agent_rows = structured_event_traces.load_agent_rows(
        gpt_rows=gpt_structured_event_rows,
        agent_sources=agent_source_paths,
        agent_rows_by_id=agent_rows_by_id,
    )
    rows_by_agent = {
        agent_id: _rows_by_source_index(rows)
        for agent_id, rows in loaded_agent_rows.items()
    }
    extra = dict(metadata_extra)
    extra.setdefault(
        "agent_source_paths",
        {agent_id: str(path) for agent_id, path in agent_source_paths.items()},
    )

    def build_row_with_agents(record: GanFrequencyRecord, **kwargs: Any) -> dict[str, Any]:
        return build_row(
            record,
            agent_rows={
                agent_id: rows_by_agent.get(agent_id, {}).get(record.source_row_index)
                for agent_id in agent_ids
            },
            **kwargs,
        )

    return run_standard_split(
        records,
        params=params,
        prompt_version=prompt_version,
        metadata_extra=extra,
        build_row=build_row_with_agents,
        summarize_rows=summarize_rows,
        gate_interpretation=gate_interpretation,
        write_report=write_report,
        progress_fields=progress_fields,
        row_kwargs=row_kwargs,
    )


def _rows_by_source_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    return {
        int(row["source_row_index"]): row
        for row in rows
        if row.get("source_row_index") is not None
    }
