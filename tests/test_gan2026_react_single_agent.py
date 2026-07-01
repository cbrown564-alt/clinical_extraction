"""Zero-LLM-cost tests for the genuine tool-using ReAct single agent
(Phase 0/1 of docs/plans/proud-bubbling-ocean.md). Covers tool binding and
agent construction only; forward()/live calls are exercised by the smoke
stage, not here.
"""
from __future__ import annotations

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.react_single_agent import (
    BUDGET,
    REACT_MAX_ITERS,
    bound_parser_tool,
    build_react_agent,
    read_boundary_guide_tool,
)


def test_bound_parser_tool_takes_no_arguments_and_finds_candidates() -> None:
    tool = bound_parser_tool(
        "She reports 2 focal seizures per week, with no recent tonic-clonic seizures."
    )
    result = tool()

    assert result["tool_name"] == "parse_seizure_frequency_candidates"
    assert result["candidates"]
    assert result["candidates"][0]["evidence_text"] == "2 focal seizures per week"


def test_bound_parser_tool_is_isolated_per_letter() -> None:
    tool_a = bound_parser_tool("2 focal seizures per week.")
    tool_b = bound_parser_tool("No further seizures since last clinic.")

    result_a = tool_a()
    result_b = tool_b()

    assert result_a["candidates"]
    assert not any(
        c["evidence_text"] == "2 focal seizures per week" for c in result_b["candidates"]
    )


def test_read_boundary_guide_tool_returns_versioned_guide() -> None:
    guide = read_boundary_guide_tool("cluster frequency")

    assert guide["guide_id"] == "cluster_frequency_vs_incidental_clustering"
    assert guide["decision_criteria"]


def test_build_react_agent_is_a_real_dspy_react_module_with_both_tools() -> None:
    agent = build_react_agent("2 focal seizures per week.")

    assert isinstance(agent, dspy.ReAct)
    assert agent.max_iters == REACT_MAX_ITERS
    tool_names = set(agent.tools.keys())
    assert "read_boundary_guide_tool" in tool_names
    assert any(name.startswith("parse_seizure_frequency_candidates") for name in tool_names)
    assert "finish" in tool_names


def test_build_react_agent_max_iters_matches_matched_budget_shape() -> None:
    # REACT_MAX_ITERS (3 ReAct-loop LM calls) + 1 dspy.ReAct final-extraction
    # call = BUDGET.model_calls_per_row (4), matching the 2026-06-12 hard50
    # matched-budget shape so results stay comparable.
    assert REACT_MAX_ITERS + 1 == BUDGET.model_calls_per_row
    assert BUDGET.max_tool_calls_per_row == 3


def test_budget_is_a_valid_agent_budget() -> None:
    caps = BUDGET.comparable_caps()
    assert caps["model_calls_per_row"] == 4
    assert caps["max_tool_calls_per_row"] == 3
