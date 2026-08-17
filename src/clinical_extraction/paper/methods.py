"""Methods the paper runner may execute."""

from __future__ import annotations

from typing import Literal

TaskName = Literal["gan2026", "exectv2"]
SplitName = Literal["dev750", "test450", "dev140", "test60"]

LIVE_METHODS: dict[str, dict[str, object]] = {
    "gan_llm_only": {
        "task": "gan2026",
        "splits": ("dev750", "test450"),
        "prompt_attr": "GAN_LLM_ONLY",
    },
    "gan_llm_with_rules": {
        "task": "gan2026",
        "splits": ("dev750", "test450"),
        "prompt_attr": "GAN_LLM_WITH_RULES",
    },
    "exect_llm_with_rules": {
        "task": "exectv2",
        "splits": ("dev140", "test60"),
        "prompt_attr": "COMPACT_LEDGER",
    },
}

HOLDOUT_SPLITS = frozenset({"test450", "test60"})


def method_spec(method: str) -> dict[str, object]:
    """Return the locked paper method, or raise."""

    try:
        return LIVE_METHODS[method]
    except KeyError as exc:
        raise ValueError(
            f"unsupported paper method {method!r}; "
            f"expected one of {sorted(LIVE_METHODS)}"
        ) from exc


def split_for(method: str, split: str) -> str:
    """Accept only the splits that belong to this paper method."""

    spec = method_spec(method)
    allowed = spec["splits"]
    assert isinstance(allowed, tuple)
    if split not in allowed:
        raise ValueError(
            f"{method} does not use split {split!r}; expected one of {allowed}"
        )
    return split


def holdout_is_aggregate_only(split: str) -> bool:
    """Locked test splits are aggregate-only."""

    return split in HOLDOUT_SPLITS
