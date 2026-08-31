"""Holgate-like written-form aliases for the prompt-component ablation.

This projection is not the living Gan parser. It only makes the Holgate
ask comparable: the prompt told the model to write ``I do not know``,
and Holgate rates are often ``N seizures per month`` rather than
``N per month``.
"""

from __future__ import annotations

import re

from clinical_extraction.tasks.shared.epilepsy.normalization import (
    normalize_frequency_label,
)

HOLGATE_DIALECT_VERSION = "holgate_dialect_v1"

_ABSTENTIONS = frozenset(
    {
        "i do not know",
        "i do not know.",
        "i don't know",
        "i don't know.",
    }
)
_ZERO_SEIZURES = frozenset(
    {
        "0 seizures",
        "0 seizures per year",
        "0 seizures per month",
        "0 seizures per week",
        "0 seizures per day",
    }
)
_SLASH_RATE = re.compile(
    r"^(\d+(?:\.\d+)?)\s*/\s*(day|week|month|year)s?$",
    re.IGNORECASE,
)
_SEIZURES_PER = re.compile(
    r"^(\d+(?:\.\d+)?)(?:\s*(?:-|to)\s*(\d+(?:\.\d+)?))?"
    r"\s+seizures?\s+per\s+"
    r"(?:(\d+(?:\.\d+)?)\s+)?"
    r"(day|week|month|year)s?$",
    re.IGNORECASE,
)


def project_holgate_dialect_label(
    label: str | None,
    *,
    final_kind: str | None = None,
) -> str | None:
    """Map Holgate-prompted wording onto a living-parser label when safe."""

    if label is None or not str(label).strip():
        if final_kind == "unknown":
            return "unknown"
        if final_kind == "no_reference":
            return "no seizure frequency reference"
        return label

    raw = str(label).strip()
    normalized = normalize_frequency_label(raw)
    if normalized in _ABSTENTIONS:
        return "unknown"
    if "seizure-free" in normalized or "seizure_free" in normalized:
        return "seizure free"
    if normalized in _ZERO_SEIZURES:
        return "seizure free"

    stripped = _strip_bound_prefix(normalized)
    slash = _SLASH_RATE.match(stripped)
    if slash is not None:
        return f"{_as_int(slash.group(1))} per {slash.group(2)}"

    seizures = _SEIZURES_PER.match(stripped)
    if seizures is not None:
        low, high, denom, unit = seizures.group(1, 2, 3, 4)
        count = (
            f"{_as_int(low)} to {_as_int(high)}"
            if high is not None
            else _as_int(low)
        )
        if denom is not None:
            return f"{count} per {_as_int(denom)} {unit}"
        return f"{count} per {unit}"
    return raw


def _strip_bound_prefix(label: str) -> str:
    if label.startswith("≤"):
        return label[1:].strip()
    if label.startswith("<="):
        return label[2:].strip()
    return label


def _as_int(value: str) -> str:
    number = float(value)
    if number.is_integer():
        return str(int(number))
    return value
