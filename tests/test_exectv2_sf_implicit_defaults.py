"""Encode-time implicit SF defaults: period count 1 and During windows.

Portability: seizure_frequency. These rules fill omitted implicit values on
already-emitted mentions. They do not invent events or standing-rate frames.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding as encoding,
)


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict[str, object]:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def test_per_unit_rate_gets_period_count_one() -> None:
    mentions = [
        _sf(
            "generalised tonic clonic seizures",
            "She had approximately 3-4 generalised tonic clonic seizures per week.",
            LowerNumberOfSeizures="3",
            UpperNumberOfSeizures="4",
            TimePeriod="Week",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    assert after[0]["attributes"]["NumberOfTimePeriods"] == "1"
    assert "TimeSince_or_TimeOfEvent" not in after[0]["attributes"]
    assert any(item["rule_id"] == "encoding.period_count_default" for item in actions)


def test_interval_range_does_not_get_period_count_one() -> None:
    mentions = [
        _sf(
            "seizures",
            "She has seizures every 3 to 4 weeks.",
            NumberOfSeizures="1",
            LowerNumberOfTimePeriods="3",
            UpperNumberOfTimePeriods="4",
            TimePeriod="Week",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    assert "NumberOfTimePeriods" not in after[0]["attributes"]
    assert all(item["rule_id"] != "encoding.period_count_default" for item in actions)


def test_dated_count_gets_during() -> None:
    mentions = [
        _sf(
            "focal seizures",
            "In March she had 2 to 3 of her focal seizures.",
            LowerNumberOfSeizures="2",
            UpperNumberOfSeizures="3",
            MonthDate="3",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    assert after[0]["attributes"]["TimeSince_or_TimeOfEvent"] == "During"
    assert any(item["rule_id"] == "encoding.during_window" for item in actions)


def test_from_to_rate_gets_during_and_period_one() -> None:
    mentions = [
        _sf(
            "generalised tonic clonic seizures",
            "She had approximately 3-4 generalised tonic clonic seizures "
            "per week from May to August.",
            LowerNumberOfSeizures="3",
            UpperNumberOfSeizures="4",
            TimePeriod="Week",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    attrs = after[0]["attributes"]
    assert attrs["NumberOfTimePeriods"] == "1"
    assert attrs["TimeSince_or_TimeOfEvent"] == "During"
    assert {item["rule_id"] for item in actions} >= {
        "encoding.period_count_default",
        "encoding.during_window",
    }


def test_last_week_point_gets_during() -> None:
    mentions = [
        _sf(
            "generalised tonic clonic seizure",
            "He forgot his dose last week and had a generalised tonic clonic seizure.",
            NumberOfSeizures="1",
            PointInTime="Last_Week",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    assert after[0]["attributes"]["TimeSince_or_TimeOfEvent"] == "During"
    assert any(item["rule_id"] == "encoding.during_window" for item in actions)


def test_last_event_stays_since_not_during() -> None:
    mentions = [
        _sf(
            "seizures",
            "Last event was in July 2016 and she has had no seizures since.",
            NumberOfSeizures="no",
            MonthDate="7",
            YearDate="2016",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    assert after[0]["attributes"]["TimeSince_or_TimeOfEvent"] == "Since"
    assert all(item["rule_id"] != "encoding.during_window" for item in actions)


def test_last_clinic_stays_since_not_during() -> None:
    mentions = [
        _sf(
            "secondary generalised seizures",
            "Since her last clinic appointment she has had four secondary "
            "generalised seizures.",
            NumberOfSeizures="4",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    attrs = after[0]["attributes"]
    assert attrs["PointInTime"] == "LastClinic"
    assert attrs["TimeSince_or_TimeOfEvent"] == "Since"
    assert all(item["rule_id"] != "encoding.during_window" for item in actions)
