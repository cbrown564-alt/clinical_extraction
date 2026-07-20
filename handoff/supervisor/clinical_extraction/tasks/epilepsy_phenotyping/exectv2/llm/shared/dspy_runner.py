"""Shared DSPy run_split loop helpers for ExECTv2 LLM pipelines."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, TextIO

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.reporting import (
    build_run_progress_payload,
    ensure_summary,
)


def emit_run_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    metadata: Mapping[str, Any],
    summarize_rows: Callable[[Sequence[dict[str, Any]]], dict[str, Any]],
    write_jsonl: Callable[[Sequence[dict[str, Any]], Path], None],
    write_report: Callable[..., None],
    report_jsonl_path: Path | None = None,
    report_path_transform: Callable[[Path], Path] | None = None,
    progress_stream: TextIO | None = None,
) -> None:
    """Write checkpoint JSONL/report artifacts and emit standard progress JSON."""

    summary = ensure_summary(rows, metadata, summarize_rows)
    checkpoint_metadata = dict(metadata)
    checkpoint_metadata["summary"] = summary

    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)

    effective_report_path = report_path
    if effective_report_path is not None and report_path_transform is not None:
        effective_report_path = report_path_transform(effective_report_path)

    if effective_report_path is not None and jsonl_path is not None:
        write_report(
            rows,
            checkpoint_metadata,
            effective_report_path,
            jsonl_path=report_jsonl_path or jsonl_path,
        )

    progress = build_run_progress_payload(
        processed=len(rows),
        total=total,
        summary=summary,
    )
    stream = progress_stream if progress_stream is not None else sys.stderr
    print(json.dumps(progress, sort_keys=True), file=stream, flush=True)
