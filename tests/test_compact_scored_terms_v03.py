"""Score explicit conditions without turning ordinary triggers into populations."""

from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    compact_scored_terms_v03 as terms,
)


def claim(kind: str, label: str, restriction: str | None) -> dict:
    return {"event": {"scope": "named", "label": label},
            "measurement": {"kind": kind}, "restriction": restriction}


def test_explicit_qualitative_conditions_are_scored() -> None:
    assert terms.restriction_key(claim("qualitative", "spells", "when meals are regular")) == (
        "regular_meals_condition",
    )
    assert terms.restriction_key(
        claim("qualitative", "generalised convulsions", "if the cluster is prolonged")
    ) == ("prolonged_cluster_condition",)
    assert terms.restriction_key(
        claim("qualitative", "focal aware auras", "perimenstrual only (days -2 to +2)")
    ) == ("within_menstrual_window",)


def test_incidental_qualitative_associations_remain_optional() -> None:
    assert terms.restriction_key(
        claim("qualitative", "seizure clusters", "when sleep is restricted offshore")
    ) == ()
    assert terms.restriction_key(
        claim("qualitative", "absence clusters", "on workdays when he skips breakfast")
    ) == ()


def test_observed_clinical_absence_remains_limited() -> None:
    assert terms.restriction_key(claim("seizure_free", "clinical seizures", "observed")) == (
        "clinical_only",
        "observed_only",
    )
    assert terms.restriction_key(claim("seizure_free", "clinical seizures", None)) == (
        "clinical_only",
    )
    assert terms.restriction_key(claim("seizure_free", "clinical seizures observed", None)) == (
        "clinical_only",
        "observed_only",
    )
