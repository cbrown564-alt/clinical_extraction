"""v0.8.4 scorer: a cluster's occurrence date is unscored context.

All other matching rules remain those of v0.8.2. Earlier scores are frozen.
"""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_v082

VERSION = "finding_v084_v1"


def compatible(pred: dict[str, Any], ref: dict[str, Any], note: str) -> bool:
    pm, rm = pred["measurement"], ref["measurement"]
    if pm["type"] == rm["type"] == "cluster":
        pred = {**pred, "measurement": {k: v for k, v in pm.items() if k != "occurred_at"}}
        ref = {**ref, "measurement": {k: v for k, v in rm.items() if k != "occurred_at"}}
    return finding_v082.compatible(pred, ref, note)


def score_letter(
    note: str, reference: list[dict[str, Any]], predictions: list[dict[str, Any]] | None
) -> dict[str, Any]:
    if predictions is None:
        return finding_v082.score_letter(note, reference, None)
    from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
        finding_matching_v07 as exact,
    )

    edges = {
        i: [j for j, ref in enumerate(reference) if compatible(pred, ref, note)]
        for i, pred in enumerate(predictions)
    }
    matching = exact.maximum_matching(edges, len(predictions))
    return {
        "usable": True,
        "tp": len(matching),
        "fp": len(predictions) - len(matching),
        "fn": len(reference) - len(matching),
        "predicted": len(predictions),
        "reference": len(reference),
        "pairs": [[predictions[i]["id"], reference[j]["id"]] for i, j in sorted(matching.items())],
    }
