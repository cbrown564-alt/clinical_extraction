"""Invariant-focused tests for exectv2 llm only parsing."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)


def test_parse_flat_compact_events() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "diagnosis",
                    "evidence": "She has focal epilepsy.",
                    "fact": "focal epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                },
                {
                    "family": "medication",
                    "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                    "fact": "lamotrigine 200 mg twice daily",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": 200,
                        "DoseUnit": "mg",
                        "Frequency": 2,
                    },
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)
    mentions = structured.mentions_from_events(record) if record is not None else []

    assert record is not None
    assert not any(str(error).startswith("schema_validation_error:") for error in errors)
    assert [event.family for event in record.clinical_events] == [
        "diagnosis",
        "medication",
    ]
    assert [mention.entity for mention in mentions] == [
        DIAGNOSIS.name,
        PRESCRIPTION.name,
    ]
    assert mentions[0].text == "focal epilepsy"
    assert mentions[0].attributes == {"DiagCategory": "Epilepsy"}
    assert mentions[1].text == "lamotrigine 200 mg twice daily"
    assert mentions[1].attributes["DrugDose"] == "200"
    assert mentions[1].attributes["Frequency"] == "2"


def test_parse_compact_short_attribute_names() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "medication",
                    "evidence": "Current treatment is lamotrigine 200 mg twice daily.",
                    "fact": "lamotrigine",
                    "attributes": {
                        "name": "lamotrigine",
                        "dose": 200,
                        "unit": "mg",
                        "frequency": "as_required",
                    },
                },
                {
                    "family": "diagnosis",
                    "evidence": "She has focal epilepsy.",
                    "fact": "focal epilepsy",
                    "attributes": {"category": "epilepsy"},
                },
                {
                    "family": "seizure_frequency",
                    "evidence": "2 focal seizures per month.",
                    "fact": "focal seizures",
                    "attributes": {
                        "count": 2,
                        "period": "month",
                        "when": "since",
                        "point": "last_clinic",
                    },
                },
                {
                    "family": "investigation",
                    "evidence": "MRI brain was normal.",
                    "fact": "MRI",
                    "attributes": {
                        "mri_performed": "yes",
                        "mri_result": "normal",
                    },
                },
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)
    mentions = structured.mentions_from_events(record) if record is not None else []

    assert record is not None
    assert not any(str(error).startswith("schema_validation_error:") for error in errors)
    by_entity = {mention.entity: mention.attributes for mention in mentions}
    assert by_entity[PRESCRIPTION.name] == {
        "DrugName": "lamotrigine",
        "DrugDose": "200",
        "DoseUnit": "mg",
        "Frequency": "As_Required",
    }
    assert by_entity[DIAGNOSIS.name] == {"DiagCategory": "Epilepsy"}
    assert by_entity[SEIZURE_FREQUENCY.name] == {
        "NumberOfSeizures": "2",
        "TimePeriod": "Month",
        "TimeSince_or_TimeOfEvent": "Since",
        "PointInTime": "LastClinic",
    }
    assert by_entity[INVESTIGATIONS.name] == {
        "MRI_Performed": "Yes",
        "MRI_Results": "Normal",
    }


def test_parse_compact_ct_short_attribute_names() -> None:
    raw = json.dumps(
        {
            "clinical_events": [
                {
                    "family": "investigation",
                    "evidence": "CT head was abnormal.",
                    "fact": "CT",
                    "attributes": {
                        "ct_performed": "yes",
                        "ct_result": "abnormal",
                    },
                }
            ]
        }
    )

    record, errors = structured.parse_structured_events_json(raw)
    mentions = structured.mentions_from_events(record) if record is not None else []

    assert record is not None
    assert not any(str(error).startswith("schema_validation_error:") for error in errors)
    assert mentions[0].entity == INVESTIGATIONS.name
    assert mentions[0].attributes == {
        "CT_Performed": "Yes",
        "CT_Results": "Abnormal",
    }


def test_parse_compact_recovers_extra_trailing_brace() -> None:
    raw = (
        '{"clinical_events":[{"family":"investigation","evidence":'
        '"MRI 2019 right occipital lobe infarct","fact":'
        '"MRI 2019 right occipital lobe infarct","attributes":'
        '{"mri_performed":"yes","mri_result":"abnormal"}}}]}'
    )

    record, errors = structured.parse_structured_events_json(raw)
    mentions = structured.mentions_from_events(record) if record is not None else []

    assert record is not None
    assert not any(str(error).startswith("invalid_json:") for error in errors)
    assert "json_dialect_repaired: unmatched_container_close" in errors
    assert [event.family for event in record.clinical_events] == ["investigation"]
    assert mentions[0].entity == INVESTIGATIONS.name
    assert mentions[0].text == "MRI 2019 right occipital lobe infarct"
    assert mentions[0].attributes == {
        "MRI_Performed": "Yes",
        "MRI_Results": "Abnormal",
    }
