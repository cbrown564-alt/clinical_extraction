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
#: Keys are already in ``_normalize_phrase`` form (lowercase, single-spaced,
#: hyphens dropped). Values are the canonical generic *surface* (space form; the
#: trailing ``.replace(" ", "-")`` in ``canonicalize_medication_name`` hyphenates).
DRUG_SURFACE_ALIASES: dict[str, str] = {
    "brivetiracetam": "brivaracetam",
    "brivitiracetam": "brivaracetam",
    "briviact": "brivaracetam",
    "buccal midazolam": "midazolam",
    "buccolam": "midazolam",
    "carbamazapine": "carbamazepine",
    "carbmazapine": "carbamazepine",
    "epilim": "sodium valproate",
    "epilim chrono": "sodium valproate",
    "epilpim chrono": "sodium valproate",
    "epilpim chrono (sodium valproate)": "sodium valproate",
    "episenta": "sodium valproate",
    "eplim": "sodium valproate",
    "eplim chrono": "sodium valproate",
    "eslicarbazepine acetate": "eslicarbazepine",
    "eslicarbazepineacetate": "eslicarbazepine",
    "frisium": "clobazam",
    "keppra": "levetiracetam",
    "lamictal": "lamotrigine",
    "lamtorigine": "lamotrigine",
    "lyrica": "pregabalin",
    "neurontin": "gabapentin",
    "phenobarbitone": "phenobarbital",
    "sodiumvalproate": "sodium valproate",
    "tegretaol": "carbamazepine",
    "tegretol": "carbamazepine",
    "tegretol retard": "carbamazepine",
    "topamax": "topiramate",
    "trileptal": "oxcarbazepine",
    "valproate": "sodium valproate",
    "valproate semisodium": "sodium valproate",
    "valproic acid": "sodium valproate",
    "vimpat": "lacosamide",
    "zobisamide": "zonisamide",
    "zonismaide": "zonisamide",
}


#: External antiseizure-medication dictionary (2026-08-27 restructure,
#: Phase B). Generic names absent from the benchmark surface list, used by
#: the recall-first prescription recogniser. Curated from the standard UK
#: ASM formulary, not from any benchmark letter.
EXTERNAL_ASM_GENERICS: tuple[str, ...] = (
    "acetazolamide",
    "cannabidiol",
    "cenobamate",
    "clonazepam",
    "diazepam",
    "ethosuximide",
    "felbamate",
    "fenfluramine",
    "lorazepam",
    "paraldehyde",
    "primidone",
    "rufinamide",
    "stiripentol",
    "sulthiame",
    "tiagabine",
    "vigabatrin",
)

#: UK brand names mapping to their generic (normalized-phrase keys, like
#: ``DRUG_SURFACE_ALIASES``).
EXTERNAL_ASM_BRAND_ALIASES: dict[str, str] = {
    "diacomit": "stiripentol",
    "diamox": "acetazolamide",
    "emeside": "ethosuximide",
    "epanutin": "phenytoin",
    "epidyolex": "cannabidiol",
    "fintepla": "fenfluramine",
    "fycompa": "perampanel",
    "inovelon": "rufinamide",
    "mysoline": "primidone",
    "ontozry": "cenobamate",
    "ospolot": "sulthiame",
    "rivotril": "clonazepam",
    "sabril": "vigabatrin",
    "zarontin": "ethosuximide",
    "zebinix": "eslicarbazepine",
    "zonegran": "zonisamide",
}


def resolve_drug_surface(surface: str) -> str:
    """Return the canonical generic surface for a drug mention, if aliased."""

    key = _normalize_phrase(surface)
    return DRUG_SURFACE_ALIASES.get(key, key)


def canonicalize_medication_name(value: str) -> str:
    """Normalize medication spelling/brand variants for clinical component scoring."""

    return resolve_drug_surface(value).replace(" ", "-")
