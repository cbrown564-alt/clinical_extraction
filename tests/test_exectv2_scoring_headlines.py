"""Invariant-focused tests for exectv2 scoring headlines."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
    score_entity,
    score_frequency_state,
    score_prescription_components,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _dx(text: str) -> ExectAnnotation:
    return _ann(DIAGNOSIS.name, text, DiagCategory="Epilepsy", Certainty="5", Negation="Affirmed")


def test_frequency_state_counts_unique_projected_states_per_letter() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="1", CUI="C0036572"),
                _ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="1", CUI="C0036572"),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="1", CUI="C0036572"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.clinical_headline.gold_count == 1
    assert score.clinical_headline.f1 == 1.0


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


def test_gold_scored_against_itself_is_perfect() -> None:
    letters = load_letters()
    score = score_entity(letters, letters, SEIZURE_FREQUENCY.name)
    assert score.per_item.f1 == 1.0
    assert score.per_letter.f1 == 1.0
    assert score.per_item.tp == 263
    assert score.per_letter.tp == 142


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


def test_diagnosis_headline_credits_gold_parent_when_pred_emits_descendant() -> None:
    """Hypothesis example (D1): gold=[epilepsy], pred=[epilepsy, focal epilepsy].
    Per-side collapse leaves gold={epilepsy}, pred={focal epilepsy}; the
    hierarchy-aware match credits the verbatim-correct diagnosis instead of
    scoring it as a paired FN+FP."""
    gold = [ExectLetter("L1", "note", (_dx("epilepsy"),))]
    pred = [ExectLetter("L1", "note", (_dx("epilepsy"), _dx("focal epilepsy")))]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name).concept_only

    assert score.f1 == 1.0
    assert score.precision_tp == 1 and score.recall_tp == 1
    assert score.pred_count == 1 and score.gold_count == 1
