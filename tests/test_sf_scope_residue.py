"""Gold-free leftover-scope drops: symptom token, febrile history, driving-only SF."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_scope_residue as residue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    diagnosis as dx,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    prescription as rx,
)


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def test_drops_bare_episode_token() -> None:
    mentions = [
        _sf(
            "episodes",
            "The frequency of these appears to be increasing to almost daily.",
            FrequencyChange="Increased",
            TimePeriod="Day",
        ),
        _sf(
            "seizures",
            "He has not had any further seizures since his last appointment.",
            NumberOfSeizures="0",
            TimeSince_or_TimeOfEvent="Since",
        ),
    ]
    after, actions = residue.apply_scope_residue_drop(mentions)
    assert [m["text"] for m in after] == ["seizures"]
    assert actions[0]["reason"] == "bare_symptom_token"


def test_drops_bare_clumsy_and_jerks_but_keeps_myoclonic_jerks() -> None:
    mentions = [
        _sf("clumsy", "he has been “clumsy”, particularly early in the morning"),
        _sf(
            "jerks",
            "The absences and jerks happen more frequently perhaps several times a day.",
            NumberOfSeizures="3",
            TimePeriod="Day",
            NumberOfTimePeriods="1",
        ),
        _sf(
            "myoclonic jerks",
            "myoclonic jerks once a week",
            NumberOfSeizures="1",
            TimePeriod="Week",
            NumberOfTimePeriods="1",
        ),
        _sf(
            "absences",
            "The absences and jerks happen more frequently perhaps several times a day.",
            CUI="C0563606",
            NumberOfSeizures="3",
            TimePeriod="Day",
            NumberOfTimePeriods="1",
        ),
    ]
    after, actions = residue.apply_scope_residue_drop(mentions)
    assert [m["text"] for m in after] == ["myoclonic jerks", "absences"]
    assert {a["reason"] for a in actions} == {"bare_symptom_token"}


def test_drops_febrile_history_mention_not_generic_current_rate() -> None:
    mentions = [
        _sf(
            "febrile seizures",
            "He had 4 febrile seizures at the age of 3, 4 and then around five.",
            NumberOfSeizures="4",
        ),
        _sf(
            "seizures",
            "He has been seizure free since his teenage years.",
            NumberOfSeizures="0",
            TimeSince_or_TimeOfEvent="Since",
        ),
    ]
    after, actions = residue.apply_scope_residue_drop(mentions)
    assert [m["text"] for m in after] == ["seizures"]
    assert actions[0]["reason"] == "febrile_history"


def test_drops_driving_licence_seizure_free_without_duration_frame() -> None:
    mentions = [
        _sf(
            "seizure",
            "I was pleased to hear that he remains seizure free and is now driving.",
            NumberOfSeizures="0",
        ),
        _sf(
            "seizures",
            "seizure free for 2 years and now driving",
            NumberOfSeizures="0",
            NumberOfTimePeriods="2",
            TimePeriod="Year",
        ),
        _sf(
            "absences",
            "absence-like seizures 2014",
            NumberOfSeizures="1",
            YearDate="2014",
        ),
    ]
    after, actions = residue.apply_scope_residue_drop(mentions)
    assert [m["text"] for m in after] == ["seizures", "absences"]
    assert actions[0]["reason"] == "driving_without_frame"


def test_diagnosis_standalone_noise_includes_bare_jerk() -> None:
    assert dx.is_diagnosis_convention_noise(
        "jerks",
        evidence="The absences and jerks happen more frequently",
        diag_category="MultipleSeizures",
    )
    assert not dx.is_diagnosis_convention_noise(
        "juvenile myoclonic epilepsy",
        evidence="juvenile myoclonic epilepsy",
        diag_category="Epilepsy",
    )


def test_diagnosis_comorbidity_noise_includes_episodic_migraine() -> None:
    assert dx.is_diagnosis_convention_noise(
        "Episodic migraine",
        evidence="Diagnosis: Episodic migraine",
        diag_category="Epilepsy",
    )


def test_compound_valproate_formulation_normalizes_to_base_drug() -> None:
    assert rx.normalize_drug_name("Valproate as Episenta") == "sodium-valproate"


def test_planned_start_regimen_is_gold_free() -> None:
    assert rx.is_planned_start_prescription(
        "levetiracetam",
        evidence="he starts levetiracetam at a dose of 250mg once-a-day",
        attributes={"DrugName": "levetiracetam"},
    )
    assert rx.is_planned_start_prescription(
        "lamotrigine",
        evidence="Medications: to start lamotrigine, as detailed below",
        attributes={"DrugName": "lamotrigine", "DrugDose": "25"},
    )
    assert rx.is_planned_start_prescription(
        "eslicarbazepine",
        evidence="I will start eslicarbazepine 400mg increasing to 800mg after 1 week",
        attributes={
            "DrugName": "eslicarbazepine",
            "DrugDose": "400mg increasing to 800mg after 1 week",
        },
    )
    assert not rx.is_planned_start_prescription(
        "lamotrigine",
        evidence="Current anti-epileptic medication: lamotrigine 75mg bd",
        attributes={"DrugName": "lamotrigine"},
    )
    assert not rx.is_planned_start_prescription(
        "lamotrigine",
        evidence="Lamotrigine 50mg am, 75mg pm increasing by 25mg increments every 2 weeks",
        attributes={
            "DrugName": "lamotrigine",
            "DrugDose": "50mg am, 75mg pm increasing by 25mg increments every 2 weeks",
        },
    )


def test_fused_am_pm_drugdose_splits_into_two_once_daily_mentions() -> None:
    rows = rx.split_daily_dose_regimen(
        "Epilim",
        evidence=(
            "He is on Epilim 300 mg in the morning and 600 mg in the evening "
            "and carbamazepine 300mg bd."
        ),
        attributes={
            "DrugName": "epilim",
            "DrugDose": "300 mg in the morning and 600 mg in the evening",
            "DoseUnit": "mg",
            "Frequency": "2",
        },
    )
    assert [row[1]["DrugDose"] for row in rows] == ["300", "600"]
    assert {row[1]["Frequency"] for row in rows} == {"1"}


def test_jme_covers_sibling_jerk_and_absence() -> None:
    kept = [
        {"text": "juvenile myoclonic epilepsy", "attributes": {"DiagCategory": "Epilepsy"}},
        {"text": "tonic clonic seizures", "attributes": {"DiagCategory": "MultipleSeizures"}},
        {"text": "myoclonic jerk", "attributes": {"DiagCategory": "MultipleSeizures"}},
        {"text": "absences", "attributes": {"DiagCategory": "MultipleSeizures"}},
    ]
    after = dx.drop_syndrome_covered_phenotypes(kept)
    assert [item["text"] for item in after] == [
        "juvenile myoclonic epilepsy",
        "tonic clonic seizures",
    ]


def test_singular_myoclonic_jerk_is_standalone_noise() -> None:
    assert dx.is_diagnosis_convention_noise(
        "myoclonic jerk",
        evidence="generalised tonic clonic seizures with myoclonic jerks, possible JME",
        diag_category="MultipleSeizures",
    )


def test_non_antiepileptic_drug_is_gold_free_exclusion() -> None:
    assert rx.is_non_antiepileptic_prescription(
        "Mirtazapine", evidence="Mirtazapine 15mg od", attributes={"DrugName": "mirtazapine"}
    )
    assert not rx.is_non_antiepileptic_prescription(
        "lamotrigine", evidence="lamotrigine 75mg bd", attributes={"DrugName": "lamotrigine"}
    )
    assert not rx.is_non_antiepileptic_prescription(
        "clobazam", evidence="clobazam as required", attributes={"DrugName": "clobazam"}
    )
