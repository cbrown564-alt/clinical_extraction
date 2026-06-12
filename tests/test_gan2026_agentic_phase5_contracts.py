from __future__ import annotations

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.contracts import (
    AgentBudget,
    MatchedBudgetComparison,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.tools import (
    parse_seizure_frequency_candidates,
    read_boundary_guide,
)


def test_parser_tool_returns_source_near_candidates_without_row_or_gold_leakage() -> None:
    note_text = (
        "Clinic Date: 12 June 2026\n"
        "She reports 2 focal seizures per week, with no recent tonic-clonic seizures."
    )

    result = parse_seizure_frequency_candidates(note_text)

    assert result.schema_version == "gan2026_agent_parser_tool_v0"
    assert result.tool_name == "parse_seizure_frequency_candidates"
    assert result.candidates
    candidate = result.candidates[0]
    assert candidate.candidate_kind == "frequency_rate"
    assert candidate.evidence_text == "2 focal seizures per week"
    assert candidate.start_char is not None
    assert candidate.end_char is not None
    assert candidate.rule_id
    assert candidate.portability in {
        "general",
        "clinical_epilepsy",
        "seizure_frequency",
        "gan2026_specific",
        "benchmark_format",
        "unknown",
    }

    payload = result.model_dump()
    forbidden_keys = {"source_row_index", "gold_label", "gold_normalized_label", "split"}
    assert forbidden_keys.isdisjoint(payload)
    assert all(forbidden_keys.isdisjoint(item) for item in payload["candidates"])


def test_parser_tool_reports_no_result_without_inventing_no_reference_answer() -> None:
    result = parse_seizure_frequency_candidates("Clinic Date: 12 June 2026\nMedication reviewed.")

    assert result.candidates == []
    assert "no_candidates_found" in result.parse_warnings


def test_boundary_guide_reader_returns_versioned_split_neutral_excerpt() -> None:
    guide = read_boundary_guide("cluster frequency versus incidental clustering")

    assert guide.schema_version == "gan2026_boundary_guide_v0"
    assert guide.guide_id == "cluster_frequency_vs_incidental_clustering"
    assert guide.version == "2026-06-12.phase5"
    assert guide.decision_criteria
    assert guide.max_output_tokens <= 260

    payload_text = str(guide.model_dump()).lower()
    assert "source_row_index" not in payload_text
    assert "gold" not in payload_text
    assert "validation" not in payload_text
    assert "test" not in payload_text


def test_boundary_guide_reader_fails_closed_with_available_ids() -> None:
    with pytest.raises(KeyError) as exc_info:
        read_boundary_guide("please give me the answer for row 12")

    message = str(exc_info.value)
    assert "Unknown boundary guide" in message
    assert "cluster_frequency_vs_incidental_clustering" in message


def test_matched_budget_comparison_accepts_same_caps_and_rejects_mismatch() -> None:
    shared = AgentBudget(
        model_calls_per_row=4,
        prompt_token_budget=2_500,
        max_completion_tokens_per_call=600,
        max_tool_calls_per_row=3,
        max_tool_output_tokens_per_row=700,
        aggregation_budget_model_calls=1,
    )
    MatchedBudgetComparison(
        reference_condition="single_self_consistency_temperature",
        candidate_condition="single_agent_tools",
        reference_budget=shared,
        candidate_budget=shared,
        aggregation_method="deterministic_normalized_label_vote",
    )

    with pytest.raises(ValueError, match="model_calls_per_row"):
        MatchedBudgetComparison(
            reference_condition="single_agent_tools",
            candidate_condition="multi_agent_matched",
            reference_budget=shared,
            candidate_budget=shared.model_copy(update={"model_calls_per_row": 5}),
            aggregation_method="deterministic_normalized_label_vote",
        )
