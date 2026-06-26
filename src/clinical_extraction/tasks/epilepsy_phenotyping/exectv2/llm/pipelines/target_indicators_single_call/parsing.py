"""Response parsing / salvage / coercion for the target-indicators single call.

Pure relocation from ``llm_target_indicators_single_call``. No regex or logic
changes.
"""

from __future__ import annotations

import ast
import json
import re
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    MentionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_all_entities import (
    parse_extraction_json as parse_all_entities_extraction_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.records import (  # noqa: E501
    ExtractionRecord,
)


def _parse_target_extraction_json(
    raw_output: str,
) -> tuple[ExtractionRecord | None, list[str]]:
    extraction, errors = parse_all_entities_extraction_json(raw_output)
    if extraction is not None:
        return ExtractionRecord(mentions=list(extraction.mentions)), errors
    literal_payload = _loads_python_literal_payload(raw_output)
    if literal_payload is not None:
        try:
            record = ExtractionRecord.model_validate(literal_payload)
        except Exception as exc:
            errors.append(f"invalid_python_literal_payload: {type(exc).__name__}")
        else:
            return record, ["parsed_python_literal_payload"]
    if not any(error.startswith("invalid_json:") for error in errors):
        return None, errors
    salvaged_mentions, dropped = _salvage_mentions_from_malformed_json(raw_output)
    if not salvaged_mentions:
        return None, errors
    salvage_errors = [f"salvaged_invalid_json_mentions: {len(salvaged_mentions)}"]
    if dropped:
        salvage_errors.append(f"dropped_malformed_json_mentions: {dropped}")
    return ExtractionRecord(mentions=salvaged_mentions), salvage_errors


def _loads_python_literal_payload(raw_output: str) -> dict[str, Any] | None:
    stripped = raw_output.strip()
    if not stripped.startswith("{") or "mentions" not in stripped:
        return None
    try:
        payload = ast.literal_eval(stripped)
    except (SyntaxError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _salvage_mentions_from_malformed_json(raw_output: str) -> tuple[list[MentionRecord], int]:
    mentions: list[MentionRecord] = []
    dropped = 0
    for obj_text in _iter_top_level_json_objects(raw_output):
        payload = _loads_salvageable_mention_object(obj_text)
        if payload is None:
            dropped += 1
            continue
        try:
            mentions.append(MentionRecord.model_validate(payload))
        except Exception:
            dropped += 1
    return mentions, dropped


def _iter_top_level_json_objects(raw_output: str) -> list[str]:
    mentions_index = raw_output.find('"mentions"')
    if mentions_index < 0:
        return []
    array_start = raw_output.find("[", mentions_index)
    array_end = raw_output.rfind("]")
    if array_start < 0:
        return []
    body = (
        raw_output[array_start + 1 : array_end]
        if array_end > array_start
        else raw_output[array_start + 1 :]
    )
    objects: list[str] = []
    level = 0
    start: int | None = None
    for index, char in enumerate(body):
        if char == "{":
            if level == 0:
                start = index
            level += 1
        elif char == "}":
            level -= 1
            if level == 0 and start is not None:
                objects.append(body[start : index + 1])
                start = None
    return objects


def _loads_salvageable_mention_object(obj_text: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(obj_text)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        return _loads_malformed_rationale_mention_object(obj_text)


def _loads_malformed_rationale_mention_object(obj_text: str) -> dict[str, Any] | None:
    entity = _extract_json_string_field(obj_text, "entity")
    evidence = _extract_json_string_field(obj_text, "evidence")
    if not entity or not evidence:
        return None
    attributes = _extract_json_object_field(obj_text, "attributes") or {}
    text = _extract_json_string_field(obj_text, "text") or _infer_text_from_evidence(
        entity,
        evidence,
    )
    if not text:
        return None
    payload: dict[str, Any] = {
        "entity": entity,
        "text": text,
        "attributes": attributes,
        "evidence": evidence,
    }
    confidence = _extract_json_string_field(obj_text, "confidence")
    if confidence:
        payload["confidence"] = confidence
    return payload


def _extract_json_string_field(obj_text: str, field: str) -> str | None:
    match = re.search(
        rf'"{re.escape(field)}"\s*:\s*"(?P<value>(?:[^"\\]|\\.)*)"',
        obj_text,
        re.DOTALL,
    )
    if not match:
        return None
    return json.loads(f'"{match.group("value")}"')


def _extract_json_object_field(obj_text: str, field: str) -> dict[str, Any] | None:
    match = re.search(rf'"{re.escape(field)}"\s*:\s*', obj_text)
    if not match:
        return None
    decoder = json.JSONDecoder()
    try:
        value, _ = decoder.raw_decode(obj_text[match.end() :])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _infer_text_from_evidence(entity: str, evidence: str) -> str:
    normalized = normalize_phrase(evidence)
    if entity == "SeizureFrequency" and "seizure" in normalized:
        return "seizures"
    return ""
