"""Shared Gan 2026 pipeline runner configuration types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
)

PipelineArchitecture = Literal[
    "deterministic_canonical_pipeline",
    "hybrid_structured_events",
    "llm_only_canonical_pipeline",
]

# The retained matrix has exactly one architecture per family.
ARCHITECTURE_FAMILY: dict[str, str] = {
    "deterministic_canonical_pipeline": "deterministic",
    "hybrid_structured_events": "hybrid",
    "llm_only_canonical_pipeline": "fully_llm",
}


class PipelineConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    architecture: PipelineArchitecture
    ablation_config: AblationConfig = AblationConfig()
    dspy_cache: bool = True
    model: str = "openai/gpt-4.1-mini"
    temperature: float = 0.0
    max_tokens: int = 900


@dataclass(frozen=True)
class PipelineOutputArtifact:
    projection_render_rows: list[dict[str, Any]]
    score_rows: list[dict[str, Any]]
    route_rows: list[dict[str, Any]]
    decision_rows: list[dict[str, Any]]
    metadata: dict[str, Any]
