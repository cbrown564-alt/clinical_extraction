"""Prespecified all-note agreement and paired uncertainty for the one-call paper."""

from __future__ import annotations

import math
import random
from collections import Counter
from typing import Any

ANALYSIS_VERSION = "one_shot_analysis_v1"
SEED = 20260913
BOOTSTRAPS = 10000


def wilson(successes: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    p = successes / total
    z = 1.959963984540054
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, centre - half), min(1.0, centre + half)]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """One entry per scheduled note, including every failed/missing condition."""
    if not rows:
        raise ValueError("No scheduled notes")
    report: dict[str, Any] = {
        "analysis_version": ANALYSIS_VERSION,
        "scheduled_notes": len(rows),
        "sampling_unit": "letter",
        "patient_linkage": "unavailable",
        "source_family_linkage": "unavailable; intervals assume independent letters",
        "absolute_interval": "Wilson 95%",
        "paired_interval": "paired percentile bootstrap 95%",
        "bootstrap_seed": SEED,
        "bootstrap_replicates": BOOTSTRAPS,
        "conditions": {},
        "paired": {},
    }
    for condition in ("rich", "simple"):
        results = [row[condition] for row in rows]
        valid = [r for r in results if r["schema_valid"]]
        usable = sum(r["failure"] is None for r in results)
        quote_slots = sum(r["quote_slots"] for r in results)
        summary: dict[str, Any] = {
            "scheduled": len(rows),
            "usable": usable,
            "coverage": usable / len(rows),
            "responses_received": sum(r["received"] for r in results),
            "schema_valid": len(valid),
            "failures": dict(Counter(r["failure"] for r in results if r["failure"])),
            "quote_slots": quote_slots,
            "exact_quotes": sum(r["exact_quotes"] for r in results),
            "notes_all_quotes_exact": sum(r["all_quotes_exact"] for r in results),
            "no_evidence_states": sum(r["no_evidence_state"] for r in results),
            "finding_counts": dict(Counter(r["finding_count"] for r in valid)),
            "finding_types": dict(Counter(k for r in valid for k in r["finding_types"])),
            "finding_certainties": dict(
                Counter(k for r in valid for k in r["finding_certainties"])
            ),
            "finding_temporalities": dict(
                Counter(k for r in valid for k in r["finding_temporalities"])
            ),
        }
        for method in ("purist", "pragmatic"):
            correct = sum(r[method + "_correct"] for r in results)
            summary[method] = {
                "correct": correct,
                "denominator": len(rows),
                "agreement": correct / len(rows),
                "ci95": wilson(correct, len(rows)),
                "conditional_agreement": correct / usable if usable else None,
            }
        report["conditions"][condition] = summary
    for method in ("purist", "pragmatic"):
        differences = [
            int(r["rich"][method + "_correct"]) - int(r["simple"][method + "_correct"])
            for r in rows
        ]
        rng = random.Random(SEED)
        draws = sorted(
            sum(rng.choices(differences, k=len(rows))) / len(rows) for _ in range(BOOTSTRAPS)
        )
        report["paired"][method] = {
            "rich_minus_simple": sum(differences) / len(rows),
            "rich_wins": differences.count(1),
            "simple_wins": differences.count(-1),
            "ties": differences.count(0),
            "denominator": len(rows),
            "ci95": [draws[249], draws[9749]],
            "degenerate_bootstrap": len(set(differences)) == 1,
        }
    return report
