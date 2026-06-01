"""Parser and schema repair for Gan 2026 hybrid adjudicator output."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair import (
    repair_decision_payload,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
)


class AdjudicatorDecisionRecord(BaseModel):
    """Traceable final-selection decision emitted by the DSPy adjudicator."""

    model_config = ConfigDict(extra="forbid")

    assertion_status: Literal[
        "asserted",
        "negated",
        "historical",
        "hypothetical",
        "unclear",
        "mixed",
    ]
    temporality: Literal["current", "recent", "historical", "future", "unclear", "mixed"]
    seizure_or_event_target: str
    window: str
    normalized_rate: str
    uncertainty: Literal["low", "medium", "high"]
    accepted_event_ids: list[str] = Field(default_factory=list)
    rejected_event_ids: list[str] = Field(default_factory=list)
    selected_event_ids: list[str] = Field(default_factory=list)
    final_label: str
    rationale: str


def parse_decision_json(raw_output: str) -> tuple[AdjudicatorDecisionRecord | None, list[str]]:
    """Parse and validate one raw hybrid-adjudicator model output."""

    errors: list[str] = []
    try:
        payload = _repair_adjudicator_required_fields(
            repair_decision_payload(json.loads(_extract_json_object(raw_output)))
        )
    except json.JSONDecodeError as exc:
        return None, [f"invalid_json: {exc.msg}"]

    try:
        decision = AdjudicatorDecisionRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    repaired_label = repair_prediction_label(decision.final_label)
    if repaired_label != decision.final_label:
        errors.append(f"final_label_repaired: {decision.final_label!r} -> {repaired_label!r}")
        decision = decision.model_copy(update={"final_label": repaired_label})

    try:
        label_to_frequency_record(decision.final_label)
    except ValueError as exc:
        errors.append(f"unscorable_final_label: {exc}")

    return decision, errors


def _repair_adjudicator_required_fields(payload: Any) -> Any:
    """Apply adjudicator-owned defaults after shared alias-only repair."""

    if not isinstance(payload, dict):
        return payload

    repaired = dict(payload)
    for key in ("seizure_or_event_target", "window", "normalized_rate", "rationale"):
        if repaired.get(key) is None:
            repaired[key] = "unknown"
    if repaired.get("uncertainty") is None:
        repaired["uncertainty"] = "high"
    return repaired


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
