from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
    repair_decision_payload,
    repair_structured_extraction_payload,
)


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


def test_repair_decision_payload_handles_llm_answer_kind_variants() -> None:
    for answer_kind in (
        "count and window",
        "count per time window",
        "direct statement",
        "direct_extraction",
        "electrographic seizure frequency",
        "patient-reported count",
    ):
        assert repair_decision_payload({"answer_kind": answer_kind}) == {"answer_kind": "frequency"}


def test_repair_decision_payload_does_not_add_parser_owned_defaults() -> None:
    assert repair_decision_payload({"normalized_rate": None}) == {"normalized_rate": None}
    assert repair_decision_payload({"uncertainty": None}) == {"uncertainty": None}
    assert repair_decision_payload({}) == {}


def test_repair_structured_extraction_payload_handles_cluster_final_kind_alias() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [{"kind": "cluster", "temporality": "ongoing"}],
            "selection": {"final_kind": "cluster_frequency"},
        }
    )

    assert payload == {
        "events": [{"kind": "cluster_frequency", "temporality": "current"}],
        "selection": {"final_kind": "frequency", "confidence": "medium"},
    }


def test_repair_structured_extraction_payload_handles_last_event_final_kind_alias() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [{"kind": "last event"}],
            "selection": {"final_kind": "last_event_only", "confidence": 0.9},
        }
    )

    assert payload == {
        "events": [{"kind": "last_event_only"}],
        "selection": {"final_kind": "frequency", "confidence": "high"},
    }
