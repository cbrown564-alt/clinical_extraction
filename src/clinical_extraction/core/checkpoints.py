"""Read legacy batch checkpoints without silently dropping duplicate records.

The owning task validates request provenance before using these rows. New
extraction runs use ArtifactStore's complete request/runtime identity instead.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_completed(path: Path | str | None, *, key: str) -> tuple[list[dict[str, Any]], set[str]]:
    if path is None or not Path(path).exists():
        return [], set()
    rows = [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines()
            if line.strip()]
    keys: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get(key), str) or not row[key]:
            raise ValueError(f'checkpoint row is missing {key}')
        if row[key] in keys:
            raise ValueError(f'checkpoint contains duplicate {key}')
        keys.add(row[key])
    return rows, keys
