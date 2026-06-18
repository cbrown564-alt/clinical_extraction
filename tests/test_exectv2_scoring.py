from dataclasses import replace

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    BIRTH_HISTORY,
    DIAGNOSIS,
    ENTITY_REGISTRY,
    INVESTIGATIONS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_AND_FEATURES,
    PHRASE_ONLY,
    benchmark_config_for,
    canonicalize_medication_name,
    match_key,
    normalize_phrase,
    score_concept_identity,
    score_entity,
    score_frequency_state,
    score_investigations_components,
    score_overall,
    score_prescription_benchmark_projection,
    score_prescription_components,
    source_near_diagnostic,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def test_normalize_phrase_strips_hyphens_quotes_and_case() -> None:
    assert (
        normalize_phrase("generalised-tonic-clonic-seizures")
        == "generalised tonic clonic seizures"
    )
    assert normalize_phrase("“absence-like”-episodes") == "absence like episodes"


def test_match_key_ignores_cuiphrase_by_default() -> None:
    a = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2", CUIPhrase="seizures")
    b = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2", CUIPhrase="different")
    assert match_key(a) == match_key(b)


def test_phrase_only_ignores_attributes() -> None:
    a = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2")
    b = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="9")
    assert match_key(a, PHRASE_ONLY) == match_key(b, PHRASE_ONLY)
    assert match_key(a, PHRASE_AND_FEATURES) != match_key(b, PHRASE_AND_FEATURES)


def test_match_key_canonicalizes_format_only_attribute_values() -> None:
    a = _ann("Prescription", "levetiracetam", DrugName="Levetiracetam", DoseUnit="MG")
    b = _ann("Prescription", "levetiracetam", DrugName="levetiracetam", DoseUnit="mg")

    assert match_key(a, PHRASE_AND_FEATURES) == match_key(b, PHRASE_AND_FEATURES)


def test_canonicalize_medication_name_accepts_brand_synonym_and_typo_variants() -> None:
    assert canonicalize_medication_name("Keppra") == "levetiracetam"
    assert canonicalize_medication_name("Lamictal") == "lamotrigine"
    assert canonicalize_medication_name("Eplim") == "sodium-valproate"
    assert canonicalize_medication_name("Tegretaol") == "carbamazepine"
    assert canonicalize_medication_name("Zonismaide") == "zonisamide"


def test_score_prescription_components_uses_clinical_regimen_keys() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "Keppra-500mg-bd",
                    DrugName="Keppra",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "levetiracetam 500 mg twice daily",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="MG",
                    Frequency="2",
                ),
            ),
        )
    ]

    score = score_prescription_components(gold, pred)

    assert score.name.f1 == 1.0
    assert score.dose.f1 == 1.0
    assert score.frequency.f1 == 1.0
    assert score.complete.f1 == 1.0
    assert score.ordinary_complete.f1 == 1.0
    assert score.clinical_headline.f1 == 1.0


def test_prescription_benchmark_projection_separates_clinical_identity_from_cui() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "Keppra-500mg-bd",
                    DrugName="Keppra",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0876060",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "levetiracetam 500 mg twice daily",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0377265",
                ),
            ),
        )
    ]

    score = score_prescription_benchmark_projection(gold, pred)

    assert score.clinical_medication_identity.f1 == 1.0
    assert score.drugname_cui_projection.f1 == 0.0
    assert score.phrase_scope.f1 == 0.0
    assert score.benchmark_with_cui.f1 == 0.0


def test_concept_identity_recall_is_entity_agnostic_precision_home_tagged() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "focal seizures",
                    DiagCategory="MultipleSeizures",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "PatientHistory",
                    "focal seizures",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_assertion.recall == 1.0
    assert score.concept_assertion.precision == 0.0
    assert score.concept_assertion.pred_count == 0
    assert score.concept_assertion.gold_count == 1


def test_concept_identity_collapses_diagnosis_specificity_to_most_specific() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "epilepsy",
                    DiagCategory="Epilepsy",
                    Certainty="5",
                    Negation="Affirmed",
                ),
                _ann(
                    DIAGNOSIS.name,
                    "focal epilepsy",
                    DiagCategory="Epilepsy",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "focal epilepsy",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_assertion.gold_count == 1
    assert score.concept_assertion.recall == 1.0
    assert score.concept_assertion.precision == 1.0


def test_concept_identity_splits_compound_same_kind_concepts() -> None:
    letters = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "focal seizures and absence seizures",
                    DiagCategory="MultipleSeizures",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(letters, letters, DIAGNOSIS.name)

    assert score.concept_assertion.gold_count == 2
    assert score.concept_assertion.tp == 2


def test_diagnosis_concept_identity_scores_projected_core_fact() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "focal epilepsy",
                    DiagCategory="Epilepsy",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "probable focal epilepsy (perinatal insult)",
                    Certainty="4",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.f1 == 1.0


def test_diagnosis_concept_identity_projects_benchmark_equivalent_diagnoses() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(DIAGNOSIS.name, "focal epilepsy", Certainty="5", Negation="Affirmed"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "symptomatic structural focal epilepsy",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.f1 == 1.0


def test_diagnosis_concept_identity_preserves_protected_seizure_type_compound() -> None:
    letters = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "focal seizures with altered awareness",
                    DiagCategory="MultipleSeizures",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(letters, letters, DIAGNOSIS.name)

    assert score.concept_only.gold_count == 1
    assert score.concept_only.tp == 1


def test_diagnosis_concept_identity_counts_unique_projected_facts_per_letter() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(DIAGNOSIS.name, "tonic clonic seizures", Certainty="5", Negation="Affirmed"),
                _ann(DIAGNOSIS.name, "tonic clonic seizures", Certainty="5", Negation="Affirmed"),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "generalised tonic clonic seizure",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.gold_count == 1
    assert score.concept_only.f1 == 1.0


def test_birth_history_concept_identity_ignores_cui_projection() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    BIRTH_HISTORY.name,
                    "born-normally",
                    Certainty="5",
                    Negation="Affirmed",
                    CUI="C3665337",
                    CUIPhrase="born-normally",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    BIRTH_HISTORY.name,
                    "birth normal",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, BIRTH_HISTORY.name)

    assert score.concept_assertion.f1 == 1.0


def test_investigations_component_score_uses_modality_result_tuple_not_cui() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    INVESTIGATIONS.name,
                    "abnormal-eeg",
                    EEG_Performed="Yes",
                    EEG_Results="Abnormal",
                    EEG_Type="Standard",
                    CUI="C0151611",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    INVESTIGATIONS.name,
                    "EEG",
                    EEG_Performed="Yes",
                    EEG_Results="Abnormal",
                    EEG_Type="Standard",
                    CUI="wrong",
                ),
            ),
        )
    ]

    score = score_investigations_components(gold, pred)

    assert score.clinical_headline.f1 == 1.0
    assert score.eeg.f1 == 1.0


def test_frequency_state_scores_active_seizure_free_and_unknown_states() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "focal seizures", NumberOfSeizures="2", CUI="C1"),
                _ann(SEIZURE_FREQUENCY.name, "absence seizures", CUI="C2"),
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "tonic clonic seizures",
                    NumberOfSeizures="0",
                    CUI="C3",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "focal seizures", NumberOfSeizures="99", CUI="C1"),
                _ann(SEIZURE_FREQUENCY.name, "absence seizures", CUI="C2"),
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "tonic clonic seizures",
                    NumberOfSeizures="0",
                    CUI="C3",
                ),
            ),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.clinical_headline.f1 == 1.0
    assert score.active_rate.tp == 1
    assert score.unknown.tp == 1
    assert score.seizure_free.tp == 1


def test_prescription_drugname_cui_projection_accepts_format_variants_with_same_cui() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "Sodium-Valproate-500mg-bd",
                    DrugName="sodiumvalproate",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0037567",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "sodium valproate 500 mg twice daily",
                    DrugName="sodium-valproate",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0037567",
                ),
            ),
        )
    ]

    score = score_prescription_benchmark_projection(gold, pred)

    assert score.drugname_cui_projection.f1 == 1.0


def test_prescription_clinical_headline_counts_rescue_regimen_without_dose() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "buccal midazolam",
                    DrugName="Midazolam",
                    Frequency="As_Required",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "rescue midazolam as required",
                    DrugName="midazolam",
                    Frequency="As_Required",
                ),
            ),
        )
    ]

    score = score_prescription_components(gold, pred)

    assert score.rescue_regimen.f1 == 1.0
    assert score.clinical_headline.f1 == 1.0
    assert score.complete.gold_count == 0
    assert score.ordinary_complete.gold_count == 0


def test_prescription_frequency_diagnostics_separate_stated_from_defaulted() -> None:
    letters = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "Lamotrigine 100mg bd",
                    DrugName="Lamotrigine",
                    DrugDose="100",
                    DoseUnit="mg",
                    Frequency="2",
                ),
                _ann(
                    "Prescription",
                    "Levetiracetam 500mg",
                    DrugName="Levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="1",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    assert score.source_stated_frequency.tp == 1
    assert score.guideline_defaulted_frequency.tp == 1
    assert score.frequency.tp == 2


def test_prescription_frequency_source_uses_note_context_for_hidden_frequency() -> None:
    note = (
        "He previously tried topiramate and phenytoin and he is currently taking "
        "levetiracetam 1250mg twice a day."
    )
    gold = [
        ExectLetter(
            "L1",
            note,
            (
                _ann(
                    "Prescription",
                    "levetiracetam-",
                    DrugName="levetiracetam",
                    DrugDose="1250",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            note,
            (
                _ann(
                    "Prescription",
                    "levetiracetam 1250mg twice a day",
                    DrugName="levetiracetam",
                    DrugDose="1250",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ),
        )
    ]

    score = score_prescription_components(gold, pred)

    assert score.source_stated_frequency.f1 == 1.0
    assert score.guideline_defaulted_frequency.gold_count == 0
    assert score.guideline_defaulted_frequency.pred_count == 0


def test_prescription_frequency_source_uses_drug_attributes_when_gold_phrase_has_typo() -> None:
    note = "Medication: Lamotrigine 50mg bd."
    letters = [
        ExectLetter(
            "L1",
            note,
            (
                _ann(
                    "Prescription",
                    "Lamotrigne",
                    DrugName="Lamotrigine",
                    DrugDose="50",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    assert score.source_stated_frequency.tp == 1
    assert score.guideline_defaulted_frequency.gold_count == 0


def test_prescription_frequency_source_accepts_dotted_bd_abbreviation() -> None:
    letters = [
        ExectLetter(
            "L1",
            "Medication: Lamotrigine 100mg b.d.",
            (
                _ann(
                    "Prescription",
                    "Lamotrigine-",
                    DrugName="Lamotrigine",
                    DrugDose="100",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    assert score.source_stated_frequency.tp == 1
    assert score.guideline_defaulted_frequency.gold_count == 0


def test_future_and_weight_based_prescriptions_are_diagnostics_not_headline() -> None:
    letters = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "increase Lamotrigine to 150mg bd",
                    DrugName="Lamotrigine",
                    DrugDose="150",
                    DoseUnit="mg",
                    Frequency="2",
                ),
                _ann(
                    "Prescription",
                    "levetiracetam 10 mg/kg/day",
                    DrugName="Levetiracetam",
                    DrugDose="10",
                    DoseUnit="mg",
                    Frequency="1",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    assert score.future_medication.tp == 1
    assert score.weight_based_dosing.tp == 1
    assert score.clinical_headline.gold_count == 0
    assert score.ordinary_complete.gold_count == 0


def test_gold_scored_against_itself_is_perfect() -> None:
    letters = load_letters()
    score = score_entity(letters, letters, SEIZURE_FREQUENCY.name)
    assert score.per_item.f1 == 1.0
    assert score.per_letter.f1 == 1.0
    assert score.per_item.tp == 263
    assert score.per_letter.tp == 142


def test_all_entity_gold_scored_against_itself_is_perfect() -> None:
    letters = load_letters()
    entities = tuple(ENTITY_REGISTRY)
    score = score_overall(letters, letters, entities, benchmark_config_for)

    assert score.per_item.f1 == 1.0
    assert score.per_letter.f1 == 1.0
    assert set(score.per_entity) == set(entities)
    assert all(entity_score.per_item.f1 == 1.0 for entity_score in score.per_entity.values())
    assert all(entity_score.per_letter.f1 == 1.0 for entity_score in score.per_entity.values())


def test_score_overall_micro_averages_item_and_entity_presence_cells() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),
                _ann(SEIZURE_FREQUENCY.name, "absence-seizures", NumberOfSeizures="1"),
                _ann(DIAGNOSIS.name, "epilepsy", DiagCategory="Epilepsy"),
            ),
        ),
        ExectLetter("L2", "note", (_ann(DIAGNOSIS.name, "single-seizure"),)),
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),
                _ann(DIAGNOSIS.name, "wrong-diagnosis", DiagCategory="Epilepsy"),
            ),
        ),
        ExectLetter(
            "L2",
            "note",
            (
                _ann(DIAGNOSIS.name, "single-seizure"),
                _ann(SEIZURE_FREQUENCY.name, "spurious-seizures", NumberOfSeizures="2"),
            ),
        ),
    ]

    score = score_overall(
        gold,
        pred,
        (SEIZURE_FREQUENCY.name, DIAGNOSIS.name),
        lambda _e: PHRASE_AND_FEATURES,
    )

    assert (score.per_item.tp, score.per_item.fp, score.per_item.fn) == (2, 2, 2)
    assert score.per_item.f1 == 0.5
    assert (score.per_letter.tp, score.per_letter.fp, score.per_letter.fn) == (2, 1, 1)
    assert score.per_letter.f1 == 2 / 3


def test_empty_predictions_score_zero_recall() -> None:
    letters = load_letters()
    empty = [
        ExectLetter(letter_id=letter.letter_id, note_text=letter.note_text) for letter in letters
    ]
    score = score_entity(letters, empty, SEIZURE_FREQUENCY.name)
    assert score.per_item.recall == 0.0
    assert score.per_item.tp == 0
    assert score.per_item.fn == 263
    assert score.per_letter.fn == 142


def test_per_item_and_per_letter_diverge_on_partial_letter() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),
                _ann(SEIZURE_FREQUENCY.name, "absence-seizures", NumberOfSeizures="1"),
            ),
        )
    ]
    # one of two mentions correct: per-item recall 0.5, but the letter counts as
    # a per-letter true positive (at least one correct mention).
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),),
        )
    ]
    score = score_entity(gold, pred, SEIZURE_FREQUENCY.name)
    assert (score.per_item.tp, score.per_item.fn) == (1, 1)
    assert score.per_item.recall == 0.5
    assert score.per_letter.f1 == 1.0


def test_spurious_mention_in_empty_gold_letter_is_per_letter_false_positive() -> None:
    gold = [ExectLetter("L1", "note", ())]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),),
        )
    ]
    score = score_entity(gold, pred, SEIZURE_FREQUENCY.name)
    assert (score.per_letter.tp, score.per_letter.fp, score.per_letter.fn) == (0, 1, 0)
    assert score.per_item.fp == 1


def test_wrong_attribute_breaks_full_feature_match_but_not_phrase_match() -> None:
    letters = load_letters()
    target = next(letter for letter in letters if letter.entities(SEIZURE_FREQUENCY.name))
    mentions = list(target.annotations)
    sf_index = next(i for i, a in enumerate(mentions) if a.entity == SEIZURE_FREQUENCY.name)
    mentions[sf_index] = replace(
        mentions[sf_index],
        attributes={**mentions[sf_index].attributes, "NumberOfSeizures": "999"},
    )
    perturbed = [
        ExectLetter(target.letter_id, target.note_text, tuple(mentions))
        if letter.letter_id == target.letter_id
        else letter
        for letter in letters
    ]

    strict = score_entity(letters, perturbed, SEIZURE_FREQUENCY.name,PHRASE_AND_FEATURES)
    lenient = score_entity(letters, perturbed, SEIZURE_FREQUENCY.name,PHRASE_ONLY)
    assert strict.per_item.fp == 1
    assert strict.per_item.fn == 1
    assert lenient.per_item.f1 == 1.0


def test_source_near_diagnostic_counts_same_entity_substring_overlap() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann("Prescription", "lamotrigine", DrugName="lamotrigine", DoseUnit="mg"),
                _ann(SEIZURE_FREQUENCY.name, "focal seizures", NumberOfSeizures="2"),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "lamotrigine 200mg bd",
                    DrugName="Lamotrigine",
                    DoseUnit="MG",
                ),
                _ann(SEIZURE_FREQUENCY.name, "2 focal seizures per month", NumberOfSeizures="3"),
            ),
        )
    ]

    diagnostic = source_near_diagnostic(
        gold,
        pred,
        ("Prescription", SEIZURE_FREQUENCY.name),
        benchmark_config_for,
    )

    assert diagnostic.per_entity["Prescription"].overlap.tp == 1
    assert diagnostic.per_entity["Prescription"].attribute_agreement_tp == 1
    assert diagnostic.per_entity[SEIZURE_FREQUENCY.name].overlap.tp == 1
    assert diagnostic.per_entity[SEIZURE_FREQUENCY.name].attribute_agreement_tp == 0
    assert diagnostic.overall.attribute_agreement_rate == 0.5
