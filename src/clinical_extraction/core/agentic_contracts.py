"""Task-neutral matched-budget contracts for agentic architecture comparisons.

Ported from `tasks.seizure_frequency.gan2026.agentic.contracts` (2026-06-12)
so both Gan 2026 and ExECTv2 agentic studies share one budget-parity
contract. See `docs/plans/proud-bubbling-ocean.md` (Phase 0) for context.
Task-specific condition-name vocabularies stay in each task's own module;
this module only enforces that two conditions' resource ceilings match.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AgentBudget(BaseModel):
    """Per-row resource ceiling for an agentic condition."""

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
    """Predeclared budget comparison between two agentic conditions.

    ``reference_condition``/``candidate_condition`` are plain strings here
    (not a closed vocabulary) so this contract stays task-neutral; each
    task module may narrow them to its own condition-name type for local
    type-checking without duplicating the validation logic below.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    reference_condition: str
    candidate_condition: str
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
