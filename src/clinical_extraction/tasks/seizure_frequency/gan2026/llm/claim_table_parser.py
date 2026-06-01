"""Parser and schema repair for Gan 2026 LLM claim-table selector output."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, ValidationError


class SectionClaimRecord(BaseModel):
    """One source-near claim from a note section or local text zone."""

    model_config = ConfigDict(extra="forbid")

    claim_id: str
    section: str | None = None
    claim_type: Literal[
        "frequency",
        "cluster_frequency",
        "seizure_free",
        "last_event_only",
        "unknown_frequency",
        "no_reference",
        "non_seizure_event",
    ]
    evidence: str
    anchor_text: str | None = None
    raw_frequency: str | None = None
    cluster_axis: Literal[
        "none",
        "cadence_only",
        "burden_only",
        "cadence_and_burden",
        "vague_cluster",
    ] = "none"
    boundary_state: Literal[
        "ordinary_frequency",
        "seizure_free_interval",
        "unknown_frequency",
        "no_frequency_reference",
        "non_epileptic_or_proxy",
        "last_event_only",
        "conditional_or_window_limited",
    ] = "ordinary_frequency"
    temporality: Literal["current", "recent", "historical", "future", "unclear"]
    assertion_status: Literal["asserted", "negated", "historical", "hypothetical", "unknown"]
    semiology: str | None = None
    uncertainty: Literal["low", "medium", "high"]


class SectionClaimFinalQueryRecord(BaseModel):
    """Model query over claim rows that chooses the Gan-facing answer."""

    model_config = ConfigDict(extra="forbid")

    selected_claim_ids: list[str]
    selector_decision: Literal[
        "select_single_claim",
        "combine_same_window_claims",
        "preserve_cluster_axis",
        "boundary_unknown",
        "boundary_no_reference",
        "boundary_seizure_free",
        "unresolved_conflict",
    ] = "select_single_claim"
    answer_kind: Literal[
        "frequency",
        "seizure_free",
        "unknown",
        "no_reference",
        "unresolved_multiple",
    ]
    cluster_axis: Literal[
        "none",
        "cadence_only",
        "burden_only",
        "cadence_and_burden",
        "vague_cluster",
    ] = "none"
    boundary_state: Literal[
        "ordinary_frequency",
        "seizure_free_interval",
        "unknown_frequency",
        "no_frequency_reference",
        "non_epileptic_or_proxy",
        "last_event_only",
        "conditional_or_window_limited",
    ] = "ordinary_frequency"
    final_label: str | None = None
    raw_selected_frequency: str | None = None
    conversion_note: str | None = None
    evidence: str
    confidence: Literal["low", "medium", "high"]
    rationale: str


class SectionClaimTableExtractionRecord(BaseModel):
    """Full llm-only-claim-table-selector extraction returned by the LLM."""

    model_config = ConfigDict(extra="forbid")

    claims: list[SectionClaimRecord]
    final_query: SectionClaimFinalQueryRecord


def parse_llm_only_claim_table_selector_json(
    raw_output: str,
    *,
    note_text: str | None = None,
) -> tuple[SectionClaimTableExtractionRecord | None, list[str]]:
    """Parse and validate one raw llm-only-claim-table-selector model output."""

    del note_text
    try:
        payload = _repair_llm_only_claim_table_selector_payload(
            json.loads(_extract_json_object(raw_output))
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]
    try:
        extraction = SectionClaimTableExtractionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    errors: list[str] = []
    if not extraction.claims:
        errors.append("claim_extraction: no claim rows")
    claim_ids = {claim.claim_id for claim in extraction.claims}
    missing = [
        claim_id
        for claim_id in extraction.final_query.selected_claim_ids
        if claim_id not in claim_ids
    ]
    if missing:
        errors.append(f"final_query: selected unknown claim IDs {missing}")
    return extraction, errors


def _repair_llm_only_claim_table_selector_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    repaired = dict(payload)
    claims = repaired.get("claims")
    if isinstance(claims, list):
        repaired["claims"] = [
            _repair_claim_payload(claim) if isinstance(claim, dict) else claim for claim in claims
        ]
    final_query = repaired.get("final_query")
    if isinstance(final_query, dict):
        repaired["final_query"] = _repair_final_query_payload(final_query)
    return repaired


def _repair_claim_payload(claim: Mapping[str, Any]) -> dict[str, Any]:
    repaired = dict(claim)
    repaired.pop("evidence_start", None)
    repaired.pop("evidence_end", None)
    repaired["claim_type"] = _repair_enum_alias(
        repaired.get("claim_type"),
        {
            "frequency",
            "cluster_frequency",
            "seizure_free",
            "last_event_only",
            "unknown_frequency",
            "no_reference",
            "non_seizure_event",
        },
    )
    repaired["cluster_axis"] = _repair_enum_alias(
        repaired.get("cluster_axis", "none"),
        {"none", "cadence_only", "burden_only", "cadence_and_burden", "vague_cluster"},
    )
    repaired["boundary_state"] = _repair_enum_alias(
        repaired.get("boundary_state", "ordinary_frequency"),
        {
            "ordinary_frequency",
            "seizure_free_interval",
            "unknown_frequency",
            "no_frequency_reference",
            "non_epileptic_or_proxy",
            "last_event_only",
            "conditional_or_window_limited",
        },
    )
    repaired["temporality"] = _repair_enum_alias(
        repaired.get("temporality"),
        {"current", "recent", "historical", "future", "unclear"},
    )
    repaired["assertion_status"] = _repair_enum_alias(
        repaired.get("assertion_status"),
        {"asserted", "negated", "historical", "hypothetical", "unknown"},
    )
    repaired["uncertainty"] = _repair_enum_alias(
        repaired.get("uncertainty"),
        {"low", "medium", "high"},
    )
    return repaired


def _repair_final_query_payload(final_query: Mapping[str, Any]) -> dict[str, Any]:
    repaired = dict(final_query)
    selected_claim_ids = repaired.get("selected_claim_ids")
    if isinstance(selected_claim_ids, str):
        repaired["selected_claim_ids"] = [
            claim_id.strip() for claim_id in selected_claim_ids.split(",") if claim_id.strip()
        ]
    elif isinstance(selected_claim_ids, list):
        repaired["selected_claim_ids"] = [
            str(_unwrap_singleton(claim_id)).strip()
            for claim_id in selected_claim_ids
            if str(_unwrap_singleton(claim_id)).strip()
        ]
    repaired["answer_kind"] = _repair_answer_kind_alias(
        repaired.get("answer_kind"),
        {
            "frequency",
            "cluster_frequency",
            "seizure_free",
            "unknown",
            "no_reference",
            "unresolved_multiple",
        },
    )
    repaired["selector_decision"] = _repair_enum_alias(
        repaired.get("selector_decision", "select_single_claim"),
        {
            "select_single_claim",
            "combine_same_window_claims",
            "preserve_cluster_axis",
            "boundary_unknown",
            "boundary_no_reference",
            "boundary_seizure_free",
            "unresolved_conflict",
        },
    )
    repaired["cluster_axis"] = _repair_enum_alias(
        repaired.get("cluster_axis", "none"),
        {"none", "cadence_only", "burden_only", "cadence_and_burden", "vague_cluster"},
    )
    repaired["boundary_state"] = _repair_enum_alias(
        repaired.get("boundary_state", "ordinary_frequency"),
        {
            "ordinary_frequency",
            "seizure_free_interval",
            "unknown_frequency",
            "no_frequency_reference",
            "non_epileptic_or_proxy",
            "last_event_only",
            "conditional_or_window_limited",
        },
    )
    repaired["confidence"] = _repair_enum_alias(
        repaired.get("confidence"),
        {"low", "medium", "high"},
    )
    if not repaired.get("rationale") and isinstance(repaired.get("evidence"), str):
        repaired["rationale"] = repaired["evidence"]
        repaired["conversion_note"] = _append_conversion_note(
            repaired.get("conversion_note"),
            (
                "Non-semantic schema repair: final_query.rationale was omitted, "
                "so it was copied from final_query.evidence."
            ),
        )
    return repaired


def _append_conversion_note(existing: Any, note: str) -> str:
    if isinstance(existing, str) and existing.strip():
        return f"{existing.strip()} {note}"
    return note


def _unwrap_singleton(value: Any) -> Any:
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


def _repair_enum_alias(value: Any, allowed: set[str]) -> Any:
    if isinstance(value, list):
        for item in value:
            unwrapped = _unwrap_singleton(item)
            if isinstance(unwrapped, str) and unwrapped in allowed:
                return unwrapped
        return _unwrap_singleton(value)
    return _unwrap_singleton(value)


def _repair_answer_kind_alias(value: Any, allowed: set[str]) -> Any:
    repaired = _repair_enum_alias(value, allowed)
    return _answer_kind_alias(repaired)


def _answer_kind_alias(value: Any) -> Any:
    if value == "cluster_frequency":
        return "frequency"
    return value


def _extract_json_object(raw_output: str) -> str:
    text = raw_output.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text
