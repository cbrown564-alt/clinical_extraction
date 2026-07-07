"""Adapter mapping de-duplicated clinical facts to/from scorer-facing mentions."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.records import (
    DedupClinicalFactRecord,
)


def clinical_facts_to_mentions(
    facts: Sequence[DedupClinicalFactRecord | Mapping[str, Any]],
) -> tuple[list[structured.MentionForEvidence], list[dict[str, Any]], list[str]]:
    """Map model-emitted simplified facts to scorer-facing mentions one-to-one."""

    mentions: list[structured.MentionForEvidence] = []
    provenance: list[dict[str, Any]] = []
    notes: list[str] = []
    for index, raw_fact in enumerate(facts):
        fact = (
            raw_fact
            if isinstance(raw_fact, DedupClinicalFactRecord)
            else DedupClinicalFactRecord.model_validate(raw_fact)
        )
        mention = _clinical_fact_to_mention(fact, index=index, notes=notes)
        if mention is None:
            continue
        mentions.append(mention)
        provenance.append(
            {
                "fact_index": index,
                "family": fact.family,
                "action": "representation_mapping_only",
                "target_entity": mention.entity,
                "added_fact": False,
                "deduplicated_by_adapter": False,
            }
        )
    return mentions, provenance, notes


def _clinical_fact_to_mention(
    fact: DedupClinicalFactRecord,
    *,
    index: int,
    notes: list[str],
) -> structured.MentionForEvidence | None:
    family = _normalize_fact_family(fact.family)
    evidence = fact.evidence.strip()
    confidence: Literal["low", "medium", "high"] = "medium"
    if fact.attributes:
        entity_by_family = {
            "diagnosis": "Diagnosis",
            "seizure_frequency": "SeizureFrequency",
            "prescription": "Prescription",
            "investigation": "Investigations",
        }
        text_by_family = {
            "diagnosis": fact.source_text.strip() or fact.concept.strip(),
            "seizure_frequency": fact.source_text.strip()
            or fact.seizure_type.strip()
            or "seizures",
            "prescription": fact.source_text.strip() or fact.drug.strip(),
            "investigation": fact.source_text.strip() or _normalize_modality(fact.modality) or "",
        }
        entity = entity_by_family.get(family)
        text = text_by_family.get(family, "")
        if entity and text:
            return structured.MentionForEvidence(
                entity=entity,
                text=text,
                attributes=dict(fact.attributes),
                evidence=evidence,
                confidence=confidence,
                rationale="mapped from replayed model-emitted de-duplicated fact",
            )
    if family == "diagnosis":
        text = fact.concept.strip()
        if not text:
            notes.append(f"clinical_facts.fact[{index}]:missing_diagnosis_concept")
            return None
        negation = _normalize_negation(fact.negation)
        return structured.MentionForEvidence(
            entity="Diagnosis",
            text=text,
            attributes={"Negation": negation},
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated diagnosis fact",
        )
    if family == "seizure_frequency":
        text = fact.seizure_type.strip() or "seizures"
        attrs = _seizure_state_attributes(fact.state, notes=notes, index=index)
        return structured.MentionForEvidence(
            entity="SeizureFrequency",
            text=text,
            attributes=attrs,
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated seizure-frequency fact",
        )
    if family == "prescription":
        drug = fact.drug.strip()
        if not drug:
            notes.append(f"clinical_facts.fact[{index}]:missing_prescription_drug")
            return None
        attrs = {"DrugName": drug}
        if fact.dose.strip():
            attrs["DrugDose"] = fact.dose.strip()
        if fact.dose_unit.strip():
            attrs["DoseUnit"] = _normalize_dose_unit(fact.dose_unit)
        if fact.frequency.strip():
            attrs["Frequency"] = _normalize_frequency(fact.frequency)
        return structured.MentionForEvidence(
            entity="Prescription",
            text=fact.source_text.strip() or drug,
            attributes=attrs,
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated prescription fact",
        )
    if family == "investigation":
        modality = _normalize_modality(fact.modality)
        if modality is None:
            notes.append(f"clinical_facts.fact[{index}]:unsupported_modality={fact.modality!r}")
            return None
        attrs = {
            f"{modality}_Performed": _normalize_performed(fact.performed),
            f"{modality}_Results": _normalize_result(fact.result),
        }
        return structured.MentionForEvidence(
            entity="Investigations",
            text=modality,
            attributes=attrs,
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated investigation fact",
        )
    notes.append(f"clinical_facts.fact[{index}]:unsupported_family={fact.family!r}")
    return None


def _normalize_fact_family(value: str) -> str:
    family = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "medication": "prescription",
        "medications": "prescription",
        "rx": "prescription",
        "investigations": "investigation",
        "seizurefrequency": "seizure_frequency",
        "seizure_frequency_state": "seizure_frequency",
    }
    return aliases.get(family, family)


def _normalize_negation(value: str) -> str:
    negation = value.strip().lower()
    if negation in {"negated", "negative", "denied", "absent", "no"}:
        return "Negated"
    return "Affirmed"


def _seizure_state_attributes(
    state: str,
    *,
    notes: list[str],
    index: int,
) -> dict[str, str]:
    normalized = state.strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"active", "active_rate", "ongoing", "rate"}:
        return {"NumberOfSeizures": "1"}
    if normalized in {"seizure_free", "free", "none", "zero"}:
        return {"NumberOfSeizures": "0"}
    if normalized in {"changed", "change", "increased", "decreased", "worse", "improved"}:
        change = "Increased" if normalized in {"increased", "worse"} else "Same"
        return {"FrequencyChange": change}
    if normalized in {"unknown", ""}:
        return {}
    notes.append(f"clinical_facts.fact[{index}]:unknown_seizure_state={state!r}_mapped_unknown")
    return {}


def _normalize_dose_unit(value: str) -> str:
    unit = value.strip().lower()
    if unit in {"g", "gram", "grams"}:
        return "g"
    return "mg"


def _normalize_frequency(value: str) -> str:
    frequency = value.strip().lower()
    aliases = {
        "once": "1",
        "once daily": "1",
        "od": "1",
        "mane": "1",
        "nocte": "1",
        "twice": "2",
        "twice daily": "2",
        "bd": "2",
        "bid": "2",
        "three times daily": "3",
        "tds": "3",
        "tid": "3",
        "as required": "As_Required",
        "prn": "As_Required",
    }
    return aliases.get(frequency, value.strip())


def _normalize_modality(value: str) -> str | None:
    modality = value.strip().lower()
    if modality in {"mri", "mri scan", "brain mri"}:
        return "MRI"
    if modality in {"ct", "ct scan"}:
        return "CT"
    if modality in {"eeg", "standard eeg", "sleep deprived eeg", "sleep-deprived eeg"}:
        return "EEG"
    if modality in {"telemetry", "video telemetry", "videotelemetry"}:
        return "EEG"
    return None


def _normalize_performed(value: str) -> str:
    performed = value.strip().lower()
    if performed in {"no", "n", "false", "not performed"}:
        return "No"
    return "Yes"


def _normalize_result(value: str) -> str:
    result = value.strip().lower()
    if result in {"normal", "negative"}:
        return "Normal"
    if result in {"abnormal", "positive", "abnormality"}:
        return "Abnormal"
    return "Unknown"


def clinical_facts_from_mentions(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Build simplified facts from saved model-emitted mention rows for replay checks."""

    facts: list[dict[str, Any]] = []
    notes: list[str] = []
    for index, mention in enumerate(mentions):
        entity = str(mention.get("entity") or "")
        attrs = mention.get("attributes") or {}
        if not isinstance(attrs, Mapping):
            attrs = {}
        evidence = str(mention.get("evidence") or "")
        text = str(mention.get("text") or "")
        if entity == "Diagnosis":
            facts.append(
                {
                    "family": "diagnosis",
                    "concept": text,
                    "negation": str(attrs.get("Negation") or "Affirmed").lower(),
                    "attributes": {str(key): str(value) for key, value in attrs.items()},
                    "source_text": text,
                    "evidence": evidence or text,
                }
            )
        elif entity == "SeizureFrequency":
            facts.append(
                {
                    "family": "seizure_frequency",
                    "seizure_type": text or "seizures",
                    "state": _fact_state_from_seizure_attrs(attrs),
                    "attributes": {str(key): str(value) for key, value in attrs.items()},
                    "source_text": text,
                    "evidence": evidence or text,
                }
            )
        elif entity == "Prescription":
            facts.append(
                {
                    "family": "prescription",
                    "drug": str(attrs.get("DrugName") or text),
                    "dose": str(attrs.get("DrugDose") or ""),
                    "dose_unit": str(attrs.get("DoseUnit") or ""),
                    "frequency": str(attrs.get("Frequency") or ""),
                    "source_text": text,
                    "attributes": {str(key): str(value) for key, value in attrs.items()},
                    "evidence": evidence or text,
                }
            )
        elif entity == "Investigations":
            fact = _investigation_fact_from_attrs(attrs, text=text, evidence=evidence)
            if fact:
                facts.append(fact)
            else:
                notes.append(f"mention[{index}]:investigation_without_supported_modality")
        else:
            notes.append(f"mention[{index}]:out_of_scope_entity={entity!r}")
    return facts, notes


def _fact_state_from_seizure_attrs(attrs: Mapping[str, Any]) -> str:
    count_values = [
        str(attrs.get("NumberOfSeizures") or ""),
        str(attrs.get("LowerNumberOfSeizures") or ""),
        str(attrs.get("UpperNumberOfSeizures") or ""),
    ]
    if any(value == "0" for value in count_values):
        return "seizure_free"
    if any(value for value in count_values):
        return "active_rate"
    if attrs.get("FrequencyChange"):
        return "changed"
    return "unknown"


def _investigation_fact_from_attrs(
    attrs: Mapping[str, Any],
    *,
    text: str,
    evidence: str,
) -> dict[str, Any] | None:
    text_upper = text.upper()
    for modality in ("MRI", "CT", "EEG"):
        performed = str(attrs.get(f"{modality}_Performed") or "")
        result = str(attrs.get(f"{modality}_Results") or "")
        if performed or result or modality in text_upper.split():
            return {
                "family": "investigation",
                "modality": modality,
                "performed": performed.lower() or "yes",
                "result": result.lower() or "unknown",
                "attributes": {str(key): str(value) for key, value in attrs.items()},
                "source_text": text,
                "evidence": evidence or text,
            }
    return None
