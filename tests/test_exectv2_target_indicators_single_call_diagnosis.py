"""Diagnosis projection and normalization tests for ExECTv2 target single-call.

Split from test_exectv2_target_indicators_single_call.py."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_target_indicators_single_call import (  # noqa: E501
    audit_only_projection_replay_switches,
    summarize_rows,
    to_predicted_letter,
)


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


def test_target_single_call_adapter_extends_probable_temporal_diagnosis_evidence() -> None:
    note = "Diagnosis: focal epilepsy-Probable temporal"
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={"Certainty": "4", "Negation": "Affirmed"},
            evidence="focal epilepsy-Probable",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].text == "temporal lobe epilepsy"
    assert any("extended_probable_temporal_diagnosis_evidence" in warning for warning in warnings)


def test_target_single_call_adapter_preserves_genetic_generalised_epilepsy() -> None:
    note = (
        "Diagnosis: genetic generalised epilepsy-epilepsy with generalised "
        "tonic clonic seizures alone."
    )
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text=(
                "genetic generalised epilepsy-epilepsy with generalised "
                "tonic chronic seizures alone."
            ),
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence=note,
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].text == "genetic generalised epilepsy"
    assert any("normalized_diagnosis_text" in warning for warning in warnings)


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


def test_target_single_call_adapter_deduplicates_same_diagnosis_concept() -> None:
    note = "Syndrome of epilepsy with generalised tonic clonic seizure alone."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="epilepsy with generalised tonic clonic seizure alone",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="Syndrome of epilepsy with generalised tonic clonic seizure alone",
        ),
        MentionRecord(
            entity="Diagnosis",
            text="epilepsy with generalised tonic clonic seizures alone",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="epilepsy with generalised tonic clonic seizure alone",
        ),
    ]

    predicted, _warnings = to_predicted_letter("EA1", mentions, note_text=note)

    syndrome_mentions = [
        mention.text
        for mention in predicted.mentions
        if mention.text == "epilepsy with generalised tonic clonic seizures alone"
    ]
    assert syndrome_mentions == ["epilepsy with generalised tonic clonic seizures alone"]


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
    note = "Diagnosis: temporal lobe epilepsy. She has intractable epilepsy and epileptic attacks."
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
        "epilepsy",
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
    assert any("projected_focal_onset_sf_candidate_to_diagnosis" in warning for warning in warnings)


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
    assert any("projected_focal_diagnosis_context_to_sf_state" in warning for warning in warnings)


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
    assert any("projected_sf_context_to_focal_diagnosis" in warning for warning in warnings)


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
    assert any("projected_sf_context_to_focal_diagnosis" in warning for warning in warnings)


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


def test_target_single_call_adapter_projects_dated_diagnosis_context_to_sf() -> None:
    note = "Seizure type and frequency: 2 generalised tonic clonic seizures 2014."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="generalised tonic clonic seizures",
            attributes={"Certainty": "5", "Negation": "Affirmed"},
            evidence="generalised tonic clonic seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    sf = [mention for mention in predicted.mentions if mention.entity == "SeizureFrequency"]
    assert sf[0].attributes["NumberOfSeizures"] == "2"
    assert sf[0].attributes["TimeSince_or_TimeOfEvent"] == "During"
    assert sf[0].attributes["YearDate"] == "2014"
    assert any("projected_dated_diagnosis_context_to_sf" in warning for warning in warnings)


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
        "projected_infrequent_diagnosis_year_to_change_state" in warning for warning in warnings
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
        "genetic generalised epilepsy",
        "epilepsy with generalised tonic clonic seizures alone",
        "tonic clonic seizures",
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


def test_target_single_call_adapter_projects_absence_like_header_diagnosis_to_sf() -> None:
    note = "Seizure type and frequency: 2 tonic clonic seizures 2014, absence like seizures 2014"
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="absence-like seizures",
            attributes={"Certainty": "5", "DiagCategory": "MultipleSeizures"},
            evidence="absence like seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    mention = predicted.mentions[0]
    assert mention.entity == "SeizureFrequency"
    assert mention.text == "absence like seizures"
    assert mention.attributes["NumberOfSeizures"] == "1"
    assert mention.attributes["YearDate"] == "2014"
    assert any(
        "projected_frequency_header_diagnosis_to_sf_state" in warning for warning in warnings
    )


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


def test_target_single_call_adapter_projects_epileptic_events_to_attack() -> None:
    note = "She continues to get a combination of epileptic and nonepileptic events."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="epileptic",
            attributes={"Certainty": "5", "DiagCategory": "MultipleSeizures"},
            evidence="combination of epileptic and nonepileptic events",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions[0].text == "epileptic attack"
    assert any("normalized_diagnosis_text" in warning for warning in warnings)


def test_target_single_call_adapter_projects_combined_epileptic_nonepileptic_events() -> None:
    note = "She continues to get a combination of epileptic and nonepileptic events."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="epileptic and nonepileptic events",
            attributes={"Certainty": "5", "DiagCategory": "MultipleSeizures"},
            evidence="combination of epileptic and nonepileptic events",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].text == "epileptic attack"
    assert any("normalized_diagnosis_text" in warning for warning in warnings)


def test_target_single_call_adapter_drops_epilepsy_inferred_only_from_seizures() -> None:
    note = "She has not had any further seizures."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="epilepsy",
            attributes={"Certainty": "5", "DiagCategory": "Epilepsy"},
            evidence="has not had any further seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert predicted.mentions == ()
    assert any("dropped_unsupported_inferred_diagnosis" in warning for warning in warnings)


def test_target_single_call_adapter_projects_context_parent_epilepsy() -> None:
    note = (
        "I reviewed this lady with epilepsy, together with her husband. "
        "I think these are in keeping with temporal lobe onset focal seizures."
    )
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="temporal lobe onset focal seizures",
            attributes={"Certainty": "4", "DiagCategory": "MultipleSeizures"},
            evidence="temporal lobe onset focal seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert any(
        mention.entity == "Diagnosis" and mention.text == "epilepsy"
        for mention in predicted.mentions
    )
    assert any("projected_context_parent_epilepsy" in warning for warning in warnings)


def test_target_single_call_adapter_splits_temporal_lobe_onset_to_focal_seizures() -> None:
    note = "I think these are in keeping with temporal lobe onset focal seizures."
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="temporal lobe onset focal seizures",
            attributes={"Certainty": "4", "DiagCategory": "MultipleSeizures"},
            evidence="temporal lobe onset focal seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert [mention.text for mention in predicted.mentions] == [
        "temporal lobe seizure",
        "focal seizures",
    ]
    assert any("split_temporal_lobe_onset_to_focal_seizures" in warning for warning in warnings)


def test_target_single_call_adapter_projects_typed_zero_state_to_diagnosis() -> None:
    note = "Focal to bilateral convulsive seizures, last event around Christmas 2017"
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="Focal to bilateral convulsive seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence="Focal to bilateral convulsive seizures, last event around Christmas 2017",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert any(
        mention.entity == "Diagnosis" and mention.text == "Focal to bilateral convulsive seizures"
        for mention in predicted.mentions
    )
    assert any("projected_typed_seizure_frequency_to_diagnosis" in warning for warning in warnings)


def test_target_single_call_adapter_projects_controlled_state_from_diagnosis_context() -> None:
    note = (
        "Diagnosis: Focal epilepsy. There has been significant improvement since "
        "increasing the dose of lamotrigine. The focal seizures are completely "
        "under control on the dose of lamotrigine 200 mg twice a day."
    )
    mentions = [
        MentionRecord(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={"Certainty": "5", "DiagCategory": "Epilepsy", "Negation": "Affirmed"},
            evidence="Focal epilepsy",
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
        and mention.text == "focal seizures"
        and mention.attributes.get("NumberOfSeizures") == "0"
        and mention.attributes.get("PointInTime") == "DrugChange"
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
        "projected_diagnosis_context_to_controlled_sf_state" in warning for warning in warnings
    )


def test_target_projection_quarantines_diagnosis_context_state_families_by_default() -> None:
    scenarios = [
        (
            "remote",
            (
                "Diagnosis: Symptomatic structural focal epilepsy. His last seizures "
                "were in his teenage years where he probably had around 3 or 4 focal "
                "to bilateral convulsive seizures."
            ),
            MentionRecord(
                entity="Diagnosis",
                text="focal epilepsy",
                attributes={
                    "Certainty": "5",
                    "DiagCategory": "Epilepsy",
                    "Negation": "Affirmed",
                },
                evidence="Symptomatic structural focal epilepsy",
            ),
            "projected_diagnosis_context_to_remote_last_seizures_state",
        ),
        (
            "controlled",
            (
                "Diagnosis: Focal epilepsy. There has been significant improvement since "
                "increasing the dose of lamotrigine. The focal seizures are completely "
                "under control on the dose of lamotrigine 200 mg twice a day."
            ),
            MentionRecord(
                entity="Diagnosis",
                text="focal epilepsy",
                attributes={
                    "Certainty": "5",
                    "DiagCategory": "Epilepsy",
                    "Negation": "Affirmed",
                },
                evidence="Focal epilepsy",
            ),
            "projected_diagnosis_context_to_controlled_sf_state",
        ),
        (
            "myoclonic",
            (
                "Diagnosis: generalised tonic clonic seizures with myoclonic jerks, "
                "possible JME. She also had very frequent myoclonic jerks."
            ),
            MentionRecord(
                entity="Diagnosis",
                text="generalised tonic clonic seizures with myoclonic jerks",
                attributes={
                    "Certainty": "5",
                    "DiagCategory": "MultipleSeizures",
                    "Negation": "Affirmed",
                },
                evidence="generalised tonic clonic seizures with myoclonic jerks",
            ),
            "projected_diagnosis_context_to_frequent_myoclonic_jerks",
        ),
    ]

    for _name, note, mention, family in scenarios:
        predicted, warnings = to_predicted_letter("EA1", [mention], note_text=note)

        assert not any(
            predicted_mention.entity == "SeizureFrequency"
            for predicted_mention in predicted.mentions
        )
        assert any(f"quarantined_projection_family: {family}" in warning for warning in warnings)


def test_target_single_call_adapter_projects_dropped_general_complex_sf_to_diagnosis() -> None:
    note = "Despite this she continues to get general and complex partial seizures."
    mentions = [
        MentionRecord(
            entity="SeizureFrequency",
            text="general and complex partial seizures",
            attributes={"FrequencyChange": "Frequent", "PointInTime": "Last_Week"},
            evidence="continues to get general and complex partial seizures",
        )
    ]

    predicted, warnings = to_predicted_letter("EA1", mentions, note_text=note)

    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].entity == "Diagnosis"
    assert predicted.mentions[0].text == "complex partial seizures"
    assert any("projected_dropped_sf_to_diagnosis" in warning for warning in warnings)
