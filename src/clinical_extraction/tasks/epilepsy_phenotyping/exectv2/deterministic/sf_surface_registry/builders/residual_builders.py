"""Catalog-backed residual-add builders."""

from __future__ import annotations

from .context import ResidualCandidate
from . import _legacy_impl as legacy
from .registry import register_builder


@register_builder("residual_all_patterns")
def residual_all_patterns(note_text: str) -> list[ResidualCandidate]:
    return legacy.sf_residual_additions(note_text)

