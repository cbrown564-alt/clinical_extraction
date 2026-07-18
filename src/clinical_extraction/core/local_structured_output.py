"""Shared diagnostics and bounded retry rules for local structured output."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import dspy

from clinical_extraction.core.json_schema_repair import (
    parse_json_payload_with_schema_repair,
)

_BLOCKING_PREFIXES = ("invalid_json:", "schema_validation_error:", "not_run")
_REPEATED_TOKEN = re.compile(r"\b([A-Za-z][A-Za-z-]*)\b(?:\s+\1\b){5,}", re.IGNORECASE)


@dataclass(frozen=True)
class StructuredOutputAssessment:
    """Machine-readable diagnosis of one structured model response."""

    failure_codes: tuple[str, ...]
    retry_eligible: bool
    parsed_payload: Any | None = None


@dataclass(frozen=True)
class FormatRetryValidation:
    """Result of checking a model-produced format-only retry."""

    accepted: bool
    notes: tuple[str, ...]


class FormatOnlyJsonRetrySignature(dspy.Signature):
    """Correct JSON shape without changing any clinical fact or value."""

    retry_input_json: str = dspy.InputField(
        desc="The malformed output, required JSON schema, and correction instruction."
    )
    repaired_json: str = dspy.OutputField(
        desc="One corrected JSON object only, with all clinical facts and values unchanged."
    )


class FormatOnlyJsonRetry(dspy.Module):
    """One bounded model call used only after a parseable schema failure."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(FormatOnlyJsonRetrySignature)

    def forward(self, retry_input_json: str) -> dspy.Prediction:
        return self.predict(retry_input_json=retry_input_json)


def assess_structured_output(
    raw_output: str,
    parse_errors: Sequence[object] | None,
    *,
    call_error: str | None = None,
    reasoning: str | None = None,
) -> StructuredOutputAssessment:
    """Classify transport and schema failures without changing model content."""

    errors = [str(error) for error in (parse_errors or [])]
    blocking = any(error.startswith(_BLOCKING_PREFIXES) for error in errors)
    codes: list[str] = []
    text = raw_output.strip()
    if call_error:
        codes.append("provider_error")
    if not text:
        codes.append("reasoning_only" if reasoning else "empty_content")
    elif blocking and not any(char in text for char in "{["):
        codes.append("schema_constraint_bypass")
    if _REPEATED_TOKEN.search(text):
        codes.append("repetition_loop")
    if _looks_truncated(text, errors):
        codes.append("truncated_json")
    if any(error.startswith("invalid_json:") for error in errors):
        codes.append("invalid_json")
    if any(error.startswith("schema_validation_error:") for error in errors):
        codes.append("schema_validation_error")

    payload: Any | None = None
    retry_eligible = False
    if codes == ["schema_validation_error"]:
        try:
            payload, _ = _parse_payload(text)
        except (ValueError, SyntaxError):
            payload = None
        retry_eligible = payload is not None
    return StructuredOutputAssessment(tuple(codes), retry_eligible, payload)


def build_format_only_retry_input(
    *, malformed_output: str, schema: Mapping[str, Any]
) -> str:
    """Build the minimal model-facing input for one format-only retry."""

    return json.dumps(
        {
            "instruction": (
                "Convert the supplied output to one JSON object matching the schema. "
                "Keep every clinical fact and value unchanged. Do not add, remove, "
                "infer, summarize, or reinterpret clinical information. Return only "
                "the corrected JSON object."
            ),
            "schema": schema,
            "malformed_output": malformed_output,
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def format_retry_preserves_values(original: Any, repaired: Any) -> bool:
    """Require a retry to preserve scalar values under the same field names."""

    return _field_values(original) == _field_values(repaired)


def validate_format_retry(
    original_output: str,
    original_errors: Sequence[object] | None,
    retry_output: str,
) -> FormatRetryValidation:
    """Accept one retry only when it repairs shape without changing values."""

    assessment = assess_structured_output(original_output, original_errors)
    if not assessment.retry_eligible:
        return FormatRetryValidation(False, ("format_retry_rejected: ineligible",))
    try:
        repaired, _ = _parse_payload(retry_output)
    except (ValueError, SyntaxError):
        return FormatRetryValidation(False, ("format_retry_rejected: invalid_json",))
    if not format_retry_preserves_values(assessment.parsed_payload, repaired):
        return FormatRetryValidation(
            False, ("format_retry_rejected: clinical_values_changed",)
        )
    return FormatRetryValidation(True, ("format_retry_applied",))


def ollama_structured_probe_request(
    model: str, *, explicit_json_instruction: bool = False
) -> dict[str, Any]:
    """Return a small native-chat request that verifies constrained JSON output."""

    schema = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["ok"]},
            "values": {"type": "array", "items": {"type": "integer"}},
        },
        "required": ["status", "values"],
        "additionalProperties": False,
    }
    prompt = "Return status ok and the values 1 and 2."
    if explicit_json_instruction:
        prompt = (
            "Return only JSON matching the supplied schema, with status ok and "
            "values [1, 2]."
        )
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "think": False,
        "format": schema,
        "options": {"temperature": 0, "num_predict": 64},
    }


def raw_output_from_adapter_error(error_text: str) -> str | None:
    """Recover a model payload preserved inside a DSPy adapter error."""

    marker = "LM Response:"
    if marker not in error_text:
        return None
    tail = error_text.split(marker, 1)[1]
    for stop in (
        "\n\nExpected to find output fields",
        "\r\n\r\nExpected to find output fields",
    ):
        if stop in tail:
            tail = tail.split(stop, 1)[0]
            break
    payload = tail.strip()
    return payload or None


def _field_values(
    payload: Any, *, key: str | None = None
) -> dict[str, Counter[tuple[str, str]]]:
    values: dict[str, Counter[tuple[str, str]]] = {}
    if key == "rationale":
        return values
    if isinstance(payload, Mapping):
        for child_key, value in payload.items():
            _merge_field_values(values, _field_values(value, key=str(child_key)))
    elif isinstance(payload, list | tuple):
        for value in payload:
            _merge_field_values(values, _field_values(value, key=key))
    elif payload is not None:
        field = key or "<root>"
        values[field] = Counter({(type(payload).__name__, str(payload)): 1})
    return values


def _merge_field_values(
    target: dict[str, Counter[tuple[str, str]]],
    source: Mapping[str, Counter[tuple[str, str]]],
) -> None:
    for field, counts in source.items():
        target.setdefault(field, Counter()).update(counts)


def _looks_truncated(text: str, errors: Sequence[str]) -> bool:
    if not any(error.startswith("invalid_json:") for error in errors):
        return False
    stripped = text.rstrip()
    return (
        stripped.startswith(("{", "["))
        and not stripped.endswith(("}", "]"))
    )


def _parse_payload(text: str) -> tuple[Any, list[str]]:
    stripped = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.DOTALL)
    if fenced:
        stripped = fenced.group(1)
    try:
        return parse_json_payload_with_schema_repair(stripped)
    except ValueError as original_error:
        starts = [index for index in (stripped.find("{"), stripped.find("[")) if index >= 0]
        start = min(starts) if starts else -1
        end = max(stripped.rfind("}"), stripped.rfind("]"))
        if start >= 0 and end > start:
            return parse_json_payload_with_schema_repair(stripped[start : end + 1])
        raise original_error
