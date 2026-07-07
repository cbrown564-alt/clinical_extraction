"""Parse and coerce stage-1 clinical-findings model outputs."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import ValidationError

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.constants import (
    _CLINICAL_KIND_VALUES,
    _DISALLOWED_MODEL_PROJECTION_FIELDS,
    _SCALAR_EVENT_FRAME_FIELDS,
    _SCALAR_FINDING_FIELDS,
    _STATEMENT_TYPE_TO_KIND,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.types import (
    ClinicalFindingsRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    loads_json_or_literal,
)


def parse_clinical_findings_json(
    raw_output: str,
) -> tuple[ClinicalFindingsRecord | None, list[str]]:
    """Parse and schema-validate one model output string."""

    payload, load_errors = loads_json_or_literal(raw_output)
    if payload is None:
        return None, load_errors

    payload, coerce_notes = _coerce_payload(payload)
    errors: list[str] = [
        *load_errors,
        *_dropped_projection_field_notes(payload),
        *coerce_notes,
    ]

    try:
        record = ClinicalFindingsRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    return record, errors


def _dropped_projection_field_notes(payload: Any) -> list[str]:
    """Report model-supplied benchmark/guideline fields ignored by the schema."""

    if not isinstance(payload, dict):
        return []
    notes: list[str] = []
    for collection_name in ("event_frames", "findings"):
        records = payload.get(collection_name)
        if not isinstance(records, list):
            continue
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            for key in sorted(_DISALLOWED_MODEL_PROJECTION_FIELDS & record.keys()):
                notes.append(
                    f"dropped_model_supplied_projection_field: {collection_name}[{index}] {key!r}"
                )
    return notes


def _coerce_payload(payload: Any) -> tuple[Any, list[str]]:
    notes: list[str] = []
    if not isinstance(payload, dict):
        return payload, notes
    findings_raw = payload.get("findings")
    if findings_raw is None and isinstance(payload.get("mentions"), list):
        findings_raw = payload.get("mentions")
        notes.append("coerced_mentions_key_to_findings")
    coerced_payload = dict(payload)

    if isinstance(findings_raw, list):
        coerced_payload["findings"] = _coerce_record_list(
            findings_raw,
            scalar_fields=_SCALAR_FINDING_FIELDS,
            notes=notes,
            record_name="finding",
            coerce_statement_type=True,
        )

    event_frames_raw = payload.get("event_frames")
    if isinstance(event_frames_raw, list):
        coerced_payload["event_frames"] = _coerce_record_list(
            event_frames_raw,
            scalar_fields=_SCALAR_EVENT_FRAME_FIELDS,
            notes=notes,
            record_name="event_frame",
            coerce_statement_type=False,
        )

    return coerced_payload, notes


def _coerce_record_list(
    records: Sequence[Any],
    *,
    scalar_fields: frozenset[str],
    notes: list[str],
    record_name: str,
    coerce_statement_type: bool,
) -> list[Any]:
    coerced_records: list[Any] = []
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            coerced_records.append(record)
            continue
        new_record = dict(record)
        clinical_kind = str(new_record.get("clinical_kind", ""))
        if (
            coerce_statement_type
            and clinical_kind
            and clinical_kind not in _CLINICAL_KIND_VALUES
            and clinical_kind in _STATEMENT_TYPE_TO_KIND
        ):
            new_record.setdefault("frequency_statement_type", clinical_kind)
            new_record["clinical_kind"] = _STATEMENT_TYPE_TO_KIND[clinical_kind]
            notes.append(
                f"coerced_statement_type_from_clinical_kind: {record_name}[{i}] {clinical_kind!r}"
            )
        for key, value in record.items():
            if key not in scalar_fields or value is None:
                continue
            if not isinstance(value, str):
                new_record[key] = str(value)
                notes.append(
                    f"coerced_field_value: {record_name}[{i}] {key!r} "
                    f"{value!r} -> {new_record[key]!r}"
                )
        coerced_records.append(new_record)
    return coerced_records
