from __future__ import annotations

import re

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
    normalize_frequency_label,
)

from .selected_evidence_cluster import (
    cluster_label_from_selected_evidence,
)
from .selected_evidence_monthly_diary import (
    monthly_diary_label_from_text,
)
from .selected_evidence_rate import (
    daily_label_from_selected_evidence,
    early_rate_label_from_selected_evidence,
    evidence_describes_current_non_epileptic_events,
    late_rate_label_from_selected_evidence,
    pre_window_rate_label_from_selected_evidence,
)
from .selected_evidence_text import (
    once_twice_thrice as _once_twice_thrice,
)
from .selected_evidence_text import (
    words_to_numbers as _words_to_numbers,
)
from .selected_evidence_window import (
    range_count_over_window,
    single_count_over_window,
    sum_counts_over_window,
)

__all__ = [
    "blocks_inexact_span_family_rewrite",
    "evidence_describes_current_non_epileptic_events",
    "parsed_frequency_kind",
    "prediction_label_from_selected_evidence",
    "should_prefer_selected_evidence_label",
]


def parsed_frequency_kind(label: str | None) -> str | None:
    """Return a parsed Gan kind, or None when the label is empty or unparsed."""

    if label is None or not str(label).strip():
        return None
    try:
        kind = str(label_to_frequency_record(str(label)).kind)
    except (TypeError, ValueError):
        return None
    if kind not in {item.value for item in FrequencyLabelKind}:
        return None
    return kind


def blocks_inexact_span_family_rewrite(
    *,
    raw_repaired: str,
    evidence: str,
    evidence_label: str,
    context_text: str | None,
) -> bool:
    """True when a paraphrase must not change an already-parsed clinical family.

    Format render stays allowed: unparsed source-near labels and same-kind
    rewrites may still use an inexact quote. Family rewrite
    (unknown ↔ frequency ↔ seizure-free, and other parsed-kind changes)
    requires an exact source span.
    """

    if not context_text or not evidence or not evidence_label:
        return False
    if evidence_is_substring(context_text, evidence):
        return False
    before = parsed_frequency_kind(raw_repaired)
    after = parsed_frequency_kind(evidence_label)
    if before is None or after is None:
        return False
    return before != after


def prediction_label_from_selected_evidence(
    evidence: str,
    context_text: str | None = None,
) -> str | None:
    if not evidence:
        return None

    text = normalize_frequency_label(_once_twice_thrice(_words_to_numbers(evidence)))

    monthly_diary = monthly_diary_label_from_text(text)
    if monthly_diary:
        return monthly_diary

    early_rate = early_rate_label_from_selected_evidence(text)
    if early_rate:
        return early_rate

    cluster_label = cluster_label_from_selected_evidence(text)
    if cluster_label:
        return cluster_label
    if re.search(r"\bclusters?\b", text):
        return None

    pre_window_rate = pre_window_rate_label_from_selected_evidence(text)
    if pre_window_rate:
        return pre_window_rate

    range_count = range_count_over_window(text)
    if range_count:
        return range_count

    summed = sum_counts_over_window(text)
    if summed:
        return summed

    single_count = single_count_over_window(text)
    if single_count:
        return single_count

    return late_rate_label_from_selected_evidence(text, context_text)


def should_prefer_selected_evidence_label(
    raw: str,
    raw_repaired: str,
    evidence: str,
    evidence_label: str,
) -> bool:
    normalized_raw = normalize_frequency_label(_words_to_numbers(str(raw)))
    normalized_evidence = normalize_frequency_label(_words_to_numbers(evidence))
    if any(
        marker in normalized_evidence
        for marker in (
            "quarter",
            "≤",
            "<=",
            "up to",
            "bimonthly",
            "fortnight",
            "median inter-seizure interval",
        )
    ):
        return True
    if re.search(r"\b(?:this|past|last)\s+(?:quarter|year)\b", normalized_evidence):
        return True
    if re.search(
        r"\b(?:so\s+far\s+this\s+year|this\s+year\s+to\s+date|\d{4}\s+so\s+far)\b",
        normalized_evidence,
    ):
        return True
    if re.search(r"\b\d+\s*/\s*30\b.*\b(?:this|past|last)\s+month\b", normalized_evidence):
        return True
    if re.search(r"\b\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?\s+\w*\s*monthly\b", normalized_evidence):
        return True
    if re.search(r"\bevery\s+(?:other|\d+)\s+(?:day|week|month|year)s?\b", normalized_evidence):
        return True
    if re.search(
        r"\bq(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)",
        normalized_evidence,
    ):
        return True
    if monthly_diary_label_from_text(normalized_evidence):
        return True
    if daily_label_from_selected_evidence(normalized_evidence) == evidence_label:
        return True
    if evidence_label == "1 per day" and re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\b(?:almost\s+)?daily\b",
        normalized_evidence,
    ):
        return True
    if " to " in evidence_label and " to " not in raw_repaired:
        return True
    if sum_counts_over_window(normalized_evidence) == evidence_label:
        return True
    if "cluster" in evidence_label and re.search(
        r"\b(?:clusters?|bursts?|grouped|when they recur|without seizures)\b",
        normalized_evidence,
    ):
        return True
    if raw_repaired in {"unknown", "no seizure frequency reference"}:
        return True
    if raw_repaired.startswith("multiple per "):
        return True
    if normalized_raw != raw_repaired and any(
        marker in normalized_raw
        for marker in ("≤", "<=", "up to", "at most", "no more than", "quarter")
    ):
        return True
    normalized_raw_rate = re.sub(
        r"\b(\d+(?:\.\d+)?)\s+or\s+(\d+(?:\.\d+)?)\b",
        r"\1 to \2",
        normalized_raw,
    )
    return not _raw_label_is_simple_rate(normalized_raw_rate)


def _raw_label_is_simple_rate(normalized_raw: str) -> bool:
    return bool(
        re.match(
            r"^(?:multiple|\d+(?:\s*to\s*\d+)?)\s+per\s+"
            r"(?:(?:multiple|\d+(?:\s*to\s*\d+)?)\s+)?"
            r"(?:day|week|month|year)s?$",
            normalized_raw,
        )
    )
