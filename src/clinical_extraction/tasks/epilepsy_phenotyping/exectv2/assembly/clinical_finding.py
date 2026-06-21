"""Evidence-backed clinical finding objects for ExECTv2 assembly."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)

Confidence = Literal["low", "medium", "high"]
_CONFIDENCE_VALUES = {"low", "medium", "high"}


@dataclass(frozen=True)
class FindingSource:
    """Source metadata for one candidate producer emission."""

    producer_id: str
    artifact_path: str
    pipeline_family: str
    model: str
    prompt_version: str
    mode: str
    ownership_label: str
    source_lane: str = ""


@dataclass(frozen=True)
class ProvenanceEvent:
    """One assembly or deterministic action attached to a finding."""

    stage: str
    action: str
    owner: str
    portability: str | None
    detail: Mapping[str, Any]

    def to_row(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "action": self.action,
            "owner": self.owner,
            "portability": self.portability,
            "detail": dict(self.detail),
        }


@dataclass(frozen=True)
class ClinicalFinding:
    """Richer internal representation rendered to scorer mentions at the edge."""

    finding_id: str
    letter_id: str
    entity: str
    text: str
    attributes: Mapping[str, str]
    evidence: str
    normalized_concept: str | None
    assertion: str | None
    confidence: Confidence | None
    source: FindingSource
    provenance: tuple[ProvenanceEvent, ...]
    rationale: str = ""
    evidence_valid: bool = True
    raw_surface: bool = False

    @classmethod
    def from_mention_row(
        cls,
        mention: Mapping[str, Any],
        *,
        finding_id: str,
        letter_id: str,
        entity: str,
        source: FindingSource,
        diagnostics: Mapping[str, Any],
        raw_surface: bool,
        evidence_valid: bool,
    ) -> ClinicalFinding:
        attributes = {
            str(key): str(value)
            for key, value in dict(mention.get("attributes", {})).items()
        }
        confidence = mention.get("confidence")
        if confidence not in _CONFIDENCE_VALUES:
            confidence = None
        return cls(
            finding_id=finding_id,
            letter_id=letter_id,
            entity=entity,
            text=str(mention.get("text", "")),
            attributes=attributes,
            evidence=str(mention.get("evidence", "")),
            normalized_concept=_normalized_concept(attributes, mention),
            assertion=_assertion(attributes),
            confidence=confidence,
            source=source,
            provenance=(
                ProvenanceEvent(
                    stage="candidate_producer",
                    action="emitted_raw_candidate" if raw_surface else "emitted_scored_candidate",
                    owner=source.ownership_label,
                    portability=None,
                    detail={
                        "producer_id": source.producer_id,
                        "source_lane": source.source_lane,
                        "raw_surface": raw_surface,
                        "diagnostics": dict(diagnostics),
                    },
                ),
            ),
            rationale=str(mention.get("rationale", "")),
            evidence_valid=evidence_valid,
            raw_surface=raw_surface,
        )

    def with_provenance(self, event: ProvenanceEvent) -> ClinicalFinding:
        return ClinicalFinding(
            finding_id=self.finding_id,
            letter_id=self.letter_id,
            entity=self.entity,
            text=self.text,
            attributes=self.attributes,
            evidence=self.evidence,
            normalized_concept=self.normalized_concept,
            assertion=self.assertion,
            confidence=self.confidence,
            source=self.source,
            provenance=(*self.provenance, event),
            rationale=self.rationale,
            evidence_valid=self.evidence_valid,
            raw_surface=self.raw_surface,
        )

    def to_predicted_mention(self) -> PredictedMention:
        return PredictedMention(
            entity=self.entity,
            text=self.text,
            attributes=dict(self.attributes),
            evidence=self.evidence,
            rationale=self.rationale,
            confidence=self.confidence,
            component_owner=self.source.ownership_label,
        )

    def to_row(self) -> dict[str, Any]:
        return {
            "entity": self.entity,
            "text": self.text,
            "attributes": dict(self.attributes),
            "evidence": self.evidence,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "component_owner": self.source.ownership_label,
            "source_artifact": self.source.artifact_path,
            "source_lane": self.source.source_lane,
            "source_pipeline_family": self.source.pipeline_family,
            "source_model": self.source.model,
            "source_prompt_version": self.source.prompt_version,
            "raw_surface": self.raw_surface,
            "evidence_valid": self.evidence_valid,
            "finding_id": self.finding_id,
            "normalized_concept": self.normalized_concept,
            "assertion": self.assertion,
            "provenance": [event.to_row() for event in self.provenance],
            "deterministic_provenance": self.deterministic_diagnostics,
        }

    @property
    def deterministic_diagnostics(self) -> dict[str, Any]:
        for event in self.provenance:
            diagnostics = event.detail.get("diagnostics")
            if isinstance(diagnostics, Mapping):
                return dict(diagnostics)
        return {}


def _normalized_concept(
    attributes: Mapping[str, str],
    mention: Mapping[str, Any],
) -> str | None:
    for key in ("CUI", "CUIPhrase", "DrugName", "DiagCategory"):
        value = attributes.get(key)
        if value:
            return value
    text = str(mention.get("text", "")).strip()
    return text or None


def _assertion(attributes: Mapping[str, str]) -> str | None:
    for key in ("Negation", "Certainty", "FrequencyChange"):
        value = attributes.get(key)
        if value:
            return value
    return None
