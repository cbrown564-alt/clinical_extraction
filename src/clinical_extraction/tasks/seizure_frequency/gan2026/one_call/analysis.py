"""Prespecified all-note agreement and paired expanded-minus-minimal uncertainty."""

from __future__ import annotations

import math
import random
from typing import Any

SEED = 20260913
BOOTSTRAPS = 10000
METHODS = ("purist", "pragmatic")


def wilson(successes: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    p = successes / total
    z = 1.959963984540054
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, centre - half), min(1.0, centre + half)]


def agreement(correct: list[bool]) -> dict[str, Any]:
    n = len(correct)
    hits = sum(correct)
    return {"correct": hits, "denominator": n, "agreement": hits / n, "ci95": wilson(hits, n)}


def paired(expanded: list[bool], minimal: list[bool]) -> dict[str, Any]:
    """Paired percentile bootstrap over letters; every scheduled letter is included."""
    if len(expanded) != len(minimal) or not expanded:
        raise ValueError("Paired conditions need the same nonempty letters")
    differences = [int(e) - int(m) for e, m in zip(expanded, minimal, strict=True)]
    n = len(differences)
    rng = random.Random(SEED)
    draws = sorted(sum(rng.choices(differences, k=n)) / n for _ in range(BOOTSTRAPS))
    return {
        "expanded_minus_minimal": sum(differences) / n,
        "expanded_wins": differences.count(1),
        "minimal_wins": differences.count(-1),
        "ties": differences.count(0),
        "denominator": n,
        "ci95": [draws[int(0.025 * BOOTSTRAPS) - 1], draws[int(0.975 * BOOTSTRAPS) - 1]],
        "bootstrap": {"seed": SEED, "replicates": BOOTSTRAPS, "unit": "letter"},
    }
