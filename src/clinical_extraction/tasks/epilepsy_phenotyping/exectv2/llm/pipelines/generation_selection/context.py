"""Runtime context passed to generation-selection strategy handlers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.generation_selection.types import (
    PromptProfile,
)


@dataclass(frozen=True)
class StrategyPrograms:
    """DSPy program instances shared across letters in one run_split batch."""

    two_stage: Any
    inventory: Any
    mention: Any
    mention_id: Any
    dedup_facts: Any
    pool: Any


@dataclass(frozen=True)
class StrategyContext:
    """Per-letter inputs for a registered call-strategy handler."""

    letter: ExectLetter
    mode: Literal["live", "prompt-only"]
    prompt_profile: PromptProfile
    programs: StrategyPrograms
    split: str
    model: str
    pool_mentions_by_letter: Mapping[str, Sequence[Mapping[str, Any]]] | None = None


@dataclass(frozen=True)
class StrategyOutcome:
    """Unified return surface from any call-strategy handler."""

    generation_prompt_input_json: str
    selection_prompt_input_json: str
    raw_generation_output: str
    raw_selection_output: str
    generation_call_error: str | None
    selection_call_error: str | None
    generation_parse_errors: list[str]
    selection_parse_errors: list[str]
    first_pass_record: Any
    final_record: Any
    inventory_details: dict[str, Any]
    row: dict[str, Any]
