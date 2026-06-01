"""Shared run metadata helpers for Gan 2026 experiment artifacts."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any


def build_run_metadata(
    *,
    mode: str,
    model: str,
    temperature: float,
    max_tokens: int,
    prompt_version: str,
    dspy_version: str,
    split: str,
    split_manifest: str,
    row_count: int | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the common metadata recorded by Gan 2026 LLM-backed runs."""

    created_at = datetime.now(UTC)
    metadata: dict[str, Any] = {
        "date": created_at.date().isoformat(),
        "created_at_utc": created_at.isoformat(),
        "mode": mode,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "prompt_version": prompt_version,
        "dspy_version": dspy_version,
        "split": split,
        "split_manifest": split_manifest,
        "git_commit": git_output(["git", "rev-parse", "--short", "HEAD"]),
        "working_tree_note": working_tree_note(),
        "python": sys.version.split()[0],
    }
    if row_count is not None:
        metadata["row_count"] = row_count
    if extra:
        metadata.update(extra)
    return metadata


def working_tree_note() -> str:
    status = git_output(["git", "status", "--short"])
    return "clean" if status == "" else "dirty/uncommitted local changes"


def git_output(args: Sequence[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
