from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_drugchange_before as drugchange_before,
)

apply_drugchange_before_sibling_drop = (
    drugchange_before.apply_drugchange_before_sibling_drop
)


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def _extra() -> dict:
    return _sf(
        "focal seizures",
        "The focal seizures were occurring more frequently, perhaps "
        "once per day before the carbamazepine was introduced.",
        NumberOfSeizures="1",
        PointInTime="DrugChange",
        TimeSince_or_TimeOfEvent="Since",
        CUI="C0751495",
    )


def test_drops_when_current_named_rate_exists() -> None:
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
        _extra(),
    ]
    after, actions = apply_drugchange_before_sibling_drop(mentions)
    assert after == [mentions[0]]
    assert actions[0]["action"] == "drop"


def test_keeps_when_it_is_the_only_active_rate() -> None:
    mentions = [_extra()]
    after, actions = apply_drugchange_before_sibling_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_named_weekly() -> None:
    mentions = [
        _sf(
            "Focal seizures with altered awareness",
            "1 seizure per week",
            NumberOfSeizures="1",
            TimePeriod="Week",
            CUI="C0270834",
        )
    ]
    after, actions = apply_drugchange_before_sibling_drop(mentions)
    assert after == mentions
    assert actions == []
