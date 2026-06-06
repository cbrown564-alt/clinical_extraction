from __future__ import annotations

import re

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    normalize_frequency_label,
)

from .selected_evidence_text import (
    format_prediction_rate,
    once_twice_thrice,
    words_to_numbers,
)


def monthly_diary_label_from_text(text: str) -> str | None:
    """Sum source-near monthly diary counts from selected evidence or LLM events."""
    normalized = normalize_frequency_label(once_twice_thrice(words_to_numbers(text)))
    for parser in (
        _date_list_diary_label_from_selected_evidence,
        _calendar_log_label_from_selected_evidence,
        _month_sleep_awake_log_label_from_selected_evidence,
        _general_monthly_diary_label_from_selected_evidence,
    ):
        label = parser(normalized)
        if label:
            return label
    return None


def _date_list_diary_label_from_selected_evidence(text: str) -> str | None:
    numeric_match = re.search(
        r"\b(?:diary\s+(?:documents|lists|records):?\s+|recorded\s+)?"
        r"(?:seizure\s+events|seizures?|events?)\s+on\s+"
        r"(?P<dates>\d{2}-\d{2}(?:,\s*\d{2}-\d{2}){1,})\b",
        text,
    )
    if numeric_match:
        month_values = [
            int(value)
            for value in re.findall(r"(\d{2})-\d{2}", numeric_match.group("dates"))
        ]
        if month_values:
            denominator = max(max(month_values) - min(month_values), 1)
            return format_prediction_rate(
                f"{len(month_values)} per {denominator}",
                "month",
            )

    month_name_pattern = (
        r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
        r"[a-z]*\s+\d{1,2}"
    )
    named_match = re.search(
        rf"\b(?:diary\s+(?:documents|lists|records):?\s+|recorded\s+)?"
        rf"(?:seizure\s+events|seizures?|events?)\s+on\s+"
        rf"(?P<dates>{month_name_pattern}(?:,\s*{month_name_pattern})*(?:,\s*and\s+{month_name_pattern}|\s+and\s+{month_name_pattern})?)\b",
        text,
    )
    if named_match:
        month_names = re.findall(
            r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b",
            named_match.group("dates"),
        )
        month_order = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
        }
        month_values = [month_order[name] for name in month_names]
        if month_values:
            denominator = max(max(month_values) - min(month_values), 1)
            return format_prediction_rate(
                f"{len(month_values)} per {denominator}",
                "month",
            )
    return None


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
    return format_prediction_rate(
        f"{sum(int(value) for value in entries)} per {len(entries)}",
        "month",
    )


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
    return format_prediction_rate(f"{sum(counts)} per {len(counts)}", "month")


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
    return format_prediction_rate(
        f"{sum(month_counts.values())} per {len(month_counts)}",
        "month",
    )


def _diary_count_value(count_text: str) -> int:
    if count_text in {"a", "an"}:
        return 1
    return 0 if count_text in {"no", "zero"} else int(count_text)
