"""Registry lookup and pipeline-family surfacing for Observatory routes."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from clinical_extraction.core.registry import load_run_registry
from clinical_extraction.observatory.models import ObservatorySettings
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_surfacing import (
    load_surfaced_runs_from_registry,
)


def registry_entry(settings: ObservatorySettings, run_id: str) -> Any:
    for entry in load_run_registry(settings.registry_path):
        if entry.run_id == run_id:
            return entry
    raise HTTPException(status_code=404, detail=f"Unknown run_id: {run_id}")


def build_pipeline_families(settings: ObservatorySettings) -> list[dict[str, Any]]:
    return load_surfaced_runs_from_registry(settings.registry_path)
