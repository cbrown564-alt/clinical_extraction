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
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    ACTIVE_DETERMINISTIC_ENTITIES,
    extract_deterministic_all9,
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    clinical_recovery_scorecard,
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


def test_onset_engine_extracts_age_and_relative_duration_forms() -> None:
    letter = ExectLetter(
        "DALL9-ONSET",
        (
            "Her epilepsy started at the age of fourteen. "
            "His epilepsy started around 10 years ago after surgery."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    onsets = [mention for mention in prediction.mentions if mention.entity == ONSET.name]

    assert [mention.text for mention in onsets] == ["epilepsy", "epilepsy"]
    assert onsets[0].attributes == {
        "Age": "14",
        "AgeUnit": "Year",
        "Certainty": "5",
        "Negation": "Affirmed",
        "CUI": "C0014544",
        "CUIPhrase": "epilepsy",
    }
    assert onsets[1].attributes == {
        "NumberOfTimePeriods": "10",
        "TimePeriod": "Year",
        "Certainty": "5",
        "Negation": "Affirmed",
        "CUI": "C0014544",
        "CUIPhrase": "epilepsy",
    }


def test_when_diagnosed_engine_extracts_age_duration_and_date_forms() -> None:
    letter = ExectLetter(
        "DALL9-WDX",
        (
            "She was diagnosed with epilepsy at the age of eighteen. "
            "The diagnosis of epilepsy was made approximately 6 years ago. "
            "His epilepsy was diagnosed in May 2017."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    mentions = [m for m in prediction.mentions if m.entity == WHEN_DIAGNOSED.name]

    assert [mention.text for mention in mentions] == ["epileps", "epileps", "epileps"]
    assert mentions[0].attributes == {
        "Age": "18",
        "AgeUnit": "Year",
        "Certainty": "5",
        "Negation": "Affirmed",
        "CUI": "C0014544",
        "CUIPhrase": "epilepsy",
    }
    assert mentions[1].attributes == {
        "NumberOfTimePeriods": "6",
        "TimePeriod": "Year",
        "Certainty": "5",
        "Negation": "Affirmed",
        "CUI": "C0014544",
        "CUIPhrase": "epilepsy",
    }
    assert mentions[2].attributes == {
        "MonthDate": "5",
        "YearDate": "2017",
        "Certainty": "5",
        "Negation": "Affirmed",
        "CUI": "C0014544",
        "CUIPhrase": "epilepsy",
    }


def test_birth_history_and_epilepsy_cause_engines_use_explicit_lexicons() -> None:
    letter = ExectLetter(
        "DALL9-BH-CAUSE",
        (
            "Birth history: he was born slightly premature at 35 weeks. "
            "His epilepsy is secondary to previous cerebral abcess. "
            "The cause of his epilepsy was a significant traumatic brain injury in 2006."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    birth_history = [m for m in prediction.mentions if m.entity == BIRTH_HISTORY.name]
    causes = [m for m in prediction.mentions if m.entity == EPILEPSY_CAUSE.name]

    assert birth_history[0].text == "born-slightly-premature"
    assert birth_history[0].attributes["PrematureBirth"] == "34to<37_LatePretermBirth"
    assert birth_history[0].attributes["CUI"] == "C3829315"

    assert [mention.text for mention in causes] == [
        "cerebral-abcess",
        "traumatic-brain-injury",
    ]
    assert causes[0].attributes["CUI"] == "C1510428"
    assert causes[1].attributes["CUI"] == "C0876926"


def test_patient_history_engine_extracts_compact_concepts_negation_and_temporal_features() -> None:
    letter = ExectLetter(
        "DALL9-PH",
        (
            "Past medical history of severe head injury due to an RTA in 2010, "
            "migraine, and depression. "
            "There is no history of febrile convulsions. "
            "She had febrile seizures at the age of 3 and 5."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    mentions = [m for m in prediction.mentions if m.entity == PATIENT_HISTORY.name]

    head_injury = next(m for m in mentions if m.text == "head-injury")
    assert head_injury.attributes == {
        "YearDate": "2010",
        "Certainty": "5",
        "Negation": "Affirmed",
        "CUI": "C0497301",
        "CUIPhrase": "head-injury",
    }
    assert head_injury.evidence == "severe head injury due to an RTA in 2010"

    migraine = next(m for m in mentions if m.text == "migraine")
    assert migraine.attributes["CUI"] == "C0149931"

    negated = next(m for m in mentions if m.text == "febrile-convulsions")
    assert negated.attributes["Certainty"] == "1"
    assert negated.attributes["Negation"] == "Negated"

    affirmed = next(m for m in mentions if m.text == "febrile-seizures")
    assert affirmed.attributes == {
        "AgeLower": "3",
        "AgeUpper": "5",
        "AgeUnit": "Year",
        "Certainty": "5",
        "Negation": "Affirmed",
        "CUI": "C0009952",
        "CUIPhrase": "febrile-seizures",
    }


def test_investigations_extracts_standard_eeg_and_unknown_results() -> None:
    letter = ExectLetter(
        "DALL9-INV",
        (
            "Investigations: EEG showed a single burst of generalised spike and wave. "
            "I do not have the results of his recent CT scan."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    investigations = [m for m in prediction.mentions if m.entity == INVESTIGATIONS.name]

    eeg = next(m for m in investigations if m.text == "EEG")
    assert eeg.attributes["EEG_Type"] == "Standard"
    assert eeg.attributes["EEG_Results"] == "Abnormal"

    ct = next(m for m in investigations if m.text == "CT")
    assert ct.attributes["CT_Results"] == "Unknown"
    assert ct.attributes["CUI"] == "C3515741"
    assert ct.attributes["CUIPhrase"] == "ct-unknown"


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

    patient_history = scorecard["patient_history_error_ledger"]
    assert patient_history["gold_mentions"] == 3
    assert patient_history["predicted_mentions"] == 3
    assert patient_history["predicted_with_cui"] == 3
    assert set(patient_history["gap_families"]) == {
        "phrase_scope_or_missing",
        "attribute_bundle",
        "cui_projection",
    }


def test_clinical_recovery_scorecard_separates_headline_from_projection() -> None:
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
                PATIENT_HISTORY.name,
                "depression",
                Certainty="5",
                Negation="Affirmed",
                CUI="C0011570",
                CUIPhrase="depression",
            ),
        ),
    )

    scorecard = clinical_recovery_scorecard.build_scorecard(
        [gold],
        [extract_deterministic_all9(letter)],
    )

    assert PATIENT_HISTORY.name not in scorecard["headline_entities"]
    assert PATIENT_HISTORY.name in scorecard["coverage_diagnostic_entities"]
    assert scorecard["entity_classes"][PATIENT_HISTORY.name] == "coverage_diagnostic"
    assert "overall_clinical_recovery" in scorecard
    assert scorecard["headline_scores"][PRESCRIPTION.name]["headline_kind"] == (
        "Clinical Component Score"
    )
    assert scorecard["headline_scores"][DIAGNOSIS.name]["headline_kind"] == (
        "Concept-Identity Headline"
    )
    assert scorecard["headline_scores"][SEIZURE_FREQUENCY.name]["headline_kind"] == (
        "Frequency State Recovery"
    )
    assert set(scorecard["artifact_projection_scores"]) == {
        "phrase_only",
        "semantic",
        "benchmark",
    }
    assert "patient_history_coverage" in scorecard


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


def test_patient_history_keeps_distinct_occurrences_diagnosis_collapses_prose() -> None:
    # Two history mentions of "diabetes" at distinct offsets with identical
    # attributes are kept as separate predictions (per-occurrence emission), so the
    # offset-based benchmark's duplicate gold copies are recoverable. A diagnosis
    # surface form repeated in prose still collapses to one (the rules cannot tell a
    # repeat assertion from a prose token, so per-occurrence is PatientHistory-only).
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


def test_prescription_keeps_current_dose_before_parenthetical_titration() -> None:
    letter = ExectLetter(
        "PRESC-CURRENT-BEFORE-TITRATION",
        "Medication: lamtorigine 250mg bd (to reduce as detailed below).",
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    assert len(prescriptions) == 1
    assert prescriptions[0].text == "lamtorigine 250mg bd"
    assert prescriptions[0].attributes["DrugName"] == "lamotrigine"
    assert prescriptions[0].attributes["DrugDose"] == "250"
    assert prescriptions[0].attributes["Frequency"] == "2"


def test_prescription_extracts_left_regimen_of_medication() -> None:
    letter = ExectLetter(
        "PRESC-LEFT-REGIMEN",
        "Current medication is 500mg bd of levetiracetam.",
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    assert len(prescriptions) == 1
    assert prescriptions[0].attributes["DrugName"] == "levetiracetam"
    assert prescriptions[0].attributes["DrugDose"] == "500"
    assert prescriptions[0].attributes["Frequency"] == "2"


def test_prescription_splits_current_am_pm_before_titration_tail() -> None:
    letter = ExectLetter(
        "PRESC-SPLIT-BEFORE-TITRATION",
        "Medication: Lamotrigine 50mg am, 75mg pm increasing by 25mg every 2 weeks.",
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    regimen_keys = [
        (m.text, m.attributes["DrugDose"], m.attributes["Frequency"])
        for m in prescriptions
    ]

    assert regimen_keys == [
        ("Lamotrigine 50mg am", "50", "1"),
        ("Lamotrigine 50mg am, 75mg pm", "75", "1"),
    ]


def test_prescription_suppresses_future_and_weight_based_headline_contexts() -> None:
    letter = ExectLetter(
        "PRESC-FUTURE-WEIGHT",
        (
            "I suggest that the dose should be increased by 100mg so that he is on "
            "Sodium Valproate 800mg bd. Medication: Levetiracetam 1500mg bd "
            "(60mg/kg/day). I suggest adding in some Clobazam to take on an as "
            "required basis for seizure clusters."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    assert prescriptions == []


def test_prescription_suppresses_to_start_and_suggest_introducing_plans() -> None:
    letter = ExectLetter(
        "PRESC-FUTURE-STARTS",
        (
            "Medication: To start Carbamazepine 100mg bd increasing gradually to "
            "400mg bd. If this increase is not successful then I would suggest "
            "introducing zonisamide 25mg od increasing by 25mg every fortnight."
        ),
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    assert prescriptions == []


def test_prescription_weight_based_restatement_does_not_drop_other_current_doses() -> None:
    """P7 (2026-07-02): a trailing mg/kg/day total for ONE dose must not silently
    drop OTHER, unrelated current doses in the same multi-dose evidence span.

    The whole-evidence weight-context search used to fire once per dose-loop
    iteration regardless of which dose it actually described, so a single
    trailing "(8mg/kg/day)" restatement suppressed every current dose in the
    sentence, not just the weight-based one.
    """

    letter = ExectLetter(
        "PRESC-MULTI-DOSE-WEIGHT-TAIL",
        "Medications: Carbamazepine 100mg am, 200mg pm (8mg/kg/day).",
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    doses = sorted(m.attributes["DrugDose"] for m in prescriptions)
    assert doses == ["100", "200"]
    # The weight-only figure (8) must never surface as its own current dose.
    assert "8" not in doses


def test_prescription_handles_twice_aday_typo() -> None:
    letter = ExectLetter(
        "PRESC-TWICE-ADAY",
        "Medications: Lamotrigine 100mg twice aday.",
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    assert len(prescriptions) == 1
    assert prescriptions[0].attributes["DrugDose"] == "100"
    assert prescriptions[0].attributes["Frequency"] == "2"


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
