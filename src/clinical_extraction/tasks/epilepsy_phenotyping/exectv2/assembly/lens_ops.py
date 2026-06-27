"""Shared assembly-lens helpers: policy types, finding copies, residual sources."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    FindingSource,
    ProvenanceEvent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import DIAGNOSIS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    diagnosis_category_for_concept,
)


@dataclass(frozen=True)
class LensPolicy:
    producer_id: str
    source_lane: str
    ownership_label: str
    portability: str | None


@dataclass(frozen=True)
class LensResult:
    entity: str
    lens_id: str
    findings: tuple[ClinicalFinding, ...]
    diagnostics: dict[str, object]


def text_counts(findings: list[ClinicalFinding]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.text] = counts.get(finding.text, 0) + 1
    return dict(sorted(counts.items()))


def rewrite_counts(findings: list[ClinicalFinding]) -> dict[str, int]:
    return text_counts(findings)


def first_source_finding_for_entity(
    store: ClinicalFindingStore,
    *,
    entity: str | None,
    policy: LensPolicy,
) -> ClinicalFinding | None:
    candidates = store.findings(
        entity=entity,
        producer_id=policy.producer_id,
        raw_surface=None,
    )
    return candidates[0] if candidates else None


def first_source_finding(
    store: ClinicalFindingStore,
    policy: LensPolicy,
) -> ClinicalFinding | None:
    return first_source_finding_for_entity(store, entity=DIAGNOSIS.name, policy=policy)


def source_for_residual(
    store: ClinicalFindingStore,
    *,
    entity: str | None,
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    ownership_suffix: str,
) -> FindingSource | None:
    if selected:
        base = selected[0].source
    else:
        seed = first_source_finding_for_entity(store, entity=entity, policy=policy)
        if seed is None:
            seed = first_source_finding_for_entity(store, entity=None, policy=policy)
        if seed is not None:
            base = seed.source
        else:
            sources = store.sources(producer_id=policy.producer_id) or store.sources()
            if not sources:
                return None
            base = sources[0]
    return FindingSource(
        producer_id=base.producer_id,
        artifact_path=base.artifact_path,
        pipeline_family=base.pipeline_family,
        model=base.model,
        prompt_version=base.prompt_version,
        mode=base.mode,
        ownership_label=f"{base.ownership_label}+{ownership_suffix}",
        source_lane=base.source_lane or policy.source_lane,
        fact_origin="post_model_rescue",
    )


def finding_with_text_attributes(
    finding: ClinicalFinding,
    *,
    text: str,
    attributes: dict[str, str],
    owner_suffix: str,
    provenance: ProvenanceEvent,
) -> ClinicalFinding:
    source = FindingSource(
        producer_id=finding.source.producer_id,
        artifact_path=finding.source.artifact_path,
        pipeline_family=finding.source.pipeline_family,
        model=finding.source.model,
        prompt_version=finding.source.prompt_version,
        mode=finding.source.mode,
        ownership_label=f"{finding.source.ownership_label}+{owner_suffix}",
        source_lane=finding.source.source_lane,
        fact_origin=finding.source.fact_origin,
    )
    return ClinicalFinding(
        finding_id=f"{finding.finding_id}:{owner_suffix}",
        letter_id=finding.letter_id,
        entity=finding.entity,
        text=text,
        attributes={str(k): str(v) for k, v in attributes.items()},
        evidence=finding.evidence,
        normalized_concept=finding.normalized_concept,
        assertion=finding.assertion,
        confidence=finding.confidence,
        source=source,
        provenance=(*finding.provenance, provenance),
        rationale=finding.rationale,
        evidence_valid=finding.evidence_valid,
        raw_surface=finding.raw_surface,
    )


def diagnosis_finding_with_text(
    finding: ClinicalFinding,
    text: str,
    *,
    owner_suffix: str,
    provenance: ProvenanceEvent,
) -> ClinicalFinding:
    attributes = {
        key: value
        for key, value in dict(finding.attributes).items()
        if key not in {"CUI", "CUIPhrase"}
    }
    attributes = sd.diagnosis_convention_attribute_repairs(
        text,
        evidence=finding.evidence or finding.text,
        attributes=attributes,
    )
    attributes.setdefault("DiagCategory", diagnosis_category_for_concept(text))
    source = FindingSource(
        producer_id=finding.source.producer_id,
        artifact_path=finding.source.artifact_path,
        pipeline_family=finding.source.pipeline_family,
        model=finding.source.model,
        prompt_version=finding.source.prompt_version,
        mode=finding.source.mode,
        ownership_label=f"{finding.source.ownership_label}+{owner_suffix}",
        source_lane=finding.source.source_lane,
        fact_origin=finding.source.fact_origin,
    )
    return ClinicalFinding(
        finding_id=f"{finding.finding_id}:alias:{normalize_phrase(text).replace(' ', '_')}",
        letter_id=finding.letter_id,
        entity=finding.entity,
        text=text,
        attributes=attributes,
        evidence=finding.evidence,
        normalized_concept=text,
        assertion=attributes.get("Certainty") or attributes.get("Negation"),
        confidence=finding.confidence,
        source=source,
        provenance=(*finding.provenance, provenance),
        rationale=finding.rationale,
        evidence_valid=finding.evidence_valid,
        raw_surface=finding.raw_surface,
    )


def diagnosis_added_finding(
    store: ClinicalFindingStore,
    *,
    text: str,
    evidence: str,
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> ClinicalFinding | None:
    source = source_for_residual(
        store,
        entity=DIAGNOSIS.name,
        selected=selected,
        policy=policy,
        ownership_suffix="standard_dictionary_diagnosis_residual",
    )
    if source is None:
        return None
    attributes = {
        "DiagCategory": diagnosis_category_for_concept(text),
        "Certainty": "5",
        "Negation": "Affirmed",
    }
    return ClinicalFinding(
        finding_id=(
            f"{store.letter_id}:{policy.producer_id}:Diagnosis:lens:{lens_id}:"
            f"{normalize_phrase(text).replace(' ', '_')}"
        ),
        letter_id=store.letter_id,
        entity=DIAGNOSIS.name,
        text=text,
        attributes=attributes,
        evidence=evidence,
        normalized_concept=text,
        assertion=attributes["Certainty"],
        confidence="high",
        source=source,
        provenance=(
            ProvenanceEvent(
                stage="entity_lens",
                action="added_diagnosis_residual_from_dictionary",
                owner="standard_dictionary",
                portability="benchmark_format",
                detail={
                    "lens_id": lens_id,
                    "producer_id": policy.producer_id,
                    "source_lane": policy.source_lane,
                    "rule_category": "benchmark_format",
                    "target_text": text,
                    "evidence": evidence,
                },
            ),
        ),
        rationale="The source phrase matches a dev residual benchmark-format concept.",
        evidence_valid=evidence in store.note_text,
        raw_surface=False,
    )


def has_diagnosis_text_with_evidence(
    findings: list[ClinicalFinding],
    *,
    text: str,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    target_text = normalize_phrase(text)
    target_evidence = normalize_phrase(evidence)
    target_attrs = {
        key: value
        for key, value in dict(attributes).items()
        if key in {"Certainty", "Negation"}
    }
    for finding in findings:
        if normalize_phrase(finding.text) != target_text:
            continue
        if normalize_phrase(finding.evidence or finding.text) != target_evidence:
            continue
        attrs = {
            key: value
            for key, value in dict(finding.attributes).items()
            if key in {"Certainty", "Negation"}
        }
        if attrs == target_attrs:
            return True
    return False
