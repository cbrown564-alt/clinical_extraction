"""Tests for the ExECTv2 all-entity LLM-only extractor."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_all_entities,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
    parse_extraction_json,
    summarize_rows,
    to_predicted_letter,
    write_report,
)
from tests.helpers.prompt_hygiene import FORBIDDEN_PHRASES

_NOTE = (
    "She has focal epilepsy. Her EEG was abnormal. "
    "She has 2 focal seizures per month."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_all_entities_prompt_hygiene_and_registry_vocab() -> None:
    payload_str = llm_only_all_entities.build_prompt_input(_LETTER)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in payload_str]
    assert leaked == []

    payload = json.loads(payload_str)
    assert payload["prompt_version"] == llm_only_all_entities.PROMPT_VERSION
    assert set(payload["attribute_vocabulary"]) == set(ENTITY_REGISTRY)
    assert "DiagCategory" in payload["attribute_vocabulary"][DIAGNOSIS.name]
    assert "FrequencyChange" in payload["attribute_vocabulary"][SEIZURE_FREQUENCY.name]
    assert payload["text_target"][SEIZURE_FREQUENCY.name].startswith("Seizure-type anchor")
    assert "dose/frequency" in payload["text_target"]["Prescription"]


def test_all_entities_parse_keeps_entity_and_coerces_attribute_values() -> None:
    raw = json.dumps({
        "mentions": [
            {
                "entity": DIAGNOSIS.name,
                "text": "focal epilepsy",
                "attributes": {"DiagCategory": "Epilepsy", "Certainty": 5},
                "evidence": "focal epilepsy",
                "confidence": "high",
                "rationale": "Direct diagnosis.",
            }
        ]
    })
    record, errors = parse_extraction_json(raw)

    assert record is not None
    assert record.mentions[0].entity == DIAGNOSIS.name
    assert record.mentions[0].attributes["Certainty"] == "5"
    assert any("coerced_attribute_value" in error for error in errors)


def test_to_predicted_letter_repairs_attributes_per_mentions_entity() -> None:
    mentions = [
        MentionRecord(
            entity=DIAGNOSIS.name,
            text="focal epilepsy",
            attributes={
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "FrequencyChange": "Increased",
            },
            evidence="focal epilepsy",
            confidence="high",
            rationale="Direct diagnosis.",
        ),
        MentionRecord(
            entity=SEIZURE_FREQUENCY.name,
            text="focal seizures",
            attributes={"NumberOfSeizures": "2", "DiagCategory": "Epilepsy"},
            evidence="2 focal seizures per month",
            confidence="high",
            rationale="Frequency directly stated.",
        ),
    ]

    letter, warnings = to_predicted_letter("TEST001", mentions, note_text=_NOTE)

    assert len(letter.mentions) == 2
    diagnosis = next(m for m in letter.mentions if m.entity == DIAGNOSIS.name)
    sf = next(m for m in letter.mentions if m.entity == SEIZURE_FREQUENCY.name)
    assert diagnosis.attributes == {
        "DiagCategory": "Epilepsy",
        "Certainty": "5",
        "CUI": "C0014547",
        "CUIPhrase": "focal epilepsy",
    }
    assert sf.attributes == {
        "NumberOfSeizures": "2",
        "CUI": "C0751495",
        "CUIPhrase": "focal seizures",
    }
    assert letter.diagnostics["cui_projected_mentions"] == 2
    assert any("Diagnosis: dropped_illegal_attribute" in warning for warning in warnings)
    assert not any(
        "DiagCategory" in warning and "SeizureFrequency" in warning
        for warning in warnings
    )


def test_to_predicted_letter_canonicalizes_format_only_attributes() -> None:
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="lamotrigine",
            attributes={"DrugName": "Lamotrigine", "DoseUnit": "MG"},
            evidence="lamotrigine",
            confidence="high",
            rationale="Medication stated.",
        )
    ]

    letter, warnings = to_predicted_letter("TEST001", mentions, note_text="Takes lamotrigine.")

    assert letter.mentions[0].attributes == {
        "DrugName": "lamotrigine",
        "DoseUnit": "mg",
        "CUI": "C0064636",
        "CUIPhrase": "lamotrigine",
    }
    assert any("normalized_attribute_value" in warning for warning in warnings)


def test_to_predicted_letter_drops_unknown_entity_and_bad_evidence() -> None:
    mentions = [
        MentionRecord(
            entity="UnknownThing",
            text="focal epilepsy",
            attributes={},
            evidence="focal epilepsy",
        ),
        MentionRecord(
            entity=DIAGNOSIS.name,
            text="ghost diagnosis",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="not in the note",
        ),
    ]

    letter, warnings = to_predicted_letter("TEST001", mentions, note_text=_NOTE)

    assert letter.mentions == ()
    assert any("dropped_unknown_entity" in warning for warning in warnings)
    assert any("dropped_evidence_not_substring" in warning for warning in warnings)


def test_summarize_rows_scores_mixed_entity_rows() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_mentions_raw": 2,
            "n_mentions_scored": 2,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "entity": DIAGNOSIS.name,
                    "text": "focal epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                },
                {
                    "entity": SEIZURE_FREQUENCY.name,
                    "text": "focal seizures",
                    "attributes": {"NumberOfSeizures": "2"},
                },
            ],
            "predicted_mentions": [
                {
                    "entity": DIAGNOSIS.name,
                    "text": "focal epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                },
                {
                    "entity": SEIZURE_FREQUENCY.name,
                    "text": "focal seizures",
                    "attributes": {"NumberOfSeizures": "2"},
                },
            ],
        }
    ]

    summary = summarize_rows(rows)

    assert summary["scores"]["semantic"]["per_item"]["tp"] == 2
    assert summary["scores"]["semantic"]["per_item"]["f1"] == 1.0
    assert summary["scores"]["semantic"]["per_entity"][DIAGNOSIS.name]["per_item"]["f1"] == 1.0
    sf_semantic = summary["scores"]["semantic"]["per_entity"][SEIZURE_FREQUENCY.name]
    assert sf_semantic["per_item"]["f1"] == 1.0
    assert "source_near" in summary["diagnostic_ladder"]


def test_write_report_marks_checkpoints_and_includes_diagnostic_ladder(tmp_path) -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_mentions_raw": 1,
            "n_mentions_scored": 1,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "entity": SEIZURE_FREQUENCY.name,
                    "text": "focal seizures",
                    "attributes": {"NumberOfSeizures": "2"},
                },
            ],
            "predicted_mentions": [
                {
                    "entity": SEIZURE_FREQUENCY.name,
                    "text": "2 focal seizures per month",
                    "attributes": {"NumberOfSeizures": "3"},
                },
            ],
        }
    ]
    report_path = tmp_path / "report.md"

    write_report(
        rows,
        {
            "prompt_version": llm_only_all_entities.PROMPT_VERSION,
            "split": "dev",
            "model": "test-model",
            "mode": "live",
            "is_checkpoint": True,
            "total_letters": 200,
        },
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "CHECKPOINT ONLY: processed 1 / 200 letters" in text
    assert "## Diagnostic Scoring Ladder" in text
    assert "source_near" in text
