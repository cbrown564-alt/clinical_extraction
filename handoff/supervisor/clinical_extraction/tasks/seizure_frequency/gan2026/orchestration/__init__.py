"""Canonical per-record orchestrators for the Gan 2026 task.

The orchestration package owns the order in which prediction-bearing stages
run. Split loading, checkpointing, provider setup, and aggregate reporting stay
in the runner modules.
"""

from .contracts import (
    GanModelOutput,
    GanRecordResult,
    GanStageEvent,
    ModelOutputSource,
)

__all__ = [
    "GanModelOutput",
    "GanRecordResult",
    "GanStageEvent",
    "ModelOutputSource",
]
