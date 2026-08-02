"""Split authorization for ExECT row-inspectable development runners."""

from __future__ import annotations

DEVELOPMENT_SPLIT_ALIASES = frozenset({"dev", "dev140"})


def is_development_split(split: str) -> bool:
    """Return whether ``split`` is an explicitly row-inspectable alias."""

    return split.strip().casefold() in DEVELOPMENT_SPLIT_ALIASES


def require_development_split(split: str) -> None:
    """Reject every split not explicitly allowlisted for row inspection."""

    if not is_development_split(split):
        raise ValueError(
            "ExECT split is not an inspectable development split: "
            f"{split!r}"
        )
