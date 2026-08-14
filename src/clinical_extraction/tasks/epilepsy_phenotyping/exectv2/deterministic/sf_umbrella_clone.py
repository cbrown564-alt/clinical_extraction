"""Drop a generic SF mention that clones a specific sibling's span."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    GENERIC_SF_CUIS,
    GENERIC_SF_PHRASES,
    SF_CUI_LEXICON,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _FREQUENCY_RATE_ATTRIBUTES,
    _frequency_state,
)

SPECIFIC_SF_CUIS = frozenset(SF_CUI_LEXICON) - GENERIC_SF_CUIS


def headline_state(mention: Mapping[str, Any]) -> str:
    return _frequency_state(dict(mention.get("attributes") or {}))


def mention_cui(mention: Mapping[str, Any]) -> str:
    return str((mention.get("attributes") or {}).get("CUI") or "")


def is_generic_sf(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    cui = mention_cui(mention)
    if cui in GENERIC_SF_CUIS:
        return True
    if cui in SPECIFIC_SF_CUIS:
        return False
    return normalize_phrase(str(mention.get("text") or "")) in GENERIC_SF_PHRASES


def specific_sf_cui(mention: Mapping[str, Any]) -> str | None:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return None
    cui = mention_cui(mention)
    if cui in SPECIFIC_SF_CUIS:
        return cui
    return None


def rate_window(mention: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    attrs = dict(mention.get("attributes") or {})
    items: list[tuple[str, str]] = []
    for key in sorted(_FREQUENCY_RATE_ATTRIBUTES):
        value = attrs.get(key)
        if value not in (None, ""):
            items.append((key, str(value)))
    return tuple(items)


def evidence_norm(mention: Mapping[str, Any]) -> str:
    return " ".join(str(mention.get("evidence") or "").lower().split())


def clone_key(
    mention: Mapping[str, Any],
) -> tuple[str, str, tuple[tuple[str, str], ...]] | None:
    evidence = evidence_norm(mention)
    window = rate_window(mention)
    if not evidence or not window:
        return None
    return (evidence, headline_state(mention), window)


def apply_umbrella_clone_drop(
    mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Drop a generic SF mention that clones a specific sibling's span.

    Gold and letter text unused. Diagnosis mentions are not siblings.
    """

    sibling_keys = {
        key
        for mention in mentions
        if specific_sf_cui(mention) is not None
        for key in (clone_key(mention),)
        if key is not None
    }
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        key = clone_key(mention)
        if is_generic_sf(mention) and key is not None and key in sibling_keys:
            actions.append(
                {
                    "action": "drop",
                    "state": key[1],
                    "from_cui": mention_cui(mention) or "none",
                    "window": ",".join(f"{name}={value}" for name, value in key[2]),
                    "text": str(mention.get("text") or ""),
                    "evidence": str(mention.get("evidence") or ""),
                }
            )
            continue
        kept.append(dict(mention))
    return kept, actions
