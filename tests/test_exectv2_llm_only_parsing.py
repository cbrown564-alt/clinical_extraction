"""Invariant-focused tests for exectv2 llm only parsing."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)


def test_parse_flat_compact_events() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "evidence": "She has focal epilepsy.",
                    "fact": "focal epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                },
                {
                    "family": "medication",
                    "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                    "fact": "lamotrigine 200 mg twice daily",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": 200,
                        "DoseUnit": "mg",
                        "Frequency": 2,
                    },
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)
    mentions = structured.flatten_events(record) if record is not None else []

    assert record is not None
    assert not any(str(error).startswith("schema_validation_error:") for error in errors)
    assert [event.family for event in record.clinical_events] == [
        "diagnosis",
        "medication",
    ]
    assert [mention.entity for mention in mentions] == [
        DIAGNOSIS.name,
        PRESCRIPTION.name,
    ]
    assert mentions[0].text == "focal epilepsy"
    assert mentions[0].attributes == {"DiagCategory": "Epilepsy"}
    assert mentions[1].text == "lamotrigine 200 mg twice daily"
    assert mentions[1].attributes["DrugDose"] == "200"
    assert mentions[1].attributes["Frequency"] == "2"


def test_parse_compact_short_attribute_names() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "medication",
                    "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                    "fact": "lamotrigine",
                    "attributes": {
                        "name": "lamotrigine",
                        "dose": 200,
                        "unit": "mg",
                        "frequency": "as_required",
                    },
                },
                {
                    "family": "diagnosis",
                    "evidence": "She has focal epilepsy.",
                    "fact": "focal epilepsy",
                    "attributes": {"category": "epilepsy"},
                },
                {
                    "family": "seizure_frequency",
                    "evidence": "2 focal seizures per month.",
                    "fact": "focal seizures",
                    "attributes": {
                        "count": 2,
                        "period": "month",
                        "when": "since",
                        "point": "last_clinic",
                    },
                },
                {
                    "family": "investigation",
                    "evidence": "MRI brain was normal.",
                    "fact": "MRI",
                    "attributes": {
                        "mri_performed": "yes",
                        "mri_result": "normal",
                    },
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)
    mentions = structured.flatten_events(record) if record is not None else []

    assert record is not None
    assert not any(str(error).startswith("schema_validation_error:") for error in errors)
    by_entity = {mention.entity: mention.attributes for mention in mentions}
    assert by_entity[PRESCRIPTION.name] == {
        "DrugName": "lamotrigine",
        "DrugDose": "200",
        "DoseUnit": "mg",
        "Frequency": "As_Required",
    }
    assert by_entity[DIAGNOSIS.name] == {"DiagCategory": "Epilepsy"}
    assert by_entity[SEIZURE_FREQUENCY.name] == {
        "NumberOfSeizures": "2",
        "TimePeriod": "Month",
        "TimeSince_or_TimeOfEvent": "Since",
        "PointInTime": "LastClinic",
    }
    assert by_entity[INVESTIGATIONS.name] == {
        "MRI_Performed": "Yes",
        "MRI_Results": "Normal",
    }


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


def test_sink_fields_are_parsed_but_never_flattened_into_scored_mentions() -> None:
    raw = json.dumps(
        {
            "clinical_events": [],
            "patient_history": [
                {"span": "blackouts", "kind": "unclassified_event"},
                {"span": "migraine", "kind": "comorbidity"},
            ],
            "medication_history": [
                {"span": "previously tried levetiracetam", "kind": "past_medication"},
                {"span": "plan to start lamotrigine", "kind": "planned_medication"},
            ],
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert errors == []
    assert record is not None
    assert [item.model_dump() for item in record.patient_history] == [
        {"span": "blackouts", "kind": "unclassified_event"},
        {"span": "migraine", "kind": "comorbidity"},
    ]
    assert [item.model_dump() for item in record.medication_history] == [
        {"span": "previously tried levetiracetam", "kind": "past_medication"},
        {"span": "plan to start lamotrigine", "kind": "planned_medication"},
    ]
    assert structured.flatten_events(record) == []


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


def test_v26_flat_events_map_to_scored_mentions_and_keep_sinks_out() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "clinical_family": "medication",
                    "event": "lamotrigine",
                    "evidence": "Current medication: lamotrigine 100 mg in the morning.",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "100",
                        "DoseUnit": "mg",
                        "Frequency": "1",
                        "Status": "current",
                    },
                },
                {
                    "clinical_family": "medication",
                    "event": "lamotrigine",
                    "evidence": "Please start lamotrigine 25 mg once a day.",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "25",
                        "DoseUnit": "mg",
                        "Frequency": "1",
                        "Status": "planned",
                    },
                },
                {
                    "clinical_family": "history",
                    "event": "Seizure-like episodes",
                    "evidence": "Seizure-like episodes several times a week. Not epileptic.",
                    "attributes": {"Kind": "non_epileptic_event"},
                },
                {
                    "clinical_family": "diagnosis",
                    "event": "focal epilepsy",
                    "evidence": "Diagnosis: focal epilepsy.",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)
    mentions = structured.flatten_events(record) if record is not None else []

    assert record is not None
    assert "schema_validation_error" not in " ".join(errors)
    assert [event.family for event in record.clinical_events] == [
        "medication",
        "medication",
        "history",
        "diagnosis",
    ]
    assert [mention.entity for mention in mentions] == [
        PRESCRIPTION.name,
        DIAGNOSIS.name,
    ]
    assert mentions[0].text == "lamotrigine"
    assert "Status" not in mentions[0].attributes
    assert mentions[0].attributes["DrugDose"] == "100"
    assert [item.kind for item in record.patient_history] == ["non_epileptic_event"]
    assert [item.span for item in record.patient_history] == ["Seizure-like episodes"]
    assert [item.kind for item in record.medication_history] == ["planned_medication"]


def test_v26_missing_event_does_not_fail_the_letter() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "clinical_family": "medication",
                    "evidence": "Current medication: lamotrigine 100 mg.",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "Status": "current",
                    },
                },
                {
                    "clinical_family": "diagnosis",
                    "event": "focal epilepsy",
                    "evidence": "Diagnosis: focal epilepsy.",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)
    mentions = structured.flatten_events(record) if record is not None else []

    assert record is not None
    assert not any(str(error).startswith("schema_validation_error:") for error in errors)
    assert [event.family for event in record.clinical_events] == [
        "medication",
        "diagnosis",
    ]
    assert record.clinical_events[0].anchor_text == ""
    assert record.clinical_events[0].mentions == []
    assert [mention.entity for mention in mentions] == [DIAGNOSIS.name]
    assert mentions[0].text == "focal epilepsy"
