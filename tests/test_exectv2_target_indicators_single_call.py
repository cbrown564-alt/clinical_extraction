import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_target_indicators_single_call import (  # noqa: E501
    COMPONENT_OWNER,
    _parse_target_extraction_json,
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


def test_target_single_call_adapter_repairs_absence_like_frequency_evidence() -> None:
    note = (
        "Seizure type and frequency: 2 tonic clonic seizures 2014, "
        "absence like seizures 2014"
    )
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
    assert any("removed_cross_modal_eeg_type_from_mri" in warning for warning in warnings)


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


def test_target_single_call_adapter_deduplicates_same_diagnosis_evidence() -> None:
    note = "The events are possibly focal onset."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={"Certainty": "4", "Negation": "Affirmed"},
            evidence="possibly focal onset",
        ),
        MentionRecord(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={"Certainty": "3", "Negation": "Affirmed"},
            evidence="possibly focal onset",
        ),
    ]

    predicted, _warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == ["focal epilepsy"]


def test_target_single_call_report_scores_projected_diagnosis_clinical_fact() -> None:
    note = "Diagnosis: probable focal epilepsy (perinatal insult)."
    predicted, _warnings = to_predicted_letter(
        "EA1",
        [
            MentionRecord(
                entity="Diagnosis",
                text="probable focal epilepsy (perinatal insult)",
                attributes={"Certainty": "4", "Negation": "Affirmed"},
                evidence="probable focal epilepsy (perinatal insult)",
            )
        ],
        note_text=note,
    )
    row = {
        "letter_id": "EA1",
        "split": "dev",
        "predicted_mentions": [
            {
                "entity": mention.entity,
                "text": mention.text,
                "attributes": dict(mention.attributes),
                "evidence": mention.evidence,
            }
            for mention in predicted.mentions
        ],
        "gold_mentions": [
            {
                "entity": "Diagnosis",
                "text": "focal epilepsy",
                "attributes": {"Certainty": "5", "Negation": "Affirmed"},
            }
        ],
    }

    summary = summarize_rows([row])
    target_report = summary["target_report"]
    diagnosis = target_report["candidates"][0]["headline_scores"]["Diagnosis"]

    assert target_report["headline_score_policies"]["Diagnosis"].startswith(
        "projected clinical-fact concept_only score"
    )
    assert diagnosis["f1"] == 1.0
    assert diagnosis["gold_count"] == 1
    assert diagnosis["pred_count"] == 1


def test_target_single_call_adapter_drops_non_epilepsy_diagnosis_core() -> None:
    note = "Her headaches are due to episodic migraine."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="episodic migraine",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="episodic migraine",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_non_epilepsy_core" in warning for warning in warnings)


def test_target_single_call_adapter_keeps_epilepsy_diagnosis_cores() -> None:
    note = (
        "Diagnosis: temporal lobe epilepsy. She has intractable epilepsy and "
        "epileptic attacks."
    )
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="temporal lobe epilepsy",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="temporal lobe epilepsy",
        ),
        MentionRecord(
            entity="Diagnosis",
            text="intractable epilepsy",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="intractable epilepsy",
        ),
        MentionRecord(
            entity="Diagnosis",
            text="epileptic attacks",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="epileptic attacks",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "temporal lobe epilepsy",
        "intractable epilepsy",
        "epileptic attacks",
    ]
    assert not any("dropped_non_epilepsy_core" in warning for warning in warnings)


def test_target_single_call_adapter_projects_diagnosis_from_selected_evidence() -> None:
    note = (
        "Diagnosis: epilepsy - probable focal. "
        "Diagnosis: focal epilepsy-Probable temporal. "
        "Epilepsy - unclassified, possibly generalised."
    )
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="epilepsy",
            attributes={"Certainty": "4", "Negation": "Affirmed"},
            evidence="epilepsy - probable focal",
        ),
        MentionRecord(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={"Certainty": "4", "Negation": "Affirmed"},
            evidence="focal epilepsy-Probable temporal",
        ),
        MentionRecord(
            entity="Diagnosis",
            text="epilepsy",
            attributes={"Certainty": "3", "Negation": "Affirmed"},
            evidence="Epilepsy - unclassified, possibly generalised",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "focal epilepsy",
        "temporal lobe epilepsy",
        "generalised epilepsy",
    ]
    assert sum("normalized_diagnosis_text" in warning for warning in warnings) == 3


def test_target_single_call_adapter_projects_unclassified_and_focal_onset_diagnosis() -> None:
    note = "Diagnosis: epilepsy - unclassified. He has seizures, possibly focal onset."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="epilepsy unclassified",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="epilepsy - unclassified",
        ),
        MentionRecord(
            entity="Diagnosis",
            text="seizures possibly focal onset",
            attributes={"Certainty": "3", "Negation": "Affirmed"},
            evidence="seizures, possibly focal onset",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == ["epilepsy", "focal epilepsy"]
    assert sum("normalized_diagnosis_text" in warning for warning in warnings) == 2


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
        "focal seizures",
    ]
    assert sum("normalized" in warning for warning in warnings) >= 2


def test_target_single_call_adapter_projects_focal_onset_sf_candidate_to_diagnosis() -> None:
    note = "She has seizures every 3 to 4 weeks, possibly focal onset."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="possibly focal onset",
            attributes={"Certainty": "3"},
            evidence="seizures every 3 to 4 weeks, possibly focal onset",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.entity for mention in predicted.mentions] == [
        "Diagnosis",
        "SeizureFrequency",
    ]
    assert predicted.mentions[0].text == "focal epilepsy"
    assert predicted.mentions[1].text == "seizures"
    assert any(
        "projected_focal_onset_sf_candidate_to_diagnosis" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_projects_focal_diagnosis_context_to_sf() -> None:
    note = "She has seizures every 3 to 4 weeks, possibly focal onset."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="focal seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="possibly focal onset",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.entity for mention in predicted.mentions] == [
        "Diagnosis",
        "SeizureFrequency",
    ]
    sf_mention = predicted.mentions[1]
    assert sf_mention.text == "seizures"
    assert sf_mention.evidence == "seizures every 3 to 4 weeks"
    assert sf_mention.attributes["NumberOfSeizures"] == "1"
    assert sf_mention.attributes["LowerNumberOfTimePeriods"] == "3"
    assert sf_mention.attributes["UpperNumberOfTimePeriods"] == "4"
    assert sf_mention.attributes["TimePeriod"] == "Week"
    assert any(
        "projected_focal_diagnosis_context_to_sf_state" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_projects_sf_context_to_focal_diagnosis() -> None:
    note = "She has seizures every 3 to 4 weeks, possibly focal onset."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizures",
            attributes={
                "NumberOfSeizures": "1",
                "NumberOfTimePeriods": "3",
                "TimePeriod": "Week",
            },
            evidence="seizures every 3 to 4 weeks",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.entity for mention in predicted.mentions] == [
        "SeizureFrequency",
        "Diagnosis",
    ]
    assert predicted.mentions[1].text == "focal epilepsy"
    assert predicted.mentions[1].attributes["Certainty"] == "3"
    assert predicted.mentions[1].evidence == "possibly focal onset"
    assert any(
        "projected_sf_context_to_focal_diagnosis" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_projects_sf_header_context_to_focal_diagnosis() -> None:
    note = (
        "Seizure type and frequency: seizures every 3 to 4 weeks, possibly focal onset\n"
        "She has seizures every 3 to 4 weeks."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="seizures every 3 to 4 weeks",
            attributes={
                "NumberOfSeizures": "1",
                "NumberOfTimePeriods": "3",
                "TimePeriod": "Week",
            },
            evidence="She has seizures every 3 to 4 weeks.",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.entity for mention in predicted.mentions] == [
        "SeizureFrequency",
        "Diagnosis",
    ]
    assert predicted.mentions[1].text == "focal epilepsy"
    assert predicted.mentions[1].attributes["Certainty"] == "3"
    assert any(
        "projected_sf_context_to_focal_diagnosis" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_projects_syndrome_without_alone_from_evidence() -> None:
    note = "Diagnosis: epilepsy with generalised tonic clonic seizures alone."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="epilepsy with generalised tonic clonic seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="epilepsy with generalised tonic clonic seizures alone",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "epilepsy with generalised tonic clonic seizures alone",
        "tonic clonic seizures",
    ]
    assert any("normalized_diagnosis_text" in warning for warning in warnings)


def test_target_single_call_adapter_drops_frequency_phrase_diagnosis() -> None:
    note = "She has seizures every 3 to 4 weeks."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="seizures every 3 to 4 weeks",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="She has seizures every 3 to 4 weeks",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_frequency_phrase_diagnosis_context" in warning for warning in warnings)


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


def test_target_single_call_adapter_drops_absence_like_diagnosis_core() -> None:
    note = "She had absence like seizures in 2014."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="absence like seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="absence like seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_non_epilepsy_core" in warning for warning in warnings)


def test_target_single_call_adapter_projects_frequency_header_absence_like_to_sf() -> None:
    note = (
        "Seizure type and frequency: 2 tonic clonic seizures 2014, "
        "absence like seizures 2014"
    )
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
        "projected_frequency_header_diagnosis_to_sf_state" in warning
        for warning in warnings
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

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["NumberOfSeizures"] == "3"
    assert attrs["TimeSince_or_TimeOfEvent"] == "Since"
    assert attrs["PointInTime"] == "LastClinic"
    assert "FrequencyChange" not in attrs
    assert any("projected_several_since_last_clinic" in warning for warning in warnings)


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
        "projected_every_n_to_m_periods_to_one_event_rate" in warning
        for warning in warnings
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
    assert any(
        "dropped_unanchored_current_seizure_free_state" in warning
        for warning in warnings
    )


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
    assert any(
        "dropped_unanchored_current_seizure_free_state" in warning
        for warning in warnings
    )


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

    assert [mention.text for mention in predicted.mentions] == ["focal seizures", "seizures"]
    zero_state = predicted.mentions[0]
    drug_change = predicted.mentions[1]
    assert zero_state.attributes["NumberOfSeizures"] == "0"
    assert drug_change.attributes["FrequencyChange"] == "Infrequent"
    assert drug_change.attributes["PointInTime"] == "DrugChange"
    assert any(
        "projected_controlled_drug_change_to_infrequent_state" in warning
        for warning in warnings
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


def test_target_single_call_adapter_projects_infrequent_diagnosis_year_to_unknown() -> None:
    note = (
        "He can get infrequent focal to bilateral convulsive seizures having "
        "around two in the year of his diagnosis."
    )
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal to bilateral convulsive seizures",
            attributes={
                "NumberOfSeizures": "2",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Year",
            },
            evidence=note,
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    attrs = predicted.mentions[0].attributes
    assert attrs["FrequencyChange"] == "Infrequent"
    assert "NumberOfSeizures" not in attrs
    assert any(
        "projected_infrequent_diagnosis_year_to_change_state" in warning
        for warning in warnings
    )


def test_target_single_call_adapter_drops_unsupported_zero_frequency_states() -> None:
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="generalised tonic clonic seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence=(
                "generalised tonic clonic seizures, which were well controlled "
                "on Sodium Valproate"
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
        sum("dropped_unsupported_episode_frequency_anchor" in warning for warning in warnings)
        == 2
    )


def test_target_single_call_adapter_splits_full_generalised_epilepsy_syndrome() -> None:
    note = (
        "Diagnosis: genetic generalised epilepsy-epilepsy with generalised tonic "
        "chronic seizures alone."
    )
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="generalised epilepsy",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence=(
                "genetic generalised epilepsy-epilepsy with generalised tonic "
                "chronic seizures alone"
            ),
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "generalised epilepsy",
        "epilepsy with generalised tonic clonic seizures alone",
    ]
    assert any("split_generalised_epilepsy_syndrome" in warning for warning in warnings)


def test_target_single_call_adapter_projects_complex_partial_conjunction_noise() -> None:
    note = "she continues to get general and complex partial seizures."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="general seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="general and complex partial seizures",
        ),
        MentionRecord(
            entity="SeizureFrequency",
            text="complex partial seizures",
            attributes={"FrequencyChange": "Same"},
            evidence="she continues to get general and complex partial seizures",
        ),
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].entity == "Diagnosis"
    assert predicted.mentions[0].text == "complex partial seizures"
    assert any("normalized_diagnosis_text" in warning for warning in warnings)
    assert any("dropped_ongoing_same_without_frequency" in warning for warning in warnings)


def test_target_single_call_adapter_expands_secondary_gtc_diagnosis() -> None:
    note = "Complex partial seizures with secondary generalised tonic clonic seizures."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="secondary generalised tonic clonic seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="secondary generalised tonic clonic seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "secondary generalised tonic clonic seizures",
        "tonic clonic seizures",
    ]
    assert any("split_secondary_gtc_to_tonic_clonic_diagnosis" in warning for warning in warnings)


def test_target_single_call_adapter_expands_syndrome_to_gtc_diagnosis() -> None:
    note = "epilepsy with generalised tonic clonic seizure alone"
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="epilepsy with generalised tonic clonic seizure alone",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="epilepsy with generalised tonic clonic seizure alone",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "epilepsy with generalised tonic clonic seizures alone",
        "tonic clonic seizures",
    ]
    assert any("split_syndrome_to_tonic_clonic_diagnosis" in warning for warning in warnings)


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

    assert [mention.text for mention in predicted.mentions] == [
        "focal to bilateral convulsive seizures",
        "convulsive seizure",
    ]
    assert all(mention.attributes["NumberOfSeizures"] == "0" for mention in predicted.mentions)
    assert any("split_convulsive_zero_state" in warning for warning in warnings)


def test_target_single_call_adapter_expands_last_event_typed_state_to_diagnosis() -> None:
    note = "Generalised tonic clonic seizure-last event July 2016."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="Generalised tonic clonic seizures",
            attributes={"NumberOfSeizures": "0", "YearDate": "2016"},
            evidence="Generalised tonic clonic seizure-last event July 2016",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.entity for mention in predicted.mentions] == [
        "SeizureFrequency",
        "Diagnosis",
    ]
    assert predicted.mentions[1].text == "Generalised tonic clonic seizures"
    assert any("projected_typed_seizure_frequency_to_diagnosis" in warning for warning in warnings)


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
    assert any(
        "projected_last_event_month_year_to_zero_since" in warning
        for warning in warnings
    )


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
        "projected_dated_absence_like_zero_to_active_rate" in warning
        for warning in warnings
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


def test_target_single_call_adapter_projects_active_rate_to_diagnosis() -> None:
    note = "In March she had 2 to 3 of her focal seizures."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={
                "LowerNumberOfSeizures": "2",
                "UpperNumberOfSeizures": "3",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
            },
            evidence="In March she had 2 to 3 of her focal seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.entity for mention in predicted.mentions] == [
        "SeizureFrequency",
        "Diagnosis",
    ]
    assert predicted.mentions[1].text == "focal seizures"
    assert any("projected_active_rate_seizure_type_to_diagnosis" in warning for warning in warnings)


def test_target_single_call_adapter_drops_zero_since_only_diagnosis_context() -> None:
    note = "She has not had any further generalised tonic clonic seizures since August 2016."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="generalised tonic clonic seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="generalised tonic clonic seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_zero_since_only_diagnosis_context" in warning for warning in warnings)


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

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "focal to bilateral convulsive seizures",
        "convulsive seizure",
    ]
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
