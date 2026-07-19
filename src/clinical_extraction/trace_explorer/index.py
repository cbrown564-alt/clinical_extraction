from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.trace_explorer.adapters.illustrative import (
    ILLUSTRATIVE_SCHEMA_VERSION,
    ImportedArtifact,
    load_illustrative_artifact,
)
from clinical_extraction.trace_explorer.contracts import BuildManifest, TraceEnvelope
from clinical_extraction.trace_explorer.object_store import ObjectStore, canonical_json_bytes
from clinical_extraction.trace_explorer.policy import RowPolicy


def _resolve_approved_path(path: Path, approved_roots: Sequence[Path]) -> Path:
    resolved = path.resolve(strict=True)
    resolved_roots = [root.resolve(strict=True) for root in approved_roots]
    if not any(resolved.is_relative_to(root) for root in resolved_roots):
        raise ValueError(f"artifact is outside an approved root: {path.name}")
    if path.is_symlink():
        raise ValueError(f"artifact symlinks are not allowed: {path.name}")
    return resolved


def _load_artifact(path: Path) -> ImportedArtifact:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"artifact could not be parsed: {path.name}") from exc
    schema_version = payload.get("schema_version")
    if schema_version == ILLUSTRATIVE_SCHEMA_VERSION:
        return load_illustrative_artifact(path)
    raise ValueError(f"unknown schema: {schema_version or '<missing>'}")


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA journal_mode=DELETE;
        PRAGMA foreign_keys=ON;
        CREATE TABLE runs (
            run_id TEXT PRIMARY KEY,
            task TEXT NOT NULL,
            dataset TEXT NOT NULL,
            split TEXT NOT NULL,
            row_policy TEXT NOT NULL,
            method TEXT NOT NULL,
            model TEXT,
            run_state TEXT NOT NULL,
            run_json TEXT NOT NULL
        );
        CREATE INDEX runs_catalog_idx ON runs(task, dataset, split, row_policy, method);
        CREATE TABLE records (
            run_id TEXT NOT NULL,
            source_id TEXT NOT NULL,
            trace_id TEXT NOT NULL UNIQUE,
            object_hash TEXT NOT NULL,
            summary_json TEXT NOT NULL,
            PRIMARY KEY (run_id, source_id),
            FOREIGN KEY (run_id) REFERENCES runs(run_id)
        );
        CREATE INDEX records_order_idx ON records(run_id, source_id);
        CREATE TABLE build_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )


def _safe_run_document(run: Any) -> dict[str, Any]:
    metadata = run.metadata.model_dump(mode="json")
    document: dict[str, Any] = {
        **metadata,
        "expected_records": run.expected_records,
        "completed_records": run.completed_records,
        "failed_records": run.failed_records,
        "quarantined_records": run.quarantined_records,
        "integrity": run.integrity,
    }
    if run.metadata.row_policy is not RowPolicy.DENIED:
        document["score_views"] = [item.model_dump(mode="json") for item in run.score_views]
    return document


def build_index(
    *,
    artifacts: Sequence[Path],
    output: Path,
    approved_roots: Sequence[Path],
) -> BuildManifest:
    """Validate explicit artifacts, then atomically replace the disposable read index."""

    if not artifacts:
        raise ValueError("at least one explicit artifact is required")
    resolved_paths = [_resolve_approved_path(path, approved_roots) for path in artifacts]
    imported = [_load_artifact(path) for path in resolved_paths]

    all_runs = [run for artifact in imported for run in artifact.runs]
    run_ids = [run.metadata.run_id for run in all_runs]
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("duplicate run ID across imported artifacts")

    artifact_hashes = {
        _relative_or_name(artifact.artifact_path, approved_roots): artifact.artifact_sha256
        for artifact in imported
    }
    build_digest = hashlib.sha256(canonical_json_bytes(artifact_hashes)).hexdigest()
    created_at = datetime.now(UTC).isoformat()
    trace_count = sum(run.trace is not None for run in all_runs)
    record_count = sum(
        run.trace is not None and run.metadata.row_policy.permits_records for run in all_runs
    )
    manifest = BuildManifest(
        build_id=f"sha256:{build_digest}",
        created_at=created_at,
        artifact_hashes=artifact_hashes,
        run_count=len(all_runs),
        trace_count=trace_count,
        record_count=record_count,
    )

    output_parent = output.parent.resolve()
    output_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".trace-explorer-build-", dir=output_parent))
    try:
        staging_objects = ObjectStore(staging / "objects")
        staging_index = staging / "index.sqlite3"
        connection = sqlite3.connect(staging_index)
        try:
            _create_schema(connection)
            connection.execute(
                "INSERT INTO build_metadata(key, value) VALUES (?, ?)",
                ("manifest", manifest.model_dump_json()),
            )
            for run in all_runs:
                safe_document = _safe_run_document(run)
                connection.execute(
                    """
                    INSERT INTO runs(
                        run_id, task, dataset, split, row_policy, method, model, run_state, run_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run.metadata.run_id,
                        run.metadata.task,
                        run.metadata.dataset,
                        run.metadata.split,
                        run.metadata.row_policy,
                        run.metadata.method,
                        run.metadata.model,
                        run.metadata.run_state,
                        json.dumps(safe_document, ensure_ascii=False, sort_keys=True),
                    ),
                )
                if run.trace is not None and run.metadata.row_policy.permits_records:
                    trace_payload = run.trace.model_dump(mode="json")
                    object_hash = staging_objects.put(trace_payload)
                    summary = {
                        "stage_count": len(run.trace.stages),
                        "finding_count": len(run.trace.findings),
                        "status": run.metadata.run_state,
                    }
                    connection.execute(
                        """
                        INSERT INTO records(run_id, source_id, trace_id, object_hash, summary_json)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            run.metadata.run_id,
                            run.trace.source.source_id,
                            run.trace.trace_id,
                            object_hash,
                            json.dumps(summary, sort_keys=True),
                        ),
                    )
            connection.commit()
        finally:
            connection.close()

        (staging / "build-manifest.json").write_text(
            manifest.model_dump_json(indent=2) + "\n",
            encoding="utf-8",
        )

        output.mkdir(parents=True, exist_ok=True)
        target_objects = output / "objects"
        target_objects.mkdir(parents=True, exist_ok=True)
        for staged_object in (staging / "objects").glob("*.json"):
            target = target_objects / staged_object.name
            if not target.exists():
                os.replace(staged_object, target)
        os.replace(staging_index, output / "index.sqlite3")
        os.replace(staging / "build-manifest.json", output / "build-manifest.json")
        (output / "reviews" / "exports").mkdir(parents=True, exist_ok=True)
        return manifest
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _relative_or_name(path: Path, approved_roots: Sequence[Path]) -> str:
    resolved = path.resolve()
    for root in approved_roots:
        try:
            return resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            continue
    return path.name


class TraceIndex:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.database_path = root / "index.sqlite3"
        self.object_store = ObjectStore(root / "objects")

    @property
    def ready(self) -> bool:
        return self.database_path.is_file()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def manifest(self) -> BuildManifest:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT value FROM build_metadata WHERE key = 'manifest'"
            ).fetchone()
        if row is None:
            raise RuntimeError("trace index has no build manifest")
        return BuildManifest.model_validate_json(row["value"])

    def list_runs(
        self,
        *,
        task: str | None = None,
        method: str | None = None,
        split: str | None = None,
        model: str | None = None,
        run_state: str | None = None,
        inspectable: bool | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        values: list[Any] = []
        for column, value in (
            ("task", task),
            ("method", method),
            ("split", split),
            ("model", model),
            ("run_state", run_state),
        ):
            if value is not None:
                clauses.append(f"{column} = ?")
                values.append(value)
        if inspectable is not None:
            operator = "IN" if inspectable else "NOT IN"
            clauses.append(f"row_policy {operator} ('illustrative', 'development_row_level')")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT run_json FROM runs {where} ORDER BY run_id",  # noqa: S608
                values,
            ).fetchall()
        return [json.loads(row["run_json"]) for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT run_json FROM runs WHERE run_id = ?", (run_id,)
            ).fetchone()
        return json.loads(row["run_json"]) if row is not None else None

    def list_record_ids(self, run_id: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT source_id FROM records WHERE run_id = ? ORDER BY source_id", (run_id,)
            ).fetchall()
        return [str(row["source_id"]) for row in rows]

    def list_records(
        self,
        run_id: str,
        *,
        after: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        parameters: list[Any] = [run_id]
        after_clause = ""
        if after is not None:
            after_clause = "AND source_id > ?"
            parameters.append(after)
        parameters.append(limit)
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT source_id, trace_id, summary_json
                FROM records
                WHERE run_id = ? {after_clause}
                ORDER BY source_id
                LIMIT ?
                """,  # noqa: S608
                parameters,
            ).fetchall()
        return [
            {
                "source_id": row["source_id"],
                "trace_id": row["trace_id"],
                **json.loads(row["summary_json"]),
            }
            for row in rows
        ]

    def get_trace(self, *, run_id: str, source_id: str) -> TraceEnvelope | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT object_hash FROM records WHERE run_id = ? AND source_id = ?",
                (run_id, source_id),
            ).fetchone()
        if row is None:
            return None
        return TraceEnvelope.model_validate(self.object_store.get(row["object_hash"]))

    def get_trace_by_id(self, trace_id: str) -> TraceEnvelope | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT object_hash FROM records WHERE trace_id = ?", (trace_id,)
            ).fetchone()
        if row is None:
            return None
        return TraceEnvelope.model_validate(self.object_store.get(row["object_hash"]))


def _build_command(arguments: argparse.Namespace) -> int:
    build_index(
        artifacts=[Path(item) for item in arguments.artifact],
        output=Path(arguments.output),
        approved_roots=[Path.cwd()],
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the local trace explorer index.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="Build an index from explicit artifacts.")
    build.add_argument("--artifact", action="append", required=True)
    build.add_argument("--output", default=".trace_explorer")
    build.set_defaults(handler=_build_command)
    arguments = parser.parse_args(argv)
    return int(arguments.handler(arguments))


if __name__ == "__main__":  # pragma: no cover - exercised through the CLI entry point
    raise SystemExit(main())
