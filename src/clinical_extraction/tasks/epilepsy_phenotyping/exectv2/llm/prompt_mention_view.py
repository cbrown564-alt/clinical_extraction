"""Shared mention views for later-stage ExECT prompts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

_DETAIL_KEYS = (
    "count",
    "lower_count",
    "upper_count",
    "period_count",
    "lower_period",
    "upper_period",
    "period",
    "state",
    "change",
    "since_or_during",
    "point_in_time",
    "day",
    "month",
    "year",
    "dose",
    "unit",
    "schedule",
    "status",
    "performed",
    "result",
    "eeg_type",
    "category",
    "age_unit",
)

_GOLD_DETAIL_KEYS = {
    "NumberOfSeizures": "count",
    "LowerNumberOfSeizures": "lower_count",
    "UpperNumberOfSeizures": "upper_count",
    "NumberOfTimePeriods": "period_count",
    "LowerNumberOfTimePeriods": "lower_period",
    "UpperNumberOfTimePeriods": "upper_period",
    "TimePeriod": "period",
    "FrequencyChange": "change",
    "TimeSince_or_TimeOfEvent": "since_or_during",
    "PointInTime": "point_in_time",
    "DayDate": "day",
    "MonthDate": "month",
    "YearDate": "year",
    "DrugDose": "dose",
    "DoseUnit": "unit",
    "Frequency": "schedule",
    "DiagCategory": "category",
    "AgeUnit": "age_unit",
    "MRI_Performed": "performed",
    "CT_Performed": "performed",
    "EEG_Performed": "performed",
    "MRI_Results": "result",
    "CT_Results": "result",
    "EEG_Results": "result",
    "EEG_Type": "eeg_type",
}

_PLAIN_TO_GOLD = {
    "count": "NumberOfSeizures",
    "lower_count": "LowerNumberOfSeizures",
    "upper_count": "UpperNumberOfSeizures",
    "period_count": "NumberOfTimePeriods",
    "lower_period": "LowerNumberOfTimePeriods",
    "upper_period": "UpperNumberOfTimePeriods",
    "period": "TimePeriod",
    "change": "FrequencyChange",
    "since_or_during": "TimeSince_or_TimeOfEvent",
    "point_in_time": "PointInTime",
    "day": "DayDate",
    "month": "MonthDate",
    "year": "YearDate",
    "dose": "DrugDose",
    "unit": "DoseUnit",
    "schedule": "Frequency",
    "category": "DiagCategory",
    "age_unit": "AgeUnit",
    "eeg_type": "EEG_Type",
}
_TEST_RESULT_KEYS = {
    "MRI": "MRI_Results",
    "CT": "CT_Results",
    "EEG": "EEG_Results",
}
_TEST_PERFORMED_KEYS = {
    "MRI": "MRI_Performed",
    "CT": "CT_Performed",
    "EEG": "EEG_Performed",
}


def mention_id(mention: Mapping[str, Any]) -> str:
    return str(mention.get("mention_id") or mention.get("finding_id") or "")


def mention_family(mention: Mapping[str, Any]) -> str:
    return str(mention.get("clinical_family") or mention.get("entity") or "")


def mention_name(mention: Mapping[str, Any]) -> str:
    return str(mention.get("clinical_name") or mention.get("text") or "")


def mention_standard_name(mention: Mapping[str, Any]) -> str:
    return str(mention.get("standard_name") or mention.get("text") or "")


def mention_sentence(mention: Mapping[str, Any]) -> str:
    return str(
        mention.get("supporting_sentence") or mention.get("evidence") or ""
    )


def mention_details(mention: Mapping[str, Any]) -> dict[str, str]:
    raw = mention.get("details")
    if not isinstance(raw, Mapping):
        raw = mention.get("attributes") or {}
    if not isinstance(raw, Mapping):
        return {}
    details: dict[str, str] = {}
    for source, target in _GOLD_DETAIL_KEYS.items():
        value = raw.get(source)
        if value is None or value == "":
            continue
        details.setdefault(target, str(value))
    for key in _DETAIL_KEYS:
        value = raw.get(key)
        if value is None or value == "":
            continue
        details[key] = str(value)
    return details


def gold_key_for_detail(family: str, standard_name: str, key: str) -> str | None:
    """Map a plain details key back to the gold attribute name."""

    if key == "result":
        return _TEST_RESULT_KEYS.get(standard_name.upper(), _TEST_RESULT_KEYS.get(family))
    if key in {"performed", "status"}:
        return _TEST_PERFORMED_KEYS.get(
            standard_name.upper(),
            _TEST_PERFORMED_KEYS.get(family),
        )
    return _PLAIN_TO_GOLD.get(key)
