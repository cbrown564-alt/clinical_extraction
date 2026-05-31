from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

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


def repair_prediction_label(raw: str | None) -> str:
    """Repair a free-form prediction into a Gan-compatible label string."""
    if raw is None:
        return "no seizure frequency reference"
    text = str(raw).strip().lower()
    if text == "":
        return "no seizure frequency reference"

    text = text.replace(" per night", " per day")
    text = text.replace(" per morning", " per day")
    text = text.replace(" per afternoon", " per day")
    text = text.replace(" per evening", " per day")
    text = _normalize_unknown_no_reference(text)

    text = _words_to_numbers(text)
    text = re.sub(r"(\d+)\s*[-–—]\s*(\d+)", r"\1 to \2", text)
    text = re.sub(r"\bonce\b", "1", text)
    text = re.sub(r"\btwice\b", "2", text)
    text = re.sub(r"\bthrice\b", "3", text)
    text = _slash_per_forms(text)
    text = _x_times_forms(text)
    text = re.sub(r"\btimes?\b(?=\s+per\b)", "", text)
    text = _every_each_forms(text)
    text = _period_words(text)
    text = _inequality_to_multiple(text)
    text = _drop_prediction_noise(text)
    text = _normalize_units(text)
    text = normalize_frequency_label(text)
    text = _reorder_period_then_count(text)
    text = _canonicalize_seizure_free(text)
    text = _normalize_units(text)
    text = _fix_cluster_block(text)
    text = _normalize_units(text)
    text = _drop_per_one(text)
    text = _cleanup_commas(text)
    text = _compress_double_per_range(text)
    text = _normalize_cluster_label(text)
    text = _normalize_cluster_label2(text)
    text = _clean_prediction_extras(text)

    if re.search(r"\bper\s+0\s+(day|week|month|year)\b", text):
        text = "unknown"

    if not _is_allowed_prediction_format(text):
        text = _fallback_prediction_repair(text)

    text = _drop_per_one(text)
    text = _cleanup_commas(text)

    if not _is_allowed_prediction_format(text):
        if text.startswith("seizure free"):
            if re.search(r"\b(month|year)\b", text) is None:
                return "seizure free for multiple year"
        elif "per " in text and not re.search(r"\b(day|week|month|year)\b", text):
            text = re.sub(r"per\s+\S+\b", "per month", text)
        if not _is_allowed_prediction_format(text):
            return "unknown"
    return text


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
    return "no seizure frequency reference"
