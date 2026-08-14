from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_lifetime_oneoff as lifetime_oneoff,
)

apply_lifetime_oneoff_active_rate_drop = (
    lifetime_oneoff.apply_lifetime_oneoff_active_rate_drop
)


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def test_drops_only_every_had_one_at_age() -> None:
    mentions = [
        _sf(
            "secondarily generalised seizures",
            "She has only every had one secondarily generalised seizures "
            "which happend when she was 22, the morning after a night out.",
            NumberOfSeizures="1",
            TimeSince_or_TimeOfEvent="During",
            AgeLower="22",
            AgeUnit="Year",
            CUI="C0270838",
        )
    ]
    after, actions = apply_lifetime_oneoff_active_rate_drop(mentions)
    assert after == []
    assert actions[0]["action"] == "drop"


def test_drops_year_of_diagnosis_count() -> None:
    mentions = [
        _sf(
            "focal to bilateral convulsive seizures",
            "He can get infrequent focal to bilateral convulsive seizures "
            "having around two in the year of his diagnosis",
            NumberOfSeizures="2",
            TimeSince_or_TimeOfEvent="During",
            YearDate="2003",
            CUI="C0877017",
        )
    ]
    after, actions = apply_lifetime_oneoff_active_rate_drop(mentions)
    assert after == []
    assert actions[0]["action"] == "drop"


def test_keeps_weekly_rate_whose_evidence_also_mentions_only_ever() -> None:
    mentions = [
        _sf(
            "focal seizures",
            "They are happening weekly. He has only ever had one episode "
            "of loss of consciousness.",
            NumberOfSeizures="1",
            NumberOfTimePeriods="1",
            TimePeriod="Week",
            CUI="C0751495",
        )
    ]
    after, actions = apply_lifetime_oneoff_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_year_stamped_count_without_lifetime_cue() -> None:
    mentions = [
        _sf(
            "generalised tonic clonic seizures",
            "2 generalised tonic clonic seizures 2014",
            NumberOfSeizures="2",
            YearDate="2014",
            CUI="C0494475",
        )
    ]
    after, actions = apply_lifetime_oneoff_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_keeps_seizure_free() -> None:
    mentions = [
        _sf(
            "seizures",
            "only ever had one seizure when she was 22",
            NumberOfSeizures="0",
            AgeLower="22",
        )
    ]
    after, actions = apply_lifetime_oneoff_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []
