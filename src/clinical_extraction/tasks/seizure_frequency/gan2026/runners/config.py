"""Shared Gan 2026 pipeline runner configuration types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
)

PipelineArchitecture = Literal[
    "deterministic",
    "deterministic_canonical_pipeline",
    "hybrid",
    "llm_only_direct_labeler",
    "hybrid_structured_events",
    "llm_only_canonical_pipeline",
]

# Architecture family groupings (for reporting and taxonomy).
# Two hybrid configs share deterministic downstream stages (normalize/project/render/score)
# but differ in their LLM task. Contrast with "fully_llm" configs (direct_labeler,
# canonical_pipeline) that
# own the full extraction-to-label pass in one LLM call with no deterministic
# normalization stage. The two hybrids differ in their LLM task:
#   - hybrid_structured_events: LLM extracts structured events (open-text → schema)
#   - hybrid: LLM assesses a pre-extracted deterministic candidate set
ARCHITECTURE_FAMILY: dict[str, str] = {
    "deterministic": "deterministic",
    "deterministic_canonical_pipeline": "deterministic",
    "hybrid": "hybrid",
    "llm_only_direct_labeler": "fully_llm",
    "hybrid_structured_events": "hybrid",
    "llm_only_canonical_pipeline": "fully_llm",
}


class PipelineConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    architecture: PipelineArchitecture
    ablation_config: AblationConfig = AblationConfig()
    use_state_graph_extract: bool = False
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
