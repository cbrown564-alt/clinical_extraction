"""Tests for the ExECTv2 Investigations verifier."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_investigations_verifier as verifier,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
)

_NOTE = (
    "MRI 2016 showed left-sided gliosis. EEG was normal. "
    "I will arrange a CT scan."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_build_prompt_input_includes_investigation_residual_rules() -> None:
    payload = json.loads(
        verifier.build_prompt_input(
            _LETTER,
            [{"text": "CT scan", "attributes": {"CT_Performed": "Yes"}}],
        )
    )

    assert payload["prompt_version"].endswith("_v0.1")
    assert payload["draft_investigations_mentions"][0]["text"] == "CT scan"
    rules = " ".join(payload["clinical_rules"])
    assert "Return only Investigations" in rules
    assert "Omit planned" in rules
    assert "modality-only mentions" in rules
    assert "gliosis" in rules
    assert "VideoTelemetry" in rules
    planned_example = next(
        example
        for example in payload["worked_examples"]
        if "I will arrange" in example["note_fragment"]
    )
    assert planned_example["correct"] == []


def test_draft_mentions_by_letter_filters_investigations() -> None:
    drafts = verifier.draft_mentions_by_letter(
        [
            {
                "letter_id": "TEST001",
                "predicted_mentions": [
                    {"entity": "Investigations", "text": "MRI", "attributes": {}},
                    {"entity": "Prescription", "text": "lamotrigine", "attributes": {}},
                ],
            }
        ]
    )

    assert drafts == {
        "TEST001": [
            {
                "text": "MRI",
                "attributes": {},
                "evidence": "",
                "confidence": "",
                "rationale": "",
            }
        ]
    }


def test_to_predicted_letter_strips_projection_attrs() -> None:
    pred, warnings = verifier.to_predicted_letter(
        "TEST001",
        [
            MentionRecord(
                text="MRI 2016 showed left-sided gliosis",
                attributes={
                    "MRI_Performed": "Yes",
                    "MRI_Results": "Abnormal",
                    "CUI": "WRONG",
                },
                evidence="MRI 2016 showed left-sided gliosis",
                confidence="high",
                rationale="Gliosis is abnormal.",
            )
        ],
        note_text=_NOTE,
    )

    assert pred.mentions[0].entity == "Investigations"
    assert pred.mentions[0].attributes["MRI_Results"] == "Abnormal"
    assert "CUI" in pred.mentions[0].attributes
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_summarize_rows_reports_investigations_clinical_recovery() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 1,
            "n_mentions_raw": 1,
            "n_mentions_scored": 1,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "text": "MRI 2016 showed left-sided gliosis",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Abnormal"},
                }
            ],
            "predicted_mentions": [
                {
                    "text": "MRI 2016 showed left-sided gliosis",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Abnormal"},
                    "evidence": "MRI 2016 showed left-sided gliosis",
                }
            ],
        }
    ]

    summary = verifier.summarize_rows(rows)

    assert summary["clinical_recovery"]["investigations"]["f1"] == 1.0
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
