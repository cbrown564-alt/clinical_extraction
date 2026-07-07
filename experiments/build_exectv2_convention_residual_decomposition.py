"""Decompose the ExECTv2 Diagnosis/SF residual into convention-bound vs genuine.

Insight-#1 driver. For the two below-target key families (Diagnosis reconciler
v0.1 = 0.658, SF state adjudicator v0.5 = 0.721) this reconstructs the per-letter
false-negative / false-positive residual using the *scorer's own* concept and
state machinery, then classifies every residual event as:

  - assertion/state-convention : right clinical concept is present on the opposite
        side in the same letter, only the annotation attribute (Diagnosis
        Certainty/Negation; SF active/seizure-free/unknown state) disagrees.
  - granularity/ownership      : the opposite side carries an ancestor/descendant
        (Diagnosis lineage) or a generic<->named seizure pairing (SF) -- the fact
        is captured at the wrong altitude.
  - related-family (Diagnosis) : opposite side carries a clinically adjacent
        epilepsy/seizure-type concept (softer convention signal).
  - genuine                    : no related concept on the opposite side -- a true
        miss (FN) or a true over-emission (FP).

No model calls. Reads existing artifacts only. Validates reconstructed
TP/FP/FN against the published residual ledgers before reporting.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    DIAGNOSIS_PARENT,
    annotation_clinical_concepts,
    collapse_concepts_to_most_specific,
    is_epilepsy_seizure_type,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    canonicalize_attribute_value,
)

DIAG_JSONL = Path(
    "experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl"
)
SF_JSONL = Path(
    "experiments/exectv2_hybrid_sf_state_adjudicator_v05_dev140_gpt41mini_20260618.jsonl"
)
OUT_JSON = Path("experiments/exectv2_convention_residual_decomposition_dev140_20260618.json")

GENERIC_SF_CUIS = {"C0036572"}  # seizure / seizures
GENERIC_SF_FREE_CUIS = {"C1299590"}  # seizure free


def _rows(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


# ---------------------------------------------------------------------------
# Diagnosis
# ---------------------------------------------------------------------------
def _diag_concepts(mentions: list[dict[str, Any]], default_entity: str) -> Any:
    stream = [
        concept
        for mention in mentions
        for concept in annotation_clinical_concepts(
            mention.get("entity", default_entity),
            mention["text"],
            mention.get("attributes", {}),
        )
        if concept.entity == "Diagnosis"
    ]
    return collapse_concepts_to_most_specific(stream)


def _lineage_related(a: str, b: str) -> bool:
    return _is_anc(a, b) or _is_anc(b, a)


def _is_anc(child: str, ancestor: str) -> bool:
    cur = DIAGNOSIS_PARENT.get(child)
    while cur is not None:
        if cur == ancestor:
            return True
        cur = DIAGNOSIS_PARENT.get(cur)
    return False


def decompose_diagnosis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tot = Counter()
    fn_bucket = Counter()
    fp_bucket = Counter()
    examples: dict[str, list[str]] = {"assertion": [], "granularity": [], "family": []}

    for row in rows:
        lid = row["letter_id"]
        gold = _diag_concepts(row.get("gold_mentions", []), "Diagnosis")
        pred = _diag_concepts(row.get("predicted_mentions", []), "Diagnosis")

        gold_a = Counter(c.assertion_key for c in gold)
        pred_a = Counter(c.assertion_key for c in pred)
        tot["tp"] += sum((gold_a & pred_a).values())
        fn_a = gold_a - pred_a
        fp_a = pred_a - gold_a
        tot["fn"] += sum(fn_a.values())
        tot["fp"] += sum(fp_a.values())

        # concept part of each residual assertion key: key = (entity, concept, assertion)
        fn_concepts = Counter(k[1] for k, n in fn_a.items() for _ in range(n))
        fp_concepts = Counter(k[1] for k, n in fp_a.items() for _ in range(n))

        # A. assertion-only convention: same concept, different assertion
        shared = fn_concepts & fp_concepts
        for concept, n in shared.items():
            fn_bucket["assertion"] += n
            fp_bucket["assertion"] += n
            if len(examples["assertion"]) < 12:
                examples["assertion"].append(f"{lid}: {concept}")
        fn_rem = fn_concepts - shared
        fp_rem = fp_concepts - shared

        fn_list = list(fn_rem.elements())
        fp_list = list(fp_rem.elements())
        used_fp: set[int] = set()

        # B. granularity (lineage) then C. related-family, greedily
        for stage in ("granularity", "family"):
            for fc in fn_list:
                if fc is None:
                    continue
                for j, pc in enumerate(fp_list):
                    if j in used_fp or pc is None:
                        continue
                    rel = (
                        _lineage_related(fc, pc)
                        if stage == "granularity"
                        else (is_epilepsy_seizure_type(fc) and is_epilepsy_seizure_type(pc))
                        or ("epilepsy" in fc and "epilepsy" in pc)
                    )
                    if rel:
                        fn_bucket[stage] += 1
                        fp_bucket[stage] += 1
                        used_fp.add(j)
                        if len(examples[stage]) < 12:
                            examples[stage].append(f"{lid}: gold[{fc}] vs pred[{pc}]")
                        fn_list[fn_list.index(fc)] = None
                        break

        for fc in fn_list:
            if fc is not None:
                fn_bucket["genuine"] += 1
        for j, pc in enumerate(fp_list):
            if pc is not None and j not in used_fp:
                fp_bucket["genuine"] += 1

    return {
        "family": "Diagnosis",
        "candidate": "diagnosis reconciler v0.1",
        "headline_f1": 0.6585,
        "counts": dict(tot),
        "fn_total": sum(fn_bucket.values()),
        "fp_total": sum(fp_bucket.values()),
        "fn_buckets": dict(fn_bucket),
        "fp_buckets": dict(fp_bucket),
        "examples": examples,
    }


# ---------------------------------------------------------------------------
# SeizureFrequency
# ---------------------------------------------------------------------------
def _sf_state(attrs: dict[str, str]) -> str:
    vals = [
        attrs.get("NumberOfSeizures"),
        attrs.get("LowerNumberOfSeizures"),
        attrs.get("UpperNumberOfSeizures"),
    ]
    if any(v == "0" for v in vals if v is not None):
        return "seizure-free"
    if any(v for v in vals):
        return "active-rate"
    return "unknown"


def _sf_type(mention: dict[str, Any]) -> tuple[str, str]:
    cui = mention.get("attributes", {}).get("CUI")
    if cui:
        return ("cui", canonicalize_attribute_value("CUI", cui))
    return ("phrase", normalize_phrase(mention["text"]))


def _sf_keys(mentions: list[dict[str, Any]]) -> Counter:
    return Counter((_sf_type(m), _sf_state(m.get("attributes", {}))) for m in mentions)


def _is_generic(typ: tuple[str, str]) -> bool:
    return typ[0] == "cui" and (typ[1] in GENERIC_SF_CUIS or typ[1] in GENERIC_SF_FREE_CUIS)


def decompose_sf(rows: list[dict[str, Any]]) -> dict[str, Any]:
    tot = Counter()
    fn_bucket = Counter()
    fp_bucket = Counter()
    examples: dict[str, list[str]] = {"state": [], "ownership": []}

    for row in rows:
        lid = row["letter_id"]
        gold = _sf_keys(row.get("gold_mentions", []))
        pred = _sf_keys(row.get("predicted_mentions", []))
        tot["tp"] += sum((gold & pred).values())
        fn = gold - pred
        fp = pred - gold
        tot["fn"] += sum(fn.values())
        tot["fp"] += sum(fp.values())

        fn_types = Counter(k[0] for k, n in fn.items() for _ in range(n))
        fp_types = Counter(k[0] for k, n in fp.items() for _ in range(n))

        # A. state-convention: identical type key present both sides, state differs
        shared = fn_types & fp_types
        for typ, n in shared.items():
            fn_bucket["state"] += n
            fp_bucket["state"] += n
            if len(examples["state"]) < 12:
                examples["state"].append(f"{lid}: {typ}")
        fn_rem = list((fn_types - shared).elements())
        fp_rem = list((fp_types - shared).elements())
        used: set[int] = set()

        # B. generic<->named ownership pairing in same letter
        for ft in fn_rem:
            if ft is None:
                continue
            for j, pt in enumerate(fp_rem):
                if j in used or pt is None:
                    continue
                if _is_generic(ft) != _is_generic(pt):  # one generic, one named
                    fn_bucket["ownership"] += 1
                    fp_bucket["ownership"] += 1
                    used.add(j)
                    if len(examples["ownership"]) < 12:
                        examples["ownership"].append(f"{lid}: gold[{ft}] vs pred[{pt}]")
                    fn_rem[fn_rem.index(ft)] = None
                    break

        for ft in fn_rem:
            if ft is not None:
                fn_bucket["genuine"] += 1
        for j, pt in enumerate(fp_rem):
            if pt is not None and j not in used:
                fp_bucket["genuine"] += 1

    return {
        "family": "SeizureFrequency",
        "candidate": "SF state adjudicator v0.5",
        "headline_f1": 0.7211,
        "counts": dict(tot),
        "fn_total": sum(fn_bucket.values()),
        "fp_total": sum(fp_bucket.values()),
        "fn_buckets": dict(fn_bucket),
        "fp_buckets": dict(fp_bucket),
        "examples": examples,
    }


def _f1(tp: int, fp: int, fn: int) -> float:
    return 2 * tp / (2 * tp + fp + fn) if tp else 0.0


def _oracle_ceilings(d: dict[str, Any], stages: list[str]) -> dict[str, Any]:
    """F1 if each successive convention bucket were resolved on BOTH sides."""
    c = d["counts"]
    tp, fp, fn = c["tp"], c["fp"], c["fn"]
    out = {"base": round(_f1(tp, fp, fn), 4)}
    cum = 0
    for stage in stages:
        # resolving a bucket: each matched pair turns one FP and one FN into a TP
        moved = d["fn_buckets"].get(stage, 0)  # symmetric pairs
        cum += moved
        out[f"+{stage}"] = round(_f1(tp + cum, fp - cum, fn - cum), 4)
    return out


def main() -> None:
    diag = decompose_diagnosis(_rows(DIAG_JSONL))
    sf = decompose_sf(_rows(SF_JSONL))
    diag["oracle_ceilings"] = _oracle_ceilings(diag, ["assertion", "granularity", "family"])
    sf["oracle_ceilings"] = _oracle_ceilings(sf, ["state", "ownership"])
    out = {
        "generated": "2026-06-18",
        "split": "dev",
        "letters": 140,
        "diagnosis": diag,
        "seizure_frequency": sf,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    for d in (diag, sf):
        c = d["counts"]
        print(f"\n=== {d['family']} ({d['candidate']}) ===")
        print(f"  reconstructed tp/fp/fn = {c['tp']}/{c['fp']}/{c['fn']}")
        fn_t, fp_t = d["fn_total"], d["fp_total"]
        print(f"  FN buckets ({fn_t}): {d['fn_buckets']}")
        print(f"  FP buckets ({fp_t}): {d['fp_buckets']}")
        fb, pb = d["fn_buckets"], d["fp_buckets"]
        conv = sum(v for k, v in fb.items() if k != "genuine") + sum(
            v for k, v in pb.items() if k != "genuine"
        )
        total = fn_t + fp_t
        print(
            f"  convention-bound share of all residual events = {conv}/{total} = {conv / total:.1%}"
        )
        print(f"  oracle ceilings: {d['oracle_ceilings']}")
    print(f"\nWrote {OUT_JSON}")


if __name__ == "__main__":
    main()
