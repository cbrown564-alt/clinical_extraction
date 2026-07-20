"""Load canonical SF surface regex patterns from patterns.yaml."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from re import Pattern

import yaml

_PATTERNS_PATH = Path(__file__).resolve().parent / "patterns.yaml"
_FLAG_MAP = {"IGNORECASE": re.IGNORECASE, "DOTALL": re.DOTALL, "MULTILINE": re.MULTILINE}


@lru_cache(maxsize=1)
def load_pattern_registry() -> dict[str, Pattern[str]]:
    payload = yaml.safe_load(_PATTERNS_PATH.read_text(encoding="utf-8")) or {}
    compiled: dict[str, Pattern[str]] = {}
    for name, spec in (payload.get("patterns") or {}).items():
        compiled[name] = _compile_pattern(str(spec["pattern"]), list(spec.get("flags") or []))
    return compiled


@lru_cache(maxsize=1)
def load_pattern_fragments() -> dict[str, str]:
    payload = yaml.safe_load(_PATTERNS_PATH.read_text(encoding="utf-8")) or {}
    return {str(key): str(value) for key, value in (payload.get("fragments") or {}).items()}


def _compile_pattern(source: str, flags: list[str]) -> Pattern[str]:
    flag_value = 0
    for flag in flags:
        flag_value |= _FLAG_MAP.get(flag, 0)
    return re.compile(source, flag_value)


def get_pattern(name: str) -> Pattern[str]:
    try:
        return load_pattern_registry()[name]
    except KeyError as exc:
        raise KeyError(f"Unknown SF surface pattern: {name!r}") from exc


def get_fragment(name: str) -> str:
    try:
        return load_pattern_fragments()[name]
    except KeyError as exc:
        raise KeyError(f"Unknown SF surface fragment: {name!r}") from exc


def pattern_names() -> tuple[str, ...]:
    return tuple(sorted(load_pattern_registry()))


def _bind_exports() -> dict[str, Pattern[str] | str]:
    registry = load_pattern_registry()
    fragments = load_pattern_fragments()
    return {
        "EVERY_N_TO_M_PERIODS": registry["EVERY_N_TO_M_PERIODS"],
        "SEIZURES_EVERY_RANGE_WEEKS": registry["SEIZURES_EVERY_RANGE_WEEKS"],
        "NO_FURTHER_SINCE": registry["NO_FURTHER_SINCE"],
        "CONTEXTUAL_RATE_NOISE": registry["CONTEXTUAL_RATE_NOISE"],
        "NO_FURTHER_GTC_SINCE": registry["NO_FURTHER_GTC_SINCE"],
        "GTC_RANGE_PER_WEEK": registry["GTC_RANGE_PER_WEEK"],
        "DATED_GTC": registry["DATED_GTC"],
        "GTCS_ACTIVE_WITHOUT_COUNT": registry["GTCS_ACTIVE_WITHOUT_COUNT"],
        "GTC_FURTHER_SINCE": registry["GTC_FURTHER_SINCE"],
        "GTC_FOUR_LAST_THREE_WEEKS": registry["GTC_FOUR_LAST_THREE_WEEKS"],
        "GTC_PER_MONTH": registry["GTC_PER_MONTH"],
        "PERIOD_UNIT": fragments["PERIOD_UNIT"],
    }


_exports = _bind_exports()
EVERY_N_TO_M_PERIODS = _exports["EVERY_N_TO_M_PERIODS"]
SEIZURES_EVERY_RANGE_WEEKS = _exports["SEIZURES_EVERY_RANGE_WEEKS"]
NO_FURTHER_SINCE = _exports["NO_FURTHER_SINCE"]
CONTEXTUAL_RATE_NOISE = _exports["CONTEXTUAL_RATE_NOISE"]
NO_FURTHER_GTC_SINCE = _exports["NO_FURTHER_GTC_SINCE"]
GTC_RANGE_PER_WEEK = _exports["GTC_RANGE_PER_WEEK"]
DATED_GTC = _exports["DATED_GTC"]
GTCS_ACTIVE_WITHOUT_COUNT = _exports["GTCS_ACTIVE_WITHOUT_COUNT"]
GTC_FURTHER_SINCE = _exports["GTC_FURTHER_SINCE"]
GTC_FOUR_LAST_THREE_WEEKS = _exports["GTC_FOUR_LAST_THREE_WEEKS"]
GTC_PER_MONTH = _exports["GTC_PER_MONTH"]
PERIOD_UNIT = _exports["PERIOD_UNIT"]

__all__ = [
    "CONTEXTUAL_RATE_NOISE",
    "DATED_GTC",
    "EVERY_N_TO_M_PERIODS",
    "GTC_FOUR_LAST_THREE_WEEKS",
    "GTC_FURTHER_SINCE",
    "GTC_PER_MONTH",
    "GTC_RANGE_PER_WEEK",
    "GTCS_ACTIVE_WITHOUT_COUNT",
    "NO_FURTHER_GTC_SINCE",
    "NO_FURTHER_SINCE",
    "PERIOD_UNIT",
    "SEIZURES_EVERY_RANGE_WEEKS",
    "get_fragment",
    "get_pattern",
    "load_pattern_fragments",
    "load_pattern_registry",
    "pattern_names",
]
