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


def load_raw_outputs_by_source_index(path: Path) -> dict[int, str]:
    """Load reusable raw model outputs from a prior row-oriented JSONL artifact."""

    reusable: dict[int, str] = {}
    if not path.exists():
        return reusable
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        raw_output = row.get("raw_output")
        source_row_index = row.get("source_row_index")
        if isinstance(source_row_index, int) and isinstance(raw_output, str) and raw_output:
            reusable[source_row_index] = raw_output
    return reusable
