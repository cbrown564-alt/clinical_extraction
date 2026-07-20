"""Canonical JSON extraction and repair for ExECTv2 LLM pipelines."""

from __future__ import annotations

import ast
import json
import re
from typing import Any

from clinical_extraction.core.json_schema_repair import (
    parse_json_payload_with_schema_repair,
)

_DEFAULT_PREFERRED_ROOTS = (
    "clinical_events",
    "mentions",
    "decisions",
    "findings",
    "event_frames",
)


def extract_json_object(
    raw: str,
    *,
    preferred_roots: tuple[str, ...] = _DEFAULT_PREFERRED_ROOTS,
) -> str:
    """Extract one JSON object (or array) from model text output."""

    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    candidates = _balanced_json_candidates(text)
    valid: list[tuple[int, str]] = []
    for index, candidate in enumerate(candidates):
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and any(key in payload for key in preferred_roots):
            valid.append((index, candidate))
        elif isinstance(payload, list):
            valid.append((index, candidate))
    if valid:
        return valid[-1][1]
    if candidates:
        return candidates[-1]
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text


def parse_json_payload(
    text: str,
    *,
    schema_repair: bool = True,
    python_literal_dialect_repair: bool = True,
    preferred_roots: tuple[str, ...] = _DEFAULT_PREFERRED_ROOTS,
) -> tuple[Any, list[str]]:
    """Extract and parse one JSON payload from model text."""

    extracted = extract_json_object(text, preferred_roots=preferred_roots)
    if schema_repair:
        return parse_json_payload_with_schema_repair(
            extracted,
            python_literal_dialect_repair=python_literal_dialect_repair,
        )
    try:
        return json.loads(extracted), []
    except json.JSONDecodeError as json_exc:
        if not python_literal_dialect_repair:
            raise
        try:
            return ast.literal_eval(extracted), ["coerced_python_literal_to_json"]
        except (SyntaxError, ValueError):
            raise json_exc from None


def loads_json_or_literal(raw: str) -> tuple[Any | None, list[str]]:
    """Load model output as JSON, with a Python-literal fallback for quote drift."""

    try:
        payload, notes = parse_json_payload(
            raw,
            schema_repair=False,
            python_literal_dialect_repair=True,
        )
    except json.JSONDecodeError as json_exc:
        return None, [f"invalid_json: {json_exc.msg}"]
    return payload, notes


def _balanced_json_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    stack: list[str] = []
    start: int | None = None
    in_string = False
    escaped = False
    pairs = {"{": "}", "[": "]"}
    closing = set(pairs.values())
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char in pairs:
            if not stack:
                start = index
            stack.append(pairs[char])
            continue
        if char not in closing or not stack:
            continue
        expected = stack.pop()
        if char != expected:
            stack = []
            start = None
            continue
        if not stack and start is not None:
            candidates.append(text[start : index + 1])
            start = None
    return candidates
