"""Error taxonomy helpers for Observatory routes."""

from __future__ import annotations

from typing import Any

_CATEGORY_MAGNITUDE: dict[str, int] = {
    "currently_no_seizure": 0,
    "seizure_freq_unknown": 0,
    "seizure_freq_1_per_yr": 1,
    "seizure_freq_1_per_6mon": 2,
    "seizure_freq_more1per6mon_less1mon": 3,
    "seizure_freq_1_per_mon": 4,
    "seizure_freq_more1mon_less1week": 5,
    "seizure_freq_1_per_week": 6,
    "seizure_freq_more1week_less1day": 7,
    "seizure_freq_1ormore_daily": 8,
    "seizure_infrequent": 1,
    "seizure_frequent": 8,
}


def category_magnitude(cat: str) -> int:
    return _CATEGORY_MAGNITUDE.get(cat, 0)


def classify_error(
    gold_category: str,
    predicted_category: str,
    purist_correct: bool,
) -> dict[str, Any]:
    if purist_correct:
        return {"error_type": "correct", "severity": 0, "severity_level": "none"}

    gold_mag = category_magnitude(gold_category)
    pred_mag = category_magnitude(predicted_category)
    severity = abs(pred_mag - gold_mag)

    if gold_mag > 0 and pred_mag == 0:
        error_type = "false_negative"
    elif gold_mag == 0 and pred_mag > 0:
        error_type = "false_positive"
    elif pred_mag > gold_mag:
        error_type = "near_miss" if pred_mag - gold_mag == 1 else "over_estimate"
    elif pred_mag < gold_mag:
        error_type = "near_miss" if gold_mag - pred_mag == 1 else "under_estimate"
    else:
        error_type = "near_miss"

    if severity == 0:
        severity_level = "none"
    elif severity == 1:
        severity_level = "near"
    elif severity <= 3:
        severity_level = "moderate"
    elif severity <= 5:
        severity_level = "significant"
    else:
        severity_level = "severe"

    return {"error_type": error_type, "severity": severity, "severity_level": severity_level}
