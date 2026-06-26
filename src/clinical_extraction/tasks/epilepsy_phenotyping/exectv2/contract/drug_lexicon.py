"""Shared drug and prescription surface alias table for ExECTv2.

Single source for typo/brand mappings consumed by benchmark projection,
scoring medication canonicalization, and deterministic prescription repair.
Keys are normalized phrase forms (lowercase, spaces, no hyphens).
"""

from __future__ import annotations

import re

_QUOTES = str.maketrans("", "", "\"'“”‘’‚‛")
_WHITESPACE = re.compile(r"\s+")


def _normalize_phrase(text: str) -> str:
    lowered = text.translate(_QUOTES).replace("-", " ").lower()
    return _WHITESPACE.sub(" ", lowered).strip()


#: Surface spellings that map to a known generic before benchmark/CUI lookup.
DRUG_SURFACE_ALIASES: dict[str, str] = {
    "brivetiracetam": "brivaracetam",
    "brivitiracetam": "brivaracetam",
    "buccal midazolam": "midazolam",
    "carbamazapine": "carbamazepine",
    "carbmazapine": "carbamazepine",
    "epilim": "sodium valproate",
    "epilim chrono": "sodium valproate",
    "epilpim chrono": "sodium valproate",
    "epilpim chrono (sodium valproate)": "sodium valproate",
    "episenta": "sodium valproate",
    "eplim": "sodium valproate",
    "eplim chrono": "sodium valproate",
    "eslicarbazepineacetate": "eslicarbazepine",
    "keppra": "levetiracetam",
    "lamictal": "lamotrigine",
    "lamtorigine": "lamotrigine",
    "phenobarbitone": "phenobarbital",
    "sodiumvalproate": "sodium valproate",
    "tegretaol": "carbamazepine",
    "tegretol": "carbamazepine",
    "tegretol retard": "carbamazepine",
    "zobisamide": "zonisamide",
    "zonismaide": "zonisamide",
}


def resolve_drug_surface(surface: str) -> str:
    """Return the canonical generic surface for a drug mention, if aliased."""

    key = _normalize_phrase(surface)
    return DRUG_SURFACE_ALIASES.get(key, key)


def canonicalize_medication_name(value: str) -> str:
    """Normalize medication spelling/brand variants for clinical component scoring."""

    return resolve_drug_surface(value).replace(" ", "-")
