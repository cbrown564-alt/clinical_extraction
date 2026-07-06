"""Item 6 — `multiple` count-sentinel audit (zero LLM).

Resolves the cross-project divergence in how the word ``multiple`` maps to a
seizure count, and measures the *score* sensitivity on Gan validation750.

Three resolution schemes are compared:

* **dynamic** (this repo): period-dependent cluster counts {2,8,18,2} by
  week/month/year/day, and a fixed 2 for the per-cluster size.
* **fixed-2** (dissertation-recursive, ``MULTIPLE_VALUE=2.0``): rewrite
  ``multiple`` -> ``2`` before label resolution.
* **fixed-3** (dissertation-experiments, ``_MULTIPLE=3.0`` / Gan §2.6.1):
  rewrite ``multiple`` -> ``3`` before label resolution.

Predictions are held fixed (frozen validation750 artifact); only the gold
resolution changes, so the delta isolates the gold-side sentinel effect.

Outputs JSON to stdout. The audit note
``docs/research/gan_multiple_sentinel_audit_2026-07.md`` is written by hand from
the printed numbers.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026 import data, labels
from clinical_extraction.tasks.shared.epilepsy.normalization import label_to_frequency_record

ROOT = Path(__file__).resolve().parents[1]
PRED_NAME = "gan2026_8c_canonical_pipeline_v03_validation750_gpt41mini_2026-06-09.jsonl"
PRED_PATH = ROOT / "experiments" / PRED_NAME


def _resolve(label: str, *, fixed: int | None) -> float | None:
    """Resolve a label to monthly frequency. ``fixed`` rewrites ``multiple`` first."""
    if fixed is not None:
        label = re.sub(r"\bmultiple\b", str(fixed), label)
    try:
        rec = label_to_frequency_record(label)
    except (ValueError, KeyError):
        return None
    return rec.monthly_frequency


def _score(
    gold_by_idx: dict[int, str],
    pred_monthly_by_idx: dict[int, float],
    *,
    fixed: int | None,
) -> dict[str, Any]:
    """Purist/Pragmatic accuracy over validation750 under one gold-resolution scheme."""

    purist_correct = pragmatic_correct = 0
    n = 0
    bin_crossers: list[dict[str, Any]] = []
    for idx, gold_label in gold_by_idx.items():
        gold_dyn = _resolve(gold_label, fixed=None)
        gold_alt = _resolve(gold_label, fixed=fixed)
        pred = pred_monthly_by_idx.get(idx)
        if pred is None or gold_dyn is None or gold_alt is None:
            continue
        n += 1
        # Bin both gold variants under each method.
        dyn_purist = labels.map_purist(gold_dyn)
        alt_purist = labels.map_purist(gold_alt)
        dyn_prag = labels.map_pragmatic(gold_dyn)
        alt_prag = labels.map_pragmatic(gold_alt)
        pred_purist = labels.map_purist(pred)
        pred_prag = labels.map_pragmatic(pred)
        if pred_purist == alt_purist:
            purist_correct += 1
        if pred_prag == alt_prag:
            pragmatic_correct += 1
        # A bin-crosser is a multiple/cluster row whose category moves under the
        # alternative resolution (these are the rows that can change the score).
        lab_lower = gold_label.lower()
        if gold_dyn != gold_alt and ("cluster" in lab_lower or "multiple" in lab_lower):
            if dyn_purist != alt_purist or dyn_prag != alt_prag:
                bin_crossers.append(
                    {
                        "source_row_index": idx,
                        "gold_label": gold_label,
                        "gold_monthly_dynamic": gold_dyn,
                        "gold_monthly_alt": gold_alt,
                        "purist_dynamic": dyn_purist,
                        "purist_alt": alt_purist,
                        "pragmatic_dynamic": dyn_prag,
                        "pragmatic_alt": alt_prag,
                        "predicted_monthly": pred,
                        "pred_purist": pred_purist,
                    }
                )
    return {
        "scheme": "dynamic" if fixed is None else f"fixed-{fixed}",
        "n": n,
        "purist_accuracy": purist_correct / n if n else 0.0,
        "pragmatic_accuracy": pragmatic_correct / n if n else 0.0,
        "bin_crossers": bin_crossers,
    }


def main() -> None:
    recs = data.load_records_for_split("validation")
    gold_by_idx = {r.source_row_index: r.gold_label for r in recs}

    rows = [
        json.loads(line)
        for line in PRED_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    pred_monthly_by_idx: dict[int, float] = {}
    for r in rows:
        comp = r.get("comparison") or {}
        pm = comp.get("predicted_monthly_frequency")
        if pm is not None:
            pred_monthly_by_idx[r["source_row_index"]] = float(pm)

    # Sanity: the prediction artifact's stored gold monthly must equal our dynamic resolve.
    mismatches = 0
    for r in rows:
        comp = r.get("comparison") or {}
        stored = comp.get("gold_monthly_frequency")
        idx = r["source_row_index"]
        ours = _resolve(gold_by_idx.get(idx, ""), fixed=None)
        if stored is not None and ours is not None and abs(float(stored) - ours) > 1e-6:
            mismatches += 1
    n_match = len(rows) - mismatches
    print(
        f"[audit] dynamic-resolution reproduces stored gold monthly "
        f"on {n_match}/{len(rows)} rows"
    )

    # Count mover rows.
    def _has(label: str | None, sub: str) -> bool:
        return sub in (label or "").lower()

    cluster = [r for r in recs if _has(r.gold_label, "cluster")]
    mult = [r for r in recs if _has(r.gold_label, "multiple")]
    both = [r for r in recs if _has(r.gold_label, "cluster") and _has(r.gold_label, "multiple")]
    mult_cluster_count = [r for r in recs if _has(r.gold_label, "multiple cluster")]

    results = {
        "validation_rows": len(recs),
        "cluster_rows": len(cluster),
        "multiple_rows": len(mult),
        "cluster_and_multiple_rows": len(both),
        "multiple_cluster_count_rows": len(mult_cluster_count),
        "schemes": {},
    }
    for fixed in (None, 2, 3):
        results["schemes"]["dynamic" if fixed is None else f"fixed-{fixed}"] = _score(
            gold_by_idx, pred_monthly_by_idx, fixed=fixed
        )

    # Compute deltas vs dynamic baseline.
    dyn = results["schemes"]["dynamic"]
    for key in ("fixed-2", "fixed-3"):
        alt = results["schemes"][key]
        alt["purist_accuracy_delta_vs_dynamic"] = (
            alt["purist_accuracy"] - dyn["purist_accuracy"]
        )
        alt["pragmatic_accuracy_delta_vs_dynamic"] = (
            alt["pragmatic_accuracy"] - dyn["pragmatic_accuracy"]
        )

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
