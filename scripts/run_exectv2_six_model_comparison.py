"""Run one frozen decision-0040 six-model ExECTv2 condition.

The retained runner uses DSPy's chat transport. GPT-5.6 Sol is available to the
configured account only through OpenAI's Responses API, so this wrapper changes
that transport alone. Prompts, parsing, family ownership, deterministic work,
scoring, checkpointing, and artifact assembly remain owned by the retained
runner.
"""

from __future__ import annotations

from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    diagnosis_decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured import (  # noqa: E501
    runner as structured_runner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
    build_dspy_lm as retained_build_dspy_lm,
)
from scripts import run_exectv2_2call_model_swap as retained_runner

SOL_MODEL = "openai/gpt-5.6-sol"


def build_six_model_lm(
    model: str,
    *,
    temperature: float,
    max_tokens: int,
    cache: bool,
    api_base: str | None = None,
    num_retries: int = 2,
    timeout: int | None = None,
) -> dspy.LM:
    """Select the Responses transport for Sol and retain all other routes."""

    if model != SOL_MODEL:
        return retained_build_dspy_lm(
            model,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=cache,
            api_base=api_base,
            num_retries=num_retries,
            timeout=timeout,
        )
    kwargs: dict[str, Any] = {
        "model_type": "responses",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "cache": cache,
        "num_retries": num_retries,
    }
    if api_base:
        kwargs["api_base"] = api_base
    if timeout is not None:
        kwargs["timeout"] = timeout
    return dspy.LM(model, **kwargs)


def main() -> None:
    structured_runner.build_dspy_lm = build_six_model_lm
    diagnosis_decomposer.build_dspy_lm = build_six_model_lm
    retained_runner.main()


if __name__ == "__main__":
    main()
