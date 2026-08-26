"""Schema / format / post boundaries for ExECT mention stacks."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)

_NOTE = (
    "Diagnosis: epilepsy – unclassified. She takes Keppra 500 mgs twice daily "
    "and will start clobazam next week. MRI requested. "
    "She has two to three seizures per month."
)


def _mention(
    entity: str,
    text: str,
    *,
    attributes: dict[str, str] | None = None,
    evidence: str | None = None,
) -> PredictedMention:
    return PredictedMention(
        entity=entity,
        text=text,
        attributes=attributes or {},
        evidence=evidence if evidence is not None else text,
        confidence="high",
        rationale="fixture",
    )


def test_secondary_generalised_tonic_clonic_keeps_gold_cuiphrase() -> None:
    concept = diagnosis_concept("secondary generalised tonic clonic seizures")
    assert concept is not None
    assert concept.cui == "C0877017"
    assert concept.cui_phrase == "secondary-generalised-tonic-clonic-seizures"
    modern = diagnosis_concept("focal to bilateral convulsive seizures")
    assert modern is not None
    assert modern.cui == "C0877017"
    assert modern.cui_phrase == "focal-to-bilateral-convulsive-seizures"


def test_schema_keeps_written_findings_without_cui() -> None:
    mentions = [
        _mention(DIAGNOSIS.name, "epilepsy", attributes={"DiagCategory": "Epilepsy"}),
        _mention("PatientHistory", "ignored"),
    ]

    schema = structured.schema_mentions(mentions)

    assert [mention.entity for mention in schema] == [DIAGNOSIS.name]
    assert "CUI" not in schema[0].attributes


def test_format_respells_same_regimen_and_attaches_cui_without_drops() -> None:
    mentions = [
        _mention(
            DIAGNOSIS.name,
            "epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Diagnosis: epilepsy – unclassified",
        ),
        _mention(
            PRESCRIPTION.name,
            "Keppra 500 mgs twice daily",
            attributes={
                "DrugName": "Keppra",
                "DrugDose": "500",
                "DoseUnit": "mgs",
                "Frequency": "2",
            },
        ),
        _mention(
            PRESCRIPTION.name,
            "clobazam next week",
            attributes={"DrugName": "clobazam"},
            evidence="will start clobazam next week",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "seizures",
            attributes={"NumberOfSeizures": "2-3", "TimePeriod": "month"},
            evidence="two to three seizures per month",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "unlabelled events",
            attributes={"Negation": "Affirmed"},
            evidence="MRI requested",
        ),
        _mention(
            INVESTIGATIONS.name,
            "MRI",
            attributes={"MRI_Performed": "No", "EEG_Performed": "No"},
            evidence="MRI requested",
        ),
        _mention(
            DIAGNOSIS.name,
            "not in note",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="this evidence is absent",
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(mentions, _NOTE)
    texts = [mention.text for mention in formatted]
    rx = next(
        mention
        for mention in formatted
        if mention.entity == PRESCRIPTION.name
        and mention.attributes.get("DrugName") == "levetiracetam"
    )
    dx = next(
        mention
        for mention in formatted
        if mention.entity == DIAGNOSIS.name and mention.text == "epilepsy"
    )
    sf = next(
        mention
        for mention in formatted
        if mention.entity == SEIZURE_FREQUENCY.name and mention.text == "seizures"
    )
    inv = next(mention for mention in formatted if mention.entity == INVESTIGATIONS.name)

    assert "clobazam next week" in texts
    assert "unlabelled events" in texts
    assert "not in note" in texts
    assert dx.text == "epilepsy"
    assert dx.attributes.get("CUI") == "C0014544"
    assert rx.text == "levetiracetam"
    assert rx.attributes["DrugName"] == "levetiracetam"
    assert rx.attributes["DoseUnit"] == "mg"
    assert sf.attributes.get("LowerNumberOfSeizures") == "2"
    assert sf.attributes.get("UpperNumberOfSeizures") == "3"
    assert "EEG_Performed" not in inv.attributes


def test_live_gate_still_drops_ungrounded_and_no_state_findings() -> None:
    mentions = [
        _mention(
            DIAGNOSIS.name,
            "not in note",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="this evidence is absent",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "unlabelled events",
            attributes={"Negation": "Affirmed"},
            evidence="MRI requested",
        ),
        _mention(
            PRESCRIPTION.name,
            "Keppra 500 mgs twice daily",
            attributes={
                "DrugName": "Keppra",
                "DrugDose": "500",
                "DoseUnit": "mgs",
                "Frequency": "2",
            },
        ),
    ]

    letter, warnings = structured.to_predicted_letter(
        "TEST001", mentions, note_text=_NOTE
    )

    assert [mention.entity for mention in letter.mentions] == [PRESCRIPTION.name]
    assert any("dropped_evidence_not_substring" in warning for warning in warnings)
    assert any("dropped_no_frequency_state_rendering" in warning for warning in warnings)


def test_format_does_not_complete_focal_from_a_seizure_type_cue() -> None:
    formatted, _warnings = structured.apply_format_stack(
        [
            _mention(
                DIAGNOSIS.name,
                "focal",
                attributes={"DiagCategory": "Epilepsy"},
                evidence="She continues to have focal seizures.",
            )
        ],
        "She continues to have focal seizures.",
    )

    assert formatted[0].text == "focal"


def test_format_writes_diagnosis_standard_name_without_semantic_remap() -> None:
    mentions = [
        _mention(
            DIAGNOSIS.name,
            "TLE",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Diagnosis: probable TLE",
        ),
        _mention(
            DIAGNOSIS.name,
            "Symptomatic structural epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Diagnosis: symptomatic structural epilepsy",
        ),
        _mention(
            DIAGNOSIS.name,
            "focal cortical dysplasia",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="MRI showed focal cortical dysplasia",
        ),
        _mention(
            DIAGNOSIS.name,
            "focal",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Diagnosis: epilepsy – probable focal",
        ),
        _mention(
            DIAGNOSIS.name,
            "complex partial",
            attributes={"DiagCategory": "MultipleSeizures"},
        ),
        _mention(
            DIAGNOSIS.name,
            "GTCS",
            attributes={"DiagCategory": "MultipleSeizures"},
        ),
        _mention(
            DIAGNOSIS.name,
            "absences",
            attributes={"DiagCategory": "MultipleSeizures"},
        ),
        _mention(
            DIAGNOSIS.name,
            "Nocturnal generalised tonic clonic seizures",
            attributes={"DiagCategory": "MultipleSeizures"},
        ),
        _mention(
            DIAGNOSIS.name,
            "focal (occipital lobe) epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert [mention.text for mention in formatted] == [
        "temporal lobe epilepsy",
        "symptomatic structural focal epilepsy",
        "focal cortical dysplasia",
        "focal epilepsy",
        "complex partial seizures",
        "generalised tonic clonic seizures",
        "absence seizures",
        "generalised tonic clonic seizures",
        "occipital lobe epilepsy",
    ]
    assert formatted[0].evidence == "Diagnosis: probable TLE"
    assert formatted[0].attributes["CUI"] == "C0014556"
    assert formatted[1].attributes["CUI"] == "C0472349"
    assert "Certainty" not in formatted[1].attributes
    assert "CUI" not in formatted[2].attributes
    assert formatted[5].attributes["DiagCategory"] == "MultipleSeizures"


def test_format_does_not_apply_a_sibling_diagnosis_qualifier() -> None:
    mention = _mention(
        DIAGNOSIS.name,
        "generalised epilepsy",
        attributes={"DiagCategory": "Epilepsy"},
        evidence=(
            "Diagnosis: generalised epilepsy and symptomatic structural temporal "
            "lobe epilepsy"
        ),
    )

    formatted, _warnings = structured.apply_format_stack([mention], mention.evidence)

    assert formatted[0].text == "generalised epilepsy"


def test_format_repairs_residual_same_fact_diagnosis_names() -> None:
    mentions = [
        _mention(
            DIAGNOSIS.name,
            "secondarily generalised seizures",
            attributes={"DiagCategory": "MultipleSeizures"},
        ),
        _mention(
            DIAGNOSIS.name,
            "focal dyscognitive seizures",
            attributes={"DiagCategory": "MultipleSeizures"},
        ),
        _mention(
            DIAGNOSIS.name,
            "focal epileptic seizures",
            attributes={"DiagCategory": "MultipleSeizures"},
        ),
        _mention(
            DIAGNOSIS.name,
            "Simple partial seizures with occasional secondary generalisation",
            attributes={"DiagCategory": "MultipleSeizures"},
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert [mention.text for mention in formatted] == [
        "secondary generalised seizures",
        "dyscognitive seizures",
        "focal seizures",
        "Simple partial seizures with secondary generalisation",
    ]
    assert all(
        mention.attributes["DiagCategory"] == "MultipleSeizures"
        for mention in formatted
    )

    single, _warnings = structured.apply_format_stack(
        [
            _mention(
                DIAGNOSIS.name,
                "secondarily generalised seizures",
                attributes={"DiagCategory": "Epilepsy"},
                evidence="She has only ever had one secondarily generalised seizure.",
            )
        ],
        "She has only ever had one secondarily generalised seizure.",
    )
    assert single[0].text == "secondarily generalised seizures"
    assert single[0].attributes["DiagCategory"] == "Epilepsy"

    rewritten, _warnings = structured.apply_format_stack(
        [
            _mention(
                DIAGNOSIS.name,
                "secondarily generalised seizures",
                attributes={"DiagCategory": "Epilepsy"},
            )
        ],
        "She continues to have secondarily generalised seizures.",
    )
    assert rewritten[0].text == "secondary generalised seizures"
    assert rewritten[0].attributes["DiagCategory"] == "MultipleSeizures"


def test_format_does_not_overwrite_diagnosis_from_a_local_qualifier() -> None:
    mentions = [
        _mention(
            DIAGNOSIS.name,
            "focal epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Diagnosis: focal epilepsy - probable temporal",
        ),
        _mention(
            DIAGNOSIS.name,
            "symptomatic structural focal epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
            evidence=(
                "He has symptomatic structural temporal lobe epilepsy caused by "
                "previous encephalitis."
            ),
        ),
        _mention(
            DIAGNOSIS.name,
            "epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Diagnosis: epilepsy, probably generalised",
        ),
        _mention(
            DIAGNOSIS.name,
            "focal epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Focal epilepsy ? right temporal lobe onset",
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert [mention.text for mention in formatted] == [
        "focal epilepsy",
        "symptomatic structural focal epilepsy",
        "epilepsy",
        "focal epilepsy",
    ]


def test_format_canonicalizes_an_already_named_lobe_syndrome() -> None:
    formatted, _warnings = structured.apply_format_stack(
        [
            _mention(
                DIAGNOSIS.name,
                "symptomatic structural temporal lobe epilepsy",
                attributes={"DiagCategory": "Epilepsy"},
            )
        ],
        "symptomatic structural temporal lobe epilepsy",
    )

    assert formatted[0].text == "temporal lobe epilepsy"


def test_format_prefers_mention_local_cadence_over_sibling_rescue_scope() -> None:
    evidence = (
        "He is taking levetiracetam 1500mg bd as well as lamotrigine 200mg bd "
        "and clobazam for seizure clusters."
    )
    mentions = [
        _mention(
            PRESCRIPTION.name,
            "levetiracetam 1500mg bd",
            attributes={
                "DrugName": "levetiracetam",
                "DrugDose": "1500",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence=evidence,
        ),
        _mention(
            PRESCRIPTION.name,
            "lamotrigine 200mg bd",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "200",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence=evidence,
        ),
        _mention(
            PRESCRIPTION.name,
            "clobazam",
            attributes={"DrugName": "clobazam"},
            evidence=evidence,
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(mentions, evidence)

    assert [mention.attributes["Frequency"] for mention in formatted] == [
        "2",
        "2",
        "As_Required",
    ]


def test_format_preserves_local_rescue_and_future_cues_in_prescription_text() -> None:
    mentions = [
        _mention(
            PRESCRIPTION.name,
            "Clobazam 10-20mg bd",
            attributes={
                "DrugName": "Clobazam",
                "DrugDose": "10-20mg",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence="Clobazam 10-20mg bd for seizure clusters",
        ),
        _mention(
            PRESCRIPTION.name,
            "Midazolam as per rescue plan",
            attributes={"DrugName": "Midazolam", "Frequency": "As_Required"},
        ),
        _mention(
            PRESCRIPTION.name,
            "Please start sodium valproate 300mg once a day",
            attributes={
                "DrugName": "sodium valproate",
                "DrugDose": "300",
                "DoseUnit": "mg",
                "Frequency": "1",
            },
        ),
        _mention(
            PRESCRIPTION.name,
            "75mg twice a day",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "75",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
            evidence=(
                "Please prescribe lamotrigine starting at 25mg once a day and "
                "increase to 75mg twice a day."
            ),
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert formatted[0].attributes["Frequency"] == "As_Required"
    assert formatted[0].text == "Clobazam 10-20mg bd"
    assert formatted[1].text == "Midazolam as per rescue plan"
    assert formatted[2].text == "Please start sodium valproate 300mg once a day"
    assert formatted[3].text == "75mg twice a day"


def test_format_repairs_single_explicit_dose_but_not_multi_dose_text() -> None:
    mentions = [
        _mention(
            PRESCRIPTION.name,
            "Zonisamide 150 mg BD",
            attributes={
                "DrugName": "Zonisamide",
                "DrugDose": "1500",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        _mention(
            PRESCRIPTION.name,
            "lamotrigine 50 mg increasing to 75 mg",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "50",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        _mention(
            PRESCRIPTION.name,
            "Clobazam 10-20mg bd for seizure clusters",
            attributes={
                "DrugName": "clobazam",
                "DoseUnit": "mg",
                "Frequency": "As_Required",
            },
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert formatted[0].attributes["DrugDose"] == "150"
    assert formatted[0].attributes["DoseUnit"] == "mg"
    assert formatted[1].attributes["DrugDose"] == "50"
    assert formatted[2].attributes["Frequency"] == "As_Required"
    assert "DrugDose" not in formatted[2].attributes


def test_format_strips_aed_dosage_form_without_changing_regimen_slots() -> None:
    mention = _mention(
        PRESCRIPTION.name,
        "Carbamazepine Controlled Release 400mgs bd",
        attributes={
            "DrugName": "Carbamazepine Controlled Release",
            "DrugDose": "400",
            "DoseUnit": "mgs",
            "Frequency": "2",
        },
    )

    formatted, _warnings = structured.apply_format_stack([mention], mention.evidence)

    assert formatted[0].text == "carbamazepine"
    assert formatted[0].attributes == {
        "DrugName": "carbamazepine",
        "DrugDose": "400",
        "DoseUnit": "mg",
        "Frequency": "2",
        "CUI": "C0006949",
        "CUIPhrase": "carbamazepine",
    }


def test_format_explicit_abnormal_investigation_cue_beats_otherwise_normal() -> None:
    mentions = [
        _mention(
            INVESTIGATIONS.name,
            "EEG",
            attributes={"EEG_Performed": "Yes", "EEG_Results": "Normal"},
            evidence=(
                "Her EEG showed some minor temporal slowing but otherwise was "
                "reported as normal."
            ),
        ),
        _mention(
            INVESTIGATIONS.name,
            "sleep deprived EEG",
            attributes={"EEG_Performed": "Yes", "EEG_Results": "Normal"},
            evidence="Her sleep deprived EEG did not show any epileptic activity.",
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert [mention.attributes["EEG_Results"] for mention in formatted] == [
        "Abnormal",
        "Normal",
    ]


def test_format_investigation_result_is_modality_local_and_negation_aware() -> None:
    shared = (
        "She had a normal MRI last year and previously an abnormal EEG with "
        "generalised spike and wave abnormalities."
    )
    mentions = [
        _mention(
            INVESTIGATIONS.name,
            "MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
            evidence=shared,
        ),
        _mention(
            INVESTIGATIONS.name,
            "EEG",
            attributes={"EEG_Performed": "Yes", "EEG_Results": "Normal"},
            evidence=shared,
        ),
        _mention(
            INVESTIGATIONS.name,
            "video EEG",
            attributes={"EEG_Performed": "Yes", "EEG_Results": "Normal"},
            evidence="The video EEG showed no epileptiform EEG correlate.",
        ),
        _mention(
            INVESTIGATIONS.name,
            "CT head",
            attributes={"CT_Performed": "Yes", "CT_Results": "Normal"},
            evidence="The CT head did not identify any acute pathology.",
        ),
        _mention(
            INVESTIGATIONS.name,
            "CT head",
            attributes={"CT_Performed": "Yes", "CT_Results": "Normal"},
            evidence="MRI showed a lesion; CT head was normal.",
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert formatted[0].attributes["MRI_Results"] == "Normal"
    assert formatted[1].attributes["EEG_Results"] == "Abnormal"
    assert formatted[2].attributes["EEG_Results"] == "Normal"
    assert formatted[3].attributes["CT_Results"] == "Normal"
    assert formatted[4].attributes["CT_Results"] == "Normal"


def test_format_writes_seizure_frequency_standard_names() -> None:
    mentions = [
        _mention(
            SEIZURE_FREQUENCY.name,
            "tonic clonic",
            attributes={"NumberOfSeizures": "0"},
            evidence="seven years without any tonic clonic seizures",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "episode",
            attributes={"NumberOfSeizures": "1"},
            evidence="his last episode was two weeks ago",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "dissociative episode",
            attributes={"NumberOfSeizures": "1"},
            evidence="one dissociative episode",
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert [mention.text for mention in formatted] == [
        "generalised tonic clonic seizures",
        "seizures",
        "dissociative episode",
    ]
    assert formatted[0].attributes["CUI"] == "C0494475"
    assert formatted[1].attributes["CUI"] == "C0036572"
    assert "CUI" not in formatted[2].attributes


def test_format_does_not_retarget_sf_type_or_invent_a_lower_bound() -> None:
    mentions = [
        _mention(
            SEIZURE_FREQUENCY.name,
            "seizure",
            attributes={"NumberOfSeizures": "1"},
            evidence="She had a recent generalised tonic chronic seizure at home.",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "absences",
            attributes={"FrequencyChange": "Increased"},
            evidence=(
                "He has had three generalised tonic clonic seizures and more of "
                "his typical absences since clinic."
            ),
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "generalised tonic clonic seizures",
            attributes={"PointInTime": "LastClinic"},
            evidence=(
                "He has had further generalised tonic clonic seizures since I "
                "last saw him."
            ),
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert [mention.text for mention in formatted] == [
        "seizures",
        "absences",
        "generalised tonic clonic seizures",
    ]
    assert "LowerNumberOfSeizures" not in formatted[2].attributes


def test_format_writes_explicit_seizure_free_as_the_closed_zero_name() -> None:
    mentions = [
        _mention(
            SEIZURE_FREQUENCY.name,
            "seizure",
            attributes={"NumberOfSeizures": "0"},
            evidence="She has remained seizure free since July.",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "seizure",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence=(
                "He remains seizure free. His last seizure was in November 2015."
            ),
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert [mention.text for mention in formatted] == ["seizure free", "seizures"]


def test_format_does_not_retarget_generic_sf_when_evidence_names_multiple_types() -> None:
    evidence = "She has focal seizures and generalised tonic clonic seizures every month."
    mention = _mention(
        SEIZURE_FREQUENCY.name,
        "seizures",
        attributes={"NumberOfSeizures": "3", "TimePeriod": "Month"},
        evidence=evidence,
    )

    formatted, _warnings = structured.apply_format_stack([mention], evidence)

    assert formatted[0].text == "seizures"


def test_format_does_not_retarget_uncertain_or_remote_generic_sf_type() -> None:
    mentions = [
        _mention(
            SEIZURE_FREQUENCY.name,
            "seizures",
            attributes={"NumberOfSeizures": "1", "TimePeriod": "Month"},
            evidence="Seizures every month, possibly focal onset.",
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "seizures",
            attributes={"NumberOfSeizures": "0", "TimeSince_or_TimeOfEvent": "Since"},
            evidence=(
                "His last seizures were in his teens, when he had focal to "
                "bilateral convulsive seizures."
            ),
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions, "\n".join(mention.evidence for mention in mentions)
    )

    assert [mention.text for mention in formatted] == ["seizures", "seizures"]


def test_new_encode_rule_families_are_independently_stoppable() -> None:
    mentions = [
        _mention(
            DIAGNOSIS.name,
            "TLE",
            attributes={"DiagCategory": "Epilepsy"},
        ),
        _mention(
            PRESCRIPTION.name,
            "Zonisamide 150 mg BD",
            attributes={
                "DrugName": "Zonisamide",
                "DrugDose": "1500",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        _mention(
            SEIZURE_FREQUENCY.name,
            "tonic clonic",
            attributes={"NumberOfSeizures": "0"},
        ),
    ]

    formatted, _warnings = structured.apply_format_stack(
        mentions,
        "\n".join(mention.evidence for mention in mentions),
        enabled_rules=frozenset(),
    )

    assert [mention.text for mention in formatted] == [
        "TLE",
        "Zonisamide 150 mg BD",
        "tonic clonic",
    ]
    assert formatted[1].attributes["DrugDose"] == "1500"
