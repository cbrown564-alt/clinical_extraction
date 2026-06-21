"""Candidate producers for ExECTv2 finding assembly."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    FindingSource,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    ProducerManifest,
)


class CandidateProducer(Protocol):
    producer_id: str
    artifact_path: Path
    ownership_label: str

    def rows_by_id(self) -> dict[str, dict[str, Any]]:
        ...


@dataclass(frozen=True)
class SavedJsonlProducer:
    """Replay a saved JSONL artifact as a candidate producer."""

    producer_id: str
    artifact_path: Path
    ownership_label: str
    source_lane: str = ""
    label: str = ""

    @classmethod
    def from_manifest(cls, manifest: ProducerManifest) -> SavedJsonlProducer:
        if manifest.kind != "saved_jsonl":
            raise ValueError(f"unsupported producer kind {manifest.kind!r}")
        return cls(
            producer_id=manifest.producer_id,
            artifact_path=manifest.artifact,
            ownership_label=manifest.ownership_label,
            source_lane=manifest.source_lane,
            label=manifest.label,
        )

    def rows_by_id(self) -> dict[str, dict[str, Any]]:
        rows: dict[str, dict[str, Any]] = {}
        for line in self.artifact_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            rows[str(row["letter_id"])] = row
        return rows

    def source_for_row(self, row: Mapping[str, Any], *, source_lane: str = "") -> FindingSource:
        return FindingSource(
            producer_id=self.producer_id,
            artifact_path=self.artifact_path.as_posix(),
            pipeline_family=str(row.get("pipeline_family", "")),
            model=str(row.get("model", "")),
            prompt_version=str(row.get("prompt_version", "")),
            mode=str(row.get("mode", "")),
            ownership_label=self.ownership_label,
            source_lane=source_lane or self.source_lane or self.producer_id,
        )


def findings_from_row(
    row: Mapping[str, Any],
    *,
    letter_id: str,
    entity: str,
    note_text: str,
    source: FindingSource,
    raw_surface: bool,
) -> tuple[ClinicalFinding, ...]:
    mentions = (
        raw_mentions_from_row(row, default_entity=entity)
        if raw_surface
        else list(row.get("predicted_mentions", []))
    )
    diagnostics = lane_diagnostics_from_row(row)
    findings: list[ClinicalFinding] = []
    for index, mention in enumerate(mentions):
        if not isinstance(mention, Mapping):
            continue
        mention_entity = str(mention.get("entity", entity))
        if mention_entity != entity:
            continue
        evidence = str(mention.get("evidence", ""))
        finding_id = (
            f"{letter_id}:{source.producer_id}:{entity}:"
            f"{'raw' if raw_surface else 'scored'}:{index}"
        )
        findings.append(
            ClinicalFinding.from_mention_row(
                mention,
                finding_id=finding_id,
                letter_id=letter_id,
                entity=entity,
                source=source,
                diagnostics=diagnostics,
                raw_surface=raw_surface,
                evidence_valid=bool(evidence) and evidence in note_text,
            )
        )
    return tuple(findings)


def raw_mentions_from_row(
    row: Mapping[str, Any],
    *,
    default_entity: str,
) -> list[dict[str, Any]]:
    raw = row.get("raw_output") or ""
    if not raw:
        return []
    try:
        payload = json.loads(str(raw))
    except json.JSONDecodeError:
        return []
    mentions = payload.get("mentions", []) if isinstance(payload, dict) else []
    out = []
    for mention in mentions:
        if not isinstance(mention, dict):
            continue
        with_entity = dict(mention)
        with_entity.setdefault("entity", default_entity)
        out.append(with_entity)
    return out


def lane_diagnostics_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "gate_warnings": list(row.get("gate_warnings", [])),
        "projection_version": row.get("projection_version", ""),
        "source_projection_version": row.get("source_projection_version", ""),
        "suppression_version": row.get("suppression_version", ""),
        "projection_actions": row.get("projection_actions", []),
        "suppression_actions": row.get("suppression_actions", []),
        "component_owner": row.get("component_owner", ""),
        "n_evidence_invalid": row.get("n_evidence_invalid", 0),
    }


def status_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "call_error": row.get("call_error"),
        "parse_errors": row.get("parse_errors", []),
        "n_mentions_raw": row.get("n_mentions_raw", 0),
        "n_mentions_scored": row.get("n_mentions_scored", 0),
        "n_evidence_invalid": row.get("n_evidence_invalid", 0),
    }
