from __future__ import annotations

import json

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.parsing import (  # noqa: E501
    parse_structured_events_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events
from clinical_extraction_local import ClinicalExtractor, ModelResponse


class RawModel:
    def __init__(self, raw: str) -> None:
        self.raw = raw

    def complete_json(self, **_: object) -> ModelResponse:
        return ModelResponse(content=self.raw, requested_model="fixture-model")


GAN_FIXTURES = [
    (
        "Two seizures per month.",
        "frequency_rate",
        "two seizures per month",
        "frequency",
        "2 per month",
    ),
    (
        "Seizures continue but the frequency is unknown.",
        "unknown_frequency",
        "frequency is unknown",
        "unknown",
        "unknown",
    ),
    (
        "There is no seizure frequency reference in this synthetic note.",
        "no_reference",
        "no seizure frequency reference",
        "no_reference",
        "no seizure frequency reference",
    ),
    (
        "The patient has been seizure free for 6 months.",
        "seizure_free",
        "seizure free for 6 months",
        "seizure_free",
        "seizure free for 6 month",
    ),
    (
        "The patient has 2 to 3 seizures per week.",
        "frequency_rate",
        "2 to 3 seizures per week",
        "frequency",
        "2 to 3 per week",
    ),
]


@pytest.mark.parametrize("note,kind,evidence,final_kind,label", GAN_FIXTURES)
def test_frequency_handoff_matches_selected_parser_on_five_synthetic_fixtures(
    note: str, kind: str, evidence: str, final_kind: str, label: str
) -> None:
    raw = json.dumps(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": kind,
                    "raw_value": evidence,
                    "applies_to": "seizures",
                    "time_window": "current",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": evidence,
                    "notes": None,
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": final_kind,
                "final_label": label,
                "evidence": evidence,
                "confidence": "high",
                "rationale": "Synthetic fixture selection.",
            },
        }
    )
    expected, _, errors, expected_trace = hybrid_structured_events.parse_structured_json_with_trace(
        raw, note_text=note
    )
    assert expected is not None and not any(error.startswith("invalid_") for error in errors)
    output = ClinicalExtractor(RawModel(raw)).run_workflow(
        "seizure_frequency", note_id="synthetic", text=note
    )
    assert output.trace["raw_model_response"] == raw
    assert output.result["value"] == (
        expected_trace["deterministic_semantic"]["after_label"]
        or expected.selection.final_label
    )
    assert output.result["evidence"] == expected.selection.evidence


EXECT_DIAGNOSIS_FIXTURES = [
    "focal epilepsy",
    "generalized epilepsy",
    "temporal lobe epilepsy",
    "drug-resistant epilepsy",
    "childhood absence epilepsy",
]


@pytest.mark.parametrize("diagnosis", EXECT_DIAGNOSIS_FIXTURES)
def test_findings_handoff_matches_selected_parse_and_assembly_on_five_fixtures(
    diagnosis: str,
) -> None:
    note = f"Synthetic assessment: {diagnosis}."
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "anchor_text": diagnosis,
                    "evidence": diagnosis,
                    "event_state": {"assertion": "present"},
                    "mentions": [
                        {
                            "entity": "Diagnosis",
                            "text": diagnosis,
                            "attributes": {"assertion": "present"},
                        }
                    ],
                    "confidence": "high",
                    "rationale": "",
                }
            ]
        }
    )
    parsed, errors = parse_structured_events_json(raw)
    assert parsed is not None and not errors
    output = ClinicalExtractor(RawModel(raw)).run_workflow(
        "clinical_findings", note_id="synthetic", text=note
    )
    assert output.trace["raw_model_response"] == raw
    expected_events = [event.model_dump() for event in parsed.clinical_events]
    assert output.trace["structured_events"] == expected_events
    assert output.result["diagnoses"][0]["evidence"] == diagnosis
    assert output.trace["assembly"]["predicted_mentions"][0]["evidence"] == diagnosis
