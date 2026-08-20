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
    "gan_llm_pre_post": {
        "task": "gan2026",
        "splits": ("dev750", "test450"),
        "prompt_attr": "GAN_LLM_PRE_POST",
    },
    "exect_llm_with_rules": {
        "task": "exectv2",
        "splits": ("dev140", "test60"),
        "prompt_attr": "COMPACT_LEDGER",
    },
    "exect_llm_only": {
        "task": "exectv2",
        "splits": ("dev140", "test60"),
        "prompt_attr": "EXECT_LLM_ONLY",
    },
    "exect_full_ledger": {
        "task": "exectv2",
        "splits": ("dev140", "test60"),
        "prompt_attr": "FULL_LEDGER",
    },
}

HOLDOUT_SPLITS = frozenset({"test450", "test60"})
GAN_MACHINE_SPLITS = {"dev750": "validation", "test450": "test"}
GAN_ROW_COUNTS = {"dev750": 750, "test450": 450}
EXECT_MACHINE_SPLITS = {"dev140": "dev", "test60": "test"}
EXECT_ROW_COUNTS = {"dev140": 140, "test60": 59}


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


def gan_machine_split(split: str) -> str:
    """Map a paper Gan split to the gan2026_split_v1 machine name."""

    try:
        return GAN_MACHINE_SPLITS[split]
    except KeyError as exc:
        raise ValueError(f"unsupported Gan paper split {split!r}") from exc


def gan_row_count(split: str) -> int:
    """Return the locked Gan paper split size."""

    try:
        return GAN_ROW_COUNTS[split]
    except KeyError as exc:
        raise ValueError(f"unsupported Gan paper split {split!r}") from exc


def exect_row_count(split: str) -> int:
    """Return the locked ExECT paper split size."""

    try:
        return EXECT_ROW_COUNTS[split]
    except KeyError as exc:
        raise ValueError(f"unsupported ExECT paper split {split!r}") from exc
