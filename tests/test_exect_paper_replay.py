"""No-call reconstruction of ExECT paper replay rows from saved raw_output."""

from __future__ import annotations

import json

from clinical_extraction.paper.exect import hydrate_saved_exect_letter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter


def _letter() -> ExectLetter:
    return ExectLetter(
        letter_id="LLM-VERTICAL-1",
        note_text=(
            "Diagnosis: focal epilepsy. MRI brain normal. "
            "Levetiracetam 500 mg twice daily. She has two seizures per month."
        ),
    )


def _raw() -> str:
    return json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "anchor_text": "focal epilepsy",
                    "evidence": "Diagnosis: focal epilepsy",
                    "event_state": {},
                    "mentions": [
                        {"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {}}
                    ],
                    "confidence": "high",
                    "rationale": "The diagnosis is explicit.",
                },
                {
                    "family": "investigation",
                    "anchor_text": "MRI brain normal",
                    "evidence": "MRI brain normal",
                    "event_state": {},
                    "mentions": [{"entity": "Investigations", "text": "MRI", "attributes": {}}],
                    "confidence": "high",
                    "rationale": "The investigation is explicit.",
                },
                {
                    "family": "medication",
                    "anchor_text": "Levetiracetam 500 mg twice daily",
                    "evidence": "Levetiracetam 500 mg twice daily",
                    "event_state": {},
                    "mentions": [
                        {
                            "entity": "Prescription",
                            "text": "Levetiracetam",
                            "attributes": {"DoseUnit": "mg", "Frequency": "2"},
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The prescription is explicit.",
                },
                {
                    "family": "seizure_frequency",
                    "anchor_text": "seizures",
                    "evidence": "She has two seizures per month",
                    "event_state": {},
                    "mentions": [
                        {
                            "entity": "SeizureFrequency",
                            "text": "seizures",
                            "attributes": {
                                "NumberOfSeizures": "2",
                                "TimePeriod": "Month",
                            },
                        }
                    ],
                    "confidence": "high",
                    "rationale": "The frequency is explicit.",
                },
            ]
        }
    )


def test_hydrate_saved_exect_letter_rebuilds_hybrid_mentions() -> None:
    letter = hydrate_saved_exect_letter(
        _letter(),
        _raw(),
        model="openai/gpt-5.6-luna",
        lane="llm_with_rules",
    )

    entities = {item["entity"] for item in letter["predicted_mentions"]}
    assert letter["letter_id"] == "LLM-VERTICAL-1"
    assert "Diagnosis" in entities
    assert "Prescription" in entities
    assert letter["predicted_family_counts"]["Diagnosis"] >= 1


def test_hydrate_saved_exect_letter_keeps_raw_lane_separate() -> None:
    raw = hydrate_saved_exect_letter(
        _letter(),
        _raw(),
        model="openai/gpt-5.6-luna",
        lane="llm",
    )
    hybrid = hydrate_saved_exect_letter(
        _letter(),
        _raw(),
        model="openai/gpt-5.6-luna",
        lane="llm_with_rules",
    )

    assert raw["letter_id"] == hybrid["letter_id"]
    assert raw["predicted_mentions"]
    assert hybrid["predicted_mentions"]
