"""Tests for ExECTv2 SF deterministic unknown suppression."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_unknown_suppression as suppression,
)


def _row(*, predicted_mentions):
    return {
        "letter_id": "L1",
        "split": "dev",
        "projection_version": "exectv2_hybrid_sf_state_projection_v0.6",
        "pipeline_family": "exectv2_hybrid_sf_state_projection",
        "predicted_mentions": list(predicted_mentions),
        "gold_mentions": [],
        "parse_errors": [],
    }


def test_unknown_suppression_drops_drug_response_scope() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"FrequencyChange": "Decreased", "PointInTime": "DrugChange"},
                "evidence": (
                    "Since the last consultation you have started him on lamotrigine, "
                    "and this has helped his seizures."
                ),
            }
        ]
    )

    suppressed = suppression.suppress_row(row)

    assert suppressed["predicted_mentions"] == []
    assert (
        suppressed["suppression_actions"][0]["rule_id"] == "unknown_suppression.drug_response_scope"
    )


def test_unknown_suppression_drops_contextual_or_historical_change_scope() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"FrequencyChange": "Same"},
                "evidence": "His epilepsy has been stable over the last few years",
            }
        ]
    )

    suppressed = suppression.suppress_row(row)

    assert suppressed["predicted_mentions"] == []
    assert (
        suppressed["suppression_actions"][0]["rule_id"]
        == "unknown_suppression.contextual_or_historical_change"
    )


def test_unknown_suppression_keeps_active_rate_mentions() -> None:
    row = _row(
        predicted_mentions=[
            {
                "entity": "SeizureFrequency",
                "text": "seizures",
                "attributes": {"NumberOfSeizures": "2"},
                "evidence": "He has two seizures per month.",
            }
        ]
    )

    suppressed = suppression.suppress_row(row)

    assert len(suppressed["predicted_mentions"]) == 1
    assert suppressed["predicted_mentions"][0]["attributes"]["NumberOfSeizures"] == "2"
    assert suppressed["suppression_actions"] == []


def test_suppress_rows_reports_action_counts() -> None:
    rows = [
        _row(
            predicted_mentions=[
                {
                    "entity": "SeizureFrequency",
                    "text": "seizures",
                    "attributes": {"FrequencyChange": "Same"},
                    "evidence": "His epilepsy has been stable over the last few years",
                }
            ]
        )
    ]

    _suppressed, metadata = suppression.suppress_rows(rows)

    assert metadata["suppression_version"] == suppression.SUPPRESSION_VERSION
    assert metadata["suppression_action_counts"] == {
        "unknown_suppression.contextual_or_historical_change": 1
    }
