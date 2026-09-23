"""Reconcile every saved R8/v0.8 unmatched finding on Gan dev750.

The output is a source-bearing local audit, not a new score. A pair in the
audit means its evidence quotations overlap in the source; it is not assumed
to be a clinically equivalent finding. No model or holdout access is used.
"""

from __future__ import annotations

import json
from collections import Counter
from functools import cache
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_v08 as v08,
)

ROOT = Path("runs/seizure_finding_annotation_v0_8/dev750_r8_saved")
SCORE = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8/dev750_r8_saved/score.json"
)
OUT = ROOT / "mixed_error_evidence_audit.json"


def pair_weight(gold: dict[str, Any], prediction: dict[str, Any], note: str) -> int:
    score = 0
    gm, pm = gold["measurement"], prediction["measurement"]
    if exact.label_key(gold["event"]["type"]) == exact.label_key(prediction["event"]["type"]):
        score += 16
    if gm["type"] == pm["type"]:
        score += 12
    if exact.measurement_equal(gm, pm):
        score += 8
    if gm["type"] == pm["type"] == "count" and exact.quantity_equal(
        gm.get("count"), pm.get("count")
    ):
        score += 16
    if gm["type"] == pm["type"] == "rate" and exact.quantity_equal(
        gm.get("count"), pm.get("count")
    ) and exact.duration_equal(gm.get("per"), pm.get("per")):
        score += 16
    if gm["type"] == pm["type"] == "cluster":
        for field in ("count", "seizures_per_cluster"):
            if gm.get(field) is not None and exact.quantity_equal(gm.get(field), pm.get(field)):
                score += 8
    if gold.get("timing", "current") == prediction.get("timing", "current"):
        score += 4
    if gold["event"].get("seizure_status", "stated") == prediction["event"].get(
        "seizure_status", "stated"
    ):
        score += 4
    if exact.period_equivalent(gold.get("period"), prediction.get("period")):
        score += 4
    if v08.compatible(prediction, gold, note):
        raise ValueError("An unmatched finding pair satisfies the scorer")
    return score


def select_overlap_pairs(
    gold: list[dict[str, Any]], prediction: list[dict[str, Any]], note: str
) -> list[tuple[int, int]]:
    """Maximum overlap pairing, breaking ties toward similar attributes."""
    edges = {
        i: [
            (j, pair_weight(g, p, note))
            for j, p in enumerate(prediction)
            if exact.evidence_overlap(note, g["evidence"], p["evidence"])
        ]
        for i, g in enumerate(gold)
    }

    @cache
    def best(i: int, used: int) -> tuple[int, int, tuple[tuple[int, int], ...]]:
        if i == len(gold):
            return 0, 0, ()
        result = best(i + 1, used)
        for j, weight in edges[i]:
            if used & (1 << j):
                continue
            rest = best(i + 1, used | (1 << j))
            candidate = (rest[0] + 1, rest[1] + weight, ((i, j),) + rest[2])
            if candidate[:2] > result[:2]:
                result = candidate
        return result

    return list(best(0, 0)[2])


def main() -> None:
    bundle = json.loads((ROOT / "review_bundle.json").read_text())
    score = json.loads(SCORE.read_text())
    rows = bundle["rows"]
    if len(rows) != 750 or len(score["letters"]) != 750:
        raise ValueError("Development coverage changed")
    if {key: sum(row[f"v08_{key}"] for row in rows) for key in ("tp", "fp", "fn")} != {
        key: score["finding_v08"][key] for key in ("tp", "fp", "fn")
    }:
        raise ValueError("Review bundle and score disagree")
    audit: list[dict[str, Any]] = []
    dimensions: Counter[str] = Counter()
    for row in rows:
        if not row["v08_fp"] or not row["v08_fn"]:
            continue
        gold = [f for f in row["reference"] if f["id"] in row["unmatched_reference_ids"]]
        prediction = [f for f in row["predicted"] if f["id"] in row["unmatched_prediction_ids"]]
        if len(gold) != row["v08_fn"] or len(prediction) != row["v08_fp"]:
            raise ValueError(f"Unmatched finding IDs disagree on {row['source_row_index']}")
        note = row["note"]
        all_edges = [
            {
                "gold_id": g["id"],
                "prediction_id": p["id"],
                "diffs": exact.attribute_diffs(p, g, note),
            }
            for g in gold
            for p in prediction
            if exact.evidence_overlap(note, g["evidence"], p["evidence"])
        ]
        pairs = []
        for gi, pi in select_overlap_pairs(gold, prediction, note):
            g, p = gold[gi], prediction[pi]
            diffs = exact.attribute_diffs(p, g, note)
            dimensions.update(diffs)
            pairs.append(
                {
                    "gold_id": g["id"],
                    "prediction_id": p["id"],
                    "diffs": diffs,
                    "gold": g,
                    "prediction": p,
                }
            )
        audit.append(
            {
                "source_row_index": row["source_row_index"],
                "source_id": row["source_id"],
                "note": note,
                "missed_count": len(gold),
                "extra_count": len(prediction),
                "any_exact_source_overlap": bool(all_edges),
                "all_overlap_edges": all_edges,
                "selected_overlap_pairs": pairs,
                "unpaired_gold": [f for f in gold if f["id"] not in {p["gold_id"] for p in pairs}],
                "unpaired_predictions": [
                    f for f in prediction if f["id"] not in {p["prediction_id"] for p in pairs}
                ],
            }
        )
    output = {
        "source": str(ROOT / "review_bundle.json"),
        "score": str(SCORE),
        "scope": (
            "Gan synthetic dev750, saved R8, v0.8 label and scorer; "
            "exact quotation overlap only"
        ),
        "letters_with_both": len(audit),
        "letters_with_any_exact_overlap": sum(row["any_exact_source_overlap"] for row in audit),
        "misses_in_mixed_letters": sum(row["missed_count"] for row in audit),
        "extras_in_mixed_letters": sum(row["extra_count"] for row in audit),
        "selected_overlap_pairs": sum(len(row["selected_overlap_pairs"]) for row in audit),
        "selected_pair_attribute_diffs": dict(dimensions),
        "rows": audit,
    }
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in output.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
