"""Tests for shared ExECTv2 benchmark-format projection helpers."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    BenchmarkConcept,
    attach_benchmark_concept,
    diagnosis_concept,
    investigation_concept,
    prescription_concept,
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
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
        ),
    )

    projected = project_cuis(prediction)

    assert projected.mentions[0].attributes["CUI"] == "C0377265"
    assert projected.mentions[1].attributes["CUI"] == "C0151611"
    assert "CUI" not in projected.mentions[2].attributes
