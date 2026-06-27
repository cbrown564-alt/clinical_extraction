"""Tests for the GEPA length-penalized feedback metric."""

from __future__ import annotations

import json

import dspy
import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.metric import (
    LengthPenaltyConfig,
    approx_tokens,
    build_metric,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.gepa.program import (
    OUTPUT_SCHEMA_JSON,
    GepaSeizureFrequencySignature,
)


def _gold(monthly: float, label: str, note: str = "Patient note.") -> dspy.Example:
    return dspy.Example(
        note_text=note,
        output_schema=OUTPUT_SCHEMA_JSON,
        gold_label=label,
        gold_monthly_frequency=monthly,
    )


def _pred(
    final_label: str | None,
    *,
    kind: str = "frequency",
    evidence: str = "once a day",
) -> dspy.Prediction:
    payload = {
        "events": [
            {
                "event_id": "e1",
                "kind": "frequency_rate",
                "raw_value": final_label,
                "applies_to": None,
                "time_window": "current",
                "temporality": "current",
                "assertion_status": "asserted",
                "evidence": evidence,
                "notes": None,
            }
        ],
        "selection": {
            "selected_event_ids": ["e1"],
            "final_kind": kind,
            "final_label": final_label,
            "evidence": evidence,
            "confidence": "high",
            "rationale": "stated rate",
        },
    }
    return dspy.Prediction(structured_json=json.dumps(payload))


def _pred_trace_with_instruction(instruction: str):
    predictor = dspy.Predict(GepaSeizureFrequencySignature)
    predictor.signature = predictor.signature.with_instructions(instruction)
    return [(predictor, {}, {})]


def test_purist_correct_scores_high():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    # 1 per day -> ~30.4/month -> daily category; gold daily.
    out = metric(_gold(30.4, "1 per day", "once a day"), _pred("1 per day", evidence="once a day"))
    assert out.score == pytest.approx(1.0)
    assert "CORRECT" in out.feedback


def test_quality_tiers_are_ordered():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    gold = _gold(30.4, "1 per day", "once a day")
    correct = metric(gold, _pred("1 per day", evidence="once a day")).score
    wrong = metric(gold, _pred("1 per year", evidence="once a day")).score
    unscorable = metric(_gold(30.4, "1 per day"), dspy.Prediction(structured_json="not json")).score
    assert correct > wrong >= 0.1
    assert wrong > unscorable
    assert unscorable == 0.0


def test_stamped_instruction_tokens_penalize_in_selection_path():
    # GEPA scores candidates with metric(example, pred) only (no pred_trace). The
    # program stamps instruction_tokens onto pred, so the penalty must still engage.
    metric = build_metric(LengthPenaltyConfig())
    gold = _gold(30.4, "1 per day", "once a day")
    lean = _pred("1 per day", evidence="once a day")
    lean.instruction_tokens = 300  # under budget
    lean.demo_tokens = 0
    bloated = _pred("1 per day", evidence="once a day")
    bloated.instruction_tokens = 3000  # far over the 600 budget
    bloated.demo_tokens = 0
    lean_score = metric(gold, lean).score
    bloated_score = metric(gold, bloated).score
    assert lean_score == pytest.approx(1.0)
    assert bloated_score < lean_score
    assert "TOO LONG" in metric(gold, bloated).feedback


def test_length_penalty_lowers_score_monotonically():
    metric = build_metric(LengthPenaltyConfig())
    gold = _gold(30.4, "1 per day", "once a day")
    pred = _pred("1 per day", evidence="once a day")
    short_trace = _pred_trace_with_instruction("Be concise.")
    short = metric(gold, pred, None, "extract", short_trace).score
    long_trace = _pred_trace_with_instruction("word " * 4000)  # far over budget
    longer = metric(gold, pred, None, "extract", long_trace).score
    assert short == pytest.approx(1.0)
    assert longer < short
    assert longer >= 1.0 - LengthPenaltyConfig().max_penalty - 1e-9


def test_length_penalty_feedback_flags_overlong_instruction():
    metric = build_metric(LengthPenaltyConfig())
    gold = _gold(30.4, "1 per day", "once a day")
    pred = _pred("1 per day", evidence="once a day")
    out = metric(gold, pred, None, "extract", _pred_trace_with_instruction("word " * 4000))
    assert "TOO LONG" in out.feedback


def test_disabled_penalty_ignores_instruction_length():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    gold = _gold(30.4, "1 per day", "once a day")
    pred = _pred("1 per day", evidence="once a day")
    out = metric(gold, pred, None, "extract", _pred_trace_with_instruction("word " * 4000))
    assert out.score == pytest.approx(1.0)


def test_feedback_demotion_hint_for_unknown_on_countable_gold():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    gold = _gold(30.4, "1 per day", "seizures once a day")
    out = metric(gold, _pred("unknown", kind="unknown", evidence="seizures once a day"))
    assert "demote" in out.feedback.lower()


def test_approx_tokens_scales_with_length():
    assert approx_tokens("") == 0
    assert approx_tokens("a" * 400) == 100
