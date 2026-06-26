"""Shared scorecard assembly primitives for ExECTv2 report scorecards."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import ClinicalRecoveryPRF1


def prf1_to_dict(score: Any, *, include_counts: bool = False) -> dict[str, Any]:
    out: dict[str, Any] = {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
    }
    if include_counts:
        out["pred_count"] = score.tp + score.fp
        out["gold_count"] = score.tp + score.fn
    return out


def overall_to_dict(score: Any, *, include_counts: bool = False) -> dict[str, Any]:
    return {
        "per_item": prf1_to_dict(score.per_item, include_counts=include_counts),
        "per_letter": prf1_to_dict(score.per_letter, include_counts=include_counts),
        "per_entity": {
            entity: {
                "per_item": prf1_to_dict(entity_score.per_item, include_counts=include_counts),
                "per_letter": prf1_to_dict(entity_score.per_letter, include_counts=include_counts),
            }
            for entity, entity_score in score.per_entity.items()
        },
    }


def recovery_from_counts(
    *,
    precision_tp: int,
    recall_tp: int,
    pred_count: int,
    gold_count: int,
) -> ClinicalRecoveryPRF1:
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return ClinicalRecoveryPRF1(
        tp=recall_tp,
        precision_tp=precision_tp,
        recall_tp=recall_tp,
        fp=max(0, pred_count - precision_tp),
        fn=max(0, gold_count - recall_tp),
        pred_count=pred_count,
        gold_count=gold_count,
        precision=precision,
        recall=recall,
        f1=f1,
    )


def as_recovery(score: Any) -> ClinicalRecoveryPRF1:
    if isinstance(score, ClinicalRecoveryPRF1):
        return score
    return recovery_from_counts(
        precision_tp=score.tp,
        recall_tp=score.tp,
        pred_count=score.tp + score.fp,
        gold_count=score.tp + score.fn,
    )


def recovery_to_dict(score: ClinicalRecoveryPRF1) -> dict[str, Any]:
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "precision_tp": score.precision_tp,
        "recall_tp": score.recall_tp,
        "fp": score.fp,
        "fn": score.fn,
        "pred_count": score.pred_count,
        "gold_count": score.gold_count,
    }


def score_to_dict(score: Any, *, include_counts: bool = False) -> dict[str, Any]:
    if isinstance(score, ClinicalRecoveryPRF1):
        return recovery_to_dict(score)
    return prf1_to_dict(score, include_counts=include_counts)


def aggregate_recovery(scores: Sequence[Mapping[str, Any]]) -> ClinicalRecoveryPRF1:
    precision_tp = recall_tp = pred_count = gold_count = 0
    for score in scores:
        headline = score["headline"]
        recovery = as_recovery(headline)
        precision_tp += recovery.precision_tp
        recall_tp += recovery.recall_tp
        pred_count += recovery.pred_count
        gold_count += recovery.gold_count
    return recovery_from_counts(
        precision_tp=precision_tp,
        recall_tp=recall_tp,
        pred_count=pred_count,
        gold_count=gold_count,
    )
