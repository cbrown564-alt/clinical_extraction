import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_target_indicators_single_call import (  # noqa: E501
    COMPONENT_OWNER,
    build_prompt_input,
    to_predicted_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)


def test_target_single_call_prompt_is_limited_to_adr0030_indicators() -> None:
    payload = json.loads(build_prompt_input(ExectLetter("EA1", "MRI was normal.")))

    assert payload["prompt_version"].startswith("exectv2_target_indicators_single_call")
    assert set(payload["attribute_vocabulary"]) == set(TARGET_INDICATORS)
    assert "EpilepsyCause" not in json.dumps(payload)
    assert "PatientHistory" not in json.dumps(payload)


def test_target_single_call_adapter_drops_non_target_and_invalid_evidence() -> None:
    note = "Diagnosis: focal epilepsy. MRI was normal."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
            evidence="focal epilepsy",
        ),
        MentionRecord(
            entity="EpilepsyCause",
            text="stroke",
            attributes={},
            evidence="stroke",
        ),
        MentionRecord(
            entity="Investigations",
            text="MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
            evidence="not in source",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].entity == "Diagnosis"
    assert predicted.mentions[0].component_owner == COMPONENT_OWNER
    assert any("dropped_non_target_entity" in warning for warning in warnings)
    assert any("dropped_evidence_not_substring" in warning for warning in warnings)


def test_target_single_call_adapter_normalizes_format_only_attribute_variants() -> None:
    note = "She had 2 to 3 focal seizures every 3 to 4 weeks."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={
                "NumberOfSeizures": "2 to 3",
                "NumberOfTimePeriods": "3 to 4",
                "TimePeriod": "weeks",
            },
            evidence="2 to 3 focal seizures every 3 to 4 weeks",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["LowerNumberOfSeizures"] == "2"
    assert attrs["UpperNumberOfSeizures"] == "3"
    assert attrs["LowerNumberOfTimePeriods"] == "3"
    assert attrs["UpperNumberOfTimePeriods"] == "4"
    assert attrs["TimePeriod"] == "Week"
    assert "NumberOfSeizures" not in attrs
    assert "NumberOfTimePeriods" not in attrs
    assert any("split_range_attribute" in warning for warning in warnings)


def test_target_single_call_adapter_normalizes_dose_units() -> None:
    note = "Current medication is Lamotrigine 125 milligrams twice a day."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Lamotrigine 125 milligrams twice a day",
            attributes={
                "DrugName": "Lamotrigine",
                "DrugDose": "125",
                "DoseUnit": "milligrams",
                "Frequency": "2",
            },
            evidence="Lamotrigine 125 milligrams twice a day",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].attributes["DoseUnit"] == "mg"
    assert any("normalized_dose_unit" in warning for warning in warnings)


def test_target_single_call_adapter_projects_diagnosis_text_to_core_fact() -> None:
    note = "Diagnosis: probable focal epilepsy (perinatal insult)."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="probable focal epilepsy (perinatal insult)",
            attributes={"Certainty": "4", "Negation": "Affirmed"},
            evidence="probable focal epilepsy (perinatal insult)",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    mention = predicted.mentions[0]
    assert mention.text == "focal epilepsy"
    assert mention.evidence == "probable focal epilepsy (perinatal insult)"
    assert mention.attributes["CUI"] == "C0014547"
    assert any("normalized_diagnosis_text" in warning for warning in warnings)


def test_target_single_call_adapter_converts_day_period_to_week_when_exact() -> None:
    note = "She has focal seizures once every 14 days."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={
                "NumberOfSeizures": "1",
                "NumberOfTimePeriods": "14",
                "TimePeriod": "days",
            },
            evidence="focal seizures once every 14 days",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["NumberOfTimePeriods"] == "2"
    assert attrs["TimePeriod"] == "Week"
    assert any("converted_day_period_to_week" in warning for warning in warnings)


def test_target_single_call_adapter_normalizes_since_last_clinic_period() -> None:
    note = "Since her last clinic appointment she has had four secondary seizures."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="secondary seizures",
            attributes={
                "NumberOfSeizures": "4",
                "TimePeriod": "Since last clinic",
            },
            evidence="Since her last clinic appointment she has had four secondary seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["NumberOfSeizures"] == "4"
    assert attrs["TimeSince_or_TimeOfEvent"] == "Since"
    assert attrs["PointInTime"] == "LastClinic"
    assert "TimePeriod" not in attrs
    assert any("normalized_since_last_clinic" in warning for warning in warnings)
