"""Gold-free mechanism tests for rules-only Prescription extraction."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    prescription as rx,
)


def _prescriptions(text: str) -> list[tuple[str, str, str, str]]:
    mentions = rx._extract_prescriptions(text)
    return [
        (
            m.attributes.get("DrugName", ""),
            m.attributes.get("DrugDose", ""),
            m.attributes.get("DoseUnit", ""),
            m.attributes.get("Frequency", ""),
        )
        for m in mentions
    ]


def test_future_start_recommendation_is_dropped() -> None:
    text = (
        "Medication: To start Carbamazepine 100mg bd increasing gradually to 400mg bd. "
        "Could you please commence him of Carbamazepine 100mg bd increasing by 100mg."
    )
    assert _prescriptions(text) == []


def test_suggest_start_alternative_is_dropped_while_current_kept() -> None:
    text = (
        "She was commenced on Sodium Valproate following her seizure cluster "
        "and is now on 400mg bd. "
        "I suggest we start her on Levetiracetam 250mg od increasing by 250mg increments "
        "weekly until she reaches 500mg bd."
    )
    assert _prescriptions(text) == [("sodium-valproate", "400", "mg", "2")]


def test_plan_titration_schedule_is_dropped_while_baseline_kept() -> None:
    text = (
        "Medication:\tLamotrigine 125mg twice daily "
        "(please increase with immediate effect in 25mg increments to 150mg twice daily)\n"
        "Plan: \t\tWeek 1&2: Lamotrigine 125mg AM, 150mg PM\n"
        "Week 3 & Continue: Lamotrigine 150mg twice daily\n"
    )
    assert _prescriptions(text) == [("lamotrigine", "125", "mg", "2")]


def test_please_prescribe_future_start_is_dropped() -> None:
    text = (
        "Medication:\tTo start eslicarbazepine as detailed below\n"
        "Please can you prescribe eslicarbazepine 400mg od, increasing to 800mg od after 1 week."
    )
    assert _prescriptions(text) == []


def test_hypothetical_future_start_is_dropped() -> None:
    text = (
        "Currently he would prefer to hold off medication. "
        "If he decided to start medication then I would suggest maybe Levetiracetam 250 mg od."
    )
    assert _prescriptions(text) == []
