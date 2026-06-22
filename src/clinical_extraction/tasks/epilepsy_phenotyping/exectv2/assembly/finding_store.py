"""Per-letter clinical finding store."""

from __future__ import annotations

from collections.abc import Iterable

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    FindingSource,
)


class ClinicalFindingStore:
    """Small per-letter collection of raw and scored clinical findings."""

    def __init__(self, letter_id: str, note_text: str = "") -> None:
        self.letter_id = letter_id
        self.note_text = note_text
        self._findings: list[ClinicalFinding] = []
        self._sources: list[FindingSource] = []

    def add(self, finding: ClinicalFinding) -> None:
        if finding.letter_id != self.letter_id:
            raise ValueError(
                f"finding {finding.finding_id} belongs to {finding.letter_id}, "
                f"not {self.letter_id}"
            )
        self._findings.append(finding)

    def register_source(self, source: FindingSource) -> None:
        if source not in self._sources:
            self._sources.append(source)

    def extend(self, findings: Iterable[ClinicalFinding]) -> None:
        for finding in findings:
            self.add(finding)

    def findings(
        self,
        *,
        entity: str | None = None,
        producer_id: str | None = None,
        raw_surface: bool | None = None,
        evidence_valid: bool | None = None,
    ) -> tuple[ClinicalFinding, ...]:
        out = self._findings
        if entity is not None:
            out = [finding for finding in out if finding.entity == entity]
        if producer_id is not None:
            out = [finding for finding in out if finding.source.producer_id == producer_id]
        if raw_surface is not None:
            out = [finding for finding in out if finding.raw_surface is raw_surface]
        if evidence_valid is not None:
            out = [finding for finding in out if finding.evidence_valid is evidence_valid]
        return tuple(out)

    def by_entity(self, entity: str) -> tuple[ClinicalFinding, ...]:
        return self.findings(entity=entity)

    def sources(self, *, producer_id: str | None = None) -> tuple[FindingSource, ...]:
        out = self._sources
        if producer_id is not None:
            out = [source for source in out if source.producer_id == producer_id]
        return tuple(out)

    def __len__(self) -> int:
        return len(self._findings)
