"""Backward-compatible re-exports for Gan 2026 run-registry records."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from clinical_extraction.core.registry import (
    REGISTRY_ROLES,
    REPLAY_STATUSES,
    RUN_DECISIONS,
    ArchitectureFamily,
    ComparisonRole,
    MetricValue,
    RegistryRole,
    ReplayStatus,
    RunDecision,
    RunRegistryEntry,
    load_run_registry,
    registry_entry_from_json_record,
    validate_run_registry_artifacts,
    write_run_registry,
)

__all__ = [
    "RUN_DECISIONS",
    "REPLAY_STATUSES",
    "REGISTRY_ROLES",
    "ArchitectureFamily",
    "ComparisonRole",
    "MetricValue",
    "RegistryRole",
    "ReplayStatus",
    "RunDecision",
    "RunRegistryEntry",
    "load_run_registry",
    "registry_entry_from_json_record",
    "validate_run_registry_artifacts",
    "write_run_registry",
    "render_run_registry_markdown",
    "write_run_registry_markdown",
]


def render_run_registry_markdown(entries: Sequence[RunRegistryEntry]) -> str:
    """Render registry entries as a compact human-facing Markdown index."""

    from .run_registry_report import (
        render_run_registry_markdown as render,
    )

    return render(entries)


def write_run_registry_markdown(entries: Sequence[RunRegistryEntry], path: Path) -> None:
    """Write a Markdown index for a run registry."""

    from .run_registry_report import (
        write_run_registry_markdown as write_markdown,
    )

    write_markdown(entries, path)
