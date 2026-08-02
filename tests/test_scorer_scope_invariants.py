"""Phase-4 standing guardrail: scorer clause-scope invariants."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.prescription import (
    _is_future_medication,
    _is_weight_based_dosing,
)

_OUT_OF_SCOPE_SENTENCE = " The patient will be reviewed again in six months in the epilepsy clinic."


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def test_headline_key_is_invariant_to_surrounding_note_text() -> None:
    annotation = _ann(
        "Prescription",
        "lamotrigine 150mg bd",
        DrugName="Lamotrigine",
        DrugDose="150",
        DoseUnit="mg",
        Frequency="2",
    )

    baseline = clinical_headline_unit_keys("Prescription", [annotation], "")
    with_context = clinical_headline_unit_keys(
        "Prescription", [annotation], "prior letter text." + _OUT_OF_SCOPE_SENTENCE
    )

    assert baseline
    assert baseline == with_context


def test_prescription_future_and_weight_tails_do_not_change_headline_membership() -> None:
    future_clean = _ann(
        "Prescription",
        "lamotrigine 150mg bd",
        DrugName="Lamotrigine",
        DrugDose="150",
        DoseUnit="mg",
        Frequency="2",
    )
    future_tail = _ann(
        "Prescription",
        "lamotrigine 150mg bd, to reduce and stop over the next six weeks",
        DrugName="Lamotrigine",
        DrugDose="150",
        DoseUnit="mg",
        Frequency="2",
    )
    weight_clean = _ann(
        "Prescription",
        "levetiracetam 1500mg bd",
        DrugName="Levetiracetam",
        DrugDose="1500",
        DoseUnit="mg",
        Frequency="2",
    )
    weight_tail = _ann(
        "Prescription",
        "levetiracetam 1500mg bd (60mg/kg/day)",
        DrugName="Levetiracetam",
        DrugDose="1500",
        DoseUnit="mg",
        Frequency="2",
    )

    assert clinical_headline_unit_keys("Prescription", [future_clean]) == (
        clinical_headline_unit_keys("Prescription", [future_tail])
    )
    assert clinical_headline_unit_keys("Prescription", [weight_clean]) == (
        clinical_headline_unit_keys("Prescription", [weight_tail])
    )
    assert _is_future_medication(future_tail) is False
    assert _is_weight_based_dosing(weight_tail) is False


def test_seizure_frequency_headline_key_invariant_to_trailing_text() -> None:
    clean = _ann(
        "SeizureFrequency",
        "focal seizures",
        NumberOfSeizures="3",
        CUI="C0036572",
    )
    trailing = _ann(
        "SeizureFrequency",
        "focal seizures, to be reviewed at the next appointment",
        NumberOfSeizures="3",
        CUI="C0036572",
    )

    assert clinical_headline_unit_keys("SeizureFrequency", [clean]) == clinical_headline_unit_keys(
        "SeizureFrequency", [trailing]
    )


def test_diagnosis_headline_unit_is_the_annotation_phrase_by_design() -> None:
    single = _ann(
        "Diagnosis",
        "focal epilepsy",
        DiagCategory="Epilepsy",
        Certainty="5",
        Negation="Affirmed",
    )
    assert clinical_headline_unit_keys("Diagnosis", [single]) == [("Diagnosis", "focal epilepsy")]
    assert clinical_headline_unit_keys(
        "Diagnosis", [single], _OUT_OF_SCOPE_SENTENCE
    ) == clinical_headline_unit_keys("Diagnosis", [single], "")
