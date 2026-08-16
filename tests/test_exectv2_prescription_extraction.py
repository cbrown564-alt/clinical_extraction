"""Exemplars for rules-only Prescription extraction."""

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
