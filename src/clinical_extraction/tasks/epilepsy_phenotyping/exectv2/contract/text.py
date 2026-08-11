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
    lowered = lowered.replace("generalized", "generalised")
    lowered = lowered.replace("cluster of ", " ").replace("clusters of ", " ")
    lowered = lowered.replace(" without change in awareness", "").replace(
        " without changes in awareness", ""
    )
    normalized = _WHITESPACE.sub(" ", lowered).strip()
    words = normalized.split()
    if words:
        if words[-1] in ("seizures", "absences", "jerks", "convulsions", "attacks", "episodes"):
            words[-1] = words[-1].rstrip("s")
        normalized = " ".join(words)
    return normalized
