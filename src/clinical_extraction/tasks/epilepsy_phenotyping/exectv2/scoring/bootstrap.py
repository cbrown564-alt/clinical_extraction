"""Cluster (per-letter) bootstrap confidence intervals for ExECTv2 scoring."""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class BootstrapCI:
    point: float
    lower: float
    upper: float
    reps: int


def f1_from_counts(tp: int, fp: int, fn: int) -> float:
    denom = 2 * tp + fp + fn
    return (2 * tp / denom) if denom else 0.0


def percentile_ci(samples: Sequence[float], *, alpha: float = 0.05) -> tuple[float, float]:
    """Percentile CI from pre-sorted or unsorted bootstrap samples."""
    ordered = sorted(samples)
    n = len(ordered)
    lo = ordered[int((alpha / 2) * n)]
    hi = ordered[min(n - 1, int((1 - alpha / 2) * n))]
    return lo, hi


def cluster_bootstrap(
    clusters: Sequence[T],
    aggregate: Callable[[Sequence[T]], float],
    *,
    reps: int = 1000,
    seed: int = 12345,
    alpha: float = 0.05,
) -> BootstrapCI:
    """Cluster bootstrap CI: resample clusters with replacement, re-aggregate."""
    n = len(clusters)
    point = aggregate(clusters) if n else 0.0
    if n == 0:
        return BootstrapCI(point=round(point, 4), lower=0.0, upper=0.0, reps=reps)
    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(reps):
        sample = [clusters[rng.randrange(n)] for _ in range(n)]
        samples.append(aggregate(sample))
    lo, hi = percentile_ci(samples, alpha=alpha)
    return BootstrapCI(point=round(point, 4), lower=round(lo, 4), upper=round(hi, 4), reps=reps)


def bootstrap_f1_ci(
    counts: Sequence[tuple[int, int, int]],
    *,
    reps: int = 1000,
    seed: int = 12345,
    alpha: float = 0.05,
) -> BootstrapCI:
    """Cluster (per-letter) bootstrap CI for a micro-averaged F1."""

    def aggregate(sample: Sequence[tuple[int, int, int]]) -> float:
        tp = sum(c[0] for c in sample)
        fp = sum(c[1] for c in sample)
        fn = sum(c[2] for c in sample)
        return f1_from_counts(tp, fp, fn)

    return cluster_bootstrap(counts, aggregate, reps=reps, seed=seed, alpha=alpha)


def bootstrap_cluster_metrics_ci(
    clusters: Sequence[T],
    metrics: Mapping[str, Callable[[Sequence[T]], float]],
    *,
    reps: int = 1000,
    seed: int = 12345,
    alpha: float = 0.05,
) -> dict[str, tuple[float, float]]:
    """Percentile bootstrap CI for multiple metrics over the same cluster resamples."""
    if not clusters:
        return {name: (0.0, 0.0) for name in metrics}
    rng = random.Random(seed)
    n = len(clusters)
    sample_lists: dict[str, list[float]] = {name: [] for name in metrics}
    for _ in range(reps):
        sample = [clusters[rng.randrange(n)] for _ in range(n)]
        for name, aggregate in metrics.items():
            sample_lists[name].append(aggregate(sample))
    return {
        name: (
            round(percentile_ci(samples, alpha=alpha)[0], 4),
            round(percentile_ci(samples, alpha=alpha)[1], 4),
        )
        for name, samples in sample_lists.items()
    }
