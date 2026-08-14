from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_dated_cluster as dated_cluster,
)

apply_dated_cluster_next_to_free_drop = dated_cluster.apply_dated_cluster_next_to_free_drop


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def test_drops_generic_december_cluster_next_to_seizure_free() -> None:
    mentions = [
        _sf(
            "seizures",
            "Since I last saw John he has not had any more seizures",
            NumberOfSeizures="0",
            PointInTime="LastClinic",
            TimeSince_or_TimeOfEvent="Since",
            CUI="C0036572",
        ),
        _sf(
            "seizures",
            "he did have a cluster of three seizures in a 24-hr period in Devember",
            NumberOfSeizures="3",
            NumberOfTimePeriods="1",
            TimePeriod="Day",
            TimeSince_or_TimeOfEvent="During",
            MonthDate="12",
            CUI="C0036572",
        ),
    ]
    after, actions = apply_dated_cluster_next_to_free_drop(mentions)
    assert after == [mentions[0]]
    assert actions[0]["action"] == "drop"


def test_keeps_named_cluster_next_to_predicted_free() -> None:
    mentions = [
        _sf(
            "seizures",
            "After a fairly long period of around 6 months without having seizures",
            NumberOfSeizures="0",
            NumberOfTimePeriods="6",
            TimePeriod="Month",
            CUI="C0036572",
        ),
        _sf(
            "cluster of seizures",
            "unfortunately Mr Francis had a cluster of seizures over the weekend",
            NumberOfSeizures="1",
            DayDate="weekend",
            CUI="C3203523",
        ),
    ]
    after, actions = apply_dated_cluster_next_to_free_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_generic_dated_cluster_without_free_sibling() -> None:
    mentions = [
        _sf(
            "seizures",
            "Currently she get around 2-4 seizures per month.",
            LowerNumberOfSeizures="2",
            UpperNumberOfSeizures="4",
            NumberOfTimePeriods="1",
            TimePeriod="Month",
            CUI="C0036572",
        ),
        _sf(
            "seizures",
            "Although she did have a cluster of seizures in August, 2017 "
            "where she had 6-9 seizures every week for 3 weeks.",
            LowerNumberOfSeizures="6",
            UpperNumberOfSeizures="9",
            NumberOfTimePeriods="1",
            TimePeriod="Week",
            TimeSince_or_TimeOfEvent="During",
            MonthDate="8",
            YearDate="2017",
            CUI="C0036572",
        ),
    ]
    after, actions = apply_dated_cluster_next_to_free_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_year_stamp_without_cluster_word() -> None:
    mentions = [
        _sf(
            "seizures",
            "He has been seizure free since starting lamotrigine",
            NumberOfSeizures="0",
            CUI="C0036572",
        ),
        _sf(
            "focal to bilateral convulsive seizure",
            "focal to bilateral convulsive seizure 2019",
            NumberOfSeizures="1",
            YearDate="2019",
            CUI="C0877017",
        ),
    ]
    after, actions = apply_dated_cluster_next_to_free_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_current_weekly_rate() -> None:
    mentions = [
        _sf(
            "seizures",
            "The smaller versions of the attacks can happen several times per week.",
            NumberOfSeizures="3",
            NumberOfTimePeriods="1",
            TimePeriod="Week",
            CUI="C0036572",
        )
    ]
    after, actions = apply_dated_cluster_next_to_free_drop(mentions)
    assert after == mentions
    assert actions == []
