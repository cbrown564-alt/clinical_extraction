from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_bare_count_active_rate as bare_count,
)

apply_bare_count_active_rate_drop = bare_count.apply_bare_count_active_rate_drop


def _sf(text: str, **attrs: str) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": text,
    }


def test_drops_bare_count_even_when_cui_is_attached() -> None:
    mentions = [
        _sf("seizures", CUI="C0036572", CUIPhrase="seizures", NumberOfSeizures="3"),
        _sf(
            "seizures",
            CUI="C0036572",
            NumberOfSeizures="0",
            NumberOfTimePeriods="2",
            TimePeriod="Year",
        ),
    ]
    after, actions = apply_bare_count_active_rate_drop(mentions)
    assert [m["attributes"].get("NumberOfSeizures") for m in after] == ["0"]
    assert actions[0]["action"] == "drop"


def test_keeps_framed_active_rate() -> None:
    mentions = [
        _sf("seizures", NumberOfSeizures="3", TimePeriod="Month", NumberOfTimePeriods="1")
    ]
    after, actions = apply_bare_count_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_dated_active_rate() -> None:
    mentions = [_sf("seizures", NumberOfSeizures="2", YearDate="2018")]
    after, actions = apply_bare_count_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_seizure_free_zero_count() -> None:
    mentions = [_sf("seizures", NumberOfSeizures="0")]
    after, actions = apply_bare_count_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_named_bare_count_when_only_generic_active_rate_remains() -> None:
    mentions = [
        _sf(
            "generalised tonic clonic seizure",
            CUI="C0494475",
            CUIPhrase="generalised tonic clonic seizure",
            NumberOfSeizures="1",
        ),
        _sf(
            "seizure",
            CUI="C0036572",
            CUIPhrase="seizure",
            NumberOfSeizures="1",
            PointInTime="Last_Year",
            TimePeriod="Year",
            TimeSince_or_TimeOfEvent="Since",
        ),
    ]
    after, actions = apply_bare_count_active_rate_drop(mentions)
    assert [m["attributes"].get("CUI") for m in after] == ["C0494475", "C0036572"]
    assert actions == []


def test_drops_bare_lower_bound() -> None:
    mentions = [_sf("seizures", LowerNumberOfSeizures="2")]
    after, actions = apply_bare_count_active_rate_drop(mentions)
    assert after == []
    assert actions[0]["action"] == "drop"
