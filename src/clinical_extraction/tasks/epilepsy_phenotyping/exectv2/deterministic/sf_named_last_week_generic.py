"""Retarget a named last-week active-rate onto generic when unknown sibling exists."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    GENERIC_SEIZURE_CUI,
    GENERIC_SF_CUIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
)

LAST_WEEK_RE = re.compile(r"\blast week\b", re.IGNORECASE)


def _attrs(mention: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in dict(mention.get("attributes") or {}).items()
        if value not in (None, "")
    }


def _cui(mention: Mapping[str, Any]) -> str:
    return str(_attrs(mention).get("CUI") or "")


def _state(mention: Mapping[str, Any]) -> str:
    return _frequency_state(dict(mention.get("attributes") or {}))


def _is_named(mention: Mapping[str, Any]) -> bool:
    cui = _cui(mention)
    return bool(cui) and cui not in GENERIC_SF_CUIS


def _is_last_week(mention: Mapping[str, Any]) -> bool:
    attrs = _attrs(mention)
    if attrs.get("PointInTime") == "Last_Week":
        return True
    return LAST_WEEK_RE.search(str(mention.get("evidence") or "")) is not None


def named_unknown_cuis(mentions: Sequence[Mapping[str, Any]]) -> set[str]:
    found: set[str] = set()
    for mention in mentions:
        if str(mention.get("entity") or "") != "SeizureFrequency":
            continue
        if _state(mention) != "unknown" or not _is_named(mention):
            continue
        found.add(_cui(mention))
    return found


def is_named_last_week_active_rate(
    mention: Mapping[str, Any], unknown_cuis: set[str]
) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    if _state(mention) != "active-rate" or not _is_named(mention):
        return False
    if not _is_last_week(mention):
        return False
    return _cui(mention) in unknown_cuis


def apply_named_last_week_generic_retarget(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    unknown_cuis = named_unknown_cuis(mentions)
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        if is_named_last_week_active_rate(mention, unknown_cuis):
            out = dict(mention)
            attrs = dict(out.get("attributes") or {})
            source = str(attrs.get("CUI") or "")
            attrs["CUI"] = GENERIC_SEIZURE_CUI
            out["attributes"] = attrs
            actions.append(
                {
                    "action": "retarget",
                    "text": str(mention.get("text") or ""),
                    "cui": source,
                }
            )
            kept.append(out)
            continue
        kept.append(dict(mention))
    return kept, actions
