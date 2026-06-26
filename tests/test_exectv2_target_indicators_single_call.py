"""Parser, prescription, and investigation adapter tests for ExECTv2 target single-call."""

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_target_indicators_single_call import (  # noqa: E501
    COMPONENT_OWNER,
    _parse_target_extraction_json,
    audit_only_projection_replay_switches,
    build_prompt_input,
    summarize_rows,
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


def test_target_single_call_parser_salvages_malformed_rationale_mentions() -> None:
    raw = (
        '{"mentions": ['
        '{"entity": "Diagnosis", "text": "focal epilepsy", '
        '"attributes": {"Certainty": "4"}, "evidence": "probable focal"}, '
        '{"attributes": {"NumberOfSeizures": "0", "PointInTime": "LastClinic"}, '
        '"confidence": "medium", "entity": "SeizureFrequency", '
        '"evidence": "several seizures since the last clinic appointment", '
        '"rationale": "unterminated model deliberation}, '
        '{"entity": "Investigations", "text": "MRI", '
        '"attributes": {"MRI_Performed": "Yes"}, "evidence": "MRI normal"}'
        "]}"
    )

    extraction, errors = _parse_target_extraction_json(raw)

    assert extraction is not None
    assert [mention.entity for mention in extraction.mentions] == [
        "Diagnosis",
        "SeizureFrequency",
        "Investigations",
    ]
    assert extraction.mentions[1].text == "seizures"
    assert any("salvaged_invalid_json_mentions" in error for error in errors)


def test_target_single_call_parser_accepts_python_literal_payload() -> None:
    raw = (
        "{'mentions': [{'entity': 'Diagnosis', 'text': 'generalised epilepsy', "
        "'attributes': {'Certainty': '3'}, "
        "'evidence': 'Epilepsy - unclassified, possibly generalised'}]}"
    )

    extraction, errors = _parse_target_extraction_json(raw)

    assert extraction is not None
    assert extraction.mentions[0].entity == "Diagnosis"
    assert errors == ["parsed_python_literal_payload"]


def test_target_single_call_parser_salvages_complete_objects_from_truncated_array() -> None:
    raw = (
        '{"mentions": ['
        '{"entity": "Diagnosis", "text": "suspected epilepsy", '
        '"attributes": {"Certainty": "3"}, "evidence": "I suspect this lady has epilepsy"}, '
        '{"entity": "Investigations", "text": "MR brain", '
        '"attributes": {"MRI_Performed": "Yes"}, "evidence": "I will arrange an MR brain"} '
    )

    extraction, errors = _parse_target_extraction_json(raw)

    assert extraction is not None
    assert [mention.entity for mention in extraction.mentions] == [
        "Diagnosis",
        "Investigations",
    ]
    assert any("salvaged_invalid_json_mentions" in error for error in errors)


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


def test_target_single_call_adapter_repairs_case_only_evidence() -> None:
    note = "Seizure type and frequency: Generalised tonic clonic seizure-last event July 2016."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizure",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence="generalised tonic clonic seizure-last event July 2016",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].evidence == "Generalised tonic clonic seizure-last event July 2016"
    assert any("repaired_evidence_case" in warning for warning in warnings)


def test_target_single_call_adapter_repairs_whitespace_equivalent_evidence() -> None:
    note = "Diagnosis:\u00a0 Temporal lobe epilepsy"
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="Temporal lobe epilepsy",
            attributes={"Certainty": "5", "DiagCategory": "Epilepsy", "Negation": "Affirmed"},
            evidence="Diagnosis: Temporal lobe epilepsy",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].text == "temporal lobe epilepsy"
    assert any("repaired_whitespace_equivalent_evidence" in warning for warning in warnings)


def test_target_single_call_adapter_repairs_no_further_since_evidence() -> None:
    note = "She has not had any further generalised tonic clonic seizures since August 2016."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizures",
            attributes={
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "Since",
                "MonthDate": "8",
                "YearDate": "2016",
            },
            evidence="no further generalised tonic clonic seizures since August 2016",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert (
        predicted.mentions[0].evidence
        == "has not had any further generalised tonic clonic seizures since August 2016"
    )
    assert any("repaired_no_further_since_evidence" in warning for warning in warnings)


def test_target_single_call_adapter_repairs_prescription_frequency_synonym_evidence() -> None:
    note = "Current medication: carbamazepine 400 mg twice a day."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="carbamazepine 400 mg bd",
            attributes={
                "DrugName": "carbamazepine",
                "DrugDose": "400",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence="carbamazepine 400 mg bd",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].evidence == "carbamazepine 400 mg twice a day"
    assert any(
        "repaired_prescription_frequency_synonym_evidence" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_repairs_ellipsis_evidence() -> None:
    note = "Current medication: levetiracetam 750mg mane, 500 mg nocte. Phenytoin 75mg tds."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Phenytoin 75mg tds",
            attributes={
                "DrugName": "Phenytoin",
                "DrugDose": "75",
                "DoseUnit": "mg",
                "Frequency": "3",
            },
            evidence="Current medication: ... Phenytoin 75mg tds",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].evidence == "Phenytoin 75mg tds"
    assert any("repaired_ellipsis_evidence" in warning for warning in warnings)


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


def test_target_single_call_adapter_infers_prescription_attrs_from_text() -> None:
    note = "Current medication is Lamotrigine 125 milligrams twice a day."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Lamotrigine 125 milligrams twice a day",
            attributes={"Frequency": "2"},
            evidence="Lamotrigine 125 milligrams twice a day",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["DrugName"] == "lamotrigine"
    assert attrs["DrugDose"] == "125"
    assert attrs["DoseUnit"] == "mg"
    assert attrs["Frequency"] == "2"
    assert any("inferred_prescription_drug_name" in warning for warning in warnings)


def test_target_single_call_adapter_extends_asymmetric_prescription_evidence() -> None:
    note = "Current medication: levetiracetam 750mg mane, 500 mg nocte."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="levetiracetam 750mg mane",
            attributes={
                "DrugName": "levetiracetam",
                "DrugDose": "750",
                "DoseUnit": "mg",
                "Frequency": "1",
            },
            evidence="levetiracetam 750mg mane",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.attributes["DrugDose"] for mention in predicted.mentions] == [
        "750",
        "500",
    ]
    assert any(
        "extended_asymmetric_prescription_evidence" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_deduplicates_prescription_regimens() -> None:
    note = "Current medication: levetiracetam 750mg mane, 500 mg nocte."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="levetiracetam 750mg mane",
            attributes={
                "DrugName": "levetiracetam",
                "DrugDose": "750",
                "DoseUnit": "mg",
                "Frequency": "1",
            },
            evidence="levetiracetam 750mg mane",
        ),
        MentionRecord(
            entity="Prescription",
            text="500 mg nocte",
            attributes={
                "DrugName": "levetiracetam",
                "DrugDose": "500",
                "DoseUnit": "mg",
                "Frequency": "1",
            },
            evidence="500 mg nocte",
        ),
    ]

    predicted, _warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.attributes["DrugDose"] for mention in predicted.mentions] == [
        "750",
        "500",
    ]


def test_target_single_call_adapter_drops_planned_prescriptions() -> None:
    note = "I suggest adding in some Clobazam to take on an as required basis."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Clobazam as required",
            attributes={"DrugName": "Clobazam", "Frequency": "As_Required"},
            evidence="Clobazam to take on an as required basis",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_planned_prescription" in warning for warning in warnings)


def test_target_single_call_adapter_drops_planned_investigations_without_results() -> None:
    note = "I will arrange further tests including an MR brain and EEG."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="MR brain",
            attributes={"MRI_Performed": "Yes"},
            evidence="MR brain",
        ),
        MentionRecord(
            entity="Investigations",
            text="EEG",
            attributes={"EEG_Performed": "Yes"},
            evidence="EEG",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert sum("dropped_planned_investigation" in warning for warning in warnings) == 2


def test_target_single_call_adapter_drops_requesting_investigations_without_results() -> None:
    note = "I will update her investigations by requesting an EEG and MRI."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="EEG",
            attributes={"CT_Performed": "No"},
            evidence="I will update her investigations by requesting an EEG and MRI",
        ),
        MentionRecord(
            entity="Investigations",
            text="MRI",
            attributes={"CT_Performed": "No"},
            evidence="I will update her investigations by requesting an EEG and MRI",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert sum("dropped_empty_investigation_attrs" in warning for warning in warnings) == 2


def test_target_single_call_adapter_drops_useful_to_get_planned_investigation() -> None:
    note = "It would be useful to get a repeat MRI scan."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="repeat MRI scan",
            attributes={"MRI_Performed": "Yes"},
            evidence="useful to get a repeat MRI scan",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_planned_investigation" in warning for warning in warnings)


def test_target_single_call_adapter_removes_cross_modal_eeg_type_from_mri() -> None:
    note = "The previous MRI has been normal. An EEG in 2014 did show temporal slowing."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="MRI",
            attributes={
                "MRI_Performed": "Yes",
                "MRI_Results": "Normal",
                "EEG_Type": "Standard",
            },
            evidence="previous MRI has been normal",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert "EEG_Type" not in predicted.mentions[0].attributes
    assert any(
        "removed_cross_modal_investigation_attrs" in warning for warning in warnings
    )


def test_target_single_call_adapter_removes_cross_modal_ct_attrs_from_mri() -> None:
    note = "Previous investigations: MRI 2015 normal, EEG 2015 normal."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="MRI",
            attributes={"CT_Performed": "No", "CT_Results": "Unknown"},
            evidence="MRI 2015 normal, EEG 2015 normal.",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any(
        "removed_cross_modal_investigation_attrs" in warning for warning in warnings
    )
    assert any("dropped_empty_investigation_attrs" in warning for warning in warnings)


def test_target_single_call_adapter_infers_investigation_performed_from_result() -> None:
    note = "An EEG in 2014 did show some temporal slowing."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="EEG",
            attributes={"EEG_Results": "Abnormal"},
            evidence="An EEG in 2014 did show some temporal slowing",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].attributes["EEG_Performed"] == "Yes"
    assert any("inferred_eeg_performed_from_result" in warning for warning in warnings)


def test_target_single_call_adapter_repairs_trailing_punctuation_evidence() -> None:
    note = "Previous investigations: MRI 2015 normal"
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
            evidence="MRI 2015 normal.",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].evidence == "MRI 2015 normal"
    assert any("repaired_trailing_punctuation_evidence" in warning for warning in warnings)


def test_target_single_call_adapter_deduplicates_investigations() -> None:
    note = "The previous MRI has been normal. An EEG in 2014 did show some temporal slowing."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
            evidence="previous MRI has been normal",
        ),
        MentionRecord(
            entity="Investigations",
            text="EEG",
            attributes={"EEG_Results": "Abnormal"},
            evidence="An EEG in 2014 did show some temporal slowing",
        ),
    ]

    predicted, _warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == ["MRI", "EEG"]


def test_target_single_call_adapter_drops_investigation_only_temporal_diagnosis() -> None:
    note = "MRI shows a subtle high intensity signal in the left temporal lobe."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="temporal lobe epilepsy",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="subtle high intensity signal in the left temporal lobe",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any(
        "dropped_investigation_only_diagnosis_context" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_drops_non_target_ecg_investigation_attrs() -> None:
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="ECG",
            attributes={
                "CT_Performed": "No",
                "EEG_Performed": "No",
                "MRI_Performed": "No",
                "MRI_Results": "Unknown",
            },
            evidence="ECG was normal",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text="ECG was normal",
    )

    assert predicted.mentions == ()
    assert any("removed_non_target_investigation_attrs" in warning for warning in warnings)


def test_target_single_call_adapter_drops_planned_unknown_result_investigation() -> None:
    note = "I am therefore arranging an MRI scan of the brain."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="MRI scan of the brain",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Unknown"},
            evidence="arranging an MRI scan of the brain",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_planned_investigation" in warning for warning in warnings)


def test_target_single_call_adapter_drops_investigation_result_from_neuro_exam() -> None:
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="MRI scan",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
            evidence="neurological examination was normal",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text="neurological examination was normal",
    )

    assert predicted.mentions == ()
    assert any("dropped_unsupported_investigation_evidence" in warning for warning in warnings)
