"""Phase D predeclared verdict and aggregate-only artifact contract.

Protocol: docs/research/gan2026/gan_rules_only_three_stage_phase_d_protocol_2026-08-29.md
Does not load test450.
"""

from __future__ import annotations

from scripts.measure_gan_rules_only_three_stage_phase_d_test450 import (
    CITED_SELECT_CORRECT,
    assert_public_payload_aggregate_only,
    phase_d_verdict,
)


def test_phase_d_verdict_promotes_only_when_candidate_beats_cited() -> None:
    assert CITED_SELECT_CORRECT == 321
    assert phase_d_verdict(322, 321) == "promotion_accepted"
    assert phase_d_verdict(321, 321) == "disappointing_development_only"
    assert phase_d_verdict(320, 321) == "disappointing_development_only"
    assert phase_d_verdict(400, 320) == "blocked_by_comparator_drift"


def test_phase_d_public_payload_rejects_class_and_row_keys() -> None:
    ok = {
        "row_count": 450,
        "row_policy": "aggregate_only",
        "comparator_select_purist_correct": 321,
        "candidate_select_purist_correct": 321,
        "verdict": "disappointing_development_only",
    }
    assert_public_payload_aggregate_only(ok)
    for leaked in (
        {"by_class": {"unknown": 1}},
        {"classification_report": {}},
        {"source_row_index": 12},
        {"rows": [{"source_row_index": 1}]},
        {"per_class_deltas": {}},
    ):
        payload = {**ok, **leaked}
        try:
            assert_public_payload_aggregate_only(payload)
        except ValueError:
            continue
        raise AssertionError(f"payload should reject {list(leaked)}")
