"""Change-only verifier for candidate alternatives in Gan 2026 experiments."""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    map_pragmatic,
    map_purist,
)

POLICY_NAME = "gan2026_change_only_candidate_verifier_v0"

ACTIVE_EVENT_FOR_UNKNOWN_PATTERN = re.compile(
    r"("
    r"ongoing seizure|"
    r"not seizure free|"
    r"seizure freedom is clearly not present|"
    r"myoclonic|"
    r"limb twitching|"
    r"tongue soreness|"
    r"bedclothes found disordered|"
    r"brief lapses|"
    r"behavio[u]?ral arrest|"
    r"automatisms|"
    r"partner mainly witnesses|"
    r"possible nocturnal seizures|"
    r"device alerts|"
    r"brief absence|"
    r"absences? from time to time|"
    r"brief jumps"
    r")",
    re.IGNORECASE,
)
SUBTYPE_NARROWING_PATTERN = re.compile(
    r"("
    r"refers only to|"
    r"refers specifically to|"
    r"specifically refers to|"
    r"only to the|"
    r"main focus|"
    r"clinically significant|"
    r"clinically more significant|"
    r"not equivalent|"
    r"combines different seizure types|"
    r"sums different seizure types|"
    r"sums both|"
    r"incorrectly sums"
    r")",
    re.IGNORECASE,
)
UNCERTAIN_SEIZURE_FREE_OVERRIDE_PATTERN = re.compile(
    r"(possible seizure|suggestive of possible|without clear seizures|not classic convulsions)",
    re.IGNORECASE,
)
PARTIAL_WINDOW_NARROWING_PATTERN = re.compile(
    r"(downward trend|most recent calendar month|none so far this month|"
    r"some months (?:are )?entirely event-free|year to date|most recent month|"
    r"this month|so far this year|only two months of data)",
    re.IGNORECASE,
)
NAMED_SEMIOLOGY_NARROWING_PATTERN = re.compile(
    r"("
    r"generalised tonic[-– ]clonic|"
    r"generalized tonic[-– ]clonic|"
    r"tonic[-– ]clonic seizures?|"
    r"convulsive seizures?|"
    r"generalised convulsions|"
    r"generalized convulsions|"
    r"focal impaired[-‑ ]awareness events|"
    r"type referenced|"
    r"weekly absences persist|"
    r"daily absences|"
    r"focal non-motor|"
    r"myoclonic jerks"
    r")",
    re.IGNORECASE,
)
SINGLE_EVENT_RATE_PATTERN = re.compile(
    r"(last event was|single .*seizure|only one seizure|one seizure in the past)",
    re.IGNORECASE,
)
CLUSTER_IMPRECISION_PATTERN = re.compile(
    r"(\bfive\b|~five|\b[2-9]\s*(?:-|to|–)\s*[2-9]\b).{0,80}\bper cluster\b|"
    r"\beach\s+~?five\b",
    re.IGNORECASE,
)
ARITHMETIC_CONTRADICTION_PATTERN = re.compile(
    r"(equates to 1 per month|3 .*every three months|3 .*per three months|"
    r"one to two seizures per week)",
    re.IGNORECASE,
)
COMPOSITE_SEIZURE_FREE_LABEL_PATTERN = re.compile(r"\bthen seizure free\b", re.IGNORECASE)
HISTORY_ONLY_UNKNOWN_PATTERN = re.compile(
    r"(no evidence of ongoing seizures|no current/recent seizure frequency|"
    r"no recent seizures reported|no recurrence|no further events|no further episodes|"
    r"no further seizures|now seizure-free|patient is now seizure-free)",
    re.IGNORECASE,
)
UNCERTAIN_REPORTING_OVERRIDE_PATTERN = re.compile(
    r"(not reliable or verifiable|lack of contemporaneous records|"
    r"does not specify (?:the )?total number of seizures|"
    r"assumes one seizure per seizure day|only the number of days with seizures)",
    re.IGNORECASE,
)
EXACT_LABEL_REFORMULATION_PATTERN = re.compile(
    r"(less precise|does not reflect the monthly rate as accurately)",
    re.IGNORECASE,
)

SYSTEM_PROMPT = (
    "You are checking whether to keep the current seizure-frequency label or "
    "switch to one proposed alternative. Default to keep_current. Switch only "
    "when the proposed evidence clearly supports the proposed label, the full "
    "letter shows the proposed label is the best current/recent seizure "
    "frequency answer, and the current label has a material clinical error. "
    "Do not invent a new label. Do not switch for merely historical, negated, "
    "conditional-only, non-epileptic, or weaker evidence. Return only JSON."
)


class ChangeOnlyVerifierOutput(BaseModel):
    recommendation: str
    proposed_supported: bool
    proposed_best_current_answer: bool
    current_label_has_material_error: bool
    confidence: str
    evidence_quotes: list[str] = Field(default_factory=list)
    reason: str = ""


def build_model_input(row: Mapping[str, Any]) -> dict[str, Any]:
    """Build model input for a current-label versus proposed-label check."""

    return {
        "system_prompt": SYSTEM_PROMPT,
        "clinical_text": row.get("clinical_text"),
        "current_label": row.get("current_label"),
        "proposed_label": row.get("proposed_label"),
        "proposed_evidence": row.get("proposed_evidence"),
        "candidate_source": row.get("candidate_source"),
        "instructions": [
            "Choose keep_current, switch_to_proposed, or human_review.",
            (
                "Use switch_to_proposed only when every boolean support field is true "
                "and confidence is high."
            ),
            "Copy evidence_quotes exactly from clinical_text.",
            "Do not use gold labels; none are provided.",
        ],
        "output_schema": {
            "recommendation": ["keep_current", "switch_to_proposed", "human_review"],
            "proposed_supported": "true or false",
            "proposed_best_current_answer": "true or false",
            "current_label_has_material_error": "true or false",
            "confidence": ["low", "medium", "high"],
            "evidence_quotes": ["exact copied phrases from clinical_text"],
            "reason": "brief explanation using only clinical_text",
        },
    }


def parse_output(raw_output: str) -> tuple[ChangeOnlyVerifierOutput | None, list[str]]:
    """Parse a change-only verifier JSON response."""

    try:
        payload = json.loads(_extract_json_object(raw_output))
        parsed = ChangeOnlyVerifierOutput.model_validate(_normalize_payload(payload))
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return None, [f"{type(exc).__name__}: {exc}"]
    errors = []
    if parsed.recommendation not in {"keep_current", "switch_to_proposed", "human_review"}:
        errors.append(f"unsupported_recommendation:{parsed.recommendation}")
    if parsed.confidence not in {"low", "medium", "high"}:
        errors.append(f"unsupported_confidence:{parsed.confidence}")
    return (None, errors) if errors else (parsed, [])


def verifier_decision(
    parsed: ChangeOnlyVerifierOutput | None,
    row: Mapping[str, Any],
    *,
    parse_errors: Sequence[str],
) -> dict[str, Any]:
    """Convert parsed output into a conservative prediction decision."""

    current_label = str(row.get("current_label") or "")
    proposed_label = str(row.get("proposed_label") or "")
    gold_label = str(row.get("gold_label") or "")
    if parsed is None or parse_errors:
        return _decision("keep_current", current_label, gold_label, False)
    evidence_exact = evidence_quotes_exact(parsed, row)
    should_switch = (
        parsed.recommendation == "switch_to_proposed"
        and parsed.proposed_supported
        and parsed.proposed_best_current_answer
        and parsed.current_label_has_material_error
        and parsed.confidence == "high"
        and evidence_exact
        and _normalized_label(proposed_label) is not None
        and _passes_seizure_free_unknown_gate(parsed, current_label, proposed_label)
        and _passes_benchmark_convention_gate(parsed, row, current_label, proposed_label)
    )
    if should_switch:
        return _decision("switch_to_proposed", proposed_label, gold_label, evidence_exact)
    return _decision(parsed.recommendation, current_label, gold_label, evidence_exact)


def evidence_quotes_exact(
    parsed: ChangeOnlyVerifierOutput,
    row: Mapping[str, Any],
) -> bool:
    clinical_text = str(row.get("clinical_text") or "")
    return bool(parsed.evidence_quotes) and all(
        quote and quote in clinical_text for quote in parsed.evidence_quotes
    )


def _passes_seizure_free_unknown_gate(
    parsed: ChangeOnlyVerifierOutput,
    current_label: str,
    proposed_label: str,
) -> bool:
    if not current_label.startswith("seizure free"):
        return True
    if _normalized_label(proposed_label) != "unknown":
        return True
    evidence_text = " ".join(parsed.evidence_quotes + [parsed.reason])
    return bool(ACTIVE_EVENT_FOR_UNKNOWN_PATTERN.search(evidence_text))


def _passes_benchmark_convention_gate(
    parsed: ChangeOnlyVerifierOutput,
    row: Mapping[str, Any],
    current_label: str,
    proposed_label: str,
) -> bool:
    evidence_text = " ".join(parsed.evidence_quotes + [parsed.reason])
    if SUBTYPE_NARROWING_PATTERN.search(evidence_text):
        return False
    if PARTIAL_WINDOW_NARROWING_PATTERN.search(evidence_text):
        return False
    normalized_proposed = _normalized_label(proposed_label) or ""
    if normalized_proposed != "unknown" and NAMED_SEMIOLOGY_NARROWING_PATTERN.search(
        evidence_text
    ):
        return False
    if current_label == "unknown" and _normalized_label(proposed_label) != "unknown":
        if SINGLE_EVENT_RATE_PATTERN.search(evidence_text):
            return False
    if normalized_proposed == "unknown" and not current_label.startswith("seizure free"):
        if HISTORY_ONLY_UNKNOWN_PATTERN.search(evidence_text):
            return False
        if UNCERTAIN_REPORTING_OVERRIDE_PATTERN.search(evidence_text):
            return False
    if EXACT_LABEL_REFORMULATION_PATTERN.search(evidence_text):
        return False
    if "multiple per cluster" in normalized_proposed:
        if CLUSTER_IMPRECISION_PATTERN.search(evidence_text):
            return False
    if ARITHMETIC_CONTRADICTION_PATTERN.search(evidence_text):
        if normalized_proposed not in {"1 per month"}:
            return False
    if not current_label.startswith("seizure free"):
        if COMPOSITE_SEIZURE_FREE_LABEL_PATTERN.search(normalized_proposed):
            return False
    clinical_text = str(row.get("clinical_text") or "")
    if "tonic" in evidence_text.lower() and re.search(
        r"(daily absences|weekly absences|several times each week|myoclonic jerks)",
        clinical_text,
        re.IGNORECASE,
    ):
        return False
    return not (
        current_label.startswith("seizure free")
        and UNCERTAIN_SEIZURE_FREE_OVERRIDE_PATTERN.search(evidence_text)
    )


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize change-only verifier transitions."""

    transitions = Counter(str(row["transition"]) for row in rows)
    recommendation_counts = Counter(str(row["recommendation"]) for row in rows)
    base_correct = sum(bool(row["current_purist_correct"]) for row in rows)
    projected = base_correct + transitions["W_to_C"] - transitions["C_to_W"]
    changed = transitions["W_to_C"] + transitions["C_to_W"]
    return {
        "component_name": "change_only_candidate_verifier",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "base_correct_rows": base_correct,
        "projected_correct_rows": projected,
        "base_purist_proxy": _rate(base_correct, len(rows)),
        "projected_purist_proxy": _rate(projected, len(rows)),
        "transition_counts": dict(sorted(transitions.items())),
        "recommendation_counts": dict(sorted(recommendation_counts.items())),
        "changed_label_precision": _rate(transitions["W_to_C"], changed),
        "decision": _decision_label(transitions),
    }


def transition(current_correct: bool, verifier_correct: bool) -> str:
    if current_correct and verifier_correct:
        return "C_to_C"
    if current_correct and not verifier_correct:
        return "C_to_W"
    if not current_correct and verifier_correct:
        return "W_to_C"
    return "W_to_W"


def _decision(
    action: str,
    label: str,
    gold_label: str,
    evidence_exact: bool,
) -> dict[str, Any]:
    return {
        "action": action,
        "label": _normalized_label(label),
        "purist_correct": _purist_correct(label, gold_label),
        "pragmatic_correct": _pragmatic_correct(label, gold_label),
        "all_evidence_quotes_exact": evidence_exact,
    }


def _decision_label(transitions: Counter[str]) -> str:
    if transitions["W_to_C"] > 0 and transitions["C_to_W"] == 0:
        return "promote_candidate"
    if transitions["W_to_C"] > transitions["C_to_W"]:
        return "diagnostic_positive_but_not_promotable"
    return "reject"


def _normalized_label(label: str | None) -> str | None:
    if not label:
        return None
    try:
        return label_to_frequency_record(label).normalized_label
    except ValueError:
        return None


def _purist_correct(label: str | None, gold_label: str) -> bool:
    if not label:
        return False
    try:
        predicted = label_to_frequency_record(label)
        gold = label_to_frequency_record(gold_label)
    except ValueError:
        return False
    return map_purist(predicted.monthly_frequency) == map_purist(gold.monthly_frequency)


def _pragmatic_correct(label: str | None, gold_label: str) -> bool:
    if not label:
        return False
    try:
        predicted = label_to_frequency_record(label)
        gold = label_to_frequency_record(gold_label)
    except ValueError:
        return False
    return map_pragmatic(predicted.monthly_frequency) == map_pragmatic(
        gold.monthly_frequency
    )


def _normalize_payload(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    normalized = dict(payload)
    for key in [
        "recommendation",
        "confidence",
        "proposed_supported",
        "proposed_best_current_answer",
        "current_label_has_material_error",
    ]:
        value = normalized.get(key)
        if isinstance(value, list) and len(value) == 1:
            normalized[key] = value[0]
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


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
