"""Drop a generic dated-cluster active-rate next to a seizure-free sibling."""

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

DATE_KEYS = ("MonthDate", "YearDate")
CLUSTER_RE = re.compile(r"\bclusters?\b", re.IGNORECASE)


def _attrs(mention: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(key): str(value)
        for key, value in dict(mention.get("attributes") or {}).items()
        if value not in (None, "")
    }


def _cui(mention: Mapping[str, Any]) -> str:
    return str(_attrs(mention).get("CUI") or "")


def _is_generic(mention: Mapping[str, Any]) -> bool:
    cui = _cui(mention)
    return cui in GENERIC_SF_CUIS or cui == ""


def is_generic_dated_cluster_active_rate(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    if _frequency_state(dict(mention.get("attributes") or {})) != "active-rate":
        return False
    if not _is_generic(mention):
        return False
    attrs = _attrs(mention)
    if not any(key in DATE_KEYS for key in attrs):
        return False
    return CLUSTER_RE.search(str(mention.get("evidence") or "")) is not None


def letter_has_seizure_free(mentions: Sequence[Mapping[str, Any]]) -> bool:
    for mention in mentions:
        if str(mention.get("entity") or "") != "SeizureFrequency":
            continue
        if _frequency_state(dict(mention.get("attributes") or {})) == "seizure-free":
            return True
    return False


def apply_dated_cluster_next_to_free_drop(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    if not letter_has_seizure_free(mentions):
        return [dict(mention) for mention in mentions], []
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        if is_generic_dated_cluster_active_rate(mention):
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
