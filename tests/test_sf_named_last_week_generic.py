from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_named_last_week_generic as named_last_week,
)

apply_named_last_week_generic_retarget = (
    named_last_week.apply_named_last_week_generic_retarget
)


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def test_retargets_named_last_week_when_same_type_unknown() -> None:
    mentions = [
        _sf(
            "focal dyscognitive seizures",
            "She gets frequent focal dyscognitive seizures in clusters.",
            FrequencyChange="Frequent",
            CUI="C0270834",
        ),
        _sf(
            "focal dyscognitive seizures",
            "Last week she had around 10-15 of these seizures over 2 days.",
            LowerNumberOfSeizures="10",
            UpperNumberOfSeizures="15",
            PointInTime="Last_Week",
            TimeSince_or_TimeOfEvent="During",
            CUI="C0270834",
        ),
    ]
    after, actions = apply_named_last_week_generic_retarget(mentions)
    assert after[0]["attributes"]["CUI"] == "C0270834"
    assert after[1]["attributes"]["CUI"] == "C0036572"
    assert actions[0]["action"] == "retarget"


def test_keeps_named_last_week_without_unknown_sibling() -> None:
    mentions = [
        _sf(
            "generalised tonic clonic seizure",
            "Unfortunately he forgot to take his normal dose of carbamazepine "
            "last week and had a generalised tonic clonic seizure.",
            NumberOfSeizures="1",
            PointInTime="Last_Week",
            TimeSince_or_TimeOfEvent="During",
            CUI="C0494475",
        )
    ]
    after, actions = apply_named_last_week_generic_retarget(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_named_last_week_when_unknown_is_a_different_type() -> None:
    mentions = [
        _sf(
            "focal seizures",
            "frequent focal seizures",
            FrequencyChange="Frequent",
            CUI="C0751495",
        ),
        _sf(
            "generalised tonic clonic seizure",
            "Last week she had a generalised tonic clonic seizure.",
            NumberOfSeizures="1",
            PointInTime="Last_Week",
            CUI="C0494475",
        ),
    ]
    after, actions = apply_named_last_week_generic_retarget(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_named_weekly_rate() -> None:
    mentions = [
        _sf(
            "Focal seizures with altered awareness",
            "1 seizure per week to 1 seizure every month\n"
            "Focal seizures with altered awareness",
            NumberOfSeizures="1",
            LowerNumberOfTimePeriods="1",
            UpperNumberOfTimePeriods="4",
            TimePeriod="Week",
            CUI="C0270834",
        )
    ]
    after, actions = apply_named_last_week_generic_retarget(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_drugchange_named_active_rate() -> None:
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
            "focal seizures",
            "The focal seizures were occurring more frequently, perhaps "
            "once per day before the carbamazepine was introduced.",
            NumberOfSeizures="1",
            PointInTime="DrugChange",
            TimeSince_or_TimeOfEvent="Since",
            CUI="C0751495",
        ),
    ]
    after, actions = apply_named_last_week_generic_retarget(mentions)
    assert after == mentions
    assert actions == []
