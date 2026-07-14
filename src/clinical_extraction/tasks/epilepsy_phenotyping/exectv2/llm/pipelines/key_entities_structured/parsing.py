"""JSON parsing, coercion, and event flattening for structured extraction.

Pure relocation from ``llm_only_key_entities_structured``. No logic changes.
"""

from __future__ import annotations

import json
import re
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    parse_json_payload_with_schema_repair,
)

from .constants import (
    ALLOWED_EVENT_FAMILIES,
)
from .records import (
    MentionForEvidence,
    StructuredExtractionRecord,
)


def parse_structured_events_json(
    raw_output: str,
) -> tuple[StructuredExtractionRecord | None, list[str]]:
    extracted = extract_json_object(raw_output)
    try:
        payload, dialect_notes = parse_json_payload_with_schema_repair(extracted)
    except json.JSONDecodeError as exc:
        repaired_raw, rationale_notes = _strip_non_scored_rationale_fields(extracted)
        if not rationale_notes:
            return None, [f"invalid_json: {exc.msg}"]
        try:
            payload, dialect_notes = parse_json_payload_with_schema_repair(repaired_raw)
        except json.JSONDecodeError:
            return None, [f"invalid_json: {exc.msg}"]
        dialect_notes = [*dialect_notes, *rationale_notes]

    payload, coerce_notes = _coerce_structured_payload(payload)
    try:
        record = StructuredExtractionRecord.model_validate(payload)
    except Exception as exc:
        return None, [f"schema_validation_error: {exc}"]
    return record, [*dialect_notes, *coerce_notes]


def _strip_non_scored_rationale_fields(raw_payload: str) -> tuple[str, list[str]]:
    """Blank malformed free-text rationale values without touching scored fields."""

    repaired, count = re.subn(
        r'"rationale"\s*:\s*"(?:\\.|[^"\\])*?(?=\r?\n\s*[}\]])',
        '"rationale": ""',
        raw_payload,
        flags=re.DOTALL,
    )
    if count == 0:
        return raw_payload, []
    return repaired, ["json_dialect_repaired: stripped_non_scored_rationale"]


def _coerce_structured_payload(payload: Any) -> tuple[Any, list[str]]:
    """Coerce event and mention state values to strings and preserve diagnostics."""

    notes: list[str] = []
    if isinstance(payload, (list, tuple)):
        notes.append("coerced_top_level_event_array")
        payload = {"clinical_events": list(payload)}
    if not isinstance(payload, dict):
        return payload, notes
    events = payload.get("clinical_events")
    if events is None and isinstance(payload.get("mentions"), list):
        events = [_legacy_mention_to_event(m) for m in payload["mentions"]]
        notes.append("coerced_legacy_mentions_to_events")
    if not isinstance(events, list):
        return payload, notes

    coerced_events: list[Any] = []
    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            coerced_events.append(event)
            continue
        event = dict(event)
        family = str(event.get("family", ""))
        mentions = event.get("mentions")
        if family == "reject" and (not isinstance(mentions, list) or not mentions):
            notes.append(f"dropped_no_mention_reject_event: event[{event_index}]")
            continue
        if family not in ALLOWED_EVENT_FAMILIES:
            notes.append(f"dropped_unknown_event_family: event[{event_index}] family={family!r}")
            continue
        event["event_state"] = _stringify_mapping(
            event.get("event_state") or {},
            notes=notes,
            prefix=f"event[{event_index}].event_state",
        )
        if isinstance(mentions, list):
            coerced_mentions: list[Any] = []
            for mention_index, mention in enumerate(mentions):
                if not isinstance(mention, dict):
                    notes.append(
                        "dropped_malformed_mention: "
                        f"event[{event_index}].mentions[{mention_index}] not_object"
                    )
                    continue
                mention = dict(mention)
                missing = [
                    key for key in ("entity", "text") if not str(mention.get(key) or "").strip()
                ]
                if missing:
                    notes.append(
                        "dropped_malformed_mention: "
                        f"event[{event_index}].mentions[{mention_index}] "
                        f"missing={','.join(missing)}"
                    )
                    continue
                mention["attributes"] = _stringify_mapping(
                    mention.get("attributes") or {},
                    notes=notes,
                    prefix=f"event[{event_index}].mentions[{mention_index}].attributes",
                )
                coerced_mentions.append(mention)
            event["mentions"] = coerced_mentions
        coerced_events.append(event)
    return {**payload, "clinical_events": coerced_events}, notes


def _legacy_mention_to_event(mention: Any) -> dict[str, Any]:
    entity = str(mention.get("entity", "")) if isinstance(mention, dict) else ""
    family = {
        "Prescription": "medication",
        "Diagnosis": "diagnosis",
        "SeizureFrequency": "seizure_frequency",
        "Investigations": "investigation",
    }.get(entity, "diagnosis")
    if not isinstance(mention, dict):
        mention = {}
    return {
        "family": family,
        "anchor_text": str(mention.get("text") or ""),
        "evidence": str(mention.get("evidence") or ""),
        "event_state": {},
        "mentions": [mention],
        "confidence": mention.get("confidence") or "medium",
        "rationale": mention.get("rationale") or "",
    }


def _stringify_mapping(mapping: Any, *, notes: list[str], prefix: str) -> dict[str, str]:
    if not isinstance(mapping, dict):
        return {}
    coerced: dict[str, str] = {}
    for key, value in mapping.items():
        if value is None:
            continue
        str_value = str(value)
        if str_value != value:
            notes.append(f"coerced_attribute_value: {prefix}.{key!s} {value!r} -> {str_value!r}")
        coerced[str(key)] = str_value
    return coerced


def flatten_events(record: StructuredExtractionRecord) -> list[MentionForEvidence]:
    mentions: list[MentionForEvidence] = []
    for event in record.clinical_events:
        for mention in event.mentions:
            mentions.append(
                MentionForEvidence(
                    entity=mention.entity,
                    text=mention.text,
                    attributes={str(k): str(v) for k, v in mention.attributes.items()},
                    evidence=event.evidence,
                    confidence=event.confidence,
                    rationale=event.rationale,
                )
            )
    return mentions
