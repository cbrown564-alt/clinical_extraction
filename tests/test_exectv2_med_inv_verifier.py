"""Tests for the ExECTv2 Prescription/Investigations verifier."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_med_inv_verifier as verifier,
)

_NOTE = (
    "Currently she is taking sodium valproate 500 mg twice a day. "
    "She should introduce lamotrigine at 25 mg every day, increasing to 75 mg bd. "
    "MRI 2016 showed left-sided gliosis. I will arrange an EEG."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_build_prompt_input_includes_dev140_residual_rules() -> None:
    payload = json.loads(
        verifier.build_prompt_input(
            _LETTER,
            [
                {
                    "entity": "Prescription",
                    "text": "lamotrigine 75mg bd",
                    "attributes": {"DrugName": "lamotrigine"},
                    "evidence": "increasing to 75 mg bd",
                }
            ],
        )
    )

    assert payload["prompt_version"].endswith("_v0.1")
    rules = " ".join(payload["clinical_rules"])
    assert "Return only Prescription and Investigations" in rules
    assert "titration targets are not current ordinary regimens" in rules
    assert "planned future investigations" in rules
    assert "modality-only Investigations" in rules
    assert "gliosis" in rules
    assert payload["draft_mentions"][0]["text"] == "lamotrigine 75mg bd"
    titration_example = next(
        example
        for example in payload["worked_examples"]
        if "target dose" in example["note_fragment"]
    )
    assert titration_example["correct"][0]["text"] == "sodium valproate 500 mg twice a day"
    planned_example = next(
        example
        for example in payload["worked_examples"]
        if "I will arrange" in example["note_fragment"]
    )
    assert planned_example["correct"] == []


def test_draft_mentions_by_letter_filters_target_entities() -> None:
    drafts = verifier.draft_mentions_by_letter(
        [
            {
                "letter_id": "TEST001",
                "predicted_mentions": [
                    {"entity": "Prescription", "text": "lamotrigine", "attributes": {}},
                    {"entity": "Investigations", "text": "MRI", "attributes": {}},
                    {"entity": "Diagnosis", "text": "epilepsy", "attributes": {}},
                ],
            }
        ]
    )

    assert [mention["entity"] for mention in drafts["TEST001"]] == [
        "Prescription",
        "Investigations",
    ]


def test_parse_and_to_predicted_letter_preserve_entity_and_strip_projection_attrs() -> None:
    raw = json.dumps(
        {
            "mentions": [
                {
                    "entity": "Prescription",
                    "text": "sodium valproate 500 mg twice a day",
                    "attributes": {
                        "DrugName": "sodium valproate",
                        "DrugDose": 500,
                        "DoseUnit": "mg",
                        "Frequency": 2,
                        "CUI": "WRONG",
                    },
                    "evidence": "sodium valproate 500 mg twice a day",
                },
                {
                    "entity": "Investigations",
                    "text": "MRI 2016 showed left-sided gliosis",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Abnormal"},
                    "evidence": "MRI 2016 showed left-sided gliosis",
                },
            ]
        }
    )

    extraction, errors = verifier.parse_med_inv_json(raw)
    assert extraction is not None
    assert any("coerced_attribute_value" in error for error in errors)
    pred, warnings = verifier.to_predicted_letter(
        "TEST001",
        extraction.mentions,
        note_text=_NOTE,
    )

    assert [mention.entity for mention in pred.mentions] == [
        "Prescription",
        "Investigations",
    ]
    rx = pred.mentions[0]
    assert rx.attributes["DrugDose"] == "500"
    assert rx.attributes["Frequency"] == "2"
    assert "CUI" in rx.attributes
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_summarize_rows_reports_med_inv_clinical_recovery() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 2,
            "n_mentions_raw": 2,
            "n_mentions_scored": 2,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "entity": "Prescription",
                    "text": "sodium valproate 500 mg twice a day",
                    "attributes": {
                        "DrugName": "sodium valproate",
                        "DrugDose": "500",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                },
                {
                    "entity": "Investigations",
                    "text": "MRI 2016 showed left-sided gliosis",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Abnormal"},
                },
            ],
            "predicted_mentions": [
                {
                    "entity": "Prescription",
                    "text": "sodium valproate 500 mg twice a day",
                    "attributes": {
                        "DrugName": "sodium valproate",
                        "DrugDose": "500",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                    "evidence": "sodium valproate 500 mg twice a day",
                },
                {
                    "entity": "Investigations",
                    "text": "MRI 2016 showed left-sided gliosis",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Abnormal"},
                    "evidence": "MRI 2016 showed left-sided gliosis",
                },
            ],
        }
    ]

    summary = verifier.summarize_rows(rows)

    assert summary["clinical_recovery"]["Prescription"]["f1"] == 1.0
    assert summary["clinical_recovery"]["Investigations"]["f1"] == 1.0
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
