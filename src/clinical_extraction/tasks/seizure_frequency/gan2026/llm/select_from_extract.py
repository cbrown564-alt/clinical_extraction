"""Apply later-stage LLM select to a codebook extract.

Select reads labelled events and quotes. It does not re-read the letter.
After the call, only join and projection run.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredExtractionRecord,
    StructuredRepairConfig,
    parse_structured_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_select import (
    GAN_LLM_SELECT_POLICY_EXAMPLES,
)

GAN_LLM_SELECT_FROM_EXTRACT = "gan_llm_select_from_extract"

__all__ = [
    "GAN_LLM_SELECT_FROM_EXTRACT",
    "GAN_LLM_SELECT_POLICY_EXAMPLES",
    "apply_llm_select",
    "extract_events_as_select_ledger",
    "later_stage_json_payload",
    "parse_extract_ledger",
    "parse_select_answer",
    "project_encode_label",
    "project_select_label",
]


def later_stage_json_payload(raw_output: str) -> dict[str, Any]:
    blob = extract_json_object(raw_output) or raw_output
    payload = json.loads(blob)
    if not isinstance(payload, dict):
        raise ValueError("later-stage output is not a JSON object")
    return payload


def parse_extract_ledger(
    raw_output: str,
    *,
    note_text: str | None,
) -> StructuredExtractionRecord:
    extraction, _, errors = parse_structured_json(
        raw_output,
        note_text=note_text,
        repair_config=StructuredRepairConfig.for_mode("raw_model"),
    )
    if extraction is None:
        raise ValueError(f"extract raw did not parse: {errors}")
    return extraction


def extract_events_as_select_ledger(
    extract: StructuredExtractionRecord,
) -> list[dict[str, Any]]:
    """Label extract events for select without an encode call."""

    selected = set(extract.selection.selected_event_ids)
    events: list[dict[str, Any]] = []
    for event in extract.events:
        row = event.model_dump()
        if event.event_id in selected and extract.selection.final_label:
            row["label"] = extract.selection.final_label
        else:
            row["label"] = event.raw_value or ""
        events.append(row)
    return events


def parse_select_answer(raw_output: str) -> dict[str, Any]:
    payload = later_stage_json_payload(raw_output)
    block: Mapping[str, Any] = payload
    nested = payload.get("selection")
    if not isinstance(payload.get("selected_event_ids"), list) and isinstance(
        nested, Mapping
    ):
        block = nested
    ids = block.get("selected_event_ids")
    if not isinstance(ids, list):
        raise ValueError("select output has no selected_event_ids")
    answer: dict[str, Any] = {
        "selected_event_ids": [str(item) for item in ids],
    }
    label = block.get("label")
    if label in (None, ""):
        label = block.get("final_label")
    if label not in (None, ""):
        answer["label"] = str(label)
    return answer


def project_encode_label(
    labels_by_id: Mapping[str, str],
    selected_event_ids: Sequence[str],
) -> str | None:
    for event_id in selected_event_ids:
        label = labels_by_id.get(event_id)
        if label:
            return label
    if selected_event_ids:
        return "unknown"
    return "no seizure frequency reference"


def project_select_label(
    labels_by_id: Mapping[str, str],
    selected_event_ids: Sequence[str],
    written_label: str | None,
) -> str | None:
    if written_label:
        return written_label
    return project_encode_label(labels_by_id, selected_event_ids)


def apply_llm_select(
    extract: StructuredExtractionRecord,
    raw_output: str,
    encoded_events: Sequence[Mapping[str, Any]],
) -> StructuredExtractionRecord:
    labels_by_id = {
        str(event["event_id"]): str(event["label"]) for event in encoded_events
    }
    answer = parse_select_answer(raw_output)
    selected_ids = answer["selected_event_ids"]
    return extract.model_copy(
        update={
            "selection": extract.selection.model_copy(
                update={
                    "selected_event_ids": selected_ids,
                    "final_label": project_select_label(
                        labels_by_id,
                        selected_ids,
                        answer.get("label"),
                    ),
                }
            )
        }
    )
