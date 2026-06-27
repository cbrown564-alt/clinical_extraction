"""Pydantic models and shared constants for the Observatory API."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    temporal_selection,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import classify_hidden_families

# The atlas hard-slice manifest module was removed; definitions stay empty until
# a canonical production replacement lands.
ATLAS_HARD_SLICE_DEFINITIONS: tuple[dict[str, object], ...] = ()

# Only ``rules_only`` is executable via /run/note and /run/ablation. Registry-backed
# families for the Explorer dropdown are served separately by /pipeline-families.
PipelineFamily = Literal["rules_only"]
TEMPORAL_SELECTION_RULES = temporal_selection.TEMPORAL_SELECTION_RULES

PROMPT_MODULES = (
    "clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler",
    "clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events",
)

EXECUTABLE_PIPELINES: set[str] = {"rules_only"}

RETIRED_PIPELINE_FAMILIES: set[str] = {
    "hybrid_parallel_state_candidate_reasoner",
    "hybrid_rules_candidates_llm_adjudicator",
    "llm_only_claim_table_selector",
    "llm_only_minimal_evidence_selector",
    "llm_only_simplified_selected_state_reasoner",
    "llm_only_sparse_operands_selected_state_reasoner",
    "llm_only_typed_adapter_reasoner",
    "llm_only_typed_operations_reasoner",
}


class ObservatorySettings(BaseModel):
    """Filesystem settings for Observatory endpoints."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    repo_root: Path
    data_path: Path
    split_manifest_path: Path
    registry_path: Path
    experiments_dir: Path


class AblationConfigPayload(BaseModel):
    """JSON-serialisable form of the deterministic rule ablation config."""

    enabled_groups: list[RuleGroup] | None = None
    enabled_portability: list[Portability] | None = None
    disabled_rule_ids: list[str] = Field(default_factory=list)

    def to_domain(self) -> AblationConfig:
        return AblationConfig(
            enabled_groups=frozenset(self.enabled_groups or list(RuleGroup)),
            enabled_portability=frozenset(self.enabled_portability or list(Portability)),
            disabled_rule_ids=frozenset(self.disabled_rule_ids),
        )


class RunNoteRequest(BaseModel):
    """Single-note execution request."""

    note_text: str = Field(min_length=1)
    pipeline: PipelineFamily = "rules_only"
    source_row_index: int = 0
    gold_label: str = "unknown"
    gold_reference: str = ""
    ablation_config: AblationConfigPayload = Field(default_factory=AblationConfigPayload)


class RunAblationRequest(BaseModel):
    """Batch deterministic ablation request against a named Gan split."""

    split: str = "validation"
    pipeline: PipelineFamily = "rules_only"
    limit: int | None = Field(default=None, ge=1)
    ablation_config: AblationConfigPayload = Field(default_factory=AblationConfigPayload)


class GoldAuditDecision(BaseModel):
    """Single human audit decision for a gold label row."""

    source_row_index: int
    split: str
    simple_class: Literal["correct", "ambiguous", "wrong"] = "ambiguous"
    rq10_class: Literal[
        "true_extraction_failure",
        "benchmark_convention_dominated",
        "underdetermined_note",
        "clinically_defensible_alternative",
        "possible_gold_weakness",
        "instrumentation_gap",
    ] | None = None
    notes: str = ""
    corrected_gold_label: str | None = None
    benchmark_convention_flag: bool = False
    all_system_fail: bool = False
    exact_evidence_but_scorer_wrong: bool = False
    clinically_defensible_alternative: bool = False
    likely_gold_defect: bool = False
    timestamp: str | None = None
    auditor: str | None = None


class TagErrorRequest(BaseModel):
    """Request to classify a single prediction into the frontend error taxonomy."""

    gold_category: str
    predicted_category: str
    purist_correct: bool = False
    pragmatic_correct: bool = False


class HardSliceMembershipRequest(BaseModel):
    """Request to compute hard-slice membership for a set of artifact rows."""

    rows: list[dict[str, Any]]
    primary_layer: str | None = None
