"""Invariant-focused tests for exectv2 llm only parsing."""

from __future__ import annotations

import json
import time

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
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


def test_parse_repairs_missing_mention_object_close_without_changing_values() -> None:
    raw = (
        '{"clinical_events":[{"family":"diagnosis","anchor_text":"epilepsy",'
        '"evidence":"Diagnosis: epilepsy","event_state":{},"mentions":['
        '{"entity":"Diagnosis","text":"epilepsy","attributes":{"Negation":"Affirmed"},'
        '{"entity":"Diagnosis","text":"focal epilepsy","attributes":{"Negation":"Affirmed"}}'
        "}]}]}"
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert "json_dialect_repaired: missing_array_object_close" in errors
    assert [mention.text for mention in record.clinical_events[0].mentions] == [
        "epilepsy",
        "focal epilepsy",
    ]
    assert all(
        mention.attributes["Negation"] == "Affirmed"
        for mention in record.clinical_events[0].mentions
    )


def test_parse_does_not_rewrite_valid_json_with_mention_close_repair() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "anchor_text": "epilepsy",
                    "evidence": "Diagnosis: epilepsy",
                    "event_state": {},
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "epilepsy",
                            "attributes": {"Negation": "Affirmed"},
                        },
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "focal epilepsy",
                            "attributes": {"Negation": "Affirmed"},
                        },
                    ],
                    "confidence": "high",
                    "rationale": "",
                }
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert "json_dialect_repaired: missing_array_object_close" not in errors


def test_parse_mention_close_near_miss_finishes_quickly() -> None:
    chunk = (
        '"attributes":{"Negation":"Affirmed"}, '
        '{"entity":"Diagnosis","text":"seizure seizure seizure","attributes":'
        '{"Negation":"Affirmed"}}'
    )
    raw = "[" + ", ".join([chunk] * 1500) + " NO_CLOSE"

    started = time.perf_counter()
    record, errors = structured.parse_structured_events_json(raw)
    elapsed = time.perf_counter() - started

    assert record is None
    assert errors and str(errors[0]).startswith("invalid_json:")
    assert elapsed < 0.4


def test_extract_json_object_unclosed_fence_finishes_quickly() -> None:
    raw = "```json\n{" + (" x}" * 80_000)

    started = time.perf_counter()
    extracted = extract_json_object(raw)
    elapsed = time.perf_counter() - started

    assert extracted.startswith("{")
    assert elapsed < 0.4


def test_extract_json_object_reads_closed_fence() -> None:
    raw = 'prefix\n```json\n{"clinical_events": []}\n```\ntrailing'

    assert extract_json_object(raw) == '{"clinical_events": []}'


def test_parse_strips_newline_broken_rationale_without_changing_values() -> None:
    raw = (
        '{"clinical_events":[{"family":"diagnosis","anchor_text":"epilepsy",'
        '"evidence":"Diagnosis: epilepsy","event_state":{},"mentions":['
        '{"entity":"Diagnosis","text":"epilepsy","attributes":{"Negation":"Affirmed"}}'
        '],"confidence":"high","rationale": "broken value\n  }]}'
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert "json_dialect_repaired: stripped_non_scored_rationale" in errors
    assert record.clinical_events[0].rationale == ""
    assert record.clinical_events[0].mentions[0].text == "epilepsy"


def test_predict_deadline_returns_note_when_call_does_not_finish() -> None:
    class _HangingProgram:
        def __call__(self, prompt_input_json: str) -> str:
            del prompt_input_json
            time.sleep(2)
            return "done"

    started = time.perf_counter()
    prediction, note = structured_one_call._predict_with_deadline(
        _HangingProgram(),
        prompt_input_json="{}",
        timeout=1,
    )
    elapsed = time.perf_counter() - started

    assert prediction is None
    assert note == "invalid_json: produce_deadline_exceeded"
    assert elapsed < 1.5


def test_parse_broken_rationale_near_miss_finishes_quickly() -> None:
    raw = ('"rationale": "' + ("x" * 80) + "\n   y") * 2000

    started = time.perf_counter()
    record, errors = structured.parse_structured_events_json(raw)
    elapsed = time.perf_counter() - started

    assert record is None
    assert errors and str(errors[0]).startswith("invalid_json:")
    assert elapsed < 0.4
