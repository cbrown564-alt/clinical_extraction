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


def test_not_had_any_further_since_date_becomes_zero() -> None:
    mentions = [
        _sf(
            "generalised tonic clonic seizures",
            "She has not had any further generalised tonic clonic seizures since August 2016.",
            MonthDate="August 2016",
            TimeSince_or_TimeOfEvent="Since",
        )
    ]

    after, actions = encoding.apply_sf_attribute_encoding(mentions)

    assert after[0]["attributes"]["NumberOfSeizures"] == "0"
    assert after[0]["attributes"]["TimeSince_or_TimeOfEvent"] == "Since"
    assert any(item["rule_id"] == "encoding.last_event_zero" for item in actions)


def test_no_absences_since_date_becomes_zero() -> None:
    mentions = [
        _sf(
            "absences",
            "There have been no absences since November 2016.",
            MonthDate="November 2016",
            TimeSince_or_TimeOfEvent="Since",
        )
    ]

    after, _actions = encoding.apply_sf_attribute_encoding(mentions)

    assert after[0]["attributes"]["NumberOfSeizures"] == "0"


def test_remote_since_range_becomes_seizure_free() -> None:
    mentions = [
        _sf(
            "focal to bilateral convulsive seizures",
            "She had 3 or 4 events since early adolescence.",
            LowerNumberOfSeizures="3",
            UpperNumberOfSeizures="4",
            TimeSince_or_TimeOfEvent="Since",
            AgeLower="early adolescence",
        )
    ]

    after, actions = encoding.apply_sf_attribute_encoding(mentions)

    assert after[0]["attributes"]["NumberOfSeizures"] == "0"
    assert after[0]["attributes"]["TimeSince_or_TimeOfEvent"] == "Since"
    assert "LowerNumberOfSeizures" not in after[0]["attributes"]
    assert any(item["rule_id"] == "encoding.last_event_zero" for item in actions)


def test_last_clinic_range_is_not_zeroed() -> None:
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
