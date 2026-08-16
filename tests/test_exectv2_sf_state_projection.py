"""Exemplars for ExECT SF state/ownership projection.

One case each for drop, change recovery, last-event repair, named-type
ownership, ablation metadata, the encoding pack, temporal alignment,
and Rule 4 onset-attribute cleanup.
"""

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
    assert attrs["NumberOfSeizures"] == "0"
    assert "state.last_event_active_to_seizure_free" in [
        action["rule_id"] for action in projected["projection_actions"]
    ]


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
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"NumberOfSeizures": "several"},
                "evidence": "several seizures since the last clinic appointment",
            }
        ]
    )
    projected = projection.project_row(row, ablation="state")
    attrs = projected["predicted_mentions"][0]["attributes"]
    assert attrs["NumberOfSeizures"] == "3"
    assert attrs["PointInTime"] == "LastClinic"


def test_temporal_direction_alignment_rules() -> None:
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


def test_rule_4_clears_paired_onset_date_and_age_attributes() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {
                    "NumberOfSeizures": "2",
                    "TimePeriod": "Year",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": "2010",
                    "MonthDate": "3",
                    "AgeLower": "14",
                    "AgeUpper": "16",
                    "AgeUnit": "Year",
                },
                "evidence": "seizures started in 2010 and he has roughly two seizures per year",
            }
        ]
    )
    attrs = projection.project_row(row, ablation="state")["predicted_mentions"][0]["attributes"]
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
