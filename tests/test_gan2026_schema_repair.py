from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_decision_payload,
    repair_selected_answer_payload,
)


def _reject_invented_event_kind(event: object) -> object:
    if isinstance(event, dict) and event.get("kind") == "invented_kind":
        raise ValueError("invalid event kind")
    return event


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
