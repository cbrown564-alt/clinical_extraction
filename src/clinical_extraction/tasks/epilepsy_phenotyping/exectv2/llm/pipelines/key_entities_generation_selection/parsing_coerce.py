"""Coercion helpers for generation-selection response parsing."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.facts import (
    _normalize_fact_family,
)

_TYPED_ATTRIBUTE_FIELDS = {
    "DrugName",
    "DrugDose",
    "DoseUnit",
    "Frequency",
    "DiagCategory",
    "Certainty",
    "Negation",
    "NumberOfSeizures",
    "LowerNumberOfSeizures",
    "UpperNumberOfSeizures",
    "TimeSince_or_TimeOfEvent",
    "MonthDate",
    "PointInTime",
    "TimePeriod",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "FrequencyChange",
    "MRI_Performed",
    "MRI_Results",
    "EEG_Performed",
    "EEG_Results",
    "CT_Performed",
    "CT_Results",
}

def _coerce_typed_mention_list(
    mentions: Any,
    *,
    prefix: str,
) -> tuple[list[Any], list[str]]:
    if mentions is None:
        return [], []
    if not isinstance(mentions, list):
        return [], [f"{prefix}:schema_validation_error: mentions_not_list"]

    normalized: list[dict[str, Any]] = []
    notes: list[str] = []
    for index, mention in enumerate(mentions):
        if not isinstance(mention, Mapping):
            notes.append(f"{prefix}:dropped_malformed_mention: mention[{index}]")
            continue
        attrs: dict[str, Any] = {}
        raw_attrs = mention.get("attributes") or {}
        if isinstance(raw_attrs, Mapping):
            attrs.update(raw_attrs)
        for field in _TYPED_ATTRIBUTE_FIELDS:
            value = mention.get(field)
            if value is None or value == "":
                continue
            attrs[field] = value
        normalized.append(
            {
                "entity": mention.get("entity"),
                "text": mention.get("text"),
                "attributes": attrs,
                "evidence": mention.get("evidence"),
                "confidence": mention.get("confidence") or "medium",
                "rationale": mention.get("rationale") or "",
            }
        )
    return coerce_mention_list(normalized, prefix=prefix)


def _coerce_event_list(events: Any, *, prefix: str) -> tuple[list[Any], list[str]]:
    payload, notes = structured._coerce_structured_payload({"clinical_events": events or []})
    prefixed_notes = [f"{prefix}:{note}" for note in notes]
    if not isinstance(payload, dict) or not isinstance(payload.get("clinical_events"), list):
        return [], [*prefixed_notes, f"{prefix}:schema_validation_error: events_not_list"]
    return list(payload["clinical_events"]), prefixed_notes


def coerce_mention_list(
    mentions: Any,
    *,
    prefix: str,
    require_mention_id: bool = False,
) -> tuple[list[Any], list[str]]:
    notes: list[str] = []
    if mentions is None:
        return [], notes
    if not isinstance(mentions, list):
        return [], [f"{prefix}:schema_validation_error: mentions_not_list"]

    coerced_mentions: list[Any] = []
    for mention_index, mention in enumerate(mentions):
        if not isinstance(mention, dict):
            notes.append(f"{prefix}:dropped_malformed_mention: mention[{mention_index}]")
            continue
        mention = dict(mention)
        missing = [
            key
            for key in (
                ("mention_id", "entity", "text", "evidence")
                if require_mention_id
                else ("entity", "text", "evidence")
            )
            if not str(mention.get(key) or "").strip()
        ]
        if missing:
            notes.append(
                f"{prefix}:dropped_malformed_mention: "
                f"mention[{mention_index}] missing={','.join(missing)}"
            )
            continue
        mention["attributes"] = structured._stringify_mapping(
            mention.get("attributes") or {},
            notes=notes,
            prefix=f"{prefix}.mention[{mention_index}].attributes",
        )
        if require_mention_id:
            mention["mention_id"] = str(mention["mention_id"])
        coerced_mentions.append(mention)
    return coerced_mentions, notes


def _coerce_clean_render_mention_list(
    mentions: Any,
    *,
    prefix: str,
) -> tuple[list[Any], list[str]]:
    notes: list[str] = []
    if mentions is None:
        return [], notes
    if not isinstance(mentions, list):
        return [], [f"{prefix}:schema_validation_error: mentions_not_list"]

    normalized: list[dict[str, Any]] = []
    for mention_index, mention in enumerate(mentions):
        if not isinstance(mention, Mapping):
            notes.append(f"{prefix}:dropped_malformed_mention: mention[{mention_index}]")
            continue
        clean_text = (
            mention.get("clean_text")
            or mention.get("rendered_text")
            or mention.get("text")
            or ""
        )
        source_text = mention.get("source_text") or ""
        evidence = mention.get("evidence") or source_text
        normalized.append(
            {
                **dict(mention),
                "text": clean_text,
                "evidence": evidence,
            }
        )
        if clean_text and "text" not in mention:
            notes.append(f"{prefix}.mention[{mention_index}].clean_text:used_as_text")
        if evidence and "evidence" not in mention and source_text:
            notes.append(f"{prefix}.mention[{mention_index}].source_text:used_as_evidence")
    coerced, coerced_notes = coerce_mention_list(
        normalized,
        prefix=prefix,
        require_mention_id=True,
    )
    return coerced, [*notes, *coerced_notes]


_DEDUP_FACT_FAMILIES = {
    "diagnosis",
    "seizure_frequency",
    "prescription",
    "investigation",
}


def _coerce_dedup_clinical_facts(
    facts: Any,
    *,
    prefix: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    notes: list[str] = []
    if facts is None:
        return [], notes
    if not isinstance(facts, list):
        return [], [f"{prefix}:schema_validation_error: facts_not_list"]

    coerced: list[dict[str, Any]] = []
    for fact_index, fact in enumerate(facts):
        if not isinstance(fact, Mapping):
            notes.append(f"{prefix}:dropped_malformed_fact: fact[{fact_index}]")
            continue
        normalized = {
            str(key): "" if value is None else str(value).strip()
            for key, value in fact.items()
        }
        family = _normalize_fact_family(normalized.get("family", ""))
        if family not in _DEDUP_FACT_FAMILIES:
            notes.append(
                f"{prefix}:dropped_malformed_fact: fact[{fact_index}] "
                f"family={normalized.get('family')!r}"
            )
            continue
        normalized["family"] = family
        if not normalized.get("evidence"):
            notes.append(
                f"{prefix}:dropped_malformed_fact: fact[{fact_index}] missing=evidence"
            )
            continue
        coerced.append(normalized)
    return coerced, notes


def _coerce_final_mention_ids(payload: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    raw_ids = (
        payload.get("final_mention_ids")
        or payload.get("selected_mention_ids")
        or payload.get("final_ids")
        or []
    )
    notes: list[str] = []
    if isinstance(raw_ids, str):
        raw_ids = [raw_ids]
        notes.append("coerced_final_mention_ids_string_to_list")
    if not isinstance(raw_ids, list):
        return [], ["final_mention_ids:schema_validation_error: ids_not_list"]
    final_ids: list[str] = []
    for index, raw_id in enumerate(raw_ids):
        if raw_id is None:
            continue
        mention_id = str(raw_id).strip()
        if not mention_id:
            notes.append(f"final_mention_ids:dropped_blank_id: index[{index}]")
            continue
        final_ids.append(mention_id)
    return final_ids, notes


def _coerce_id_list(ids: Any, *, prefix: str) -> tuple[list[str], list[str]]:
    notes: list[str] = []
    if isinstance(ids, str):
        ids = [ids]
        notes.append(f"{prefix}:coerced_string_to_list")
    if not isinstance(ids, list):
        return [], [f"{prefix}:schema_validation_error: ids_not_list"]
    coerced: list[str] = []
    for index, raw_id in enumerate(ids):
        if raw_id is None:
            continue
        mention_id = str(raw_id).strip()
        if not mention_id:
            notes.append(f"{prefix}:dropped_blank_id: index[{index}]")
            continue
        coerced.append(mention_id)
    return coerced, notes
