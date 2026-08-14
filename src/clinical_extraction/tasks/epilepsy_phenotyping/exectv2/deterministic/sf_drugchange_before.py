"""Drop a named DrugChange-before active-rate, optionally only with a sibling rate."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    GENERIC_SF_CUIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
)

BEFORE_RE = re.compile(r"\bbefore\b", re.IGNORECASE)


def _attrs(mention: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in dict(mention.get("attributes") or {}).items()
        if value not in (None, "")
    }


def _cui(mention: Mapping[str, Any]) -> str:
    return str(_attrs(mention).get("CUI") or "")


def _is_named(mention: Mapping[str, Any]) -> bool:
    cui = _cui(mention)
    return bool(cui) and cui not in GENERIC_SF_CUIS


def _is_active_rate(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    return _frequency_state(dict(mention.get("attributes") or {})) == "active-rate"


def is_drugchange_before_active_rate(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    if _frequency_state(dict(mention.get("attributes") or {})) != "active-rate":
        return False
    if not _is_named(mention):
        return False
    if _attrs(mention).get("PointInTime") != "DrugChange":
        return False
    return BEFORE_RE.search(str(mention.get("evidence") or "")) is not None


def letter_has_other_active_rate(mentions: Sequence[Mapping[str, Any]]) -> bool:
    return any(
        _is_active_rate(mention) and not is_drugchange_before_active_rate(mention)
        for mention in mentions
    )


def apply_drugchange_before_active_rate_drop(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        if is_drugchange_before_active_rate(mention):
            actions.append(
                {
                    "action": "drop",
                    "text": str(mention.get("text") or ""),
                    "cui": _cui(mention),
                }
            )
            continue
        kept.append(dict(mention))
    return kept, actions


def apply_drugchange_before_sibling_drop(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if not letter_has_other_active_rate(mentions):
        return [dict(mention) for mention in mentions], []
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        if is_drugchange_before_active_rate(mention):
            actions.append(
                {
                    "action": "drop",
                    "text": str(mention.get("text") or ""),
                    "cui": _cui(mention),
                }
            )
            continue
        kept.append(dict(mention))
    return kept, actions
