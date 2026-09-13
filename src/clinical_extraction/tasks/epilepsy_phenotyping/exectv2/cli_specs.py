"""CLI dispatch specifications for selected ExECTv2 methods."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .runners import (
    split,
)


@dataclass(frozen=True)
class ExectCliSpec:
    """Small method specification shared by command-line callers."""

    description: str
    run_split: Callable[..., tuple[list[dict[str, Any]], dict[str, Any]]]


def get_cli_specs() -> dict[str, ExectCliSpec]:
    """Return the canonical names accepted for new benchmark execution."""

    def run_rules(letters, **kwargs):
        return split.run_split(letters, method="rules", **kwargs)

    spec = ExectCliSpec("Run the ExECT deterministic rules method.", run_rules)

    def run_llm(letters, **kwargs):
        return split.run_split(letters, method="llm", **kwargs)

    llm_spec = ExectCliSpec("Run the ExECT LLM-only method.", run_llm)

    def run_llm_with_rules(letters, **kwargs):
        return split.run_split(letters, method="llm_with_rules", **kwargs)

    hybrid_spec = ExectCliSpec("Run the ExECT LLM-with-rules method.", run_llm_with_rules)
    return {
        "rules": spec,
        "llm": llm_spec,
        "llm_with_rules": hybrid_spec,
    }


__all__ = ["ExectCliSpec", "get_cli_specs"]
