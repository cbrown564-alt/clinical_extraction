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


def test_ownership_projection_assigns_named_count_to_named_type() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"CUI": "C0036572", "NumberOfSeizures": "2"},
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
