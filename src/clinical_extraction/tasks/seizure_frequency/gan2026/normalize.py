from __future__ import annotations

import re

from clinical_extraction.tasks.seizure_frequency.gan2026.contract import label_parser as _labels
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
)

from .contract.benchmark_prediction_repair import (
    BENCHMARK_REPAIR_RULES,
    BENCHMARK_REPAIR_STEPS,
    FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES,
    FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS,
)
from .contract.gold_policy import (
    CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES,
)
from .deterministic.rules.benchmark_repair import (
    BenchmarkRepairTrace,
    apply_benchmark_repair_rules,
)
from .selected_evidence.selected_evidence_derivation import (
    blocks_inexact_span_family_rewrite,
    prediction_label_from_selected_evidence,
    should_prefer_selected_evidence_label,
)
from .selected_evidence.selected_evidence_monthly_diary import (
    monthly_diary_label_from_text,
)
from .selected_evidence.selected_evidence_rate import (
    _evidence_describes_medication_use_limit,
)
from .selected_evidence.selected_evidence_text import (
    once_twice_thrice as _once_twice_thrice,
)
from .selected_evidence.selected_evidence_text import (
    words_to_numbers as _words_to_numbers,
)
from .selected_evidence.selected_evidence_window import (
    range_count_over_window,
    single_count_over_window,
    sum_counts_over_window,
)

_SIMPLE_RATE_LABEL = re.compile(
    r"^(?P<count>\d+)\s+per\s+(?P<denominator>\d+)\s+(?P<unit>day|week|month|year)$"
)

FrequencyLabelKind = _labels.FrequencyLabelKind
FrequencyLabelRecord = _labels.FrequencyLabelRecord
label_to_frequency_record = _labels.label_to_frequency_record
label_to_monthly_frequency = _labels.label_to_monthly_frequency
normalize_frequency_label = _labels.normalize_frequency_label
parse_label_bounds = _labels.parse_label_bounds
_parse_range = _labels._parse_range

__all__ = [
    "BENCHMARK_REPAIR_RULES",
    "BENCHMARK_REPAIR_STEPS",
    "CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES",
    "FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES",
    "FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS",
    "FrequencyLabelKind",
    "FrequencyLabelRecord",
    "label_to_frequency_record",
    "label_to_monthly_frequency",
    "normalize_frequency_label",
    "parse_label_bounds",
    "repair_prediction_label",
    "repair_prediction_label_clean_scorer_facing",
    "repair_prediction_label_clean_scorer_facing_with_trace",
    "repair_prediction_label_format_preserving",
    "repair_prediction_label_format_preserving_with_trace",
    "repair_prediction_label_with_evidence",
    "repair_prediction_label_with_trace",
]


def repair_prediction_label(
    raw: str | None,
    ablation_config: AblationConfig | None = None,
) -> str:
    """Repair a free-form prediction into a Gan-compatible label string."""
    return repair_prediction_label_with_trace(raw, ablation_config).final_label


def repair_prediction_label_format_preserving(raw: str | None) -> str:
    """Repair only scorer-format issues without semantic fallback/remapping.

    This path is intended for clean LLM-first attribution replays. It preserves
    parser-compatible casing, units, word numbers, event-word noise, and compact
    rate syntax, but leaves vague quantities and unrecognized labels untouched.
    """
    return repair_prediction_label_format_preserving_with_trace(raw).final_label


def repair_prediction_label_clean_scorer_facing(raw: str | None) -> str:
    """Apply clean Gan scorer-facing normalization after strict format repair."""
    return repair_prediction_label_clean_scorer_facing_with_trace(raw).final_label


def repair_prediction_label_clean_scorer_facing_with_trace(
    raw: str | None,
) -> BenchmarkRepairTrace:
    """Strict format repair plus named Gan gold-normalization policy rules."""
    strict_trace = repair_prediction_label_format_preserving_with_trace(raw)
    text, policy_events = apply_benchmark_repair_rules(
        strict_trace.final_label,
        CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES,
        AblationConfig(),
    )
    return BenchmarkRepairTrace(
        raw_label=raw,
        initial_label=strict_trace.initial_label,
        final_label=text,
        events=(*strict_trace.events, *policy_events),
    )


def repair_prediction_label_format_preserving_with_trace(raw: str | None) -> BenchmarkRepairTrace:
    """Strict format-only prediction repair with traceable repair events."""
    if raw is None:
        return BenchmarkRepairTrace(
            raw_label=None,
            initial_label="no seizure frequency reference",
            final_label="no seizure frequency reference",
            events=(),
        )
    text = str(raw).strip().lower()
    if text == "":
        return BenchmarkRepairTrace(
            raw_label=raw,
            initial_label="no seizure frequency reference",
            final_label="no seizure frequency reference",
            events=(),
        )
    initial_label = text
    text, events = apply_benchmark_repair_rules(
        text,
        FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES,
        AblationConfig(),
    )
    return BenchmarkRepairTrace(
        raw_label=raw,
        initial_label=initial_label,
        final_label=text,
        events=events,
    )


def repair_prediction_label_with_evidence(
    raw: str | None,
    evidence: str,
    ablation_config: AblationConfig | None = None,
    context_text: str | None = None,
) -> str:
    """Repair a prediction, using selected evidence only for benchmark formatting.

    The evidence string is assumed to have already been selected by the prediction-bearing
    model or pipeline. This function may preserve explicit counts or time windows from that
    selected evidence, but it does not choose different clinical evidence.
    """

    if raw is None:
        return repair_prediction_label(raw, ablation_config)
    raw_repaired = repair_prediction_label(raw, ablation_config)
    raw_window_label = _raw_window_label(str(raw))
    if raw_repaired == "no seizure frequency reference" and raw_window_label:
        raw_repaired = repair_prediction_label(raw_window_label, ablation_config)
    evidence_label = prediction_label_from_selected_evidence(evidence, context_text)
    if _should_preserve_raw_window_label(raw_window_label, evidence, evidence_label):
        return raw_repaired
    if evidence_label is None and raw_repaired == "no seizure frequency reference":
        evidence_label = prediction_label_from_selected_evidence(str(raw), context_text)
    normalized_evidence = normalize_frequency_label(
        _once_twice_thrice(_words_to_numbers(str(evidence or "")))
    )
    if (
        evidence_label is None
        and normalized_evidence
        and _evidence_describes_medication_use_limit(normalized_evidence)
        and "cluster" in raw_repaired
    ):
        # Rescue/as-required medication cadence is not seizure-frequency evidence.
        return "unknown"
    if (
        evidence_label
        and raw_repaired.startswith("seizure free")
        and not evidence_label.startswith("seizure free")
    ):
        return raw_repaired
    if evidence_label and should_prefer_selected_evidence_label(
        raw,
        raw_repaired,
        evidence,
        evidence_label,
    ):
        if blocks_inexact_span_family_rewrite(
            raw_repaired=raw_repaired,
            evidence=evidence,
            evidence_label=evidence_label,
            context_text=context_text,
        ):
            return raw_repaired
        return repair_prediction_label(evidence_label, ablation_config)
    return raw_repaired


def _raw_window_label(raw_text: str) -> str | None:
    normalized_raw = normalize_frequency_label(raw_text.strip().lower())
    for derive_label in (
        range_count_over_window,
        sum_counts_over_window,
        single_count_over_window,
    ):
        label = derive_label(normalized_raw)
        if label:
            return label
    return None


def _should_preserve_raw_window_label(
    raw_window_label: str | None,
    evidence: str,
    evidence_label: str | None,
) -> bool:
    if raw_window_label is None or evidence_label is None:
        return False
    normalized_evidence = normalize_frequency_label(str(evidence).strip().lower())
    if monthly_diary_label_from_text(normalized_evidence) != evidence_label:
        return False
    raw_match = _SIMPLE_RATE_LABEL.fullmatch(raw_window_label)
    evidence_match = _SIMPLE_RATE_LABEL.fullmatch(evidence_label)
    if raw_match is None or evidence_match is None:
        return False
    return (
        raw_match.group("count") == evidence_match.group("count")
        and raw_match.group("unit") == evidence_match.group("unit")
        and int(raw_match.group("denominator")) > int(evidence_match.group("denominator"))
    )


def repair_prediction_label_with_trace(
    raw: str | None,
    ablation_config: AblationConfig | None = None,
) -> BenchmarkRepairTrace:
    """Repair a prediction and expose benchmark-format repair events."""
    ablation_config = ablation_config or AblationConfig()
    if raw is None:
        return BenchmarkRepairTrace(
            raw_label=None,
            initial_label="no seizure frequency reference",
            final_label="no seizure frequency reference",
            events=(),
        )
    text = str(raw).strip().lower()
    if text == "":
        return BenchmarkRepairTrace(
            raw_label=raw,
            initial_label="no seizure frequency reference",
            final_label="no seizure frequency reference",
            events=(),
        )

    initial_label = text
    text, events = apply_benchmark_repair_rules(
        text,
        BENCHMARK_REPAIR_RULES,
        ablation_config,
    )
    return BenchmarkRepairTrace(
        raw_label=raw,
        initial_label=initial_label,
        final_label=text,
        events=events,
    )
