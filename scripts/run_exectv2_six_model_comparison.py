"""Run one frozen decision-0041 single-call six-model ExECTv2 condition.

The retained runner uses DSPy's chat transport. GPT-5.6 Sol is available to the
configured account only through OpenAI's Responses API, so this wrapper changes
that transport alone. Prompts, parsing, family ownership, deterministic work,
scoring, checkpointing, and artifact assembly remain owned by the retained
runner.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured import (  # noqa: E501
    runner as structured_runner,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
    build_dspy_lm as retained_build_dspy_lm,
)
from scripts import run_exectv2_2call_model_swap as retained_runner

SOL_MODEL = "openai/gpt-5.6-sol"
SOL_REQUEST_TIMEOUT_SECONDS = 300
OLLAMA_NUM_CTX_ENV = "CLINICAL_EXTRACTION_OLLAMA_NUM_CTX"


def configure_declared_runtime(config_path: Path) -> None:
    """Make frozen local runtime metadata effective before constructing the LM."""

    payload = json.loads(config_path.read_text(encoding="utf-8"))
    model = str(payload["model"])
    if not model.startswith("ollama_chat/"):
        return
    runtime_metadata = payload.get("runtime_metadata", {})
    if "num_ctx" not in runtime_metadata:
        raise ValueError(f"local config has no declared num_ctx: {config_path}")
    declared = str(int(runtime_metadata["num_ctx"]))
    existing = os.environ.get(OLLAMA_NUM_CTX_ENV)
    if existing is not None and existing != declared:
        raise ValueError(
            f"{OLLAMA_NUM_CTX_ENV}={existing} conflicts with declared num_ctx={declared}"
        )
    os.environ[OLLAMA_NUM_CTX_ENV] = declared


def _config_path_from_argv(argv: list[str]) -> Path:
    try:
        return Path(argv[argv.index("--config") + 1])
    except (ValueError, IndexError) as exc:
        raise SystemExit("--config is required") from exc


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
    kwargs["timeout"] = timeout if timeout is not None else SOL_REQUEST_TIMEOUT_SECONDS
    return dspy.LM(model, **kwargs)


def main() -> None:
    configure_declared_runtime(_config_path_from_argv(sys.argv[1:]))
    structured_runner.build_dspy_lm = build_six_model_lm
    retained_runner.main()


if __name__ == "__main__":
    main()
