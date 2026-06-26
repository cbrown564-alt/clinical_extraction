"""Artifact path selection and loading for Observatory routes."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from clinical_extraction.observatory.helpers import safe_repo_path
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)


def select_artifact_paths(
    repo_root: Path,
    paths: Sequence[str],
    split: str | None,
    requested: str | None,
) -> list[str]:
    if requested is not None:
        if requested not in paths:
            raise HTTPException(
                status_code=404,
                detail=f"Run does not reference artifact: {requested}",
            )
        return [requested]

    jsonl_paths = [p for p in paths if Path(p).suffix == ".jsonl"]
    if not jsonl_paths:
        return []

    if split and "+" in split and "test" in split:
        return jsonl_paths

    def _file_size(path: str) -> int:
        try:
            return os.path.getsize(safe_repo_path(repo_root, path))
        except Exception:
            return 0

    largest = max(jsonl_paths, key=_file_size)
    return [largest]


def load_artifact_content(path: Path, *, limit: int | None) -> Any:
    if path.suffix == ".jsonl":
        rows = load_jsonl_rows(path)
        return rows[:limit] if limit is not None else rows
    if path.suffix == ".json":
        content = json.loads(path.read_text(encoding="utf-8"))
        if limit is not None and isinstance(content, list):
            return content[:limit]
        return content
    return {"text": path.read_text(encoding="utf-8")}
