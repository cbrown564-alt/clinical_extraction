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


def test_parse_json_payload_with_schema_repair_handles_literal_control_characters() -> None:
    # Regression guard: some local models emit raw newlines inside string
    # values (typically in verbose multi-paragraph rationale fields) instead
    # of the escaped "\n" JSON requires, which `json.loads` rejects by default.
    payload, notes = parse_json_payload_with_schema_repair(
        '{"rationale": "first paragraph.\n\nsecond paragraph."}'
    )

    assert payload == {"rationale": "first paragraph.\n\nsecond paragraph."}
    assert notes == ["json_dialect_repaired: literal_control_characters"]


def test_parse_json_payload_with_schema_repair_handles_trailing_commas() -> None:
    payload, notes = parse_json_payload_with_schema_repair(
        '{"events": [{"kind": "frequency_rate",}], "selection": {},}'
    )

    assert payload == {
        "events": [{"kind": "frequency_rate"}],
        "selection": {},
    }
    assert notes == ["json_dialect_repaired: trailing_commas"]


def test_parse_json_payload_with_schema_repair_handles_local_key_and_container_drift() -> None:
    payload, notes = parse_json_payload_with_schema_repair(
        """{
        "events": [{pevent_id": "e1", "kind": "frequency_rate"}
        },
        "selection": {"final_kind": "frequency"}
        }"""
    )

    assert payload == {
        "events": [{"pevent_id": "e1", "kind": "frequency_rate"}],
        "selection": {"final_kind": "frequency"},
    }
    assert notes == [
        "json_dialect_repaired: unquoted_object_keys",
        "json_dialect_repaired: extra_container_close",
    ]


def test_parse_json_payload_with_schema_repair_handles_mixed_key_quote() -> None:
    payload, notes = parse_json_payload_with_schema_repair(
        '''{"attributes": {"TimeSince_or_TimeOf': "Since"}}'''
    )

    assert payload == {"attributes": {"TimeSince_or_TimeOf": "Since"}}
    assert notes == ["json_dialect_repaired: mixed_object_key_quote"]


def test_parse_json_payload_with_schema_repair_can_disable_python_literal_dialect() -> None:
    try:
        parse_json_payload_with_schema_repair(
            "{'events': [{'notes': None}], 'selection': {'confidence': 'high'}}",
            python_literal_dialect_repair=False,
        )
    except ValueError as exc:
        assert "Expecting property name enclosed in double quotes" in str(exc)
    else:  # pragma: no cover - keeps the assertion explicit if json changes behavior.
        raise AssertionError("Expected strict JSON parsing to reject Python literal syntax")


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


def test_repair_decision_payload_coerces_stringified_numeric_confidence() -> None:
    # Regression guard: qwen3.6:35b sometimes emits a numeric confidence as a
    # JSON string (e.g. "confidence": "0.8") rather than a bare number, which
    # the existing int|float-only numeric-confidence repair did not catch,
    # causing a spurious "Input should be 'low', 'medium' or 'high'" error.
    assert repair_decision_payload({"confidence": "0.8"}) == {"confidence": "high"}
    assert repair_decision_payload({"confidence": "0.6"}) == {"confidence": "medium"}
    assert repair_decision_payload({"confidence": "0.2"}) == {"confidence": "low"}
    assert repair_decision_payload({"confidence": "not-a-number"}) == {"confidence": "not-a-number"}


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


def test_repair_decision_payload_leaves_already_valid_assertion_status_unchanged() -> None:
    # Regression guard: an earlier alias entry mapped the already-valid
    # "unknown" assertion_status to "unclear" (a temporality-only value),
    # which made every correct "unknown" model output fail schema validation.
    for assertion_status in ("asserted", "negated", "historical", "hypothetical", "unknown"):
        assert repair_decision_payload({"assertion_status": assertion_status}) == {
            "assertion_status": assertion_status
        }


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


def test_repair_structured_extraction_payload_handles_qwen_temporality_aliases() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [
                {
                    "assertion_status": "asserted",
                    "kind": "frequency_rate",
                    "temporality": "hypothetical",
                },
                {
                    "assertion_status": "negated",
                    "kind": "seizure_free",
                    "temporality": "historical/current",
                },
                {
                    "assertion_status": "current",
                    "kind": "frequency_rate",
                    "temporality": "recent",
                },
            ],
            "selection": {"final_kind": "frequency"},
        }
    )

    assert payload == {
        "events": [
            {
                "assertion_status": "asserted",
                "kind": "frequency_rate",
                "temporality": "future",
            },
            {
                "assertion_status": "negated",
                "kind": "seizure_free",
                "temporality": "current",
            },
            {
                "assertion_status": "asserted",
                "kind": "frequency_rate",
                "temporality": "recent",
            },
        ],
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


def test_repair_structured_extraction_payload_repairs_structural_key_drift() -> None:
    payload = repair_structured_extraction_payload(
        {
            "events": [
                {"event_id": "e1", "kind": "frequency_rate", "evidence": "weekly"},
                {
                    "pevent_id": "e2",
                    "kind": "no_reference",
                    "evidence": None,
                    "temporlagity": "historical",
                },
                {"kind": "seizure_free", "evidence": "none this year"},
            ],
            "selection": {"final_kind": "frequency", "rationality": "Selected e1."},
        }
    )

    assert payload["events"][1]["event_id"] == "e2"
    assert payload["events"][1]["evidence"] == ""
    assert payload["events"][1]["temporality"] == "historical"
    assert "temporlagity" not in payload["events"][1]
    assert payload["events"][2]["event_id"] == "e3"
    assert payload["selection"]["rationale"] == "Selected e1."
    assert "rationality" not in payload["selection"]


def test_repair_structured_extraction_payload_preserves_non_no_reference_null_evidence() -> None:
    payload = repair_structured_extraction_payload(
        {"events": [{"kind": "frequency_rate", "evidence": None}], "selection": {}}
    )

    assert payload["events"][0]["evidence"] is None
