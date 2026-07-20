"""Temporal anchor and date parsing for assessment assembly."""

from __future__ import annotations

import re
from collections.abc import Sequence
from datetime import date
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.clinical_assessment import (
    DateReference,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.assessment.common import (
    _clean_phrase,
    _multi_month_bucket_count_to_float,
    _small_number_to_float,
)


def _extract_frequency_multi_month_bucket_matches(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> list[dict[str, Any]]:
    count_token = r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"
    month_token = (
        r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?"
    )
    pattern = re.compile(
        rf"\b(?P<low>{count_token})"
        rf"(?:\s+to\s+(?P<high>{count_token}))?"
        r"(?:\s+[A-Za-z][A-Za-z-]*){0,6}?"
        r"\s+(?:in|during|throughout)\s+"
        rf"(?P<month>{month_token})(?:\s+(?P<year>\d{{4}}))?\b",
        flags=re.IGNORECASE,
    )
    matches: list[dict[str, Any]] = []
    seen: set[tuple[str, float, float]] = set()
    for match in pattern.finditer(source_phrase):
        count_low = _small_number_to_float(match.group("low"))
        count_high = _small_number_to_float(match.group("high") or match.group("low"))
        if count_low is None or count_high is None:
            continue
        month_iso, year_inferred = _month_token_to_iso(
            match.group("month"),
            year=match.group("year"),
            reference_date=reference_date,
        )
        if month_iso is None:
            continue
        key = (month_iso, count_low, count_high)
        if key in seen:
            continue
        seen.add(key)
        matches.append(
            {
                "count_low": count_low,
                "count_high": count_high,
                "month_iso": month_iso,
                "year_inferred": year_inferred,
            }
        )
    return matches


def _extract_frequency_current_month_bucket_match(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> dict[str, Any] | None:
    month_iso = _reference_month_iso(reference_date)
    if month_iso is None:
        return None
    count_token = (
        r"\d+|no|zero|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve"
    )
    event_token = r"seizures?|events?|episodes?|absences?|spasms?|attacks?|jerks?"
    patterns = [
        re.compile(
            rf"\b(?P<count>{count_token})\s+(?:\w+\s+){{0,3}}?(?:{event_token})\s+"
            r"so\s+far\s+this\s+month\b",
            flags=re.IGNORECASE,
        ),
        re.compile(
            rf"\bthis\s+month\s+so\s+far\b(?:\s+\w+){{0,6}}?\s+(?P<count>{count_token})\s+"
            rf"(?:\w+\s+){{0,3}}?(?:{event_token})\b",
            flags=re.IGNORECASE,
        ),
    ]
    for pattern in patterns:
        match = pattern.search(source_phrase)
        if match is None:
            continue
        count_value = match.groupdict().get("count")
        if not count_value:
            continue
        count = _multi_month_bucket_count_to_float(count_value)
        if count is None:
            continue
        return {
            "count_low": count,
            "count_high": count,
            "month_iso": month_iso,
            "year_inferred": False,
        }
    return None


def _extract_frequency_article_month_bucket_matches(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> list[dict[str, Any]]:
    month_token = (
        r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?"
    )
    event_token = r"seizures?|events?|episodes?|absences?|spasms?|attacks?|jerks?"
    pattern = re.compile(
        rf"\b(?:a|an|another)\s+(?:[A-Za-z][A-Za-z-]*\s+){{0,3}}?"
        rf"(?P<event>(?:{event_token}))\s+(?:in|during|throughout)\s+"
        rf"(?P<month>{month_token})(?:\s+(?P<year>\d{{4}}))?\b",
        flags=re.IGNORECASE,
    )
    matches: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in pattern.finditer(source_phrase):
        month_iso, year_inferred = _month_token_to_iso(
            match.group("month"),
            year=match.group("year"),
            reference_date=reference_date,
        )
        if month_iso is None or month_iso in seen:
            continue
        seen.add(month_iso)
        matches.append(
            {
                "count_low": 1.0,
                "count_high": 1.0,
                "month_iso": month_iso,
                "year_inferred": year_inferred,
            }
        )
    return matches


def _extract_frequency_summary_count_with_month_list(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> tuple[float, float, bool] | None:
    explicit_window = _extract_explicit_multi_month_window_months(source_phrase)
    month_mentions = _extract_month_mentions(source_phrase, reference_date=reference_date)
    if explicit_window is None or len(month_mentions) < 2:
        return None
    count_match = re.search(
        r"\b(?P<low>\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve)"
        r"(?:\s+to\s+(?P<high>\d+|one|two|three|four|five|six|seven|eight|"
        r"nine|ten|eleven|twelve))?"
        r"(?:\s+\w+){0,4}\s+"
        r"(?:jerks?|seizures?|events?|episodes?|absences?|spasms?)\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if count_match is None:
        return None
    count_low = _small_number_to_float(count_match.group("low"))
    count_high = _small_number_to_float(count_match.group("high") or count_match.group("low"))
    if count_low is None or count_high is None:
        return None
    inferred_year = any(mention["year_inferred"] for mention in month_mentions)
    return count_low, count_high, inferred_year


def _extract_explicit_multi_month_window_months(source_phrase: str) -> int | None:
    match = re.search(
        r"\b(?:over|during|across|within)\s+(?:the\s+past\s+|past\s+|last\s+)?"
        r"(?P<count>\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve)\s+months?\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    count = _small_number_to_float(match.group("count"))
    if count is None or count <= 1:
        return None
    return int(count)


def _extract_month_mentions(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> list[dict[str, Any]]:
    month_token = (
        r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t|tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?"
    )
    pattern = re.compile(
        rf"\b(?P<month>{month_token})(?:\s+(?P<year>\d{{4}}))?\b",
        flags=re.IGNORECASE,
    )
    mentions: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in pattern.finditer(source_phrase):
        month_iso, year_inferred = _month_token_to_iso(
            match.group("month"),
            year=match.group("year"),
            reference_date=reference_date,
        )
        if month_iso is None or month_iso in seen:
            continue
        seen.add(month_iso)
        mentions.append(
            {
                "month_iso": month_iso,
                "year_inferred": year_inferred,
            }
        )
    return mentions


def _month_token_to_iso(
    month: str,
    *,
    year: str | None,
    reference_date: str | None,
) -> tuple[str | None, bool]:
    if year:
        return _month_year_to_iso(month, year), False
    if reference_date is None:
        return None, False
    return _month_without_year_to_iso(month, reference_date=reference_date), True


def _reference_month_iso(reference_date: str | None) -> str | None:
    if reference_date is None:
        return None
    parts = reference_date.split("-")
    if len(parts) < 2:
        return None
    try:
        year = int(parts[0])
        month = int(parts[1])
    except ValueError:
        return None
    if month < 1 or month > 12:
        return None
    return f"{year:04d}-{month:02d}"


def _inclusive_month_span(month_isos: Sequence[str]) -> int | None:
    if not month_isos:
        return None
    parsed: list[tuple[int, int]] = []
    for month_iso in month_isos:
        parts = month_iso.split("-")
        try:
            parsed.append((int(parts[0]), int(parts[1])))
        except (IndexError, ValueError):
            return None
    start_year, start_month = min(parsed)
    end_year, end_month = max(parsed)
    return (end_year - start_year) * 12 + (end_month - start_month) + 1


def _extract_frequency_anchor_window_date(
    source_phrase: str,
    *,
    reference_date: str,
) -> tuple[str | None, list[str], bool]:
    last_event_month_year = re.search(
        r"\bsince\s+last\s+[^.]{0,40}?\bseizure\s+in\s+"
        r"(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if last_event_month_year is not None:
        parsed = _month_year_to_iso(
            last_event_month_year.group("month"),
            last_event_month_year.group("year"),
        )
        if parsed is not None:
            return parsed, ["frequency_rate_anchor_from_last_event_phrase"], True
    since_month_year = re.search(
        r"\bsince\s+(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if since_month_year is not None:
        parsed = _month_year_to_iso(
            since_month_year.group("month"),
            since_month_year.group("year"),
        )
        if parsed is not None:
            return parsed, [], True
    since_numeric_month_year = re.search(
        r"\bsince\s+(?P<month>\d{1,2})\s*(?:/|-)\s*(?P<year>\d{4})\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if since_numeric_month_year is not None:
        parsed = _numeric_month_year_to_iso(
            since_numeric_month_year.group("month"),
            since_numeric_month_year.group("year"),
        )
        if parsed is not None:
            return parsed, [], True
    last_event_month_without_year = re.search(
        r"\bsince\s+last\s+[^.]{0,40}?\bseizure\s+in\s+(?P<month>[A-Za-z]+)\b",
        source_phrase,
        flags=re.IGNORECASE,
    )
    if last_event_month_without_year is not None:
        parsed = _month_without_year_to_iso(
            last_event_month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            return (
                parsed,
                [
                    "frequency_rate_anchor_year_inferred_from_reference_date",
                    "frequency_rate_anchor_from_last_event_phrase",
                ],
                True,
            )
    return None, [], False


def _extract_seizure_free_anchor_date(
    source_phrase: str,
    *,
    reference_date: str | None,
) -> tuple[DateReference | None, list[str]]:
    normalized = _clean_phrase(source_phrase)
    day_numeric = re.search(
        r"\bsince\s+(?P<day>\d{1,2})[/-](?P<month>\d{1,2})[/-](?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_numeric is not None:
        parsed = _numeric_day_month_year_to_iso(
            day_numeric.group("day"),
            day_numeric.group("month"),
            day_numeric.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="day",
                source="seizure_free_source_phrase",
                source_phrase=day_numeric.group(0),
            ), []
    day_named = re.search(
        r"\bsince\s+(?P<day>\d{1,2})(?:\s+|-)"
        r"(?P<month>[A-Za-z]+)(?:\s+|-)(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_named is not None:
        parsed = _day_month_year_to_iso(
            day_named.group("day"),
            day_named.group("month"),
            day_named.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="day",
                source="seizure_free_source_phrase",
                source_phrase=day_named.group(0),
            ), []
    event_day_named = re.search(
        r"\b(?:last event on|last seizure on|last reported event was on|"
        r"last such episode occurred on|most recent episode was on)\s+"
        r"(?P<day>\d{1,2})(?:\s+|-)(?P<month>[A-Za-z]+)(?:\s+|-)"
        r"(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if event_day_named is not None:
        parsed = _day_month_year_to_iso(
            event_day_named.group("day"),
            event_day_named.group("month"),
            event_day_named.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="day",
                source="seizure_free_source_phrase",
                source_phrase=event_day_named.group(0),
            ), ["seizure_free_anchor_from_last_event_phrase"]
    month_year = re.search(
        r"\bsince\s+(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if month_year is not None:
        parsed = _month_year_to_iso(
            month_year.group("month"),
            month_year.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase",
                source_phrase=month_year.group(0),
            ), []
    numeric_month_year = re.search(
        r"\bsince\s+(?P<month>\d{1,2})\s*(?:/|-)\s*(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if numeric_month_year is not None:
        parsed = _numeric_month_year_to_iso(
            numeric_month_year.group("month"),
            numeric_month_year.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase",
                source_phrase=numeric_month_year.group(0),
            ), []
    event_month_year = re.search(
        r"\b(?:since|commencing|starting|titration|titrating|dose increase|"
        r"dose titration)(?P<context>.{0,80}?)\b(?:at|in|from)\s+"
        r"(?:the\s+)?(?:(?P<qualifier>early|mid|late|end)(?:\s+of)?[\s-]+)?"
        r"(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if event_month_year is not None:
        parsed = _month_year_to_iso(
            event_month_year.group("month"),
            event_month_year.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_event_anchor_month_year",
                source_phrase=event_month_year.group(0),
            ), [
                "seizure_free_anchor_from_event_phrase",
                *(
                    ["seizure_free_anchor_approximate_start_month_policy"]
                    if event_month_year.group("qualifier")
                    else []
                ),
            ]
    day_month_without_year = re.search(
        r"\b(?:since|last event on|last seizure on|last reported event was on|"
        r"last such episode occurred on|most recent episode was on)\s+"
        r"(?P<day>\d{1,2})\s*(?:/|-|\s+)(?P<month>[A-Za-z]+)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if day_month_without_year is not None and reference_date is not None:
        parsed = _day_month_without_year_to_iso(
            day_month_without_year.group("day"),
            day_month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            source = "seizure_free_source_phrase_year_inferred_from_reference_date"
            issues = ["seizure_free_anchor_year_inferred_from_reference_date"]
            if "last" in day_month_without_year.group(0).lower():
                issues.append("seizure_free_anchor_from_last_event_phrase")
            return DateReference(
                date=parsed,
                date_precision="day",
                source=source,
                source_phrase=day_month_without_year.group(0),
            ), issues
    numeric_day_month_without_year = re.search(
        r"\b(?:since|last event on|last seizure on|last reported event was on|"
        r"last such episode occurred on|most recent episode was on)\s+"
        r"(?P<day>\d{1,2})[/-](?P<month>\d{1,2})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if numeric_day_month_without_year is not None and reference_date is not None:
        parsed = _numeric_day_month_without_year_to_iso(
            numeric_day_month_without_year.group("day"),
            numeric_day_month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            issues = ["seizure_free_anchor_year_inferred_from_reference_date"]
            if "last" in numeric_day_month_without_year.group(0).lower():
                issues.append("seizure_free_anchor_from_last_event_phrase")
            return DateReference(
                date=parsed,
                date_precision="day",
                source="seizure_free_source_phrase_year_inferred_from_reference_date",
                source_phrase=numeric_day_month_without_year.group(0),
            ), issues
    approximate_year = re.search(
        r"\bsince\s+(?P<qualifier>early|mid|late)\s+(?P<year>\d{4})\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if approximate_year is not None:
        parsed = _approximate_year_to_iso(
            approximate_year.group("qualifier"),
            approximate_year.group("year"),
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase_approximate_anchor_policy",
                source_phrase=approximate_year.group(0),
            ), ["seizure_free_anchor_approximate_start_month_policy"]
    season_without_year = re.search(
        r"\bsince\s+(?P<qualifier>early|mid|late)?\s*"
        r"(?P<season>spring|summer|autumn|fall|winter)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if season_without_year is not None and reference_date is not None:
        parsed = _season_without_year_to_iso(
            season_without_year.group("season"),
            qualifier=season_without_year.group("qualifier"),
            reference_date=reference_date,
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase_approximate_anchor_policy",
                source_phrase=season_without_year.group(0),
            ), [
                "seizure_free_anchor_year_inferred_from_reference_date",
                "seizure_free_anchor_approximate_start_month_policy",
            ]
    event_month_without_year = re.search(
        r"\b(?:since|commencing|starting|titration|titrating|dose increase|dose titration)"
        r"(?P<context>.{0,80}?)\b(?:at|in|from)\s+"
        r"(?:the\s+)?"
        r"(?:(?P<qualifier>early|mid|late|end)(?:\s+of)?[\s-]+)?"
        r"(?P<month>[A-Za-z]+)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if event_month_without_year is not None and reference_date is not None:
        parsed = _month_without_year_to_iso(
            event_month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source=("seizure_free_event_anchor_month_year_inferred_from_reference_date"),
                source_phrase=event_month_without_year.group(0),
            ), [
                "seizure_free_anchor_year_inferred_from_reference_date",
                "seizure_free_anchor_from_event_phrase",
                *(
                    ["seizure_free_anchor_approximate_start_month_policy"]
                    if event_month_without_year.group("qualifier")
                    else []
                ),
            ]
    month_without_year = re.search(
        r"\bsince\s+(?:(?P<qualifier>early|mid|late)[\s-]+)?"
        r"(?P<month>[A-Za-z]+)\b",
        normalized,
        flags=re.IGNORECASE,
    )
    if month_without_year is not None and reference_date is not None:
        parsed = _month_without_year_to_iso(
            month_without_year.group("month"),
            reference_date=reference_date,
        )
        if parsed is not None:
            return DateReference(
                date=parsed,
                date_precision="month",
                source="seizure_free_source_phrase_year_inferred_from_reference_date",
                source_phrase=month_without_year.group(0),
            ), [
                "seizure_free_anchor_year_inferred_from_reference_date",
                *(
                    ["seizure_free_anchor_approximate_start_month_policy"]
                    if month_without_year.group("qualifier")
                    else []
                ),
            ]
    return None, []


def _mentions_since_anchor(source_phrase: str) -> bool:
    return bool(re.search(r"\bsince\b", source_phrase, flags=re.IGNORECASE))


def _month_year_to_iso(month: str, year: str) -> str | None:
    month_number = _month_number(month)
    if month_number is None:
        return None
    return f"{int(year):04d}-{month_number:02d}"


def _day_month_year_to_iso(day: str, month: str, year: str) -> str | None:
    month_number = _month_number(month)
    if month_number is None:
        return None
    try:
        parsed = date(int(year), month_number, int(day))
    except ValueError:
        return None
    return parsed.isoformat()


def _numeric_day_month_year_to_iso(day: str, month: str, year: str) -> str | None:
    try:
        parsed = date(int(year), int(month), int(day))
    except ValueError:
        return None
    return parsed.isoformat()


def _numeric_month_year_to_iso(month: str, year: str) -> str | None:
    try:
        month_number = int(month)
    except ValueError:
        return None
    if not 1 <= month_number <= 12:
        return None
    return f"{int(year):04d}-{month_number:02d}"


def _day_month_without_year_to_iso(
    day: str,
    month: str,
    *,
    reference_date: str,
) -> str | None:
    month_number = _month_number(month)
    if month_number is None:
        return None
    return _day_numeric_month_without_year_to_iso(
        day,
        str(month_number),
        reference_date=reference_date,
    )


def _numeric_day_month_without_year_to_iso(
    day: str,
    month: str,
    *,
    reference_date: str,
) -> str | None:
    return _day_numeric_month_without_year_to_iso(
        day,
        month,
        reference_date=reference_date,
    )


def _day_numeric_month_without_year_to_iso(
    day: str,
    month: str,
    *,
    reference_date: str,
) -> str | None:
    try:
        reference = date.fromisoformat(reference_date)
        month_number = int(month)
        day_number = int(day)
    except ValueError:
        return None
    year = reference.year
    if month_number > reference.month:
        year -= 1
    try:
        parsed = date(year, month_number, day_number)
    except ValueError:
        return None
    if parsed > reference:
        try:
            parsed = date(year - 1, month_number, day_number)
        except ValueError:
            return None
    return parsed.isoformat()


def _approximate_year_to_iso(qualifier: str, year: str) -> str | None:
    month = {
        "early": 1,
        "mid": 6,
        "late": 10,
    }.get(qualifier.strip().lower())
    if month is None:
        return None
    return f"{int(year):04d}-{month:02d}"


def _season_without_year_to_iso(
    season: str,
    *,
    qualifier: str | None,
    reference_date: str,
) -> str | None:
    season_key = season.strip().lower()
    season_start_month = {
        "spring": 3,
        "summer": 6,
        "autumn": 9,
        "fall": 9,
        "winter": 12,
    }.get(season_key)
    if season_start_month is None:
        return None
    offset = {
        "early": 0,
        "mid": 1,
        "late": 2,
        None: 0,
    }.get(None if qualifier is None else qualifier.strip().lower(), 0)
    month_number = season_start_month + offset
    if month_number > 12:
        month_number -= 12
    try:
        reference = date.fromisoformat(reference_date)
    except ValueError:
        return None
    year = reference.year
    if month_number > reference.month:
        year -= 1
    return f"{year:04d}-{month_number:02d}"


def _month_without_year_to_iso(month: str, *, reference_date: str) -> str | None:
    month_number = _month_number(month)
    if month_number is None:
        return None
    try:
        reference = date.fromisoformat(reference_date)
    except ValueError:
        return None
    year = reference.year
    if month_number > reference.month:
        year -= 1
    return f"{year:04d}-{month_number:02d}"


def _month_number(month: str) -> int | None:
    lookup = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }
    return lookup.get(month.strip().lower())


def _whole_months_between(anchor_date: str, reference_date: str) -> int | None:
    try:
        reference = date.fromisoformat(reference_date)
    except ValueError:
        return None
    anchor_parts = anchor_date.split("-")
    try:
        anchor_year = int(anchor_parts[0])
        anchor_month = int(anchor_parts[1])
        anchor_day = int(anchor_parts[2]) if len(anchor_parts) == 3 else 1
        anchor = date(anchor_year, anchor_month, anchor_day)
    except (IndexError, ValueError):
        return None
    months = (reference.year - anchor.year) * 12 + reference.month - anchor.month
    if len(anchor_parts) == 3 and reference.day < anchor.day:
        months -= 1
    return max(months, 0)
