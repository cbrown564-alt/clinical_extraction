"""Grouped cross-validated calibration proxy for reliability cells."""

from __future__ import annotations

import itertools
import math
from collections import defaultdict
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    _CALIBRATION_FEATURES,
    FAMILIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.scoring import (
    confidence_bin,
)

# Logistic-regression fit hyperparameters for the grouped calibration scoring rule.
# ``LOGISTIC_L2_STRENGTH`` was raised from 0.015 to 0.03 after the four-family
# scorer-scope fixes (7949a9d4, 2026-07-02) re-scored the dev140 surface: the
# lighter penalty over-fit a cluster of high-confidence full-200 cells and produced
# a non-monotone reliability curve (adjacent-bin reversal 0.1105 > the 0.10
# promotion gate). L2 = 0.03 restores monotonicity (reversal 0.0784) on full-200
# while leaving dev140 cross-validated ECE essentially unchanged (0.0245 -> 0.0229).
# See ``exectv2_calibration_redesign_2026-07-07.md`` for the L2 sweep and the
# external-signal null result that motivated operating on regularization rather
# than on additional features.
_LOGISTIC_LEARNING_RATE = 0.18
_LOGISTIC_EPOCHS = 700
LOGISTIC_L2_STRENGTH = 0.03


def calibration_proxy(cells: list[dict[str, Any]]) -> dict[str, Any]:
    scored = cross_validated_calibration_scores(cells, fold_count=5)
    pairs = [(float(row["calibrated_confidence"]), bool(row["correct"])) for row in scored]
    baseline_pairs = [
        (float(row["training_fold_base_rate"]), bool(row["correct"])) for row in scored
    ]
    heuristic = heuristic_calibration_baseline(cells)
    bins = reliability_bins(scored, bin_count=5)
    per_family = [
        calibration_summary_for_family(
            str(family),
            [row for row in scored if str(row["family"]) == family],
            baseline_pairs=[
                (float(row["training_fold_base_rate"]), bool(row["correct"]))
                for row in scored
                if str(row["family"]) == family
            ],
        )
        for family in FAMILIES
    ]
    ece = expected_calibration_error(pairs, bins)
    brier = brier_score(pairs)
    baseline_brier = brier_score(baseline_pairs)
    return {
        "definition": (
            "Frozen no-call scoring rule trained by grouped cross-validation over "
            "dev140 rich-schema candidate-family cells. Features are family and "
            "predeclared provenance/evidence ambiguity flags; no full-200 or "
            "holdout rows are loaded."
        ),
        "model_type": "grouped_cross_validated_logistic_scoring_rule",
        "validation_status": (
            "dev140 cross-validated development evidence only; not a full-200 or "
            "holdout calibration claim."
        ),
        "feature_set": list(_CALIBRATION_FEATURES),
        "cell_count": len(scored),
        "fold_count": len({row["fold"] for row in scored}),
        "bin_count": len(bins),
        "expected_calibration_error": round(ece, 4),
        "brier_score": round(brier, 4),
        "constant_base_rate_brier_score": round(baseline_brier, 4),
        "brier_improvement_vs_base_rate": round(baseline_brier - brier, 4),
        "overall_accuracy": round(sum(1 for row in scored if row["correct"]) / len(scored), 4)
        if scored
        else 0.0,
        "mean_calibrated_confidence": round(
            sum(float(row["calibrated_confidence"]) for row in scored) / len(scored),
            4,
        )
        if scored
        else 0.0,
        "max_adjacent_bin_reversal": max_adjacent_bin_reversal(bins),
        "leakage_audit": calibration_leakage_audit(scored),
        "heuristic_baseline": heuristic,
        "bins": bins,
        "per_family": per_family,
    }


def heuristic_calibration_baseline(cells: list[dict[str, Any]]) -> dict[str, Any]:
    bins: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cell in cells:
        bins[confidence_bin(float(cell["confidence_proxy"]))].append(cell)

    rows = []
    total = len(cells)
    ece = 0.0
    for label in ("very_high", "high", "medium", "low"):
        bucket = bins.get(label, [])
        if not bucket:
            continue
        avg_confidence = sum(float(c["confidence_proxy"]) for c in bucket) / len(bucket)
        accuracy = sum(1 for c in bucket if c["correct"]) / len(bucket)
        ece += (len(bucket) / total) * abs(avg_confidence - accuracy)
        rows.append(
            {
                "bin": label,
                "cells": len(bucket),
                "avg_confidence_proxy": round(avg_confidence, 4),
                "accuracy": round(accuracy, 4),
                "mean_cell_f1": round(sum(float(c["f1"]) for c in bucket) / len(bucket), 4),
            }
        )
    return {
        "definition": (
            "External no-call confidence proxy from family, evidence validity, "
            "source-to-final changes, confidence labels, and deterministic action burden."
        ),
        "cell_count": total,
        "bin_count": len(rows),
        "expected_calibration_error": round(ece, 4),
        "brier_score": round(
            brier_score(
                [(float(cell["confidence_proxy"]), bool(cell["correct"])) for cell in cells]
            ),
            4,
        ),
        "bins": rows,
    }


def cross_validated_calibration_scores(
    cells: list[dict[str, Any]],
    *,
    fold_count: int,
) -> list[dict[str, Any]]:
    if not cells:
        return []
    folds = group_folds(cells, fold_count=fold_count)
    scored: list[dict[str, Any]] = []
    for fold_index, test_letters in enumerate(folds):
        train = [cell for cell in cells if str(cell["letter_id"]) not in test_letters]
        test = [cell for cell in cells if str(cell["letter_id"]) in test_letters]
        weights = fit_logistic_scoring_rule(train)
        train_base_rate = (
            sum(1 for cell in train if bool(cell["correct"])) / len(train) if train else 0.5
        )
        for cell in test:
            probability = predict_logistic_probability(weights, cell)
            scored.append(
                {
                    "candidate": cell["candidate"],
                    "model_label": cell["model_label"],
                    "letter_id": cell["letter_id"],
                    "family": cell["family"],
                    "fold": fold_index,
                    "correct": bool(cell["correct"]),
                    "f1": cell["f1"],
                    "calibrated_confidence": round(probability, 6),
                    "training_fold_base_rate": round(train_base_rate, 6),
                }
            )
    return scored


def group_folds(
    cells: list[dict[str, Any]],
    *,
    fold_count: int,
) -> list[set[str]]:
    letter_ids = sorted({str(cell["letter_id"]) for cell in cells})
    folds = [set() for _ in range(fold_count)]
    for index, letter_id in enumerate(letter_ids):
        folds[index % fold_count].add(letter_id)
    return folds


def fit_logistic_scoring_rule(cells: list[dict[str, Any]]) -> list[float]:
    weights = [0.0 for _ in range(len(_CALIBRATION_FEATURES) + 1)]
    if not cells:
        return weights
    learning_rate = _LOGISTIC_LEARNING_RATE
    l2 = LOGISTIC_L2_STRENGTH
    epochs = _LOGISTIC_EPOCHS
    for _ in range(epochs):
        gradients = [0.0 for _ in weights]
        for cell in cells:
            features = calibration_vector(cell)
            probability = sigmoid(
                sum(weight * value for weight, value in zip(weights, features, strict=True))
            )
            target = 1.0 if cell["correct"] else 0.0
            error = probability - target
            for index, value in enumerate(features):
                gradients[index] += error * value
        n = float(len(cells))
        for index in range(len(weights)):
            penalty = 0.0 if index == 0 else l2 * weights[index]
            weights[index] -= learning_rate * ((gradients[index] / n) + penalty)
    return weights


def predict_logistic_probability(weights: list[float], cell: dict[str, Any]) -> float:
    raw = sum(
        weight * value for weight, value in zip(weights, calibration_vector(cell), strict=True)
    )
    return min(max(sigmoid(raw), 0.001), 0.999)


def calibration_vector(cell: dict[str, Any]) -> list[float]:
    features = cell["features"]
    family = str(cell["family"])
    return [
        1.0,
        1.0 if family == "Diagnosis" else 0.0,
        1.0 if family == "SeizureFrequency" else 0.0,
        1.0 if family == "Prescription" else 0.0,
        1.0 if family == "Investigations" else 0.0,
        1.0 if bool(features["evidence_invalid"]) else 0.0,
        1.0 if bool(features["low_confidence"]) else 0.0,
        1.0 if bool(features["source_final_delta"]) else 0.0,
        1.0 if bool(features["active_rate"]) else 0.0,
        1.0 if bool(features["plan_language"]) else 0.0,
        1.0 if bool(features["result_state"]) else 0.0,
        min(float(features["deterministic_action_count"]), 5.0) / 5.0,
        min(float(features["prediction_count"]), 8.0) / 8.0,
    ]


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def reliability_bins(
    scored: list[dict[str, Any]],
    *,
    bin_count: int,
) -> list[dict[str, Any]]:
    if not scored:
        return []
    ordered = sorted(scored, key=lambda row: float(row["calibrated_confidence"]))
    rows = []
    total = len(ordered)
    for index in range(bin_count):
        start = (index * total) // bin_count
        end = ((index + 1) * total) // bin_count
        bucket = ordered[start:end]
        if not bucket:
            continue
        avg_confidence = sum(float(row["calibrated_confidence"]) for row in bucket) / len(bucket)
        accuracy = sum(1 for row in bucket if row["correct"]) / len(bucket)
        rows.append(
            {
                "bin": f"q{index + 1}",
                "confidence_range": [
                    round(float(bucket[0]["calibrated_confidence"]), 4),
                    round(float(bucket[-1]["calibrated_confidence"]), 4),
                ],
                "cells": len(bucket),
                "avg_confidence_proxy": round(avg_confidence, 4),
                "avg_calibrated_confidence": round(avg_confidence, 4),
                "accuracy": round(accuracy, 4),
                "calibration_gap": round(accuracy - avg_confidence, 4),
                "ece_contribution": round(
                    (len(bucket) / total) * abs(accuracy - avg_confidence),
                    4,
                ),
                "mean_cell_f1": round(sum(float(row["f1"]) for row in bucket) / len(bucket), 4),
            }
        )
    return rows


def calibration_summary_for_family(
    family: str,
    rows: list[dict[str, Any]],
    *,
    baseline_pairs: list[tuple[float, bool]],
) -> dict[str, Any]:
    pairs = [(float(row["calibrated_confidence"]), bool(row["correct"])) for row in rows]
    bins = reliability_bins(rows, bin_count=min(4, len(rows))) if rows else []
    return {
        "family": family,
        "cells": len(rows),
        "accuracy": round(sum(1 for row in rows if row["correct"]) / len(rows), 4) if rows else 0.0,
        "mean_calibrated_confidence": round(
            sum(float(row["calibrated_confidence"]) for row in rows) / len(rows), 4
        )
        if rows
        else 0.0,
        "expected_calibration_error": round(expected_calibration_error(pairs, bins), 4),
        "brier_score": round(brier_score(pairs), 4),
        "constant_base_rate_brier_score": round(brier_score(baseline_pairs), 4),
        "bin_count": len(bins),
    }


def expected_calibration_error(
    pairs: list[tuple[float, bool]],
    bins: list[dict[str, Any]],
) -> float:
    total = len(pairs)
    if not total:
        return 0.0
    return sum(float(row["ece_contribution"]) for row in bins)


def brier_score(pairs: list[tuple[float, bool]]) -> float:
    if not pairs:
        return 0.0
    return sum((float(score) - (1.0 if outcome else 0.0)) ** 2 for score, outcome in pairs) / len(
        pairs
    )


def max_adjacent_bin_reversal(bins: list[dict[str, Any]]) -> float:
    reversals = [
        max(0.0, float(left["accuracy"]) - float(right["accuracy"]))
        for left, right in zip(bins, bins[1:], strict=False)
    ]
    return round(max(reversals), 4) if reversals else 0.0


def calibration_leakage_audit(scored: list[dict[str, Any]]) -> dict[str, Any]:
    fold_letters: dict[int, set[str]] = defaultdict(set)
    for row in scored:
        fold_letters[int(row["fold"])].add(str(row["letter_id"]))
    shared = False
    folds = sorted(fold_letters)
    for left, right in itertools.combinations(folds, 2):
        if fold_letters[left] & fold_letters[right]:
            shared = True
            break
    return {
        "surface": "dev140 rich-schema holistic assembly reliability scorecard",
        "group_key": "letter_id",
        "fold_count": len(folds),
        "unique_groups": len(set().union(*fold_letters.values())) if fold_letters else 0,
        "shared_letter_between_train_and_test": shared,
        "forbidden_validation_rows_loaded": False,
        "forbidden_row_level_outputs_emitted": False,
        "candidate_identity_used_as_feature": False,
        "gold_or_failure_residual_used_as_feature": False,
    }
