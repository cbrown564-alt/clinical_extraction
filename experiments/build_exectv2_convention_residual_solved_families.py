"""Convention-vs-genuine residual decomposition for the two SOLVED key families.

Companion to build_exectv2_convention_residual_decomposition.py. Confirms whether
Prescription (verifier v0.1, F1 0.817) and Investigations (verifier v0.1, F1
0.872) cleared target because their residual is structurally easier (grounded,
genuine) rather than because of lucky convention alignment.

Same test, adapted to the component-table scorers:
  - clinical identity = drug name (Prescription) / modality (Investigations).
  - attribute convention = identity present on BOTH sides in the same letter,
        only a sub-attribute disagrees (dose/frequency/regimen-class; performed/
        result/EEG-type).
  - genuine = identity present on only one side (true miss / true over-emission).

No model calls. Reconstructs the clinical-headline residual using the scorer's
own component-key functions and validates TP/FP/FN against the headline F1.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    _investigation_modality_key,
    _prescription_component_key,
)

PRESC_JSONL = Path("experiments/exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618.jsonl")
INV_JSONL = Path("experiments/exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.jsonl")
OUT_JSON = Path("experiments/exectv2_convention_residual_solved_families_dev140_20260618.json")


def _rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _ann(mention: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(
        attributes=mention.get("attributes", {}),
        text=mention.get("text", ""),
        raw_text=mention.get("text", ""),
    )


def _f1(tp: int, fp: int, fn: int) -> float:
    return 2 * tp / (2 * tp + fp + fn) if tp else 0.0


def _decompose(rows: list[dict[str, Any]], headline_keys, identity_of, family: str, candidate: str, f1: float) -> dict[str, Any]:
    tot = Counter()
    fn_bucket = Counter()
    fp_bucket = Counter()
    examples: dict[str, list[str]] = {"attribute": []}

    for row in rows:
        lid = row["letter_id"]
        gold = Counter(headline_keys(row.get("gold_mentions", [])))
        pred = Counter(headline_keys(row.get("predicted_mentions", [])))
        tot["tp"] += sum((gold & pred).values())
        fn = gold - pred
        fp = pred - gold
        tot["fn"] += sum(fn.values())
        tot["fp"] += sum(fp.values())

        fn_id = Counter(identity_of(k) for k, n in fn.items() for _ in range(n))
        fp_id = Counter(identity_of(k) for k, n in fp.items() for _ in range(n))
        shared = fn_id & fp_id
        for ident, n in shared.items():
            fn_bucket["attribute"] += n
            fp_bucket["attribute"] += n
            if len(examples["attribute"]) < 12:
                examples["attribute"].append(f"{lid}: {ident}")
        fn_bucket["genuine"] += sum((fn_id - shared).values())
        fp_bucket["genuine"] += sum((fp_id - shared).values())

    return {
        "family": family,
        "candidate": candidate,
        "headline_f1": f1,
        "counts": dict(tot),
        "reconstructed_f1": round(_f1(tot["tp"], tot["fp"], tot["fn"]), 4),
        "fn_total": sum(fn_bucket.values()),
        "fp_total": sum(fp_bucket.values()),
        "fn_buckets": dict(fn_bucket),
        "fp_buckets": dict(fp_bucket),
        "examples": examples,
    }


def _presc_headline_keys(mentions: list[dict[str, Any]]) -> list[Any]:
    keys: list[Any] = []
    for m in mentions:
        if m.get("entity", "Prescription") != "Prescription":
            continue
        key = _prescription_component_key(_ann(m), "clinical_headline", "")
        if key is not None:
            keys.append(key)
    return keys


def _inv_headline_keys(mentions: list[dict[str, Any]]) -> list[Any]:
    keys: list[Any] = []
    for m in mentions:
        if m.get("entity", "Investigations") != "Investigations":
            continue
        for modality in ("EEG", "MRI", "CT"):
            mk = _investigation_modality_key(_ann(m), modality)
            if mk is not None:
                keys.append(mk)
    return keys


def main() -> None:
    presc = _decompose(
        _rows(PRESC_JSONL), _presc_headline_keys, lambda k: k[1], "Prescription", "prescription verifier v0.1", 0.817
    )
    inv = _decompose(
        _rows(INV_JSONL), _inv_headline_keys, lambda k: k[0], "Investigations", "investigations verifier v0.1", 0.872
    )
    out = {"generated": "2026-06-18", "split": "dev", "letters": 140, "prescription": presc, "investigations": inv}
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    for d in (presc, inv):
        c = d["counts"]
        print(f"\n=== {d['family']} ({d['candidate']}) ===")
        print(f"  reconstructed tp/fp/fn = {c['tp']}/{c['fp']}/{c['fn']}  (F1 {d['reconstructed_f1']} vs reported {d['headline_f1']})")
        print(f"  FN buckets ({d['fn_total']}): {d['fn_buckets']}")
        print(f"  FP buckets ({d['fp_total']}): {d['fp_buckets']}")
        conv = d["fn_buckets"].get("attribute", 0) + d["fp_buckets"].get("attribute", 0)
        total = d["fn_total"] + d["fp_total"]
        print(f"  attribute-convention share of residual = {conv}/{total} = {conv/total:.1%}" if total else "  no residual")
    print(f"\nWrote {OUT_JSON}")


if __name__ == "__main__":
    main()
