from __future__ import annotations

import json

from clinical_extraction.core.local_structured_output import (
    assess_structured_output,
    build_format_only_retry_input,
    format_retry_preserves_values,
    ollama_structured_probe_request,
    raw_output_from_adapter_error,
    validate_format_retry,
)


def test_assessment_distinguishes_common_local_model_failures() -> None:
    assert assess_structured_output("", ["not_run"]).failure_codes == (
        "empty_content",
    )
    assert assess_structured_output(
        "I found several events.", ["invalid_json: Expecting value"]
    ).failure_codes == ("schema_constraint_bypass", "invalid_json")
    assert assess_structured_output(
        '{"events": [{"evidence": "same same same same same same same same',
        ["invalid_json: Unterminated string"],
    ).failure_codes == ("repetition_loop", "truncated_json", "invalid_json")


def test_only_parseable_schema_failures_are_format_retry_eligible() -> None:
    assessment = assess_structured_output(
        '{"clinical_events": {"family": "diagnosis"}}',
        ["schema_validation_error: Input should be a valid list"],
    )

    assert assessment.retry_eligible is True
    assert assessment.parsed_payload == {
        "clinical_events": {"family": "diagnosis"}
    }
    assert assess_structured_output(
        "not json", ["invalid_json: Expecting value"]
    ).retry_eligible is False


def test_format_retry_requires_all_clinical_values_to_be_unchanged() -> None:
    original = {
        "events": {"family": "diagnosis", "evidence": "Diagnosis: epilepsy"},
        "rationale": "verbose reasoning may be removed",
    }
    reshaped = {
        "events": [
            {"family": "diagnosis", "evidence": "Diagnosis: epilepsy"}
        ],
        "rationale": "",
    }
    changed = {
        "events": [{"family": "diagnosis", "evidence": "Diagnosis: focal epilepsy"}]
    }
    swapped = {
        "events": [
            {"family": "Diagnosis: epilepsy", "evidence": "diagnosis"}
        ]
    }

    assert format_retry_preserves_values(original, reshaped)
    assert not format_retry_preserves_values(original, changed)
    assert not format_retry_preserves_values(original, swapped)


def test_format_retry_instruction_is_plain_and_keeps_research_metadata_out() -> None:
    payload = json.loads(
        build_format_only_retry_input(
            malformed_output="{'events': {}}",
            schema={"type": "object", "properties": {"events": {"type": "array"}}},
        )
    )

    assert "Keep every clinical fact and value unchanged" in payload["instruction"]
    assert "Return only the corrected JSON object" in payload["instruction"]
    assert "benchmark" not in payload["instruction"].lower()
    assert payload["malformed_output"] == "{'events': {}}"


def test_format_retry_validation_accepts_reshape_and_rejects_clinical_change() -> None:
    original = '{"events": {"family": "diagnosis", "evidence": "epilepsy"}}'
    original_errors = ["schema_validation_error: Input should be a valid list"]

    accepted = validate_format_retry(
        original,
        original_errors,
        '{"events": [{"family": "diagnosis", "evidence": "epilepsy"}]}',
    )
    changed = validate_format_retry(
        original,
        original_errors,
        '{"events": [{"family": "diagnosis", "evidence": "focal epilepsy"}]}',
    )

    assert accepted.accepted is True
    assert accepted.notes == ("format_retry_applied",)
    assert changed.accepted is False
    assert changed.notes == ("format_retry_rejected: clinical_values_changed",)


def test_ollama_probe_uses_native_think_false_schema_constraint() -> None:
    request = ollama_structured_probe_request("gemma4:26b")

    assert request["model"] == "gemma4:26b"
    assert request["stream"] is False
    assert request["think"] is False
    assert request["format"]["required"] == ["status", "values"]
    assert request["options"]["temperature"] == 0


def test_ollama_probe_can_mirror_explicit_json_application_prompt() -> None:
    request = ollama_structured_probe_request(
        "qwen3.6:35b", explicit_json_instruction=True
    )

    assert "Return only JSON matching the supplied schema" in request["messages"][0][
        "content"
    ]
    assert request["think"] is False
    assert isinstance(request["format"], dict)


def test_adapter_error_recovery_preserves_embedded_raw_response() -> None:
    error = (
        "AdapterParseError: LM Response:\n"
        '{"events": [], "selection": {}}\n\n'
        "Expected to find output fields: structured_json"
    )

    assert raw_output_from_adapter_error(error) == (
        '{"events": [], "selection": {}}'
    )
