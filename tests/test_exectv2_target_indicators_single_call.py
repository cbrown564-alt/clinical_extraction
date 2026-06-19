import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_target_indicators_single_call import (  # noqa: E501
    COMPONENT_OWNER,
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
