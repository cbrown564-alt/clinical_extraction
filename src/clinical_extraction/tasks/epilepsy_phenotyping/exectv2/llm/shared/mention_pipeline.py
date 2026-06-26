"""Shared mention parsing, evidence gating, and attribute repair for ExECTv2 LLM pipelines."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from clinical_extraction.core.evidence import (
    evidence_is_substring,
    repair_evidence_text_if_source_exact,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import EntitySpec
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    canonicalize_attribute_value,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    parse_json_payload,
)


class MentionRecord(BaseModel):
    """One entity mention emitted by an LLM extraction call."""

    model_config = ConfigDict(extra="ignore")

    text: str
    attributes: dict[str, Any] = {}
    evidence: str
    confidence: Literal["low", "medium", "high"] = "medium"
    rationale: str = ""


class ExtractionRecord(BaseModel):
    """Full LLM output for one letter."""

    model_config = ConfigDict(extra="ignore")

    mentions: list[MentionRecord] = []


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


def repair_attributes(
    attrs: dict[str, str],
    *,
    spec: EntitySpec,
) -> tuple[dict[str, str], list[str]]:
    """Strip illegal attribute keys and illegal closed-vocab values.

    Semantically-neutral: the LLM clinical fact is never altered, only
    schema-invalid keys are dropped. Both actions are logged.
    """
    repaired: dict[str, str] = {}
    warnings: list[str] = []
    for key, value in attrs.items():
        if key in spec.noise_attributes:
            continue
        if key not in spec.legal_attributes:
            warnings.append(f"dropped_illegal_attribute: {key!r}")
            continue
        normalized_value = canonicalize_attribute_value(key, value)
        if normalized_value != value:
            warnings.append(
                f"normalized_attribute_value: {key!r}={value!r} -> {normalized_value!r}"
            )
        if key in spec.closed_vocab and normalized_value not in spec.closed_vocab[key]:
            warnings.append(
                f"dropped_illegal_value: {key!r}={normalized_value!r} not in "
                f"{sorted(spec.closed_vocab[key])}"
            )
            continue
        repaired[key] = normalized_value
    return repaired, warnings


def check_evidence(
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[list[MentionRecord], list[MentionRecord], list[str]]:
    """Partition mentions into (evidence_valid, evidence_invalid).

    Per policy: mentions whose evidence is not an exact substring of the note
    are dropped from the scored set and logged. They are never silently kept.
    """
    valid: list[MentionRecord] = []
    invalid: list[MentionRecord] = []
    warnings: list[str] = []
    for mention in mentions:
        repaired_evidence = repair_evidence_text_if_source_exact(mention.evidence, note_text)
        if repaired_evidence and evidence_is_substring(note_text, repaired_evidence):
            if repaired_evidence != mention.evidence:
                warnings.append(f"repaired_evidence_exact_copy: text={mention.text!r}")
                mention = mention.model_copy(update={"evidence": repaired_evidence})
            valid.append(mention)
            continue
        invalid.append(mention)
        reason = "empty_evidence" if not mention.evidence else "evidence_not_substring"
        warnings.append(f"dropped_{reason}: text={mention.text!r}")
    return valid, invalid, warnings
