from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_last_event_duration as last_event,
)

apply_last_event_duration_complete = last_event.apply_last_event_duration_complete
apply_single_last_event = last_event.apply_single_last_event


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def test_converts_single_seizure_n_weeks_ago_even_when_already_framed() -> None:
    mentions = [
        _sf(
            "seizure",
            "She reports having a single seizure some 3 weeks ago.",
            NumberOfSeizures="1",
            NumberOfTimePeriods="3",
            TimePeriod="Week",
            TimeSince_or_TimeOfEvent="During",
            CUI="C0036572",
        )
    ]
    after, actions = apply_last_event_duration_complete(mentions)
    attrs = after[0]["attributes"]
    assert attrs["NumberOfSeizures"] == "0"
    assert attrs["NumberOfTimePeriods"] == "3"
    assert attrs["TimePeriod"] == "Week"
    assert "TimeSince_or_TimeOfEvent" not in attrs
    assert actions[0]["action"] == "repair"


def test_keeps_current_rate_without_ago_duration() -> None:
    mentions = [
        _sf(
            "seizures",
            "They happen about 1-2 per month and are always the same.",
            LowerNumberOfSeizures="1",
            UpperNumberOfSeizures="2",
            NumberOfTimePeriods="1",
            TimePeriod="Month",
        )
    ]
    after, actions = apply_last_event_duration_complete(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_seizure_free() -> None:
    mentions = [
        _sf(
            "seizures",
            "last event 3 weeks ago",
            NumberOfSeizures="0",
            NumberOfTimePeriods="3",
            TimePeriod="Week",
        )
    ]
    after, actions = apply_last_event_duration_complete(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_dated_cluster_without_ago_duration() -> None:
    mentions = [
        _sf(
            "seizures",
            "he did have a cluster of three seizures in a 24-hr period in Devember",
            NumberOfSeizures="3",
            NumberOfTimePeriods="1",
            TimePeriod="Day",
            MonthDate="12",
        )
    ]
    after, actions = apply_last_event_duration_complete(mentions)
    assert after == mentions
    assert actions == []


def test_single_last_event_converts_single_count_one() -> None:
    mentions = [
        _sf(
            "seizure",
            "She reports having a single seizure some 3 weeks ago.",
            NumberOfSeizures="1",
            NumberOfTimePeriods="3",
            TimePeriod="Week",
            TimeSince_or_TimeOfEvent="During",
            CUI="C0036572",
        )
    ]
    after, actions = apply_single_last_event(mentions)
    assert after[0]["attributes"]["NumberOfSeizures"] == "0"
    assert actions[0]["action"] == "repair"


def test_single_last_event_converts_last_seizure_count_one() -> None:
    mentions = [
        _sf(
            "seizure",
            "Her last seizure now was 5 months ago",
            NumberOfSeizures="1",
            NumberOfTimePeriods="5",
            TimePeriod="Month",
            CUI="C0036572",
        )
    ]
    after, actions = apply_single_last_event(mentions)
    assert after[0]["attributes"]["NumberOfSeizures"] == "0"
    assert actions[0]["action"] == "repair"


def test_single_last_event_skips_lifetime_count_last_event() -> None:
    mentions = [
        _sf(
            "focal to bilateral seizures",
            "focal to bilateral seizures 2 events in total, last event 10 years ago.",
            NumberOfSeizures="2",
            NumberOfTimePeriods="10",
            TimePeriod="Year",
            CUI="C0877017",
        )
    ]
    after, actions = apply_single_last_event(mentions)
    assert after == mentions
    assert actions == []


def test_count_is_one_variant_skips_multi_count() -> None:
    mentions = [
        _sf(
            "seizures",
            "he had three seizures about 2 weeks ago",
            NumberOfSeizures="3",
            NumberOfTimePeriods="2",
            TimePeriod="Week",
        )
    ]
    after, actions = apply_last_event_duration_complete(
        mentions, require_count_one=True
    )
    assert after == mentions
    assert actions == []
