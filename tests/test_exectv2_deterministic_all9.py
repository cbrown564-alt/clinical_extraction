"""Tests for the first ExECTv2 deterministic all-entity baseline."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.validate import (
    validate_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    ACTIVE_DETERMINISTIC_ENTITIES,
    extract_deterministic_all9,
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    deterministic_all9_scorecard,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_overall,
    score_prescription_components,
    semantic_config_for,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _letter() -> ExectLetter:
    text = (
        "Diagnosis: focal epilepsy. EEG was abnormal. MRI brain was normal. "
        "Current medication: Lamotrigine 150mg bd and levetiracetam 500 mg od. "
        "Seizure type and frequency: focal seizures 2 per month."
    )
    return ExectLetter("DALL9-001", text)


def test_extract_deterministic_all9_emits_active_structured_entities_and_sf() -> None:
    letter = _letter()
    prediction = extract_deterministic_all9(letter)

    entities = {mention.entity for mention in prediction.mentions}
    assert {DIAGNOSIS.name, INVESTIGATIONS.name, PRESCRIPTION.name, SEIZURE_FREQUENCY} <= entities
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
                SEIZURE_FREQUENCY,
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


def test_deterministic_all9_scorecard_reports_prescription_projection_ladder() -> None:
    letter = _letter()
    gold = ExectLetter(
        letter.letter_id,
        letter.note_text,
        (
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
                CUI="C0377265",
                CUIPhrase="levetiracetam",
            ),
        ),
    )

    scorecard = deterministic_all9_scorecard.build_scorecard(
        [gold],
        [extract_deterministic_all9(letter)],
    )

    projection = scorecard["prescription_benchmark_projection_scores"]
    assert set(projection) == {
        "phrase_scope",
        "semantic_without_cui",
        "benchmark_with_cui",
        "clinical_medication_identity",
        "drugname_cui_projection",
        "source_stated_frequency",
        "guideline_defaulted_frequency",
    }
    assert projection["clinical_medication_identity"]["f1"] == 1.0


def test_run_all9_on_letters_preserves_order() -> None:
    letters = [_letter(), ExectLetter("DALL9-002", "No epilepsy-related content.")]
    predictions = run_all9_on_letters(letters)

    assert [prediction.letter_id for prediction in predictions] == [
        "DALL9-001",
        "DALL9-002",
    ]


def test_dev_split_all9_predictions_are_schema_clean() -> None:
    letters = load_letters_for_split("dev")
    predictions = run_all9_on_letters(letters)

    errors = []
    for letter, prediction in zip(letters, predictions, strict=True):
        result = validate_letter(prediction, source_text=letter.note_text)
        errors.extend(
            (letter.letter_id, issue.code, issue.message)
            for issue in result.issues
            if issue.severity == "error"
        )

    assert errors == []


def test_dev_split_prescription_component_scores_clear_goal_threshold() -> None:
    letters = load_letters_for_split("dev")
    predictions = run_all9_on_letters(letters)
    adapted = [
        to_exect_letter(prediction, note_text=letter.note_text)
        for prediction, letter in zip(predictions, letters, strict=True)
    ]

    score = score_prescription_components(letters, adapted)

    assert score.name.f1 >= 0.9
    assert score.dose.f1 >= 0.9
    assert score.frequency.f1 >= 0.9
    assert score.complete.f1 >= 0.9
