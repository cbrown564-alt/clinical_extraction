"""Run a frozen Gan condition, selecting Responses transport for GPT-5.6 Sol."""

from __future__ import annotations

import argparse
import sys
from typing import Any

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026 import llm_config
from clinical_extraction.tasks.seizure_frequency.gan2026.cli import llm_pipeline_cli
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events

SOL_MODEL = "openai/gpt-5.6-sol"
FROZEN_PROMPT_VERSION = hybrid_structured_events.PROMPT_VERSION_V0_7
_RETAINED_BUILD_DSPY_LM = llm_config.build_dspy_lm


def build_hosted_lm(
    model: str,
    *,
    temperature: float,
    max_tokens: int,
    cache: bool,
    api_base: str | None = None,
    num_retries: int = 2,
    timeout: int | None = None,
) -> dspy.LM:
    """Preserve retained routing except for Sol's required Responses transport."""

    if model != SOL_MODEL:
        return _RETAINED_BUILD_DSPY_LM(
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
        "max_tokens": max_tokens,
        "cache": cache,
        "num_retries": num_retries,
    }
    if api_base:
        kwargs["api_base"] = api_base
    if timeout is not None:
        kwargs["timeout"] = timeout
    return dspy.LM(model, **kwargs)


def main(argv: list[str] | None = None) -> None:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--prompt-version", required=True)
    prompt_args, remaining = parser.parse_known_args(raw_argv)
    if prompt_args.prompt_version != FROZEN_PROMPT_VERSION:
        parser.error(
            "hosted Gan conditions require prompt "
            f"{FROZEN_PROMPT_VERSION!r}; got {prompt_args.prompt_version!r}"
        )
    hybrid_structured_events.set_active_prompt_version(prompt_args.prompt_version)
    llm_config.build_dspy_lm = build_hosted_lm
    llm_pipeline_cli.main(remaining)


if __name__ == "__main__":
    main()
