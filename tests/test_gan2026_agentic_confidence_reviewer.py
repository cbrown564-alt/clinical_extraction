"""Tests for the decoupled variant-D confidence reviewer (shadow stage).

Pure-logic + stubbed-LM only; no live model calls.
"""

from __future__ import annotations

import json

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.confidence_reviewer import (
    CONFIDENCE_REVIEWER_VERSION,
    ConfidenceReview,
    ConfidenceReviewer,
    build_review_payload,
    parse_probability,
    review_from_raw,
)


def test_parse_probability_strict_json() -> None:
    prob, reason, err = parse_probability('{"probability": 80, "reason": "clear rate"}')
    assert (prob, reason, err) == (80, "clear rate", None)


def test_parse_probability_clamps_out_of_range() -> None:
    assert parse_probability('{"probability": 140}')[0] == 100
    assert parse_probability('{"probability": -5}')[0] == 0


def test_parse_probability_regex_fallback_on_bad_json() -> None:
    prob, _reason, err = parse_probability("I estimate about 35 percent.")
    assert prob == 35
    assert err == "regex_int_fallback"


def test_parse_probability_empty_and_missing_field() -> None:
    assert parse_probability("")[2] == "empty_output"
    assert parse_probability('{"reason": "no number"}')[2] == "no_probability_field"


def test_review_from_raw_computes_risk_complement() -> None:
    review = review_from_raw('{"probability": 70, "reason": "ok"}')
    assert review.calibrated_confidence == pytest.approx(0.70)
    assert review.risk == pytest.approx(0.30)
    assert review.probability_0_100 == 70
    assert review.source == CONFIDENCE_REVIEWER_VERSION


def test_review_from_raw_unparseable_is_none_not_crash() -> None:
    review = review_from_raw("garbage with no digits")
    assert review.calibrated_confidence is None
    assert review.risk is None
    assert review.error == "parse_failed"


def test_payload_is_blind_to_rationale_and_carries_stated_answer() -> None:
    payload = json.loads(build_review_payload("note body", "2 per month", "frequency"))
    assert payload["stated_answer"] == {"final_label": "2 per month", "answer_kind": "frequency"}
    assert payload["variant"] == "D"
    # Decoupling invariant: the payload must NOT leak the model's own events/rationale.
    blob = json.dumps(payload).lower()
    assert "rationale" not in blob
    assert "events" not in blob


def test_reviewer_review_uses_stubbed_predict(monkeypatch: pytest.MonkeyPatch) -> None:
    """review() should turn a stubbed LM output into a ConfidenceReview without a live call."""

    class _StubPrediction:
        elicitation_json = '{"probability": 42, "reason": "borderline last-event"}'

    reviewer = ConfidenceReviewer.__new__(ConfidenceReviewer)  # bypass LM construction
    reviewer._lm = object()
    reviewer._predict = lambda **_: _StubPrediction()

    review = reviewer.review(note_text="n", final_label="unknown", final_kind="unknown")
    assert isinstance(review, ConfidenceReview)
    assert review.probability_0_100 == 42
    assert review.calibrated_confidence == pytest.approx(0.42)


def test_reviewer_review_swallows_llm_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _boom(**_kwargs):
        raise RuntimeError("api down")

    reviewer = ConfidenceReviewer.__new__(ConfidenceReviewer)
    reviewer._lm = object()
    reviewer._predict = _boom

    review = reviewer.review(note_text="n", final_label="x", final_kind="frequency")
    assert review.calibrated_confidence is None
    assert review.error is not None and "RuntimeError" in review.error
