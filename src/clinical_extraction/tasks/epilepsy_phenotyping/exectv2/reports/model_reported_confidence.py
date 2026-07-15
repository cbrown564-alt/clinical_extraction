"""Aggregate-only evaluation of model-reported confidence across ExECT splits."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}
FAILURE_RISK = {"low": 1.0, "medium": 0.5, "high": 0.0}


def cell_confidence(mentions: Iterable[Mapping[str, Any]], family: str) -> str:
    """Return the least-confident usable label for one model-produced family cell."""

    labels = [
        str(mention.get("confidence", "")).strip().lower()
        for mention in mentions
        if str(mention.get("entity", "")) == family
        and str(mention.get("confidence", "")).strip().lower() in CONFIDENCE_ORDER
    ]
    return min(labels, key=CONFIDENCE_ORDER.__getitem__) if labels else "missing"


def failure_auroc(cells: Sequence[Mapping[str, Any]]) -> float | None:
    """Pairwise AUROC for ordinal confidence as a predictor of cell failure."""

    usable = [cell for cell in cells if str(cell["confidence"]) in FAILURE_RISK]
    errors = [cell for cell in usable if not bool(cell["final_correct"])]
    correct = [cell for cell in usable if bool(cell["final_correct"])]
    if not errors or not correct:
        return None
    wins = 0.0
    comparisons = 0
    for error in errors:
        error_risk = FAILURE_RISK[str(error["confidence"])]
        for success in correct:
            success_risk = FAILURE_RISK[str(success["confidence"])]
            comparisons += 1
            wins += float(error_risk > success_risk) + 0.5 * float(error_risk == success_risk)
    return round(wins / comparisons, 4)


def summarize_cells(cells: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build an aggregate summary that contains no row identifiers or row contents."""

    total = len(cells)
    errors = sum(not bool(cell["final_correct"]) for cell in cells)
    usable = sum(str(cell["confidence"]) != "missing" for cell in cells)
    by_confidence = []
    for label in ("low", "medium", "high", "missing"):
        bucket = [cell for cell in cells if str(cell["confidence"]) == label]
        bucket_errors = sum(not bool(cell["final_correct"]) for cell in bucket)
        by_confidence.append(
            {
                "confidence": label,
                "cells": len(bucket),
                "correct_cells": len(bucket) - bucket_errors,
                "error_cells": bucket_errors,
                "accuracy": _rate(len(bucket) - bucket_errors, len(bucket)),
                "error_rate": _rate(bucket_errors, len(bucket)),
            }
        )

    policies = [
        _policy(cells, errors, "low_or_medium", {"low", "medium"}),
        _policy(
            cells,
            errors,
            "low_or_medium_or_missing",
            {"low", "medium", "missing"},
        ),
    ]
    directions: Counter[str] = Counter()
    changed = 0
    for cell in cells:
        source = bool(cell["source_correct"])
        final = bool(cell["final_correct"])
        if bool(cell["source_final_changed"]):
            changed += 1
            directions[
                "correct_to_correct"
                if source and final
                else "correct_to_wrong"
                if source
                else "wrong_to_correct"
                if final
                else "wrong_to_wrong"
            ] += 1

    return {
        "cells": total,
        "correct_cells": total - errors,
        "error_cells": errors,
        "accuracy": _rate(total - errors, total),
        "usable_confidence_cells": usable,
        "usable_confidence_coverage": _rate(usable, total),
        "failure_auroc_usable_labels": failure_auroc(cells),
        "by_confidence": by_confidence,
        "review_policies": policies,
        "source_to_final": {
            "changed_cells": changed,
            **{
                key: directions[key]
                for key in (
                    "wrong_to_correct",
                    "correct_to_wrong",
                    "correct_to_correct",
                    "wrong_to_wrong",
                )
            },
        },
    }


def verdict(summary: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the frozen stop rule to one test60 model summary."""

    coverage = float(summary["usable_confidence_coverage"])
    auroc = summary["failure_auroc_usable_labels"]
    policy_passes = [
        str(policy["id"])
        for policy in summary["review_policies"]
        if float(policy["catch_rate"]) >= 0.5 and float(policy["review_burden"]) <= 0.3
    ]
    informative = (
        coverage >= 0.8 and auroc is not None and float(auroc) >= 0.65 and bool(policy_passes)
    )
    return {
        "informative": informative,
        "coverage_gate": coverage >= 0.8,
        "auroc_gate": auroc is not None and float(auroc) >= 0.65,
        "review_policy_gate": bool(policy_passes),
        "passing_review_policies": policy_passes,
        "decision": (
            "confidence_informative_for_named_saved_output"
            if informative
            else "negative_result_do_not_adopt_confidence_review_policy"
        ),
    }


def _policy(
    cells: Sequence[Mapping[str, Any]],
    total_errors: int,
    policy_id: str,
    reviewed_labels: set[str],
) -> dict[str, Any]:
    reviewed = [cell for cell in cells if str(cell["confidence"]) in reviewed_labels]
    caught = sum(not bool(cell["final_correct"]) for cell in reviewed)
    false_alarms = len(reviewed) - caught
    return {
        "id": policy_id,
        "reviewed_cells": len(reviewed),
        "review_burden": _rate(len(reviewed), len(cells)),
        "caught_error_cells": caught,
        "catch_rate": _rate(caught, total_errors),
        "false_alarm_cells": false_alarms,
        "false_alarm_rate": _rate(false_alarms, len(reviewed)),
    }


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0
