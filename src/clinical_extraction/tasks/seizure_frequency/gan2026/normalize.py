from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.benchmark_repair import (
    BenchmarkRepairStep,
    BenchmarkRepairTrace,
    apply_benchmark_repair_rules,
    benchmark_repair_rule,
)

DAY_IN_YEAR = 365.0
DAYS_PER = {
    "day": 1.0,
    "week": 7.0,
    "month": 30.0,
    "year": 365.0,
}


class FrequencyLabelKind(StrEnum):
    FREQUENCY = "frequency"
    SEIZURE_FREE = "seizure_free"
    UNKNOWN = "unknown"
    NO_REFERENCE = "no_reference"
    UNRESOLVED_MULTIPLE = "unresolved_multiple"


@dataclass(frozen=True)
class FrequencyLabelRecord:
    raw_label: str
    normalized_label: str
    kind: FrequencyLabelKind
    yearly_bounds: tuple[float, float] | None
    monthly_frequency: float


def normalize_frequency_label(label: str) -> str:
    """Normalize label text before Gan-compatible parsing.

    This is a placeholder for the first milestone: port the author-provided repair and
    parsing behavior under tests, preserving benchmark compatibility.
    """
    return " ".join(label.strip().lower().split())


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
    evidence_label = _prediction_label_from_selected_evidence(evidence, context_text)
    if evidence_label is None and raw_repaired == "no seizure frequency reference":
        evidence_label = _prediction_label_from_selected_evidence(str(raw), context_text)
    if evidence_label and _should_prefer_selected_evidence_label(
        raw,
        raw_repaired,
        evidence,
        evidence_label,
    ):
        return repair_prediction_label(evidence_label, ablation_config)
    return raw_repaired


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


def label_to_frequency_record(label: str) -> FrequencyLabelRecord:
    """Convert a normalized Gan label while retaining pre-scoring semantics."""
    normalized = normalize_frequency_label(label)
    if normalized == "unknown":
        return FrequencyLabelRecord(
            raw_label=label,
            normalized_label=normalized,
            kind=FrequencyLabelKind.UNKNOWN,
            yearly_bounds=None,
            monthly_frequency=1000.0,
        )
    if normalized == "no seizure frequency reference":
        return FrequencyLabelRecord(
            raw_label=label,
            normalized_label=normalized,
            kind=FrequencyLabelKind.NO_REFERENCE,
            yearly_bounds=None,
            monthly_frequency=1000.0,
        )

    scoring_label = normalized
    if "cluster" in scoring_label:
        if "unknown" in scoring_label:
            return FrequencyLabelRecord(
                raw_label=label,
                normalized_label=normalized,
                kind=FrequencyLabelKind.UNKNOWN,
                yearly_bounds=None,
                monthly_frequency=1000.0,
            )
        scoring_label = _expand_cluster_label(scoring_label)

    min_per_year, max_per_year = parse_label_bounds(scoring_label)
    if min_per_year == max_per_year == 0:
        kind = FrequencyLabelKind.SEIZURE_FREE
    elif min_per_year < 0 or max_per_year < 0:
        kind = _sentinel_kind(min_per_year, max_per_year)
    else:
        kind = FrequencyLabelKind.FREQUENCY

    monthly_frequency = (
        1000.0
        if min_per_year < 0 or max_per_year < 0
        else ((min_per_year + max_per_year) / 2) / 12
    )
    return FrequencyLabelRecord(
        raw_label=label,
        normalized_label=normalized,
        kind=kind,
        yearly_bounds=(min_per_year, max_per_year),
        monthly_frequency=monthly_frequency,
    )


def parse_label_bounds(label: str) -> tuple[float, float]:
    """Parse a Gan label into yearly lower and upper bounds.

    This follows the author CSV-preparation parser. It normalizes cluster labels by
    counting cluster events and dropping the trailing per-cluster detail.
    """
    if not isinstance(label, str):
        raise ValueError(f"label is not a string: {label!r}")

    raw = label
    normalized = _clean_label_for_bounds(label)

    if "seizure free" in normalized:
        return 0.0, 0.0
    if (
        "unknown" in normalized
        or normalized.startswith("multiple per")
        or " per multiple " in normalized
    ):
        return -1.0, -1.0
    if "no seizure frequency reference" in normalized:
        return -2.0, -2.0

    pattern = re.compile(
        r"^"
        r"(?P<n1>\d+(?:\.\d+)?)(?:\s*to\s*(?P<n2>\d+(?:\.\d+)?))?"
        r"\s+per\s+"
        r"(?:(?P<d1>\d+(?:\.\d+)?)(?:\s*to\s*(?P<d2>\d+(?:\.\d+)?))?\s+)?"
        r"(?P<period>day|week|month|year)s?"
        r"$",
        re.IGNORECASE,
    )
    match = pattern.match(normalized)
    if not match:
        normalized = normalized.replace(" or more per ", " per ")
        normalized = normalized.replace(" to multiple per ", " per ")
        match = pattern.match(normalized)
    if not match:
        raise ValueError(f"Unparsable label (raw: {raw!r} / normalized: {normalized!r})")

    n1, n2 = match.group("n1"), match.group("n2")
    d1, d2 = match.group("d1"), match.group("d2")
    period = match.group("period")

    n_min = _pick_min(n1, n2)
    n_max = _pick_max(n1, n2)
    d_min = _pick_min(d1, d2, default=1.0)
    d_max = _pick_max(d1, d2, default=1.0)
    days = DAYS_PER[period]

    min_per_year = n_min * DAY_IN_YEAR / (d_max * days)
    max_per_year = n_max * DAY_IN_YEAR / (d_min * days)
    return float(min_per_year), float(max_per_year)


def label_to_monthly_frequency(label: str) -> float:
    """Convert a Gan label to the monthly numeric value used by evaluation.

    The evaluation script uses the midpoint of yearly bounds divided by 12. Sentinel
    values for unknown and no-reference are both scored as the unknown category.
    """
    return label_to_frequency_record(label).monthly_frequency


def _sentinel_kind(min_per_year: float, max_per_year: float) -> FrequencyLabelKind:
    if min_per_year == max_per_year == -2.0:
        return FrequencyLabelKind.NO_REFERENCE
    if min_per_year == max_per_year == -1.0:
        return FrequencyLabelKind.UNRESOLVED_MULTIPLE
    return FrequencyLabelKind.UNKNOWN


def _clean_label_for_bounds(label: str) -> str:
    text = label
    for source, replacement in (
        (" or more cluster ", " cluster "),
        (" or more day,", " day,"),
        (" or more month,", " month,"),
        (" or more year,", " year,"),
    ):
        text = text.replace(source, replacement)

    normalized = normalize_frequency_label(text)
    normalized = re.sub(r",\s*[^,]*?\bper\s+cluster\b.*$", "", normalized)
    normalized = re.sub(r"(\d+)\s*[-–—]\s*(\d+)", r"\1 to \2", normalized)
    normalized = re.sub(r"\bclusters?\b", "", normalized)
    return " ".join(normalized.split())


def _expand_cluster_label(label: str) -> str:
    normalized = label.replace("multiple per cluster", "2 per cluster")
    normalized = _replace_multiple_cluster_count(normalized)

    cluster_match = re.search(r"(\d+(?:\s*to\s*\d+)?)\s*clusters?\b", normalized)
    per_cluster_match = re.search(
        r"(\d+(?:\s*to\s*\d+)?)\s*per\s*cluster\b",
        normalized,
    )
    if not cluster_match or not per_cluster_match:
        raise ValueError(f"Unparsable cluster label: {label!r}")

    cluster_min, cluster_max = _parse_range(cluster_match.group(1))
    per_cluster_min, per_cluster_max = _parse_range(per_cluster_match.group(1))
    min_frequency = cluster_min * per_cluster_min
    max_frequency = cluster_max * per_cluster_max

    period_match = re.search(r"per\s+(.+?)(?:,|$)", normalized)
    period = period_match.group(1).strip() if period_match else "month"
    period = _normalize_period(period)

    frequency = (
        str(int(min_frequency))
        if min_frequency == max_frequency
        else f"{int(min_frequency)} to {int(max_frequency)}"
    )
    return f"{frequency} per {period}"


def _replace_multiple_cluster_count(label: str) -> str:
    if label.endswith("week") or "week," in label:
        return label.replace("multiple cluster per ", "2 cluster per ")
    if label.endswith("month") or "month," in label:
        return label.replace("multiple cluster per ", "8 cluster per ")
    if label.endswith("year") or "year," in label:
        return label.replace("multiple cluster per ", "18 cluster per ")
    if label.endswith("day") or "day," in label:
        return label.replace("multiple cluster per ", "2 cluster per ")
    return label


def _normalize_period(period: str) -> str:
    normalized = re.sub(r"\s*(?:-|–)\s*", " to ", period.strip().lower())
    normalized = " ".join(normalized.split())
    for unit in ("week", "day", "month", "year"):
        normalized = re.sub(rf"\b{unit}s\b", unit, normalized)
    return normalized


def _parse_range(token: str) -> tuple[int, int]:
    match = re.match(r"^(\d+)\s*(?:to|-|–)\s*(\d+)$", token.strip().lower())
    if match:
        left, right = int(match.group(1)), int(match.group(2))
        return min(left, right), max(left, right)
    match = re.match(r"^(\d+)$", token.strip().lower())
    if match:
        value = int(match.group(1))
        return value, value
    raise ValueError(f"Malformed range: {token!r}")


def _pick_min(left: str | None, right: str | None, default: float | None = None) -> float:
    if left is None and right is None:
        if default is None:
            raise ValueError("missing numeric bound")
        return default
    if right is None:
        return float(left)
    return min(float(left), float(right))


def _pick_max(left: str | None, right: str | None, default: float | None = None) -> float:
    if left is None and right is None:
        if default is None:
            raise ValueError("missing numeric bound")
        return default
    if right is None:
        return float(left)
    return max(float(left), float(right))


NUM_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
}
UNIT_SYNONYMS = {
    "d": "day",
    "day": "day",
    "days": "day",
    "w": "week",
    "wk": "week",
    "wks": "week",
    "week": "week",
    "weeks": "week",
    "mo": "month",
    "mon": "month",
    "mons": "month",
    "mos": "month",
    "month": "month",
    "months": "month",
    "y": "year",
    "yr": "year",
    "yr.": "year",
    "yrs": "year",
    "year": "year",
    "years": "year",
}
ALLOWED_PREDICTION_PATTERNS = (
    re.compile(r"^unknown$"),
    re.compile(r"^no seizure frequency reference$"),
    re.compile(
        r"^seizure free for (?:multiple|\d+(?:\.\d+)?(?: to \d+(?:\.\d+)?)?) "
        r"(?:month|year)$"
    ),
    re.compile(
        r"^(?:multiple|\d+(?: to \d+)?) per "
        r"(?:(?:multiple|\d+(?: to \d+)?) )?(?:day|week|month|year)$"
    ),
    re.compile(
        r"^(?:multiple|\d+(?: to \d+)?) cluster per "
        r"(?:(?:multiple|\d+(?: to \d+)?) )?(?:day|week|month|year), "
        r"(?:multiple|\d+(?: to \d+)?) per cluster$"
    ),
    re.compile(r"^unknown, (?:multiple|\d+(?: to \d+)?) per cluster$"),
)


def _is_allowed_prediction_format(text: str) -> bool:
    return any(pattern.match(text) for pattern in ALLOWED_PREDICTION_PATTERNS)


def _normalize_unknown_no_reference(text: str) -> str:
    no_reference_pattern = (
        r"\bno (?:seizure )?(?:frequency|freq)"
        r"(?: reference| info(?:rmation)?| mentioned| noted)?\b"
    )
    if re.search(
        no_reference_pattern,
        text,
    ):
        return "no seizure frequency reference"
    if text.strip() == "unknown" or re.fullmatch(r"unknown\s*[,;:]*\s*", text):
        return "unknown"
    return text


def _words_to_numbers(text: str) -> str:
    return re.sub(
        r"\b(" + "|".join(NUM_WORDS) + r")\b",
        lambda match: NUM_WORDS[match.group(0)],
        text,
    )


def _normalize_units(text: str) -> str:
    unit_pattern = "|".join(map(re.escape, sorted(UNIT_SYNONYMS, key=len, reverse=True)))
    text = re.sub(rf"\b({unit_pattern})\b", lambda m: UNIT_SYNONYMS[m.group(0)], text)
    return re.sub(r"\b(day|week|month|year)s\b", r"\1", text)


def _slash_per_forms(text: str) -> str:
    unit_pattern = r"d|day|wk|wks?|week|mo|mon|mos|mons?|month|yr|yrs?|y|year"

    def replace(match: re.Match[str]) -> str:
        unit = UNIT_SYNONYMS.get(match.group("unit"), match.group("unit"))
        return f"{match.group('num')} per {unit}"

    return re.sub(
        rf"(?P<num>\d+(?:\s*to\s*\d+)?)\s*/\s*(?P<unit>{unit_pattern})s?\b",
        replace,
        text,
    )


def _x_times_forms(text: str) -> str:
    unit_pattern = r"d|day|wk|wks?|week|mo|mon|mos?|month|yr|yrs?|y|year"
    text = re.sub(r"(?<=\d)\s*[x×]\s*(?=per\b|/)", " ", text)
    text = re.sub(
        rf"\bx\s*(\d+)\s*/\s*({unit_pattern})s?\b",
        lambda match: f"{match.group(1)} per {UNIT_SYNONYMS.get(match.group(2), '')}",
        text,
    )
    return re.sub(
        r"(\d+(?:\s*to\s*\d+)?)\s*(?:x|times?)\s*"
        r"(?=per\b|/|\b(?:daily|weekly|monthly|yearly|annually)\b)",
        r"\1 ",
        text,
    )


def _every_each_forms(text: str) -> str:
    text = re.sub(r"\b\d+\s+(?=every\s+other\s+(day|week|month|year)\b)", "", text)
    text = re.sub(r"\b\d+\s+(?=(?:every|each)\s+\d+\s*(day|week|month|year)s?\b)", "", text)
    text = re.sub(r"\b(?:every|each)\s+other\s+(day|week|month|year)\b", r"1 per 2 \1", text)
    text = re.sub(r"\b(?:every|each)\s+(\d+)\s*(day|week|month|year)s?\b", r"1 per \1 \2", text)
    text = re.sub(r"\b(?:every|each)\s+(day|week|month|year)s?\b", r"1 per \1", text)
    return re.sub(r"\bper\s+(?:each|every)\s+", "per ", text)


def _period_words(text: str) -> str:
    text = re.sub(
        r"(\d+(?:\s*to\s*\d+)?|\bmultiple\b)?\s*\bweekly\b",
        lambda match: (match.group(1) or "1") + " per week",
        text,
    )
    text = re.sub(
        r"(\d+(?:\s*to\s*\d+)?|\bmultiple\b)?\s*\bmonthly\b",
        lambda match: (match.group(1) or "1") + " per month",
        text,
    )
    text = re.sub(
        r"(\d+(?:\s*to\s*\d+)?|\bmultiple\b)?\s*\bdaily\b",
        lambda match: (match.group(1) or "1") + " per day",
        text,
    )
    text = re.sub(r"\b(?:annually|yearly)\b", "1 per year", text)
    text = re.sub(r"\bsemiweekly\b", "2 per week", text)
    text = re.sub(r"\bbiweekly\b", "1 per 2 week", text)
    text = re.sub(r"\bsemimonthly\b", "2 per month", text)
    return re.sub(r"\bbimonthly\b", "1 per 2 month", text)


def _inequality_to_multiple(text: str) -> str:
    text = re.sub(
        r"\b(?:at least|no less than|more than|over|greater than)\b\s*(\d+(?:\s*to\s*\d+)?)",
        "multiple",
        text,
    )
    text = re.sub(
        r"\b(?:at most|no more than|less than|under|up to)\b\s*(\d+(?:\s*to\s*\d+)?)",
        "multiple",
        text,
    )
    text = re.sub(r"[≥>]\s*\d+(?:\s*to\s*\d+)?", "multiple", text)
    return re.sub(r"[≤<]\s*\d+(?:\s*to\s*\d+)?", "multiple", text)


def _drop_prediction_noise(text: str) -> str:
    text = re.sub(r"\b(?:approximately|approx\.?|about|around|nearly|~)\b", "", text)
    text = re.sub(r"\b(?:a few|few|several)\b", "multiple", text)
    text = re.sub(r"\ba couple of\b", "2", text)
    return _drop_prediction_format_noise(text)


def _drop_prediction_format_noise(text: str) -> str:
    text = re.sub(r"\b(?:approximately|approx\.?|about|around|nearly|~)\b", "", text)
    text = re.sub(r"\bseizures?\b(?!\s*[- ]?free)", "", text)
    text = re.sub(r"\b(?:episodes?|events?|attacks?|spells?|szs?)\b", "", text)
    text = re.sub(r"\b(?:of|the|a|an)\b", "", text)
    return normalize_frequency_label(text)


def _reorder_period_then_count(text: str) -> str:
    if "cluster" in text:
        return text
    return re.sub(
        r"\bper\s+(day|week|month|year)\s+(\d+(?:\s*to\s*\d+)?|multiple)\b",
        r"\2 per \1",
        text,
    )


def _canonicalize_seizure_free(text: str) -> str:
    if (
        "seizure free" not in text
        and "seizure-free" not in text
        and "sz free" not in text
        and "sz-free" not in text
    ):
        return text
    text = text.replace("seizure-free", "seizure free")
    text = text.replace("sz free", "seizure free").replace("sz-free", "seizure free")
    match = re.search(
        r"seizure free(?:\s*for)?\s*"
        r"(\d+(?:\.\d+)?(?:\s*to\s*\d+(?:\.\d+)?)?)\s*(month|year)s?\b",
        text,
    )
    if match:
        return f"seizure free for {match.group(1)} {match.group(2)}"
    if re.search(r"seizure free since\b", text):
        return "seizure free for multiple year"
    return "seizure free for multiple year"


def _fix_cluster_block(text: str) -> str:
    if "cluster" not in text:
        return text
    text = re.sub(r"\bclusters\b", "cluster", text)
    text = re.sub(
        r"\bunknown\s+per\s+cluster\s+(\d+(?:\s*to\s*\d+)?)\b",
        r"unknown, \1 per cluster",
        text,
    )
    text = re.sub(
        r"\bunknown\s+per\s+cluster\s*,\s*(\d+(?:\s*to\s*\d+)?|multiple)\b",
        r"unknown, \1 per cluster",
        text,
    )
    text = re.sub(r"\bunknown\s+per\s+cluster\b", "unknown, multiple per cluster", text)
    text = re.sub(
        r"\b(\d+(?:\s*to\s*\d+)?)\s*per\s*cluster\s*to\s*(\d+(?:\s*to\s*\d+)?)\s*per\s*cluster\b",
        r"\1 to \2 per cluster",
        text,
    )
    text = re.sub(
        r"\b(cluster per (?:\d+(?:\s*to\s*\d+)?\s*)?(?:day|week|month|year))\s+"
        r"(?=(?:\d+(?:\s*to\s*\d+)?|multiple)\s*per\s*cluster\b)",
        r"\1, ",
        text,
    )
    text = re.sub(
        r"\b((?:\d+(?:\s*to\s*\d+)?|multiple)\s*per\s*cluster)\s*,\s*"
        r"((?:\d+(?:\s*to\s*\d+)?|multiple)\s*)cluster\s*per\s*"
        r"((?:\d+(?:\s*to\s*\d+)?\s*)?)(day|week|month|year)\b",
        r"\2cluster per \3\4, \1",
        text,
    )
    if "cluster per" in text and "per cluster" not in text and "unknown" not in text:
        return "unknown"
    return text


def _drop_per_one(text: str) -> str:
    return re.sub(r"\bper\s+1\s+(day|week|month|year)\b", r"per \1", text)


def _cleanup_commas(text: str) -> str:
    text = re.sub(r"\s*,\s*", ", ", text)
    return normalize_frequency_label(text)


def _compress_double_per_range(text: str) -> str:
    pattern = re.compile(
        r"\b(?P<a>(?:multiple|\d+(?:\s*to\s*\d+)?))\s*per\s*"
        r"(?P<dena>(?:\d+(?:\s*to\s*\d+)?\s+)?)?(?P<unita>day|week|month|year)\s*to\s*"
        r"(?P<b>(?:multiple|\d+(?:\s*to\s*\d+)?))\s*per\s*"
        r"(?P<denb>(?:\d+(?:\s*to\s*\d+)?\s+)?)?(?P<unitb>day|week|month|year)\b"
    )

    def replace(match: re.Match[str]) -> str:
        den_a = (match.group("dena") or "").strip() or "1"
        den_b = (match.group("denb") or "").strip() or "1"
        if match.group("unita") != match.group("unitb") or den_a != den_b:
            return match.group(0)
        left = match.group("a")
        right = match.group("b")
        if "multiple" in (left, right):
            return f"multiple per {match.group('unita')}"
        left_min, left_max = _parse_range(left)
        right_min, right_max = _parse_range(right)
        low = min(left_min, right_min)
        high = max(left_max, right_max)
        unit = match.group("unita")
        return f"{low} per {unit}" if low == high else f"{low} to {high} per {unit}"

    previous = None
    while previous != text:
        previous = text
        text = pattern.sub(replace, text)
    return text


def _normalize_cluster_label(text: str) -> str:
    stripped = re.sub(r"\bcluster\b", "", text.strip().lower()).strip()
    match = re.match(
        r"^(\d+(?:\s*to\s*\d+)?)\s*(?:per\s+)?(\d+(?:\s*to\s*\d+)?\s+)?(\w+)?$",
        stripped,
    )
    if not match:
        return text
    number = match.group(1)
    denominator = match.group(2)
    unit = match.group(3)
    if denominator and unit:
        return f"{number} per {denominator.strip()} {unit}"
    if unit:
        return f"{number} per {unit}"
    return f"{number} per month"


def _normalize_cluster_label2(text: str) -> str:
    text = text.replace("，", ",")
    text = normalize_frequency_label(text)
    num = r"\d+(?:\s*to\s*\d+)?"
    unit = r"(?:day|week|month|year)s?"

    dual = re.compile(
        rf"^(?P<v1>{num})\s*(?:cluster\s+)?per\s+(?:(?P<v2>{num})\s+)?"
        rf"(?P<unit>{unit})\s*,\s*(?P<v3>{num})\s+per\s+cluster$"
    )
    match = dual.match(text)
    if match:
        denominator = _omit_one(match.group("v2"))
        unit_value = _singular_unit(match.group("unit"))
        left = f"{match.group('v1')} cluster per "
        left += f"{denominator} {unit_value}" if denominator else unit_value
        return f"{left}, {match.group('v3')} per cluster"

    cleaned = re.sub(rf"\b({num})\s+cluster\s+per\b", r"\1 per", text)
    cleaned = re.sub(r"\bper\s+cluster\s+per\b", "per", cleaned)
    single = re.compile(rf"^(?P<v1>{num})\s*per\s+(?:(?P<v2>{num})\s+)?(?P<unit>{unit})$")
    match = single.match(cleaned)
    if match:
        denominator = _omit_one(match.group("v2"))
        unit_value = _singular_unit(match.group("unit"))
        return f"{match.group('v1')} per {denominator + ' ' if denominator else ''}{unit_value}"

    cluster_only = re.compile(rf"^(?P<v1>{num})\s+per\s+cluster$")
    match = cluster_only.match(text)
    if match:
        return f"unknown, {match.group('v1')} per cluster"
    return text


def _singular_unit(unit: str) -> str:
    return unit[:-1] if unit.endswith("s") else unit


def _omit_one(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = normalize_frequency_label(value)
    return None if normalized == "1" else normalized


def _clean_prediction_extras(text: str) -> str:
    num = r"\d+(?:\s*to\s*\d+)?"
    unit = r"(?:day|week|month|year)s?"
    pattern = re.compile(
        rf"^(?P<head>.*?\bper\s+{num}\s+year)\s+(?P<tail>{num}\s+month)\s*(?P<end>,?.*)$"
    )
    match = pattern.match(text)
    if match:
        end = match.group("end") or ""
        return f"{match.group('head').rstrip()}{(' ' + end.strip()) if end.strip() else ''}".strip()

    pattern = re.compile(
        rf"^(?P<left>.*?\bper\s+(?:{num}\s+)?{unit})\s+to\s+"
        rf"{num}\s+per\s+(?:{num}\s+)?{unit}\s*$"
    )
    match = pattern.match(text)
    if match:
        return match.group("left").strip()
    return text


def _fallback_prediction_repair(text: str) -> str:
    if "unknown" in text:
        match = re.search(r"(\d+(?:\s*to\s*\d+)?|multiple)\s*per\s*cluster", text)
        return f"unknown, {match.group(1)} per cluster" if match else "unknown"
    if "cluster" in text:
        cluster_match = re.search(
            r"(?P<count>(?:\d+(?:\s*to\s*\d+)?|multiple))\s*clusters?\s*per\s*"
            r"(?P<den>(?:\d+(?:\s*to\s*\d+)?\s*)?)(?P<unit>day|week|month|year)",
            text,
        )
        per_cluster_match = re.search(
            r"(?P<pc>(?:\d+(?:\s*to\s*\d+)?|multiple))\s*per\s*cluster",
            text,
        )
        if cluster_match and per_cluster_match:
            denominator = (cluster_match.group("den") or "").strip()
            unit = cluster_match.group("unit")
            den_text = (denominator + " ").strip() if denominator and denominator != "1" else ""
            return (
                f"{cluster_match.group('count')} cluster per {den_text}{unit}, "
                f"{per_cluster_match.group('pc')} per cluster"
            )
        return "unknown"

    match = re.search(
        r"(?P<num>(?:\d+(?:\s*to\s*\d+)?|multiple))\s*per\s*"
        r"(?P<den>(?:\d+(?:\s*to\s*\d+)?\s*)?)(?P<unit>day|week|month|year)",
        text,
    )
    if match:
        denominator = (match.group("den") or "").strip()
        unit = match.group("unit")
        den_text = (denominator + " ").strip() if denominator and denominator != "1" else ""
        return f"{match.group('num')} per {den_text}{unit}"

    event_per_window = re.search(
        r"(?P<num>(?:\d+(?:\s*to\s*\d+)?|multiple))\s+"
        r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,5}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|tonic))"
        r".*?\bper\s+(?P<den>(?:\d+(?:\s*to\s*\d+)?\s*)?)"
        r"(?P<unit>day|week|month|year)",
        text,
    )
    if event_per_window:
        denominator = (event_per_window.group("den") or "").strip()
        unit = event_per_window.group("unit")
        den_text = f"{denominator} " if denominator and denominator != "1" else ""
        return f"{event_per_window.group('num')} per {den_text}{unit}"
    return "no seizure frequency reference"


def _daypart_to_day(text: str) -> str:
    text = text.replace(" per night", " per day")
    text = text.replace(" per morning", " per day")
    text = text.replace(" per afternoon", " per day")
    return text.replace(" per evening", " per day")


def _normalize_ranges(text: str) -> str:
    return re.sub(r"(\d+)\s*[-–—]\s*(\d+)", r"\1 to \2", text)


def _once_twice_thrice(text: str) -> str:
    text = re.sub(r"\bonce\b", "1", text)
    text = re.sub(r"\btwice\b", "2", text)
    return re.sub(r"\bthrice\b", "3", text)


def _drop_times_before_per(text: str) -> str:
    return re.sub(r"\btimes?\b(?=\s+per\b)", "", text)


def _zero_period_to_unknown(text: str) -> str:
    if re.search(r"\bper\s+0\s+(day|week|month|year)\b", text):
        return "unknown"
    return text


def _prediction_label_from_selected_evidence(
    evidence: str,
    context_text: str | None = None,
) -> str | None:
    if not evidence:
        return None

    text = normalize_frequency_label(_once_twice_thrice(_words_to_numbers(evidence)))
    unit = r"day|week|month|year"
    count = r"\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?"

    monthly_diary = monthly_diary_label_from_text(text)
    if monthly_diary:
        return monthly_diary

    q_interval = _q_interval_label_from_selected_evidence(text)
    if q_interval:
        return q_interval

    median_interval = _median_interval_label_from_selected_evidence(text)
    if median_interval:
        return median_interval

    if evidence_describes_current_non_epileptic_events(text):
        return "seizure free for multiple year"

    upper_bound = re.search(
        rf"(?:≤|<=|up to|at most|no more than)\s+(?P<count>{count})\s+"
        rf"(?:seizures?\s+)?per\s+(?P<unit>{unit})s?\b",
        text,
    )
    if upper_bound:
        return _format_prediction_rate(upper_bound.group("count"), upper_bound.group("unit"))
    upper_bound_in_weeks = re.search(
        rf"(?:≤|<=|up to|at most|no more than)\s+(?P<count>{count})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"\bin\s+(?:bad\s+|flare\s+)?weeks?\b",
        text,
    )
    if upper_bound_in_weeks:
        return _format_prediction_rate(upper_bound_in_weeks.group("count"), "week")

    if re.search(r"\bbimonthly\b", text):
        return _format_prediction_rate("1 per 2", "month")
    every_other = re.search(rf"\bevery\s+other\s+(?P<unit>{unit})\b", text)
    if every_other:
        return _format_prediction_rate("1 per 2", every_other.group("unit"))
    no_definite_recent = re.search(
        r"\bno\s+definite\s+epileptic\s+events?\b.*\b(?:past|last|this)\s+"
        rf"(?:(?P<count>\d+)\s+)?(?P<unit>{unit})s?\b",
        text,
    )
    if no_definite_recent:
        count_text = no_definite_recent.group("count") or "multiple"
        return f"seizure free for {count_text} {no_definite_recent.group('unit')}"

    days_per_week = re.search(
        rf"\b(?:occurring|occur|events?|seizures?|spells?)\b.{0,60}"
        rf"\b(?:on\s+)?(?P<count>{count})\s+days?\s+of\s+the\s+week\b",
        text,
    )
    if not days_per_week:
        days_per_week = re.search(
            rf"\b(?P<count>{count})\s+days?\s+per\s+week\b",
            text,
        )
    if days_per_week:
        return _format_prediction_rate(days_per_week.group("count"), "week")

    cluster_label = _cluster_label_from_selected_evidence(text)
    if cluster_label:
        return cluster_label
    if re.search(r"\bclusters?\b", text):
        return None

    yesterday = re.search(
        r"\b\d+\s+(?!(?:day|week|month|year)s?\b)"
        r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|attack|convulsion|spasm|mal|event)).*\byesterday\b",
        text,
    )
    if yesterday:
        return _format_prediction_rate("1", "day")

    compact_daily = re.search(r"\b1\s*/\s*d\b", text)
    if compact_daily:
        return _format_prediction_rate("1", "day")

    range_count = _range_count_over_window(text)
    if range_count:
        return range_count

    summed = _sum_counts_over_window(text)
    if summed:
        return summed

    single_count = _single_count_over_window(text)
    if single_count:
        return single_count

    slash_week = re.search(
        r"\b(?P<count>\d+)\s*/\s*7\b",
        text,
    )
    if slash_week:
        return _format_prediction_rate(slash_week.group("count"), "week")
    slash_month = re.search(
        r"\b(?P<count>\d+)\s*/\s*30\b.*\b(?:this|past|last)\s+month\b",
        text,
    )
    if slash_month:
        return _format_prediction_rate(slash_month.group("count"), "month")
    fortnight = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:over|in|during|for)?\s*(?:the\s+)?(?:past|last)\s+fortnight\b",
        text,
    )
    if not fortnight:
        fortnight = re.search(
            r"\b(?:past|last)\s+fortnight\b.*?"
            rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
            r"(?:seizure|attack|convulsion|spasm|event|episode)",
            text,
        )
    if fortnight:
        return _format_prediction_rate(f"{fortnight.group('count')} per 2", "week")

    monthly_shorthand = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+\s+){{0,4}}monthly\b",
        text,
    )
    if monthly_shorthand:
        return _format_prediction_rate(monthly_shorthand.group("count"), "month")

    single_last_period = re.search(
        rf"\b(?:single|1)\b.*\b(?:last|past)\s+(?P<unit>{unit})\b",
        text,
    )
    if single_last_period:
        return _format_prediction_rate("1", single_last_period.group("unit"))

    quarter = re.search(
        rf"\b(?P<count>{count})\s+(?:seizures?\s+)?per\s+quarter\b",
        text,
    )
    if quarter:
        return _format_prediction_rate(quarter.group("count"), "3 month")
    this_quarter = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:this|past|last)\s+quarter\b",
        text,
    )
    if this_quarter:
        return _format_prediction_rate(this_quarter.group("count"), "3 month")

    this_year = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,4}}"
        r"(?:this|past|last)\s+year\b",
        text,
    )
    if this_year:
        elapsed_months = _elapsed_months_in_year_context(context_text)
        if elapsed_months:
            return _format_prediction_rate(
                f"{this_year.group('count')} per {elapsed_months}",
                "month",
            )
        return _format_prediction_rate(this_year.group("count"), "year")
    year_to_date = re.search(
        rf"\b(?P<count>{count})\s+(?:[a-z]+(?:-[a-z]+)?\s+){{0,5}}"
        r"(?:so\s+far\s+this\s+year|this\s+year\s+to\s+date|"
        r"\d{4}\s+so\s+far)\b",
        text,
    )
    if year_to_date:
        elapsed_months = _elapsed_months_in_year_context(context_text)
        if elapsed_months:
            return _format_prediction_rate(
                f"{year_to_date.group('count')} per {elapsed_months}",
                "month",
            )
        return _format_prediction_rate(year_to_date.group("count"), "year")

    daily = _daily_label_from_selected_evidence(text)
    if daily:
        return daily

    times_every = re.search(
        rf"\b(?P<count>\d+)\s+(?:times|seizures?)?\s*every\s+"
        rf"(?P<period>\d+)\s+(?P<unit>{unit})s?\b",
        text,
    )
    if times_every:
        return _format_prediction_rate(
            f"{times_every.group('count')} per {times_every.group('period')}",
            times_every.group("unit"),
        )

    every_range = re.search(
        rf"\bevery\s+(?P<count>{count})\s+(?P<unit>{unit})s?\b",
        text,
    )
    if every_range:
        return _format_prediction_rate(
            f"1 per {every_range.group('count')}",
            every_range.group("unit"),
        )

    interval_range = re.search(
        rf"\bintervals?\s+ranging\s+(?P<count>{count})\s+"
        rf"(?P<unit>{unit})s?\b",
        text,
    )
    if interval_range:
        return _format_prediction_rate(
            f"1 per {interval_range.group('count')}",
            interval_range.group("unit"),
        )

    return None


def _should_prefer_selected_evidence_label(
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
    if _daily_label_from_selected_evidence(normalized_evidence) == evidence_label:
        return True
    if evidence_label == "1 per day" and re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\b(?:almost\s+)?daily\b",
        normalized_evidence,
    ):
        return True
    if " to " in evidence_label and " to " not in raw_repaired:
        return True
    if _sum_counts_over_window(normalized_evidence) == evidence_label:
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
    return not _raw_label_is_simple_rate(normalized_raw)


def _raw_label_is_simple_rate(normalized_raw: str) -> bool:
    return bool(
        re.match(
            r"^(?:multiple|\d+(?:\s*to\s*\d+)?)\s+per\s+"
            r"(?:(?:multiple|\d+(?:\s*to\s*\d+)?)\s+)?"
            r"(?:day|week|month|year)s?$",
            normalized_raw,
        )
    )


def _calendar_log_label_from_selected_evidence(text: str) -> str | None:
    entries = re.findall(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*x\s*(\d+)\b",
        text,
    )
    if len(entries) < 2:
        entries = re.findall(
            r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
            r"[a-z]*\s*:\s*(\d+)\s+days?\b",
            text,
        )
    if len(entries) < 2:
        return None
    return _format_prediction_rate(
        f"{sum(int(value) for value in entries)} per {len(entries)}",
        "month",
    )


def monthly_diary_label_from_text(text: str) -> str | None:
    """Sum source-near monthly diary counts from selected evidence or LLM events."""
    normalized = normalize_frequency_label(_once_twice_thrice(_words_to_numbers(text)))
    for parser in (
        _calendar_log_label_from_selected_evidence,
        _month_sleep_awake_log_label_from_selected_evidence,
        _general_monthly_diary_label_from_selected_evidence,
    ):
        label = parser(normalized)
        if label:
            return label
    return None


def _month_sleep_awake_log_label_from_selected_evidence(text: str) -> str | None:
    month_pattern = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
    count_pattern = r"\d+|no|zero|a|an"
    state_pattern = r"sleep|asleep|night|nocturnal|awake|waking|daytime|day"
    counts_by_month: dict[str, int] = {}
    for sentence in re.split(r"(?<=[.;])\s+", text):
        month_match = re.search(rf"\b(?P<month>{month_pattern})\b", sentence)
        if not month_match or not re.search(rf"\b(?:{state_pattern})\b", sentence):
            continue
        state_counts = []
        for match in re.finditer(
            rf"\b(?P<count>{count_pattern})\s+(?!in\s+)"
            rf"(?:\w+\s+){{0,3}}(?:{state_pattern})\b",
            sentence,
        ):
            count_value = _diary_count_value(match.group("count"))
            if count_value <= 100:
                state_counts.append(count_value)
        for match in re.finditer(
            rf"\b(?P<count>{count_pattern})\s+in\s+"
            rf"(?:{state_pattern})\b",
            sentence,
        ):
            count_value = _diary_count_value(match.group("count"))
            if count_value <= 100:
                state_counts.append(count_value)
        if state_counts:
            count_sum = sum(state_counts)
            if count_sum <= 100:
                counts_by_month.setdefault(month_match.group("month"), count_sum)
    counts = list(counts_by_month.values())
    if len(counts) < 2:
        return None
    return _format_prediction_rate(f"{sum(counts)} per {len(counts)}", "month")


def _general_monthly_diary_label_from_selected_evidence(text: str) -> str | None:
    month = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
    number = r"\d+|no|zero|a|an"
    month_counts: dict[str, int] = {}

    def add(month_key: str, count_text: str) -> None:
        count_value = _diary_count_value(count_text)
        if count_value > 100:
            return
        month_counts.setdefault(month_key, count_value)

    for match in re.finditer(
        rf"\b(?P<count>{number})\s+"
        r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        rf"(?:seizures?|events?|convulsions?)\s+(?:so\s+far\s+)?in\s+(?P<month>{month})\b",
        text,
    ):
        add(match.group("month"), match.group("count"))
    for match in re.finditer(
        rf"\b(?P<count>{number})\s+(?:were\s+)?in\s+(?P<month>{month})\b",
        text,
    ):
        add(match.group("month"), match.group("count"))
    for match in re.finditer(
        rf"\b(?P<count>{number})\s+in\s+(?P<month>{month})\b",
        text,
    ):
        add(match.group("month"), match.group("count"))
    for match in re.finditer(
        rf"\bin\s+(?P<month>{month})\b[^.;]*?\b(?:had|recorded|reports?)\s+"
        rf"(?P<count>{number})\b",
        text,
    ):
        add(match.group("month"), match.group("count"))
    this_month = re.search(
        rf"\b(?:this\s+month|as\s+of\s+this\s+month)\b[^.;]*?\b"
        rf"(?:had|has\s+had|reports?|recorded)?\s*(?P<count>{number})\s+"
        r"(?:seizures?|events?|convulsions?)\b",
        text,
    )
    if not this_month:
        this_month = re.search(
            rf"\b(?P<count>{number})\s+"
            r"(?:seizures?|events?|convulsions?)\s+(?:so\s+far\s+)?"
            r"(?:this\s+month|to\s+date\s+in\s+this\s+month)\b",
            text,
        )
    if this_month:
        add("this_month", this_month.group("count"))

    if len(month_counts) < 2:
        return None
    return _format_prediction_rate(
        f"{sum(month_counts.values())} per {len(month_counts)}",
        "month",
    )


def _diary_count_value(count_text: str) -> int:
    if count_text in {"a", "an"}:
        return 1
    return 0 if count_text in {"no", "zero"} else int(count_text)


def _q_interval_label_from_selected_evidence(text: str) -> str | None:
    interval = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
    interval_range = rf"{interval}(?:\s*(?:to|-|–|—)\s*{interval})?"
    match = re.search(
        rf"\bq\s*(?P<interval>{interval_range})\s*"
        r"(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
        text,
    )
    if not match:
        match = re.search(
            rf"\bq(?P<interval>{interval_range})\s*"
            r"(?P<unit>d|day|wk|week|mo|month|yr|year)\b",
            text,
        )
    if not match:
        return None
    unit = UNIT_SYNONYMS.get(match.group("unit"), match.group("unit"))
    return _format_prediction_rate(
        f"1 per {_words_to_numbers(match.group('interval'))}",
        unit,
    )


def _median_interval_label_from_selected_evidence(text: str) -> str | None:
    match = re.search(
        r"\bmedian inter-seizure interval\s*(?:≈|~|about|approximately|around)?\s*"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not match:
        return None
    return _format_prediction_rate(f"1 per {match.group('interval')}", match.group("unit"))


def _daily_label_from_selected_evidence(text: str) -> str | None:
    if re.search(r"\b(?:no|without)\b.{0,80}\b(?:events?|spells?|seizures?)\b", text):
        return None
    if re.search(r"\bdaily\s+(?:entries|diary|logs?)\b", text):
        return None
    if re.search(
        r"\b(?:dozens?|scores?)\b.{0,30}\b(?:in|per|each|a)\s+(?:day|24\s*hours?)\b",
        text,
    ):
        return "multiple per day"
    if re.search(
        r"\b(?:multiple|several|many|daily)\b.{0,40}"
        r"\b(?:events?|seizures?|spells?)\b",
        text,
    ):
        return "multiple per day"
    if re.search(r"\b(?:daily|every night|each night|nightly)\b", text):
        return _format_prediction_rate("1", "day")
    return None


def evidence_describes_current_non_epileptic_events(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:events?|episodes?|spells?|seizure-like episodes?)\b"
            r".{0,80}\b(?:currently|current|present|at present)\b"
            r".{0,80}\bnon-epileptic\b",
            text,
        )
        or re.search(
            r"\b(?:currently|current|present|at present)\b"
            r".{0,80}\bnon-epileptic\b"
            r".{0,80}\b(?:events?|episodes?|spells?|seizure-like episodes?)\b",
            text,
        )
    )


def _cluster_label_from_selected_evidence(text: str) -> str | None:
    if re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\b(?:almost\s+)?daily\b",
        text,
    ):
        return "1 per day"
    if re.search(
        r"\bclusters?\s+of\s+(?:jumps?|jerks?)\b.{0,40}\balmost\s+1\s+per\s+day\b",
        text,
    ):
        return "1 per day"

    recurrence_cluster = re.search(
        r"\b(?:go|remain|stretches?)\b.{0,50}"
        r"\b(?:nearly|almost|about|around|up to\s+)?"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\b.{0,80}"
        r"\b(?:when they recur|then)\b.{0,80}"
        r"\b(?P<per>\d+(?:\s*(?:to|-|–|—|and)\s*\d+)?)\b"
        r".{0,30}\b(?:one|1)\s+day\b",
        text,
    )
    if recurrence_cluster:
        per_cluster = re.sub(r"\s*(?:-|–|—|and)\s*", " to ", recurrence_cluster.group("per"))
        return (
            f"1 cluster per {recurrence_cluster.group('interval')} "
            f"{recurrence_cluster.group('unit')}, {per_cluster} per cluster"
        )
    recurrence_cluster_between = re.search(
        r"\b(?:go|remain|stretches?)\b.{0,50}"
        r"\b(?:nearly|almost|about|around|up to\s+)?"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\b.{0,120}"
        r"\b(?:between|often between)\s+"
        r"(?P<per>\d+(?:\s*(?:to|-|–|—|and)\s*\d+)?)\b",
        text,
    )
    if recurrence_cluster_between:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            recurrence_cluster_between.group("per"),
        )
        return (
            f"1 cluster per {recurrence_cluster_between.group('interval')} "
            f"{recurrence_cluster_between.group('unit')}, {per_cluster} per cluster"
        )

    seizure_free_cluster_day = re.search(
        r"\b(?:seizure-free|without\s+seizures?)\s+for\s+"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:consecutive\s+)?(?P<unit>day|week|month)s?\b.{0,120}"
        r"\b(?:followed\s+by|then)\s+(?:a\s+)?day\b.{0,100}"
        r"\b(?:multiple|several|batches?|clusters?|clustering)\b.{0,80}"
        r"\b(?:typically\s+)?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\b",
        text,
    )
    if seizure_free_cluster_day:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            seizure_free_cluster_day.group("per"),
        )
        return (
            f"1 cluster per {seizure_free_cluster_day.group('interval')} "
            f"{seizure_free_cluster_day.group('unit')}, {per_cluster} per cluster"
        )

    seizure_free_batch = re.search(
        r"\b(?:go|manage|remain)\b.{0,30}"
        r"(?P<interval>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month)s?\s+without\s+seizures?\b.{0,140}"
        r"\b(?:batches?|clusters?|clustering)\b.{0,80}?"
        r"\b(?:with\s+)?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\b"
        r".{0,40}\b(?:within\s+24\s+hours?|events?)\b",
        text,
    )
    if seizure_free_batch:
        per_cluster = re.sub(
            r"\s*(?:-|–|—|and)\s*",
            " to ",
            seizure_free_batch.group("per"),
        )
        return (
            f"1 cluster per {seizure_free_batch.group('interval')} "
            f"{seizure_free_batch.group('unit')}, {per_cluster} per cluster"
        )

    cluster_multiple_days = re.search(
        r"\b(?:past|last)\s+month\b.{0,120}\bclusters?\b.{0,80}"
        r"\b(?:on|over)\s+multiple\s+days?\b",
        text,
    )
    if cluster_multiple_days and _evidence_implies_multiple_per_cluster(text):
        return "multiple cluster per month, multiple per cluster"

    monthly_cluster = re.search(r"\bmonthly\s+clusters?\b", text)
    if monthly_cluster:
        per_cluster = re.search(
            r"\b(?P<count>\d+(?:\s*to\s*\d+)?)\s+"
            r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
            r"(?:seizure|absence|attack|convulsion|spasm|event|mal))",
            text[monthly_cluster.end() :],
        )
        if per_cluster:
            return f"1 cluster per month, {per_cluster.group('count')} per cluster"
        if _evidence_implies_multiple_per_cluster(text):
            return "1 cluster per month, multiple per cluster"

    monthly_burst = re.search(
        r"\b(?:clusters?|bursts?)\b.*\b(?:once\s+each|1\s+each|once\s+per|1\s+per)\s+month\b",
        text,
    )
    if monthly_burst and _evidence_implies_multiple_per_cluster(text):
        return "1 cluster per month, multiple per cluster"

    weekly_cluster = re.search(r"\bweekly\b.*\bclusters?\b", text)
    if weekly_cluster and _evidence_implies_multiple_per_cluster(text):
        return "1 cluster per week, multiple per cluster"
    cluster_weekly_per_cluster = re.search(
        r"\bclusters?\b.*\b(?:now\s+)?weekly\b.*?"
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:or\s+more\s+)?(?:events?|seizures?)?(?:\s+within\b.*)?"
        r"(?:per\s+cluster)?\b",
        text,
    )
    if cluster_weekly_per_cluster:
        return (
            "1 cluster per week, "
            f"{cluster_weekly_per_cluster.group('count')} per cluster"
        )
    weekly_cluster_count = re.search(
        r"\bweekly\b.*\bclusters?\b.*?"
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:or\s+more\s+)?(?:events?|seizures?)\b",
        text,
    )
    if weekly_cluster_count:
        return f"1 cluster per week, {weekly_cluster_count.group('count')} per cluster"

    cluster_days_month = re.search(
        r"\b(?:cluster\s+days?|clusters?)\s+"
        r"(?:(?P<count_word>twice)|(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?))\s+"
        r"this\s+month\b.*?"
        r"(?:sizes?\s+unrecorded|typically\s+(?P<per>\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?)"
        r"(?:\s+or\s+more)?\s+(?:seizures?|events?)\s+in\s+24\s*h)",
        text,
    )
    if cluster_days_month:
        count_text = (
            "2"
            if cluster_days_month.group("count_word")
            else cluster_days_month.group("count")
        )
        per_cluster = cluster_days_month.group("per") or "multiple"
        return f"{count_text} cluster per month, {per_cluster} per cluster"

    cluster_days_month_reversed = re.search(
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+cluster\s+days?\s+"
        r"this\s+month\b.*?(?:sizes?\s+unrecorded|typically\s+"
        r"(?P<per>\d+(?:\s*(?:to|-|–|—|or)\s*\d+)?)"
        r"(?:\s+or\s+more)?\s+(?:seizures?|events?)\s+in\s+24\s*h)",
        text,
    )
    if cluster_days_month_reversed:
        per_cluster = cluster_days_month_reversed.group("per") or "multiple"
        return (
            f"{cluster_days_month_reversed.group('count')} cluster per month, "
            f"{per_cluster} per cluster"
        )

    clusters_x_month = re.search(
        r"\bclusters?\s+(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s*×\s*/\s*month\b"
        r".*?(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+events?\b",
        text,
    )
    if clusters_x_month:
        return (
            f"{clusters_x_month.group('count')} cluster per month, "
            f"{clusters_x_month.group('per')} per cluster"
        )

    quarterly_cluster = re.search(
        r"\bquarterly\s+clusters?\b.*?\b(?P<per>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:convulsions?|seizures?|events?)\s+per\s+episode\b",
        text,
    )
    if quarterly_cluster:
        return f"1 cluster per 3 month, {quarterly_cluster.group('per')} per cluster"

    burst_monthly = re.search(
        r"\b(?:bursts?|clusters?)\b.*\b(?:around\s+the\s+beginning\s+of\s+most|"
        r"roughly\s+(?:once|1)\s+a|(?:once|1)\s+a|each)\s+month\b",
        text,
    )
    if burst_monthly:
        return "1 cluster per month, multiple per cluster"

    grouped_weekly = re.search(
        r"\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:nights?|mornings?|evenings?)\s+per\s+week\b.*\b"
        r"(?:several|multiple|grouped|clusters?|bursts?)\b",
        text,
    )
    if grouped_weekly:
        return (
            f"{grouped_weekly.group('count')} cluster per week, "
            "multiple per cluster"
        )

    several_per_fortnight = re.search(
        r"\bclusters?\s+arise\s+on\s+several\s+(?:evenings?|mornings?|days?)\s+"
        r"per\s+fortnight\b.*?\b(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?:spells?|seizures?|events?)\b",
        text,
    )
    if several_per_fortnight:
        return (
            "multiple cluster per 2 week, "
            f"{several_per_fortnight.group('count')} per cluster"
        )

    every_cluster = re.search(
        r"\b(?:clusters?|bursts?)\b.*\bevery\s+"
        r"(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+"
        r"(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if every_cluster:
        if _evidence_implies_multiple_per_cluster(text):
            return (
                f"1 cluster per {every_cluster.group('count')} "
                f"{every_cluster.group('unit')}, multiple per cluster"
            )
        return _format_prediction_rate(
            f"1 per {every_cluster.group('count')}",
            every_cluster.group("unit"),
        )

    cluster_match = re.search(
        r"\b(?:≈|~|about\s+|approximately\s+|around\s+)?"
        r"(?P<count>\d+(?:\s*(?:to|-|–|—)\s*\d+)?)\s+clusters?\s+"
        r"(?:(?:per|every)\s+(?:(?P<den>\d+)\s+)?(?P<unit>day|week|month|year)"
        r"|(?:this|past|last)\s+(?P<period>day|week|month|year|quarter))\b",
        text,
    )
    if not cluster_match:
        return None

    tail = text[cluster_match.end() :]
    per_cluster_match = re.search(
        r"\b(?:each|per\s+cluster|cluster(?:s)?\s+(?:with|of|having))\s+"
        r"(?:≈|~|about\s+|approximately\s+|around\s+)?(?P<count>\d+)\s+"
        r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|absence|attack|convulsion|spasm|event|mal))",
        tail,
    )
    denominator = cluster_match.group("den") or "1"
    unit = cluster_match.group("unit") or cluster_match.group("period")
    if unit == "quarter":
        denominator = "3"
        unit = "month"
    den_text = f"{denominator} " if denominator != "1" else ""
    if not per_cluster_match:
        return (
            f"{cluster_match.group('count')} cluster per {den_text}{unit}, "
            "multiple per cluster"
        )
    return (
        f"{cluster_match.group('count')} cluster per {den_text}{unit}, "
        f"{per_cluster_match.group('count')} per cluster"
    )


def _evidence_implies_multiple_per_cluster(text: str) -> bool:
    return bool(
        re.search(
            r"\b(?:several|multiple|bursts?|flurries|episodes?\s+over\s+"
            r"(?:a\s+)?few\s+days|over\s+(?:several|multiple)\s+days|"
            r"lasting\s+\d+\s*(?:to|-|–|—)\s*\d+\s+days|"
            r"number\s+per\s+cluster\s+not\s+documented|"
            r"imprecise\s+number\s+of\s+events\s+per\s+burst)\b",
            text,
        )
    )


def _sum_counts_over_window(text: str) -> str | None:
    window = re.search(
        r"\b(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)\s+"
        r"(?:(?P<count>\d+)\s+)?(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not window:
        return None

    prefix = text
    counts = [
        int(value)
        for value in re.findall(
            r"\b(\d+)\s+(?!(?:day|week|month|year)s?\b)"
            r"(?!(?:seizure[- ]free|free)\b)"
            r"(?=(?:tonic(?:-clonic)?|drop|absence|"
            r"(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
            r"(?:seizure|attack|convulsion|spasm|mal|event)))",
            prefix,
        )
    ]
    if not counts:
        return None

    denominator = window.group("count") or "1"
    unit = window.group("unit")
    return _format_prediction_rate(f"{sum(counts)} per {denominator}", unit)


def _range_count_over_window(text: str) -> str | None:
    window = re.search(
        r"\b(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)\s+"
        r"(?:(?P<count>\d+)\s+)?(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not window:
        return None

    range_match = re.search(
        r"\b(?P<low>\d+)\s*(?:to|-|–|—|or)\s*(?P<high>\d+)\s+"
        r"(?=(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|tonic))",
        text,
    )
    if not range_match:
        return None

    denominator = window.group("count") or "1"
    unit = window.group("unit")
    return _format_prediction_rate(
        f"{range_match.group('low')} to {range_match.group('high')} per {denominator}",
        unit,
    )


def _single_count_over_window(text: str) -> str | None:
    match = re.search(
        r"\b(?P<count>\d+)\s+(?:[a-z]+(?:-[a-z]+)?\s+){0,4}"
        r"(?:seizure|attack|convulsion|spasm|mal|event|episode)s?\s+"
        r"(?:in|over|during|for)\s+(?:the\s+)?(?:past|last)?\s*"
        r"(?P<denominator>\d+)\s+(?P<unit>day|week|month|year)s?\b",
        text,
    )
    if not match:
        return None
    return _format_prediction_rate(
        f"{match.group('count')} per {match.group('denominator')}",
        match.group("unit"),
    )


def _format_prediction_rate(count_text: str, unit_text: str) -> str:
    count = re.sub(r"\s*(?:-|–|—)\s*", " to ", count_text.strip())
    count = re.sub(r"\s+or\s+", " to ", count)
    count = re.sub(r"\s+", " ", count)
    unit = unit_text.rstrip("s").strip()
    if " per " in count:
        return f"{count} {unit}"
    return f"{count} per {unit}"


def _elapsed_months_in_year_context(context_text: str | None) -> int | None:
    if not context_text:
        return None
    text = normalize_frequency_label(context_text)
    month_names = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }
    month_pattern = "|".join(month_names)
    match = re.search(
        rf"\b(?:clinic\s+date|sent)\s*:\s*\d{{1,2}}\s+({month_pattern})\s+\d{{4}}\b",
        text,
    )
    if not match:
        return None
    return month_names[match.group(1)]


def _fallback_if_disallowed(text: str) -> str:
    return text if _is_allowed_prediction_format(text) else _fallback_prediction_repair(text)


def _final_allowed_format_repair(text: str) -> str:
    if _is_allowed_prediction_format(text):
        return text
    if text.startswith("seizure free"):
        if re.search(r"\b(month|year)\b", text) is None:
            return "seizure free for multiple year"
    elif "per " in text and not re.search(r"\b(day|week|month|year)\b", text):
        text = re.sub(r"per\s+\S+\b", "per month", text)
    if not _is_allowed_prediction_format(text):
        return "unknown"
    return text


BENCHMARK_REPAIR_STEPS = (
    BenchmarkRepairStep(
        rule_id="benchmark_repair.daypart_to_day",
        description="Map night/morning/afternoon/evening denominators to day.",
        apply=_daypart_to_day,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.unknown_no_reference",
        description="Normalize common unknown and no-reference prediction phrases.",
        apply=_normalize_unknown_no_reference,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.word_numbers",
        description="Convert number words used in labels to digits.",
        apply=_words_to_numbers,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.range_delimiters",
        description="Normalize hyphenated numeric ranges to 'to'.",
        apply=_normalize_ranges,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.once_twice_thrice",
        description="Convert once/twice/thrice to numeric counts.",
        apply=_once_twice_thrice,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.slash_per_forms",
        description="Convert slash-per shorthand into count per period labels.",
        apply=_slash_per_forms,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.x_times_forms",
        description="Convert x/times shorthand into count per period labels.",
        apply=_x_times_forms,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.drop_times_before_per",
        description="Drop redundant times tokens before per.",
        apply=_drop_times_before_per,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.every_each_forms",
        description="Convert every/each period phrasing into count per period labels.",
        apply=_every_each_forms,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.period_words",
        description="Convert daily/weekly/monthly/yearly period words into per labels.",
        apply=_period_words,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.inequality_to_multiple",
        description="Map inequality phrases to multiple when scorer format lacks bounds.",
        apply=_inequality_to_multiple,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.drop_prediction_noise",
        description="Drop approximate and seizure-word noise from prediction labels.",
        apply=_drop_prediction_noise,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_units_first",
        description="Normalize unit abbreviations and plurals.",
        apply=_normalize_units,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_whitespace_first",
        description="Normalize case, whitespace, and surrounding label text.",
        apply=normalize_frequency_label,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.reorder_period_then_count",
        description="Reorder period-then-count predictions into count-per-period labels.",
        apply=_reorder_period_then_count,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.canonicalize_seizure_free",
        description="Canonicalize seizure-free predictions into scorer-compatible labels.",
        apply=_canonicalize_seizure_free,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_units_after_seizure_free",
        description="Normalize units after seizure-free canonicalization.",
        apply=_normalize_units,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.fix_cluster_block",
        description="Repair cluster labels before final cluster normalization.",
        apply=_fix_cluster_block,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_units_after_cluster",
        description="Normalize units after cluster repair.",
        apply=_normalize_units,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.drop_per_one_first",
        description="Drop explicit per-one denominators.",
        apply=_drop_per_one,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.cleanup_commas_first",
        description="Clean comma spacing and normalize whitespace.",
        apply=_cleanup_commas,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.compress_double_per_range",
        description="Compress double per-period ranges with matching denominators.",
        apply=_compress_double_per_range,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_cluster_label",
        description="Normalize compact cluster-only labels.",
        apply=_normalize_cluster_label,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_cluster_label2",
        description="Normalize dual cluster and per-cluster labels.",
        apply=_normalize_cluster_label2,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.clean_prediction_extras",
        description="Drop trailing prediction extras that break scorer parsing.",
        apply=_clean_prediction_extras,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.zero_period_to_unknown",
        description="Map impossible zero-period denominators to unknown.",
        apply=_zero_period_to_unknown,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.fallback_if_disallowed",
        description="Apply fallback repair when the label is outside accepted formats.",
        apply=_fallback_if_disallowed,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.drop_per_one_final",
        description="Drop per-one denominators after fallback repair.",
        apply=_drop_per_one,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.cleanup_commas_final",
        description="Clean comma spacing after fallback repair.",
        apply=_cleanup_commas,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.final_allowed_format_repair",
        description="Final accepted-format guard before returning a prediction label.",
        apply=_final_allowed_format_repair,
    ),
)

FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS = (
    BenchmarkRepairStep(
        rule_id="benchmark_repair.daypart_to_day",
        description="Map night/morning/afternoon/evening denominators to day.",
        apply=_daypart_to_day,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.unknown_no_reference",
        description="Normalize explicit unknown and no-reference prediction phrases.",
        apply=_normalize_unknown_no_reference,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.word_numbers",
        description="Convert number words used in labels to digits.",
        apply=_words_to_numbers,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.range_delimiters",
        description="Normalize hyphenated numeric ranges to 'to'.",
        apply=_normalize_ranges,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.once_twice_thrice",
        description="Convert once/twice/thrice to numeric counts.",
        apply=_once_twice_thrice,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.slash_per_forms",
        description="Convert slash-per shorthand into count per period labels.",
        apply=_slash_per_forms,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.x_times_forms",
        description="Convert x/times shorthand into count per period labels.",
        apply=_x_times_forms,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.drop_times_before_per",
        description="Drop redundant times tokens before per.",
        apply=_drop_times_before_per,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.every_each_forms",
        description="Convert every/each period phrasing into count per period labels.",
        apply=_every_each_forms,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.period_words",
        description="Convert daily/weekly/monthly/yearly period words into per labels.",
        apply=_period_words,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.drop_prediction_format_noise",
        description="Drop event-word and approximation noise without vague remapping.",
        apply=_drop_prediction_format_noise,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_units_first",
        description="Normalize unit abbreviations and plurals.",
        apply=_normalize_units,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_whitespace_first",
        description="Normalize case, whitespace, and surrounding label text.",
        apply=normalize_frequency_label,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.reorder_period_then_count",
        description="Reorder period-then-count predictions into count-per-period labels.",
        apply=_reorder_period_then_count,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.canonicalize_seizure_free",
        description="Canonicalize seizure-free predictions into scorer-compatible labels.",
        apply=_canonicalize_seizure_free,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_units_after_seizure_free",
        description="Normalize units after seizure-free canonicalization.",
        apply=_normalize_units,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.fix_cluster_block",
        description="Repair cluster labels before final cluster normalization.",
        apply=_fix_cluster_block,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_units_after_cluster",
        description="Normalize units after cluster repair.",
        apply=_normalize_units,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.drop_per_one_first",
        description="Drop explicit per-one denominators.",
        apply=_drop_per_one,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.cleanup_commas_first",
        description="Clean comma spacing and normalize whitespace.",
        apply=_cleanup_commas,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.compress_double_per_range",
        description="Compress double per-period ranges with matching denominators.",
        apply=_compress_double_per_range,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_cluster_label",
        description="Normalize compact cluster-only labels.",
        apply=_normalize_cluster_label,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_cluster_label2",
        description="Normalize dual cluster and per-cluster labels.",
        apply=_normalize_cluster_label2,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.clean_prediction_extras",
        description="Drop trailing prediction extras that break scorer parsing.",
        apply=_clean_prediction_extras,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.drop_per_one_final",
        description="Drop per-one denominators after strict format repair.",
        apply=_drop_per_one,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.cleanup_commas_final",
        description="Clean comma spacing after strict format repair.",
        apply=_cleanup_commas,
    ),
)

BENCHMARK_REPAIR_RULES = tuple(
    benchmark_repair_rule(
        rule_id=step.rule_id,
        description=step.description,
        apply=step.apply,
    )
    for step in BENCHMARK_REPAIR_STEPS
)

FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES = tuple(
    benchmark_repair_rule(
        rule_id=step.rule_id,
        description=step.description,
        apply=step.apply,
    )
    for step in FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS
)
