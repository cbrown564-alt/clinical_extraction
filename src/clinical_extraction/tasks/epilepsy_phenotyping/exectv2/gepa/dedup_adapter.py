"""Parse and project GEPA's de-duplicated clinical-fact output."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
)

from ..contract.prediction import PredictedLetter
from ..data import ExectLetter
from ..llm.pipelines.key_entities_structured import MentionForEvidence, to_predicted_letter
from ..llm.shared.json_parse import extract_json_object

PROMPT_VERSION = "exectv2_gepa_dedup_adapter_v1"
PIPELINE_FAMILY = "exectv2_gepa_dedup"
COMPONENT_OWNER = "gepa_llm_only_dedup"

_FACT_FAMILIES = {
    "diagnosis",
    "seizure_frequency",
    "prescription",
    "investigation",
}


class DedupClinicalFactRecord(BaseModel):
    """One simplified clinical fact emitted by the retained GEPA program."""

    model_config = ConfigDict(extra="ignore")

    family: str
    evidence: str
    concept: str = ""
    negation: str = ""
    seizure_type: str = ""
    state: str = ""
    drug: str = ""
    dose: str = ""
    dose_unit: str = ""
    frequency: str = ""
    modality: str = ""
    performed: str = ""
    result: str = ""
    source_text: str = ""
    attributes: dict[str, str] = Field(default_factory=dict)


class DedupClinicalFactsRecord(BaseModel):
    """Validated collection of GEPA de-duplicated clinical facts."""

    model_config = ConfigDict(extra="ignore")

    clinical_facts: list[DedupClinicalFactRecord] = Field(default_factory=list)


def parse_dedup_clinical_facts_json(
    raw_output: str,
) -> tuple[DedupClinicalFactsRecord | None, list[str]]:
    """Parse model output while preserving format-repair diagnostics."""

    try:
        payload, dialect_notes = parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    facts, fact_notes = _coerce_facts(
        payload.get("clinical_facts") or payload.get("facts") or []
    )
    notes = [*dialect_notes, *fact_notes]
    try:
        record = DedupClinicalFactsRecord.model_validate({**payload, "clinical_facts": facts})
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def clinical_facts_to_mentions(
    facts: Sequence[DedupClinicalFactRecord | Mapping[str, Any]],
) -> tuple[list[MentionForEvidence], list[dict[str, Any]], list[str]]:
    """Map model facts to scorer-facing mentions without adding or merging facts."""

    mentions: list[MentionForEvidence] = []
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


def to_predicted_letter_from_dedup_facts(
    letter: ExectLetter,
    record: DedupClinicalFactsRecord | Mapping[str, Any],
) -> tuple[PredictedLetter, list[str], list[dict[str, Any]], list[str]]:
    """Project GEPA facts through the retained evidence and schema gates."""

    fact_record = (
        record
        if isinstance(record, DedupClinicalFactsRecord)
        else DedupClinicalFactsRecord.model_validate(record)
    )
    mentions, provenance, adapter_notes = clinical_facts_to_mentions(
        fact_record.clinical_facts
    )
    predicted, gate_warnings = to_predicted_letter(
        letter.letter_id,
        mentions,
        note_text=letter.note_text,
        prompt_version=PROMPT_VERSION,
        component_owner=COMPONENT_OWNER,
        pipeline_family=PIPELINE_FAMILY,
    )
    return predicted, gate_warnings, provenance, adapter_notes


def _coerce_facts(facts: Any) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(facts, list):
        return [], ["clinical_facts:schema_validation_error: facts_not_list"]

    coerced: list[dict[str, Any]] = []
    notes: list[str] = []
    for index, fact in enumerate(facts):
        if not isinstance(fact, Mapping):
            notes.append(f"clinical_facts:dropped_malformed_fact: fact[{index}]")
            continue
        normalized = {
            str(key): value if key == "attributes" else "" if value is None else str(value).strip()
            for key, value in fact.items()
        }
        family = _normalize_fact_family(str(normalized.get("family", "")))
        if family not in _FACT_FAMILIES:
            notes.append(
                "clinical_facts:dropped_malformed_fact: "
                f"fact[{index}] family={normalized.get('family')!r}"
            )
            continue
        normalized["family"] = family
        if not normalized.get("evidence"):
            notes.append(
                f"clinical_facts:dropped_malformed_fact: fact[{index}] missing=evidence"
            )
            continue
        coerced.append(normalized)
    return coerced, notes


def _clinical_fact_to_mention(
    fact: DedupClinicalFactRecord,
    *,
    index: int,
    notes: list[str],
) -> MentionForEvidence | None:
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
            "seizure_frequency": (
                fact.source_text.strip() or fact.seizure_type.strip() or "seizures"
            ),
            "prescription": fact.source_text.strip() or fact.drug.strip(),
            "investigation": (
                fact.source_text.strip() or _normalize_modality(fact.modality) or ""
            ),
        }
        entity = entity_by_family.get(family)
        text = text_by_family.get(family, "")
        if entity and text:
            return MentionForEvidence(
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
        return MentionForEvidence(
            entity="Diagnosis",
            text=text,
            attributes={"Negation": _normalize_negation(fact.negation)},
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated diagnosis fact",
        )
    if family == "seizure_frequency":
        return MentionForEvidence(
            entity="SeizureFrequency",
            text=fact.seizure_type.strip() or "seizures",
            attributes=_seizure_state_attributes(fact.state, notes=notes, index=index),
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated seizure-frequency fact",
        )
    if family == "prescription":
        drug = fact.drug.strip()
        if not drug:
            notes.append(f"clinical_facts.fact[{index}]:missing_prescription_drug")
            return None
        attributes = {"DrugName": drug}
        if fact.dose.strip():
            attributes["DrugDose"] = fact.dose.strip()
        if fact.dose_unit.strip():
            attributes["DoseUnit"] = _normalize_dose_unit(fact.dose_unit)
        if fact.frequency.strip():
            attributes["Frequency"] = _normalize_frequency(fact.frequency)
        return MentionForEvidence(
            entity="Prescription",
            text=fact.source_text.strip() or drug,
            attributes=attributes,
            evidence=evidence,
            confidence=confidence,
            rationale="mapped from model-emitted de-duplicated prescription fact",
        )
    if family == "investigation":
        modality = _normalize_modality(fact.modality)
        if modality is None:
            notes.append(f"clinical_facts.fact[{index}]:unsupported_modality={fact.modality!r}")
            return None
        return MentionForEvidence(
            entity="Investigations",
            text=modality,
            attributes={
                f"{modality}_Performed": _normalize_performed(fact.performed),
                f"{modality}_Results": _normalize_result(fact.result),
            },
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
    if value.strip().lower() in {"negated", "negative", "denied", "absent", "no"}:
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
    if value.strip().lower() in {"g", "gram", "grams"}:
        return "g"
    return "mg"


def _normalize_frequency(value: str) -> str:
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
    return aliases.get(value.strip().lower(), value.strip())


def _normalize_modality(value: str) -> str | None:
    modality = value.strip().lower()
    if modality in {"mri", "mri scan", "brain mri"}:
        return "MRI"
    if modality in {"ct", "ct scan"}:
        return "CT"
    if modality in {
        "eeg",
        "standard eeg",
        "sleep deprived eeg",
        "sleep-deprived eeg",
        "telemetry",
        "video telemetry",
        "videotelemetry",
    }:
        return "EEG"
    return None


def _normalize_performed(value: str) -> str:
    if value.strip().lower() in {"no", "n", "false", "not performed"}:
        return "No"
    return "Yes"


def _normalize_result(value: str) -> str:
    result = value.strip().lower()
    if result in {"normal", "negative"}:
        return "Normal"
    if result in {"abnormal", "positive", "abnormality"}:
        return "Abnormal"
    return "Unknown"
