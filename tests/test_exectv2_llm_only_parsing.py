"""Invariant-focused tests for exectv2 llm only parsing."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)


def test_parse_structured_events_coerces_nested_values() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "medication",
                    "anchor_text": "lamotrigine",
                    "evidence": "lamotrigine 200 mg twice daily",
                    "event_state": {"dose": 200},
                    "mentions": [
                        {
                            "entity": PRESCRIPTION.name,
                            "text": "lamotrigine",
                            "attributes": {
                                "DrugName": "lamotrigine",
                                "DrugDose": 200,
                                "DoseUnit": "mg",
                                "Frequency": 2,
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "Medication stated.",
                }
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    event = record.clinical_events[0]
    assert event.event_state["dose"] == "200"
    assert event.mentions[0].attributes["DrugDose"] == "200"
    assert event.mentions[0].attributes["Frequency"] == "2"
    assert any("coerced_attribute_value" in error for error in errors)


def test_parse_structured_events_drops_unknown_event_family_without_coercion() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diabetes",
                    "anchor_text": "Diabetes",
                    "evidence": "Diabetes, hypothyroidism",
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "Diabetes",
                            "attributes": {"Negation": "Affirmed"},
                        }
                    ],
                    "confidence": "high",
                    "rationale": "",
                },
                {
                    "family": "diagnosis",
                    "anchor_text": "epilepsy",
                    "evidence": "Diagnosis: epilepsy",
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "epilepsy",
                            "attributes": {
                                "DiagCategory": "Epilepsy",
                                "Certainty": "5",
                                "Negation": "Affirmed",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "Diagnosis stated.",
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert [event.family for event in record.clinical_events] == ["diagnosis"]
    assert "dropped_unknown_event_family: event[0] family='diabetes'" in errors


def test_parse_structured_events_uses_last_complete_payload_after_thinking_leak() -> None:
    first = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "anchor_text": "earlier epilepsy",
                    "evidence": "Diagnosis: epilepsy",
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "epilepsy",
                            "attributes": {
                                "DiagCategory": "Epilepsy",
                                "Certainty": "5",
                                "Negation": "Affirmed",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "",
                }
            ]
        }
    )
    final = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "anchor_text": "final focal epilepsy",
                    "evidence": "Diagnosis: focal epilepsy",
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "focal epilepsy",
                            "attributes": {
                                "DiagCategory": "Epilepsy",
                                "Certainty": "5",
                                "Negation": "Affirmed",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "",
                }
            ]
        }
    )
    raw = f"{first}\n</think>\nThe final answer is:\n{final}"

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert errors == []
    assert record.clinical_events[0].anchor_text == "final focal epilepsy"
