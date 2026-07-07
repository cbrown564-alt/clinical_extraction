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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    cross_model_structured_event_adjudicator as cross_model_base,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    llm_event_reasoner,
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
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_metadata import (
    build_run_metadata,
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
MetadataFinalizer = Callable[[Sequence[Mapping[str, Any]], dict[str, Any]], None]
WriteReport = Callable[..., None]
RowsBySourceIndex = Callable[[Sequence[Mapping[str, Any]]], Mapping[int, Mapping[str, Any]]]
SplitDispatchKind = Literal[
    "standard",
    "structured_event",
    "cross_model_structured_event",
    "matched_budget",
]
ValidateConditions = Callable[[Sequence[str]], None]
BuildMatchedBudgets = Callable[..., Mapping[str, Any]]


@dataclass(frozen=True)
class RegisteredAgenticStage:
    """Registry entry describing how a stage routes through ``run_driver``."""

    stage_id: str
    dispatch_kind: SplitDispatchKind
    module: str
    description: str = ""


@dataclass(frozen=True)
class AgenticSplitHooks:
    """Stage-local callbacks supplied when dispatching a registered split runner."""

    prompt_version: str
    metadata_extra: Mapping[str, Any]
    build_row: RowBuilder
    summarize_rows: SummarizeRows
    gate_interpretation: GateInterpretation | None = None
    finalize_metadata: MetadataFinalizer | None = None
    write_report: WriteReport | None = None
    progress_fields: Sequence[str] = (
        "call_failures",
        "parse_or_validation_failures",
        "purist_correct",
    )


@dataclass(frozen=True)
class CrossModelSplitContext:
    """Substrate paths for ``cross_model_structured_event`` dispatch."""

    gpt_structured_event_source_path: Path
    agent_source_paths: Mapping[str, Path]
    gpt_structured_event_rows: Sequence[Mapping[str, Any]] | None = None
    agent_rows_by_id: Mapping[str, Sequence[Mapping[str, Any]]] | None = None
    agent_ids: Sequence[str] = field(default_factory=lambda: cross_model_base.AGENT_IDS)
    row_kwargs: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class MatchedBudgetSplitContext:
    """Context for ``matched_budget`` dispatch (Phase 6 multi-condition runner)."""

    default_conditions: Sequence[str]
    validate_conditions: ValidateConditions
    default_budgets: BuildMatchedBudgets
    conditions: Sequence[str] | None = None


@dataclass(frozen=True)
class StructuredEventSplitContext:
    """Substrate paths for ``structured_event`` dispatch."""

    default_structured_event_jsonl_path: Path
    structured_event_jsonl_path: Path | None = None
    structured_event_rows: Sequence[Mapping[str, Any]] | None = None
    structured_event_source_path: Path | None = None
    rows_by_source_index: RowsBySourceIndex | None = None
    row_kwargs: Mapping[str, Any] | None = None


_STAGE_REGISTRY: dict[str, RegisteredAgenticStage] = {}


def register_agentic_stage(stage: RegisteredAgenticStage) -> None:
    """Register one agentic stage for ``dispatch_registered_split`` routing."""

    if stage.stage_id in _STAGE_REGISTRY:
        existing = _STAGE_REGISTRY[stage.stage_id]
        if existing != stage:
            raise ValueError(
                f"agentic stage {stage.stage_id!r} already registered from {existing.module!r}"
            )
        return
    _STAGE_REGISTRY[stage.stage_id] = stage


def registered_agentic_stages() -> Mapping[str, RegisteredAgenticStage]:
    """Return a read-only view of registered agentic stages."""

    return dict(_STAGE_REGISTRY)


def dispatch_registered_split(
    stage_id: str,
    records: Sequence[GanFrequencyRecord],
    *,
    params: SplitRunParams,
    hooks: AgenticSplitHooks,
    structured_event_context: StructuredEventSplitContext | None = None,
    cross_model_context: CrossModelSplitContext | None = None,
    matched_budget_context: MatchedBudgetSplitContext | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Route a registered stage through the appropriate ``run_driver`` split helper."""
    try:
        stage = _STAGE_REGISTRY[stage_id]
    except KeyError as exc:
        registered = ", ".join(sorted(_STAGE_REGISTRY)) or "(none)"
        raise KeyError(
            f"unknown agentic stage {stage_id!r}; registered stages: {registered}"
        ) from exc

    split_kwargs = {
        "records": records,
        "params": params,
        "prompt_version": hooks.prompt_version,
        "metadata_extra": hooks.metadata_extra,
        "build_row": hooks.build_row,
        "summarize_rows": hooks.summarize_rows,
        "gate_interpretation": hooks.gate_interpretation,
        "write_report": hooks.write_report,
        "progress_fields": hooks.progress_fields,
    }
    if stage.dispatch_kind == "standard":
        return run_standard_split(
            **split_kwargs,
            finalize_metadata=hooks.finalize_metadata,
            row_kwargs=(structured_event_context.row_kwargs if structured_event_context else None),
        )
    if stage.dispatch_kind == "structured_event":
        if structured_event_context is None:
            raise ValueError(
                f"stage {stage_id!r} requires structured_event_context for structured_event dispatch"
            )
        return run_structured_event_split(
            **split_kwargs,
            default_structured_event_jsonl_path=(
                structured_event_context.default_structured_event_jsonl_path
            ),
            structured_event_jsonl_path=structured_event_context.structured_event_jsonl_path,
            structured_event_rows=structured_event_context.structured_event_rows,
            structured_event_source_path=structured_event_context.structured_event_source_path,
            rows_by_source_index=structured_event_context.rows_by_source_index,
        )
    if stage.dispatch_kind == "cross_model_structured_event":
        if cross_model_context is None:
            raise ValueError(
                "stage "
                f"{stage_id!r} requires cross_model_context for cross_model_structured_event dispatch"
            )
        return run_cross_model_structured_event_split(
            **split_kwargs,
            gpt_structured_event_source_path=cross_model_context.gpt_structured_event_source_path,
            agent_source_paths=cross_model_context.agent_source_paths,
            agent_ids=cross_model_context.agent_ids,
            gpt_structured_event_rows=cross_model_context.gpt_structured_event_rows,
            agent_rows_by_id=cross_model_context.agent_rows_by_id,
            row_kwargs=cross_model_context.row_kwargs,
        )
    if stage.dispatch_kind == "matched_budget":
        if matched_budget_context is None:
            raise ValueError(
                f"stage {stage_id!r} requires matched_budget_context for matched_budget dispatch"
            )
        return run_matched_budget_split(
            records=records,
            params=params,
            prompt_version=hooks.prompt_version,
            metadata_extra=hooks.metadata_extra,
            build_row=hooks.build_row,
            summarize_rows=hooks.summarize_rows,
            matched_budget_context=matched_budget_context,
        )
    raise ValueError(f"unsupported dispatch_kind {stage.dispatch_kind!r} for stage {stage_id!r}")


def run_matched_budget_split(
    records: Sequence[GanFrequencyRecord],
    *,
    params: SplitRunParams,
    prompt_version: str,
    metadata_extra: Mapping[str, Any],
    build_row: RowBuilder,
    summarize_rows: SummarizeRows,
    matched_budget_context: MatchedBudgetSplitContext,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run Phase 6 matched-budget multi-condition traces over one split."""
    active_conditions = tuple(
        matched_budget_context.conditions or matched_budget_context.default_conditions
    )
    matched_budget_context.validate_conditions(active_conditions)
    if params.mode == "live":
        configure_dspy_for_stage(
            model=params.model,
            temperature=params.temperature,
            max_tokens=params.max_tokens,
            cache=params.dspy_cache,
            api_base=params.api_base,
        )
    budgets = matched_budget_context.default_budgets(max_tokens=params.max_tokens)
    shared_row_kwargs = {
        "split": params.split,
        "split_manifest": params.split_manifest,
        "model": params.model,
        "temperature": params.temperature,
        "max_tokens": params.max_tokens,
        "mode": params.mode,
        "budgets": budgets,
        "conditions": active_conditions,
    }
    rows = [build_row(record, **shared_row_kwargs) for record in records]
    metadata = build_run_metadata(
        mode=params.mode,
        model=params.model,
        temperature=params.temperature,
        max_tokens=params.max_tokens,
        prompt_version=prompt_version,
        dspy_version="none",
        split=params.split,
        split_manifest=params.split_manifest,
        api_base=params.api_base,
        row_count=len(records),
    )
    metadata.update(dict(metadata_extra))
    metadata.update(
        {
            "dspy_cache": params.dspy_cache,
            "conditions": list(active_conditions),
            "condition_filter": list(active_conditions),
            "matched_budget": {
                condition: budget.model_dump(mode="json")
                for condition, budget in budgets.items()
                if condition in active_conditions
            },
        }
    )
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


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
    agent_ids: Sequence[str] = cross_model_base.AGENT_IDS,
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
    """Run a split over records with saved multi-agent structured-event traces."""
    if gpt_structured_event_rows is None:
        gpt_structured_event_rows = load_jsonl_rows(gpt_structured_event_source_path)
    loaded_agent_rows = cross_model_base._load_agent_rows(
        gpt_rows=gpt_structured_event_rows,
        agent_sources=agent_source_paths,
        agent_rows_by_id=agent_rows_by_id,
    )
    rows_by_agent = {
        agent_id: llm_event_reasoner._rows_by_source_index(rows)
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


register_agentic_stage(
    RegisteredAgenticStage(
        stage_id="llm_event_reasoner",
        dispatch_kind="structured_event",
        module="clinical_extraction.tasks.seizure_frequency.gan2026.agentic.llm_event_reasoner",
        description="Core structured-event LLM reasoner and shared scoring helpers",
    )
)
register_agentic_stage(
    RegisteredAgenticStage(
        stage_id="runner",
        dispatch_kind="matched_budget",
        module="clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner",
        description="Phase 6 matched-budget multi-condition agentic runner",
    )
)
