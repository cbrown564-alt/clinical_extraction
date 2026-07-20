from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Iterable

from pydantic import BaseModel


class PRF1(BaseModel):
    """Precision / recall / F1 over a set of true-positive, false-positive, and
    false-negative counts. Task-neutral: works for any matching regime that can
    reduce to tp/fp/fn."""

    model_config = {"frozen": True}

    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float

    @property
    def gold_count(self) -> int:
        return self.tp + self.fn

    @property
    def pred_count(self) -> int:
        return self.tp + self.fp


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def f1_score(precision: float, recall: float) -> float:
    return safe_div(2 * precision * recall, precision + recall)


def prf1_from_counts(tp: int, fp: int, fn: int) -> PRF1:
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    return PRF1(
        tp=tp,
        fp=fp,
        fn=fn,
        precision=precision,
        recall=recall,
        f1=f1_score(precision, recall),
    )


def multiset_prf1(gold_keys: Iterable[Hashable], pred_keys: Iterable[Hashable]) -> PRF1:
    """Score predicted items against gold items by multiset match on a hashable key.

    A predicted key matches a gold key when they are equal; multiplicity is
    respected, so two predicted copies of a key with one gold copy yield one
    true positive and one false positive. Use this for unaligned mention sets
    (e.g. multiple entity mentions per document) where order does not matter."""

    gold = Counter(gold_keys)
    pred = Counter(pred_keys)
    tp = sum((gold & pred).values())
    fp = sum((pred - gold).values())
    fn = sum((gold - pred).values())
    return prf1_from_counts(tp, fp, fn)


def sum_prf1(parts: Iterable[PRF1]) -> PRF1:
    """Aggregate per-unit PRF1 results into a single micro-averaged PRF1 by
    summing tp/fp/fn. Use to roll per-document mention scores up to a corpus
    per-item score."""

    tp = fp = fn = 0
    for part in parts:
        tp += part.tp
        fp += part.fp
        fn += part.fn
    return prf1_from_counts(tp, fp, fn)
