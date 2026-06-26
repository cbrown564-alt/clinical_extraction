"""JSON parsing, coercion, and record-extraction for generation-selection responses."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.facts import (
    _normalize_fact_family,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.records import (
    DedupClinicalFactsRecord,
    StructuredGenerationSelectionRecord,
    StructuredMentionIdSelectionRecord,
    StructuredMentionSelectionRecord,
    StructuredPoolAdjudicationRecord,
    StructuredPoolGroupAdjudicationRecord,
)


def parse_events_json(
    raw_output: str,
) -> tuple[structured.StructuredExtractionRecord | None, list[str]]:
    return structured.parse_structured_events_json(raw_output)


def parse_generation_selection_json(
    raw_output: str,
) -> tuple[StructuredGenerationSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_events, generated_notes = _coerce_event_list(
        payload.get("generated_events") or payload.get("clinical_events") or [],
        prefix="generated_events",
    )
    final_events, final_notes = _coerce_event_list(
        payload.get("final_events") or payload.get("clinical_events") or [],
        prefix="final_events",
    )
    notes.extend(generated_notes)
    notes.extend(final_notes)
    try:
        record = StructuredGenerationSelectionRecord.model_validate(
            {
                **payload,
                "generated_events": generated_events,
                "final_events": final_events,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_generation_selection_mentions_json(
    raw_output: str,
) -> tuple[StructuredMentionSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_mentions, generated_notes = coerce_mention_list(
        payload.get("generated_mentions") or payload.get("mentions") or [],
        prefix="generated_mentions",
    )
    final_mentions, final_notes = coerce_mention_list(
        payload.get("final_mentions") or payload.get("mentions") or [],
        prefix="final_mentions",
    )
    notes.extend(generated_notes)
    notes.extend(final_notes)
    try:
        record = StructuredMentionSelectionRecord.model_validate(
            {
                **payload,
                "generated_mentions": generated_mentions,
                "final_mentions": final_mentions,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


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


def parse_generation_selection_typed_mentions_json(
    raw_output: str,
) -> tuple[StructuredMentionSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_mentions, generated_notes = _coerce_typed_mention_list(
        payload.get("generated_typed_mentions")
        or payload.get("generated_mentions")
        or [],
        prefix="generated_typed_mentions",
    )
    final_mentions, final_notes = _coerce_typed_mention_list(
        payload.get("final_typed_mentions")
        or payload.get("final_mentions")
        or [],
        prefix="final_typed_mentions",
    )
    notes.extend(generated_notes)
    notes.extend(final_notes)
    try:
        record = StructuredMentionSelectionRecord.model_validate(
            {
                **payload,
                "generated_mentions": generated_mentions,
                "final_mentions": final_mentions,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


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


def parse_generation_selection_mention_ids_json(
    raw_output: str,
) -> tuple[StructuredMentionIdSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_mentions, generated_notes = coerce_mention_list(
        payload.get("generated_mentions") or payload.get("mentions") or [],
        prefix="generated_mentions",
        require_mention_id=True,
    )
    final_ids, final_id_notes = _coerce_final_mention_ids(payload)
    notes.extend(generated_notes)
    notes.extend(final_id_notes)
    try:
        record = StructuredMentionIdSelectionRecord.model_validate(
            {
                **payload,
                "generated_mentions": generated_mentions,
                "final_mention_ids": final_ids,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_generation_selection_clean_render_ids_json(
    raw_output: str,
) -> tuple[StructuredMentionIdSelectionRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    generated_mentions, generated_notes = _coerce_clean_render_mention_list(
        payload.get("generated_mentions") or payload.get("mentions") or [],
        prefix="generated_mentions",
    )
    final_ids, final_id_notes = _coerce_final_mention_ids(payload)
    notes.extend(generated_notes)
    notes.extend(final_id_notes)
    try:
        record = StructuredMentionIdSelectionRecord.model_validate(
            {
                **payload,
                "generated_mentions": generated_mentions,
                "final_mention_ids": final_ids,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_dedup_clinical_facts_json(
    raw_output: str,
) -> tuple[DedupClinicalFactsRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    facts, fact_notes = _coerce_dedup_clinical_facts(
        payload.get("clinical_facts") or payload.get("facts") or [],
        prefix="clinical_facts",
    )
    notes.extend(fact_notes)
    try:
        record = DedupClinicalFactsRecord.model_validate(
            {**payload, "clinical_facts": facts}
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_qwen_pool_adjudication_json(
    raw_output: str,
) -> tuple[StructuredPoolAdjudicationRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    final_ids, final_id_notes = _coerce_final_mention_ids(payload)
    notes.extend(final_id_notes)
    selection_summary = payload.get("selection_summary") or []
    if not isinstance(selection_summary, list):
        notes.append("selection_summary:schema_validation_error: summary_not_list")
        selection_summary = []
    try:
        record = StructuredPoolAdjudicationRecord.model_validate(
            {
                **payload,
                "final_mention_ids": final_ids,
                "selection_summary": selection_summary,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def parse_qwen_pool_group_adjudication_json(
    raw_output: str,
) -> tuple[StructuredPoolGroupAdjudicationRecord | None, list[str]]:
    try:
        payload, dialect_notes = structured.parse_json_payload_with_schema_repair(
            extract_json_object(raw_output)
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return None, [f"schema_validation_error: expected_object got {type(payload).__name__}"]

    notes = list(dialect_notes)
    raw_groups = payload.get("fact_groups") or payload.get("groups") or []
    if not isinstance(raw_groups, list):
        raw_groups = []
        notes.append("fact_groups:schema_validation_error: groups_not_list")

    fact_groups: list[dict[str, Any]] = []
    final_ids: list[str] = []
    selection_summary: list[dict[str, Any]] = []
    if not raw_groups:
        alias_ids, alias_notes = _coerce_final_mention_ids(payload)
        notes.extend(alias_notes)
        if alias_ids:
            final_ids.extend(alias_ids)
            notes.append("fact_groups:used_model_emitted_final_mention_ids_alias")
            raw_summary = payload.get("selection_summary") or []
            if isinstance(raw_summary, list):
                selection_summary = [
                    (
                        dict(item)
                        if isinstance(item, Mapping)
                        else {"reason": str(item)}
                    )
                    for item in raw_summary
                ]

    for group_index, raw_group in enumerate(raw_groups):
        if not isinstance(raw_group, Mapping):
            notes.append(f"fact_groups:dropped_malformed_group: group[{group_index}]")
            continue
        group = dict(raw_group)
        decision = str(group.get("decision") or "").strip().lower()
        if decision not in {"include", "exclude"}:
            decision = "exclude"
            notes.append(f"fact_groups:coerced_unknown_decision_to_exclude: group[{group_index}]")
        equivalent_ids, equivalent_notes = _coerce_id_list(
            group.get("equivalent_mention_ids") or group.get("mention_ids") or [],
            prefix=f"fact_groups.group[{group_index}].equivalent_mention_ids",
        )
        notes.extend(equivalent_notes)
        representative_id = str(group.get("representative_mention_id") or "").strip()
        if decision == "include":
            if representative_id:
                final_ids.append(representative_id)
            else:
                notes.append(
                    f"fact_groups:included_group_missing_representative_id: group[{group_index}]"
                )
        group["decision"] = decision
        group["representative_mention_id"] = representative_id
        group["equivalent_mention_ids"] = equivalent_ids
        fact_groups.append(group)
        selection_summary.append(
            {
                "group_id": str(group.get("group_id") or f"group[{group_index}]"),
                "decision": decision,
                "mention_id": representative_id,
                "reason": str(group.get("reason") or ""),
            }
        )

    try:
        record = StructuredPoolGroupAdjudicationRecord.model_validate(
            {
                **payload,
                "fact_groups": fact_groups,
                "final_mention_ids": final_ids,
                "selection_summary": selection_summary,
            }
        )
    except Exception as exc:
        return None, [*notes, f"schema_validation_error: {exc}"]
    return record, notes


def final_record_from_generation_selection(
    record: StructuredGenerationSelectionRecord,
) -> structured.StructuredExtractionRecord:
    return structured.StructuredExtractionRecord(clinical_events=record.final_events)


def final_mentions_from_generation_selection(
    record: StructuredMentionSelectionRecord,
) -> list[structured.MentionForEvidence]:
    return list(record.final_mentions)


def final_mentions_from_mention_id_selection(
    record: StructuredMentionIdSelectionRecord,
) -> tuple[list[structured.MentionForEvidence], list[str]]:
    by_id: dict[str, dict[str, Any]] = {}
    notes: list[str] = []
    for mention in record.generated_mentions:
        mention_id = str(mention.get("mention_id") or "").strip()
        if not mention_id:
            continue
        if mention_id in by_id:
            notes.append(f"duplicate_generated_mention_id: {mention_id}")
        by_id[mention_id] = mention

    selected: list[structured.MentionForEvidence] = []
    for mention_id in record.final_mention_ids:
        mention = by_id.get(str(mention_id))
        if mention is None:
            notes.append(f"unknown_final_mention_id: {mention_id}")
            continue
        selected.append(structured.MentionForEvidence.model_validate(mention))
    return selected, notes


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
