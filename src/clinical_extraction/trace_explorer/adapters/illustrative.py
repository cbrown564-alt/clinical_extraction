from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.core.evidence import (
    EvidenceGrade,
    grade_evidence,
    locate_evidence,
    repair_evidence_text_if_source_exact,
)
from clinical_extraction.trace_explorer.contracts import (
    EvidenceReference,
    FindingSnapshot,
    RunMetadata,
    ScoreView,
    SourceRecord,
    TraceChange,
    TraceDiagnostic,
    TraceEnvelope,
    TraceStage,
)
from clinical_extraction.trace_explorer.policy import derive_row_policy

ILLUSTRATIVE_SCHEMA_VERSION = "illustrative.fixture.v1"


@dataclass(frozen=True)
class ImportedRun:
    metadata: RunMetadata
    score_views: tuple[ScoreView, ...]
    integrity: dict[str, Any]
    expected_records: int
    completed_records: int
    failed_records: int
    quarantined_records: int
    trace: TraceEnvelope | None


@dataclass(frozen=True)
class ImportedArtifact:
    artifact_path: Path
    artifact_sha256: str
    runs: tuple[ImportedRun, ...]

    @property
    def traces_by_run(self) -> dict[str, TraceEnvelope]:
        return {run.metadata.run_id: run.trace for run in self.runs if run.trace is not None}


def _safe_artifact_path(path: Path) -> str:
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def _make_evidence(
    raw: dict[str, Any],
    *,
    source: SourceRecord,
    stage_id: str,
) -> EvidenceReference:
    citation = str(raw.get("citation", ""))
    grade = grade_evidence(source.text, citation)
    located = locate_evidence(source.text, citation)
    start, end = located if located is not None else (None, None)
    repaired = repair_evidence_text_if_source_exact(citation, source.text)
    return EvidenceReference(
        evidence_id=raw["evidence_id"],
        source_id=source.source_id,
        citation=citation,
        start=start,
        end=end,
        grade=grade,
        role=raw["role"],
        finding_ids=tuple(raw.get("finding_ids", ())),
        stage_ids=(stage_id,),
        repaired_citation=(
            repaired
            if grade not in {EvidenceGrade.EXACT, EvidenceGrade.ABSENT, EvidenceGrade.EMPTY}
            else None
        ),
        repair_kind=(grade.value.casefold() if grade.value.startswith("REPAIRED_") else None),
    )


def _make_stage(raw: dict[str, Any], source: SourceRecord) -> TraceStage:
    stage_id = raw["stage_id"]
    evidence = tuple(
        _make_evidence(item, source=source, stage_id=stage_id)
        for item in raw.get("evidence", ())
    )
    changes = tuple(
        TraceChange.model_validate({**item, "stage_id": stage_id})
        for item in raw.get("changes", ())
    )
    stage_payload = {
        **raw,
        "evidence": evidence,
        "changes": changes,
    }
    return TraceStage.model_validate(stage_payload)


def load_illustrative_artifact(path: Path) -> ImportedArtifact:
    payload_bytes = path.read_bytes()
    artifact_sha256 = hashlib.sha256(payload_bytes).hexdigest()
    payload = json.loads(payload_bytes)
    if payload.get("schema_version") != ILLUSTRATIVE_SCHEMA_VERSION:
        raise ValueError(f"unknown schema: {payload.get('schema_version', '<missing>')}")
    if payload.get("fixture_id") != "SYN-014":
        raise ValueError("illustrative adapter accepts SYN-014 only")

    source_payload = payload["source"]
    source_text = source_payload["text"]
    source = SourceRecord(
        source_id=source_payload["source_id"],
        text=source_text,
        character_count=len(source_text),
        text_sha256=hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
    )

    imported_runs: list[ImportedRun] = []
    for raw_run in payload["runs"]:
        run_payload = raw_run["run"]
        has_trace = bool(raw_run.get("stages"))
        source_ids = (source.source_id,) if has_trace else ()
        row_policy = derive_row_policy(
            dataset=run_payload["dataset"],
            split=run_payload["split"],
            source_ids=source_ids,
        )
        metadata = RunMetadata.model_validate(
            {
                **run_payload,
                "row_policy": row_policy,
                "artifact_sha256": artifact_sha256,
                "artifact_path": _safe_artifact_path(path),
            }
        )
        score_views = tuple(
            ScoreView.model_validate(item) for item in raw_run.get("score_views", ())
        )
        trace: TraceEnvelope | None = None
        if has_trace:
            stages = tuple(_make_stage(item, source) for item in raw_run["stages"])
            findings = tuple(
                FindingSnapshot.model_validate(item) for item in raw_run.get("findings", ())
            )
            trace_digest = hashlib.sha256(
                "|".join(
                    (
                        "trace.v1",
                        metadata.run_id,
                        source.source_id,
                        artifact_sha256,
                    )
                ).encode("utf-8")
            ).hexdigest()
            trace = TraceEnvelope(
                trace_id=f"sha256:{trace_digest}",
                run=metadata,
                source=source,
                stages=stages,
                findings=findings,
                score_views=score_views,
                diagnostics=tuple(
                    TraceDiagnostic.model_validate(item)
                    for item in raw_run.get("diagnostics", ())
                ),
            )

        imported_runs.append(
            ImportedRun(
                metadata=metadata,
                score_views=score_views,
                integrity=dict(raw_run.get("integrity", {})),
                expected_records=int(raw_run.get("expected_records", 0)),
                completed_records=int(raw_run.get("completed_records", 0)),
                failed_records=int(raw_run.get("failed_records", 0)),
                quarantined_records=int(raw_run.get("quarantined_records", 0)),
                trace=trace,
            )
        )

    return ImportedArtifact(
        artifact_path=path,
        artifact_sha256=artifact_sha256,
        runs=tuple(imported_runs),
    )
