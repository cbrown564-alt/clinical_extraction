"""Tests for the ExECTv2 standard-dictionary translation layer.

These encode the dictionary *mappings as principles* (drug/dose/frequency
normalization, diagnosis benchmark-convention repair, SF rewrites) and assert
parity with the existing deterministic sources the dictionary consolidates.
"""

from __future__ import annotations

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    PRESCRIPTION_CONCEPT_BY_PHRASE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    all_entities,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)

# ---------------------------------------------------------------------------
# Prescription dictionary
# ---------------------------------------------------------------------------


def test_normalize_drug_name_generic_alias_and_unknown() -> None:
    assert sd.normalize_drug_name("lamotrigine") == "lamotrigine"
    # Misspelling alias collapses to the generic.
    assert sd.normalize_drug_name("lamtorigine") == "lamotrigine"
    assert sd.normalize_drug_name("not-a-drug") is None


def test_normalize_drug_name_matches_benchmark_lexicon() -> None:
    # Every known surface maps to its benchmark canonical generic.
    for phrase, concept in PRESCRIPTION_CONCEPT_BY_PHRASE.items():
        assert sd.normalize_drug_name(phrase) == concept.canonical


@pytest.mark.parametrize(
    ("unit", "expected"),
    [
        ("mg", "mg"),
        ("mgs", "mg"),
        ("mgms", "mg"),
        ("milligrams", "mg"),
        ("g", "g"),
        ("grams", "g"),
    ],
)
def test_normalize_dose_unit_variants(unit: str, expected: str) -> None:
    assert sd.normalize_dose_unit(unit) == expected
    # Parity with the live deterministic extractor's canonicalizer.
    assert sd.normalize_dose_unit(unit) == all_entities._canonical_dose_unit(unit)


def test_dose_from_text() -> None:
    assert sd.dose_from_text("lamotrigine 250mg bd") == ("250", "mg")
    assert sd.dose_from_text("valproate 1.5 grams daily") == ("1.5", "g")
    assert sd.dose_from_text("no dose here") is None


def test_normalize_dose_value_strips_redundant_unit_only_for_atomic_dose() -> None:
    assert sd.normalize_dose_value("75mg") == "75"
    assert sd.normalize_dose_value("75 mg") == "75"
    assert sd.normalize_dose_value("750mg mane, 500 mg nocte") == "750mg mane, 500 mg nocte"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("bd", "2"),
        ("twice daily", "2"),
        ("tds", "3"),
        ("three times a day", "3"),
        ("od", "1"),
        ("once daily", "1"),
        ("nocte", "1"),
        ("prn", "As_Required"),
        ("as required", "As_Required"),
        ("no frequency", None),
    ],
)
def test_frequency_code(text: str, expected: str | None) -> None:
    assert sd.frequency_code(text) == expected
    # Parity with the deterministic extractor's frequency reader.
    assert sd.frequency_code(text) == all_entities._frequency_from_text(text)


def test_split_daily_dose_regimen_uses_source_time_markers() -> None:
    rows = sd.split_daily_dose_regimen(
        "levetiracetam 750mg mane, 500 mg nocte",
        evidence="Current antiepileptic medication: levetiracetam 750mg mane, 500 mg nocte",
        attributes={"DrugName": "levetiracetam", "DrugDose": "750mg mane, 500 mg nocte"},
    )
    assert [attrs["DrugDose"] for _, attrs, _ in rows] == ["750", "500"]
    assert [attrs["Frequency"] for _, attrs, _ in rows] == ["1", "1"]
    assert {rule for _, _, rule in rows} == {"split_explicit_uneven_daily_dose_regimen"}


def test_split_daily_dose_regimen_does_not_split_single_twice_daily_dose() -> None:
    assert (
        sd.split_daily_dose_regimen(
            "Sodium Valproate 800mg bd",
            evidence=(
                "I suggest that the dose should be increased so he is on "
                "Sodium Valproate 800mg bd."
            ),
            attributes={"DrugName": "sodium-valproate", "DrugDose": "800", "Frequency": "2"},
        )
        == []
    )


def test_split_daily_dose_regimen_does_not_resplit_already_split_once_daily_dose() -> None:
    assert (
        sd.split_daily_dose_regimen(
            "levetiracetam 750mg mane",
            evidence="Current antiepileptic medication: levetiracetam 750mg mane, 500 mg nocte",
            attributes={"DrugName": "levetiracetam", "DrugDose": "750", "Frequency": "1"},
        )
        == []
    )


# ---------------------------------------------------------------------------
# Diagnosis convention dictionary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("focal dyscognitive seizures", "dyscognitive seizures"),
        ("grand mal seizure", "grand mal"),
        ("secondarily generalised seizures", "secondary generalised seizures"),
        ("right hippocampal sclerosis", "temporal lobe epilepsy"),
    ],
)
def test_diagnosis_convention_alias_repairs(text: str, expected: str) -> None:
    assert sd.diagnosis_convention_target(text, evidence=text) == expected


def test_diagnosis_residual_benchmark_target_uses_evidence() -> None:
    # focal epilepsy concept but evidence names symptomatic epilepsy without "focal".
    assert (
        sd.diagnosis_convention_target(
            "focal epilepsy", evidence="symptomatic epilepsy with seizures"
        )
        == "symptomatic epilepsy"
    )
    # No matching convention -> unchanged.
    assert (
        sd.diagnosis_convention_target(
            "temporal lobe epilepsy", evidence="temporal lobe epilepsy"
        )
        is None
    )


def test_is_diagnosis_convention_noise() -> None:
    # Standalone symptom term, not tagged Epilepsy -> drop.
    assert sd.is_diagnosis_convention_noise(
        "myoclonic jerks", evidence="myoclonic jerks", diag_category="SingleSeizure"
    )
    # Same term tagged Epilepsy is kept.
    assert not sd.is_diagnosis_convention_noise(
        "myoclonic jerks", evidence="myoclonic jerks", diag_category="Epilepsy"
    )
    # Weak generic-epilepsy context without a strong assertion -> drop.
    assert sd.is_diagnosis_convention_noise(
        "epilepsy", evidence="referred to the epilepsy nurse", diag_category="Epilepsy"
    )
    # Strong diagnostic assertion overrides the weak context -> kept.
    assert not sd.is_diagnosis_convention_noise(
        "epilepsy", evidence="diagnosis of epilepsy", diag_category="Epilepsy"
    )


def test_diagnosis_residual_additions_dedupes_by_concept() -> None:
    note = "Diagnosis: focal onset epilepsy (occipital). Previous episode of status epilepticus."
    additions = sd.diagnosis_residual_additions(note)
    texts = {text for text, _ in additions}
    assert "occipital lobe epilepsy" in texts
    assert "status epilepticus" in texts
    # No spurious additions when the note lacks the patterns.
    assert sd.diagnosis_residual_additions("Routine follow up, no change.") == []


# ---------------------------------------------------------------------------
# SeizureFrequency rewrite dictionary
# ---------------------------------------------------------------------------


def test_sf_convention_rewrite_cluster_of_3() -> None:
    result = sd.sf_convention_rewrite(
        "cluster of 3", evidence="a cluster of 3 in March", attributes={}
    )
    assert result is not None
    text, attrs, rule = result
    assert text == "seizure cluster"
    assert attrs["CUI"] == "C3203523"
    assert attrs["CUIPhrase"] == "seizure cluster"
    assert rule == "rewrite_cluster_of_3_to_seizure_cluster"


def test_sf_convention_rewrite_absences_requires_evidence() -> None:
    result = sd.sf_convention_rewrite(
        "absences", evidence="frequent typical absences", attributes={}
    )
    assert result is not None
    assert result[0] == "typical absences"
    # Without the evidence cue, no rewrite.
    assert sd.sf_convention_rewrite("absences", evidence="some absences", attributes={}) is None
