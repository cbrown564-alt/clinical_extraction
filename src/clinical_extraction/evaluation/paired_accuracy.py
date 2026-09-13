"""Paired accuracy tests for one gold label per letter."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import comb, sqrt


@dataclass(frozen=True)
class PairedAccuracyTest:
    """Exact McNemar and a Wald interval on the accuracy difference."""

    n: int
    correct_a: int
    correct_b: int
    a_only: int
    b_only: int
    p_value: float
    accuracy_delta: float
    delta_ci_low: float
    delta_ci_high: float


def exact_mcnemar_p(a_only: int, b_only: int) -> float:
    """Two-sided exact McNemar p-value on the discordant pair counts."""

    if a_only < 0 or b_only < 0:
        raise ValueError("discordant counts must be non-negative")
    discordant = a_only + b_only
    if discordant == 0:
        return 1.0
    k = min(a_only, b_only)
    tail = sum(comb(discordant, i) for i in range(k + 1)) / (2**discordant)
    return min(1.0, 2.0 * tail)


def paired_accuracy_test(
    a_correct: Sequence[bool],
    b_correct: Sequence[bool],
    *,
    z: float = 1.959963984540054,
) -> PairedAccuracyTest:
    """Compare two paired correctness vectors on the same letters."""

    if len(a_correct) != len(b_correct):
        raise ValueError("paired correctness vectors must have the same length")
    n = len(a_correct)
    if n == 0:
        raise ValueError("paired correctness vectors must not be empty")
    a_only = 0
    b_only = 0
    correct_a = 0
    correct_b = 0
    for left, right in zip(a_correct, b_correct, strict=True):
        correct_a += int(left)
        correct_b += int(right)
        if left and not right:
            a_only += 1
        elif right and not left:
            b_only += 1
    delta = (correct_a - correct_b) / n
    discordant = a_only + b_only
    if discordant == 0:
        low = high = 0.0
    else:
        variance = (discordant - ((a_only - b_only) ** 2) / n) / (n**2)
        se = sqrt(max(variance, 0.0))
        low = delta - z * se
        high = delta + z * se
    return PairedAccuracyTest(
        n=n,
        correct_a=correct_a,
        correct_b=correct_b,
        a_only=a_only,
        b_only=b_only,
        p_value=exact_mcnemar_p(a_only, b_only),
        accuracy_delta=delta,
        delta_ci_low=low,
        delta_ci_high=high,
    )
