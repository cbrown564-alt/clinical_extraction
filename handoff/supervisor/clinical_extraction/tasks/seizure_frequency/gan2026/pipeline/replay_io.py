"""Saved-output replay IO helpers for Gan 2026 artifact analysis."""

from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)


def load_raw_outputs_by_source_index(path: Path) -> dict[int, str]:
    """Load reusable raw model outputs from a prior row-oriented JSONL artifact."""

    reusable: dict[int, str] = {}
    if not path.exists():
        return reusable
    for row in load_jsonl_rows(path):
        raw_output = row.get("raw_output")
        source_row_index = row.get("source_row_index")
        if isinstance(source_row_index, int) and isinstance(raw_output, str) and raw_output:
            reusable[source_row_index] = raw_output
    return reusable
