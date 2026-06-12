"""Matched-budget contracts for Gan 2026 agentic comparisons."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ConditionName = Literal[
    "single_greedy",
    "single_self_consistency_temperature",
    "single_self_consistency_cross_model",
    "single_agent_tools",
    "multi_agent_matched",
]


class AgentBudget(BaseModel):
    """Per-row resource ceiling for a Gan 2026 agentic condition."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    model_calls_per_row: int = Field(ge=0)
    prompt_token_budget: int = Field(ge=0)
    max_completion_tokens_per_call: int = Field(ge=0)
    max_tool_calls_per_row: int = Field(ge=0)
    max_tool_output_tokens_per_row: int = Field(ge=0)
    aggregation_budget_model_calls: int = Field(ge=0)

    def comparable_caps(self) -> dict[str, int]:
        return {
            "model_calls_per_row": self.model_calls_per_row,
            "prompt_token_budget": self.prompt_token_budget,
            "max_completion_tokens_per_call": self.max_completion_tokens_per_call,
            "max_tool_calls_per_row": self.max_tool_calls_per_row,
            "max_tool_output_tokens_per_row": self.max_tool_output_tokens_per_row,
            "aggregation_budget_model_calls": self.aggregation_budget_model_calls,
        }


class MatchedBudgetComparison(BaseModel):
    """Predeclared budget comparison between two Phase 6 conditions."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    reference_condition: ConditionName
    candidate_condition: ConditionName
    reference_budget: AgentBudget
    candidate_budget: AgentBudget
    aggregation_method: str

    @model_validator(mode="after")
    def validate_matched_budget(self) -> MatchedBudgetComparison:
        reference_caps = self.reference_budget.comparable_caps()
        candidate_caps = self.candidate_budget.comparable_caps()
        mismatches = [
            name
            for name, reference_value in reference_caps.items()
            if candidate_caps[name] != reference_value
        ]
        if mismatches:
            mismatch_text = ", ".join(mismatches)
            raise ValueError(f"Matched-budget comparison mismatch: {mismatch_text}")
        return self
