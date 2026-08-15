"""Drop leftover-scope SF mentions that are not current epileptic frequency.

Gold-free: predicates use only mention text, evidence, and attributes.
They do not read gold keys or letter IDs.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)

BARE_SYMPTOM_TOKENS = frozenset({"clumsy", "jerk", "jerks"})
_FEBRILE_RE = re.compile(r"\bfebrile\s+(?:seizures?|convulsions?)\b", re.IGNORECASE)
_DRIVING_RE = re.compile(r"\b(?:driving|licence|license|dvla)\b", re.IGNORECASE)
_GENERIC_SF_PHRASES = frozenset(
    {"seizure", "seizures", "seizure free", "seizure freedom"}
)
_DURATION_KEYS = (
    "TimePeriod",
    "NumberOfTimePeriods",
    "LowerNumberOfTimePeriods",
    "UpperNumberOfTimePeriods",
    "YearDate",
    "MonthDate",
    "DayDate",
    "PointInTime",
    "TimeSince_or_TimeOfEvent",
    "AgeLower",
    "AgeUpper",
    "AgeUnit",
)


def scope_residue_reason(mention: Mapping[str, Any]) -> str | None:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return None
    phrase = normalize_phrase(str(mention.get("text") or ""))
    evidence = str(mention.get("evidence") or mention.get("text") or "")
    cui_phrase = normalize_phrase(str((mention.get("attributes") or {}).get("CUIPhrase") or ""))
    if phrase in BARE_SYMPTOM_TOKENS:
        return "bare_symptom_token"
    if _FEBRILE_RE.search(phrase) or _FEBRILE_RE.search(cui_phrase):
        return "febrile_history"
    if phrase in _GENERIC_SF_PHRASES and _DRIVING_RE.search(evidence):
        attrs = {
            str(key): str(value)
            for key, value in dict(mention.get("attributes") or {}).items()
            if value not in (None, "")
        }
        if not any(key in attrs for key in _DURATION_KEYS):
            return "driving_without_frame"
    return None


def apply_scope_residue_drop(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        reason = scope_residue_reason(mention)
        if reason is not None:
            actions.append(
                {
                    "action": "drop",
                    "reason": reason,
                    "text": str(mention.get("text") or ""),
                    "cui": str((mention.get("attributes") or {}).get("CUI") or ""),
                }
            )
            continue
        kept.append(dict(mention))
    return kept, actions
