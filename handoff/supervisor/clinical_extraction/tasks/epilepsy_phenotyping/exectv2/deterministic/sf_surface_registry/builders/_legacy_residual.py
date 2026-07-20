"""Legacy SF convention residual additions (Stack B).

.. deprecated::
    Extracted from ``_legacy_impl``; behavior-preserving.
"""
# ruff: noqa: F405 — legacy regex constants are star-imported from ``_legacy_constants``.

from __future__ import annotations

import re

from ._legacy_constants import *  # noqa: F401,F403 (re-export legacy constants)
from ._legacy_noise import _sf_number


def sf_residual_additions(note_text: str) -> list[tuple[str, str, dict[str, str]]]:
    """Return bounded dev residual SF additions from explicit source patterns."""

    additions: list[tuple[str, str, dict[str, str]]] = []
    for match in re.finditer(_SF_GENERIC_EVERY_RANGE_RE, note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": match.group("low"),
                    "UpperNumberOfTimePeriods": match.group("high"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_PER_MONTH_RANGE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GENERIC_OVER_MONTHS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": match.group("months"),
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GENERIC_SINGLE_LAST_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Week",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_GENERIC_BETWEEN_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_SEVERAL_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_EVERY_WEEKS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_WEEKLY_SEIZURES_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GENERIC_LAST_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Month",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_CURRENT_SEIZURES_TIMES_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "LowerNumberOfSeizures": _sf_number(match.group("low")),
                    "UpperNumberOfSeizures": _sf_number(match.group("high")),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_ONE_SEIZURE_PER_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SEIZURE_EVERY_YEAR_RANGE_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": _sf_number(match.group("low")),
                    "UpperNumberOfTimePeriods": _sf_number(match.group("high")),
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SEIZURE_INCREASE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "FrequencyChange": "Increased",
                },
            )
        )
    for match in _SF_SEIZURE_FREQUENCY_REDUCED_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "FrequencyChange": "Decreased",
                },
            )
        )
    for match in _SF_ONE_SEIZURE_PER_WEEK_TO_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "1",
                    "LowerNumberOfTimePeriods": "1",
                    "UpperNumberOfTimePeriods": "4",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_AROUND_N_SEIZURES_PER_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_HAD_N_SEIZURES_RE.finditer(note_text):
        window = note_text[max(0, match.start() - 80) : match.end() + 80]
        if re.search(r"\bfebrile\b|\bprevious\b|\bfirst seizure\b", window, re.IGNORECASE):
            continue
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                },
            )
        )
    for match in _SF_GENERIC_TOTAL_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": match.group("count"),
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_FREQUENT_SEIZURES_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                },
            )
        )
    for match in re.finditer(_SF_GENERIC_NO_FURTHER_SINCE_RE, note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_NOT_HAD_ANY_MORE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_SINGLE_SEIZURE_WEEKS_AGO_RE.finditer(note_text):
        additions.append(
            (
                "seizure",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_LAST_SEIZURES_TEENAGE_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_BROAD_SEIZURE_FREE_RE.finditer(note_text):
        window = note_text[max(0, match.start() - 60) : match.end() + 60]
        if re.search(_SF_CONTEXTUAL_RATE_NOISE_RE, window):
            continue
        additions.append(
            (
                "seizure-free",
                match.group(0),
                {
                    "CUI": "C1299590",
                    "CUIPhrase": "seizure-free",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for match in _SF_LAST_SEIZURE_MONTHS_RE.finditer(note_text):
        additions.append(
            (
                "seizures",
                match.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizures",
                    "NumberOfSeizures": "0",
                    "NumberOfTimePeriods": match.group("months"),
                    "TimePeriod": "Month",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in re.finditer(_SF_DATED_GTC_RE, note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_GTC_LAST_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizure",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizure",
                    "NumberOfSeizures": "1",
                    "PointInTime": "Last_Week",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in _SF_GTC_DAY_BURST_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Day",
                    "TimeSince_or_TimeOfEvent": "During",
                },
            )
        )
    for match in re.finditer(_SF_GTC_RANGE_PER_WEEK_RE, note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "LowerNumberOfSeizures": match.group("low"),
                    "UpperNumberOfSeizures": match.group("high"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in re.finditer(_SF_GTC_FOUR_LAST_THREE_WEEKS_RE, note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "4",
                    "NumberOfTimePeriods": "3",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_GTC_SINCE_PREVIOUS_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in re.finditer(_SF_GTC_PER_MONTH_RE, note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_GTC_ONE_TO_TWO_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "LowerNumberOfSeizures": _sf_number(match.group("low")),
                    "UpperNumberOfSeizures": _sf_number(match.group("high")),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in re.finditer(_SF_GTC_FURTHER_SINCE_RE, note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in re.finditer(_SF_NO_FURTHER_GTC_SINCE_RE, note_text):
        additions.append(
            (
                "generalised tonic clonic seizures",
                match.group(0),
                {
                    "CUI": "C0494475",
                    "CUIPhrase": "generalised tonic clonic seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_ABSENCE_LIKE_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "absence like seizures",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absence like seizures",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": match.group("year"),
                },
            )
        )
    matched = _SF_FSAW_FORTNIGHT_RE.search(note_text)
    if matched is not None:
        additions.append(
            (
                "focal seizures with altered awareness",
                matched.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "2",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_EVERY_WEEKS_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": match.group("weeks"),
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_SEVERAL_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_FSAW_ONE_PER_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_FSAW_PROBABLY_SEVERAL_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "focal seizures with altered awareness",
                match.group(0),
                {
                    "CUI": "C0270834",
                    "CUIPhrase": "focal seizures with altered awareness",
                    "NumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_SECONDARY_PER_PERIOD_RE.finditer(note_text):
        attrs = {
            "CUI": "C0270838",
            "CUIPhrase": "secondary generalised seizures",
            "LowerNumberOfSeizures": match.group("count"),
            "NumberOfTimePeriods": "1",
            "TimePeriod": match.group("period").title(),
        }
        if match.group("high"):
            attrs["UpperNumberOfSeizures"] = match.group("high")
        else:
            attrs["NumberOfSeizures"] = match.group("count")
            attrs.pop("LowerNumberOfSeizures", None)
        additions.append(("secondary generalised seizures", match.group(0), attrs))
    for match in _SF_SECONDARY_AROUND_PER_YEAR_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizures",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizures",
                    "NumberOfSeizures": match.group("count"),
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Year",
                },
            )
        )
    for match in _SF_SECONDARY_ONCE_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizure",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizure",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_SECONDARY_LAST_CHRISTMAS_RE.finditer(note_text):
        additions.append(
            (
                "secondary generalised seizures",
                match.group(0),
                {
                    "CUI": "C0270838",
                    "CUIPhrase": "secondary generalised seizures",
                    "NumberOfSeizures": "0",
                    "DayDate": "25",
                    "MonthDate": "12",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    for match in _SF_COMPLEX_PARTIAL_PER_MONTH_RE.finditer(note_text):
        additions.append(
            (
                "complex partial seizure",
                match.group(0),
                {
                    "CUI": "C0149958",
                    "CUIPhrase": "complex partial seizure",
                    "LowerNumberOfSeizures": "1",
                    "UpperNumberOfSeizures": "2",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                },
            )
        )
    for match in _SF_MYCLONIC_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                },
            )
        )
    for match in _SF_MYCLONIC_DAILY_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                    "FrequencyChange": "Frequent",
                },
            )
        )
    for match in _SF_MYCLONIC_ONE_WEEK_RE.finditer(note_text):
        additions.append(
            (
                "myoclonic jerks",
                match.group(0),
                {
                    "CUI": "C0027066",
                    "CUIPhrase": "myoclonic jerks",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Week",
                },
            )
        )
    for match in _SF_ABSENCE_UNKNOWN_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                },
            )
        )
    for match in _SF_ABSENCES_FREQUENT_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                    "FrequencyChange": "Frequent",
                },
            )
        )
    for match in _SF_TYPICAL_ABSENCES_SINCE_RE.finditer(note_text):
        additions.append(
            (
                "typical absences",
                match.group(0),
                {
                    "CUI": "C4316903",
                    "CUIPhrase": "typical absences",
                    "FrequencyChange": "Same",
                    "PointInTime": "LastClinic",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_ABSENCES_ACTIVE_RE.finditer(note_text):
        additions.append(
            (
                "absences",
                match.group(0),
                {
                    "CUI": "C0563606",
                    "CUIPhrase": "absences",
                    "NumberOfSeizures": "1",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Day",
                },
            )
        )
    for match in _SF_FOCAL_MOTOR_ACTIVE_RE.finditer(note_text):
        additions.append(
            (
                "focal motor seizure",
                match.group(0),
                {
                    "CUI": "C0016399",
                    "CUIPhrase": "focal motor seizure",
                    "NumberOfSeizures": "1",
                },
            )
        )
    for match in _SF_FOCAL_MOTOR_FREE_RE.finditer(note_text):
        additions.append(
            (
                "focal motor seizures",
                match.group(0),
                {
                    "CUI": "C0016399",
                    "CUIPhrase": "focal motor seizures",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for match in _SF_FTB_GENERIC_LAST_EVENT_RE.finditer(note_text):
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                match.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                },
            )
        )
    for match in _SF_FTB_DATED_EVENTS_RE.finditer(note_text):
        for month, year in (("8", match.group("year1")), ("9", match.group("year2"))):
            additions.append(
                (
                    "focal to bilateral convulsive seizures",
                    match.group(0),
                    {
                        "CUI": "C0877017",
                        "CUIPhrase": "focal to bilateral convulsive seizures",
                        "MonthDate": month,
                        "NumberOfSeizures": "1",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": year,
                    },
                )
            )
    for match in _SF_FTB_LAST_ONE_CHRISTMAS_RE.finditer(note_text):
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                match.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "DayDate": "25",
                    "MonthDate": "12",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": match.group("year"),
                },
            )
        )
    matched = _SF_SEIZURES_RETURNED_RE.search(note_text)
    if matched is not None:
        additions.append(
            (
                "seizure",
                matched.group(0),
                {
                    "CUI": "C0036572",
                    "CUIPhrase": "seizure",
                    "FrequencyChange": "Increased",
                },
            )
        )
    matched = _SF_CLUSTER_AUGUST_RE.search(note_text)
    if matched is not None:
        additions.append(
            (
                "cluster of seizures",
                matched.group(0),
                {
                    "CUI": "C3203523",
                    "CUIPhrase": "cluster of seizures",
                    "MonthDate": "8",
                    "NumberOfSeizures": "1",
                    "TimeSince_or_TimeOfEvent": "During",
                    "YearDate": matched.group("year"),
                },
            )
        )
    matched = _SF_FTB_LAST_EVENT_RE.search(note_text)
    if matched is not None:
        additions.append(
            (
                "focal to bilateral convulsive seizures",
                matched.group(0),
                {
                    "CUI": "C0877017",
                    "CUIPhrase": "focal to bilateral convulsive seizures",
                    "FrequencyChange": "Infrequent",
                },
            )
        )
        additions.append(
            (
                "convulsive seizure",
                matched.group(0),
                {
                    "CUI": "C0751494",
                    "CUIPhrase": "convulsive seizure",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": matched.group("year"),
                },
            )
        )
    matched = _SF_SINGLE_CONVULSIVE_LAST_EVENT_RE.search(note_text)
    if matched is not None:
        additions.append(
            (
                "convulsive seizure",
                matched.group(0),
                {
                    "CUI": "C0751494",
                    "CUIPhrase": "convulsive seizure",
                    "NumberOfSeizures": "0",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "YearDate": matched.group("year"),
                },
            )
        )
    for match in _SF_REMAINS_SEIZURE_FREE_RE.finditer(note_text):
        evidence = match.group(0)
        additions.append(
            (
                "seizure-free",
                evidence,
                {
                    "CUI": "C1299590",
                    "CUIPhrase": "seizure-free",
                    "NumberOfSeizures": "0",
                },
            )
        )
    for pattern in (_SF_SEIZURES_HAVE_STOPPED_RE, _SF_NO_EVENTS_SINCE_SURGERY_RE):
        for match in pattern.finditer(note_text):
            additions.append(
                (
                    "seizures",
                    match.group(0),
                    {
                        "CUI": "C0036572",
                        "CUIPhrase": "seizures",
                        "NumberOfSeizures": "0",
                    },
                )
            )
    return additions


__all__ = [
    "sf_residual_additions",
]
