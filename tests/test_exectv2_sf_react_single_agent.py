"""Zero-LLM-cost tests for the ExECTv2 SF ReAct single agent (Phase 3)."""

from __future__ import annotations

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.agentic.react_single_agent import (
    BUDGET,
    REACT_MAX_ITERS,
    build_react_agent,
)


def test_build_react_agent_has_both_tools_and_finish() -> None:
    agent = build_react_agent("2 to 3 focal seizures per month.")

    assert isinstance(agent, dspy.ReAct)
    assert agent.max_iters == REACT_MAX_ITERS
    tool_names = set(agent.tools.keys())
    assert "check_evidence_in_letter" in tool_names
    assert "read_sf_boundary_guide" in tool_names
    assert "finish" in tool_names


def test_budget_matches_matched_budget_shape() -> None:
    assert REACT_MAX_ITERS + 1 == BUDGET.model_calls_per_row
    assert BUDGET.max_tool_calls_per_row == 3
