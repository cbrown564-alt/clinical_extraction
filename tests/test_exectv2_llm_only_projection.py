"""Invariant-focused tests for exectv2 llm only projection."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts.run_exectv2_2call_model_swap import _v26_history_last_event_mentions

_NOTE = (
    "She has focal epilepsy with 2 focal seizures per month. "
    "Current treatment is lamotrigine 200 mg twice daily. "
    "MRI brain was normal; sleep-deprived EEG showed sharp waves."
)

_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_v26_last_event_history_is_promoted_to_seizure_free() -> None:
    row = {
        "prompt_version": structured.PROMPT_VERSION_V26,
        "structured_events": [
            {
                "family": "history",
                "event": "focal to bilateral convulsive seizures",
                "evidence": "Focal to bilateral convulsive seizures, last event 2015",
            },
            {
                "family": "history",
                "event": "focal seizures",
                "evidence": "No events resembling focal seizures",
            },
        ],
    }

    promoted = _v26_history_last_event_mentions(row)

    assert len(promoted) == 1
    assert promoted[0]["text"] == "focal to bilateral convulsive seizures"
    assert promoted[0]["attributes"] == {
        "NumberOfSeizures": "0",
        "TimeSince_or_TimeOfEvent": "Since",
        "YearDate": "2015",
    }


def test_flatten_events_preserves_cross_entity_renderings() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "seizure_frequency",
                    "anchor_text": "focal seizures",
                    "evidence": "focal epilepsy with 2 focal seizures per month",
                    "event_state": {"rate": "2 per 1 Month"},
                    "mentions": [
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "focal epilepsy",
                            "attributes": {
                                "DiagCategory": "Epilepsy",
                                "Certainty": "5",
                                "Negation": "Affirmed",
                            },
                        },
                        {
                            "entity": DIAGNOSIS.name,
                            "text": "focal seizures",
                            "attributes": {
                                "DiagCategory": "MultipleSeizures",
                                "Certainty": "5",
                                "Negation": "Affirmed",
                            },
                        },
                        {
                            "entity": SEIZURE_FREQUENCY.name,
                            "text": "focal seizures",
                            "attributes": {
                                "NumberOfSeizures": "2",
                                "NumberOfTimePeriods": "1",
                                "TimePeriod": "Month",
                            },
                        },
                    ],
                    "confidence": "high",
                    "rationale": "Diagnosis and rate are stated.",
                }
            ]
        }
    )
    record, errors = structured.parse_structured_events_json(raw)
    assert record is not None
    assert errors == []

    mentions = structured.flatten_events(record)

    assert [mention.entity for mention in mentions] == [
        DIAGNOSIS.name,
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
    ]
    assert all(
        mention.evidence == "focal epilepsy with 2 focal seizures per month" for mention in mentions
    )


def test_to_predicted_letter_gates_evidence_and_projects_cuis() -> None:
    mentions = [
        structured.MentionForEvidence(
            entity=DIAGNOSIS.name,
            text="focal epilepsy",
            attributes={
                "CUI": "WRONG",
                "CUIPhrase": "wrong phrase",
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "FrequencyChange": "Increased",
            },
            evidence="focal epilepsy with 2 focal seizures per month",
            confidence="high",
            rationale="Diagnosis stated.",
        ),
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="focal seizures",
            attributes={"NumberOfSeizures": "2", "DiagCategory": "Epilepsy"},
            evidence="focal epilepsy with 2 focal seizures per month",
            confidence="high",
            rationale="Frequency stated.",
        ),
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="focal seizures",
            attributes={"Negation": "Affirmed"},
            evidence="focal epilepsy with 2 focal seizures per month",
            confidence="high",
            rationale="No frequency-state attributes.",
        ),
        structured.MentionForEvidence(
            entity=INVESTIGATIONS.name,
            text="MRI",
            attributes={"MRI_Performed": "Yes"},
            evidence="MRI brain was normal",
            confidence="high",
            rationale="Duplicate modality-only rendering.",
        ),
        structured.MentionForEvidence(
            entity=INVESTIGATIONS.name,
            text="MRI brain",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
            evidence="MRI brain was normal",
            confidence="high",
            rationale="Result-bearing rendering.",
        ),
        structured.MentionForEvidence(
            entity="PatientHistory",
            text="focal seizures",
            attributes={},
            evidence="focal epilepsy with 2 focal seizures per month",
        ),
        structured.MentionForEvidence(
            entity=INVESTIGATIONS.name,
            text="EEG",
            attributes={"EEG_Performed": "Yes"},
            evidence="not in the note",
        ),
        structured.MentionForEvidence(
            entity=PRESCRIPTION.name,
            text="lamotrigine 200 mg twice daily",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "200",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence="Current treatment: lamotrigine 200 mg twice daily",
            confidence="high",
            rationale="Mention text itself is exact source evidence.",
        ),
        structured.MentionForEvidence(
            entity=DIAGNOSIS.name,
            text="focal seizures",
            attributes={
                "DiagCategory": "MultipleSeizures",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
            evidence="wrong wrapper focal seizures",
            confidence="high",
            rationale="Diagnosis mention text itself is exact source evidence.",
        ),
    ]

    letter, warnings = structured.to_predicted_letter("TEST001", mentions, note_text=_NOTE)

    assert [mention.entity for mention in letter.mentions] == [
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
        INVESTIGATIONS.name,
        PRESCRIPTION.name,
        DIAGNOSIS.name,
    ]
    diagnosis = letter.mentions[0]
    sf = letter.mentions[1]
    assert diagnosis.attributes["CUI"] == "C0014547"
    assert diagnosis.attributes["CUIPhrase"] == "focal epilepsy"
    assert "FrequencyChange" not in diagnosis.attributes
    assert sf.attributes["CUI"] == "C0751495"
    assert "DiagCategory" not in sf.attributes
    assert letter.mentions[2].text == "MRI brain"
    assert letter.mentions[3].evidence == "lamotrigine 200 mg twice daily"
    assert letter.mentions[4].evidence == "focal seizures"
    assert any("dropped_out_of_scope_entity" in warning for warning in warnings)
    assert any("dropped_evidence_not_substring" in warning for warning in warnings)
    assert any("repaired_evidence_from_mention_text" in warning for warning in warnings)
    assert any("Diagnosis: dropped_illegal_attribute" in warning for warning in warnings)
    assert any(
        "Diagnosis: dropped_model_supplied_projection_attribute" in warning for warning in warnings
    )
    assert any("dropped_no_frequency_state_rendering" in warning for warning in warnings)
    assert any("dropped_duplicate_modality_only_rendering" in warning for warning in warnings)


def test_summarize_rows_scores_only_key_entities() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_events_raw": 2,
            "n_mentions_raw": 4,
            "n_mentions_scored": 4,
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
                {
                    "entity": PRESCRIPTION.name,
                    "text": "lamotrigine 200 mg twice daily",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "200",
                        "DoseUnit": "mg",
                        "Frequency": "twice daily",
                    },
                },
                {
                    "entity": INVESTIGATIONS.name,
                    "text": "MRI",
                    "attributes": {"MRI_Performed": "Yes"},
                },
                {
                    "entity": "PatientHistory",
                    "text": "ignored",
                    "attributes": {},
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
                {
                    "entity": PRESCRIPTION.name,
                    "text": "lamotrigine 200 mg twice daily",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "200",
                        "DoseUnit": "mg",
                        "Frequency": "twice daily",
                    },
                },
                {
                    "entity": INVESTIGATIONS.name,
                    "text": "MRI",
                    "attributes": {"MRI_Performed": "Yes"},
                },
            ],
        }
    ]

    summary = structured.summarize_rows(rows)

    assert summary["scores"]["semantic"]["per_item"]["f1"] == 1.0
    assert set(summary["scores"]["semantic"]["per_entity"]) == set(structured.KEY_ENTITY_NAMES)
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
    assert set(summary["clinical_recovery"]["per_entity"]) == set(structured.KEY_ENTITY_NAMES)
    assert summary["clinical_recovery"]["per_entity"][PRESCRIPTION.name]["f1"] == 1.0
    assert summary["clinical_recovery"]["per_entity"][DIAGNOSIS.name]["f1"] == 1.0
    assert summary["clinical_recovery"]["per_entity"][SEIZURE_FREQUENCY.name]["f1"] == 1.0
    assert summary["clinical_recovery"]["per_entity"][INVESTIGATIONS.name]["f1"] == 1.0
    assert summary["n_events_raw"] == 2
    assert summary["diagnostic_ladder"]["source_near"]["overall"]["overlap"]["f1"] == 1.0


def test_write_report_includes_goal_and_diagnostic_ladder(tmp_path) -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_events_raw": 0,
            "n_mentions_raw": 0,
            "n_mentions_scored": 0,
            "n_evidence_invalid": 0,
            "gold_mentions": [],
            "predicted_mentions": [],
        }
    ]
    report_path = tmp_path / "report.md"

    structured.write_report(
        rows,
        {
            "prompt_version": structured.PROMPT_VERSION,
            "pipeline_family": structured.PIPELINE_FAMILY,
            "split": "dev",
            "model": "test-model",
            "mode": "prompt-only",
            "is_checkpoint": True,
            "total_letters": 140,
        },
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "CHECKPOINT ONLY: processed 1 / 140 letters" in text
    assert "Goal item F1" in text
    assert "## Key Clinical-Recovery Headlines" in text
    assert "## Diagnostic Scoring Ladder" in text


def test_v26_events_project_through_to_predicted_letter() -> None:
    note = (
        "Diagnosis: focal epilepsy. "
        "She has 2 focal seizures per month. "
        "Current medication: lamotrigine 100 mg in the morning and 200 mg in the evening. "
        "She previously tried levetiracetam. "
        "MRI brain was normal."
    )
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "clinical_family": "diagnosis",
                    "event": "focal epilepsy",
                    "evidence": "Diagnosis: focal epilepsy.",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                },
                {
                    "clinical_family": "seizure_frequency",
                    "event": "focal seizures",
                    "evidence": "She has 2 focal seizures per month.",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Month",
                    },
                },
                {
                    "clinical_family": "medication",
                    "event": "lamotrigine",
                    "evidence": (
                        "Current medication: lamotrigine 100 mg in the morning "
                        "and 200 mg in the evening."
                    ),
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "100",
                        "DoseUnit": "mg",
                        "Frequency": "1",
                        "Status": "current",
                    },
                },
                {
                    "clinical_family": "medication",
                    "event": "lamotrigine",
                    "evidence": (
                        "Current medication: lamotrigine 100 mg in the morning "
                        "and 200 mg in the evening."
                    ),
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "200",
                        "DoseUnit": "mg",
                        "Frequency": "1",
                        "Status": "current",
                    },
                },
                {
                    "clinical_family": "medication",
                    "event": "levetiracetam",
                    "evidence": "She previously tried levetiracetam.",
                    "attributes": {
                        "DrugName": "levetiracetam",
                        "Status": "past",
                    },
                },
                {
                    "clinical_family": "investigation",
                    "event": "MRI",
                    "evidence": "MRI brain was normal.",
                    "attributes": {
                        "MRI_Performed": "Yes",
                        "MRI_Results": "Normal",
                    },
                },
                {
                    "clinical_family": "history",
                    "event": "tried",
                    "evidence": "She previously tried levetiracetam.",
                    "attributes": {"Kind": "unclassified_event"},
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)
    assert record is not None
    assert not any(str(error).startswith("schema_validation_error:") for error in errors)

    mentions = structured.flatten_events(record)
    letter, warnings = structured.to_predicted_letter(
        "TEST001",
        mentions,
        note_text=note,
        prompt_version=structured.PROMPT_VERSION_V26,
    )

    assert [mention.entity for mention in letter.mentions] == [
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
        PRESCRIPTION.name,
        PRESCRIPTION.name,
        INVESTIGATIONS.name,
    ]
    assert [mention.text for mention in letter.mentions] == [
        "focal epilepsy",
        "focal seizures",
        "lamotrigine",
        "lamotrigine",
        "MRI",
    ]
    doses = [
        mention.attributes.get("DrugDose")
        for mention in letter.mentions
        if mention.entity == PRESCRIPTION.name
    ]
    assert doses == ["100", "200"]
    assert all("Status" not in mention.attributes for mention in letter.mentions)
    sf = next(mention for mention in letter.mentions if mention.entity == SEIZURE_FREQUENCY.name)
    assert sf.attributes["NumberOfSeizures"] == "2"
    assert sf.attributes["TimePeriod"] == "Month"
    investigation = next(
        mention for mention in letter.mentions if mention.entity == INVESTIGATIONS.name
    )
    assert investigation.attributes["MRI_Performed"] == "Yes"
    assert investigation.attributes["MRI_Results"] == "Normal"
    assert [item.kind for item in record.medication_history] == ["past_medication"]
    assert [item.span for item in record.medication_history] == ["levetiracetam"]
    assert [item.kind for item in record.patient_history] == ["unclassified_event"]
    assert not any("schema_validation_error" in warning for warning in warnings)
