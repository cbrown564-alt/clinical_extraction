"""Legacy SF convention noise classifier (Stack B).

.. deprecated::
    Extracted from ``_legacy_impl``; behavior-preserving.
"""
# ruff: noqa: F405 — legacy regex constants are star-imported from ``_legacy_constants``.

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase

from ._legacy_constants import *  # noqa: F401,F403 (legacy regex constants)


def is_sf_convention_noise(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """True for SF renderings that are prompt-selection residue, not frequency facts."""

    phrase = normalize_phrase(text)
    attrs = {str(key): str(value) for key, value in attributes.items()}
    cui = attrs.get("CUI")
    if _SF_VAGUE_EPISODE_RE.fullmatch(phrase):
        return True
    if phrase in {
        "absences and jerks",
        "attacks",
        "collapses",
        "collapse episode",
        "dissociative seizures",
        "drops",
        "drop attacks",
        "events",
        "febrile seizure",
        "febrile seizures",
        "general and complex partial seizures",
        "grand mal episodes",
        "mini shakes",
        "minor seizures",
        "one of them",
        "seizure frequency",
        "seizure like episodes",
        "these",
        "staring episodes",
        "two unprovoked generalised seizures",
    }:
        return True
    if phrase == "one seizure" and _SF_RISK_COUNSELLING_RE.search(evidence):
        return True
    if phrase == "further seizures" and _SF_RISK_COUNSELLING_RE.search(evidence):
        return True
    if phrase == "previous seizures":
        return True
    if (
        cui == "C0563606"
        and "NumberOfSeizures" not in attrs
        and re.search(
            r"\b(?:absence\s+like\s+seizures\s+2014|typical\s+absences|"
            r"at\s+(?:around\s+)?the\s+age\s+of\s+8\b[^.]{0,120}\brelatively\s+infrequent|"
            r"relatively\s+infrequent\b[^.]{0,120}\bat\s+(?:around\s+)?the\s+age\s+of\s+8)\b",
            evidence,
            re.IGNORECASE,
        )
    ):
        return True
    if cui == "C0036572" and re.search(
        r"\baround\s+3\s+seizures\s+per\s+month\b",
        evidence,
        re.IGNORECASE,
    ):
        return True
    if cui == "C0877017" and re.search(
        r"\b(?:focal\s+to\s+bilateral\s+convulsive\s+seizures?\s+\d{4}|"
        r"three\s+episodes\s+whilst\s+asleep)\b",
        evidence,
        re.IGNORECASE,
    ):
        return True
    if (
        cui == "C1299590"
        and attrs.get("NumberOfSeizures") == "0"
        and _SF_CONTEXTUAL_RATE_NOISE_RE.search(evidence)
    ):
        return True
    if cui == "C1299590" and attrs.get("NumberOfSeizures") == "0":
        return False
    if phrase in {"seizure", "seizures", "seizure free", "seizure freedom"} and (
        _SF_CONTEXTUAL_RATE_NOISE_RE.search(evidence)
    ):
        return True
    if phrase in {"seizure", "seizures", "seizure free"} and _SF_CONTEXTUAL_SEIZURE_FREE_RE.search(
        evidence
    ):
        return True
    if phrase == "seizure" and _SF_HISTORICAL_COMPARATOR_RE.search(evidence):
        return True
    return False


def _sf_number(value: str) -> str:
    return _SF_SMALL_NUMBERS.get(value.lower(), value)


__all__ = [
    "is_sf_convention_noise",
    "_sf_number",
]
