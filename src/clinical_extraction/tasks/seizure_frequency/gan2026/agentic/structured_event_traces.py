"""Saved structured-event traces used by the retained Gan V12 ceiling."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    fresh_evidence_support,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

AgentId = Literal["gpt", "qwen", "deepseek"]
AGENT_IDS: tuple[AgentId, ...] = ("gpt", "qwen", "deepseek")

DEFAULT_QWEN_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/gan2026_v06_validation750_hybrid_structured_events_qwen3635b_2026-06-12.jsonl"
)
DEFAULT_DEEPSEEK_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/gan2026_v06_validation750_hybrid_structured_events_deepseek_2026-06-12.jsonl"
)


def load_agent_rows(
    *,
    gpt_rows: Sequence[Mapping[str, Any]],
    agent_sources: Mapping[str, Path],
    agent_rows_by_id: Mapping[str, Sequence[Mapping[str, Any]]] | None,
) -> dict[str, Sequence[Mapping[str, Any]]]:
    """Load the three saved trace streams without making model calls."""

    if agent_rows_by_id is not None:
        return {
            "gpt": tuple(agent_rows_by_id.get("gpt", gpt_rows)),
            "qwen": tuple(agent_rows_by_id.get("qwen", ())),
            "deepseek": tuple(agent_rows_by_id.get("deepseek", ())),
        }
    rows: dict[str, Sequence[Mapping[str, Any]]] = {"gpt": tuple(gpt_rows)}
    for agent_id in ("qwen", "deepseek"):
        source_path = agent_sources[agent_id]
        rows[agent_id] = tuple(load_jsonl_rows(source_path)) if source_path.exists() else ()
    return rows


def agent_prompt_summary(
    agent_id: AgentId,
    row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return the source-near trace fields exposed to the V12 reasoner."""

    return {
        "agent_id": agent_id,
        "agent_prompt_version": row.get("prompt_version") if row else None,
        "structured_event_input": fresh_evidence_support.inspect_structured_events(row),
    }
