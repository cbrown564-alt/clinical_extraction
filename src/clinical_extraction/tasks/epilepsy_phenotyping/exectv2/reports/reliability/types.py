"""Runtime types for cross-model reliability scorecard runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReliabilityRun:
    candidate: str
    model_label: str
    rows_path: Path
    summary_path: Path | None = None
    surface_id: str = "rich_schema_reliability"
    role: str = ""
    claim_boundary: str = ""
