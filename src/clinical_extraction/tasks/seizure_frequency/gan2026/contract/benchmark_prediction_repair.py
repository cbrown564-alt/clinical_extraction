from __future__ import annotations

import re

from clinical_extraction.tasks.seizure_frequency.gan2026.contract import label_parser as _labels
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.gold_policy import (
    UNIT_SYNONYMS,
    _normalize_ranges,
    _words_to_numbers,
)
from clinical_extraction.tasks.shared.epilepsy.terms import MONTH_NAME_PATTERN

from ..deterministic.rules.benchmark_repair import (
    BenchmarkRepairStep,
    benchmark_repair_rule,
)

normalize_frequency_label = _labels.normalize_frequency_label
_parse_range = _labels._parse_range


ALLOWED_PREDICTION_PATTERNS = (
    re.compile(r"^unknown$"),
    re.compile(r"^no seizure frequency reference$"),
    re.compile(
        r"^seizure free for (?:multiple|\d+(?:\.\d+)?(?: to \d+(?:\.\d+)?)?) "
        r"(?:day|week|month|year)$"
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


def _underscore_label_separators(text: str) -> str:
    return re.sub(r"(?<=[a-z0-9])_(?=[a-z0-9])", " ", text)


def _normalize_units(text: str) -> str:
    unit_pattern = "|".join(map(re.escape, sorted(UNIT_SYNONYMS, key=len, reverse=True)))
    text = re.sub(rf"\b({unit_pattern})\b", lambda m: UNIT_SYNONYMS[m.group(0)], text)
    return re.sub(r"\b(day|week|month|year)s\b", r"\1", text)


def _slash_per_forms(text: str) -> str:
    unit_pattern = r"h|hr|hrs?|hour|d|day|wk|wks?|week|mo|mon|mos|mons?|month|yr|yrs?|y|year"

    def replace(match: re.Match[str]) -> str:
        unit = UNIT_SYNONYMS.get(match.group("unit"), match.group("unit"))
        return f"{match.group('num')} per {unit}"

    return re.sub(
        rf"(?P<num>\d+(?:\s*to\s*\d+)?)\s*/\s*(?P<unit>{unit_pattern})s?\b",
        replace,
        text,
    )


def _x_times_forms(text: str) -> str:
    unit_pattern = r"h|hr|hrs?|hour|d|day|wk|wks?|week|mo|mon|mos?|month|yr|yrs?|y|year"
    text = re.sub(
        rf"(\d+)\s*[x×]\s*/\s*({unit_pattern})s?\b",
        lambda match: f"{match.group(1)} per {UNIT_SYNONYMS.get(match.group(2), match.group(2))}",
        text,
    )
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
    text = re.sub(r"\b\d+\s+(?=every\s+other\s+(day|week|month|year|nights?)\b)", "", text)
    text = re.sub(
        r"\b\d+\s+(?=(?:every|each)\s+\d+(?:\s+to\s+\d+)?\s*(day|week|month|year)s?\b)",
        "",
        text,
    )
    text = re.sub(r"\b(?:every|each)\s+other\s+(day|week|month|year)\b", r"1 per 2 \1", text)
    text = re.sub(r"\b(?:every|each)\s+other\s+nights?\b", "1 per 2 day", text)
    text = re.sub(
        r"\b(?:every|each)\s+(\d+)\s+to\s+(\d+)\s*(day|week|month|year)s?\b",
        r"1 per \1 to \2 \3",
        text,
    )
    text = re.sub(r"\b(?:every|each)\s+(\d+)\s*(day|week|month|year)s?\b", r"1 per \1 \2", text)
    text = re.sub(r"\b(?:every|each)\s+(day|week|month|year)s?\b", r"1 per \1", text)
    text = re.sub(r"\b(?:every|each)\s+nights?\b", "1 per day", text)
    text = re.sub(r"\b(?:every|each)\s+(?:morning|afternoon|evening)s?\b", "1 per day", text)
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
    text = re.sub(
        r"(\d+(?:\s*to\s*\d+)?|\bmultiple\b)?\s*\bnightly\b",
        lambda match: (match.group(1) or "1") + " per day",
        text,
    )
    text = re.sub(r"\b(?:annually|yearly)\b", "1 per year", text)
    text = re.sub(r"\bsemiweekly\b", "2 per week", text)
    text = re.sub(r"\bbiweekly\b", "1 per 2 week", text)
    text = re.sub(r"\bfortnightly\b", "1 per 2 week", text)
    text = re.sub(
        r"(\d+(?:\s*to\s*\d+)?|\bmultiple\b)?\s*\bquarterly\b",
        lambda match: (match.group(1) or "1") + " per 3 month",
        text,
    )
    text = re.sub(r"\bsemimonthly\b", "2 per month", text)
    return re.sub(r"\bbimonthly\b", "1 per 2 month", text)


def _strip_upper_bound_qualifier(text: str) -> str:
    text = re.sub(
        r"^(?:<=|\u2264|up to|at most|no more than)\s+"
        r"(?=\d+(?:\s*to\s*\d+)?\s+per\s+)",
        "",
        text,
    )
    return re.sub(
        r"\b(day|week|month|year)\s+or\s+less$",
        r"\1",
        text,
    )


def _normalize_quarter_period(text: str) -> str:
    return re.sub(r"\bper\s+quarter\b", "per 3 month", text)


def _seizure_days_to_rate(text: str) -> str:
    """Project diary-style day counts onto the already stated period."""

    def replace(match: re.Match[str]) -> str:
        denominator = (match.group("den") or "").strip()
        unit = match.group("unit")
        den_text = f"{denominator} " if denominator and denominator != "1" else ""
        return f"{match.group('count')} per {den_text}{unit}"

    return re.sub(
        r"\b(?P<count>\d+(?:\s*to\s*\d+)?|multiple)\s+"
        r"(?:seizure[-\s]+)?days?\s+per\s+"
        r"(?P<den>(?:\d+(?:\s*to\s*\d+)?\s+)?)(?P<unit>week|month|year)\b",
        replace,
        text,
    )


def _inequality_to_multiple(text: str) -> str:
    text = re.sub(
        r"^(?:<=|\u2264|up to|at most|no more than)\s+"
        r"(?=\d+(?:\s*to\s*\d+)?\s+per\s+)",
        "",
        text,
    )
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


def _many_to_multiple(text: str) -> str:
    return re.sub(r"\bmany\b", "multiple", text)


def _hourly_to_multiple_per_day(text: str) -> str:
    return re.sub(
        r"\b(?:\d+(?:\s*to\s*\d+)?|multiple)\s+per\s+(?:h|hr|hour)\b",
        "multiple per day",
        text,
    )


def _vague_frequency_to_multiple(text: str) -> str:
    text = re.sub(
        r"\bmost\s+nights?(?:\s+of\s+the\s+week)?\b",
        "multiple per week",
        text,
    )
    text = re.sub(r"\bmost\s+days\b", "multiple per week", text)
    text = re.sub(r"\bmost\s+shifts\b", "multiple per week", text)
    text = re.sub(r"\brare\b(?!\s+per\b)", "multiple per year", text)
    text = re.sub(r"\boccasional\b(?!\s+per\b)", "multiple per month", text)
    text = re.sub(r"\bfrequent\b(?!\s+per\b)", "multiple per day", text)
    text = re.sub(r"\brare\s+per\s+unspecified\s+time\b", "multiple per year", text)
    text = re.sub(
        r"\boccasional\s+per\s+unspecified\s+time\b",
        "multiple per month",
        text,
    )
    text = re.sub(r"\bfrequent\s+per\s+unspecified\s+time\b", "multiple per day", text)
    text = re.sub(r"\brare\s+per\s+", "multiple per ", text)
    text = re.sub(r"\boccasional\s+per\s+", "multiple per ", text)
    return re.sub(r"\bfrequent\s+per\s+", "multiple per ", text)


def _drop_prediction_noise(text: str) -> str:
    text = re.sub(
        r"\b(?:approximately|approx\.?|about|around|nearly|roughly|typically|circa|~)\b",
        "",
        text,
    )
    text = re.sub(r"\b(?:a few|few|several)\b", "multiple", text)
    text = re.sub(r"\ba couple of\b", "2", text)
    return _drop_prediction_format_noise(text)


def _drop_prediction_format_noise(text: str) -> str:
    normalized = normalize_frequency_label(text)
    if normalized in {"unknown", "no seizure frequency reference"}:
        return normalized
    text = re.sub(
        r"\b(?:approximately|approx\.?|about|around|nearly|roughly|typically|circa|~)\b",
        "",
        text,
    )
    text = re.sub(r"\bseizures?\b(?!\s*[- ]?free)", "", text)
    text = re.sub(
        r"\b(?:episodes?|events?|attacks?|spells?|szs?|absences?|"
        r"myoclonic|jerks?|automatisms?|convulsions?)\b",
        "",
        text,
    )
    text = re.sub(r"\b(?:of|the|a|an|such|focal|clinically|suspected)\b", "", text)
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
        r"(\d+(?:\.\d+)?(?:\s*to\s*\d+(?:\.\d+)?)?|multiple)\s*(day|week|month|year)s?\b",
        text,
    )
    if match:
        return f"seizure free for {match.group(1)} {match.group(2)}"
    if re.search(r"\b(year|years)\b", text):
        return "seizure free for multiple year"
    if re.search(rf"\b(months?|{MONTH_NAME_PATTERN})\b", text):
        return "seizure free for multiple month"
    if re.search(r"\b(week|weeks)\b", text):
        return "seizure free for multiple week"
    if re.search(r"\b(day|days)\b", text):
        return "seizure free for multiple day"
    if re.search(r"seizure free since\b", text):
        return "seizure free for multiple month"
    return "seizure free for multiple year"



def _fix_cluster_block(text: str) -> str:
    if "cluster" not in text:
        return text
    text = re.sub(r"\bclustered\b", "", text).strip()
    if "cluster" not in text:
        return normalize_frequency_label(text)
    text = re.sub(r"\bclusters\b", "cluster", text)
    text = re.sub(
        r"\b(?P<count>\d+(?:\s*to\s*\d+)?|multiple)\s+per\s+"
        r"(?P<window>(?:\d+(?:\s*to\s*\d+)?\s+)?(?:day|week|month|year))\s+"
        r"cluster\s+of\s+(?P<burden>\d+(?:\s*to\s*\d+)?|multiple)"
        r"(?:\s+(?:absences?|seizures?|events?|episodes?))?\b",
        r"\g<count> cluster per \g<window>, \g<burden> per cluster",
        text,
    )
    text = re.sub(
        r"\b(?P<count>\d+(?:\s*to\s*\d+)?|multiple)\s+per\s+"
        r"(?P<window>(?:\d+(?:\s*to\s*\d+)?\s+)?(?:day|week|month|year))\s+"
        r"cluster\s+(?P<burden>\d+(?:\s*to\s*\d+)?|multiple)\b",
        r"\g<count> cluster per \g<window>, \g<burden> per cluster",
        text,
    )
    text = re.sub(
        r"\b(\d+(?:\s*to\s*\d+)?|multiple)\s+"
        r"(?:absences?|seizures?|events?|episodes?)\s+per\s+cluster\b",
        r"\1 per cluster",
        text,
    )
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
        cadence = re.search(
            r"\b((?P<count>\d+(?:\s*to\s*\d+)?|multiple)\s+cluster\s+per\s+"
            r"(?:\d+(?:\s*to\s*\d+)?\s+)?(?:day|week|month|year))\b",
            text,
        )
        if cadence:
            # Singleton cadence-only clusters often mark uncertain burden and
            # should stay unknown; 2+/multiple keep dual form for scoring.
            count_text = cadence.group("count")
            if count_text == "1":
                return "unknown"
            return f"{cadence.group(1)}, multiple per cluster"
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
            den_text = f"{denominator} " if denominator and denominator != "1" else ""
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
        den_text = f"{denominator} " if denominator and denominator != "1" else ""
        return f"{match.group('num')} per {den_text}{unit}"

    leftover_rate = re.search(
        r"(?P<num>(?:\d+(?:\s*to\s*\d+)?|multiple))\s+"
        r"(?P<leftover>(?:[a-z]+(?:-[a-z]+)?\s+){1,8})"
        r"per\s+(?P<den>(?:\d+(?:\s*to\s*\d+)?\s*)?)"
        r"(?P<unit>day|week|month|year)",
        text,
    )
    if leftover_rate and not re.search(r"\b(?:day|night)s?\b", leftover_rate.group("leftover")):
        denominator = (leftover_rate.group("den") or "").strip()
        unit = leftover_rate.group("unit")
        den_text = f"{denominator} " if denominator and denominator != "1" else ""
        return f"{leftover_rate.group('num')} per {den_text}{unit}"

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
    if re.search(r"\b(?:seizure|attack|convulsion|spasm|event|absence|tonic)\b", text):
        return "unknown"
    return "no seizure frequency reference"


def _daypart_to_day(text: str) -> str:
    text = text.replace(" per night", " per day")
    text = text.replace(" per morning", " per day")
    text = text.replace(" per afternoon", " per day")
    return text.replace(" per evening", " per day")


def _normalize_or_count_ranges(text: str) -> str:
    """Project countable ``N or M per ...`` ranges to ``N to M per ...``.

    Benchmark-format projection: preserves both endpoints already present in the
    selected label instead of collapsing through fallback to one end.
    """
    text = re.sub(
        r"\b(?:every|each)\s+(?P<low>\d+(?:\.\d+)?)\s+or\s+(?P<high>\d+(?:\.\d+)?)\s+"
        r"(?P<unit>day|week|month|year)s?\b",
        r"every \g<low> to \g<high> \g<unit>",
        text,
    )
    text = re.sub(
        r"\b(?P<low>\d+(?:\.\d+)?)\s+or\s+(?P<high>\d+(?:\.\d+)?)\s+"
        r"(?P<article>per|a)\s+(?P<unit>day|week|month|year)s?\b",
        r"\g<low> to \g<high> per \g<unit>",
        text,
    )
    return re.sub(
        r"\b(?P<low>\d+(?:\.\d+)?)\s+or\s+(?P<high>\d+(?:\.\d+)?)\s+(?=per\b)",
        r"\g<low> to \g<high> ",
        text,
    )


def _in_period_count_to_per(text: str) -> str:
    """Project ``N in/within M months`` observation counts to ``N per M month``."""
    return re.sub(
        r"\b(?P<count>\d+(?:\s*to\s*\d+)?|multiple)\s+"
        r"(?:(?:seizures?|events?|episodes?|attacks?|convulsions?)\s+)?"
        r"(?:in|within)\s+(?:the\s+)?(?:past\s+|last\s+)?"
        r"(?P<den>\d+(?:\s*to\s*\d+)?)\s+(?P<unit>day|week|month|year)s?\b",
        r"\g<count> per \g<den> \g<unit>",
        text,
    )


def _cluster_over_in_window(text: str) -> str:
    """Project ``N clusters over/in M weeks`` before inequality remaps ``over``."""
    has_per_cluster = bool(re.search(r"\bper\s+cluster\b", text))

    def _replace(match: re.Match[str]) -> str:
        count = match.group("count")
        den = match.group("den")
        unit = match.group("unit")
        unit = re.sub(r"s$", "", unit)
        cadence = f"{count} cluster per {den} {unit}"
        if count == "1" or has_per_cluster:
            return cadence
        return f"{cadence}, multiple per cluster"

    return re.sub(
        r"\b(?P<count>\d+(?:\s*to\s*\d+)?|multiple)\s+clusters?\s+"
        r"(?:over|in)\s+(?:the\s+)?(?:past\s+|last\s+)?"
        r"(?P<den>\d+(?:\s*to\s*\d+)?)\s+(?P<unit>days?|weeks?|months?|years?)\b",
        _replace,
        text,
    )


def _once_twice_thrice(text: str) -> str:
    text = re.sub(
        r"\bonce\s+or\s+twice\s+a\s+(day|week|month|year)s?\b",
        r"1 to 2 per \1",
        text,
    )
    text = re.sub(r"\bonce\b", "1", text)
    text = re.sub(r"\btwice\b", "2", text)
    return re.sub(r"\bthrice\b", "3", text)


def _drop_times_before_per(text: str) -> str:
    return re.sub(r"\btimes?\b(?=\s+per\b)", "", text)


def _zero_period_to_unknown(text: str) -> str:
    if re.search(r"\bper\s+0\s+(day|week|month|year)\b", text):
        return "unknown"
    return text


def _fallback_if_disallowed(text: str) -> str:
    return text if _is_allowed_prediction_format(text) else _fallback_prediction_repair(text)


def _final_allowed_format_repair(text: str) -> str:
    if _is_allowed_prediction_format(text):
        return text
    if text.startswith("seizure free"):
        if re.search(r"\b(day|week|month|year)\b", text) is None:
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
        rule_id="benchmark_repair.underscore_label_separators",
        description="Convert underscore-separated model labels into ordinary label tokens.",
        apply=_underscore_label_separators,
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
        rule_id="benchmark_repair.or_count_ranges",
        description="Project countable N or M per-period ranges to N to M.",
        apply=_normalize_or_count_ranges,
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
        description="Convert daily/nightly/weekly/monthly/yearly period words into per labels.",
        apply=_period_words,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_quarter_period",
        description="Convert quarter denominators to the Gan-compatible 3 month window.",
        apply=_normalize_quarter_period,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.seizure_days_to_rate",
        description="Project seizure-day counts per period into count-per-period labels.",
        apply=_seizure_days_to_rate,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.cluster_over_in_window",
        description=(
            "Project cluster counts over or in a stated window into cadence-only "
            "cluster labels before inequality remapping."
        ),
        apply=_cluster_over_in_window,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.inequality_to_multiple",
        description="Map inequality phrases to multiple when scorer format lacks bounds.",
        apply=_inequality_to_multiple,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.many_to_multiple",
        description="Map many as a vague count synonym to the accepted multiple token.",
        apply=_many_to_multiple,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.hourly_to_multiple_per_day",
        description="Map any per-hour seizure frequency to multiple per day.",
        apply=_hourly_to_multiple_per_day,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.vague_frequency_to_multiple",
        description="Preserve vague frequency words as unresolved multiple labels.",
        apply=_vague_frequency_to_multiple,
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
        rule_id="benchmark_repair.in_period_count_to_per",
        description="Project N in/within M period observation counts to N per M period.",
        apply=_in_period_count_to_per,
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
        rule_id="benchmark_repair.underscore_label_separators",
        description="Convert underscore-separated model labels into ordinary label tokens.",
        apply=_underscore_label_separators,
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
        rule_id="benchmark_repair.or_count_ranges",
        description="Project countable N or M per-period ranges to N to M.",
        apply=_normalize_or_count_ranges,
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
        description="Convert daily/nightly/weekly/monthly/yearly period words into per labels.",
        apply=_period_words,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.strip_upper_bound_qualifier",
        description="Drop explicit upper-bound qualifiers from otherwise parser-compatible rates.",
        apply=_strip_upper_bound_qualifier,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.normalize_quarter_period",
        description="Convert quarter denominators to the Gan-compatible 3 month window.",
        apply=_normalize_quarter_period,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.seizure_days_to_rate",
        description="Project seizure-day counts per period into count-per-period labels.",
        apply=_seizure_days_to_rate,
    ),
    BenchmarkRepairStep(
        rule_id="benchmark_repair.many_to_multiple",
        description="Map many as a vague count synonym to the accepted multiple token.",
        apply=_many_to_multiple,
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
