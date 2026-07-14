"""Shared mention parsing, evidence gating, and attribute repair for ExECTv2 LLM pipelines."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.repair import (
    ExtractionRecord,
    MentionRecord,
    check_evidence,
    repair_attributes,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    parse_json_payload,
)

__all__ = [
    "ExtractionRecord",
    "MentionRecord",
    "check_evidence",
    "has_blocking_parse_issue",
    "parse_extraction_json",
    "raw_output_from_adapter_parse_error",
    "repair_attributes",
]


def has_blocking_parse_issue(errors: Any) -> bool:
    """Return whether parsing failed before a prediction could be scored."""

    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for error in (errors or [])
    )


def parse_extraction_json(
    raw_output: str,
) -> tuple[ExtractionRecord | None, list[str]]:
    """Parse and schema-validate one LLM output string.

    Returns (record, errors). If errors contains a blocking issue
    (invalid_json or schema_validation_error), record is None.
    Non-blocking issues (coercions, unknown fields) are noted in errors.
    """
    try:
        payload, dialect_notes = parse_json_payload(raw_output, schema_repair=True)
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]

    payload, coerce_notes = _coerce_payload(payload)
    errors: list[str] = [*dialect_notes, *coerce_notes]

    try:
        record = ExtractionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    return record, errors


def raw_output_from_adapter_parse_error(error_text: str) -> str | None:
    """Recover the model payload embedded in a DSPy adapter parse error."""

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


def _coerce_payload(payload: Any) -> tuple[Any, list[str]]:
    """Coerce numeric attribute values to strings; note coercions."""
    notes: list[str] = []
    if isinstance(payload, list):
        notes.append("coerced_top_level_mention_array")
        payload = {"mentions": payload}
    if not isinstance(payload, dict):
        return payload, notes
    mentions_raw = payload.get("mentions")
    if not isinstance(mentions_raw, list):
        return payload, notes
    coerced_mentions = []
    for i, mention in enumerate(mentions_raw):
        if not isinstance(mention, dict):
            coerced_mentions.append(mention)
            continue
        attrs = mention.get("attributes")
        if isinstance(attrs, dict):
            new_attrs: dict[str, str] = {}
            for k, v in attrs.items():
                if v is None:
                    continue
                str_v = str(v)
                if str_v != v:
                    notes.append(f"coerced_attribute_value: mention[{i}] {k!r} {v!r} -> {str_v!r}")
                new_attrs[str(k)] = str_v
            mention = dict(mention)
            mention["attributes"] = new_attrs
        coerced_mentions.append(mention)
    return {**payload, "mentions": coerced_mentions}, notes
