"""Unit tests for the grouped logistic calibration scoring-rule internals.

These pin the fit/predict contract and the regularization behavior that the
calibration redesign (L2 bump to clear the full-200 adjacent-bin-reversal gate)
depends on. Hand-built cells keep the tests deterministic and independent of any
saved dev140/full-200 artifact.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability import (
    calibration,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    _CALIBRATION_FEATURES,
)


def _cell(*, correct: bool, family: str, features: dict) -> dict:
    return {
        "candidate": "test",
        "model_label": "test",
        "letter_id": "EA0001",
        "family": family,
        "f1": 1.0 if correct else 0.0,
        "correct": correct,
        "risk_score": 0.2,
        "confidence_proxy": 0.8,
        "features": features,
    }


def _features(**overrides: bool) -> dict:
    base = {
        "evidence_invalid": False,
        "low_confidence": False,
        "source_final_delta": False,
        "active_rate": False,
        "plan_language": False,
        "result_state": False,
        "deterministic_action_count": 0,
        "prediction_count": 1,
    }
    base.update(overrides)
    return base


def test_l2_strength_is_a_named_module_constant() -> None:
    """The L2 strength must be a named, documented constant (not a magic number)
    so the post-redesign regularization choice is transparent and tunable."""

    assert hasattr(calibration, "LOGISTIC_L2_STRENGTH")
    assert calibration.LOGISTIC_L2_STRENGTH == 0.03


def test_fit_returns_one_weight_per_feature_plus_bias() -> None:
    """The weight vector length tracks ``_CALIBRATION_FEATURES`` plus the bias term."""

    cells = [
        _cell(correct=True, family="Diagnosis", features=_features()),
        _cell(correct=False, family="SeizureFrequency", features=_features(evidence_invalid=True)),
    ]
    weights = calibration.fit_logistic_scoring_rule(cells)
    assert len(weights) == len(_CALIBRATION_FEATURES) + 1


def test_fit_on_empty_returns_zero_weights() -> None:
    weights = calibration.fit_logistic_scoring_rule([])
    assert weights == [0.0 for _ in range(len(_CALIBRATION_FEATURES) + 1)]


def test_predict_probability_is_bounded_into_open_unit_interval() -> None:
    """Predicted probabilities stay within the clipped [0.001, 0.999] range."""

    cells = [
        _cell(correct=True, family="Diagnosis", features=_features()),
        _cell(correct=False, family="Diagnosis", features=_features(evidence_invalid=True)),
    ]
    weights = calibration.fit_logistic_scoring_rule(cells)
    for cell in cells:
        probability = calibration.predict_logistic_probability(weights, cell)
        assert 0.001 <= probability <= 0.999


def test_stronger_l2_shrinks_non_bias_weights() -> None:
    """Increasing L2 regularization must not increase the magnitude of the
    fitted non-bias weights — the regularization redesign lever."""

    n = 40
    cells = []
    for i in range(n):
        cells.append(
            _cell(
                correct=(i % 2 == 0),
                family="Diagnosis" if i % 2 == 0 else "SeizureFrequency",
                features=_features(evidence_invalid=(i % 3 == 0)),
            )
        )
    original = calibration.LOGISTIC_L2_STRENGTH
    try:
        calibration.LOGISTIC_L2_STRENGTH = 0.01
        weak = calibration.fit_logistic_scoring_rule(cells)
        calibration.LOGISTIC_L2_STRENGTH = 0.5
        strong = calibration.fit_logistic_scoring_rule(cells)
    finally:
        calibration.LOGISTIC_L2_STRENGTH = original
    # Non-bias weights (index >= 1) shrink in absolute magnitude under stronger L2.
    weak_mag = sum(abs(w) for w in weak[1:])
    strong_mag = sum(abs(w) for w in strong[1:])
    assert strong_mag <= weak_mag
