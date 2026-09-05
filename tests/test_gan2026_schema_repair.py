from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_decision_payload,
    repair_selected_answer_payload,
    repair_structured_extraction_payload,
)


def _reject_invented_event_kind(event: object) -> object:
    if isinstance(event, dict) and event.get("kind") == "invented_kind":
        raise ValueError("invalid event kind")
    return event


def test_parse_json_payload_with_schema_repair_drops_unmatched_closing_brace() -> None:
    payload, notes = parse_json_payload_with_schema_repair(
        '{"clinical_events":[{"family":"investigation","fact":"MRI","attributes":{"mri_result":"abnormal"}}}]}'
    )

    assert payload == {
        "clinical_events": [
            {
                "family": "investigation",
                "fact": "MRI",
                "attributes": {"mri_result": "abnormal"},
            }
        ]
    }
    assert notes == ["json_dialect_repaired: unmatched_container_close"]


def test_parse_json_payload_with_schema_repair_handles_python_literal_dialect() -> None:
    payload, notes = parse_json_payload_with_schema_repair(
        "{'events': [{'notes': None}], 'selection': {'confidence': 'high'}}"
    )

    assert payload == {"events": [{"notes": None}], "selection": {"confidence": "high"}}
    assert notes == ["json_dialect_repaired: python_literal"]


def test_repair_decision_payload_handles_common_schema_aliases() -> None:
    payload = repair_decision_payload(
        {
            "assertion_status": "present",
            "uncertainty": "certain",
            "normalized_rate": 2.0,
            "answer_kind": "patient self-report",
            "confidence": 0.9,
        }
    )

    assert payload == {
        "assertion_status": "asserted",
        "uncertainty": "low",
        "normalized_rate": "2.0",
        "answer_kind": "frequency",
        "confidence": "high",
    }


def test_repair_selected_answer_payload_quarantines_only_invalid_unselected_event() -> None:
    payload, notes, quarantined = repair_selected_answer_payload(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "weekly",
                },
                {
                    "event_id": "e2",
                    "kind": "invented_kind",
                    "temporality": "historical",
                    "assertion_status": "asserted",
                    "evidence": "years ago",
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "1 per week",
                "evidence": "weekly",
                "confidence": "high",
                "rationale": "Selected e1.",
            },
        },
        event_validator=_reject_invented_event_kind,
    )

    assert [event["event_id"] for event in payload["events"]] == ["e1"]
    assert notes == ["unselected_event_quarantined: e2"]
    assert quarantined == ["e2"]


def test_repair_selected_answer_payload_never_quarantines_selected_event() -> None:
    payload, notes, quarantined = repair_selected_answer_payload(
        {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "invented_kind",
                    "temporality": "current",
                    "assertion_status": "asserted",
                    "evidence": "weekly",
                }
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "1 per week",
                "evidence": "weekly",
                "confidence": "high",
                "rationale": "Selected e1.",
            },
        }
    )

    assert payload["events"][0]["event_id"] == "e1"
    assert notes == []
    assert quarantined == []


def _event(
    event_id: str,
    *,
    kind: str | None = "frequency_rate",
    raw_value: str = "6 to 7 per year",
    evidence: str = "6 to 7 per year",
) -> dict[str, object]:
    event: dict[str, object] = {
        "event_id": event_id,
        "raw_value": raw_value,
        "temporality": "current",
        "assertion_status": "asserted",
        "evidence": evidence,
    }
    if kind is not None:
        event["kind"] = kind
    return event


def test_repair_fills_omitted_kind_from_sibling_with_same_raw_value() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [
                _event("e1"),
                _event("e2"),
                _event("e3", kind=None),
            ],
            "selection": {
                "selected_event_ids": ["e1", "e2", "e3"],
                "final_kind": "frequency",
                "final_label": "6 to 7 per year",
                "evidence": "6 to 7 per year",
                "confidence": "high",
                "rationale": "Same rate stated three times.",
            },
        }
    )

    assert [event["kind"] for event in payload["events"]] == [
        "frequency_rate",
        "frequency_rate",
        "frequency_rate",
    ]
    assert payload["selection"]["final_label"] == "6 to 7 per year"


def test_repair_fills_omitted_kind_from_selection_when_no_sibling() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [_event("e1", kind=None, raw_value="seizure free for 6 month")],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "seizure_free",
                "final_label": "seizure free for 6 month",
                "evidence": "6 to 7 per year",
                "confidence": "high",
                "rationale": "Quiet interval.",
            },
        }
    )

    assert payload["events"][0]["kind"] == "seizure_free"


def test_repair_fills_frequency_kind_from_written_raw_value_and_final_kind() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [_event("e1", kind=None)],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "6 to 7 per year",
                "evidence": "6 to 7 per year",
                "confidence": "high",
                "rationale": "Current yearly count.",
            },
        }
    )

    assert payload["events"][0]["kind"] == "frequency_rate"


def test_repair_fills_cluster_kind_from_written_raw_value_and_final_kind() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [
                _event(
                    "e1",
                    kind=None,
                    raw_value="1 cluster per 5 day, 3 per cluster",
                    evidence="clusters every 5 days",
                )
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": "frequency",
                "final_label": "1 cluster per 5 day, 3 per cluster",
                "evidence": "clusters every 5 days",
                "confidence": "high",
                "rationale": "Cluster rate.",
            },
        }
    )

    assert payload["events"][0]["kind"] == "cluster_frequency"


def test_repair_does_not_invent_kind_from_raw_value_alone() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [_event("e1", kind=None)],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_label": "6 to 7 per year",
                "evidence": "6 to 7 per year",
                "confidence": "high",
                "rationale": "Current yearly count.",
            },
        }
    )

    assert "kind" not in payload["events"][0]


def test_repair_does_not_fill_kind_when_siblings_disagree() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [
                _event("e1", kind="frequency_rate"),
                _event("e2", kind="cluster_frequency"),
                _event("e3", kind=None),
            ],
            "selection": {
                "selected_event_ids": ["e3"],
                "final_kind": "unresolved_multiple",
                "final_label": "unknown",
                "evidence": "6 to 7 per year",
                "confidence": "low",
                "rationale": "Conflicting event types.",
            },
        }
    )

    assert "kind" not in payload["events"][2]


def test_repair_fills_omitted_selected_event_ids_with_empty_list() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [_event("e1", kind="unknown_frequency")],
            "selection": {
                "final_kind": "unknown",
                "final_label": "unknown",
                "evidence": "increase in brief absence episodes",
                "confidence": "high",
                "rationale": "The absence count was not quantified.",
            },
        }
    )

    assert payload["selection"]["selected_event_ids"] == []
    assert payload["selection"]["final_label"] == "unknown"


def test_repair_treats_null_selected_event_ids_as_omitted() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [_event("e1", kind="seizure_free")],
            "selection": {
                "selected_event_ids": None,
                "final_kind": "unknown",
                "final_label": "unknown",
                "evidence": "events have been sparse",
                "confidence": "medium",
                "rationale": "No countable rate was written.",
            },
        }
    )

    assert payload["selection"]["selected_event_ids"] == []


def test_repair_accepts_one_call_example_answer_shape() -> None:
    payload = repair_structured_extraction_payload(
        {
            "facts": [
                {
                    "fact_id": "f1",
                    "kind": "frequency_rate",
                    "raw_value": "brief periods of daily seizures",
                    "normalised_label": "1 per day",
                    "temporality": "current",
                    "applies_to": "seizures",
                    "time_window": None,
                    "evidence": "brief periods of daily seizures",
                },
                {
                    "fact_id": "f2",
                    "kind": "frequency_rate",
                    "raw_value": "usually every 2 weeks",
                    "normalised_label": "1 per 2 week",
                    "temporality": "current",
                    "applies_to": "seizures",
                    "time_window": None,
                    "evidence": "usually every 2 weeks",
                },
            ],
            "answer": {"selected_fact_ids": ["f2"]},
        }
    )

    assert "facts" not in payload
    assert "answer" not in payload
    assert [event["event_id"] for event in payload["events"]] == ["f1", "f2"]
    assert payload["selection"]["selected_event_ids"] == ["f2"]
    assert payload["selection"]["final_kind"] == "frequency"
    assert payload["selection"]["rationale"] == ""
    assert payload["selection"]["confidence"] == "medium"


def test_repair_does_not_invent_selected_event_ids_from_the_event_list() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [
                _event("e1", kind="seizure_free"),
                _event("e2", kind="frequency_rate"),
            ],
            "selection": {
                "final_kind": "unknown",
                "final_label": "unknown",
                "evidence": "events have been sparse",
                "confidence": "medium",
                "rationale": "No countable rate was written.",
            },
        }
    )

    assert payload["selection"]["selected_event_ids"] == []
