"""Tests for the ExECTv2 Diagnosis candidate acceptance gate."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_acceptance_gate as gate,
)

_NOTE = (
    "Diagnosis: focal epilepsy. "
    "Seizure type and frequency: generalised tonic clonic seizures monthly."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_build_candidate_pool_merges_exact_duplicates_and_assigns_family() -> None:
    candidates = gate.build_candidate_pool(
        verifier_mentions=[
            {
                "text": "focal epilepsy",
                "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                "evidence": "Diagnosis: focal epilepsy",
            }
        ],
        decomposer_mentions=[
            {
                "text": "focal epilepsy",
                "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                "evidence": "Diagnosis: focal epilepsy",
            },
            {
                "text": "tonic clonic seizures",
                "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                "evidence": "generalised tonic clonic seizures",
            },
        ],
    )

    assert [candidate["candidate_id"] for candidate in candidates] == ["C0", "C1"]
    assert candidates[0]["sources"] == ["decomposer", "verifier"]
    assert candidates[0]["family"] == "focal_epilepsy_family"
    assert candidates[1]["family"] == "tonic_clonic_family"


def test_build_prompt_input_exposes_decision_schema_and_rules() -> None:
    payload = json.loads(
        gate.build_prompt_input(
            _LETTER,
            candidates=[
                {
                    "candidate_id": "C0",
                    "text": "epilepsy",
                    "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: focal epilepsy",
                    "family": "generic_epilepsy",
                    "sources": ["decomposer"],
                }
            ],
        )
    )

    assert payload["prompt_version"] == gate.PROMPT_VERSION
    assert payload["prompt_version"].endswith("_v0.1")
    assert payload["candidate_mentions"][0]["candidate_id"] == "C0"
    assert payload["output_schema"]["decisions"][0]["decision"] == "accept | reject"
    rules = " ".join(payload["acceptance_rules"])
    assert "one decision for every candidate_id" in rules
    assert "frequency-only seizure type" in rules
    assert "Do not invent new Diagnosis mentions" in rules


def test_parse_decisions_requires_known_shape() -> None:
    decisions, errors = gate.parse_decision_json(
        '{"decisions":[{"candidate_id":"C0","decision":"accept","reason_code":"direct_assertion"}]}'
    )

    assert errors == []
    assert decisions == {"C0": "accept"}


def test_to_predicted_letter_renders_only_accepted_candidates() -> None:
    candidates = [
        {
            "candidate_id": "C0",
            "text": "focal epilepsy",
            "attributes": {"Certainty": "5", "Negation": "Affirmed"},
            "evidence": "Diagnosis: focal epilepsy",
            "family": "focal_epilepsy_family",
            "sources": ["verifier"],
        },
        {
            "candidate_id": "C1",
            "text": "tonic clonic seizures",
            "attributes": {"Certainty": "5", "Negation": "Affirmed"},
            "evidence": "generalised tonic clonic seizures",
            "family": "tonic_clonic_family",
            "sources": ["decomposer"],
        },
    ]

    pred, warnings = gate.to_predicted_letter(
        "TEST001",
        candidates,
        accepted_ids={"C0"},
        note_text=_NOTE,
    )

    assert warnings == []
    assert [mention.text for mention in pred.mentions] == ["focal epilepsy"]
    assert pred.mentions[0].attributes["CUI"]
    assert pred.mentions[0].component_owner == gate.COMPONENT_OWNER


def test_summarize_rows_reports_gate_counts() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_candidates": 2,
            "n_accepted": 1,
            "n_mentions_scored": 1,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                }
            ],
            "predicted_mentions": [
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: focal epilepsy",
                }
            ],
        }
    ]

    summary = gate.summarize_rows(rows)

    assert summary["clinical_recovery"]["diagnosis"]["f1"] == 1.0
    assert summary["n_candidates"] == 2
    assert summary["n_accepted"] == 1
