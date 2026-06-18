"""Tests for the ExECTv2 family-conditioned event-ledger extractor."""

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
    llm_family_conditioned_event_ledger as ledger,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from tests.test_exectv2_llm_only_sf import FORBIDDEN_PHRASES

_NOTE = (
    "Diagnosis: focal epilepsy. "
    "Current treatment is lamotrigine 100 mg twice daily. "
    "She has focal seizures every month. "
    "MRI brain was normal and sleep-deprived EEG showed sharp waves."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_prompt_is_one_schema_conditioned_by_target_family() -> None:
    payloads = {
        entity: json.loads(ledger.build_prompt_input(_LETTER, entity))
        for entity in (
            PRESCRIPTION.name,
            DIAGNOSIS.name,
            SEIZURE_FREQUENCY.name,
            INVESTIGATIONS.name,
        )
    }

    schema_keys = {
        tuple(payload["output_schema"]["clinical_events"][0].keys())
        for payload in payloads.values()
    }
    assert len(schema_keys) == 1

    for entity, payload in payloads.items():
        leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in json.dumps(payload)]
        assert leaked == []
        assert payload["prompt_version"] == ledger.PROMPT_VERSION
        assert payload["target_family"] == entity
        assert set(payload["attribute_vocabulary"]) == {entity}
        assert payload["output_schema"]["clinical_events"][0]["family"] == (
            ledger.ENTITY_TO_EVENT_FAMILY[entity]
        )
        assert payload["output_schema"]["clinical_events"][0]["mentions"][0]["entity"] == entity
        assert set(payload["event_lane_guide"]) == {ledger.ENTITY_TO_EVENT_FAMILY[entity]}
        assert all(
            row["family"] == ledger.ENTITY_TO_EVENT_FAMILY[entity]
            for row in payload["candidate_evidence_ledger"]
        )
        assert any(
            rule.startswith(f"Return only {entity} mentions")
            for rule in payload["clinical_rules"]
        )

    assert "DrugName" in payloads[PRESCRIPTION.name]["attribute_vocabulary"][PRESCRIPTION.name]
    assert "Certainty" in payloads[DIAGNOSIS.name]["attribute_vocabulary"][DIAGNOSIS.name]
    assert (
        "NumberOfSeizures"
        in payloads[SEIZURE_FREQUENCY.name]["attribute_vocabulary"][SEIZURE_FREQUENCY.name]
    )
    assert "EEG_Type" in payloads[INVESTIGATIONS.name]["attribute_vocabulary"][INVESTIGATIONS.name]


def test_normalize_target_family_accepts_entity_or_event_family() -> None:
    assert ledger.normalize_target_family("Prescription") == PRESCRIPTION.name
    assert ledger.normalize_target_family("medication") == PRESCRIPTION.name
    assert ledger.normalize_target_family("seizure_frequency") == SEIZURE_FREQUENCY.name


def test_to_predicted_letter_filters_to_target_and_strips_projection_attrs() -> None:
    mentions = [
        structured.MentionForEvidence(
            entity=PRESCRIPTION.name,
            text="lamotrigine 100 mg twice daily",
            evidence="Current treatment is lamotrigine 100 mg twice daily.",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "100",
                "DoseUnit": "mg",
                "Frequency": "2",
                "CUI": "model-supplied",
            },
        ),
        structured.MentionForEvidence(
            entity=DIAGNOSIS.name,
            text="focal epilepsy",
            evidence="Diagnosis: focal epilepsy.",
            attributes={"DiagCategory": "Epilepsy", "Certainty": "5", "Negation": "Affirmed"},
        ),
    ]

    prediction, warnings = ledger.to_predicted_letter(
        "TEST001",
        mentions,
        note_text=_NOTE,
        target_family=PRESCRIPTION.name,
    )

    assert [m.entity for m in prediction.mentions] == [PRESCRIPTION.name]
    assert prediction.diagnostics["target_family"] == PRESCRIPTION.name
    assert any("dropped_non_target_entity" in warning for warning in warnings)
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_to_predicted_letter_keeps_sf_render_gate() -> None:
    mentions = [
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="focal seizures",
            evidence="She has focal seizures every month.",
            attributes={},
        )
    ]

    prediction, warnings = ledger.to_predicted_letter(
        "TEST001",
        mentions,
        note_text=_NOTE,
        target_family=SEIZURE_FREQUENCY.name,
    )

    assert prediction.mentions == ()
    assert any("dropped_no_frequency_state_rendering" in warning for warning in warnings)


def test_to_predicted_letter_normalizes_sf_text_to_selected_anchor() -> None:
    note_text = (
        "focal seizures with altered awareness, last event 3 years ago. "
        "focal to bilateral seizures 2 events in total. "
        "very frequent myoclonic jerks. "
        "absences and jerks happen several times a day."
    )
    mentions = [
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="focal seizures with altered awareness, last event 3 years ago",
            evidence="focal seizures with altered awareness, last event 3 years ago",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
        ),
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="focal to bilateral seizures 2 events in total",
            evidence="focal to bilateral seizures 2 events in total",
            attributes={"NumberOfSeizures": "2"},
        ),
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="very frequent myoclonic jerks",
            evidence="very frequent myoclonic jerks",
            attributes={"FrequencyChange": "Frequent"},
        ),
        structured.MentionForEvidence(
            entity=SEIZURE_FREQUENCY.name,
            text="absences and jerks happen several times a day",
            evidence="absences and jerks happen several times a day",
            attributes={"NumberOfSeizures": "3", "TimePeriod": "Day"},
        ),
    ]

    prediction, warnings = ledger.to_predicted_letter(
        "TEST001",
        mentions,
        note_text=note_text,
        target_family=SEIZURE_FREQUENCY.name,
    )

    assert [m.text for m in prediction.mentions] == [
        "focal seizures with altered awareness",
        "focal to bilateral seizures",
        "myoclonic jerks",
        "absences",
    ]
    assert all("dropped_no_frequency_state_rendering" not in warning for warning in warnings)


def test_summarize_rows_scores_target_family_headline() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "target_family": PRESCRIPTION.name,
            "parse_errors": [],
            "gold_mentions": [
                {
                    "entity": PRESCRIPTION.name,
                    "text": "lamotrigine 100 mg twice daily",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "100",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                }
            ],
            "predicted_mentions": [
                {
                    "entity": PRESCRIPTION.name,
                    "text": "lamotrigine 100 mg twice daily",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "100",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                }
            ],
        }
    ]

    summary = ledger.summarize_rows(rows, target_family=PRESCRIPTION.name)

    assert summary["target_family"] == PRESCRIPTION.name
    assert summary["clinical_recovery"]["headline"]["f1"] == 1.0
    assert summary["clinical_recovery"]["current_comparator_f1"] == 0.817
