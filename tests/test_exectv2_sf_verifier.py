"""Tests for the ExECTv2 SeizureFrequency verifier."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_sf_verifier as verifier,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
)

_NOTE = (
    "Seizure type and frequency: several seizures since last clinic. "
    "She had 3-4 generalised tonic chronic seizures per week."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_build_prompt_input_includes_draft_and_v03_sf_rules() -> None:
    payload = json.loads(
        verifier.build_prompt_input(
            _LETTER,
            [
                {
                    "text": "generalised tonic chronic seizures",
                    "attributes": {"LowerNumberOfSeizures": "3"},
                    "evidence": "3-4 generalised tonic chronic seizures per week",
                }
            ],
        )
    )

    assert payload["prompt_version"] == verifier.PROMPT_VERSION
    assert payload["prompt_version"].endswith("_v0.3")
    assert payload["draft_seizure_frequency_mentions"][0]["text"] == (
        "generalised tonic chronic seizures"
    )
    rules = " ".join(payload["clinical_rules"])
    assert "source 'tonic chronic seizures'" in rules
    assert "Apply a named-seizure-frequency gate" in rules
    assert "For 'several' use NumberOfSeizures='3'" in rules
    assert "for 'a few' use NumberOfSeizures='2'" in rules
    assert "a few seizures per year" in rules
    assert "Do not deduplicate separately supported SF mentions" in rules
    assert "single focal seizure" in rules
    assert "generic episodes, dizzy spells, or aura descriptions" in rules
    assert "unlabelled 'episodes', 'events', 'blackouts'" in rules
    assert "last event X. Previous event Y" in rules
    assert "Never use 'unknown' as NumberOfSeizures" in rules
    assert "last had a seizure before this around a year ago" in rules
    assert "occasional jerks" in rules
    assert "completely under control" in rules
    assert "FrequencyChange='Infrequent'" in rules
    assert "teenage years" in rules
    typo_example = next(
        example
        for example in payload["worked_examples"]
        if "tonic chronic seizures" in example["note_fragment"]
    )
    assert typo_example["correct"][0]["text"] == "generalised tonic clonic seizures"
    single_event_example = next(
        example
        for example in payload["worked_examples"]
        if "single focal seizure" in example["note_fragment"]
    )
    assert single_event_example["correct"] == []
    episodes_example = next(
        example
        for example in payload["worked_examples"]
        if "episodes around twice a week" in example["note_fragment"]
    )
    assert episodes_example["correct"] == []
    teenage_example = next(
        example
        for example in payload["worked_examples"]
        if "teenage years" in example["note_fragment"]
    )
    assert teenage_example["correct"][0]["text"] == "seizures"
    assert teenage_example["correct"][0]["attributes"]["NumberOfSeizures"] == "0"
    previous_event_example = next(
        example
        for example in payload["worked_examples"]
        if "last had a seizure before this around a year ago" in example["note_fragment"]
    )
    assert len(previous_event_example["correct"]) == 1
    improvement_example = next(
        example
        for example in payload["worked_examples"]
        if "significant improvement since increasing" in example["note_fragment"]
    )
    assert improvement_example["correct"][0]["text"] == "seizures"
    assert improvement_example["correct"][0]["attributes"]["FrequencyChange"] == "Infrequent"


def test_draft_mentions_by_letter_filters_sf_mentions() -> None:
    drafts = verifier.draft_mentions_by_letter(
        [
            {
                "letter_id": "TEST001",
                "predicted_mentions": [
                    {"entity": "SeizureFrequency", "text": "seizures", "attributes": {}},
                    {"entity": "Diagnosis", "text": "focal epilepsy", "attributes": {}},
                ],
            }
        ]
    )

    assert drafts == {
        "TEST001": [
            {
                "text": "seizures",
                "attributes": {},
                "evidence": "",
                "confidence": "",
                "rationale": "",
            }
        ]
    }


def test_to_predicted_letter_strips_projection_attrs_and_projects_cui() -> None:
    pred, warnings = verifier.to_predicted_letter(
        "TEST001",
        [
            MentionRecord(
                text="generalised tonic clonic seizures",
                attributes={
                    "CUI": "WRONG",
                    "CUIPhrase": "wrong",
                    "LowerNumberOfSeizures": "3",
                    "UpperNumberOfSeizures": "4",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
                evidence="3-4 generalised tonic chronic seizures per week",
                confidence="high",
                rationale="Source typo is normalized.",
            )
        ],
        note_text=_NOTE,
    )

    assert pred.mentions[0].text == "generalised tonic clonic seizures"
    assert pred.mentions[0].attributes["CUI"] == "C0494475"
    assert pred.mentions[0].attributes["CUIPhrase"] == "generalised tonic clonic seizures"
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_summarize_rows_reports_sf_clinical_recovery() -> None:
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
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "CUI": "C0494475",
                        "CUIPhrase": "generalised-tonic-clonic-seizures",
                        "LowerNumberOfSeizures": "3",
                        "UpperNumberOfSeizures": "4",
                    },
                }
            ],
            "predicted_mentions": [
                {
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "CUI": "C0494475",
                        "CUIPhrase": "generalised-tonic-clonic-seizures",
                        "LowerNumberOfSeizures": "3",
                        "UpperNumberOfSeizures": "4",
                    },
                    "evidence": "3-4 generalised tonic chronic seizures per week",
                }
            ],
        }
    ]

    summary = verifier.summarize_rows(rows)

    assert summary["clinical_recovery"]["seizure_frequency"]["f1"] == 1.0
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
    assert summary["n_draft_mentions"] == 1


def test_write_report_includes_sf_headline(tmp_path) -> None:
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
    assert "## SeizureFrequency Clinical-Recovery Headline" in text
    assert "Draft SF mentions" in text
