"""Zero-LLM-cost tests for the ExECTv2 SF agentic-redo tools (Phase 3, see
docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_predeclaration_2026-07-01.md).
"""
from __future__ import annotations

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.agentic.tools import (
    bound_evidence_check_tool,
    read_sf_boundary_guide,
)


def test_read_sf_boundary_guide_resolves_by_alias() -> None:
    guide = read_sf_boundary_guide("seizure free")
    assert guide["guide_id"] == "seizure_free_anchor_guide"
    assert isinstance(guide["content"], dict)
    assert guide["content"]


def test_read_sf_boundary_guide_resolves_by_exact_id() -> None:
    guide = read_sf_boundary_guide("clinical_rules")
    assert guide["guide_id"] == "clinical_rules"
    assert isinstance(guide["content"], list)


def test_read_sf_boundary_guide_covers_all_six_guides() -> None:
    for guide_id in (
        "clinical_rules",
        "generic_seizure_policy",
        "seizure_free_anchor_guide",
        "typed_candidate_guide",
        "unknown_change_recovery_lane",
        "state_decision_guide",
    ):
        guide = read_sf_boundary_guide(guide_id)
        assert guide["guide_id"] == guide_id
        assert guide["content"]


def test_read_sf_boundary_guide_fails_closed_with_available_ids() -> None:
    with pytest.raises(KeyError) as exc_info:
        read_sf_boundary_guide("please give me the answer")
    message = str(exc_info.value)
    assert "Unknown SF boundary guide" in message
    assert "clinical_rules" in message


def test_evidence_check_tool_is_isolated_per_letter() -> None:
    tool_a = bound_evidence_check_tool("2 to 3 focal seizures per month.")
    tool_b = bound_evidence_check_tool("No further seizures since last clinic.")

    result_a = tool_a("2 to 3 focal seizures per month")
    result_b = tool_b("2 to 3 focal seizures per month")

    assert result_a["is_exact"] is True
    assert result_b["is_exact"] is False
    assert result_b["grade"] == "ABSENT"


def test_evidence_check_tool_reports_exact_grade() -> None:
    tool = bound_evidence_check_tool("She reports seizure-free for 6 months following surgery.")
    result = tool("seizure-free for 6 months following surgery")
    assert result["grade"] == "EXACT"
    assert result["is_exact"] is True
