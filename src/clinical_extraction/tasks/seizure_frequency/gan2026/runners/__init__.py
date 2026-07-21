"""Retained Gan 2026 pipeline runners."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    ARCHITECTURE_FAMILY,
    PIPELINE_METHOD,
    PipelineArchitecture,
    PipelineConfiguration,
    PipelineOutputArtifact,
)

__all__ = [
    "ARCHITECTURE_FAMILY",
    "PIPELINE_METHOD",
    "PipelineArchitecture",
    "PipelineConfiguration",
    "PipelineOutputArtifact",
    "deterministic_canonical",
    "get_cli_specs",
    "hybrid_structured_events",
    "llm_only_canonical",
    "run_split",
    "write_deterministic_report",
]


def __getattr__(name: str) -> Any:
    """Load only the runner requested by the caller."""

    if name in {"deterministic_canonical", "hybrid_structured_events", "llm_only_canonical"}:
        return import_module(f"{__name__}.{name}")
    if name == "get_cli_specs":
        from clinical_extraction.tasks.seizure_frequency.gan2026.runners.cli_specs import (
            get_cli_specs,
        )

        return get_cli_specs
    if name == "run_split":
        from clinical_extraction.tasks.seizure_frequency.gan2026.runners.split import run_split

        return run_split
    if name == "write_deterministic_report":
        from clinical_extraction.tasks.seizure_frequency.gan2026.runners.reports import (
            write_deterministic_report,
        )

        return write_deterministic_report
    raise AttributeError(name)
