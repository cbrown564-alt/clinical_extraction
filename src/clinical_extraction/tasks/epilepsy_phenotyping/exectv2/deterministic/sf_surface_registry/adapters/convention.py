"""Convention-phase adapter — catalog-driven Stack B facade."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..builders.registry import apply_noise, apply_rewrite, residual_candidates


def apply_rewrite_adapter(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    """Registry-backed rewrite facade."""

    return apply_rewrite(text, evidence=evidence, attributes=attributes)


def is_noise_adapter(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> bool:
    """Registry-backed noise filter facade."""

    return apply_noise(text, evidence=evidence, attributes=attributes)


def residual_candidates_adapter(note_text: str) -> list[tuple[str, str, dict[str, str]]]:
    """Registry-backed residual-add facade."""

    return residual_candidates(note_text)
