from __future__ import annotations

import re
from enum import StrEnum


class SeizureFrequencyCategory(StrEnum):
    CURRENTLY_NO_SEIZURE = "currently_no_seizure"
    SEIZURE_FREQ_UNKNOWN = "seizure_freq_unknown"
    SEIZURE_FREQ_1_PER_YR = "seizure_freq_1_per_yr"
    SEIZURE_FREQ_1_PER_6MON = "seizure_freq_1_per_6mon"
    SEIZURE_FREQ_MORE1PER6MON_LESS1MON = "seizure_freq_more1per6mon_less1mon"
    SEIZURE_FREQ_1_PER_MON = "seizure_freq_1_per_mon"
    SEIZURE_FREQ_MORE1MON_LESS1WEEK = "seizure_freq_more1mon_less1week"
    SEIZURE_FREQ_1_PER_WEEK = "seizure_freq_1_per_week"
    SEIZURE_FREQ_MORE1WEEK_LESS1DAY = "seizure_freq_more1week_less1day"
    SEIZURE_FREQ_1ORMORE_DAILY = "seizure_freq_1ormore_daily"
    SEIZURE_INFREQUENT = "seizure_infrequent"
    SEIZURE_FREQUENT = "seizure_frequent"


def map_purist(per_month: float) -> str:
    if per_month == 0:
        return SeizureFrequencyCategory.CURRENTLY_NO_SEIZURE
    if per_month == 1000:
        return SeizureFrequencyCategory.SEIZURE_FREQ_UNKNOWN
    if 0 < per_month <= 0.16:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1_PER_YR
    if 0.16 < per_month <= 0.18:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1_PER_6MON
    if 0.18 < per_month <= 0.99:
        return SeizureFrequencyCategory.SEIZURE_FREQ_MORE1PER6MON_LESS1MON
    if 0.99 < per_month <= 1.1:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1_PER_MON
    if 1.1 < per_month <= 3.9:
        return SeizureFrequencyCategory.SEIZURE_FREQ_MORE1MON_LESS1WEEK
    if 3.9 < per_month <= 4.1:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1_PER_WEEK
    if 4.1 < per_month <= 29:
        return SeizureFrequencyCategory.SEIZURE_FREQ_MORE1WEEK_LESS1DAY
    if 29 < per_month <= 999:
        return SeizureFrequencyCategory.SEIZURE_FREQ_1ORMORE_DAILY
    return SeizureFrequencyCategory.SEIZURE_FREQ_UNKNOWN


def map_pragmatic(per_month: float) -> str:
    if per_month == 0:
        return SeizureFrequencyCategory.CURRENTLY_NO_SEIZURE
    if per_month == 1000:
        return SeizureFrequencyCategory.SEIZURE_FREQ_UNKNOWN
    if 0 < per_month <= 1.1:
        return SeizureFrequencyCategory.SEIZURE_INFREQUENT
    if 1.1 < per_month <= 999:
        return SeizureFrequencyCategory.SEIZURE_FREQUENT
    return SeizureFrequencyCategory.SEIZURE_FREQ_UNKNOWN


def _has_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def classify_hidden_families(
    *,
    note_text: str,
    gold_label: str,
    predicted_label: str,
) -> tuple[str, ...]:
    text = " ".join([note_text, gold_label, predicted_label]).lower()
    families: list[str] = []

    if gold_label == "unknown" or predicted_label == "unknown":
        families.append("unknown_boundary")
    if "seizure free" in gold_label or "seizure free" in predicted_label or _has_any(
        text, "seizure-free", "seizure free", "no seizures", "no further events", "last seizure"
    ):
        families.append("seizure_free_duration")
    if _has_any(text, "cluster", "clusters", "per cluster"):
        families.append("cluster_burden")
    if _has_any(text, "diary", "calendar", "log", "entries"):
        families.append("diary_or_log_aggregation")
    if _has_any(text, "nightly", "daily", "weekly", "monthly", "yearly", "per day", "per week"):
        families.append("rate_bucket_or_denominator")
    if _has_any(text, "past ", "since ", "last ", "previous", "histor", "currently", "current"):
        families.append("current_vs_historical")
    if _has_any(
        text,
        "focal",
        "generalised",
        "generalized",
        "absence",
        "tonic",
        "clonic",
        "aura",
        "semiology",
    ):
        families.append("competing_semiologies")
    if _has_any(text, "uncertain", "unclear", "possible", "suspected", "may represent", "unknown"):
        families.append("uncertainty_or_ambiguity")
    if _has_any(text, "bimonthly", "biweekly", "every other", "multiple per", "most weekdays"):
        families.append("benchmark_format_convention")

    if not families:
        families.append("unclassified")
    return tuple(dict.fromkeys(families))


def boundary_band(per_month: float | None) -> str:
    """Coarsen a gold monthly rate into a partitioning frequency-boundary band.

    The bands collapse ``map_purist``'s twelve categories into six
    mutually-exclusive bins keyed off the *gold* rate, so every scored row lands
    in exactly one band regardless of what any candidate predicts. They map onto
    the val->test gap candidates named in the 2026-06-14 next-phase brief
    (denominator/window across the rate bands; unknown/no-reference as
    ``band_unknown``). Thresholds mirror ``map_purist`` exactly.
    """

    if per_month is None:
        return "band_unknown"
    if per_month == 0:
        return "band_zero"
    if per_month == 1000:
        return "band_unknown"
    if 0 < per_month <= 0.99:
        return "band_submonthly"
    if 0.99 < per_month <= 3.9:
        return "band_monthly"
    if 3.9 < per_month <= 29:
        return "band_weekly"
    if 29 < per_month <= 999:
        return "band_daily"
    return "band_unknown"


# Word-boundary qualitative families for gap decomposition. Unlike the legacy
# ``classify_hidden_families`` keyword set, these are anchored on word
# boundaries and scanned over note text only, so they do not saturate on
# substrings ("log" in "neurological") or near-universal label tokens. Only the
# two families that stayed discriminating on validation750 are kept; semiology
# presence was dropped because it fires on a majority of epilepsy notes and so
# cannot isolate the gap.
_CLUSTER_BURDEN_RE = re.compile(r"\bclusters?\b", re.IGNORECASE)
_SEIZURE_FREE_DURATION_RE = re.compile(
    r"\bseizure[- ]free\b|\bno seizures\b|\blast seizure\b"
    r"|\bno further (?:events|seizures)\b",
    re.IGNORECASE,
)


def classify_boundary_families(
    *,
    note_text: str,
    gold_per_month: float | None,
) -> tuple[str, ...]:
    """Sharpened, gap-discriminating family taxonomy for transition readouts.

    Returns the row's partitioning ``boundary_band`` (always exactly one) plus
    any cleaned qualitative families it triggers. This is the taxonomy the
    per-family transition instrumentation uses; the legacy
    ``classify_hidden_families`` is intentionally left untouched because frozen
    pre-registrations (``selective_boundary_candidate_predeclaration``) and the
    ``rq1_rq2`` control panels depend on its exact family names.
    """

    families: list[str] = [boundary_band(gold_per_month)]
    if _CLUSTER_BURDEN_RE.search(note_text):
        families.append("cluster_burden")
    if _SEIZURE_FREE_DURATION_RE.search(note_text):
        families.append("seizure_free_duration")
    return tuple(dict.fromkeys(families))

