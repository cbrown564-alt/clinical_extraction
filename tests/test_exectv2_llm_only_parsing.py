"""Invariant-focused tests for exectv2 llm only parsing."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)

_NOTE = (
    "She has focal epilepsy with 2 focal seizures per month. "
    "Current treatment is lamotrigine 200 mg twice daily. "
    "MRI brain was normal; sleep-deprived EEG showed sharp waves."
)

_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_candidate_evidence_ledger_types_family_lanes() -> None:
    note = (
        "Current medication lamotrigine 200 mg twice daily. "
        "I will request a repeat MRI scan next year. "
        "MRI 2016 showed left hippocampal sclerosis. "
        "EEG did show temporal slowing. "
        "Diagnosis: focal epilepsy. "
        "Family history includes epilepsy. "
        "He has not had any events which resemble absences, myoclonus or focal seizures. "
        "She has not had any further seizures since last clinic."
    )
    letter = ExectLetter(letter_id="TEST002", note_text=note)

    ledger = structured.candidate_evidence_ledger_for_letter(letter)

    assert any(
        item["family"] == "medication" and item["lane_hint"] == "current_regimen" for item in ledger
    )
    assert any(
        item["family"] == "investigation" and item["lane_hint"] == "planned_investigation"
        for item in ledger
    )
    assert any(
        item["family"] == "investigation"
        and item["lane_hint"] == "performed_investigation"
        and item["anchor_hint"] == "EEG"
        for item in ledger
    )
    assert any(
        item["family"] == "diagnosis" and item["lane_hint"] == "diagnosis_assertion"
        for item in ledger
    )
    assert any(
        item["family"] == "diagnosis" and item["lane_hint"] == "diagnosis_context_only"
        for item in ledger
    )
    assert any(
        item["family"] == "diagnosis" and item["lane_hint"] == "symptom_or_nonepileptic"
        for item in ledger
    )
    assert any(
        item["family"] == "seizure_frequency" and item["lane_hint"] == "reject" for item in ledger
    )
    assert any(
        item["family"] == "seizure_frequency" and item["lane_hint"] == "seizure_free_anchor"
        for item in ledger
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


def test_parse_structured_events_repairs_python_literal_dialect() -> None:
    raw = (
        "{'clinical_events': [{'family': 'diagnosis', 'anchor_text': 'epilepsy', "
        "'evidence': 'Diagnosis: epilepsy', 'event_state': {'certainty': 5}, "
        "'mentions': [{'entity': 'Diagnosis', 'text': 'epilepsy', "
        "'attributes': {'DiagCategory': 'Epilepsy', 'Certainty': 5, "
        "'Negation': 'Affirmed'}}], 'confidence': 'high', "
        "'rationale': 'Diagnosis stated.'}]}"
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert record.clinical_events[0].mentions[0].attributes["Certainty"] == "5"
    assert "json_dialect_repaired: python_literal" in errors


def test_parse_structured_events_repairs_anchor_key_typo_without_changing_value() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "medication",
                    "anchor:s_text": "Clobazam 10 mg",
                    "evidence": "Clobazam 10 mg bd",
                    "mentions": [],
                    "confidence": "high",
                }
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert record.clinical_events[0].anchor_text == "Clobazam 10 mg"
    assert "schema_repaired: anchor:s_text_to_anchor_text" in errors


def test_parse_structured_events_repairs_missing_mention_object_close() -> None:
    raw = """{
      "clinical_events": [{
        "family": "diagnosis",
        "anchor_text": "focal seizures",
        "evidence": "focal seizures last month",
        "mentions": [{
          "entity": "Diagnosis",
          "text": "focal seizures",
          "attributes": {"DiagCategory": "MultipleSeizures"},
          {"entity": "SeizureFrequency", "text": "focal seizures", "attributes": {}}
        }],
        "confidence": "high"
      }]
    }"""

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert [mention.entity for mention in record.clinical_events[0].mentions] == [
        "Diagnosis",
        "SeizureFrequency",
    ]
    assert "json_dialect_repaired: missing_array_object_close" in errors


def test_parse_structured_events_drops_no_mention_reject_events() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "reject",
                    "anchor_text": "limb shaking",
                    "evidence": "limb shaking with retained consciousness",
                    "mentions": [],
                    "confidence": "low",
                    "rationale": "The event is explicitly rejected as non-epileptic.",
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
    assert "dropped_no_mention_reject_event: event[0]" in errors


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


def test_parse_structured_events_strips_unclosed_non_scored_rationale() -> None:
    raw = """
{
  "clinical_events": [
    {
      "family": "diagnosis",
      "anchor_text": "epilepsy",
      "evidence": "Diagnosis: epilepsy",
      "event_state": {"Certainty": "5", "DiagCategory": "Epilepsy"},
      "mentions": [
        {
          "entity": "Diagnosis",
          "text": "epilepsy",
          "attributes": {"Certainty": "5", "DiagCategory": "Epilepsy"}
        }
      ],
      "confidence": "high",
      "rationale": "I will reason through several alternatives.
    },
    {
      "family": "investigation",
      "anchor_text": "MRI",
      "evidence": "MRI 2011 Normal",
      "event_state": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
      "mentions": [
        {
          "entity": "Investigations",
          "text": "MRI",
          "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"}
        }
      ],
      "confidence": "high",
      "rationale": "MRI result stated."
    }
  ]
}
"""

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert [event.family for event in record.clinical_events] == [
        "diagnosis",
        "investigation",
    ]
    assert record.clinical_events[0].rationale == ""
    assert "json_dialect_repaired: stripped_non_scored_rationale" in errors


def test_parse_structured_events_accepts_top_level_event_array() -> None:
    raw = json.dumps(
        [
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
            }
        ]
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert record.clinical_events[0].anchor_text == "epilepsy"
    assert not any(error.startswith("schema_validation_error") for error in errors)


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


def test_parse_structured_events_drops_malformed_nested_mentions() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "investigation",
                    "anchor_text": "EEG recording",
                    "evidence": "confirmed with an EEG recording",
                    "mentions": [
                        {
                            "entity": INVESTIGATIONS.name,
                            "text": "EEG recording",
                            "attributes": {
                                "EEG_Performed": "Yes",
                                "EEG_Results": "Abnormal",
                            },
                        },
                        {"attributes": {"CUI": "UMLS CUI not available in text"}},
                        "not a mention object",
                    ],
                    "confidence": "high",
                    "rationale": "EEG recording is stated.",
                }
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)

    assert record is not None
    assert len(record.clinical_events[0].mentions) == 1
    assert record.clinical_events[0].mentions[0].entity == INVESTIGATIONS.name
    assert any("missing=entity,text" in error for error in errors)
    assert any("not_object" in error for error in errors)
    assert not any(error.startswith("schema_validation_error") for error in errors)
