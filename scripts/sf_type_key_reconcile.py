"""Study-local SF type-key reconcile. Not wired into the production pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    GENERIC_SF_CUIS,
    GENERIC_SF_PHRASES,
    SF_CUI_LEXICON,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
)

SPECIFIC_SF_CUIS = frozenset(SF_CUI_LEXICON) - GENERIC_SF_CUIS
Arm = Literal["retarget_generic_unique", "drop_generic_duplicate_state", "bundle"]


def headline_state(mention: Mapping[str, Any]) -> str:
    return _frequency_state(dict(mention.get("attributes") or {}))


def mention_cui(mention: Mapping[str, Any]) -> str:
    return str((mention.get("attributes") or {}).get("CUI") or "")


def is_generic_sf(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    if mention_cui(mention) in GENERIC_SF_CUIS:
        return True
    return normalize_phrase(str(mention.get("text") or "")) in GENERIC_SF_PHRASES


def specific_sf_cui(mention: Mapping[str, Any]) -> str | None:
    cui = mention_cui(mention)
    if cui in SPECIFIC_SF_CUIS:
        return cui
    return None


def candidate_specific_cuis(mentions: Sequence[Mapping[str, Any]]) -> set[str]:
    found: set[str] = set()
    for mention in mentions:
        entity = str(mention.get("entity") or "")
        cui = mention_cui(mention)
        if entity == "SeizureFrequency" and cui in SPECIFIC_SF_CUIS:
            found.add(cui)
        elif entity == "Diagnosis" and cui in SPECIFIC_SF_CUIS:
            found.add(cui)
    return found


def _canonical_phrase(cui: str) -> str:
    phrases = SF_CUI_LEXICON.get(cui)
    return phrases[0] if phrases else cui


def _rewrite_type(mention: dict[str, Any], cui: str) -> dict[str, Any]:
    out = dict(mention)
    attrs = dict(out.get("attributes") or {})
    phrase = _canonical_phrase(cui)
    attrs["CUI"] = cui
    attrs["CUIPhrase"] = phrase
    out["attributes"] = attrs
    out["text"] = phrase
    return out


def _existing_specific_states(mentions: Sequence[Mapping[str, Any]]) -> set[str]:
    return {
        headline_state(mention)
        for mention in mentions
        if specific_sf_cui(mention) is not None
    }


def _existing_specific_keys(
    mentions: Sequence[Mapping[str, Any]],
) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    for mention in mentions:
        cui = specific_sf_cui(mention)
        if cui is None:
            continue
        keys.add((cui, headline_state(mention)))
    return keys


def apply_type_key_reconcile(
    mentions: Sequence[Mapping[str, Any]],
    *,
    arm: Arm,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Return rewritten mentions and action records. Gold and letter text unused."""

    working = [dict(mention) for mention in mentions]
    actions: list[dict[str, str]] = []
    do_drop = arm in {"drop_generic_duplicate_state", "bundle"}
    do_retarget = arm in {"retarget_generic_unique", "bundle"}

    if do_drop:
        specific_states = _existing_specific_states(working)
        kept: list[dict[str, Any]] = []
        for mention in working:
            if (
                is_generic_sf(mention)
                and headline_state(mention) in specific_states
            ):
                actions.append(
                    {
                        "action": "drop",
                        "state": headline_state(mention),
                        "from_cui": mention_cui(mention) or "none",
                    }
                )
                continue
            kept.append(mention)
        working = kept

    if do_retarget:
        candidates = candidate_specific_cuis(working)
        retargeted: list[dict[str, Any]] = []
        if len(candidates) == 1:
            target = next(iter(candidates))
            present = _existing_specific_keys(working)
            for mention in working:
                if not is_generic_sf(mention):
                    retargeted.append(mention)
                    continue
                state = headline_state(mention)
                if (target, state) in present:
                    actions.append(
                        {
                            "action": "skip_already_present",
                            "state": state,
                            "from_cui": mention_cui(mention) or "none",
                            "to_cui": target,
                        }
                    )
                    retargeted.append(mention)
                    continue
                retargeted.append(_rewrite_type(mention, target))
                present.add((target, state))
                actions.append(
                    {
                        "action": "retarget",
                        "state": state,
                        "from_cui": mention_cui(mention) or "none",
                        "to_cui": target,
                    }
                )
        else:
            retargeted = working
        working = retargeted

    return working, actions
