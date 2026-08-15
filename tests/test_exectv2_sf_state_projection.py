"""Tests for ExECTv2 SF deterministic state/ownership projection."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection as projection,
)


def _row(*, predicted_mentions, candidate_spans=()):
    return {
        "letter_id": "L1",
        "split": "dev",
        "prompt_version": "exectv2_hybrid_sf_state_adjudicator_v0.5",
        "pipeline_family": "exectv2_hybrid_sf_state_adjudicator",
        "predicted_mentions": list(predicted_mentions),
        "candidate_spans": list(candidate_spans),
        "gold_mentions": [],
        "parse_errors": [],
    }


def test_state_projection_drops_unlabelled_active_rate() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"NumberOfSeizures": "4"},
                "evidence": "Mr Richards has had 4 more attacks.",
            }
        ]
    )

    projected = projection.project_row(row, ablation="state")

    assert projected["predicted_mentions"] == []
    assert projected["projection_actions"][0]["rule_id"] == "state.drop_unlabelled_active_rate"


def test_state_projection_adds_explicit_change_candidate() -> None:
    row = _row(
        predicted_mentions=[],
        candidate_spans=[
            {
                "candidate_type": "generic_qualitative_change",
                "evidence": "Given that she is still having fairly frequent seizures",
                "text_hint": "seizures",
            }
        ],
    )

    projected = projection.project_row(row, ablation="state")

    assert projected["predicted_mentions"][0]["text"] == "seizures"
    assert projected["predicted_mentions"][0]["attributes"]["FrequencyChange"] == "Frequent"
    assert projected["projection_actions"][0]["rule_id"] == "state.change_recovery"


def test_state_projection_repairs_single_event_duration_to_seizure_free() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizure",
                "attributes": {"NumberOfSeizures": "1"},
                "evidence": "She reports having a single seizure some 3 weeks ago.",
            }
        ]
    )

    projected = projection.project_row(row, ablation="state")
    attrs = projected["predicted_mentions"][0]["attributes"]

    assert attrs["NumberOfSeizures"] == "0"
    assert attrs["NumberOfTimePeriods"] == "3"
    assert attrs["TimePeriod"] == "Week"


def test_state_projection_completes_single_last_event_after_temporal_alignment() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizure",
                "attributes": {
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "3",
                    "TimePeriod": "Week",
                    "TimeSince_or_TimeOfEvent": "During",
                },
                "evidence": "She reports having a single seizure some 3 weeks ago.",
            }
        ]
    )

    projected = projection.project_row(row, ablation="state")
    attrs = projected["predicted_mentions"][0]["attributes"]
    rule_ids = [action["rule_id"] for action in projected["projection_actions"]]

    assert attrs["NumberOfSeizures"] == "0"
    assert attrs["NumberOfTimePeriods"] == "3"
    assert attrs["TimePeriod"] == "Week"
    assert "TimeSince_or_TimeOfEvent" not in attrs
    assert "state.last_event_active_to_seizure_free" in rule_ids


def test_ownership_projection_assigns_named_count_to_named_type() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "CUI": "C0036572",
                    "NumberOfSeizures": "2",
                    "TimePeriod": "Year",
                },
                "evidence": "She has had 2 generalised tonic clonic seizures this year.",
            }
        ]
    )

    projected = projection.project_row(row, ablation="ownership")

    assert projected["predicted_mentions"][0]["text"] == "generalised tonic clonic seizures"
    assert projected["predicted_mentions"][0]["attributes"]["CUI"] == "C0494475"
    assert projected["projection_actions"][0]["rule_id"] == "ownership.generic_active_to_named"


def test_combined_drops_generic_clone_after_last_event_conversion() -> None:
    span = "focal to bilateral seizures 2 events in total, last event 10 years ago."
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "focal to bilateral seizures",
                "attributes": {"NumberOfSeizures": "2"},
                "evidence": span,
            },
            {
                "entity": "SeizureFrequency",
                "text": "focal to bilateral seizures",
                "attributes": {
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": "10",
                    "TimePeriod": "Year",
                },
                "evidence": span,
            },
        ]
    )

    projected = projection.project_row(row, ablation="combined")
    cuis = [mention["attributes"].get("CUI") for mention in projected["predicted_mentions"]]
    rule_ids = [action["rule_id"] for action in projected["projection_actions"]]

    assert "C0036572" not in cuis
    assert "C0877017" in cuis
    assert "ownership.drop_umbrella_clone" in rule_ids


def test_combined_preserves_cluster_and_generlised_cuis() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "cluster of seizures",
                "attributes": {"NumberOfSeizures": "3", "TimePeriod": "Day"},
                "evidence": "cluster of seizures",
            },
            {
                "entity": "SeizureFrequency",
                "text": "generlised tonic clonic seizure",
                "attributes": {"NumberOfSeizures": "1", "TimePeriod": "Year"},
                "evidence": "generlised tonic clonic seizure",
            },
        ]
    )

    projected = projection.project_row(row, ablation="combined")
    by_text = {
        mention["text"]: mention["attributes"].get("CUI")
        for mention in projected["predicted_mentions"]
    }

    assert by_text["cluster of seizures"] == "C3203523"
    assert by_text["generlised tonic clonic seizure"] == "C0494475"
    assert projected["projection_version"].endswith("v0.15")


def test_combined_drops_bare_count_active_rate() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"NumberOfSeizures": "3", "CUI": "C0036572"},
                "evidence": "three seizures",
            },
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": "2",
                    "TimePeriod": "Year",
                    "CUI": "C0036572",
                },
                "evidence": "seizure free for 2 years",
            },
        ]
    )

    projected = projection.project_row(row, ablation="combined")
    states = [
        mention["attributes"].get("NumberOfSeizures")
        for mention in projected["predicted_mentions"]
    ]
    rule_ids = [action["rule_id"] for action in projected["projection_actions"]]

    assert "3" not in states
    assert "0" in states
    assert "ownership.drop_bare_count_active_rate" in rule_ids


def test_combined_drops_lifetime_oneoff_active_rate() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "secondarily generalised seizures",
                "attributes": {
                    "NumberOfSeizures": "1",
                    "AgeLower": "22",
                    "AgeUnit": "Year",
                    "CUI": "C0270838",
                },
                "evidence": (
                    "She has only every had one secondarily generalised "
                    "seizures which happend when she was 22."
                ),
            },
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": "5",
                    "TimePeriod": "Year",
                    "CUI": "C0036572",
                },
                "evidence": "seizure free for 5 years",
            },
        ]
    )

    projected = projection.project_row(row, ablation="combined")
    cuis = [mention["attributes"].get("CUI") for mention in projected["predicted_mentions"]]
    rule_ids = [action["rule_id"] for action in projected["projection_actions"]]

    assert "C0270838" not in cuis
    assert "C0036572" in cuis
    assert "ownership.drop_lifetime_oneoff_active_rate" in rule_ids


def test_combined_drops_generic_dated_cluster_next_to_free() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "NumberOfSeizures": "0",
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "CUI": "C0036572",
                },
                "evidence": "Since I last saw John he has not had any more seizures",
            },
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "NumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Day",
                    "TimeSince_or_TimeOfEvent": "During",
                    "MonthDate": "12",
                    "CUI": "C0036572",
                },
                "evidence": (
                    "he did have a cluster of three seizures in a "
                    "24-hr period in Devember"
                ),
            },
        ]
    )

    projected = projection.project_row(row, ablation="combined")
    states = [
        mention["attributes"].get("NumberOfSeizures")
        for mention in projected["predicted_mentions"]
    ]
    rule_ids = [action["rule_id"] for action in projected["projection_actions"]]

    assert "3" not in states
    assert "0" in states
    assert "ownership.drop_dated_cluster_next_to_free" in rule_ids


def test_combined_retargets_named_last_week_to_generic() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "focal dyscognitive seizures",
                "attributes": {
                    "FrequencyChange": "Frequent",
                    "CUI": "C0270834",
                },
                "evidence": "She gets frequent focal dyscognitive seizures in clusters.",
            },
            {
                "entity": "SeizureFrequency",
                "text": "focal dyscognitive seizures",
                "attributes": {
                    "LowerNumberOfSeizures": "10",
                    "UpperNumberOfSeizures": "15",
                    "PointInTime": "Last_Week",
                    "TimeSince_or_TimeOfEvent": "During",
                    "CUI": "C0270834",
                },
                "evidence": (
                    "Last week she had around 10-15 of these seizures over 2 days."
                ),
            },
        ]
    )

    projected = projection.project_row(row, ablation="combined")
    cuis_by_point = {
        mention["attributes"].get("PointInTime"): mention["attributes"].get("CUI")
        for mention in projected["predicted_mentions"]
    }
    rule_ids = [action["rule_id"] for action in projected["projection_actions"]]

    assert cuis_by_point["Last_Week"] == "C0036572"
    assert "C0270834" in {
        mention["attributes"].get("CUI") for mention in projected["predicted_mentions"]
    }
    assert "ownership.retarget_last_week_named_to_generic" in rule_ids


def test_combined_drops_drugchange_before_when_other_rate_exists() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "focal motor seizures",
                "attributes": {
                    "LowerNumberOfSeizures": "2",
                    "UpperNumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                    "CUI": "C0016399",
                },
                "evidence": "Focal motor seizures, (left arm jerks) 2-3 per month",
            },
            {
                "entity": "SeizureFrequency",
                "text": "focal seizures",
                "attributes": {
                    "NumberOfSeizures": "1",
                    "PointInTime": "DrugChange",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "CUI": "C0751495",
                },
                "evidence": (
                    "The focal seizures were occurring more frequently, "
                    "perhaps once per day before the carbamazepine was introduced."
                ),
            },
        ]
    )

    projected = projection.project_row(row, ablation="combined")
    cuis = [mention["attributes"].get("CUI") for mention in projected["predicted_mentions"]]
    rule_ids = [action["rule_id"] for action in projected["projection_actions"]]

    assert "C0751495" not in cuis
    assert "C0016399" in cuis
    assert "ownership.drop_drugchange_before_if_other_active_rate" in rule_ids


def test_combined_keeps_lone_drugchange_before_active_rate() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "focal seizures",
                "attributes": {
                    "NumberOfSeizures": "1",
                    "PointInTime": "DrugChange",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "CUI": "C0751495",
                },
                "evidence": (
                    "The focal seizures were occurring more frequently, "
                    "perhaps once per day before the carbamazepine was introduced."
                ),
            }
        ]
    )

    projected = projection.project_row(row, ablation="combined")
    cuis = [mention["attributes"].get("CUI") for mention in projected["predicted_mentions"]]
    rule_ids = [action["rule_id"] for action in projected["projection_actions"]]

    assert "C0751495" in cuis
    assert "ownership.drop_drugchange_before_if_other_active_rate" not in rule_ids


def test_project_rows_reports_ablation_metadata() -> None:
    rows = [
        _row(
            predicted_mentions=[
                {
                    "entity": "SeizureFrequency",
                    "text": "seizures",
                    "attributes": {"NumberOfSeizures": "4"},
                    "evidence": "Mr Richards has had 4 more attacks.",
                }
            ]
        )
    ]

    _projected, metadata = projection.project_rows(rows, ablation="combined")

    assert metadata["projection_version"] == projection.PROJECTION_VERSION
    assert metadata["ablation"] == "combined"
    assert metadata["projection_action_counts"]["state.drop_unlabelled_active_rate"] == 1


def test_state_projection_applies_prompt_convention_encoding_pack() -> None:
    """List 11 / range / interval / last-event / dated heading / text cleanup.

    One governing case for the Phase 3 encoding pack. Internal rows are
    synthetic plus permitted dev20 shapes, not a scoreboard.
    """

    cases = (
        (
            "seizures",
            {"NumberOfSeizures": "several"},
            "several seizures since the last clinic appointment",
            {"NumberOfSeizures": "3", "PointInTime": "LastClinic"},
        ),
        (
            "seizures",
            {"NumberOfSeizures": "2-4"},
            "she has 2-4 seizures",
            {"LowerNumberOfSeizures": "2", "UpperNumberOfSeizures": "4"},
        ),
        (
            "focal seizures",
            {},
            "focal seizures with altered awareness every 3 weeks",
            {"NumberOfSeizures": "1", "NumberOfTimePeriods": "3", "TimePeriod": "Week"},
        ),
        (
            "Generalised tonic clonic seizure",
            {},
            "Generalised tonic clonic seizure-last event July 2016.",
            {
                "NumberOfSeizures": "0",
                "MonthDate": "7",
                "YearDate": "2016",
                "TimeSince_or_TimeOfEvent": "Since",
            },
        ),
        (
            "absence like seizures",
            {"YearDate": "2014"},
            "absence like seizures 2014",
            {
                "NumberOfSeizures": "1",
                "YearDate": "2014",
                "TimeSince_or_TimeOfEvent": "During",
            },
        ),
        (
            "seizure frequency",
            {"NumberOfTimePeriods": "4", "TimePeriod": "Week"},
            "the seizure frequency is roughly every 4 weeks",
            {"NumberOfSeizures": "1", "text": "seizure"},
        ),
    )
    for text, attrs, evidence, expected in cases:
        row = _row(
            predicted_mentions=[
                {
                    "entity": "SeizureFrequency",
                    "text": text,
                    "attributes": dict(attrs),
                    "evidence": evidence,
                }
            ]
        )
        projected = projection.project_row(row, ablation="state")
        mention = projected["predicted_mentions"][0]
        got = dict(mention["attributes"])
        got["text"] = mention["text"]
        for key, value in expected.items():
            assert got.get(key) == value, (evidence, key, got.get(key), value)

    coincided = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizure",
                "attributes": {"NumberOfSeizures": "1"},
                "evidence": "His last seizure coincided with forgetting to take his medication.",
            }
        ]
    )
    projected = projection.project_row(coincided, ablation="state")
    assert projected["predicted_mentions"][0]["attributes"].get("NumberOfSeizures") != "0"


def test_temporal_direction_alignment_rules() -> None:
    # Rule 1: PointInTime missing TimeSince_or_TimeOfEvent -> Adds Since
    row1 = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"PointInTime": "DrugChange"},
                "evidence": "No events since drug change",
            }
        ]
    )
    proj1 = projection.project_row(row1, ablation="state")
    assert proj1["predicted_mentions"][0]["attributes"]["TimeSince_or_TimeOfEvent"] == "Since"

    # Rule 2: Duration without date -> Strips TimeSince_or_TimeOfEvent
    row2 = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "TimePeriod": "Year",
                    "NumberOfTimePeriods": "3",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
                "evidence": "seizure free for 3 years",
            }
        ]
    )
    proj2 = projection.project_row(row2, ablation="state")
    assert "TimeSince_or_TimeOfEvent" not in proj2["predicted_mentions"][0]["attributes"]

    # Rule 4: Active rate mention with historical onset framing -> Strip onset attrs
    row4 = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "NumberOfSeizures": "2",
                    "TimePeriod": "Year",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": "2010",
                },
                "evidence": "seizures started in 2010 and he has roughly two seizures per year",
            }
        ]
    )
    proj4 = projection.project_row(row4, ablation="state")
    attrs4 = proj4["predicted_mentions"][0]["attributes"]
    assert "TimeSince_or_TimeOfEvent" not in attrs4
    assert "YearDate" not in attrs4

    # Rule 5: Seizure-free mention (NumberOfSeizures == '0') -> TimeSince_or_TimeOfEvent is Since
    row5 = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "During",
                },
                "evidence": "no seizures in 2017",
            }
        ]
    )
    proj5 = projection.project_row(row5, ablation="state")
    assert proj5["predicted_mentions"][0]["attributes"]["TimeSince_or_TimeOfEvent"] == "Since"


def _attrs_after_state_projection(attributes: dict, evidence: str) -> dict:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": attributes,
                "evidence": evidence,
            }
        ]
    )
    return projection.project_row(row, ablation="state")["predicted_mentions"][0]["attributes"]


def test_rule_4_clears_paired_onset_date_and_age_attributes() -> None:
    attrs = _attrs_after_state_projection(
        {
            "NumberOfSeizures": "2",
            "TimePeriod": "Year",
            "TimeSince_or_TimeOfEvent": "Since",
            "YearDate": "2010",
            "MonthDate": "3",
            "AgeLower": "14",
            "AgeUpper": "16",
            "AgeUnit": "Year",
        },
        "seizures started in 2010 and he has roughly two seizures per year",
    )

    # A MonthDate with no YearDate, an AgeUpper with no AgeLower, or an AgeUnit
    # qualifying an age that is no longer there, is incoherent.
    for key in (
        "YearDate",
        "MonthDate",
        "AgeLower",
        "AgeUpper",
        "AgeUnit",
        "TimeSince_or_TimeOfEvent",
    ):
        assert key not in attrs
    assert attrs["NumberOfSeizures"] == "2"


def test_rule_4_onset_framing_requires_a_real_date_or_age_phrase() -> None:
    # "since 20mg" contains the old bare "since 20" substring but frames a dose,
    # not an onset year, so Rule 4 must not strip this mention's YearDate.
    attrs = _attrs_after_state_projection(
        {
            "NumberOfSeizures": "2",
            "TimePeriod": "Month",
            "TimeSince_or_TimeOfEvent": "Since",
            "YearDate": "2019",
        },
        "he has had two seizures a month since 20mg lamotrigine was introduced",
    )

    assert attrs["YearDate"] == "2019"


def test_rule_4_onset_framing_matches_since_the_age_of_n() -> None:
    # The old bare "since age" substring missed the far more common
    # "since the age of N" phrasing, so onset attributes survived.
    attrs = _attrs_after_state_projection(
        {
            "NumberOfSeizures": "1",
            "NumberOfTimePeriods": "1",
            "TimePeriod": "Year",
            "AgeLower": "17",
            "AgeUnit": "Year",
        },
        "He has had on average one seizure a year since the age of 17 but a total of 3 in 2020.",
    )

    assert "AgeLower" not in attrs
    assert "AgeUnit" not in attrs
    assert attrs["TimePeriod"] == "Year"


def test_rule_6_strips_frequency_change_from_concrete_counts() -> None:
    attrs = _attrs_after_state_projection(
        {"NumberOfSeizures": "3", "TimePeriod": "Month", "FrequencyChange": "Increased"},
        "he has had 3 seizures a month, more than before",
    )

    assert "FrequencyChange" not in attrs
    assert attrs["NumberOfSeizures"] == "3"


def test_rule_6_keeps_frequency_change_without_a_count() -> None:
    attrs = _attrs_after_state_projection(
        {"FrequencyChange": "Increased"},
        "his seizures have become more frequent",
    )

    assert attrs["FrequencyChange"] == "Increased"


def test_rule_7_strips_time_period_when_point_in_time_is_present() -> None:
    attrs = _attrs_after_state_projection(
        {
            "NumberOfSeizures": "2",
            "PointInTime": "LastClinic",
            "TimePeriod": "Month",
            "NumberOfTimePeriods": "3",
        },
        "he has had 2 seizures since his last clinic",
    )

    assert "TimePeriod" not in attrs
    assert "NumberOfTimePeriods" not in attrs
    assert attrs["PointInTime"] == "LastClinic"


def test_rule_8_strips_time_since_for_a_day_anchored_event() -> None:
    attrs = _attrs_after_state_projection(
        {
            "NumberOfSeizures": "1",
            "DayDate": "14",
            "MonthDate": "3",
            "YearDate": "2019",
            "TimeSince_or_TimeOfEvent": "Since",
        },
        "he had a seizure on 14 March 2019",
    )

    assert "TimeSince_or_TimeOfEvent" not in attrs
    assert attrs["DayDate"] == "14"


def test_rule_8_keeps_time_since_for_a_day_anchored_seizure_free_period() -> None:
    # The day starts the seizure-free period; it is not the date of an event.
    attrs = _attrs_after_state_projection(
        {
            "NumberOfSeizures": "0",
            "DayDate": "14",
            "MonthDate": "3",
            "YearDate": "2019",
            "TimeSince_or_TimeOfEvent": "Since",
        },
        "he has been seizure free since 14 March 2019",
    )

    assert attrs["TimeSince_or_TimeOfEvent"] == "Since"


