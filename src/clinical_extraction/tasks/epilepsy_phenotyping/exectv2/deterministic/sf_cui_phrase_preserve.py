"""Keep a type the model already wrote when assigning an SF CUI."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    GENERIC_SEIZURE_CUI,
    assign_cui,
)

CLUSTER_CUI = "C3203523"
CLUSTER_PHRASE = "cluster of seizures"
CLUSTER_RE = re.compile(r"\bclusters?\s+of\s+seizures?\b", re.I)
GENERIC_OR_EMPTY = frozenset({"", GENERIC_SEIZURE_CUI})
GENERLISED_RE = re.compile(r"generlised", re.I)
Arm = Literal["preserve_cluster_cui", "fold_generlised_cui", "bundle"]
ARMS: tuple[Arm, ...] = (
    "preserve_cluster_cui",
    "fold_generlised_cui",
    "bundle",
)


def mention_cui(mention: Mapping[str, Any]) -> str:
    return str((mention.get("attributes") or {}).get("CUI") or "")


def _set_cui(mention: Mapping[str, Any], cui: str, phrase: str) -> dict[str, Any]:
    out = dict(mention)
    attrs = dict(out.get("attributes") or {})
    attrs["CUI"] = cui
    attrs["CUIPhrase"] = phrase
    out["attributes"] = attrs
    return out


def _cluster_hit(mention: Mapping[str, Any]) -> bool:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return False
    text = str(mention.get("text") or "")
    return bool(CLUSTER_RE.search(text)) and mention_cui(mention) in GENERIC_OR_EMPTY


def _generlised_cui(mention: Mapping[str, Any]) -> str | None:
    if str(mention.get("entity") or "") != "SeizureFrequency":
        return None
    if mention_cui(mention):
        return None
    text = str(mention.get("text") or "")
    if not GENERLISED_RE.search(text):
        return None
    folded = GENERLISED_RE.sub("generalised", text)
    return assign_cui(folded)


def apply_cui_phrase_preserve(
    mentions: Sequence[Mapping[str, Any]],
    *,
    arm: Arm,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    do_cluster = arm in {"preserve_cluster_cui", "bundle"}
    do_typo = arm in {"fold_generlised_cui", "bundle"}
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for mention in mentions:
        out = dict(mention)
        if do_cluster and _cluster_hit(out):
            out = _set_cui(out, CLUSTER_CUI, CLUSTER_PHRASE)
            actions.append(
                {
                    "action": "preserve_cluster_cui",
                    "text": str(mention.get("text") or ""),
                }
            )
        if do_typo:
            cui = _generlised_cui(out)
            if cui:
                out = _set_cui(out, cui, str(out.get("text") or ""))
                actions.append(
                    {
                        "action": "fold_generlised_cui",
                        "text": str(mention.get("text") or ""),
                        "cui": cui,
                    }
                )
        kept.append(out)
    return kept, actions
