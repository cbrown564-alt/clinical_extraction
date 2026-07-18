"""Shared, non-semantic JSON dialect repair for structured model output."""

from __future__ import annotations

import ast
import json
import re
from typing import Any


def parse_json_payload_with_schema_repair(
    raw_payload: str,
    *,
    python_literal_dialect_repair: bool = True,
) -> tuple[Any, list[str]]:
    """Parse JSON with explicit, named repairs that do not change values."""

    try:
        return json.loads(raw_payload), []
    except json.JSONDecodeError as json_error:
        try:
            return (
                json.loads(raw_payload, strict=False),
                ["json_dialect_repaired: literal_control_characters"],
            )
        except json.JSONDecodeError:
            pass
        without_trailing_commas = re.sub(r",\s*([}\]])", r"\1", raw_payload)
        if without_trailing_commas != raw_payload:
            try:
                return json.loads(without_trailing_commas), [
                    "json_dialect_repaired: trailing_commas"
                ]
            except json.JSONDecodeError:
                pass
        repaired_syntax, syntax_notes = _repair_local_json_syntax_drift(raw_payload)
        if syntax_notes:
            try:
                return json.loads(repaired_syntax), syntax_notes
            except json.JSONDecodeError:
                pass
        if not python_literal_dialect_repair:
            raise json_error from None
        try:
            return ast.literal_eval(raw_payload), ["json_dialect_repaired: python_literal"]
        except (SyntaxError, ValueError):
            raise json_error from None


def _repair_local_json_syntax_drift(raw_payload: str) -> tuple[str, list[str]]:
    """Repair bounded punctuation drift without changing scalar values."""

    repaired = raw_payload
    notes: list[str] = []
    repaired, count = re.subn(
        r'(?P<prefix>[{,]\s*)(?P<key>[A-Za-z_][A-Za-z0-9_:]*)(?P<suffix>"\s*:)',
        r'\g<prefix>"\g<key>\g<suffix>',
        repaired,
    )
    if count:
        notes.append("json_dialect_repaired: unquoted_object_keys")
    repaired, count = re.subn(
        r'(?P<prefix>[{,]\s*)"(?P<key>[A-Za-z_][A-Za-z0-9_:]*)\'\s*:',
        r'\g<prefix>"\g<key>":',
        repaired,
    )
    if count:
        notes.append("json_dialect_repaired: mixed_object_key_quote")
    repaired, count = re.subn(
        r'(\}\s*)}(\s*,\s*"selection"\s*:)',
        r'\1]\2',
        repaired,
    )
    if count:
        notes.append("json_dialect_repaired: extra_container_close")
    return repaired, notes
