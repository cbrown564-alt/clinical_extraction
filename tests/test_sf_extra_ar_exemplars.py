"""Exemplars for landed ExECT SF extra-AR ownership rules.

One fire and one refuse per living family. Closed type-key study arms stay
in artifacts, not pytest. Intermediate keep/drop edges live in git history.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding as encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_bare_count_active_rate as bare_count,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_cui_phrase_preserve as cui_phrase_preserve,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_dated_cluster as dated_cluster,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_drugchange_before as drugchange_before,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_last_event_duration as last_event,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_lifetime_oneoff as lifetime_oneoff,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_named_last_week_generic as named_last_week,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_scope_residue as residue,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_umbrella_clone as umbrella_clone,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    assign_cui,
)


def _sf(text: str, evidence: str | None = None, **attrs: str) -> dict[str, object]:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "attributes": dict(attrs),
        "evidence": evidence or text,
    }


def test_encoding_last_event_no_count_becomes_zero_since() -> None:
    mentions = [
        _sf(
            "seizures",
            "Last event was in July 2016 and she has had no seizures since.",
            NumberOfSeizures="no",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    assert after[0]["attributes"]["NumberOfSeizures"] == "0"
    assert after[0]["attributes"]["TimeSince_or_TimeOfEvent"] == "Since"
    assert any(item["rule_id"] == "encoding.last_event_zero" for item in actions)


def test_encoding_last_clinic_range_is_not_zeroed() -> None:
    mentions = [
        _sf(
            "seizures",
            "Several seizures since the last clinic appointment.",
            NumberOfSeizures="several",
            PointInTime="LastClinic",
            TimeSince_or_TimeOfEvent="Since",
        )
    ]
    after, actions = encoding.apply_sf_attribute_encoding(mentions)
    assert after[0]["attributes"].get("NumberOfSeizures") != "0"
    assert all(item["rule_id"] != "encoding.last_event_zero" for item in actions)


def test_bare_count_drops_even_when_cui_is_attached() -> None:
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
    after, actions = bare_count.apply_bare_count_active_rate_drop(mentions)
    assert [mention["attributes"].get("NumberOfSeizures") for mention in after] == ["0"]
    assert actions[0]["action"] == "drop"


def test_bare_count_keeps_framed_active_rate() -> None:
    mentions = [
        _sf("seizures", NumberOfSeizures="3", TimePeriod="Month", NumberOfTimePeriods="1")
    ]
    after, actions = bare_count.apply_bare_count_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_cui_phrase_preserves_cluster_and_rewrites_generic() -> None:
    assert assign_cui("cluster of seizures") == "C3203523"
    mentions = [_sf("cluster of seizures", CUI="C0036572", NumberOfSeizures="3")]
    after, actions = cui_phrase_preserve.apply_cui_phrase_preserve(
        mentions, arm="preserve_cluster_cui"
    )
    assert after[0]["attributes"]["CUI"] == "C3203523"
    assert actions[0]["action"] == "preserve_cluster_cui"


def test_cui_phrase_does_not_overwrite_specific_cui() -> None:
    mentions = [_sf("cluster of seizures", CUI="C0494475")]
    after, actions = cui_phrase_preserve.apply_cui_phrase_preserve(
        mentions, arm="preserve_cluster_cui"
    )
    assert after[0]["attributes"]["CUI"] == "C0494475"
    assert actions == []


def test_dated_cluster_drops_generic_next_to_seizure_free() -> None:
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
    after, actions = dated_cluster.apply_dated_cluster_next_to_free_drop(mentions)
    assert after == [mentions[0]]
    assert actions[0]["action"] == "drop"


def test_dated_cluster_keeps_named_cluster_next_to_free() -> None:
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
    after, actions = dated_cluster.apply_dated_cluster_next_to_free_drop(mentions)
    assert after == mentions
    assert actions == []


def test_drugchange_before_drops_named_historical_rate() -> None:
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
    after, actions = drugchange_before.apply_drugchange_before_active_rate_drop(mentions)
    assert after == [mentions[0]]
    assert actions[0]["action"] == "drop"


def test_drugchange_before_keeps_current_rate_without_before() -> None:
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
    after, actions = drugchange_before.apply_drugchange_before_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_drugchange_sibling_drops_when_current_named_rate_exists() -> None:
    historical = _sf(
        "focal seizures",
        "The focal seizures were occurring more frequently, perhaps "
        "once per day before the carbamazepine was introduced.",
        NumberOfSeizures="1",
        PointInTime="DrugChange",
        TimeSince_or_TimeOfEvent="Since",
        CUI="C0751495",
    )
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
        historical,
    ]
    after, actions = drugchange_before.apply_drugchange_before_sibling_drop(mentions)
    assert after == [mentions[0]]
    assert actions[0]["action"] == "drop"


def test_drugchange_sibling_keeps_when_it_is_the_only_active_rate() -> None:
    mentions = [
        _sf(
            "focal seizures",
            "The focal seizures were occurring more frequently, perhaps "
            "once per day before the carbamazepine was introduced.",
            NumberOfSeizures="1",
            PointInTime="DrugChange",
            TimeSince_or_TimeOfEvent="Since",
            CUI="C0751495",
        )
    ]
    after, actions = drugchange_before.apply_drugchange_before_sibling_drop(mentions)
    assert after == mentions
    assert actions == []


def test_last_event_converts_single_seizure_n_weeks_ago() -> None:
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
    after, actions = last_event.apply_last_event_duration_complete(mentions)
    attrs = after[0]["attributes"]
    assert attrs["NumberOfSeizures"] == "0"
    assert attrs["NumberOfTimePeriods"] == "3"
    assert "TimeSince_or_TimeOfEvent" not in attrs
    assert actions[0]["action"] == "repair"


def test_last_event_keeps_current_rate_without_ago_duration() -> None:
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
    after, actions = last_event.apply_last_event_duration_complete(mentions)
    assert after == mentions
    assert actions == []


def test_lifetime_oneoff_drops_only_every_had_one_at_age() -> None:
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
    after, actions = lifetime_oneoff.apply_lifetime_oneoff_active_rate_drop(mentions)
    assert after == []
    assert actions[0]["action"] == "drop"


def test_lifetime_oneoff_keeps_weekly_rate_with_only_ever_aside() -> None:
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
    after, actions = lifetime_oneoff.apply_lifetime_oneoff_active_rate_drop(mentions)
    assert after == mentions
    assert actions == []


def test_named_last_week_retargets_when_same_type_unknown() -> None:
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
    after, actions = named_last_week.apply_named_last_week_generic_retarget(mentions)
    assert after[1]["attributes"]["CUI"] == "C0036572"
    assert actions[0]["action"] == "retarget"


def test_named_last_week_keeps_without_unknown_sibling() -> None:
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
    after, actions = named_last_week.apply_named_last_week_generic_retarget(mentions)
    assert after == mentions
    assert actions == []


def test_scope_residue_drops_bare_episode_token() -> None:
    mentions = [
        _sf(
            "episodes",
            "The frequency of these appears to be increasing to almost daily.",
            FrequencyChange="Increased",
            TimePeriod="Day",
        ),
        _sf(
            "seizures",
            "He has not had any further seizures since his last appointment.",
            NumberOfSeizures="0",
            TimeSince_or_TimeOfEvent="Since",
        ),
    ]
    after, actions = residue.apply_scope_residue_drop(mentions)
    assert [mention["text"] for mention in after] == ["seizures"]
    assert actions[0]["reason"] == "bare_symptom_token"


def test_scope_residue_drops_febrile_history_not_current_free() -> None:
    mentions = [
        _sf(
            "febrile seizures",
            "He had 4 febrile seizures at the age of 3, 4 and then around five.",
            NumberOfSeizures="4",
        ),
        _sf(
            "seizures",
            "He has been seizure free since his teenage years.",
            NumberOfSeizures="0",
            TimeSince_or_TimeOfEvent="Since",
        ),
    ]
    after, actions = residue.apply_scope_residue_drop(mentions)
    assert [mention["text"] for mention in after] == ["seizures"]
    assert actions[0]["reason"] == "febrile_history"


def test_umbrella_clone_drops_generic_clone_of_specific_span() -> None:
    span = "focal to bilateral seizures 2 events in total, last event 10 years ago."
    mentions = [
        _sf(
            "focal seizures with altered awareness",
            "focal seizures with altered awareness, last event 3 years ago",
            CUI="C0270834",
            NumberOfSeizures="0",
            NumberOfTimePeriods="3",
            TimePeriod="Year",
        ),
        _sf(
            "seizures",
            span,
            CUI="C0036572",
            NumberOfSeizures="0",
            NumberOfTimePeriods="10",
            TimePeriod="Year",
        ),
        _sf(
            "focal to bilateral seizures",
            span,
            CUI="C0877017",
            NumberOfSeizures="0",
            NumberOfTimePeriods="10",
            TimePeriod="Year",
        ),
    ]
    after, actions = umbrella_clone.apply_umbrella_clone_drop(mentions)
    sf = [mention for mention in after if mention["entity"] == "SeizureFrequency"]
    assert [mention["attributes"]["CUI"] for mention in sf] == ["C0270834", "C0877017"]
    assert actions[0]["action"] == "drop"


def test_umbrella_clone_keeps_generic_when_evidence_differs() -> None:
    mentions = [
        _sf(
            "focal to bilateral convulsive seizures",
            "focal to bilateral convulsive seizures, last event 2018",
            CUI="C0877017",
            NumberOfSeizures="0",
        ),
        _sf(
            "seizure free",
            "he remains seizure free after his surgery.",
            CUI="C1299590",
            NumberOfSeizures="0",
        ),
    ]
    after, actions = umbrella_clone.apply_umbrella_clone_drop(mentions)
    assert [mention["attributes"]["CUI"] for mention in after] == ["C0877017", "C1299590"]
    assert actions == []
