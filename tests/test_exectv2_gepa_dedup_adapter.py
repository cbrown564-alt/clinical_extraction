"""Tests for the retained GEPA de-duplicated-fact adapter."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.dedup_adapter import (
    COMPONENT_OWNER,
    clinical_facts_to_mentions,
    parse_dedup_clinical_facts_json,
    to_predicted_letter_from_dedup_facts,
)

NOTE = (
    "She has focal epilepsy. No seizures since last review. "
    "Current treatment is lamotrigine 200 mg twice daily. MRI brain was normal."
)
LETTER = ExectLetter(letter_id="GEPA-ADAPTER-1", note_text=NOTE)


def _facts() -> list[dict[str, str]]:
    return [
        {
            "family": "diagnosis",
            "concept": "focal epilepsy",
            "negation": "affirmed",
            "evidence": "focal epilepsy",
        },
        {
            "family": "seizure_frequency",
            "seizure_type": "seizures",
            "state": "seizure_free",
            "evidence": "No seizures since last review.",
        },
        {
            "family": "prescription",
            "drug": "lamotrigine",
            "dose": "200",
            "dose_unit": "mg",
            "frequency": "twice daily",
            "evidence": "lamotrigine 200 mg twice daily",
        },
        {
            "family": "investigation",
            "modality": "MRI",
            "performed": "yes",
            "result": "normal",
            "evidence": "MRI brain was normal.",
        },
    ]


def test_parser_and_adapter_preserve_one_fact_per_mention() -> None:
    record, errors = parse_dedup_clinical_facts_json(
        json.dumps({"clinical_facts": [*_facts(), _facts()[0]]})
    )

    assert record is not None
    assert errors == []
    mentions, provenance, adapter_notes = clinical_facts_to_mentions(record.clinical_facts)

    assert adapter_notes == []
    assert [mention.entity for mention in mentions] == [
        "Diagnosis",
        "SeizureFrequency",
        "Prescription",
        "Investigations",
        "Diagnosis",
    ]
    assert all(item["added_fact"] is False for item in provenance)
    assert all(item["deduplicated_by_adapter"] is False for item in provenance)


def test_projection_uses_exact_evidence_and_gepa_attribution() -> None:
    record, errors = parse_dedup_clinical_facts_json(json.dumps({"clinical_facts": _facts()}))
    assert record is not None
    assert errors == []

    predicted, gate_warnings, provenance, adapter_notes = (
        to_predicted_letter_from_dedup_facts(LETTER, record)
    )

    assert gate_warnings == []
    assert adapter_notes == []
    assert len(provenance) == 4
    assert [mention.component_owner for mention in predicted.mentions] == [COMPONENT_OWNER] * 4
    assert [mention.entity for mention in predicted.mentions] == [
        "Diagnosis",
        "SeizureFrequency",
        "Prescription",
        "Investigations",
    ]


def test_parser_drops_malformed_facts_with_diagnostics() -> None:
    record, errors = parse_dedup_clinical_facts_json(
        json.dumps(
            {
                "clinical_facts": [
                    {"family": "diagnosis", "concept": "epilepsy"},
                    {"family": "unsupported", "evidence": "text"},
                    "not an object",
                ]
            }
        )
    )

    assert record is not None
    assert record.clinical_facts == []
    assert len(errors) == 3
