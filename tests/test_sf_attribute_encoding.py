"""Gold-free SF attribute encoding on already-emitted mentions."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_attribute_encoding as encoding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection as projection,
)


def _sf(
    text: str,
    evidence: str,
    **attrs: str,
) -> dict[str, object]:
    return {
        "entity": "SeizureFrequency",
        "text": text,
        "evidence": evidence,
        "attributes": dict(attrs),
    }


def test_last_event_no_count_becomes_zero_since() -> None:
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


def test_none_since_missing_count_becomes_zero() -> None:
    mentions = [_sf("seizures", "He has had none since the last clinic.")]

    after, _actions = encoding.apply_sf_attribute_encoding(mentions)

    assert after[0]["attributes"]["NumberOfSeizures"] == "0"
    assert after[0]["attributes"]["TimeSince_or_TimeOfEvent"] == "Since"


def test_active_interval_count_is_not_zeroed() -> None:
    mentions = [
        _sf(
            "focal seizures",
            "Focal seizures continue every 3 weeks.",
            NumberOfSeizures="1",
        )
    ]

    after, actions = encoding.apply_sf_attribute_encoding(mentions)

    assert after[0]["attributes"]["NumberOfSeizures"] == "1"
    assert all(item["rule_id"] != "encoding.last_event_zero" for item in actions)


def test_projection_maps_no_last_event_to_seizure_free() -> None:
    row = {
        "letter_id": "L1",
        "split": "dev",
        "prompt_version": "test",
        "pipeline_family": "test",
        "predicted_mentions": [
            _sf(
                "seizures",
                "Last event July 2016. She has had no seizures since then.",
                NumberOfSeizures="no",
            )
        ],
        "candidate_spans": [],
        "gold_mentions": [],
        "parse_errors": [],
    }

    projected = projection.project_row(row, ablation="state")
    attrs = projected["predicted_mentions"][0]["attributes"]
    assert attrs["NumberOfSeizures"] == "0"
    assert attrs["TimeSince_or_TimeOfEvent"] == "Since"
