"""Allowed seizure-frequency label forms for later-stage encode and select.

This list is intentionally example-heavy. Both prompts must emit only these
written shapes. It is the output dialect, not a letter-to-label cookbook.
"""

from __future__ import annotations

from typing import Any

LABEL_FORM_RULES = [
    "Write the label using only the forms below. Copy an example and change the numbers if needed.",
    "Use digits, not word numbers.",
    "Use day, week, month, or year. Prefer the singular word.",
    "A night count is a day count: once per night becomes 1 per day.",
    "Flatten a bound: at most four per day, or ≤ four per day, becomes 4 per day.",
    "Do not write <=, >=, up to, at most, several, handful, frequent, or a calendar date.",
    (
        "If none of these forms fit, write unknown when seizures are "
        "discussed, or no seizure frequency reference when there is no "
        "usable frequency evidence."
    ),
]

LABEL_FORMS: list[dict[str, Any]] = [
    {
        "form": "N per unit",
        "description": "A single count in one day, week, month, or year.",
        "examples": ["1 per day", "4 per week", "3 per month", "2 per year"],
    },
    {
        "form": "N per N unit",
        "description": "A single count over a stated number of days, weeks, months, or years.",
        "examples": ["1 per 2 day", "1 per 2 week", "2 per 6 month"],
    },
    {
        "form": "N per N to N unit",
        "description": "A single count over a range of days, weeks, months, or years.",
        "examples": ["1 per 2 to 3 day", "1 per 2 to 3 week", "1 per 4 to 6 month"],
    },
    {
        "form": "N to N per unit",
        "description": "A count range in one day, week, month, or year.",
        "examples": [
            "2 to 3 per day",
            "2 to 4 per week",
            "3 to 5 per month",
            "2 to 4 per year",
        ],
    },
    {
        "form": "N to N per N unit",
        "description": "A count range over a stated number of days, weeks, months, or years.",
        "examples": ["2 to 4 per 3 month", "2 to 3 per 2 week"],
    },
    {
        "form": "multiple per unit",
        "description": "More than one seizure in one day, week, or month, with no number given.",
        "examples": ["multiple per day", "multiple per week", "multiple per month"],
    },
    {
        "form": "multiple per N unit",
        "description": (
            "More than one seizure over a stated number of months, "
            "with no number given."
        ),
        "examples": ["multiple per 2 month"],
    },
    {
        "form": "N per multiple unit",
        "description": "A count over an unstated number of days or months.",
        "examples": ["1 per multiple day", "1 per multiple month"],
    },
    {
        "form": "cluster per unit, N per cluster",
        "description": (
            "How often clusters happen, and how many seizures are in each "
            "cluster. The cluster count or the time between clusters may be a range."
        ),
        "examples": [
            "1 cluster per day, 5 per cluster",
            "1 cluster per week, 4 per cluster",
            "1 cluster per 4 month, 5 per cluster",
            "6 cluster per month, 4 per cluster",
            "1 cluster per 4 to 5 day, 2 per cluster",
        ],
    },
    {
        "form": "cluster per unit, range per cluster",
        "description": "How often clusters happen, and a range of seizures in each cluster.",
        "examples": [
            "1 cluster per day, 2 to 4 per cluster",
            "1 cluster per week, 3 to 6 per cluster",
            "1 cluster per month, 4 to 6 per cluster",
        ],
    },
    {
        "form": "cluster per unit, multiple per cluster",
        "description": (
            "How often clusters happen, and more than one seizure in each "
            "cluster with no number given."
        ),
        "examples": [
            "1 cluster per day, multiple per cluster",
            "1 cluster per week, multiple per cluster",
            "1 cluster per month, multiple per cluster",
        ],
    },
    {
        "form": "unknown cluster count",
        "description": "Clusters are described, but how often they happen is not known.",
        "examples": [
            "unknown, 5 per cluster",
            "unknown, 2 to 4 per cluster",
            "unknown, multiple per cluster",
        ],
    },
    {
        "form": "seizure free for a duration",
        "description": "No seizures for a stated length of time.",
        "examples": [
            "seizure free for 6 month",
            "seizure free for 2 year",
            "seizure free for 3 months",
            "seizure free for 2 years",
            "seizure free for 2 to 3 months",
        ],
    },
    {
        "form": "seizure free for a vague duration",
        "description": "No seizures for an unstated length of time.",
        "examples": [
            "seizure free for multiple month",
            "seizure free for multiple year",
        ],
    },
    {
        "form": "unknown",
        "description": "Seizures are discussed, but there is no usable frequency.",
        "examples": ["unknown"],
    },
    {
        "form": "no seizure frequency reference",
        "description": "There is no usable frequency evidence.",
        "examples": ["no seizure frequency reference"],
    },
]


def label_forms_payload() -> dict[str, Any]:
    """Model-facing label-form block shared by encode and select."""

    return {
        "rules": list(LABEL_FORM_RULES),
        "forms": [dict(row) for row in LABEL_FORMS],
    }
