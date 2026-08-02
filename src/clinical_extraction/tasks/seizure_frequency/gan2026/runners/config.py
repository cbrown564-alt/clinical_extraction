"""Configuration types for Gan 2026 pipeline runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
)

PipelineArchitecture = Literal[
    "rules",
    "deterministic_canonical_pipeline",
    "hybrid_structured_events",
    "llm",
    "llm_only_canonical_pipeline",
]

# These values are retained evidence identifiers. User-facing commands use
# ``rules``, ``llm``, and ``llm_with_rules``.
PIPELINE_METHOD: dict[str, str] = {
    "deterministic_canonical_pipeline": "rules_only",
    "hybrid_structured_events": "llm_with_rules",
    "llm_only_canonical_pipeline": "llm_only",
}

# Kept for readers of saved run metadata and older imports.
ARCHITECTURE_FAMILY = PIPELINE_METHOD


class PipelineConfiguration(BaseModel):
    model_config = ConfigDict(frozen=True)

    architecture: PipelineArchitecture
    ablation_config: AblationConfig = AblationConfig()
    dspy_cache: bool = True
    model: str = "openai/gpt-4.1-mini"
    temperature: float = 0.0
    max_tokens: int = 900
    api_base: str | None = None
    api_key: str | None = None
    timeout: int | None = None
    # Explicit identities keep replay and concurrent conditions from relying on
    # process-global prompt state. ``None`` preserves the selected module
    # default for older callers and historical artifacts.
    prompt_version: str | None = None
    repair_mode: str | None = None


@dataclass(frozen=True)
class PipelineOutputArtifact:
    projection_render_rows: list[dict[str, Any]]
    score_rows: list[dict[str, Any]]
    route_rows: list[dict[str, Any]]
    decision_rows: list[dict[str, Any]]
    metadata: dict[str, Any]
