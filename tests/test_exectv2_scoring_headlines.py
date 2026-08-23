"""Invariant-focused tests for exectv2 scoring headlines."""

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    clinical_recovery_scorecard,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.recovery import (
    score_for_primary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
    score_entity,
    score_frequency_state,
    score_prescription_components,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    exact_clinical_headline_scores,
    gold_headline_support,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _dx(text: str) -> ExectAnnotation:
    return _ann(DIAGNOSIS.name, text, DiagCategory="Epilepsy", Certainty="5", Negation="Affirmed")


def test_frequency_headline_keys_folded_phrase_not_cui_attach() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "2 tonic clonic seizures in 2014",
                    NumberOfSeizures="2",
                    CUI="C0494475",
                    CUIPhrase="tonic clonic seizures",
                ),
            ),
        )
    ]
    pred_no_cui = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "grand mal",
                    NumberOfSeizures="2",
                ),
            ),
        )
    ]
    pred_wrong_cui = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "focal seizures",
                    NumberOfSeizures="3",
                    CUI="C0036572",
                ),
            ),
        )
    ]

    matched = score_frequency_state(gold, pred_no_cui)
    mismatched = score_frequency_state(gold, pred_wrong_cui)

    assert matched.clinical_headline.f1 == 1.0
    assert mismatched.clinical_headline.f1 == 0.0
    assert matched.benchmark_with_cui.f1 == 0.0


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


@pytest.mark.local_corpus
def test_gold_scored_against_itself_is_perfect() -> None:
    letters = load_letters()
    score = score_entity(letters, letters, SEIZURE_FREQUENCY.name)
    assert score.per_item.f1 == 1.0
    assert score.per_letter.f1 == 1.0
    assert score.per_item.tp == 263
    assert score.per_letter.tp == 142


@pytest.mark.local_corpus
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


def test_diagnosis_concept_diagnostic_credits_parent_for_descendant() -> None:
    """Diagnostic example: gold=[epilepsy], pred=[epilepsy, focal epilepsy].
    Per-side collapse leaves gold={epilepsy}, pred={focal epilepsy}; the
    hierarchy-aware diagnostic credits the relation. This is not the reported
    exact clinical-headline scorer."""
    gold = [ExectLetter("L1", "note", (_dx("epilepsy"),))]
    pred = [ExectLetter("L1", "note", (_dx("epilepsy"), _dx("focal epilepsy")))]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name).concept_only

    assert score.f1 == 1.0
    assert score.precision_tp == 1 and score.recall_tp == 1
    assert score.pred_count == 1 and score.gold_count == 1


def test_reported_diagnosis_headline_requires_exact_concept_identity() -> None:
    gold = [ExectLetter("L1", "note", (_dx("epilepsy"),))]
    pred = [ExectLetter("L1", "note", (_dx("focal epilepsy"),))]

    score = exact_clinical_headline_scores(gold, pred)[DIAGNOSIS.name]

    assert score["tp"] == 0
    assert score["fp"] == 1
    assert score["fn"] == 1
    assert score["f1"] == 0.0


def test_clinical_recovery_scorecard_uses_exact_diagnosis_headline() -> None:
    gold = [ExectLetter("L1", "note", (_dx("epilepsy"),))]
    pred = [ExectLetter("L1", "note", (_dx("epilepsy"), _dx("focal epilepsy")))]

    entry = clinical_recovery_scorecard._headline_scores(gold, pred)[DIAGNOSIS.name]

    assert entry["headline_kind"] == "Exact Clinical-Fact Score"
    assert entry["headline"].f1 == 0.0


def test_llm_first_primary_uses_exact_diagnosis_headline() -> None:
    exact = {"f1": 0.0}
    permissive = {"f1": 1.0}
    scorecard = {
        "headline_scores": {
            DIAGNOSIS.name: {"headline": exact, "concept_only": permissive}
        }
    }

    assert score_for_primary(DIAGNOSIS.name, scorecard) is exact


def test_reported_diagnosis_headline_does_not_use_other_family_recall() -> None:
    gold = [ExectLetter("L1", "note", (_dx("focal seizures"),))]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "focal seizures", NumberOfSeizures="1"),),
        )
    ]

    score = exact_clinical_headline_scores(gold, pred)[DIAGNOSIS.name]

    assert score["tp"] == 0
    assert score["recall_tp"] == 0
    assert score["fn"] == 1

@pytest.mark.local_corpus
def test_four_family_gold_support_matches_headline_f1_denominator() -> None:
    dev = gold_headline_support(load_letters_for_split("dev"))
    holdout = gold_headline_support(load_letters_for_split("test"))

    assert dev["letter_count"] == 140
    assert dev["gold_count"] == 796
    assert dev["by_family"] == {
        "Diagnosis": 289,
        "SeizureFrequency": 165,
        "Prescription": 206,
        "Investigations": 136,
    }
    assert holdout["letter_count"] == 59
    assert holdout["gold_count"] == 328
    assert holdout["by_family"] == {
        "Diagnosis": 122,
        "SeizureFrequency": 74,
        "Prescription": 85,
        "Investigations": 47,
    }


def test_reported_headline_aggregate_rejects_asymmetric_diagnostic_counts() -> None:
    with pytest.raises(ValueError, match="symmetric exact unit keys"):
        aggregate_scores(
            (
                {
                    "tp": 1,
                    "precision_tp": 0,
                    "recall_tp": 1,
                    "fp": 0,
                    "fn": 0,
                },
            )
        )
