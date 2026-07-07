"""Zero-LLM-cost tests for the Angle 2 (ceiling) multi-agent architectures
(Phase 0/2 of docs/plans/proud-bubbling-ocean.md). Covers structural
constraints and construction only; forward()/live calls are exercised by
the smoke/battery/hard50 stages, not here.
"""

from __future__ import annotations

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.multi_agent_ceiling import (
    D3_STATIC_BUDGET,
    ORCHESTRATOR_MAX_ITERS,
    BoundaryHazardListerSignature,
    ClusterBurdenListerSignature,
    FrequencyFactListerSignature,
    ResolverSignature,
    build_dynamic_orchestrator_agent,
)

SPECIALIST_SIGNATURES = (
    FrequencyFactListerSignature,
    BoundaryHazardListerSignature,
    ClusterBurdenListerSignature,
)


def test_specialists_cannot_structurally_emit_a_final_label() -> None:
    # This is the exact gap that made the 2026-06-12 multi_agent_matched
    # condition fake (four identical final-labelers wearing role costumes).
    # Enforced by schema absence, not by a prompt instruction that could be
    # ignored.
    for signature in SPECIALIST_SIGNATURES:
        output_fields = set(signature.output_fields.keys())
        assert "final_label" not in output_fields
        assert "answer_kind" not in output_fields
        assert "decision_json" not in output_fields


def test_specialists_have_exactly_one_distinctly_named_output_field() -> None:
    expected = {
        FrequencyFactListerSignature: "frequency_facts_json",
        BoundaryHazardListerSignature: "boundary_hazards_json",
        ClusterBurdenListerSignature: "cluster_burden_json",
    }
    for signature, field_name in expected.items():
        assert set(signature.output_fields.keys()) == {field_name}


def test_resolver_is_the_only_place_a_final_label_may_appear() -> None:
    output_fields = set(ResolverSignature.output_fields.keys())
    assert output_fields == {"decision_json"}
    input_fields = set(ResolverSignature.input_fields.keys())
    assert input_fields == {
        "prompt_input_json",
        "frequency_facts_json",
        "boundary_hazards_json",
        "cluster_burden_json",
    }


def test_dynamic_orchestrator_has_all_five_tools_plus_finish() -> None:
    agent = build_dynamic_orchestrator_agent("{}", "2 focal seizures per week.")

    assert isinstance(agent, dspy.ReAct)
    assert agent.max_iters == ORCHESTRATOR_MAX_ITERS
    tool_names = set(agent.tools.keys())
    assert "frequency_fact_lister" in tool_names
    assert "boundary_hazard_lister" in tool_names
    assert "cluster_burden_lister" in tool_names
    assert "read_boundary_guide_tool" in tool_names
    assert any(name.startswith("parse_seizure_frequency_candidates") for name in tool_names)
    assert "finish" in tool_names


def test_d3_static_budget_is_four_calls_no_deterministic_tool_calls() -> None:
    caps = D3_STATIC_BUDGET.comparable_caps()
    assert caps["model_calls_per_row"] == 4
    assert caps["max_tool_calls_per_row"] == 0
