"""Prompt builders for the structured-event extractor."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from .constants import (
    COMPACT_VERSIONS,
    LLM_ONLY_VERSIONS,
    prompt_version_for,
)
from .prompt_compact import (
    build_compact_llm_only_prompt_input,
    build_compact_prompt_input,
)


def build_prompt_input(
    letter: ExectLetter,
    *,
    prompt_version: str | None = None,
) -> str:
    """Build the Compact structured-event payload."""

    selected = prompt_version_for(prompt_version=prompt_version)
    if selected in LLM_ONLY_VERSIONS:
        return build_compact_llm_only_prompt_input(letter)
    if selected in COMPACT_VERSIONS:
        return build_compact_prompt_input(letter)
    raise ValueError(f"unsupported Compact prompt version {selected!r}")


__all__ = ["build_prompt_input"]
