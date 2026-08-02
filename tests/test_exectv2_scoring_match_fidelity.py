"""Invariant-focused tests for exectv2 scoring match fidelity."""


from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_AND_FEATURES,
    PHRASE_ONLY,
    match_key,
    score_frequency_state,
    score_prescription_components,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def test_phrase_only_ignores_attributes() -> None:
    a = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2")
    b = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="9")
    assert match_key(a, PHRASE_ONLY) == match_key(b, PHRASE_ONLY)
    assert match_key(a, PHRASE_AND_FEATURES) != match_key(b, PHRASE_AND_FEATURES)


def test_match_key_ignores_cuiphrase_by_default() -> None:
    a = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2", CUIPhrase="seizures")
    b = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2", CUIPhrase="different")
    assert match_key(a) == match_key(b)


def test_active_rate_fidelity_penalizes_wrong_rate_headline_forgives() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    NumberOfSeizures="6",
                    NumberOfTimePeriods="1",
                    TimePeriod="Week",
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
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    NumberOfSeizures="6",
                    NumberOfTimePeriods="3",
                    TimePeriod="Week",
                ),
            ),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.clinical_headline.f1 == 1.0
    assert score.active_rate_fidelity.f1 == 0.0


def test_active_rate_fidelity_treats_bare_count_and_degenerate_range_as_equal() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="2"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    LowerNumberOfSeizures="2",
                    UpperNumberOfSeizures="2",
                ),
            ),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.active_rate_fidelity.f1 == 1.0
    assert match_key(gold[0].annotations[0]) == match_key(pred[0].annotations[0])


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
