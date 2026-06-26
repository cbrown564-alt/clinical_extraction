from __future__ import annotations

import re

_QUOTES = str.maketrans("", "", "\"'“”‘’‚‛")
_WHITESPACE = re.compile(r"\s+")
_LOWERCASE_ATTRIBUTE_VALUES: frozenset[str] = frozenset({"DrugName", "DoseUnit"})


def normalize_phrase(text: str) -> str:
    """Normalize an annotated phrase for label matching.

    Gold phrases store spaces as hyphens and sometimes carry quotes (including
    mid-phrase) and case variation. Normalization makes phrase comparison robust
    to those surface differences without relying on (drifted) character offsets."""

    lowered = text.translate(_QUOTES).replace("-", " ").lower()
    return _WHITESPACE.sub(" ", lowered).strip()


def canonicalize_attribute_value(key: str, value: str) -> str:
    """Apply format-only canonicalization before attribute matching.

    This deliberately cannot create a missing attribute or infer a clinical
    category. It only removes quote/whitespace noise and normalizes attributes
    where case is a spelling artifact under the ExECTv2 contract.
    """

    normalized = _WHITESPACE.sub(" ", str(value).translate(_QUOTES)).strip()
    if key in _LOWERCASE_ATTRIBUTE_VALUES:
        normalized = normalized.lower()
    return normalized
