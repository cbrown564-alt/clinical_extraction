"""Investigations lens for ExECTv2 assembly."""

from __future__ import annotations

from .base import InvestigationsLens, ThinArtifactLens


class InvestigationsDictionaryLens(ThinArtifactLens):
    """Behavior-preserving adapter retained after the v10 no-op cleanup.

    Investigation residual providers remain available to prompt construction in
    ``prompt_content.py``. They are intentionally not consumed by this
    assembly-side lens because the predeclared dev140/test59 study found zero
    score movement for all three former lens rules.
    """

    pass


__all__ = [
    "InvestigationsDictionaryLens",
    "InvestigationsLens",
]
