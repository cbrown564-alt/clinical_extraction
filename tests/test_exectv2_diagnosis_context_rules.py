from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import DIAGNOSIS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    extract_deterministic_all9,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities.diagnosis import (  # noqa: E501
    _extract_diagnoses,
)


def _diagnosis_texts(note_text: str) -> list[str]:
    prediction = extract_deterministic_all9(
        ExectLetter("DX-CONTEXT", note_text),
        include_diagnosis_resolution_candidate=True,
    )
    return [
        mention.text.lower()
        for mention in prediction.mentions
        if mention.entity == DIAGNOSIS.name
    ]


def test_diagnosis_rules_exclude_negated_family_and_administrative_mentions() -> None:
    texts = _diagnosis_texts(
        "Diagnosis: genetic generalised epilepsy. "
        "There is no history of focal seizures. "
        "His mother had childhood absence seizures. "
        "I do not think these are epileptic seizures. "
        "Please contact the epilepsy nurse specialist."
    )

    assert texts == ["genetic generalised epilepsy"]


def test_diagnosis_context_rules_do_not_overreach_from_unrelated_no_or_admin_text() -> None:
    texts = _diagnosis_texts(
        "No medication changes are needed and focal epilepsy remains controlled. "
        "The patient has temporal lobe epilepsy; contact the epilepsy nurse if needed."
    )

    assert texts == ["focal epilepsy", "temporal lobe epilepsy"]


def test_diagnosis_rules_keep_a_diagnosis_that_is_followed_by_its_cause() -> None:
    texts = _diagnosis_texts(
        "Diagnosis: localisation related epilepsy secondary to a previous cerebral abscess. "
        "She also has symptomatic epilepsy due to neurocysticercosis."
    )

    assert "localisation related epilepsy" in texts
    assert "symptomatic epilepsy" in texts


def test_diagnosis_rules_accept_hyphenated_multiword_surfaces() -> None:
    texts = _diagnosis_texts("Impression: generalised tonic-clonic seizures.")

    assert texts == ["generalised tonic-clonic seizures"]


def test_diagnosis_rules_keep_patient_history_and_family_witness_statements() -> None:
    texts = _diagnosis_texts(
        "John's epilepsy started at the age of four. "
        "His brother said that he has had three generalised tonic clonic seizures."
    )

    assert texts == ["epilepsy", "generalised tonic clonic seizures"]


def test_diagnosis_rules_reuse_the_bounded_benchmark_residual_dictionary() -> None:
    prediction = extract_deterministic_all9(
        ExectLetter(
            "DX-RESIDUAL",
            "Diagnosis: Focal epilepsy ? right temporal lobe onset. "
            "Impression: drug refractory focal (occipital lobe) epilepsy.",
        ),
        include_diagnosis_resolution_candidate=True,
        include_diagnosis_benchmark_residuals=True,
    )
    mentions = [
        mention for mention in prediction.mentions if mention.entity == DIAGNOSIS.name
    ]
    by_text = {mention.text.lower(): mention for mention in mentions}

    assert "temporal lobe onset seizure" in by_text
    assert "drug" in by_text
    assert "benchmark_format" in by_text["drug"].component_owner


def test_diagnosis_residual_dictionary_can_be_ablated() -> None:
    mentions = _extract_diagnoses(
        "Impression: drug refractory focal (occipital lobe) epilepsy.",
        include_benchmark_residuals=False,
    )

    assert "drug" not in {mention.text.lower() for mention in mentions}


def test_rules_only_defaults_to_no_benchmark_residual_additions() -> None:
    prediction = extract_deterministic_all9(
        ExectLetter(
            "DX-DEFAULT",
            "Impression: drug refractory focal (occipital lobe) epilepsy.",
        )
    )

    assert "drug" not in {
        mention.text.lower()
        for mention in prediction.mentions
        if mention.entity == DIAGNOSIS.name
    }


def test_rules_only_retained_default_does_not_enable_resolution_candidate() -> None:
    prediction = extract_deterministic_all9(
        ExectLetter(
            "DX-RETAINED",
            "Diagnosis: localisation related epilepsy secondary to an abscess.",
        )
    )

    assert "localisation related epilepsy" not in {
        mention.text.lower()
        for mention in prediction.mentions
        if mention.entity == DIAGNOSIS.name
    }
