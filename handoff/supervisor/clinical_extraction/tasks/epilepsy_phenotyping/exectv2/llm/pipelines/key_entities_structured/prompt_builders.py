"""Full and qwen_compact prompt builders for the structured-event extractor."""

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from .constants import (
    PromptProfile,
)
from .prompt_builders_full import (
    build_full_prompt_input,
)
from .prompt_builders_qwen_compact import (
    _build_qwen_compact_prompt_input,
)


def build_prompt_input(
    letter: ExectLetter,
    *,
    prompt_profile: PromptProfile = "full",
    prompt_version: str | None = None,
) -> str:
    """Build the single-prompt structured-event payload."""

    if prompt_profile == "qwen_compact":
        return _build_qwen_compact_prompt_input(letter)
    return build_full_prompt_input(
        letter,
        prompt_profile=prompt_profile,
        prompt_version=prompt_version,
    )


__all__ = ["build_prompt_input", "_build_qwen_compact_prompt_input"]
