"""Zero-LLM-cost tests for the ExECTv2 SF Angle 2 architectures (Phase 3)."""

from __future__ import annotations

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.agentic.multi_agent_ceiling import (
    D3_STATIC_BUDGET,
    ORCHESTRATOR_MAX_ITERS,
    ActiveRateFactListerSignature,
    ClusterOrChangeListerSignature,
    SeizureFreeHazardListerSignature,
    SFResolverSignature,
    build_dynamic_orchestrator_agent,
)

SPECIALIST_SIGNATURES = (
    ActiveRateFactListerSignature,
    SeizureFreeHazardListerSignature,
    ClusterOrChangeListerSignature,
)


def test_specialists_cannot_structurally_emit_mentions() -> None:
    for signature in SPECIALIST_SIGNATURES:
        output_fields = set(signature.output_fields.keys())
        assert "mentions" not in output_fields
        assert "extraction_json" not in output_fields


def test_specialists_have_exactly_one_distinctly_named_output_field() -> None:
    expected = {
        ActiveRateFactListerSignature: "active_rate_facts_json",
        SeizureFreeHazardListerSignature: "seizure_free_hazards_json",
        ClusterOrChangeListerSignature: "cluster_or_change_json",
    }
    for signature, field_name in expected.items():
        assert set(signature.output_fields.keys()) == {field_name}


def test_resolver_is_the_only_place_mentions_may_appear() -> None:
    assert set(SFResolverSignature.output_fields.keys()) == {"extraction_json"}
    assert set(SFResolverSignature.input_fields.keys()) == {
        "prompt_input_json",
        "active_rate_facts_json",
        "seizure_free_hazards_json",
        "cluster_or_change_json",
    }


def test_dynamic_orchestrator_has_all_five_tools_plus_finish() -> None:
    agent = build_dynamic_orchestrator_agent("{}", "2 focal seizures per week.")

    assert isinstance(agent, dspy.ReAct)
    assert agent.max_iters == ORCHESTRATOR_MAX_ITERS
    tool_names = set(agent.tools.keys())
    assert "active_rate_fact_lister" in tool_names
    assert "seizure_free_hazard_lister" in tool_names
    assert "cluster_or_change_lister" in tool_names
    assert "check_evidence_in_letter" in tool_names
    assert "read_sf_boundary_guide" in tool_names
    assert "finish" in tool_names


def test_d3_static_budget_is_four_calls_no_deterministic_tool_calls() -> None:
    caps = D3_STATIC_BUDGET.comparable_caps()
    assert caps["model_calls_per_row"] == 4
    assert caps["max_tool_calls_per_row"] == 0
