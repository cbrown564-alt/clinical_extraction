"""Tests for the first ExECTv2 deterministic all-entity baseline."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    BIRTH_HISTORY,
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    ONSET,
    PATIENT_HISTORY,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
    WHEN_DIAGNOSED,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.validate import (
    validate_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    ACTIVE_DETERMINISTIC_ENTITIES,
    extract_deterministic_all9,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_overall,
    semantic_config_for,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _letter() -> ExectLetter:
    text = (
        "Diagnosis: focal epilepsy. EEG was abnormal. MRI brain was normal. "
        "Her epilepsy started at the age of 4. "
        "She was diagnosed with epilepsy at the age of 4. "
        "Birth history: she was born normally. "
        "The epilepsy is secondary to Tuberous sclerosis. "
        "Past medical history includes depression and migraine. "
        "There is no history of febrile convulsions. "
        "Current medication: Lamotrigine 150mg bd and levetiracetam 500 mg od. "
        "Seizure type and frequency: focal seizures 2 per month."
    )
    return ExectLetter("DALL9-001", text)


def test_extract_deterministic_all9_emits_active_structured_entities_and_sf() -> None:
    letter = _letter()
    prediction = extract_deterministic_all9(letter)

    entities = {mention.entity for mention in prediction.mentions}
    assert {
        DIAGNOSIS.name,
        EPILEPSY_CAUSE.name,
        INVESTIGATIONS.name,
        ONSET.name,
        PRESCRIPTION.name,
        PATIENT_HISTORY.name,
        WHEN_DIAGNOSED.name,
        BIRTH_HISTORY.name,
        SEIZURE_FREQUENCY.name,
    } <= entities
    assert prediction.diagnostics["architecture_track"] == "rules_only"
    assert set(prediction.diagnostics["active_entities"]) == set(ACTIVE_DETERMINISTIC_ENTITIES)

    validation = validate_letter(prediction, source_text=letter.note_text)
    assert validation.ok
    assert not [issue for issue in validation.issues if issue.code == "evidence_not_substring"]


def test_structured_mentions_carry_rule_taxonomy_and_benchmark_cui() -> None:
    prediction = extract_deterministic_all9(_letter())
    by_entity = {}
    for mention in prediction.mentions:
        by_entity.setdefault(mention.entity, []).append(mention)

    diagnosis = by_entity[DIAGNOSIS.name][0]
    assert diagnosis.text == "focal epilepsy"
    assert diagnosis.attributes["DiagCategory"] == "Epilepsy"
    assert diagnosis.attributes["CUI"] == "C0014547"
    assert "deterministic_diagnosis" in diagnosis.component_owner

    eeg = next(m for m in by_entity[INVESTIGATIONS.name] if m.text == "EEG")
    assert eeg.attributes["EEG_Performed"] == "Yes"
    assert eeg.attributes["EEG_Results"] == "Abnormal"
    assert eeg.attributes["CUI"] == "C0151611"
    assert "clinical_epilepsy" in eeg.component_owner

    onset = by_entity[ONSET.name][0]
    assert onset.text == "epilepsy"
    assert onset.attributes["Age"] == "4"
    assert onset.attributes["AgeUnit"] == "Year"
    assert onset.attributes["Certainty"] == "5"
    assert onset.attributes["Negation"] == "Affirmed"
    assert onset.attributes["CUI"] == "C0014544"
    assert "onset_epilepsy_age" in onset.component_owner

    when_diagnosed = by_entity[WHEN_DIAGNOSED.name][0]
    assert when_diagnosed.text == "epileps"
    assert when_diagnosed.attributes["Age"] == "4"
    assert when_diagnosed.attributes["AgeUnit"] == "Year"
    assert when_diagnosed.attributes["CUI"] == "C0014544"
    assert "benchmark_format" in when_diagnosed.component_owner

    birth_history = by_entity[BIRTH_HISTORY.name][0]
    assert birth_history.text == "born-normally"
    assert birth_history.attributes["Certainty"] == "5"
    assert birth_history.attributes["Negation"] == "Affirmed"
    assert birth_history.attributes["CUI"] == "C3665337"
    assert "birth_history" in birth_history.component_owner

    cause = by_entity[EPILEPSY_CAUSE.name][0]
    assert cause.text == "Tuberous-sclerosis"
    assert cause.attributes["Certainty"] == "5"
    assert cause.attributes["Negation"] == "Affirmed"
    assert cause.attributes["CUI"] == "C0041341"
    assert "epilepsy_cause" in cause.component_owner

    patient_history = by_entity[PATIENT_HISTORY.name]
    depression = next(m for m in patient_history if m.text == "depression")
    assert depression.attributes["Certainty"] == "5"
    assert depression.attributes["Negation"] == "Affirmed"
    assert depression.attributes["CUI"] == "C0011570"
    assert "patient_history" in depression.component_owner

    febrile = next(m for m in patient_history if m.text == "febrile-convulsions")
    assert febrile.attributes["Certainty"] == "1"
    assert febrile.attributes["Negation"] == "Negated"
    assert febrile.attributes["CUI"] == "C0009952"

    lamotrigine = next(m for m in by_entity[PRESCRIPTION.name] if m.text == "Lamotrigine 150mg bd")
    assert lamotrigine.attributes["DrugName"] == "lamotrigine"
    assert lamotrigine.attributes["DrugDose"] == "150"
    assert lamotrigine.attributes["DoseUnit"] == "mg"
    assert lamotrigine.attributes["Frequency"] == "2"
    assert lamotrigine.attributes["CUI"] == "C0064636"
    assert "benchmark_format" in lamotrigine.component_owner


def test_deterministic_all9_scores_tiny_active_entity_gold() -> None:
    letter = _letter()
    gold = ExectLetter(
        letter.letter_id,
        letter.note_text,
        (
            _ann(
                DIAGNOSIS.name,
                "focal epilepsy",
                DiagCategory="Epilepsy",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0014547",
                CUIPhrase="focal epilepsy",
            ),
            _ann(
                DIAGNOSIS.name,
                "epilepsy",
                DiagCategory="Epilepsy",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0014544",
                CUIPhrase="epilepsy",
            ),
            _ann(
                DIAGNOSIS.name,
                "focal seizures",
                DiagCategory="Epilepsy",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0751495",
                CUIPhrase="focal-seizures",
            ),
            _ann(
                INVESTIGATIONS.name,
                "EEG",
                EEG_Performed="Yes",
                EEG_Results="Abnormal",
                CUI="C0151611",
                CUIPhrase="eeg abnormal",
            ),
            _ann(
                INVESTIGATIONS.name,
                "MRI",
                MRI_Performed="Yes",
                MRI_Results="Normal",
                CUI="C0436481",
                CUIPhrase="mri normal",
            ),
            _ann(
                ONSET.name,
                "epilepsy",
                Age="4",
                AgeUnit="Year",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0014544",
                CUIPhrase="epilepsy",
            ),
            _ann(
                WHEN_DIAGNOSED.name,
                "epileps",
                Age="4",
                AgeUnit="Year",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0014544",
                CUIPhrase="epilepsy",
            ),
            _ann(
                BIRTH_HISTORY.name,
                "born-normally",
                Certainty="5",
                Negation="Affirmed",
                CUI="C3665337",
                CUIPhrase="born-normally",
            ),
            _ann(
                EPILEPSY_CAUSE.name,
                "Tuberous-sclerosis",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0041341",
                CUIPhrase="Tuberous-sclerosis",
            ),
            _ann(
                PATIENT_HISTORY.name,
                "depression",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0011570",
                CUIPhrase="depression",
            ),
            _ann(
                PATIENT_HISTORY.name,
                "migraine",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0149931",
                CUIPhrase="migraine",
            ),
            _ann(
                PATIENT_HISTORY.name,
                "febrile-convulsions",
                Certainty="1",
                Negation="Negated",
                CUI="C0009952",
                CUIPhrase="febrile-convulsions",
            ),
            _ann(
                PRESCRIPTION.name,
                "Lamotrigine 150mg bd",
                DrugName="lamotrigine",
                DrugDose="150",
                DoseUnit="mg",
                Frequency="2",
                CUI="C0064636",
                CUIPhrase="lamotrigine",
            ),
            _ann(
                PRESCRIPTION.name,
                "levetiracetam 500 mg od",
                DrugName="levetiracetam",
                DrugDose="500",
                DoseUnit="mg",
                Frequency="1",
                CUI="C0037567",
                CUIPhrase="levetiracetam",
            ),
            _ann(
                SEIZURE_FREQUENCY.name,
                "focal seizures",
                NumberOfSeizures="2",
                NumberOfTimePeriods="1",
                TimePeriod="Month",
                CUI="C0751495",
                CUIPhrase="focal seizures",
            ),
        ),
    )

    predicted = extract_deterministic_all9(letter)
    adapted = to_exect_letter(predicted, note_text=letter.note_text)
    score = score_overall(
        [gold],
        [adapted],
        ACTIVE_DETERMINISTIC_ENTITIES,
        semantic_config_for,
    )

    assert score.per_item.f1 == 1.0
    assert score.per_letter.f1 == 1.0


def test_onset_and_when_diagnosed_extract_multiple_temporal_entities() -> None:
    letter = ExectLetter(
        "DALL9-MULTI",
        (
            "Her epilepsy started at the age of fourteen. "
            "She was diagnosed with epilepsy at the age of eighteen."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    onsets = [mention for mention in prediction.mentions if mention.entity == ONSET.name]
    when_diagnosed = [
        mention for mention in prediction.mentions if mention.entity == WHEN_DIAGNOSED.name
    ]

    assert len(onsets) == 1
    assert onsets[0].attributes["Age"] == "14"
    assert len(when_diagnosed) == 1
    assert when_diagnosed[0].attributes["Age"] == "18"


def test_prescription_extracts_current_regimen_after_previous_trials() -> None:
    letter = ExectLetter(
        "PRESC-CURRENT-AFTER-TRIALS",
        (
            "He has previously tried topiramate and phenytoin and he is currently "
            "taking levetiracetam 1250mg twice a day and carbamazepine 400mg "
            "twice a day."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    assert {
        (
            m.attributes["DrugName"],
            m.attributes["DrugDose"],
            m.attributes["DoseUnit"],
            m.attributes["Frequency"],
        )
        for m in prescriptions
    } == {
        ("levetiracetam", "1250", "mg", "2"),
        ("carbamazepine", "400", "mg", "2"),
    }


def test_patient_history_keeps_distinct_occurrences_diagnosis_collapses_prose() -> None:
    text = (
        "Past medical history includes diabetes and depression. "
        "She has epilepsy. Her epilepsy is well controlled. The epilepsy diagnosis stands. "
        "On a background of diabetes, she remains stable."
    )
    letter = ExectLetter(letter_id="DUP1", note_text=text)

    prediction = extract_deterministic_all9(letter)
    diabetes = [
        m for m in prediction.mentions if m.entity == PATIENT_HISTORY.name and m.text == "diabetes"
    ]
    epilepsy = [
        m
        for m in prediction.mentions
        if m.entity == DIAGNOSIS.name and m.text.lower() == "epilepsy"
    ]

    assert len(diabetes) == 2
    spans = [m.evidence_span for m in diabetes]
    assert all(span is not None for span in spans)
    starts = {span.start_char for span in spans if span is not None}
    assert len(starts) == 2
    assert all(
        span is not None
        and span.start_char is not None
        and span.end_char is not None
        and text[span.start_char : span.end_char] == span.text
        for span in spans
    )
    assert len(epilepsy) == 1
