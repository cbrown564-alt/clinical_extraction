from dataclasses import replace

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DIAGNOSIS,
    SEIZURE_FREQUENCY,
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
    score_entity,
    score_overall,
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
    a = _ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="2", CUIPhrase="seizures")
    b = _ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="2", CUIPhrase="different")
    assert match_key(a) == match_key(b)


def test_phrase_only_ignores_attributes() -> None:
    a = _ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="2")
    b = _ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="9")
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


def test_gold_scored_against_itself_is_perfect() -> None:
    letters = load_letters()
    score = score_entity(letters, letters, SEIZURE_FREQUENCY)
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
                _ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="2"),
                _ann(SEIZURE_FREQUENCY, "absence-seizures", NumberOfSeizures="1"),
                _ann(DIAGNOSIS, "epilepsy", DiagCategory="Epilepsy"),
            ),
        ),
        ExectLetter("L2", "note", (_ann(DIAGNOSIS, "single-seizure"),)),
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="2"),
                _ann(DIAGNOSIS, "wrong-diagnosis", DiagCategory="Epilepsy"),
            ),
        ),
        ExectLetter(
            "L2",
            "note",
            (
                _ann(DIAGNOSIS, "single-seizure"),
                _ann(SEIZURE_FREQUENCY, "spurious-seizures", NumberOfSeizures="2"),
            ),
        ),
    ]

    score = score_overall(
        gold,
        pred,
        (SEIZURE_FREQUENCY, DIAGNOSIS),
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
    score = score_entity(letters, empty, SEIZURE_FREQUENCY)
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
                _ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="2"),
                _ann(SEIZURE_FREQUENCY, "absence-seizures", NumberOfSeizures="1"),
            ),
        )
    ]
    # one of two mentions correct: per-item recall 0.5, but the letter counts as
    # a per-letter true positive (at least one correct mention).
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="2"),),
        )
    ]
    score = score_entity(gold, pred, SEIZURE_FREQUENCY)
    assert (score.per_item.tp, score.per_item.fn) == (1, 1)
    assert score.per_item.recall == 0.5
    assert score.per_letter.f1 == 1.0


def test_spurious_mention_in_empty_gold_letter_is_per_letter_false_positive() -> None:
    gold = [ExectLetter("L1", "note", ())]
    pred = [
        ExectLetter("L1", "note", (_ann(SEIZURE_FREQUENCY, "two-seizures", NumberOfSeizures="2"),))
    ]
    score = score_entity(gold, pred, SEIZURE_FREQUENCY)
    assert (score.per_letter.tp, score.per_letter.fp, score.per_letter.fn) == (0, 1, 0)
    assert score.per_item.fp == 1


def test_wrong_attribute_breaks_full_feature_match_but_not_phrase_match() -> None:
    letters = load_letters()
    target = next(letter for letter in letters if letter.entities(SEIZURE_FREQUENCY))
    mentions = list(target.annotations)
    sf_index = next(i for i, a in enumerate(mentions) if a.entity == SEIZURE_FREQUENCY)
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

    strict = score_entity(letters, perturbed, SEIZURE_FREQUENCY, PHRASE_AND_FEATURES)
    lenient = score_entity(letters, perturbed, SEIZURE_FREQUENCY, PHRASE_ONLY)
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
                _ann(SEIZURE_FREQUENCY, "focal seizures", NumberOfSeizures="2"),
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
                _ann(SEIZURE_FREQUENCY, "2 focal seizures per month", NumberOfSeizures="3"),
            ),
        )
    ]

    diagnostic = source_near_diagnostic(
        gold,
        pred,
        ("Prescription", SEIZURE_FREQUENCY),
        benchmark_config_for,
    )

    assert diagnostic.per_entity["Prescription"].overlap.tp == 1
    assert diagnostic.per_entity["Prescription"].attribute_agreement_tp == 1
    assert diagnostic.per_entity[SEIZURE_FREQUENCY].overlap.tp == 1
    assert diagnostic.per_entity[SEIZURE_FREQUENCY].attribute_agreement_tp == 0
    assert diagnostic.overall.attribute_agreement_rate == 0.5
