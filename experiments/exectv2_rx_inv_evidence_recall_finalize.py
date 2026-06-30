"""Finalizes Phase 4 of
``docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md``
(Prescription + Investigations extension): merges the 4 parallel adjudication batches
written by sub-agents (``_rx_inv_ev_recall/_verdicts_batch{0,1,2,3}.json``, one verdict
per case across the 23 Prescription + 27 Investigations ``source_near`` false-negative
cases produced by ``exectv2_rx_inv_evidence_recall_consolidation_check.py``) against the
mechanical H1_CARDINALITY / H2_GENUINE_DIVERGENCE split, computes the mechanism x verdict
cross-tab and the decision numbers PER FAMILY (not pooled, per the plan's Phase 4
predeclaration -- Rx and Inv's headline conventions differ from each other as well as
from Dx/SF), both the predeclared formula (mirrors Dx Phase 1 / SF Phase 3 exactly) and
the plain verdict-only reading, reported side by side.

Note: ``case_id`` is only unique WITHIN an entity (the upstream script resets the counter
per family), so all matching here is keyed on (entity, case_id) pairs, not case_id alone.

Usage: uv run python experiments/exectv2_rx_inv_evidence_recall_finalize.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
OUT = ROOT / "_rx_inv_ev_recall"

VERDICTS = ("GOLD_RIGHT", "MODEL_DEFENSIBLE", "BOTH_DEFENSIBLE")
MECHS = ("H1_CARDINALITY", "H2_GENUINE_DIVERGENCE")
ENTITIES = ("Prescription", "Investigations")


def classify(share: float) -> str:
    if share >= 0.50:
        return "H-inflated CONFIRMED (>= 50%)"
    if share < 0.30:
        return "H-genuine stands (< 30%)"
    return "PARTIAL result (30-50%)"


def main() -> None:
    cases = json.loads((OUT / "_cases.json").read_text(encoding="utf-8"))
    verdicts: dict[tuple[str, int], dict] = {}
    for b in range(4):
        rows = json.loads((OUT / f"_verdicts_batch{b}.json").read_text(encoding="utf-8"))
        for r in rows:
            verdicts[(r["entity"], r["case_id"])] = r

    missing = sorted({(c["entity"], c["case_id"]) for c in cases} - verdicts.keys())
    assert not missing, f"un-adjudicated cases: {missing}"

    for c in cases:
        v = verdicts[(c["entity"], c["case_id"])]
        c["verdict"] = v["verdict"]
        c["verdict_reason"] = v["reason"]

    csv_rows = []
    per_entity_final: dict[str, dict] = {}

    for entity in ENTITIES:
        ecases = [c for c in cases if c["entity"] == entity]
        crosstab: Counter[tuple[str, str]] = Counter()
        for c in ecases:
            crosstab[(c["mechanism"], c["verdict"])] += 1
            csv_rows.append({
                "entity": c["entity"],
                "case_id": c["case_id"],
                "letter": c["letter_id"],
                "mechanism": c["mechanism"],
                "verdict": c["verdict"],
                "missed_text": c["gold_missed"]["text"],
                "cross_entity_overlap": c["cross_entity_overlap"],
                "reason": c["verdict_reason"],
            })

        mech_counts = Counter(c["mechanism"] for c in ecases)
        verdict_counts = Counter(c["verdict"] for c in ecases)
        total = len(ecases)
        h1 = mech_counts["H1_CARDINALITY"]
        h2 = mech_counts["H2_GENUINE_DIVERGENCE"]

        h1_gold_right = crosstab[("H1_CARDINALITY", "GOLD_RIGHT")]
        h2_gold_right = crosstab[("H2_GENUINE_DIVERGENCE", "GOLD_RIGHT")]
        h2_model_defensible = crosstab[("H2_GENUINE_DIVERGENCE", "MODEL_DEFENSIBLE")]
        h2_both_defensible = crosstab[("H2_GENUINE_DIVERGENCE", "BOTH_DEFENSIBLE")]

        # Predeclared formula (mirrors Dx Phase 1 / SF Phase 3 exactly): all of H1 is
        # "inflated" by construction; only H2-and-GOLD_RIGHT is the strict bucket.
        inflated_strict = h1 + h2_model_defensible + h2_both_defensible
        genuine_strict = h2_gold_right

        # Plain verdict-only reading.
        inflated_verdict_only = verdict_counts["MODEL_DEFENSIBLE"] + verdict_counts["BOTH_DEFENSIBLE"]
        genuine_verdict_only = verdict_counts["GOLD_RIGHT"]

        print(f"\n=== {entity}: mechanism x verdict cross-tab ({total} source_near FNs) ===")
        print(f"{'mechanism':<22}{'GOLD_RIGHT':>12}{'MODEL_DEFENSIBLE':>18}{'BOTH_DEFENSIBLE':>17}{'TOTAL':>8}")
        for m in MECHS:
            gr, md, bd = (crosstab[(m, v)] for v in VERDICTS)
            print(f"{m:<22}{gr:>12}{md:>18}{bd:>17}{mech_counts[m]:>8}")
        print(f"{'TOTAL':<22}{verdict_counts['GOLD_RIGHT']:>12}{verdict_counts['MODEL_DEFENSIBLE']:>18}"
              f"{verdict_counts['BOTH_DEFENSIBLE']:>17}{total:>8}")

        share_strict = inflated_strict / total if total else 0.0
        share_verdict_only = inflated_verdict_only / total if total else 0.0
        print(f"\n[predeclared formula] H-inflated = {inflated_strict}/{total} = {share_strict:.1%}   "
              f"H-genuine = {genuine_strict}/{total} = {genuine_strict/total:.1%}")
        print(f"[plain verdict-only]   H-inflated = {inflated_verdict_only}/{total} = {share_verdict_only:.1%}   "
              f"H-genuine = {genuine_verdict_only}/{total} = {genuine_verdict_only/total:.1%}")
        if h1:
            print(f"H1_CARDINALITY verdict split: GOLD_RIGHT={h1_gold_right}/{h1} ({h1_gold_right/h1:.1%})")
        print(f"VERDICT [{entity}, predeclared]:   {classify(share_strict)}")
        print(f"VERDICT [{entity}, verdict-only]:  {classify(share_verdict_only)}")

        per_entity_final[entity] = {
            "n_cases": total,
            "mechanism_counts": dict(mech_counts),
            "verdict_counts": dict(verdict_counts),
            "crosstab": {f"{m}|{v}": crosstab[(m, v)] for m in MECHS for v in VERDICTS},
            "h1_gold_right_subset": h1_gold_right,
            "inflated_strict": inflated_strict, "inflated_strict_share": share_strict,
            "genuine_strict": genuine_strict, "genuine_strict_share": genuine_strict / total if total else 0.0,
            "inflated_verdict_only": inflated_verdict_only, "inflated_verdict_only_share": share_verdict_only,
            "genuine_verdict_only": genuine_verdict_only,
            "genuine_verdict_only_share": genuine_verdict_only / total if total else 0.0,
            "verdict_predeclared": classify(share_strict),
            "verdict_verdict_only": classify(share_verdict_only),
        }

    out_csv = OUT / "_adjudication.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)

    final = {"per_entity": per_entity_final, "cases": cases}
    check_path = EXPERIMENTS / "exectv2_rx_inv_evidence_recall_consolidation_check.json"
    existing = json.loads(check_path.read_text(encoding="utf-8"))
    existing.update(final)
    check_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"\nWrote {out_csv}")
    print(f"Wrote {check_path}")


if __name__ == "__main__":
    main()
