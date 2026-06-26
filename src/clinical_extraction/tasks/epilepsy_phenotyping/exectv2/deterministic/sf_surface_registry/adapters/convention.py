"""Convention-phase adapter — Phase 0 delegates to legacy Stack B."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def apply_rewrite(
    text: str,
    *,
    evidence: str,
    attributes: Mapping[str, Any],
) -> tuple[str, dict[str, Any], str] | None:
    """Registry-backed rewrite facade (shadow-read delegates to Stack B)."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.standard_dictionary import (
        sf_convention_rewrite,
    )

    return sf_convention_rewrite(text, evidence=evidence, attributes=attributes)
