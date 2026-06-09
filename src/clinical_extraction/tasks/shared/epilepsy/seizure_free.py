from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class SeizureFreeAssertion:
    """Epilepsy-general representation of a seizure-free assertion.

    Usable by both Gan 2026 and ExECTv2 without depending on either task's
    internal machinery. ``duration_months`` is None when the duration is
    indeterminate (e.g. "multiple year" or no explicit period stated).
    """

    source_text: str
    duration_months: float | None
    evidence: str


def is_zero_count_mention(attributes: Mapping[str, str]) -> bool:
    """Whether an attribute map represents a seizure-free assertion via a zero count.

    In ExECTv2, annotators encode seizure-free observations as SeizureFrequency
    mentions with ``NumberOfSeizures="0"`` rather than a positive count.
    """
    return attributes.get("NumberOfSeizures") == "0"
