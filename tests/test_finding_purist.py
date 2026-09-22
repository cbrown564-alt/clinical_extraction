"""Finding Purist inventory score. The exact matcher remains a separate result."""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_purist as purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r8 as r8


def finding(
    fid: str, label: str, measurement: dict[str, Any], evidence: str, **extra: Any
) -> dict[str, Any]:
    return {
        "id": fid,
        "event": {"type": label, "scope": r8.derive_scope(label), "seizure_status": "stated"},
        "measurement": measurement,
        "timing": "current",
        "evidence": evidence,
        **extra,
    }


def rate(count: float, per: float, unit: str = "week") -> dict[str, Any]:
    return {
        "type": "rate",
        "count": {"type": "number", "value": count},
        "per": {"type": "number", "value": per, "unit": unit},
    }


def assert_pair(
    note: str,
    ref: dict[str, Any],
    pred: dict[str, Any],
    *,
    purist_match: bool,
    exact_match: bool,
) -> None:
    got = purist.score_letter(note, [ref], [pred])
    frozen = exact.score_letter(note, [ref], [pred])
    assert got["tp"] == int(purist_match)
    assert frozen["tp"] == int(exact_match)


def test_finding_purist_fixture_contract() -> None:
    """The named cases that freeze Finding Purist apart from the exact matcher."""
    weekly = "She has seizures every six weeks."
    same_band = finding("r", "seizures", rate(2, 6), "every six weeks")
    other_band = finding("p", "seizures", rate(3, 6), "every six weeks")
    assert purist.purist_band(same_band) == purist.purist_band(other_band)
    assert_pair(weekly, same_band, other_band, purist_match=True, exact_match=False)

    daily = "She has one seizure a day."
    assert_pair(
        daily,
        finding("r", "seizures", rate(1, 1, "day"), "one seizure a day"),
        finding("p", "seizures", rate(1, 1, "week"), "one seizure a day"),
        purist_match=False,
        exact_match=False,
    )

    window = "Patient reports seizures every 6 days over the past two months."
    kept = finding("r", "seizures", rate(1, 6, "day"), "seizures every 6 days")
    omitted = finding(
        "p",
        "seizures",
        rate(1, 6, "day"),
        "seizures every 6 days",
        period={"time": "over the past two months"},
    )
    assert_pair(window, omitted, kept, purist_match=True, exact_match=False)

    status = finding(
        "p",
        "seizures",
        rate(1, 6, "day"),
        "seizures every 6 days",
        event={"type": "seizures", "scope": "unspecified", "seizure_status": "uncertain"},
    )
    assert_pair(window, kept, status, purist_match=True, exact_match=False)

    wording = "Rarer generalised tonic-clonic seizures continue."
    quote = "Rarer generalised tonic-clonic seizures"
    synonym = {"type": "qualitative", "frequency": "occasional"}
    mapped = {"type": "qualitative", "frequency": "intermittent"}
    assert_pair(
        wording,
        finding("r", "generalised tonic-clonic seizures", synonym, quote),
        finding("p", "generalised tonic-clonic seizures", mapped, "tonic-clonic seizures"),
        purist_match=True,
        exact_match=False,
    )
    contradiction = {"type": "qualitative", "frequency": "rare"}
    decreased = {"type": "qualitative", "frequency": "decreased"}
    assert_pair(
        wording,
        finding("r", "generalised tonic-clonic seizures", contradiction, quote),
        finding("p", "generalised tonic-clonic seizures", decreased, "tonic-clonic seizures"),
        purist_match=False,
        exact_match=False,
    )

    absence = "She has had no seizures for six months."
    six_months = finding(
        "r",
        "seizures",
        {"type": "seizure_free", "duration": {"type": "number", "value": 6, "unit": "month"}},
        "no seizures for six months",
    )
    two_weeks = finding(
        "p",
        "seizures",
        {"type": "seizure_free", "duration": {"type": "number", "value": 2, "unit": "week"}},
        "no seizures for six months",
    )
    assert_pair(absence, six_months, two_weeks, purist_match=False, exact_match=False)
    collapsed = purist.score_letter(absence, [six_months], [two_weeks], collapse_seizure_free=True)
    assert collapsed["tp"] == 1
    since = "No generalised seizures since March."
    march = {"type": "seizure_free", "since": {"time": "March", "form": "calendar"}}
    since_march = {"type": "seizure_free", "since": {"time": "since March", "form": "relative"}}
    assert_pair(
        since,
        finding("r", "generalised seizures", march, "since March"),
        finding("p", "generalised seizures", since_march, "since March"),
        purist_match=True,
        exact_match=True,
    )

    renamed = "She has weekly events."
    assert_pair(
        renamed,
        finding("r", "absences", rate(1, 1), "weekly events"),
        finding("p", "generalised tonic-clonic seizures", rate(1, 1), "weekly events"),
        purist_match=False,
        exact_match=False,
    )
    historical = finding(
        "p", "seizures", rate(1, 6, "day"), "seizures every 6 days", timing="historical"
    )
    assert_pair(window, kept, historical, purist_match=False, exact_match=False)

    prose = "Counted 3 seizures since the last review."
    counted = finding(
        "r",
        "seizures",
        {"type": "count", "count": {"type": "number", "value": 3}},
        "Counted 3 seizures",
        period={"time": "since the last review"},
    )
    this_month = finding(
        "p",
        "seizures",
        {"type": "count", "count": {"type": "number", "value": 3}},
        "Counted 3 seizures",
        period={"time": "this month so far"},
    )
    assert purist.purist_band(counted) is None
    assert_pair(prose, counted, this_month, purist_match=False, exact_match=False)
    assert_pair(prose, counted, counted, purist_match=True, exact_match=True)

    duplicate = purist.score_letter(weekly, [same_band], [other_band, other_band | {"id": "q"}])
    assert (duplicate["tp"], duplicate["fp"], duplicate["fn"]) == (1, 1, 0)


def test_unusable_inventory_adds_false_negatives_only() -> None:
    note = "She has seizures every six weeks."
    reference = [finding("r", "seizures", rate(1, 6), "every six weeks")]
    unusable = purist.score_letter(note, reference, None)
    empty_ok = purist.score_letter("No relevant text.", [], [])
    empty_fp = purist.score_letter(note, [], reference)
    summary = purist.aggregate([unusable, empty_ok, empty_fp])
    assert (unusable["usable"], unusable["tp"], unusable["fp"], unusable["fn"]) == (False, 0, 0, 1)
    assert summary["matching_version"] == purist.MATCHING_VERSION
    assert summary["unusable_letters"] == 1
    assert summary["empty_state_correct"] == 1
    assert summary["exact_inventory"] == 1
    assert summary["precision"] == 0.0 and summary["recall"] == 0.0
    companion = purist.aggregate([unusable], collapse_seizure_free=True)
    assert companion["matching_version"] == purist.COLLAPSED_VERSION
