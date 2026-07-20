"""Shared text normalization for ExECTv2 contracts, scoring, and projection."""

from __future__ import annotations

import re

_QUOTES = str.maketrans("", "", "\"'“”‘’‚‛")
_WHITESPACE = re.compile(r"\s+")


def normalize_phrase(text: str) -> str:
    """Normalize an annotated phrase for label matching.

    Gold phrases store spaces as hyphens and sometimes carry quotes (including
    mid-phrase) and case variation. Normalization makes phrase comparison robust
    to those surface differences without relying on (drifted) character offsets."""

    lowered = text.translate(_QUOTES).replace("-", " ").lower()
    return _WHITESPACE.sub(" ", lowered).strip()
