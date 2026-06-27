"""DSPy LM configuration for Gan 2026 pipeline runners."""

from __future__ import annotations


def configure_lm(
    *,
    model: str,
    temperature: float,
    max_tokens: int,
    dspy_cache: bool,
) -> None:
    import dspy

    from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
        build_dspy_lm,
    )

    lm = build_dspy_lm(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache=dspy_cache,
    )
    dspy.configure(lm=lm)
