"""v0.8.2 saved-response scorer: seizure-free duration is the scored value.

The co-stated since anchor remains source detail. The v0.8 scorer and all
previous references remain frozen.
"""

from __future__ import annotations

from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_v08 as old,
)

VERSION = "finding_v082_v1"


def compatible(pred: dict[str, Any], ref: dict[str, Any], note: str) -> bool:
    pm, rm = pred["measurement"], ref["measurement"]
    if pm["type"] == rm["type"] == "seizure_free" and (
        pm.get("duration") is not None or rm.get("duration") is not None
    ):
        if not exact.evidence_overlap(note, pred.get("evidence", ""), ref.get("evidence", "")):
            return False
        if pred.get("timing", "current") != ref.get("timing", "current"):
            return False
        if exact.label_key(pred["event"]["type"]) != exact.label_key(ref["event"]["type"]):
            if "events" not in {
                exact.norm_text(pred["event"]["type"]),
                exact.norm_text(ref["event"]["type"]),
            }:
                return False
        if not exact.duration_equal(pm.get("duration"), rm.get("duration")):
            return False
        # Keep the old scorer's source support and period rules. A copy without
        # either anchor makes the anchor invisible to its native equality check.
        pred_without_anchor = {**pred, "measurement": {**pm, "since": None}}
        ref_without_anchor = {**ref, "measurement": {**rm, "since": None}}
        return old.compatible(pred_without_anchor, ref_without_anchor, note)
    return old.compatible(pred, ref, note)


def score_letter(
    note: str, reference: list[dict[str, Any]], predictions: list[dict[str, Any]] | None
) -> dict[str, Any]:
    if predictions is None:
        return old.score_letter(note, reference, None)
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
