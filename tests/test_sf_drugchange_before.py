from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_drugchange_before as drugchange_before,
)

apply_drugchange_before_active_rate_drop = (
    drugchange_before.apply_drugchange_before_active_rate_drop
)


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def test_drops_named_drugchange_before_rate() -> None:
    mentions = [
        _sf(
            "focal motor seizures",
            "Focal motor seizures, (left arm jerks) 2-3 per month",
            LowerNumberOfSeizures="2",
            UpperNumberOfSeizures="3",
            NumberOfTimePeriods="1",
            TimePeriod="Month",
            CUI="C0016399",
        ),
        _sf(
            "focal to bilateral convulsive seizures",
            "Focal to bilateral convulsive seizures, last event 2015",
            NumberOfSeizures="0",
            TimeSince_or_TimeOfEvent="Since",
            YearDate="2015",
            CUI="C0877017",
        ),
        _sf(
            "focal seizures",
            "The focal seizures were occurring more frequently, perhaps "
            "once per day before the carbamazepine was introduced.",
            NumberOfSeizures="1",
            PointInTime="DrugChange",
            TimeSince_or_TimeOfEvent="Since",
            CUI="C0751495",
        ),
    ]
    after, actions = apply_drugchange_before_active_rate_drop(mentions)
    assert after == mentions[:2]
    assert actions[0]["action"] == "drop"


def test_keeps_drugchange_current_rate_without_before() -> None:
    mentions = [
        _sf(
            "seizures",
            "During the time that he has been on lamotrigine he has "
            "continued to have seizures around once per week.",
            NumberOfSeizures="1",
            NumberOfTimePeriods="1",
            TimePeriod="Week",
            PointInTime="DrugChange",
            CUI="C0036572",
        )
    ]
    after, actions = apply_drugchange_before_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_named_weekly_without_drugchange() -> None:
    mentions = [
        _sf(
            "Focal seizures with altered awareness",
            "1 seizure per week to 1 seizure every month",
            NumberOfSeizures="1",
            LowerNumberOfTimePeriods="1",
            UpperNumberOfTimePeriods="4",
            TimePeriod="Week",
            CUI="C0270834",
        )
    ]
    after, actions = apply_drugchange_before_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_year_stamp() -> None:
    mentions = [
        _sf(
            "focal to bilateral convulsive seizure",
            "focal to bilateral convulsive seizure 2019",
            NumberOfSeizures="1",
            YearDate="2019",
            CUI="C0877017",
        )
    ]
    after, actions = apply_drugchange_before_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_drugchange_seizure_free() -> None:
    mentions = [
        _sf(
            "seizures",
            "seizure free since starting lamotrigine before this clinic",
            NumberOfSeizures="0",
            PointInTime="DrugChange",
            CUI="C0751495",
        )
    ]
    after, actions = apply_drugchange_before_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []
