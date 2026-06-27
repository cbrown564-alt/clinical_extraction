from __future__ import annotations

import re

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)

_LOWERCASE_ATTRIBUTE_VALUES: frozenset[str] = frozenset({"DrugName", "DoseUnit"})
_QUOTES = str.maketrans("", "", "\"'“”‘’‚‛")
_WHITESPACE = re.compile(r"\s+")


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


__all__ = ["canonicalize_attribute_value", "normalize_phrase"]
