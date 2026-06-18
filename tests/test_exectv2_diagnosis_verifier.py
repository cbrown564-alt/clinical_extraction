"""Tests for the ExECTv2 Diagnosis verifier."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_diagnosis_verifier as verifier,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
)

_NOTE = (
    "Diagnosis: possible JME. She has myoclonic jerks but no epileptic attack. "
    "Previous diagnosis was focal epilepsy."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_build_prompt_input_includes_draft_and_v05_diagnosis_rules() -> None:
    payload = json.loads(
        verifier.build_prompt_input(
            _LETTER,
            [
                {
                    "text": "possible JME",
                    "attributes": {"Certainty": "5"},
                    "evidence": "Diagnosis: possible JME",
                }
            ],
        )
    )

    assert payload["prompt_version"] == verifier.PROMPT_VERSION
    assert payload["prompt_version"].endswith("_v0.2")
    assert payload["draft_diagnosis_mentions"][0]["text"] == "possible JME"
    rules = " ".join(payload["clinical_rules"])
    assert "Diagnosis text may be a normalized core clinical concept" in rules
    assert "Render only the core clinical concept span" in rules
    assert "Do not emit CUI or CUIPhrase" in rules
    assert "'epilepsy - probable focal' -> 'focal epilepsy'" in rules
    assert "'generalised tonic clonic seizures' -> 'tonic clonic seizures'" in rules
    assert "Never write 'tonic chronic'" in rules
    assert "Never use attribute labels" in rules
    assert "myoclonic jerks" in rules
    focal_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: epilepsy - probable focal."
    )
    assert focal_example["correct"][0]["text"] == "focal epilepsy"
    jme_example = next(
        example
        for example in payload["worked_examples"]
        if example["note_fragment"] == "Diagnosis: possible JME."
    )
    assert jme_example["correct"][0]["text"] == "JME"
    assert jme_example["correct"][0]["attributes"]["Certainty"] == "3"


def test_draft_mentions_by_letter_filters_diagnosis_mentions() -> None:
    drafts = verifier.draft_mentions_by_letter(
        [
            {
                "letter_id": "TEST001",
                "predicted_mentions": [
                    {"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {}},
                    {"entity": "Prescription", "text": "lamotrigine", "attributes": {}},
                ],
            }
        ]
    )

    assert drafts == {
        "TEST001": [
            {
                "text": "focal epilepsy",
                "attributes": {},
                "evidence": "",
                "confidence": "",
                "rationale": "",
            }
        ]
    }


def test_to_predicted_letter_strips_model_supplied_projection_attrs() -> None:
    pred, warnings = verifier.to_predicted_letter(
        "TEST001",
        [
            MentionRecord(
                text="JME",
                attributes={
                    "CUI": "WRONG",
                    "CUIPhrase": "wrong",
                    "DiagCategory": "Epilepsy",
                    "Certainty": "3",
                    "Negation": "Affirmed",
                },
                evidence="Diagnosis: possible JME",
                confidence="high",
                rationale="Possible JME.",
            )
        ],
        note_text=_NOTE,
    )

    assert pred.mentions[0].text == "JME"
    assert pred.mentions[0].attributes["CUI"] == "C0270853"
    assert pred.mentions[0].attributes["CUIPhrase"] == "juvenile myoclonic epilepsy"
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_summarize_rows_reports_diagnosis_clinical_recovery() -> None:
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
                    "text": "jme",
                    "attributes": {"Certainty": "3", "Negation": "Affirmed"},
                }
            ],
            "predicted_mentions": [
                {
                    "text": "JME",
                    "attributes": {"Certainty": "3", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: possible JME",
                }
            ],
        }
    ]

    summary = verifier.summarize_rows(rows)

    assert summary["clinical_recovery"]["diagnosis"]["f1"] == 1.0
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
    assert summary["n_draft_mentions"] == 1


def test_write_report_includes_diagnosis_headline(tmp_path) -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 0,
            "n_mentions_raw": 0,
            "n_mentions_scored": 0,
            "n_evidence_invalid": 0,
            "gold_mentions": [],
            "predicted_mentions": [],
        }
    ]
    path = tmp_path / "report.md"

    verifier.write_report(
        rows,
        {
            "prompt_version": verifier.PROMPT_VERSION,
            "pipeline_family": verifier.PIPELINE_FAMILY,
            "split": "dev",
            "model": "test-model",
            "mode": "prompt-only",
        },
        path,
        jsonl_path=tmp_path / "rows.jsonl",
    )

    text = path.read_text(encoding="utf-8")
    assert "## Diagnosis Clinical-Recovery Headline" in text
    assert "Draft Diagnosis mentions" in text
