"""Strict first-response parsing. No format repair, semantic repair or answer inference."""

from __future__ import annotations

import json
import math
import re
from typing import Any

from jsonschema import Draft202012Validator  # type: ignore[import-untyped]
from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.one_call.prompts import (
    EXPANDED_SCHEMA,
    Condition,
    Simple,
)
from clinical_extraction.tasks.shared.epilepsy.normalization import label_to_frequency_record

NO_REFERENCE = "no seizure frequency reference"
ENVELOPE = re.compile(
    r"\s*\[\[ ## structured_json ## \]\]\s*(.*?)\s*(?:\[\[ ## completed ## \]\]\s*)?", re.S
)
_EXPANDED = Draft202012Validator(EXPANDED_SCHEMA)

_NUMBER = r"(?:\d+(?:\.\d+)?)"
_RANGE = rf"{_NUMBER}(?: to {_NUMBER})?"
_UNIT = r"(?:day|week|month|year)s?"
_PERIOD = rf"(?:(?:{_RANGE}|multiple) )?{_UNIT}"
_RATE = rf"(?:{_RANGE}|multiple) per {_PERIOD}"
_LABEL = re.compile(
    rf"(?:{_RATE}|(?:{_RANGE}|multiple) cluster per {_PERIOD}, "
    rf"(?:{_RANGE}|multiple) per cluster|unknown, (?:{_RANGE}|multiple) per cluster|"
    rf"seizure free(?: for (?:{_RANGE}|multiple) {_UNIT})?|unknown|"
    rf"{NO_REFERENCE})"
)


def native_categories(label: str) -> dict[str, str]:
    """Read-only projection of a declared label into the native Purist/Pragmatic bands."""
    if not _LABEL.fullmatch(label):
        raise ValueError("Label is outside the declared grammar")
    if any(float(n) <= 0 for n in re.findall(_NUMBER, label)):
        raise ValueError("Counts and denominators must be positive")
    for left, right in re.findall(rf"({_NUMBER}) to ({_NUMBER})", label):
        if float(left) > float(right):
            raise ValueError("Reversed bounds")
    frequency = label_to_frequency_record(label).monthly_frequency
    if not math.isfinite(frequency):
        raise ValueError("Non-finite frequency")
    return {"purist": str(map_purist(frequency)), "pragmatic": str(map_pragmatic(frequency))}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _answer_check(answer: Any, condition: Condition) -> tuple[str | None, dict[str, str] | None]:
    """Answer-only validity, independent of any findings and their links."""
    if condition == "expanded" and isinstance(answer, dict):
        answer = {k: v for k, v in answer.items() if k != "claim_indices"}
    try:
        parsed = Simple.model_validate({"answer": answer}).answer
    except ValidationError:
        return "invalid_schema", None
    try:
        categories = native_categories(parsed.label)
    except (ValueError, ZeroDivisionError, OverflowError):
        return "invalid_target_label", None
    evidence = parsed.evidence
    if parsed.label == NO_REFERENCE:
        if evidence is not None:
            return "absent_required_evidence", categories
    elif evidence is None or not evidence.strip():
        return "absent_required_evidence", categories
    return None, categories


def _expanded_check(payload: dict[str, Any]) -> str | None:
    if any(True for _ in _EXPANDED.iter_errors(payload)):
        return "invalid_schema"
    findings, answer = payload["findings"], payload["answer"]
    if any(i >= len(findings) for i in answer["claim_indices"]):
        return "invalid_schema"
    if answer["label"] == NO_REFERENCE and (findings or answer["claim_indices"]):
        return "invalid_schema"
    return None


def inspect(
    content: str | None, finish_reason: str | None, note: str, condition: Condition
) -> dict[str, Any]:
    """Classify one first response.

    ``failure`` is whole-response usability, the primary all-note view.
    ``answer_failure`` judges only the declared answer, as a secondary view.
    """
    result: dict[str, Any] = {
        "failure": None,
        "answer_failure": None,
        "label": None,
        "categories": None,
        "findings": None,
        "quote_slots": 0,
        "exact_quotes": 0,
    }

    def failed(reason: str) -> dict[str, Any]:
        return {**result, "failure": reason, "answer_failure": reason}

    if finish_reason == "length":
        return failed("truncation")
    if content is None or not content.strip():
        return failed("no_response")
    match = ENVELOPE.fullmatch(content)
    if not match or "[[ ##" in match[1]:
        return failed("invalid_envelope")
    try:
        payload = json.loads(match[1], object_pairs_hook=_unique_object)
    except (ValueError, TypeError):
        return failed("invalid_syntax")
    if not isinstance(payload, dict):
        return failed("invalid_schema")

    answer_failure, categories = _answer_check(payload.get("answer"), condition)
    declared = payload.get("answer")
    answer: dict[str, Any] = declared if isinstance(declared, dict) else {}
    result["answer_failure"] = answer_failure
    result["categories"] = categories
    result["label"] = answer.get("label") if answer_failure != "invalid_schema" else None

    quotes = [answer.get("evidence")] if answer.get("label") != NO_REFERENCE else []
    if condition == "minimal":
        record_failure = (
            "invalid_schema"
            if set(payload) != {"answer"} or set(answer) != {"label", "evidence"}
            else None
        )
    else:
        record_failure = _expanded_check(payload)
        if record_failure is None:
            result["findings"] = payload["findings"]
            quotes += [q for f in payload["findings"] for q in f["evidence"]]
    result["quote_slots"] = len(quotes)
    result["exact_quotes"] = sum(
        isinstance(q, str) and bool(q.strip()) and q in note for q in quotes
    )
    result["failure"] = record_failure or answer_failure
    return result
