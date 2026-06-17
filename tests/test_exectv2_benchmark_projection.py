"""Tests for shared ExECTv2 benchmark-format projection helpers."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    BenchmarkConcept,
    attach_benchmark_concept,
    birth_history_concept,
    diagnosis_concept,
    epilepsy_cause_concept,
    investigation_concept,
    onset_concept,
    prescription_concept,
    project_cuis,
    when_diagnosed_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    BIRTH_HISTORY,
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    ONSET,
    PRESCRIPTION,
    WHEN_DIAGNOSED,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)


def test_prescription_projection_keeps_benchmark_brand_and_generic_concepts_separate() -> None:
    keppra = prescription_concept("Keppra")
    levetiracetam = prescription_concept("levetiracetam")

    assert keppra == BenchmarkConcept("keppra", "C0876060", "keppra")
    assert levetiracetam == BenchmarkConcept(
        "levetiracetam",
        "C0377265",
        "levetiracetam",
    )


def test_investigation_projection_uses_modality_result_concept() -> None:
    assert investigation_concept("EEG", "Abnormal") == BenchmarkConcept(
        "EEG",
        "C0151611",
        "eeg abnormal",
    )
    assert investigation_concept("MRI", None) == BenchmarkConcept("MRI", "C0436539", "MRI")


def test_diagnosis_projection_maps_observed_phrases_to_category_and_cui() -> None:
    assert diagnosis_concept("JME") == BenchmarkConcept(
        "Epilepsy",
        "C0270853",
        "juvenile myoclonic epilepsy",
    )


def test_onset_projection_maps_source_near_epilepsy_phrase() -> None:
    assert onset_concept("epilepsy") == BenchmarkConcept("epilepsy", "C0014544", "epilepsy")


def test_new_structured_entity_projections_are_finite_benchmark_lookups() -> None:
    assert when_diagnosed_concept() == BenchmarkConcept("epilepsy", "C0014544", "epilepsy")
    assert birth_history_concept("born-slightly-premature") == BenchmarkConcept(
        "late-preterm-birth",
        "C3829315",
        "late-preterm-birth",
    )
    assert epilepsy_cause_concept("cerebral-abcess") == BenchmarkConcept(
        "cerebral-abscess",
        "C1510428",
        "cerebral-abscess",
    )


def test_attach_benchmark_concept_does_not_overwrite_existing_clinical_attributes() -> None:
    attrs = attach_benchmark_concept(
        {"DrugDose": "500", "DoseUnit": "mg"},
        BenchmarkConcept("levetiracetam", "C0377265", "levetiracetam"),
        canonical_key="DrugName",
    )

    assert attrs == {
        "DrugDose": "500",
        "DoseUnit": "mg",
        "DrugName": "levetiracetam",
        "CUI": "C0377265",
        "CUIPhrase": "levetiracetam",
    }


def test_project_cuis_is_precision_first_and_leaves_unknown_mentions_without_guessing() -> None:
    prediction = PredictedLetter(
        letter_id="PROJ-001",
        mentions=(
            PredictedMention(
                entity=PRESCRIPTION.name,
                text="levetiracetam 500 mg bd",
                attributes={"DrugName": "levetiracetam", "DrugDose": "500"},
                evidence="levetiracetam 500 mg bd",
                component_owner="fixture",
            ),
            PredictedMention(
                entity=INVESTIGATIONS.name,
                text="EEG",
                attributes={"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                evidence="EEG was abnormal",
                component_owner="fixture",
            ),
            PredictedMention(
                entity=DIAGNOSIS.name,
                text="not-in-lexicon",
                attributes={},
                evidence="not-in-lexicon",
                component_owner="fixture",
            ),
            PredictedMention(
                entity=ONSET.name,
                text="epilepsy",
                attributes={"Age": "4", "AgeUnit": "Year"},
                evidence="epilepsy started at the age of 4",
                component_owner="fixture",
            ),
            PredictedMention(
                entity=WHEN_DIAGNOSED.name,
                text="epileps",
                attributes={"Age": "4", "AgeUnit": "Year"},
                evidence="diagnosed with epilepsy at the age of 4",
                component_owner="fixture",
            ),
            PredictedMention(
                entity=BIRTH_HISTORY.name,
                text="born-normally",
                attributes={"Certainty": "5"},
                evidence="born normally",
                component_owner="fixture",
            ),
            PredictedMention(
                entity=EPILEPSY_CAUSE.name,
                text="Tuberous-sclerosis",
                attributes={"Certainty": "5"},
                evidence="Tuberous sclerosis",
                component_owner="fixture",
            ),
        ),
    )

    projected = project_cuis(prediction)

    assert projected.mentions[0].attributes["CUI"] == "C0377265"
    assert projected.mentions[1].attributes["CUI"] == "C0151611"
    assert "CUI" not in projected.mentions[2].attributes
    assert projected.mentions[3].attributes["CUI"] == "C0014544"
    assert projected.mentions[4].attributes["CUI"] == "C0014544"
    assert projected.mentions[5].attributes["CUI"] == "C3665337"
    assert projected.mentions[6].attributes["CUI"] == "C0041341"
