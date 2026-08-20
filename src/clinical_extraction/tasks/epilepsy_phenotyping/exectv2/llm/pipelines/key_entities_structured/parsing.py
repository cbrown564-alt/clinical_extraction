"""JSON parsing and Compact-event coercion for structured extraction."""

from __future__ import annotations

import json
import re
from typing import Any

from clinical_extraction.core.json_schema_repair import (
    parse_json_payload_with_schema_repair,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)

from .constants import (
    ALLOWED_EVENT_FAMILIES,
    FAMILY_TO_ENTITY,
    KEY_ENTITY_NAMES,
)
from .records import StructuredExtractionRecord

_ENTITY_TO_FAMILY = {entity: family for family, entity in FAMILY_TO_ENTITY.items()}


def _with_identity(mapping: dict[str, str]) -> dict[str, str]:
    return {**mapping, **{value: value for value in mapping.values()}}


_ATTR_ALIASES: dict[str, dict[str, str]] = {
    "medication": _with_identity(
        {
            "name": "DrugName",
            "dose": "DrugDose",
            "unit": "DoseUnit",
            "frequency": "Frequency",
        }
    ),
    "diagnosis": _with_identity({"category": "DiagCategory"}),
    "seizure_frequency": _with_identity(
        {
            "count": "NumberOfSeizures",
            "count_lower": "LowerNumberOfSeizures",
            "count_upper": "UpperNumberOfSeizures",
            "periods": "NumberOfTimePeriods",
            "periods_lower": "LowerNumberOfTimePeriods",
            "periods_upper": "UpperNumberOfTimePeriods",
            "period": "TimePeriod",
            "day": "DayDate",
            "month": "MonthDate",
            "year": "YearDate",
            "when": "TimeSince_or_TimeOfEvent",
            "point": "PointInTime",
            "change": "FrequencyChange",
            "age_lower": "AgeLower",
            "age_upper": "AgeUpper",
            "age_unit": "AgeUnit",
        }
    ),
    "investigation": _with_identity(
        {
            "eeg_performed": "EEG_Performed",
            "eeg_result": "EEG_Results",
            "mri_performed": "MRI_Performed",
            "mri_result": "MRI_Results",
            "ct_performed": "CT_Performed",
            "ct_result": "CT_Results",
        }
    ),
}

_VALUE_ALIASES: dict[str, dict[str, str]] = {
    "Frequency": {
        "1": "1",
        "2": "2",
        "3": "3",
        "as_required": "As_Required",
        "asrequired": "As_Required",
    },
    "DiagCategory": {
        "epilepsy": "Epilepsy",
        "multiple_seizures": "MultipleSeizures",
        "multipleseizures": "MultipleSeizures",
        "single_seizure": "SingleSeizure",
        "singleseizure": "SingleSeizure",
    },
    "TimePeriod": {
        "day": "Day",
        "days": "Day",
        "week": "Week",
        "weeks": "Week",
        "month": "Month",
        "months": "Month",
        "year": "Year",
        "years": "Year",
    },
    "TimeSince_or_TimeOfEvent": {
        "during": "During",
        "since": "Since",
    },
    "PointInTime": {
        "birthday": "Birthday",
        "drug_change": "DrugChange",
        "drugchange": "DrugChange",
        "last_clinic": "LastClinic",
        "lastclinic": "LastClinic",
        "last_month": "Last_Month",
        "lastmonth": "Last_Month",
        "last_week": "Last_Week",
        "lastweek": "Last_Week",
        "last_year": "Last_Year",
        "lastyear": "Last_Year",
        "surgery": "Surgery",
    },
    "FrequencyChange": {
        "decreased": "Decreased",
        "frequent": "Frequent",
        "increased": "Increased",
        "infrequent": "Infrequent",
        "same": "Same",
    },
    "AgeUnit": {
        "month": "Month",
        "months": "Month",
        "year": "Year",
        "years": "Year",
    },
    "EEG_Performed": {"yes": "Yes", "no": "No"},
    "EEG_Results": {
        "abnormal": "Abnormal",
        "normal": "Normal",
        "unknown": "Unknown",
    },
    "MRI_Performed": {"yes": "Yes", "no": "No"},
    "MRI_Results": {
        "abnormal": "Abnormal",
        "normal": "Normal",
        "unknown": "Unknown",
    },
    "CT_Performed": {"yes": "Yes", "no": "No"},
    "CT_Results": {
        "abnormal": "Abnormal",
        "normal": "Normal",
        "unknown": "Unknown",
    },
}


def _canonical_value(attr: str, value: str) -> str:
    aliases = _VALUE_ALIASES.get(attr)
    if aliases is None:
        return value
    key = value.strip().lower().replace(" ", "_").replace("-", "_")
    return aliases.get(key, value)


def _canonicalize_compact_attributes(
    family: str, attributes: dict[str, str]
) -> dict[str, str]:
    aliases = _ATTR_ALIASES.get(family) or _ATTR_ALIASES.get(
        _ENTITY_TO_FAMILY.get(family, ""), {}
    )
    canonical: dict[str, str] = {}
    for key, value in attributes.items():
        contract_key = aliases.get(key, key)
        canonical[contract_key] = _canonical_value(contract_key, value)
    return canonical


def _family_for_aliases(family: str, entity: str = "") -> str:
    if family in _ATTR_ALIASES:
        return family
    return _ENTITY_TO_FAMILY.get(entity, family)


def parse_structured_events_json(
    raw_output: str,
    *,
    prompt_version: str | None = None,
) -> tuple[StructuredExtractionRecord | None, list[str]]:
    extracted = extract_json_object(raw_output)
    extracted, structural_notes = _repair_missing_mention_object_close(extracted)
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

    del prompt_version  # Kept for call-site compatibility; only Compact remains.
    payload, coerce_notes = _coerce_structured_payload(payload)
    try:
        record = StructuredExtractionRecord.model_validate(payload)
    except Exception as exc:
        return None, [f"schema_validation_error: {exc}"]
    return record, [*structural_notes, *dialect_notes, *coerce_notes]


def _repair_missing_mention_object_close(raw_payload: str) -> tuple[str, list[str]]:
    """Close one mention before a second mention accidentally nested beside it."""

    repaired, count = re.subn(
        r'("attributes"\s*:\s*\{[^{}]*\})\s*,\s*'
        r'(\{\s*"entity"\s*:.*?"attributes"\s*:\s*\{[^{}]*\}\s*\})'
        r'\s*}\s*(\])',
        r'\1}, \2\3',
        raw_payload,
        flags=re.DOTALL,
    )
    if not count:
        return raw_payload, []
    return repaired, ["json_dialect_repaired: missing_array_object_close"]


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
    """Coerce Compact clinical_events to the living schema."""

    notes: list[str] = []
    if isinstance(payload, (list, tuple)):
        notes.append("coerced_top_level_event_array")
        payload = {"clinical_events": list(payload)}
    if not isinstance(payload, dict):
        return payload, notes
    events = payload.get("clinical_events")
    if not isinstance(events, list):
        return payload, notes

    coerced_events: list[Any] = []
    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        event = dict(event)
        if not str(event.get("family") or "").strip() and event.get("clinical_family"):
            event["family"] = event["clinical_family"]
            notes.append(f"schema_repaired: clinical_family_to_family: event[{event_index}]")
        family = str(event.get("family") or "")
        if family not in ALLOWED_EVENT_FAMILIES:
            notes.append(f"dropped_unknown_event_family: event[{event_index}] family={family!r}")
            continue
        fact = str(event.get("fact") or event.get("event") or "").strip()
        coerced_events.append(
            {
                "family": family,
                "evidence": str(event.get("evidence") or ""),
                "fact": fact,
                "attributes": _canonicalize_compact_attributes(
                    family,
                    _stringify_mapping(
                        event.get("attributes") or {},
                        notes=notes,
                        prefix=f"event[{event_index}].attributes",
                    ),
                ),
            }
        )
    return {"clinical_events": coerced_events}, notes


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


def mentions_from_events(record: StructuredExtractionRecord) -> list[PredictedMention]:
    """Spell each Compact event into the scorer mention names."""

    mentions: list[PredictedMention] = []
    for event in record.clinical_events:
        entity = FAMILY_TO_ENTITY.get(event.family, "")
        if entity not in KEY_ENTITY_NAMES or not event.fact:
            continue
        mentions.append(
            PredictedMention(
                entity=entity,
                text=event.fact,
                attributes={str(key): str(value) for key, value in event.attributes.items()},
                evidence=event.evidence,
            )
        )
    return mentions
