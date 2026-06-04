"""Promoted selective-verifier component for Gan 2026 assembly."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field, ValidationError

PROMOTED_VERIFIER_DESIGN = "binary_quote_highest_answer_selector"

BINARY_SYSTEM_PROMPT = (
    "Check a proposed seizure-frequency answer using the full clinical letter. "
    "Answer the first three fields with only true or false. First, does the "
    "quoted text support the proposed answer? Second, is the proposed answer the "
    "highest current seizure frequency described anywhere in the letter? Third, "
    "are you certain? Then choose exactly one answer from answer_choices. Do not "
    "create a new answer. If none of the answer choices is clearly right, choose "
    "human_review. For the highest-frequency field, compare across all current "
    "or recent seizure/event types in the letter, not only the seizure type named "
    "in the quote. Set selected_label_is_highest_frequency to false if any other "
    "current or recent seizure type is more frequent, if another active seizure "
    "type continues but has no clear count, or if the proposed answer is about "
    "seizure freedom for only one seizure type while another type still occurs. "
    "Do not mark a zero-seizure answer as highest when any current seizure-like "
    "events continue. Only answer true when the proposed answer is at least as "
    "frequent as every other current seizure/event frequency in the full letter. "
    "Return only JSON matching the requested fields."
)


class BinaryQuoteHighestOutput(BaseModel):
    quote_supports_label: bool
    selected_label_is_highest_frequency: bool
    certain: bool
    selected_answer: str
    supporting_quotes: list[str] = Field(default_factory=list)
    reason: str = ""


def build_binary_quote_highest_model_input(
    predeclared: Mapping[str, Any],
    source_text_by_row: Mapping[int, str] | None = None,
) -> dict[str, Any]:
    """Render the promoted verifier's model-facing input."""

    source_text_by_row = source_text_by_row or {}
    snippet_payload = predeclared["prompt_design_candidates"]["support_parts_fact_check"]
    source_row_index = int(predeclared["source_row_index"])
    proposed_answer = snippet_payload.get("proposed_answer")
    return {
        "system_prompt": BINARY_SYSTEM_PROMPT,
        "clinical_text": source_text_by_row.get(source_row_index)
        or snippet_payload.get("clinical_text"),
        "selected_quote": snippet_payload.get("clinical_text"),
        "proposed_answer": proposed_answer,
        "answer_choices": [proposed_answer, "unknown", "human_review"],
        "competing_possibilities": snippet_payload.get("competing_possibilities", []),
        "review_reasons": snippet_payload.get("review_reasons", []),
        "output_schema": {
            "quote_supports_label": "true or false.",
            "selected_label_is_highest_frequency": (
                "true if proposed_answer is the highest current seizure "
                "frequency in clinical_text; otherwise false."
            ),
            "certain": "true or false.",
            "selected_answer": "One value copied from answer_choices.",
            "supporting_quotes": ["Exact copied phrases from clinical_text."],
            "reason": "Brief explanation using only the provided clinical text.",
        },
    }


def parse_binary_quote_highest_output(
    raw_output: str,
) -> tuple[BinaryQuoteHighestOutput | None, list[str]]:
    """Parse the promoted verifier JSON output."""

    try:
        payload = json.loads(_extract_json_object(raw_output))
        payload = normalize_binary_quote_highest_payload(payload)
        parsed = BinaryQuoteHighestOutput.model_validate(payload)
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return None, [f"{type(exc).__name__}: {exc}"]
    return parsed, []


def binary_quote_highest_evidence_exact(
    parsed: BinaryQuoteHighestOutput,
    model_input: Mapping[str, Any],
) -> bool:
    """Check that every returned quote is copied from the clinical text."""

    clinical_text = str(model_input.get("clinical_text") or "")
    return bool(parsed.supporting_quotes) and all(
        quote and quote in clinical_text for quote in parsed.supporting_quotes
    )


def summarize_saved_binary_verifier_rows(
    verifier_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize saved promoted-verifier rows for assembly replay."""

    promoted_rows = [
        row
        for row in verifier_rows
        if str(row.get("task_design") or "") == PROMOTED_VERIFIER_DESIGN
    ]
    delta_counts = Counter(
        str((row.get("verifier_vs_routing") or {}).get("delta") or "")
        for row in promoted_rows
    )
    action_counts = Counter(str(row.get("design_action") or "") for row in promoted_rows)
    parse_ok_rows = [
        row
        for row in promoted_rows
        if row.get("parsed_output") is not None and not row.get("parse_errors")
    ]
    return {
        "component_name": PROMOTED_VERIFIER_DESIGN,
        "row_count": len(promoted_rows),
        "call_ok_rows": sum(row.get("call_status") == "ok" for row in promoted_rows),
        "parse_ok_rows": len(parse_ok_rows),
        "parse_error_rows": len(promoted_rows) - len(parse_ok_rows),
        "decision_changed_rows": sum(
            bool((row.get("verifier_vs_routing") or {}).get("decision_changed"))
            for row in promoted_rows
        ),
        "w_to_c_vs_routing_rows": delta_counts["W_to_C"],
        "c_to_w_vs_routing_rows": delta_counts["C_to_W"],
        "c_to_review_vs_routing_rows": delta_counts["C_to_review"],
        "w_to_review_vs_routing_rows": delta_counts["W_to_review"],
        "unchanged_rows": delta_counts["unchanged"],
        "regression_source_row_indices": [
            int(row["source_row_index"])
            for row in promoted_rows
            if (row.get("verifier_vs_routing") or {}).get("delta") == "C_to_W"
        ],
        "action_counts": dict(sorted(action_counts.items())),
        "delta_counts": dict(sorted(delta_counts.items())),
    }


def normalize_binary_quote_highest_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    normalized = dict(payload)
    value = normalized.get("selected_answer")
    if isinstance(value, list) and len(value) == 1:
        normalized["selected_answer"] = value[0]
    return normalized


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if match:
        return match.group(1)
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        return stripped[first : last + 1]
    raise ValueError("no JSON object found")
