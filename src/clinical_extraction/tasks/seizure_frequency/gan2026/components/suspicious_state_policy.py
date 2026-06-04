"""Deterministic suspicious selected-state policy for Gan 2026 assembly."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

REVIEW_FLAGS = {
    "selected_evidence_missing_exact_trace",
    "competing_current_rates_without_controlling_semiology",
    "diary_log_date_list_without_defined_observation_window",
    "denominator_window_mismatch",
    "selected_source_id_invalid",
}

UNKNOWN_FLAGS = {
    "frequency_with_exclusive_conditionality",
    "frequency_with_count_blocking_ambiguity",
    "unresolved_cluster_cadence_with_per_cluster_burden",
    "seizure_free_with_recent_event_blocker",
    "seizure_free_non_all_type_scope_with_current_events",
    "vague_trend_without_absolute_current_frequency",
}


def suspicious_flags(
    state: Mapping[str, Any],
    *,
    exact_trace: bool,
    source_id_status: str,
) -> list[str]:
    """Return deterministic flags for selected states that need routing."""

    flags: list[str] = []
    state_kind = str(state.get("state_kind") or "")
    currentness = str(state.get("currentness") or "")
    conditionality_note = str(state.get("conditionality_note") or "")
    ambiguity_text = _lower_join(
        state.get("ambiguity_flags") or [],
        state.get("competing_state_summary"),
        state.get("raw_model_label_hint"),
    )
    cluster = state.get("cluster") or {}
    rate = state.get("rate") or {}
    boundary = state.get("seizure_free_boundary") or {}
    selected_text = _lower_join(
        state.get("selected_evidence"),
        state.get("raw_source_phrase"),
        rate.get("rate_text"),
        conditionality_note,
    )

    if state_kind == "frequency" and _exclusive_conditionality(currentness, conditionality_note):
        flags.append("frequency_with_exclusive_conditionality")
    if state_kind == "frequency" and _ambiguity_blocks_count(ambiguity_text):
        flags.append("frequency_with_count_blocking_ambiguity")
    if (
        cluster.get("has_cluster_pattern")
        and not cluster.get("cluster_cadence_known")
        and (
            cluster.get("seizures_per_cluster_low") is not None
            or cluster.get("seizures_per_cluster_high") is not None
        )
    ):
        flags.append("unresolved_cluster_cadence_with_per_cluster_burden")
    if state_kind == "seizure_free" and boundary.get("has_recent_events_or_conditions"):
        flags.append("seizure_free_with_recent_event_blocker")
    if (
        state_kind == "seizure_free"
        and not boundary.get("applies_to_all_seizure_types")
        and _has_current_nonzero_events(selected_text, ambiguity_text)
    ):
        flags.append("seizure_free_non_all_type_scope_with_current_events")
    if _competing_current_rates_without_controlling_semiology(state, ambiguity_text):
        flags.append("competing_current_rates_without_controlling_semiology")
    if _diary_log_without_window(selected_text, rate):
        flags.append("diary_log_date_list_without_defined_observation_window")
    if _denominator_window_mismatch(selected_text, rate):
        flags.append("denominator_window_mismatch")
    if _vague_trend_without_absolute_frequency(selected_text, ambiguity_text, rate):
        flags.append("vague_trend_without_absolute_current_frequency")
    if not exact_trace:
        flags.append("selected_evidence_missing_exact_trace")
    if exact_trace and source_id_status not in {"valid", "not_instrumented"}:
        flags.append("selected_source_id_invalid")
    return sorted(set(flags))


def routing_action(flags: Sequence[str]) -> str:
    """Map suspicious-state flags to the deterministic no-call action."""

    if not flags:
        return "render"
    if any(flag in REVIEW_FLAGS for flag in flags):
        return "route_review"
    if any(flag in UNKNOWN_FLAGS for flag in flags):
        return "route_unknown"
    return "render"


def final_policy_label(comparator_label: str, action: str) -> str | None:
    """Return the no-call label for a routed selected state."""

    if action == "route_unknown":
        return "unknown"
    if action == "route_review":
        return None
    return comparator_label


def first_failure_owner(flags: Sequence[str]) -> str:
    """Assign a coarse first-failure owner for suspicious selected-state flags."""

    if not flags:
        return "none"
    if "selected_evidence_missing_exact_trace" in flags:
        return "evidence_trace"
    if "selected_source_id_invalid" in flags:
        return "source_id_trace"
    if any(flag.startswith("seizure_free") for flag in flags):
        return "seizure_free_boundary"
    if any("cluster" in flag for flag in flags):
        return "cluster_boundary"
    if any("conditionality" in flag for flag in flags):
        return "conditionality"
    if any("denominator" in flag or "diary" in flag for flag in flags):
        return "rate_window"
    return "selected_state_ambiguity"


def _exclusive_conditionality(currentness: str, note: str) -> bool:
    text = note.lower()
    if currentness == "conditional":
        return True
    return bool(
        re.search(r"\b(only|exclusively)\s+(?:after|when|if|with|during)\b", text)
        or re.search(r"\b(?:when|if|with|during)\b.*\bonly\b", text)
    )


def _ambiguity_blocks_count(text: str) -> bool:
    return bool(
        re.search(
            r"\b(exact|absolute|number|count|events?).*\b(unclear|unknown|not stated)\b",
            text,
        )
        or re.search(r"\b(unclear|unknown|not stated).*\b(exact|absolute|number|count)\b", text)
    )


def _has_current_nonzero_events(*texts: str) -> bool:
    text = " ".join(texts)
    return bool(
        re.search(r"\b(recent|current|ongoing|continues?|still|breakthrough)\b", text)
        and re.search(r"\b(seizure|event|convulsion|absence|cluster)s?\b", text)
    )


def _competing_current_rates_without_controlling_semiology(
    state: Mapping[str, Any], ambiguity_text: str
) -> bool:
    competing = str(state.get("competing_state_summary") or "").lower()
    applies_to = str(state.get("applies_to") or "").lower()
    if not competing or not re.search(
        r"\b(per|daily|weekly|monthly|yearly|week|month)\b", competing
    ):
        return False
    if any(word in applies_to for word in ("all", "overall", "total")):
        return False
    return "competing" in ambiguity_text or "different" in competing or "also" in competing


def _diary_log_without_window(text: str, rate: Mapping[str, Any]) -> bool:
    if not re.search(r"\b(diary|log|recorded|dates?|entries)\b", text):
        return False
    return not bool(rate.get("rate_time_basis_known") and rate.get("time_unit"))


def _denominator_window_mismatch(text: str, rate: Mapping[str, Any]) -> bool:
    if not bool(rate.get("rate_time_basis_known") and rate.get("time_unit")):
        return False
    if re.search(r"\bper\s+(?:day|week|month|year)\b", text):
        return False
    return bool(
        re.search(r"\b(on|most|many|several)\s+(?:shifts|days|weekdays|nights)\b", text)
        or re.search(r"\bwithin\s+\d+\s+(?:day|week|month|year)s?\b", text)
    )


def _vague_trend_without_absolute_frequency(
    text: str, ambiguity_text: str, rate: Mapping[str, Any]
) -> bool:
    trend_text = f"{text} {ambiguity_text}"
    if not re.search(
        r"\b(more frequent|increased|increase|worse|worsening|thin out)\b", trend_text
    ):
        return False
    return not bool(
        rate.get("time_unit")
        and (rate.get("count_is_multiple") or rate.get("count_low") is not None)
    )


def _lower_join(*values: Any) -> str:
    flattened: list[str] = []
    for value in values:
        if isinstance(value, (list, tuple)):
            flattened.extend(str(item) for item in value)
        elif value is not None:
            flattened.append(str(value))
    return " ".join(flattened).lower()

