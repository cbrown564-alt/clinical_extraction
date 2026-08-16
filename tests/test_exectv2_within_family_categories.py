"""Exemplars for ExECT within-family category keys."""

from scripts.exectv2_within_family_categories import family_subtypes


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
        _mention("SeizureFrequency", FrequencyChange="Increased")
    ) == ("qualitative_frequency_change",)
    assert family_subtypes(
        _mention("SeizureFrequency", NumberOfSeizures="0", TimePeriod="Year")
    ) == ("seizure_free",)


def test_prescription_categories_keep_rescue_separate_from_complete_regimens() -> None:
    assert family_subtypes(
        _mention("Prescription", DrugName="midazolam", Frequency="As_Required")
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
