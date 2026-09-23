"""v0.8.5 scorer: require cluster observation windows, not cluster spans.

A source-backed within-cluster span stays in evidence. When the reference has
no observation period, an emitted period cannot change the cluster score.
Earlier scorer versions and saved results remain frozen.
"""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_v08, finding_v084

VERSION = "finding_v085_v1"


def compatible(pred: dict[str, Any], ref: dict[str, Any], note: str) -> bool:
    if pred["measurement"]["type"] == ref["measurement"]["type"] == "cluster":
        pm = {k: v for k, v in pred["measurement"].items() if k != "occurred_at"}
        rm = {k: v for k, v in ref["measurement"].items() if k != "occurred_at"}
        if rm.get("seizures_per_cluster") is None and pm.get("seizures_per_cluster") == {
            "type": "qualitative",
            "quantity": "multiple",
        }:
            # "Multiple" only repeats the meaning of cluster; it is not a
            # measured size when the source states cadence but no size.
            pm.pop("seizures_per_cluster")
        if not exact.measurement_equal(pm, rm):
            return False
        if ref["measurement"].get("count") is not None and ref.get("period") is not None:
            if not finding_v08._period_agrees(
                pred.get("period"),
                ref.get("period"),
                note,
                pred.get("evidence", ""),
                ref.get("evidence", ""),
            ):
                return False
        if ref.get("period") is None:
            pred = {key: value for key, value in pred.items() if key != "period"}
    return finding_v084.compatible(pred, ref, note)


def score_letter(
    note: str, reference: list[dict[str, Any]], predictions: list[dict[str, Any]] | None
) -> dict[str, Any]:
    if predictions is None:
        return finding_v084.score_letter(note, reference, None)
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
