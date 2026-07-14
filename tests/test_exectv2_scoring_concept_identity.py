"""Invariant-focused tests for exectv2 scoring concept identity."""


from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    BIRTH_HISTORY,
    DIAGNOSIS,
    INVESTIGATIONS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _dx(text: str) -> ExectAnnotation:
    return _ann(DIAGNOSIS.name, text, DiagCategory="Epilepsy", Certainty="5", Negation="Affirmed")


def test_diagnosis_concept_identity_recall_accepts_seizure_frequency_anchor() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "focal to bilateral convulsive seizures",
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
                    SEIZURE_FREQUENCY.name,
                    "focal to bilateral convulsive seizures",
                    NumberOfSeizures="0",
                    TimeSince_or_TimeOfEvent="Since",
                    YearDate="2017",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.recall == 1.0
    assert score.concept_only.precision == 0.0
    assert score.concept_only.pred_count == 0


def test_diagnosis_recall_from_seizure_frequency_uses_projected_core_vocabulary() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(DIAGNOSIS.name, "tonic clonic seizures", Certainty="5", Negation="Affirmed"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "generalised tonic clonic seizure",
                    NumberOfSeizures="0",
                    TimeSince_or_TimeOfEvent="Since",
                    YearDate="2017",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.recall == 1.0


def test_diagnosis_concept_identity_normalizes_common_llm_typo() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "tonic clonic seizures",
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
                    "generalised tonic chronic seizures",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.f1 == 1.0


def test_diagnosis_concept_identity_projects_temporal_lobe_onset_focal_seizures() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "temporal lobe seizure",
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
                    "temporal lobe onset focal seizures",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.f1 == 1.0


def test_diagnosis_concept_identity_projects_complex_partial_conjunction() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "complex partial seizures",
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
                    "general and complex partial seizures",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.f1 == 1.0


def test_investigations_headline_ignores_eeg_type_component() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    INVESTIGATIONS.name,
                    "EEG",
                    EEG_Performed="Yes",
                    EEG_Results="Normal",
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
                    "video EEG",
                    EEG_Performed="Yes",
                    EEG_Results="Normal",
                    EEG_Type="VideoTelemetry",
                ),
            ),
        )
    ]

    score = score_investigations_components(gold, pred)

    assert score.clinical_headline.f1 == 1.0
    assert score.eeg_type.precision == 0.0


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


def test_diagnosis_concept_only_collapses_assertion_variants_per_letter() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "epilepsy with generalised tonic clonic seizures alone",
                    Certainty="5",
                    Negation="Affirmed",
                ),
                _ann(
                    DIAGNOSIS.name,
                    "epilepsy with generalised tonic clonic seizure alone",
                    Certainty="4",
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
                    "epilepsy with generalised tonic clonic seizures alone",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.gold_count == 1
    assert score.concept_only.f1 == 1.0
    assert score.concept_assertion.gold_count == 2


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
