"""Matched-budget contracts for Gan 2026 agentic comparisons.

``AgentBudget``/``MatchedBudgetComparison`` moved to
``clinical_extraction.core.agentic_contracts`` (2026-07-01) so ExECTv2 can
reuse the same budget-parity contract; re-exported here for backward
compatibility. ``ConditionName`` stays Gan-2026-specific.
"""

from __future__ import annotations

from typing import Literal

from clinical_extraction.core.agentic_contracts import (
    AgentBudget,
    MatchedBudgetComparison,
)

ConditionName = Literal[
    "single_greedy",
    "single_self_consistency_temperature",
    "single_self_consistency_cross_model",
    "single_agent_tools",
    "multi_agent_matched",
    "single_agent_tools_react",
    "multi_agent_dynamic_orchestrator",
    "multi_agent_d3_static",
]

__all__ = ["AgentBudget", "ConditionName", "MatchedBudgetComparison"]
