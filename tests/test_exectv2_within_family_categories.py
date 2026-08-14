from scripts.build_exectv2_sf_split_decomposition import (
    letter_profile,
    same_type_multi_state,
)
from scripts.build_six_model_category_cut_performance import _score_exect_subtype
from scripts.exectv2_within_family_categories import (
    family_subtypes,
    mentions_for_subtype,
)


def _mention(entity: str, **attributes: str) -> dict:
    return {"entity": entity, "text": entity, "attributes": attributes}


def test_diagnosis_categories_follow_gold_diag_category() -> None:
    assert family_subtypes(
        _mention("Diagnosis", DiagCategory="MultipleSeizures")
    ) == ("multiple_seizures",)


def test_seizure_frequency_categories_distinguish_cadence_window_and_change() -> None:
    assert family_subtypes(
        _mention(
            "SeizureFrequency",
            NumberOfSeizures="2",
            NumberOfTimePeriods="1",
            TimePeriod="Month",
        )
    ) == ("numeric_cadence_rate",)
    assert family_subtypes(
        _mention(
            "SeizureFrequency",
            NumberOfSeizures="2",
            PointInTime="LastClinic",
        )
    ) == ("count_in_named_window",)
    assert family_subtypes(
        _mention("SeizureFrequency", FrequencyChange="Increased")
    ) == ("qualitative_frequency_change",)


def test_seizure_frequency_zero_count_is_seizure_free_not_a_rate() -> None:
    assert family_subtypes(
        _mention(
            "SeizureFrequency",
            NumberOfSeizures="0",
            TimePeriod="Year",
        )
    ) == ("seizure_free",)
    assert family_subtypes(
        _mention(
            "SeizureFrequency",
            LowerNumberOfSeizures="0",
            UpperNumberOfSeizures="3",
            TimePeriod="Month",
        )
    ) == ("numeric_cadence_rate",)


def test_sf_letter_profiles_are_gold_state_sets() -> None:
    assert letter_profile([]) == "empty"
    assert (
        letter_profile(
            [_mention("SeizureFrequency", NumberOfSeizures="2", TimePeriod="Month")]
        )
        == "active_rate_only"
    )
    assert (
        letter_profile([_mention("SeizureFrequency", FrequencyChange="Increased")])
        == "unknown_only"
    )
    assert (
        letter_profile(
            [
                _mention("SeizureFrequency", NumberOfSeizures="2", TimePeriod="Month"),
                _mention("SeizureFrequency", FrequencyChange="Increased"),
            ]
        )
        == "mixed"
    )


def test_sf_same_type_multi_state_requires_two_states_on_one_cui() -> None:
    shared = {"CUI": "C0036572"}
    assert same_type_multi_state(
        [
            _mention(
                "SeizureFrequency",
                NumberOfSeizures="2",
                TimePeriod="Month",
                **shared,
            ),
            _mention("SeizureFrequency", FrequencyChange="Increased", **shared),
        ]
    )
    assert not same_type_multi_state(
        [
            _mention(
                "SeizureFrequency",
                NumberOfSeizures="2",
                TimePeriod="Month",
                CUI="C0036572",
            ),
            _mention("SeizureFrequency", FrequencyChange="Increased", CUI="C0014544"),
        ]
    )


def test_prescription_categories_keep_rescue_separate_from_complete_regimens() -> None:
    assert family_subtypes(
        _mention(
            "Prescription",
            DrugName="midazolam",
            Frequency="As_Required",
        )
    ) == ("rescue_as_required",)
    assert family_subtypes(
        _mention(
            "Prescription",
            DrugName="lamotrigine",
            DrugDose="100",
            DoseUnit="mg",
            Frequency="2",
        )
    ) == ("complete_regimen",)


def test_investigation_categories_are_modality_and_result_specific() -> None:
    mention = _mention(
        "Investigations",
        MRI_Performed="Yes",
        MRI_Results="Normal",
        EEG_Performed="Yes",
        EEG_Results="Abnormal",
    )
    assert family_subtypes(mention) == ("eeg_abnormal", "mri_normal")

    mri = mentions_for_subtype([mention], "Investigations", "mri_normal")
    assert mri == [
        _mention(
            "Investigations",
            MRI_Performed="Yes",
            MRI_Results="Normal",
        )
    ]


def test_mentions_for_subtype_does_not_leak_other_family_subtypes() -> None:
    mentions = [
        _mention("Diagnosis", DiagCategory="Epilepsy"),
        _mention("Diagnosis", DiagCategory="SingleSeizure"),
        _mention("Prescription", DrugName="lamotrigine"),
    ]
    assert mentions_for_subtype(mentions, "Diagnosis", "epilepsy") == [mentions[0]]


def test_subtype_score_selects_by_gold_and_isolates_the_named_family() -> None:
    epilepsy = _mention("Diagnosis", DiagCategory="Epilepsy")
    single = _mention("Diagnosis", DiagCategory="SingleSeizure")
    rows = [
        {
            "letter_id": "EA_EPILEPSY",
            "gold_mentions": [epilepsy],
            "predicted_mentions": [
                epilepsy,
                _mention("Prescription", DrugName="lamotrigine"),
            ],
        },
        {
            "letter_id": "EA_SINGLE",
            "gold_mentions": [single],
            "predicted_mentions": [],
        },
    ]

    epilepsy_score = _score_exect_subtype(
        rows, family="Diagnosis", subtype="epilepsy", field="predicted_mentions"
    )
    single_score = _score_exect_subtype(
        rows,
        family="Diagnosis",
        subtype="single_seizure",
        field="predicted_mentions",
    )

    assert epilepsy_score["f1"] == 1.0
    assert single_score["f1"] == 0.0
    assert epilepsy_score["gold_mentions"] == 1
    assert single_score["gold_mentions"] == 1
    assert epilepsy_score["n_letters"] == 1
