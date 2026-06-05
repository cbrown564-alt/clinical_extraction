"""Structured candidate/event contract for Gan 2026 validation ablations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

MIN_VALIDATION_COVERAGE = 150
MIN_W_TO_C = 25
W_TO_C_GATE_FAILURE = f"w_to_c_below_{MIN_W_TO_C}"
MAX_C_TO_W_RATE = 0.05
MIN_PARSE_OK_EXACT_EVIDENCE_RATE = 0.95

CandidateSource = Literal[
    "deterministic_candidate",
    "state_graph_node",
    "llm_candidate",
    "typed_candidate_contract",
    "structured_event",
    "adjudicator_synthesis",
]
EventKind = Literal[
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "last_event_only",
    "unknown_frequency",
    "no_reference",
]
Temporality = Literal["current", "recent", "historical", "future", "unclear"]
AssertionStatus = Literal["asserted", "negated", "hypothetical", "uncertain"]
PanelRole = Literal["hard", "control", "synthetic_hard", "synthetic_control"]
Transition = Literal["W_to_C", "C_to_W", "C_to_C", "W_to_W", "not_selected"]


@dataclass(frozen=True)
class StructuredCandidateEvent:
    """Typed candidate/event row used before any holdout-facing audit."""

    source_row_index: int
    split: str
    candidate_id: str
    candidate_source: CandidateSource
    event_kind: EventKind
    event_target: str
    temporality: Temporality
    assertion_status: AssertionStatus
    evidence: str
    current_label: str
    proposed_label: str
    gold_label: str
    parse_ok: bool
    exact_evidence: bool
    selected_for_ablation: bool
    panel_role: PanelRole
    prediction_bearing: bool
    transition: Transition
    contract_issues: tuple[str, ...]


def build_candidate_events(
    rows: Sequence[Mapping[str, Any]],
) -> list[StructuredCandidateEvent]:
    """Build typed candidate events from row-shaped validation surfaces."""

    return [build_candidate_event(row) for row in rows]


def build_candidate_event(row: Mapping[str, Any]) -> StructuredCandidateEvent:
    """Build and validate one structured candidate/event row."""

    current_label = str(row.get("current_label") or "")
    proposed_label = str(row.get("proposed_label") or "")
    gold_label = str(row.get("gold_label") or "")
    parse_ok = bool(row.get("parse_ok"))
    evidence = str(row.get("evidence") or "")
    note_text = str(row.get("note_text") or row.get("clinical_text") or "")
    exact_evidence = bool(evidence and note_text and evidence_is_substring(note_text, evidence))
    selected = bool(row.get("selected_for_ablation"))
    prediction_bearing = selected and bool(proposed_label)
    contract_issues = _contract_issues(
        row,
        parse_ok=parse_ok,
        exact_evidence=exact_evidence,
        prediction_bearing=prediction_bearing,
    )
    return StructuredCandidateEvent(
        source_row_index=int(row["source_row_index"]),
        split=str(row.get("split") or "validation"),
        candidate_id=str(row["candidate_id"]),
        candidate_source=_literal(
            row.get("candidate_source"),
            {
                "deterministic_candidate",
                "state_graph_node",
                "llm_candidate",
                "typed_candidate_contract",
                "structured_event",
                "adjudicator_synthesis",
            },
            "typed_candidate_contract",
        ),
        event_kind=_literal(
            row.get("event_kind"),
            {
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
            },
            "unknown_frequency",
        ),
        event_target=str(row.get("event_target") or "seizure"),
        temporality=_literal(
            row.get("temporality"),
            {"current", "recent", "historical", "future", "unclear"},
            "unclear",
        ),
        assertion_status=_literal(
            row.get("assertion_status"),
            {"asserted", "negated", "hypothetical", "uncertain"},
            "uncertain",
        ),
        evidence=evidence,
        current_label=current_label,
        proposed_label=proposed_label,
        gold_label=gold_label,
        parse_ok=parse_ok,
        exact_evidence=exact_evidence,
        selected_for_ablation=selected,
        panel_role=_literal(
            row.get("panel_role"),
            {"hard", "control", "synthetic_hard", "synthetic_control"},
            "hard",
        ),
        prediction_bearing=prediction_bearing,
        transition=_transition(current_label, proposed_label, gold_label, selected),
        contract_issues=contract_issues,
    )


def summarize_validation_gate(
    events: Sequence[StructuredCandidateEvent],
) -> dict[str, Any]:
    """Summarize whether a validation ablation may proceed to frozen test audit."""

    selected = [event for event in events if event.prediction_bearing]
    transitions = Counter(event.transition for event in selected)
    parse_ok_exact = sum(
        event.parse_ok and event.exact_evidence and not event.contract_issues
        for event in selected
    )
    selected_count = len(selected)
    c_to_w_rows = transitions["C_to_W"]
    c_to_w_rate = _rate(c_to_w_rows, selected_count)
    parse_ok_exact_rate = _rate(parse_ok_exact, selected_count)
    gate_failures = []
    if selected_count < MIN_VALIDATION_COVERAGE:
        gate_failures.append("coverage_below_150")
    if transitions["W_to_C"] < MIN_W_TO_C:
        gate_failures.append(W_TO_C_GATE_FAILURE)
    if c_to_w_rate > MAX_C_TO_W_RATE:
        gate_failures.append("c_to_w_above_5_percent")
    if parse_ok_exact_rate < MIN_PARSE_OK_EXACT_EVIDENCE_RATE:
        gate_failures.append("parse_ok_exact_evidence_below_95_percent")
    return {
        "component_name": "structured_candidate_contract",
        "policy_name": "gan2026_structured_candidate_event_contract_v0",
        "selected_prediction_bearing_rows": selected_count,
        "panel_role_counts": dict(sorted(Counter(event.panel_role for event in selected).items())),
        "transition_counts": dict(sorted(transitions.items())),
        "w_to_c_rows": transitions["W_to_C"],
        "c_to_w_rows": c_to_w_rows,
        "c_to_w_rate": c_to_w_rate,
        "parse_ok_exact_evidence_rows": parse_ok_exact,
        "parse_ok_exact_evidence_rate": parse_ok_exact_rate,
        "frozen_test_audit_ready": not gate_failures,
        "gate_failures": gate_failures,
        "claim_boundary": (
            "Validation-development structured candidate/event gate only. "
            "No locked-test row-level inspection or holdout-facing use is authorized."
        ),
    }


def _contract_issues(
    row: Mapping[str, Any],
    *,
    parse_ok: bool,
    exact_evidence: bool,
    prediction_bearing: bool,
) -> tuple[str, ...]:
    issues = []
    for field in (
        "source_row_index",
        "candidate_id",
        "candidate_source",
        "event_kind",
        "evidence",
        "current_label",
        "proposed_label",
    ):
        if row.get(field) in (None, ""):
            issues.append(f"missing_{field}")
    if prediction_bearing and not parse_ok:
        issues.append("parse_not_ok")
    if prediction_bearing and not exact_evidence:
        issues.append("evidence_not_exact")
    return tuple(issues)


def _transition(
    current_label: str,
    proposed_label: str,
    gold_label: str,
    selected: bool,
) -> Transition:
    if not selected:
        return "not_selected"
    current_correct = _purist_correct(current_label, gold_label)
    proposed_correct = _purist_correct(proposed_label, gold_label)
    if not current_correct and proposed_correct:
        return "W_to_C"
    if current_correct and not proposed_correct:
        return "C_to_W"
    if current_correct and proposed_correct:
        return "C_to_C"
    return "W_to_W"


def _purist_correct(prediction_label: str, gold_label: str) -> bool:
    try:
        parsed_prediction = label_to_frequency_record(prediction_label)
        parsed_gold = label_to_frequency_record(gold_label)
    except ValueError:
        return False
    if parsed_prediction is None or parsed_gold is None:
        return False
    return map_purist(parsed_prediction.monthly_frequency) == map_purist(
        parsed_gold.monthly_frequency
    )


def _literal(value: Any, allowed: set[str], default: str) -> Any:
    text = str(value or default)
    return text if text in allowed else default


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
