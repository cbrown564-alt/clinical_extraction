"""Shared JSONL artifact IO helpers for Gan 2026 experiment runners."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


def write_jsonl_rows(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    """Write row dictionaries to a newline-delimited JSON artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    """Load non-empty rows from a newline-delimited JSON artifact."""

    with path.open(encoding="utf-8-sig") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_raw_outputs_by_source_index(path: Path) -> dict[int, str]:
    """Compatibility wrapper for saved-output replay analysis loading."""

    from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.replay_io import (
        load_raw_outputs_by_source_index as _load_raw_outputs_by_source_index,
    )

    return _load_raw_outputs_by_source_index(path)
