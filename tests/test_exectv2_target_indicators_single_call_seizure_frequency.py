"""Seizure-frequency projection, quarantine, and drop tests for ExECTv2 target single-call.

Split from test_exectv2_target_indicators_single_call.py."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_target_indicators_single_call import (  # noqa: E501
    audit_only_projection_replay_switches,
    to_predicted_letter,
)


def test_target_single_call_adapter_repairs_absence_like_frequency_evidence() -> None:
    note = "Seizure type and frequency: 2 tonic clonic seizures 2014, absence like seizures 2014"
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="absence like seizures",
            attributes={
                "NumberOfSeizures": "1",
                "TimeSince_or_TimeOfEvent": "During",
                "YearDate": "2014",
            },
            evidence="he had 2 tonic clonic seizures in 2014 and one absence-like seizure",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].evidence == "absence like seizures 2014"
    assert any("repaired_absence_like_frequency_evidence" in warning for warning in warnings)


def test_target_single_call_adapter_normalizes_absence_like_sf_text_from_evidence() -> None:
    note = "2 generalised tonic clonic seizures 2014, absence like seizures 2014"
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizures",
            attributes={
                "NumberOfSeizures": "2",
                "TimeSince_or_TimeOfEvent": "During",
                "YearDate": "2014",
            },
            evidence="absence like seizures 2014",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].text == "absence like seizures"
    assert any("normalized_seizure_frequency_text_from_evidence" in warning for warning in warnings)


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


def test_target_single_call_adapter_normalizes_drug_dose_numbers() -> None:
    note = "Current medication: Phenytoin 75mg tds."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Phenytoin 75mg tds",
            attributes={
                "DrugName": "phenytoin",
                "DrugDose": "75mg",
                "DoseUnit": "mg",
                "Frequency": "3",
            },
            evidence="Phenytoin 75mg tds",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].attributes["DrugDose"] == "75"
    assert any("normalized_drug_dose_number" in warning for warning in warnings)


def test_target_single_call_adapter_splits_asymmetric_same_drug_dosing() -> None:
    note = "Current medication: levetiracetam 750mg mane, 500 mg nocte."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="levetiracetam 750mg mane, 500 mg nocte",
            attributes={
                "DrugName": "levetiracetam",
                "DrugDose": "750",
                "DoseUnit": "mg",
                "Frequency": "1",
            },
            evidence="levetiracetam 750mg mane, 500 mg nocte",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    doses = [mention.attributes["DrugDose"] for mention in predicted.mentions]
    assert doses == ["750", "500"]
    assert all(mention.attributes["Frequency"] == "1" for mention in predicted.mentions)
    assert any("split_asymmetric_same_drug_dosing" in warning for warning in warnings)


def test_target_single_call_adapter_splits_morning_evening_same_drug_dosing() -> None:
    note = "Epilim 300 mg in the morning and 600 mg in the evening."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Epilim 300 mg in the morning and 600 mg in the evening",
            attributes={
                "DrugName": "Epilim",
                "DrugDose": "300 mg in the morning and 600 mg in the evening",
                "DoseUnit": "mg",
                "Frequency": "1",
            },
            evidence="Epilim 300 mg in the morning and 600 mg in the evening",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.attributes["DrugDose"] for mention in predicted.mentions] == [
        "300",
        "600",
    ]
    assert all(mention.attributes["Frequency"] == "1" for mention in predicted.mentions)
    assert any("split_asymmetric_same_drug_dosing" in warning for warning in warnings)


def test_target_single_call_adapter_splits_morning_afternoon_same_drug_dosing() -> None:
    note = "Lamictal 100 mg in the morning, 175 mg in the afternoon."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Lamictal 100 mg in the morning, 175 mg in the afternoon",
            attributes={
                "DrugName": "Lamictal",
                "DrugDose": "100/175",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence="Lamictal 100 mg in the morning, 175 mg in the afternoon",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.attributes["DrugDose"] for mention in predicted.mentions] == [
        "100",
        "175",
    ]
    assert all(mention.attributes["Frequency"] == "1" for mention in predicted.mentions)
    assert any("split_asymmetric_same_drug_dosing" in warning for warning in warnings)


def test_target_single_call_adapter_splits_asymmetric_total_daily_dosing() -> None:
    note = "Current medication: levetiracetam 750mg mane, 500 mg nocte."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="levetiracetam 750mg mane, 500 mg nocte",
            attributes={
                "DrugName": "levetiracetam",
                "DrugDose": "1250",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence="levetiracetam 750mg mane, 500 mg nocte",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.attributes["DrugDose"] for mention in predicted.mentions] == [
        "750",
        "500",
    ]
    assert all(mention.attributes["Frequency"] == "1" for mention in predicted.mentions)
    assert any("split_asymmetric_same_drug_dosing" in warning for warning in warnings)


def test_target_single_call_adapter_repairs_total_daily_dose_to_per_dose() -> None:
    note = "Current medication: Phenytoin 75mg tds."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Phenytoin 75mg tds",
            attributes={
                "DrugName": "phenytoin",
                "DrugDose": "225",
                "DoseUnit": "mg",
                "Frequency": "3",
            },
            evidence="Phenytoin 75mg tds",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].attributes["DrugDose"] == "75"
    assert any("inferred_prescription_dose" in warning for warning in warnings)


def test_target_single_call_adapter_projects_nocte_frequency_from_evidence() -> None:
    note = "Sodium Valproate 800mg nocte."
    mentions = [
        MentionRecord(
            entity="Prescription",
            text="Sodium Valproate 800mg bd",
            attributes={
                "DrugName": "Sodium Valproate",
                "DrugDose": "800",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence="800mg nocte",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].attributes["Frequency"] == "1"
    assert any("projected_prescription_frequency_from_evidence" in warning for warning in warnings)


def test_target_single_call_adapter_projects_eeg_context_to_mri_normal() -> None:
    note = "The previous MRI has been normal. An EEG in 2014 did show some temporal slowing."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="EEG",
            attributes={"EEG_Results": "Abnormal"},
            evidence="An EEG in 2014 did show some temporal slowing",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == ["EEG", "MRI"]
    assert predicted.mentions[1].attributes["MRI_Performed"] == "Yes"
    assert predicted.mentions[1].attributes["MRI_Results"] == "Normal"
    assert any("projected_eeg_context_to_mri_normal" in warning for warning in warnings)


def test_target_single_call_adapter_projects_mri_context_to_eeg_result() -> None:
    note = "The previous MRI has been normal. An EEG in 2014 did show some temporal slowing."
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
            evidence="previous MRI has been normal",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == ["MRI", "EEG"]
    assert predicted.mentions[1].attributes["EEG_Performed"] == "Yes"
    assert predicted.mentions[1].attributes["EEG_Results"] == "Abnormal"
    assert any("projected_mri_context_to_eeg_result" in warning for warning in warnings)


def test_target_single_call_adapter_projects_temporal_focal_epilepsy() -> None:
    note = "Diagnosis: focal epilepsy-Probable temporal"
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="probable temporal focal epilepsy",
            attributes={"Certainty": "4", "Negation": "Affirmed"},
            evidence="focal epilepsy-Probable temporal",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].text == "temporal lobe epilepsy"
    assert any("normalized_diagnosis_text" in warning for warning in warnings)


def test_target_single_call_adapter_projects_unclear_epilepsy_with_generalised_evidence() -> None:
    note = "Diagnosis: Epilepsy - unclassified, possibly generalised."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="unclear epilepsy",
            attributes={"Certainty": "3", "Negation": "Affirmed"},
            evidence="Epilepsy - unclassified, possibly generalised",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].text == "generalised epilepsy"
    assert any("normalized_diagnosis_text" in warning for warning in warnings)


def test_target_single_call_adapter_projects_header_parent_epilepsy() -> None:
    note = "Diagnosis: Epilepsy - unclassified, possibly generalised."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="generalised epilepsy",
            attributes={"Certainty": "3", "Negation": "Affirmed"},
            evidence="Epilepsy - unclassified, possibly generalised",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "generalised epilepsy",
        "epilepsy",
    ]
    assert any("projected_header_parent_epilepsy" in warning for warning in warnings)


def test_target_single_call_adapter_normalizes_focal_without_awareness_concept() -> None:
    note = "In March she had 2 to 3 of her focal seizures without change in awareness."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="focal seizures without change in awareness",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="focal seizures without change in awareness",
        ),
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures without change in awareness",
            attributes={
                "LowerNumberOfSeizures": "2",
                "UpperNumberOfSeizures": "3",
                "TimeSince_or_TimeOfEvent": "During",
                "MonthDate": "March",
            },
            evidence="In March she had 2 to 3 of her focal seizures without change in awareness",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "focal seizures",
        "focal seizures",
    ]
    assert sum("normalized" in warning for warning in warnings) >= 2


def test_target_single_call_adapter_drops_generic_and_nonepileptic_seizure_diagnoses() -> None:
    note = "She has seizures and previous dissociative seizures."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="seizures",
        ),
        MentionRecord(
            entity="Diagnosis",
            text="dissociative seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="dissociative seizures",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert sum("dropped_non_epilepsy_core" in warning for warning in warnings) == 2


def test_target_single_call_adapter_projects_frequency_header_absence_like_to_sf() -> None:
    note = "Seizure type and frequency: 2 tonic clonic seizures 2014, absence like seizures 2014"
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="absence-like seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="absence like seizures 2014",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.entity for mention in predicted.mentions] == ["SeizureFrequency"]
    assert predicted.mentions[0].text == "absence like seizures"
    assert predicted.mentions[0].attributes["NumberOfSeizures"] == "1"
    assert predicted.mentions[0].attributes["YearDate"] == "2014"
    assert any(
        "projected_frequency_header_diagnosis_to_sf_state" in warning for warning in warnings
    )


def test_target_single_call_adapter_drops_febrile_seizure_frequency() -> None:
    note = "He had 4 febrile seizures at the age of 3, 4 and then around five."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="febrile seizures",
            attributes={"NumberOfSeizures": "4"},
            evidence="4 febrile seizures at the age of 3, 4 and then around five",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_non_seizure_frequency_anchor" in warning for warning in warnings)


def test_target_single_call_adapter_projects_remote_last_seizures_to_seizure_free() -> None:
    note = (
        "His last seizures were in his teenage years where he probably had "
        "around 3 or 4 focal to bilateral convulsive seizures."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal to bilateral convulsive seizures",
            attributes={
                "LowerNumberOfSeizures": "3",
                "UpperNumberOfSeizures": "4",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Year",
            },
            evidence=note,
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    sf_mention = predicted.mentions[0]
    diagnosis_mention = predicted.mentions[1]
    assert sf_mention.text == "seizures"
    assert sf_mention.attributes["NumberOfSeizures"] == "0"
    assert sf_mention.attributes["TimeSince_or_TimeOfEvent"] == "Since"
    assert sf_mention.attributes["AgeLower"] == "13"
    assert sf_mention.attributes["AgeUpper"] == "19"
    assert diagnosis_mention.entity == "Diagnosis"
    assert diagnosis_mention.text == "focal to bilateral convulsive seizures"
    assert any("projected_remote_last_seizures_to_seizure_free" in warning for warning in warnings)


def test_target_single_call_adapter_projects_vague_yearly_rate() -> None:
    note = "It seems as if he's definitely having a few seizures per year though."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizures",
            attributes={"FrequencyChange": "Frequent"},
            evidence="a few seizures per year",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["NumberOfSeizures"] == "2"
    assert attrs["NumberOfTimePeriods"] == "1"
    assert attrs["TimePeriod"] == "Year"
    assert "FrequencyChange" not in attrs
    assert any("projected_vague_yearly_rate" in warning for warning in warnings)


def test_target_single_call_adapter_projects_generic_roughly_two_yearly_rate() -> None:
    note = "He has had roughly two seizures per year since then."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizure",
            attributes={
                "NumberOfSeizures": "2",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Year",
            },
            evidence="roughly two seizures per year since then",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    mention = predicted.mentions[0]
    assert mention.text == "seizures"
    assert mention.attributes["NumberOfSeizures"] == "2"
    assert mention.attributes["TimePeriod"] == "Year"
    assert any("projected_generic_yearly_rate_anchor" in warning for warning in warnings)


def test_target_single_call_adapter_projects_several_since_last_clinic() -> None:
    note = "He has had several seizures since the last clinic appointment."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizures",
            attributes={"FrequencyChange": "Frequent"},
            evidence="several seizures since the last clinic appointment",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=note,
        projection_family_switches=audit_only_projection_replay_switches(),
    )

    attrs = predicted.mentions[0].attributes
    assert attrs["NumberOfSeizures"] == "3"
    assert attrs["TimeSince_or_TimeOfEvent"] == "Since"
    assert attrs["PointInTime"] == "LastClinic"
    assert "FrequencyChange" not in attrs
    assert any("projected_several_since_last_clinic" in warning for warning in warnings)


def test_target_single_call_adapter_repairs_reversed_since_last_clinic_evidence() -> None:
    note = "Since her last clinic appointment she has had four secondary generalised seizures."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="secondary generalised seizures",
            attributes={
                "NumberOfSeizures": "4",
                "TimeSince_or_TimeOfEvent": "Since",
                "PointInTime": "LastClinic",
            },
            evidence=(
                "she has had four secondary generalised seizures. Since her last clinic appointment"
            ),
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=note,
        projection_family_switches=audit_only_projection_replay_switches(),
    )

    assert predicted.mentions[0].evidence == note.rstrip(".")
    assert predicted.mentions[0].attributes["NumberOfSeizures"] == "4"
    assert any("repaired_since_last_clinic_count_evidence" in warning for warning in warnings)


def test_target_single_call_adapter_projects_four_since_last_clinic() -> None:
    note = "Since her last clinic appointment she has had four secondary generalised seizures."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="secondary generalised seizures",
            attributes={"TimeSince_or_TimeOfEvent": "Since", "PointInTime": "LastClinic"},
            evidence=note.rstrip("."),
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=note,
        projection_family_switches=audit_only_projection_replay_switches(),
    )

    assert predicted.mentions[0].attributes["NumberOfSeizures"] == "4"
    assert (
        predicted.diagnostics["target_projection_family_switches"][
            "projected_four_since_last_clinic"
        ]
        is True
    )
    assert any("projected_four_since_last_clinic" in warning for warning in warnings)


def test_target_projection_quarantines_last_clinic_projection_by_default() -> None:
    note = "Since her last clinic appointment she has had four secondary generalised seizures."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="secondary generalised seizures",
            attributes={"TimeSince_or_TimeOfEvent": "Since", "PointInTime": "LastClinic"},
            evidence=note.rstrip("."),
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert "NumberOfSeizures" not in predicted.mentions[0].attributes
    assert (
        predicted.diagnostics["target_projection_family_switches"][
            "projected_four_since_last_clinic"
        ]
        is False
    )
    assert any(
        "quarantined_projection_family: projected_four_since_last_clinic" in warning
        for warning in warnings
    )


def test_target_projection_quarantines_phrase_specific_evidence_repairs_by_default() -> None:
    since_clinic_note = (
        "Since her last clinic appointment she has had four secondary generalised seizures."
    )
    since_clinic_mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="secondary generalised seizures",
            attributes={
                "NumberOfSeizures": "4",
                "TimeSince_or_TimeOfEvent": "Since",
                "PointInTime": "LastClinic",
            },
            evidence=(
                "she has had four secondary generalised seizures. Since her last clinic appointment"
            ),
        )
    ]

    since_clinic_predicted, since_clinic_warnings = to_predicted_letter(
        "EA1",
        since_clinic_mentions,
        note_text=since_clinic_note,
    )

    christmas_note = (
        "He can get infrequent focal to bilateral convulsive seizures having "
        "around two in the year of his diagnosis and his last one being around "
        "Christmas time in 2017."
    )
    christmas_mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal to bilateral convulsive seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence=(
                "no further seizures having around two in the year of his diagnosis "
                "and his last one being around Christmas time in 2017"
            ),
        )
    ]

    christmas_predicted, christmas_warnings = to_predicted_letter(
        "EA1",
        christmas_mentions,
        note_text=christmas_note,
    )

    assert since_clinic_predicted.mentions == ()
    assert christmas_predicted.mentions == ()
    assert any(
        "quarantined_projection_family: repaired_since_last_clinic_count_evidence" in warning
        for warning in since_clinic_warnings
    )
    assert any(
        "quarantined_projection_family: repaired_last_event_evidence" in warning
        for warning in christmas_warnings
    )


def test_target_projection_quarantines_christmas_point_projection_by_default() -> None:
    note = "Focal to bilateral convulsive seizures, last event around Christmas 2017."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal to bilateral convulsive seizures",
            attributes={
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "Since",
                "PointInTime": "Christmas",
                "YearDate": "2017",
            },
            evidence="Focal to bilateral convulsive seizures, last event around Christmas 2017",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].attributes.get("YearDate") == "2017"
    assert "MonthDate" not in predicted.mentions[0].attributes
    assert any(
        "quarantined_projection_family: projected_christmas_point_to_month_date" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_projects_march_range_count() -> None:
    note = "In March she had 2 to 3 of her focal seizures without change in awareness."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={
                "NumberOfSeizures": "2",
                "NumberOfTimePeriods": "3",
                "TimePeriod": "Month",
            },
            evidence="In March she had 2 to 3 of her focal seizures without change in awareness",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["LowerNumberOfSeizures"] == "2"
    assert attrs["UpperNumberOfSeizures"] == "3"
    assert attrs["TimeSince_or_TimeOfEvent"] == "During"
    assert attrs["MonthDate"] == "3"
    assert any("projected_march_range_count" in warning for warning in warnings)


def test_target_single_call_adapter_projects_every_n_periods_to_one_event_rate() -> None:
    note = "Seizure type and frequency: focal seizures with altered awareness every 3 weeks."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures with altered awareness",
            attributes={"NumberOfTimePeriods": "3", "TimePeriod": "weeks"},
            evidence="focal seizures with altered awareness every 3 weeks",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["NumberOfSeizures"] == "1"
    assert attrs["NumberOfTimePeriods"] == "3"
    assert attrs["TimePeriod"] == "Week"
    assert any("projected_every_n_periods_to_one_event_rate" in warning for warning in warnings)


def test_target_single_call_adapter_projects_every_n_to_m_periods_to_one_event_rate() -> None:
    note = "She has seizures every 3 to 4 weeks."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizures every 3 to 4 weeks",
            attributes={
                "NumberOfSeizures": "1",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
            },
            evidence="She has seizures every 3 to 4 weeks",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    mention = predicted.mentions[0]
    assert mention.text == "seizures"
    assert mention.attributes["NumberOfSeizures"] == "1"
    assert mention.attributes["LowerNumberOfTimePeriods"] == "3"
    assert mention.attributes["UpperNumberOfTimePeriods"] == "4"
    assert mention.attributes["TimePeriod"] == "Week"
    assert "NumberOfTimePeriods" not in mention.attributes
    assert any(
        "projected_every_n_to_m_periods_to_one_event_rate" in warning for warning in warnings
    )


def test_target_single_call_adapter_drops_unanchored_current_seizure_free_state() -> None:
    note = "I was pleased to hear that he remains seizure free and is now driving."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizures",
            attributes={
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "During",
                "PointInTime": "LastClinic",
            },
            evidence="remains seizure free",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_unanchored_current_seizure_free_state" in warning for warning in warnings)


def test_target_single_call_adapter_drops_unanchored_current_seizure_free_text() -> None:
    note = "I was pleased to hear that he remains seizure free and is now driving."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizure free",
            attributes={
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "During",
                "PointInTime": "Last_Month",
            },
            evidence="he remains seizure free",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_unanchored_current_seizure_free_state" in warning for warning in warnings)


def test_target_single_call_adapter_drops_best_control_zero_state() -> None:
    note = "At present her epilepsy is the best it's ever been."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizures",
            attributes={"NumberOfSeizures": "0", "PointInTime": "Last_Year"},
            evidence="At present her epilepsy is the best it's ever been",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_vague_best_control_zero_state" in warning for warning in warnings)


def test_target_single_call_adapter_projects_controlled_drug_change_state() -> None:
    note = (
        "There has been improvement since increasing lamotrigine. The focal "
        "seizures are completely under control on the dose of lamotrigine "
        "200 mg twice a day."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "Since",
                "PointInTime": "DrugChange",
            },
            evidence=(
                "the focal seizures are completely under control on the dose "
                "of lamotrigine 200 mg twice a day"
            ),
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    outputs = [(mention.entity, mention.text) for mention in predicted.mentions]
    assert ("SeizureFrequency", "focal seizures") in outputs
    assert ("Diagnosis", "focal seizures") in outputs
    assert ("SeizureFrequency", "seizures") in outputs
    zero_state = next(
        mention
        for mention in predicted.mentions
        if mention.entity == "SeizureFrequency" and mention.text == "focal seizures"
    )
    drug_change = next(
        mention
        for mention in predicted.mentions
        if mention.entity == "SeizureFrequency" and mention.text == "seizures"
    )
    assert zero_state.attributes["NumberOfSeizures"] == "0"
    assert drug_change.attributes["FrequencyChange"] == "Infrequent"
    assert drug_change.attributes["PointInTime"] == "DrugChange"
    assert any(
        "projected_controlled_drug_change_to_infrequent_state" in warning for warning in warnings
    )


def test_target_single_call_adapter_splits_cluster_frequency_state() -> None:
    note = (
        "She had a cluster of seizures in August, 2017 where she had "
        "6-9 seizures every week for 3 weeks."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizures",
            attributes={
                "LowerNumberOfSeizures": "6",
                "UpperNumberOfSeizures": "9",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Week",
            },
            evidence="cluster of seizures in August, 2017 where she had 6-9 seizures every week",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "seizures",
        "cluster of seizures",
    ]
    assert predicted.mentions[1].attributes["NumberOfSeizures"] == "1"
    assert any("split_cluster_of_seizures_state" in warning for warning in warnings)


def test_target_single_call_adapter_drops_unsupported_zero_frequency_states() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence=(
                "generalised tonic clonic seizures, which were well controlled on Sodium Valproate"
            ),
        ),
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizure",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence="He last had a seizure before this around a year ago",
        ),
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=" ".join(m.evidence for m in mentions),
    )

    assert predicted.mentions == ()
    assert any("dropped_controlled_without_zero_anchor" in warning for warning in warnings)
    assert any("dropped_relative_prior_event_not_seizure_free" in warning for warning in warnings)


def test_target_single_call_adapter_drops_typed_zero_from_generic_seizure_free() -> None:
    note = "He remains seizure free."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence="He remains seizure free",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_generic_zero_state_for_typed_anchor" in warning for warning in warnings)


def test_target_single_call_adapter_drops_unsupported_minor_episode_rate() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="minor seizures",
            attributes={
                "LowerNumberOfSeizures": "4",
                "UpperNumberOfSeizures": "5",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Year",
            },
            evidence="The episodes last no longer than 3 minutes and occur 4 to 5 times a year.",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=mentions[0].evidence,
    )

    assert predicted.mentions == ()
    assert any("dropped_unsupported_episode_frequency_anchor" in warning for warning in warnings)


def test_target_single_call_adapter_drops_unsupported_episode_rate_for_typed_anchor() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="complex partial seizures",
            attributes={
                "LowerNumberOfSeizures": "4",
                "UpperNumberOfSeizures": "5",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Year",
            },
            evidence="The episodes last no longer than 3 minutes and occur 4 to 5 times a year.",
        ),
        MentionRecord(
            entity="SeizureFrequency",
            text="temporal lobe onset focal seizures",
            attributes={"FrequencyChange": "Frequent"},
            evidence="she has been getting episodes around twice a week of an unusual thought",
        ),
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=" ".join(m.evidence for m in mentions),
    )

    assert predicted.mentions == ()
    assert (
        sum("dropped_unsupported_episode_frequency_anchor" in warning for warning in warnings) == 2
    )


def test_target_single_call_adapter_expands_convulsive_zero_state() -> None:
    note = "focal to bilateral convulsive seizures, last event around Christmas 2017"
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal to bilateral convulsive seizures",
            attributes={
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "Since",
                "YearDate": "2017",
            },
            evidence="focal to bilateral convulsive seizures, last event around Christmas 2017",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    outputs = [(mention.entity, mention.text) for mention in predicted.mentions]
    assert ("SeizureFrequency", "focal to bilateral convulsive seizures") in outputs
    assert ("SeizureFrequency", "convulsive seizure") in outputs
    assert ("Diagnosis", "focal to bilateral convulsive seizures") in outputs
    assert all(
        mention.attributes["NumberOfSeizures"] == "0"
        for mention in predicted.mentions
        if mention.entity == "SeizureFrequency"
    )
    assert any("split_convulsive_zero_state" in warning for warning in warnings)


def test_target_single_call_adapter_projects_last_event_count_to_zero_since() -> None:
    note = "Generalised tonic clonic seizure-last event July 2016."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="Generalised tonic clonic seizure",
            attributes={"NumberOfSeizures": "1", "TimeSince_or_TimeOfEvent": "Since"},
            evidence="Generalised tonic clonic seizure-last event July 2016",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    mention = predicted.mentions[0]
    assert mention.attributes["NumberOfSeizures"] == "0"
    assert mention.attributes["TimeSince_or_TimeOfEvent"] == "Since"
    assert mention.attributes["MonthDate"] == "7"
    assert mention.attributes["YearDate"] == "2016"
    assert any("projected_last_event_month_year_to_zero_since" in warning for warning in warnings)


def test_target_single_call_adapter_projects_dated_absence_like_zero_to_active() -> None:
    note = "2 generalised tonic clonic seizures 2014, absence like seizures 2014"
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="absence-like seizures",
            attributes={
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "During",
                "YearDate": "2014",
            },
            evidence="2 generalised tonic clonic seizures 2014, absence like seizures 2014",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    mention = predicted.mentions[0]
    assert mention.attributes["NumberOfSeizures"] == "1"
    assert mention.attributes["TimeSince_or_TimeOfEvent"] == "During"
    assert mention.attributes["YearDate"] == "2014"
    assert any(
        "projected_dated_absence_like_zero_to_active_rate" in warning for warning in warnings
    )


def test_target_single_call_adapter_drops_previous_event_frequency_state() -> None:
    note = "Generalised tonic clonic seizure-last event July 2016. Previous event December 2015."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="Generalised tonic clonic seizure",
            attributes={
                "NumberOfSeizures": "1",
                "TimeSince_or_TimeOfEvent": "During",
                "MonthDate": "12",
            },
            evidence="Previous event December 2015",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_previous_event_not_headline_frequency" in warning for warning in warnings)


def test_target_single_call_adapter_repairs_last_event_suffix_evidence() -> None:
    note = (
        "He can get infrequent focal to bilateral convulsive seizures having "
        "around two in the year of his diagnosis and his last one being around "
        "Christmas time in 2017."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal to bilateral convulsive seizures",
            attributes={
                "NumberOfSeizures": "0",
                "TimeSince_or_TimeOfEvent": "Since",
                "YearDate": "2017",
            },
            evidence=(
                "no further seizures having around two in the year of his diagnosis "
                "and his last one being around Christmas time in 2017"
            ),
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=note,
        projection_family_switches=audit_only_projection_replay_switches(),
    )

    outputs = [(mention.entity, mention.text) for mention in predicted.mentions]
    assert ("SeizureFrequency", "focal to bilateral convulsive seizures") in outputs
    assert ("SeizureFrequency", "convulsive seizure") in outputs
    assert ("Diagnosis", "focal to bilateral convulsive seizures") in outputs
    assert any("repaired_last_event_evidence" in warning for warning in warnings)


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


def test_target_single_call_adapter_drops_non_seizure_frequency_anchor() -> None:
    note = "Her epilepsy is controlled."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="epilepsy",
            attributes={"NumberOfSeizures": "0"},
            evidence="epilepsy is controlled",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_non_seizure_frequency_anchor" in warning for warning in warnings)


def test_target_single_call_adapter_removes_unknown_like_frequency_numbers() -> None:
    note = "She has complex partial seizures, frequency unknown."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="complex partial seizures",
            attributes={
                "NumberOfSeizures": "unknown",
                "NumberOfTimePeriods": "unknown",
            },
            evidence="complex partial seizures, frequency unknown",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert "NumberOfSeizures" not in attrs
    assert "NumberOfTimePeriods" not in attrs
    assert any("removed_unknown_like_frequency_number" in warning for warning in warnings)


def test_target_single_call_adapter_projects_infrequent_companion_state() -> None:
    note = (
        "He can get infrequent focal to bilateral convulsive seizures having around "
        "two in the year of his diagnosis and his last one being around Christmas "
        "time in 2017. Focal to bilateral convulsive seizures, last event around "
        "Christmas 2017."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="Focal to bilateral convulsive seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence="Focal to bilateral convulsive seizures, last event around Christmas 2017",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=note,
        projection_family_switches=audit_only_projection_replay_switches(),
    )

    assert any(
        mention.entity == "SeizureFrequency"
        and mention.text == "Focal to bilateral convulsive seizures"
        and mention.attributes.get("FrequencyChange") == "Infrequent"
        for mention in predicted.mentions
    )
    assert any("projected_infrequent_context_state" in warning for warning in warnings)


def test_target_single_call_adapter_projects_later_infrequent_companion_state() -> None:
    note = (
        "Seizure type and frequency: Focal to bilateral convulsive seizures, "
        "last event around Christmas 2017. He can get infrequent focal to "
        "bilateral convulsive seizures having around two in the year of his "
        "diagnosis and his last one being around Christmas time in 2017."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="Focal to bilateral convulsive seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence="Focal to bilateral convulsive seizures, last event around Christmas 2017",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=note,
        projection_family_switches=audit_only_projection_replay_switches(),
    )

    assert any(
        mention.entity == "SeizureFrequency"
        and mention.text == "Focal to bilateral convulsive seizures"
        and mention.attributes.get("FrequencyChange") == "Infrequent"
        for mention in predicted.mentions
    )
    assert any("projected_infrequent_context_state" in warning for warning in warnings)


def test_target_single_call_adapter_projects_controlled_focal_state() -> None:
    note = (
        "I think that the focal seizures are completely under control on the dose "
        "of lamotrigine 200 mg twice a day."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={"NumberOfSeizures": "0"},
            evidence="focal seizures are completely under control",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert any(
        mention.entity == "Diagnosis" and mention.text == "focal seizures"
        for mention in predicted.mentions
    )
    assert any(
        mention.entity == "SeizureFrequency"
        and mention.text == "seizures"
        and mention.attributes.get("FrequencyChange") == "Infrequent"
        and mention.attributes.get("PointInTime") == "DrugChange"
        for mention in predicted.mentions
    )
    assert any(
        "projected_controlled_context_to_infrequent_state" in warning for warning in warnings
    )


def test_target_single_call_adapter_projects_remote_teenage_last_seizures() -> None:
    note = (
        "Diagnosis: Symptomatic structural focal epilepsy. His last seizures "
        "were in his teenage years where he probably had around 3 or 4 focal "
        "to bilateral convulsive seizures."
    )
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={"Certainty": "5", "DiagCategory": "Epilepsy", "Negation": "Affirmed"},
            evidence="Symptomatic structural focal epilepsy",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=note,
        projection_family_switches=audit_only_projection_replay_switches(),
    )

    assert any(
        mention.entity == "SeizureFrequency"
        and mention.text == "seizures"
        and mention.attributes.get("NumberOfSeizures") == "0"
        and mention.attributes.get("AgeLower") == "13"
        and mention.attributes.get("AgeUpper") == "19"
        for mention in predicted.mentions
    )
    assert any(
        "projected_diagnosis_context_to_remote_last_seizures_state" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_projects_frequent_myoclonic_jerks() -> None:
    note = (
        "Diagnosis: generalised tonic clonic seizures with myoclonic jerks, "
        "possible JME. She also had very frequent myoclonic jerks."
    )
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="generalised tonic clonic seizures with myoclonic jerks",
            attributes={
                "Certainty": "5",
                "DiagCategory": "MultipleSeizures",
                "Negation": "Affirmed",
            },
            evidence="generalised tonic clonic seizures with myoclonic jerks",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=note,
        projection_family_switches=audit_only_projection_replay_switches(),
    )

    assert any(
        mention.entity == "SeizureFrequency"
        and mention.text == "myoclonic jerks"
        and mention.attributes.get("FrequencyChange") == "Frequent"
        for mention in predicted.mentions
    )
    assert any(
        "projected_diagnosis_context_to_frequent_myoclonic_jerks" in warning for warning in warnings
    )


def test_target_projection_quarantines_infrequent_context_state_by_default() -> None:
    note = (
        "He can get infrequent focal to bilateral convulsive seizures having around "
        "two in the year of his diagnosis and his last one being around Christmas "
        "time in 2017. Focal to bilateral convulsive seizures, last event around "
        "Christmas 2017."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="Focal to bilateral convulsive seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence="Focal to bilateral convulsive seizures, last event around Christmas 2017",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert not any(
        mention.entity == "SeizureFrequency"
        and mention.attributes.get("FrequencyChange") == "Infrequent"
        for mention in predicted.mentions
    )
    assert any(
        "quarantined_projection_family: projected_infrequent_context_state" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_projects_returned_seizures_to_increased_state() -> None:
    note = (
        "Seizure type and frequency: focal seizures with altered awareness every 3 weeks. "
        "Unfortunately after the period of seizure freedom the seizures have returned."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures with altered awareness",
            attributes={
                "NumberOfSeizures": "1",
                "NumberOfTimePeriods": "3",
                "TimePeriod": "Week",
            },
            evidence="focal seizures with altered awareness every 3 weeks",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert any(
        mention.entity == "SeizureFrequency"
        and mention.text == "seizure"
        and mention.attributes.get("FrequencyChange") == "Increased"
        for mention in predicted.mentions
    )
    assert any("projected_returned_context_to_increased_state" in warning for warning in warnings)


def test_target_single_call_adapter_drops_unsupported_loss_of_consciousness_rate() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="episodes of loss of consciousness",
            attributes={"NumberOfSeizures": "7", "TimePeriod": "Year"},
            evidence="around 7 episodes of loss of consciousness since the beginning of the year",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=mentions[0].evidence,
    )

    assert predicted.mentions == ()
    assert any("dropped_unsupported_episode_frequency_anchor" in warning for warning in warnings)


def test_target_single_call_adapter_drops_single_event_frequency_state() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="single focal seizure",
            attributes={"NumberOfSeizures": "1", "DayDate": "22"},
            evidence="He had an event on 22 December.",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text="He had an event on 22 December.",
    )

    assert predicted.mentions == ()
    assert any("dropped_single_event_not_frequency_state" in warning for warning in warnings)


def test_target_single_call_adapter_drops_single_focal_event_frequency_state() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizure",
            attributes={"NumberOfSeizures": "1", "DayDate": "22"},
            evidence="He had an event on 22 December.",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text="He had an event on 22 December.",
    )

    assert predicted.mentions == ()
    assert any("dropped_single_event_not_frequency_state" in warning for warning in warnings)


def test_target_single_call_adapter_keeps_active_recent_seizure_with_relative_prior_event() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizure",
            attributes={
                "NumberOfSeizures": "1",
                "TimeSince_or_TimeOfEvent": "During",
                "PointInTime": "Last_Week",
            },
            evidence=(
                "had a generalised tonic clonic seizure. He last had a seizure "
                "before this around a year ago."
            ),
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=mentions[0].evidence,
    )

    assert any(
        mention.entity == "SeizureFrequency"
        and mention.text == "generalised tonic clonic seizure"
        and mention.attributes.get("NumberOfSeizures") == "1"
        for mention in predicted.mentions
    )
    assert not any(
        "dropped_relative_prior_event_not_seizure_free" in warning for warning in warnings
    )


def test_target_single_call_adapter_drops_improvement_frequency_change_duplicate() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={"FrequencyChange": "Decreased"},
            evidence="significant improvement since increasing the dose of lamotrigine",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=mentions[0].evidence,
    )

    assert predicted.mentions == ()
    assert any("dropped_improvement_phrase_not_headline_state" in warning for warning in warnings)


def test_target_single_call_adapter_drops_frequency_when_type_not_in_evidence() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={"FrequencyChange": "Increased"},
            evidence="they seem to happen more often if he is angry or upset",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=mentions[0].evidence,
    )

    assert predicted.mentions == ()
    assert any("dropped_unsupported_episode_frequency_anchor" in warning for warning in warnings)


def test_target_single_call_adapter_normalizes_untyped_seizures_over_months() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizures with myoclonic jerks",
            attributes={
                "NumberOfSeizures": "15",
                "NumberOfTimePeriods": "4",
                "TimePeriod": "Month",
            },
            evidence="approximately 15 seizures over 4 months which all happen during sleep",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=mentions[0].evidence,
    )

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].entity == "SeizureFrequency"
    assert predicted.mentions[0].text == "seizures"
    assert any("normalized_seizure_frequency_text" in warning for warning in warnings)


def test_target_single_call_adapter_drops_occasional_jerks_zero_state() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="jerks with flashing lights",
            attributes={"NumberOfSeizures": "0", "UpperNumberOfSeizures": "1"},
            evidence="she still gets occasional jerks with flashing lights",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=mentions[0].evidence,
    )

    assert predicted.mentions == ()
    assert any("dropped_occasional_jerks_not_seizure_free" in warning for warning in warnings)


def test_target_single_call_adapter_drops_inconsistent_zero_positive_rate() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "During"},
            evidence="approximately 3-4 generalised tonic clonic seizures per week",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text=mentions[0].evidence,
    )

    assert predicted.mentions == ()
    assert any(
        "dropped_inconsistent_zero_state_with_active_rate" in warning for warning in warnings
    )


def test_target_single_call_adapter_drops_eeg_confirmation_without_result_language() -> None:
    mentions = [
        MentionRecord(
            entity="Investigations",
            text="EEG recording",
            attributes={"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
            evidence="confirmed with an EEG recording",
        )
    ]

    predicted, warnings = to_predicted_letter(
        "EA1",
        mentions,
        note_text="which was confirmed with an EEG recording.",
    )

    assert predicted.mentions == ()
    assert any("dropped_unsupported_eeg_confirmation" in warning for warning in warnings)
