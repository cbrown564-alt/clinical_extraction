"""Score event labels, seizure subtypes and measurements on saved R8 versus v0.8.1.

The whole-finding score and its pairs are frozen inputs. Remaining predictions
and gold findings are paired one-to-one only when their exact source quotations
overlap. This is a development diagnostic, not a new model evaluation.
"""

from __future__ import annotations

import json
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r8 as r8,
)

REVIEW = Path("runs/seizure_finding_annotation_v0_8_1/dev750_r8_saved/review_bundle.json")
OUTPUT = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_1/"
    "dev750_r8_saved/component_score.json"
)
VERSION = "finding_components_v081_v2"


def measurement_agrees(pred: dict[str, Any], gold: dict[str, Any]) -> bool:
    """Native measurement kind, value and denominator; observation window is separate."""
    return exact.measurement_equal(pred["measurement"], gold["measurement"])


def event_agrees(pred: dict[str, Any], gold: dict[str, Any]) -> bool:
    return exact.label_key(pred["event"]["type"]) == exact.label_key(gold["event"]["type"])


def subtype_key(finding: dict[str, Any]) -> tuple[str, ...]:
    """Named seizure features, excluding cluster and affected-day count units."""
    words = {
        exact._lemma(word)
        for word in r8.TYPE_WORDS.findall(finding["event"]["type"])
    }
    return tuple(sorted(words - {"cluster", "seizure day"}))


def subtype_agrees(pred: dict[str, Any], gold: dict[str, Any]) -> bool:
    return subtype_key(pred) == subtype_key(gold)


def residual_pairs(
    note: str, gold: list[dict[str, Any]], pred: list[dict[str, Any]]
) -> list[tuple[int, int]]:
    """Maximise source-aligned pairs, then agreement of their scored components."""
    edges = {
        gi: [
            pi
            for pi, p in enumerate(pred)
            if exact.evidence_overlap(note, p["evidence"], g["evidence"])
        ]
        for gi, g in enumerate(gold)
    }

    @lru_cache(None)
    def solve(gi: int, used: int) -> tuple[int, tuple[tuple[int, int], ...]]:
        if gi == len(gold):
            return 0, ()
        best = solve(gi + 1, used)
        for pi in edges[gi]:
            if used & (1 << pi):
                continue
            later, pairs = solve(gi + 1, used | (1 << pi))
            weight = (
                10_000
                + 100 * measurement_agrees(pred[pi], gold[gi])
                + 50 * event_agrees(pred[pi], gold[gi])
                + 25 * subtype_agrees(pred[pi], gold[gi])
                + 10 * (pred[pi].get("timing") == gold[gi].get("timing"))
            )
            option = later + weight, ((gi, pi), *pairs)
            if option[0] > best[0]:
                best = option
        return best

    return list(solve(0, 0)[1])


def score_row(row: dict[str, Any]) -> dict[str, Any]:
    gold = {f["id"]: f for f in row["reference"]}
    pred = {f["id"]: f for f in row["predicted"]}
    anchored = [(gid, pid) for pid, gid in row["pairs"]]
    used_gold = {gid for gid, _ in anchored}
    used_pred = {pid for _, pid in anchored}
    remaining_gold = [f for f in row["reference"] if f["id"] not in used_gold]
    remaining_pred = [f for f in row["predicted"] if f["id"] not in used_pred]
    aligned = anchored + [
        (remaining_gold[gi]["id"], remaining_pred[pi]["id"])
        for gi, pi in residual_pairs(row["note"], remaining_gold, remaining_pred)
    ]
    pairs = [
        {
            "gold_id": gid,
            "prediction_id": pid,
            "measurement_correct": measurement_agrees(pred[pid], gold[gid]),
            "subtype_correct": subtype_agrees(pred[pid], gold[gid]),
            "event_correct": event_agrees(pred[pid], gold[gid]),
        }
        for gid, pid in aligned
    ]
    aligned_gold = {pair["gold_id"] for pair in pairs}
    aligned_pred = {pair["prediction_id"] for pair in pairs}
    return {
        "source_row_index": row["source_row_index"],
        "usable": row["usable"],
        "pairs": pairs,
        "unpaired_gold": [f["id"] for f in row["reference"] if f["id"] not in aligned_gold],
        "unpaired_predictions": [
            f["id"] for f in row["predicted"] if f["id"] not in aligned_pred
        ],
    }


def aggregate(rows: list[dict[str, Any]], review: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "version": VERSION,
        "dataset": "Gan synthetic dev750",
        "reference": "seizure_finding_annotation_v0.8.1",
        "predictions": "saved R8 projected under v0.8",
        "letters": len(rows),
        "usable_letters": sum(row["usable"] for row in rows),
        "aligned_pairs": sum(len(row["pairs"]) for row in rows),
        "unpaired_gold": sum(len(row["unpaired_gold"]) for row in rows),
        "unpaired_predictions": sum(len(row["unpaired_predictions"]) for row in rows),
    }
    for name, field in (
        ("measurement", "measurement_correct"),
        ("subtype", "subtype_correct"),
        ("event", "event_correct"),
    ):
        tp = sum(pair[field] for row in rows for pair in row["pairs"])
        fp = sum(len(row["unpaired_predictions"]) for row in rows) + sum(
            not pair[field] for row in rows for pair in row["pairs"]
        )
        fn = sum(len(row["unpaired_gold"]) for row in rows) + sum(
            not pair[field] for row in rows for pair in row["pairs"]
        )
        result[name] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
        }
    assert result["measurement"]["tp"] + result["measurement"]["fn"] == sum(
        len(row["reference"]) for row in review
    )
    assert result["event"]["tp"] + result["event"]["fp"] == sum(
        len(row["predicted"]) for row in review
    )
    return result


def main() -> None:
    source_bytes = REVIEW.read_bytes()
    source = json.loads(source_bytes)
    review = source["rows"]
    if len(review) != 750 or source["aggregate"]["tp"] != 1019:
        raise ValueError("Unexpected saved v0.8.1 development bundle")
    rows = [score_row(row) for row in review]
    summary = aggregate(rows, review)
    summary.update(
        {
            "split": "dev750",
            "model_prompt": "one_shot_frequency_v2_measurements_r8",
            "replay_mode": "saved R8 responses, v0.8 projection",
            "repair_policy": "no additional repair",
            "source_review_sha256": sha256(source_bytes).hexdigest(),
            "whole_finding": {
                key: source["aggregate"][key] for key in ("tp", "fp", "fn")
            },
        }
    )
    result = {"aggregate": summary, "rows": rows}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result["aggregate"], indent=2))


if __name__ == "__main__":
    main()
