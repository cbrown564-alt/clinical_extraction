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
