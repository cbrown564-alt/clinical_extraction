"""Private-data-conscious progress, resume, and atomic finalization."""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections.abc import Iterable, Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .config import EndpointConfig
from .errors import ResumeMismatchError, safe_error
from .extractor import ClinicalExtractor
from .input import InputNote
from .versions import PACKAGE_VERSION, version_record


def _json_line(value: Mapping[str, Any]) -> str:
    return json.dumps(dict(value), ensure_ascii=False, sort_keys=True) + "\n"


def _private_permissions(path: Path) -> None:
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _private_permissions(temporary)
    os.replace(temporary, path)


def _write_jsonl_atomic(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(_json_line(row))
        handle.flush()
        os.fsync(handle.fileno())
    _private_permissions(temporary)
    os.replace(temporary, path)


def _append_synced(path: Path, row: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(_json_line(row))
        handle.flush()
        os.fsync(handle.fileno())
    _private_permissions(path)


def _input_identity(notes: Iterable[InputNote]) -> str:
    digest = hashlib.sha256()
    for note in notes:
        digest.update(note.note_id.encode("utf-8"))
        digest.update(b"\0")
        digest.update(note.text.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def run_identity(
    notes: list[InputNote], workflows: tuple[str, ...], config: EndpointConfig
) -> dict[str, Any]:
    return {
        "input_sha256": _input_identity(notes),
        "workflows": list(workflows),
        "endpoint": config.public_dict()["endpoint"],
        "model": config.model,
        "settings": asdict(config.settings),
        "versions": version_record(),
    }


def _paths(output: Path) -> tuple[Path, Path]:
    partial = output.with_name(f".{output.name}.partial.jsonl")
    metadata = output.with_name(f".{output.name}.partial.meta.json")
    return partial, metadata


def _load_partial(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        note_id = str(row.get("id", ""))
        if not note_id or note_id in seen:
            raise ResumeMismatchError()
        seen.add(note_id)
        rows.append(row)
    return rows


def _workflow_row(
    extractor: ClinicalExtractor,
    *,
    note: InputNote,
    workflows: tuple[str, ...],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, int]]:
    results: dict[str, Any] = {}
    traces: dict[str, Any] = {}
    counts = {"model_calls": 0, "format_fallbacks": 0}
    for workflow in workflows:
        try:
            output = extractor.run_workflow(workflow, note_id=note.note_id, text=note.text)
        except Exception as exc:
            results[workflow] = {"status": "error", "error": safe_error(exc)}
            continue
        results[workflow] = {"status": "ok", "result": output.result}
        traces[workflow] = output.trace
        counts["model_calls"] += output.model_response.request_attempts
        counts["format_fallbacks"] += int(output.model_response.request_attempts > 1)
    statuses = [result["status"] for result in results.values()]
    if all(value == "ok" for value in statuses):
        status = "ok"
    elif all(value == "error" for value in statuses):
        status = "error"
    else:
        status = "partial"
    return (
        {
            "id": note.note_id,
            "status": status,
            "package_version": PACKAGE_VERSION,
            "model": getattr(getattr(extractor.model, "config", None), "model", "configured-model"),
            "workflows": results,
            "warnings": [],
        },
        {"id": note.note_id, "workflows": traces},
        counts,
    )


def run_batch(
    *,
    extractor: ClinicalExtractor,
    config: EndpointConfig,
    notes: list[InputNote],
    workflows: tuple[str, ...],
    output: Path,
    trace_output: Path | None = None,
    resume: bool = False,
    retry_failed: bool = False,
    overwrite: bool = False,
) -> dict[str, Any]:
    if output.exists() and not overwrite:
        raise FileExistsError(f"output exists: {output.name}")
    if trace_output is not None and trace_output.exists() and not overwrite:
        raise FileExistsError(f"trace output exists: {trace_output.name}")
    partial_path, metadata_path = _paths(output)
    identity = run_identity(notes, workflows, config)
    completed: dict[str, dict[str, Any]] = {}
    if resume:
        if not partial_path.is_file() or not metadata_path.is_file():
            raise ResumeMismatchError()
        saved_identity = json.loads(metadata_path.read_text(encoding="utf-8"))
        if saved_identity != identity:
            raise ResumeMismatchError()
        completed = {str(row["id"]): row for row in _load_partial(partial_path)}
    else:
        if partial_path.exists() or metadata_path.exists():
            raise FileExistsError("a partial run exists; use --resume or remove it privately")
        _write_json_atomic(metadata_path, identity)

    started = time.monotonic()
    traces: list[dict[str, Any]] = []
    totals = {"model_calls": 0, "format_fallbacks": 0}
    for note in notes:
        existing = completed.get(note.note_id)
        if existing is not None and not (retry_failed and existing.get("status") == "error"):
            continue
        row, trace, counts = _workflow_row(
            extractor, note=note, workflows=workflows
        )
        if existing is None:
            _append_synced(partial_path, row)
        else:
            completed[note.note_id] = row
            _write_jsonl_atomic(partial_path, completed.values())
        completed[note.note_id] = row
        traces.append(trace)
        for key in totals:
            totals[key] += counts[key]

    ordered = [completed[note.note_id] for note in notes]
    _write_jsonl_atomic(output, ordered)
    if trace_output is not None:
        _write_jsonl_atomic(trace_output, traces)
    partial_path.unlink(missing_ok=True)
    metadata_path.unlink(missing_ok=True)
    summary = {
        "notes": len(notes),
        "ok": sum(row["status"] == "ok" for row in ordered),
        "partial": sum(row["status"] == "partial" for row in ordered),
        "failed": sum(row["status"] == "error" for row in ordered),
        "model_calls": totals["model_calls"],
        "structured_output_fallbacks": totals["format_fallbacks"],
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "output": str(output),
        "trace_output": str(trace_output) if trace_output else None,
    }
    return summary
