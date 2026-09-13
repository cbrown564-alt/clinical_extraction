"""Immutable artifacts and request-aware execution history in a local SQLite store."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.core.artifacts import (
    Assertion,
    CoverageRecord,
    EvidenceRef,
    ExecutionConfiguration,
    ExtractionArtifact,
    InferenceAttempt,
    PreparedExtractionRequest,
    PromptComponent,
    Relationship,
    SourceRef,
    canonical_json,
    freeze_json,
    lifecycle_manifest_from_artifact,
    sha256_json,
    sha256_text,
)


def artifact_from_record(
    record: Mapping[str, Any],
    *,
    content_decoder: Callable[[Any], Any] = freeze_json,
) -> ExtractionArtifact[Any]:
    """Load a portable artifact, validating request, response and derived-content hashes."""
    r = dict(record["request"])
    r["sources"] = tuple(SourceRef(**item) for item in r["sources"])
    r["rendered_messages"] = tuple(r["rendered_messages"])
    components = []
    for item in r["prompt_components"]:
        component = PromptComponent.from_value(
            component_id=item["component_id"],
            version=item["version"],
            content=item["content"],
            rendered_paths=item["rendered_paths"],
        )
        if component.content_sha256 != item["content_sha256"]:
            raise ValueError("prompt component content hash mismatch")
        components.append(component)
    r["prompt_components"] = tuple(components)
    request = PreparedExtractionRequest(**r)
    if sha256_text(request.prompt_input_json) != request.prompt_input_sha256:
        raise ValueError("prompt input hash mismatch")
    if sha256_json(request.rendered_messages) != request.rendered_messages_sha256:
        raise ValueError("rendered message hash mismatch")
    identity = {
        "task_id": request.task_id,
        "profile_id": request.profile_id,
        "profile_version": request.profile_version,
        "schema_version": request.schema_version,
        "sources": [s.to_dict() for s in request.sources],
        "prompt_input_sha256": request.prompt_input_sha256,
        "rendered_messages_sha256": request.rendered_messages_sha256,
        "components_sha256": sha256_json([c.to_dict(include_content=False) for c in components]),
    }
    if request.request_id != f"request:{sha256_json(identity)}":
        raise ValueError("request identity mismatch")

    def evidence(items: Any) -> tuple[EvidenceRef, ...]:
        return tuple(
            EvidenceRef(**{**item, "source": SourceRef(**item["source"])}) for item in items
        )

    assertions = tuple(
        Assertion(
            **{**a, "content": content_decoder(a["content"]), "evidence": evidence(a["evidence"])}
        )
        for a in record["assertions"]
    )
    relationships = tuple(
        Relationship(**{**r, "evidence": evidence(r["evidence"])}) for r in record["relationships"]
    )
    coverage = CoverageRecord(**{k: tuple(v) for k, v in record["coverage"].items()})
    artifact = ExtractionArtifact.create(
        status=record["status"],
        request=request,
        attempts=tuple(InferenceAttempt(**a) for a in record["attempts"]),
        raw_payload=record["raw_payload"],
        assertions=assertions,
        relationships=relationships,
        coverage=coverage,
        diagnostics=record["diagnostics"],
        compatibility_output=record["compatibility_output"],
    )
    if artifact.artifact_id != record["artifact_id"]:
        raise ValueError("artifact identity mismatch")
    return artifact


class ArtifactStore:
    """Persist captures and manifests; each execution revision remains inspectable.

    Resume identity includes the complete request, runtime and program version.
    Failed captures are returned as failures unless an explicit retry is requested.
    No source ID is used as a unique record key. SQLite transactions preserve
    atomicity, including on Windows; callers close the store with a context manager.
    """

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, timeout=30)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS artifacts (
                artifact_id TEXT PRIMARY KEY, content_sha256 TEXT NOT NULL,
                payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS executions (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT, execution_key TEXT NOT NULL,
                artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
                manifest TEXT NOT NULL, manifest_sha256 TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS execution_lookup ON executions(execution_key, sequence);
        """)

    def __enter__(self) -> ArtifactStore:
        return self

    def __exit__(self, *args: Any) -> None:
        self.connection.close()

    @staticmethod
    def execution_key(
        request: PreparedExtractionRequest, runtime: ExecutionConfiguration, program_version: str
    ) -> str:
        return sha256_json(
            {
                "request_id": request.request_id,
                "runtime": runtime.to_dict(),
                "program_version": program_version,
            }
        )

    def get(self, execution_key: str) -> ExtractionArtifact[Any] | None:
        row = self.connection.execute(
            """
            SELECT a.payload, a.content_sha256, e.manifest, e.manifest_sha256
            FROM executions e JOIN artifacts a USING(artifact_id)
            WHERE e.execution_key=? ORDER BY e.sequence DESC LIMIT 1
        """,
            (execution_key,),
        ).fetchone()
        if row is None:
            return None
        payload, digest, manifest, manifest_digest = row
        if sha256_text(payload) != digest or sha256_text(manifest) != manifest_digest:
            raise ValueError("stored artifact or manifest checksum mismatch")
        artifact = artifact_from_record(json.loads(payload))
        m = json.loads(manifest)
        if m["artifact_id"] != artifact.artifact_id:
            raise ValueError("stored manifest refers to another artifact")
        runtime = ExecutionConfiguration(**m["runtime"])
        if self.execution_key(artifact.request, runtime, m["program_version"]) != execution_key:
            raise ValueError("stored execution identity mismatch")
        return artifact

    def put(
        self,
        artifact: ExtractionArtifact[Any],
        runtime: ExecutionConfiguration,
        *,
        program_version: str,
        replay_mode: str = "live",
        dataset_id: str | None = None,
        split: str | None = None,
        row_policy: str | None = None,
    ) -> None:
        key = self.execution_key(artifact.request, runtime, program_version)
        manifest = lifecycle_manifest_from_artifact(
            artifact,
            runtime=runtime,
            program_version=program_version,
            replay_mode=replay_mode,
            dataset_id=dataset_id,
            split=split,
            row_policy=row_policy,
        )
        payload = canonical_json(artifact.to_dict())
        manifest_json = canonical_json(manifest.to_dict())
        with self.connection:
            prior = self.connection.execute(
                "SELECT payload FROM artifacts WHERE artifact_id=?", (artifact.artifact_id,)
            ).fetchone()
            if prior and prior[0] != payload:
                raise ValueError("immutable artifact has conflicting content")
            self.connection.execute(
                "INSERT OR IGNORE INTO artifacts VALUES (?, ?, ?)",
                (artifact.artifact_id, sha256_text(payload), payload),
            )
            self.connection.execute(
                """INSERT INTO executions
                (execution_key, artifact_id, manifest, manifest_sha256) VALUES (?, ?, ?, ?)""",
                (key, artifact.artifact_id, manifest_json, sha256_text(manifest_json)),
            )

    def execute(
        self,
        request: PreparedExtractionRequest,
        runtime: ExecutionConfiguration,
        *,
        program_version: str,
        capture: Callable[[], ExtractionArtifact[Any]],
        replay_only: bool = False,
        retry_failed: bool = False,
    ) -> ExtractionArtifact[Any]:
        key = self.execution_key(request, runtime, program_version)
        saved = self.get(key)
        if saved is not None and (saved.status == "ready" or not retry_failed or replay_only):
            return saved
        if replay_only:
            raise ValueError("no saved artifact for this exact request and runtime")
        artifact = capture()
        if artifact.request.to_dict() != request.to_dict():
            raise ValueError("capture returned a different request")
        self.put(artifact, runtime, program_version=program_version)
        return artifact

    def records(self) -> list[dict[str, Any]]:
        """Read all manifests, preserving failures and repeated execution revisions."""
        rows = self.connection.execute(
            "SELECT execution_key, manifest, manifest_sha256 FROM executions ORDER BY sequence"
        ).fetchall()
        records = []
        for key, manifest, digest in rows:
            if sha256_text(manifest) != digest:
                raise ValueError("stored manifest checksum mismatch")
            records.append({"execution_key": key, **json.loads(manifest)})
        return records
