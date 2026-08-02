"""CLI dispatch specifications for selected ExECTv2 methods."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .runners import RULES_METHOD_ALIASES, split


@dataclass(frozen=True)
class ExectCliSpec:
    """Small method specification shared by command-line callers."""

    description: str
    run_split: Callable[..., tuple[list[dict[str, Any]], dict[str, Any]]]


def get_cli_specs() -> dict[str, ExectCliSpec]:
    """Return the active rules CLI and its exact legacy method aliases."""

    def run_rules(letters, **kwargs):
        return split.run_split(letters, method="rules", **kwargs)

    spec = ExectCliSpec("Run the ExECT deterministic rules method.", run_rules)
    return {
        name: spec for name in RULES_METHOD_ALIASES
    }


__all__ = ["ExectCliSpec", "get_cli_specs"]
