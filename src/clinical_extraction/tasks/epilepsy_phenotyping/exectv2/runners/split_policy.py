"""Split authorization for ExECT development runners."""

from __future__ import annotations

LOCKED_SPLIT_ALIASES = frozenset(
    {
        "test",
        "test60",
        "holdout",
        "locked_test",
        "locked-test",
        "aggregate_only",
        "aggregate-only",
    }
)


def is_locked_split(split: str) -> bool:
    """Return whether a caller supplied a governed locked/aggregate alias."""

    return split.strip().casefold() in LOCKED_SPLIT_ALIASES
