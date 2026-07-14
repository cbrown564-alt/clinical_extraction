"""Schemas and scoring helpers owned by the retained Gan V12 ceiling."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.core.evidence import score_evidence_set
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist

DEFAULT_STRUCTURED_EVENT_JSONL_PATH = Path(
    "experiments/"
    "gan2026_three_way_comparison_validation750_hybrid_structured_events_"
    "gpt41mini_2026-06-07.jsonl"
)

DecisionKind = Literal[
    "frequency",
    "seizure_free",
    "unknown",
    "no_reference",
    "unresolved_multiple",
]
Uncertainty = Literal["low", "medium", "high"]
UNCERTAINTY_VALUES = ("low", "medium", "high")
DecisionAttribution = Literal[
    "llm_selected_tool_rendered",
    "llm_selected_format_repaired",
    "llm_original_structured_event_kept",
]
DECISION_ATTRIBUTION_VALUES = (
    "llm_selected_tool_rendered",
    "llm_selected_format_repaired",
    "llm_original_structured_event_kept",
)


class ToolTrace(BaseModel):
    """Optional model-reported trace attached to a V12 decision."""

    model_config = ConfigDict(extra="forbid")

    tool_name: str
    status: str
    input_summary: str | None = None
    output_summary: str | None = None


class ReasonedFrequencyDecision(BaseModel):
    """Common prediction schema used by the retained V12 reasoner."""

    model_config = ConfigDict(extra="forbid")

    final_label: str
    final_kind: DecisionKind
    selected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    rejected_event_ids: tuple[str, ...] = Field(default_factory=tuple)
    evidence: tuple[str, ...] = Field(default_factory=tuple)
    boundary_profile: tuple[str, ...] = Field(default_factory=tuple)
    calculation_trace: str | None = None
    clinical_rationale: str
    uncertainty: Uncertainty
    tool_calls: tuple[ToolTrace, ...] = Field(default_factory=tuple)
    attribution: DecisionAttribution


def inspect_structured_events(
    structured_event_row: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Return compact source-near events without gold or deterministic labels."""

    if structured_event_row is None:
        return {
            "event_table": [],
            "original_final": None,
            "input_warnings": ["missing_structured_event_row"],
        }
    structured_record = dict(structured_event_row.get("structured_record") or {})
    events = [
        _event_table_row(event, structured_event_row)
        for event in structured_record.get("events") or []
        if isinstance(event, Mapping)
    ]
    selection = dict(structured_record.get("selection") or {})
    return {
        "event_table": events,
        "original_final": {
            "final_label": selection.get("final_label"),
            "final_kind": selection.get("final_kind"),
            "selected_event_ids": list(selection.get("selected_event_ids") or []),
            "evidence": selection.get("evidence"),
            "confidence": selection.get("confidence"),
            "rationale": selection.get("rationale"),
        },
        "input_warnings": [],
    }


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize V12 rows across raw, format-only, final, and baseline layers."""

    summary: dict[str, Any] = {
        "rows": len(rows),
        "prediction_bearing_rows": 0,
        "model_calls_attempted": 0,
        "call_failures": 0,
        "parse_or_validation_failures": 0,
        "evidence_exact_substrings": 0,
        "v0_purist_correct": 0,
        "v0_pragmatic_correct": 0,
        "raw_model_purist_correct": 0,
        "raw_model_pragmatic_correct": 0,
        "format_only_purist_correct": 0,
        "format_only_pragmatic_correct": 0,
        "final_purist_correct": 0,
        "final_pragmatic_correct": 0,
        "format_repair_rows": 0,
        "wrong_to_correct_vs_v0": 0,
        "correct_to_wrong_vs_v0": 0,
        "changed_labels_vs_v0": 0,
    }
    final_labels: Counter[str] = Counter()
    for row in rows:
        summary["prediction_bearing_rows"] += int(row.get("decision_record") is not None)
        summary["model_calls_attempted"] += int(row.get("model_call_attempted") is True)
        summary["call_failures"] += int(row.get("call_error") is not None)
        summary["parse_or_validation_failures"] += int(
            _has_blocking_parse_issue(row.get("parse_errors"))
        )
        summary["evidence_exact_substrings"] += int(bool(row.get("evidence_valid")))
        baseline_comparison = dict(
            dict(row.get("v0_reference") or {}).get("comparison") or {}
        )
        summary["v0_purist_correct"] += int(bool(baseline_comparison.get("purist_correct")))
        summary["v0_pragmatic_correct"] += int(
            bool(baseline_comparison.get("pragmatic_correct"))
        )
        for layer_name, summary_prefix in (
            ("raw_model", "raw_model"),
            ("format_only", "format_only"),
            ("final", "final"),
        ):
            comparison = dict(
                dict(dict(row.get("score_layers") or {}).get(layer_name) or {}).get(
                    "comparison"
                )
                or {}
            )
            summary[f"{summary_prefix}_purist_correct"] += int(
                bool(comparison.get("purist_correct"))
            )
            summary[f"{summary_prefix}_pragmatic_correct"] += int(
                bool(comparison.get("pragmatic_correct"))
            )
        transition = dict(row.get("transition_vs_v0") or {})
        summary["wrong_to_correct_vs_v0"] += int(
            transition.get("purist_transition") == "wrong_to_correct"
        )
        summary["correct_to_wrong_vs_v0"] += int(
            transition.get("purist_transition") == "correct_to_wrong"
        )
        summary["changed_labels_vs_v0"] += int(bool(transition.get("label_changed")))
        summary["format_repair_rows"] += int(bool(row.get("format_repair_events")))
        final_label = dict(dict(row.get("score_layers") or {}).get("final") or {}).get(
            "final_label"
        )
        if final_label is not None:
            final_labels[str(final_label)] += 1
    summary["net_purist_gain_vs_v0"] = (
        summary["wrong_to_correct_vs_v0"] - summary["correct_to_wrong_vs_v0"]
    )
    summary["changed_label_precision_vs_v0"] = (
        round(summary["wrong_to_correct_vs_v0"] / summary["changed_labels_vs_v0"], 4)
        if summary["changed_labels_vs_v0"]
        else None
    )
    summary["final_labels"] = dict(sorted(final_labels.items()))
    return summary


def gate_interpretation(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Interpret the retained V12 schema and evidence gate."""

    rows = int(summary.get("rows", 0))
    prediction_bearing_rows = int(summary.get("prediction_bearing_rows", 0))
    if rows > 0 and prediction_bearing_rows == 0:
        return {
            "status": "prompt_only_no_prediction",
            "rows": rows,
            "parse_or_validation_failure_rate": 0.0,
            "max_parse_or_validation_failure_rate": 0.04,
            "evidence_exact_rate": 0.0,
            "min_evidence_exact_rate": 0.90,
            "interpretation": (
                "Prompt-only scaffold generated without model calls; run live "
                "permitted validation before applying contract gates."
            ),
        }
    parse_failures = int(summary.get("parse_or_validation_failures", 0))
    evidence_exact = int(summary.get("evidence_exact_substrings", 0))
    parse_rate = parse_failures / rows if rows else 0.0
    evidence_rate = evidence_exact / rows if rows else 0.0
    passes_contract = rows > 0 and parse_rate <= 0.04 and evidence_rate >= 0.90
    return {
        "status": "pass_contract_smoke" if passes_contract else "needs_contract_work",
        "rows": rows,
        "parse_or_validation_failure_rate": round(parse_rate, 4),
        "max_parse_or_validation_failure_rate": 0.04,
        "evidence_exact_rate": round(evidence_rate, 4),
        "min_evidence_exact_rate": 0.90,
        "interpretation": (
            "Contract smoke passes; evaluate against predeclared gates next."
            if passes_contract
            else "Do not promote; fix the schema/evidence contract first."
        ),
    }


def _repair_event_to_dict(event: Any) -> dict[str, Any]:
    return {
        "rule_id": event.rule_id,
        "group": str(event.group),
        "portability": str(event.portability),
        "before": event.before,
        "after": event.after,
    }


def _score_layer(
    record: GanFrequencyRecord,
    decision: ReasonedFrequencyDecision | None,
) -> dict[str, Any]:
    label = decision.final_label if decision else None
    return {
        "final_label": label,
        "final_kind": decision.final_kind if decision else None,
        "attribution": decision.attribution if decision else "no_prediction",
        "comparison": _compare_label_to_gold(record, label),
    }


def _decision_evidence_valid(
    note_text: str,
    decision: ReasonedFrequencyDecision | None,
) -> bool:
    if decision is None or not decision.evidence:
        return False
    scored = score_evidence_set(note_text, decision.evidence)
    return scored.total > 0 and scored.grounded == scored.total


def _v0_reference(structured_event_row: Mapping[str, Any] | None) -> dict[str, Any]:
    if structured_event_row is None:
        return {
            "final_label": None,
            "final_kind": None,
            "selected_event_ids": [],
            "comparison": {},
        }
    selection = dict(
        dict(structured_event_row.get("structured_record") or {}).get("selection") or {}
    )
    return {
        "final_label": selection.get("final_label"),
        "final_kind": selection.get("final_kind"),
        "selected_event_ids": list(selection.get("selected_event_ids") or []),
        "comparison": dict(structured_event_row.get("comparison") or {}),
        "evidence_valid": structured_event_row.get("evidence_valid"),
    }


def _transition_vs_v0(
    *,
    v0_reference: Mapping[str, Any],
    final_layer: Mapping[str, Any],
) -> dict[str, Any]:
    if final_layer.get("final_label") is None:
        return {"purist_transition": "unscored", "label_changed": False}
    baseline_comparison = dict(v0_reference.get("comparison") or {})
    final_comparison = dict(final_layer.get("comparison") or {})
    baseline_correct = baseline_comparison.get("purist_correct")
    final_correct = final_comparison.get("purist_correct")
    if baseline_correct is True and final_correct is True:
        transition = "correct_to_correct"
    elif baseline_correct is True and final_correct is False:
        transition = "correct_to_wrong"
    elif baseline_correct is False and final_correct is True:
        transition = "wrong_to_correct"
    elif baseline_correct is False and final_correct is False:
        transition = "wrong_to_wrong"
    else:
        transition = "unscored"
    return {
        "purist_transition": transition,
        "label_changed": v0_reference.get("final_label") != final_layer.get("final_label"),
    }


def _extract_json_object(raw_output: str) -> str:
    text = raw_output.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end >= start:
        return text[start : end + 1]
    return text


def _event_table_row(
    event: Mapping[str, Any],
    structured_event_row: Mapping[str, Any],
) -> dict[str, Any]:
    event_id = str(event.get("event_id") or "")
    normalized = _normalized_event_by_id(structured_event_row).get(event_id)
    return {
        "event_id": event_id,
        "kind": event.get("kind"),
        "temporality": event.get("temporality"),
        "assertion_status": event.get("assertion_status"),
        "certainty": event.get("certainty"),
        "applies_to": event.get("applies_to"),
        "raw_value": event.get("raw_value"),
        "time_window": event.get("time_window"),
        "evidence": event.get("evidence"),
        "normalized_candidate": _normalized_candidate_summary(normalized),
    }


def _normalized_candidate_summary(
    normalized: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    if normalized is None:
        return None
    return {
        "normalized_label": normalized.get("normalized_label"),
        "semantic_kind": normalized.get("semantic_kind"),
        "monthly_frequency": normalized.get("monthly_frequency"),
        "validation_errors": list(normalized.get("validation_errors") or []),
    }


def _normalized_event_by_id(row: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        str(event.get("event_id")): event
        for event in row.get("normalized_events") or []
        if isinstance(event, Mapping) and event.get("event_id") is not None
    }


def _compare_label_to_gold(record: GanFrequencyRecord, label: str | None) -> dict[str, Any]:
    gold_monthly = record.gold_monthly_frequency
    if label is None:
        return _empty_comparison(gold_monthly, error="missing_label")
    try:
        predicted_record = label_to_frequency_record(str(label))
    except ValueError as exc:
        comparison = _empty_comparison(gold_monthly, error=str(exc))
        comparison["final_label"] = label
        return comparison
    predicted_monthly = predicted_record.monthly_frequency
    predicted_purist = map_purist(predicted_monthly)
    gold_purist = map_purist(gold_monthly)
    predicted_pragmatic = map_pragmatic(predicted_monthly)
    gold_pragmatic = map_pragmatic(gold_monthly)
    return {
        "final_label": predicted_record.normalized_label,
        "predicted_monthly_frequency": predicted_monthly,
        "gold_monthly_frequency": gold_monthly,
        "predicted_purist_category": str(predicted_purist),
        "gold_purist_category": str(gold_purist),
        "purist_correct": predicted_purist == gold_purist,
        "predicted_pragmatic_category": str(predicted_pragmatic),
        "gold_pragmatic_category": str(gold_pragmatic),
        "pragmatic_correct": predicted_pragmatic == gold_pragmatic,
    }


def _empty_comparison(gold_monthly: float, *, error: str) -> dict[str, Any]:
    return {
        "predicted_monthly_frequency": None,
        "gold_monthly_frequency": gold_monthly,
        "predicted_purist_category": None,
        "gold_purist_category": str(map_purist(gold_monthly)),
        "purist_correct": False,
        "predicted_pragmatic_category": None,
        "gold_pragmatic_category": str(map_pragmatic(gold_monthly)),
        "pragmatic_correct": False,
        "error": error,
    }


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(
            ("invalid_json:", "schema_validation_error:", "unscorable_final_label:")
        )
        for error in (errors or [])
    )
