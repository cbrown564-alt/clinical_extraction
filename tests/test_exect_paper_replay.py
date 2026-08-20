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
                    "evidence": "Diagnosis: focal epilepsy",
                    "fact": "focal epilepsy",
                    "attributes": {},
                },
                {
                    "family": "investigation",
                    "evidence": "MRI brain normal",
                    "fact": "MRI",
                    "attributes": {},
                },
                {
                    "family": "medication",
                    "evidence": "Levetiracetam 500 mg twice daily",
                    "fact": "Levetiracetam",
                    "attributes": {"DoseUnit": "mg", "Frequency": "2"},
                },
                {
                    "family": "seizure_frequency",
                    "evidence": "She has two seizures per month",
                    "fact": "seizures",
                    "attributes": {"NumberOfSeizures": "2", "TimePeriod": "Month"},
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
