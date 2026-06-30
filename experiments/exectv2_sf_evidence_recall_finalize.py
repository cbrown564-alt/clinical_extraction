"""Finalizes Phase 3 of
``docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md``
(SF extension): merges the 4 parallel adjudication batches written by sub-agents
(``_sf_ev_recall/_verdicts_batch{0,1,2,3}.json``, one verdict per of the 72
``source_near`` SeizureFrequency false-negative cases produced by
``exectv2_sf_evidence_recall_consolidation_check.py``) against the mechanical
H1_CARDINALITY / H2_GENUINE_DIVERGENCE split, computes the mechanism x verdict
cross-tab, and writes the canonical adjudication CSV + the final decision numbers
(both the predeclared formula, mirroring Dx Phase 1 exactly, and the plain
verdict-only reading, reported side by side per the plan's own "report both, don't
force a binary verdict" discipline when they diverge).

Usage: uv run python experiments/exectv2_sf_evidence_recall_finalize.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
OUT = ROOT / "_sf_ev_recall"

VERDICTS = ("GOLD_RIGHT", "MODEL_DEFENSIBLE", "BOTH_DEFENSIBLE")
MECHS = ("H1_CARDINALITY", "H2_GENUINE_DIVERGENCE")


def main() -> None:
    cases = json.loads((OUT / "_cases.json").read_text(encoding="utf-8"))
    verdicts: dict[int, dict] = {}
    for b in range(4):
        rows = json.loads((OUT / f"_verdicts_batch{b}.json").read_text(encoding="utf-8"))
        for r in rows:
            verdicts[r["case_id"]] = r

    missing = sorted({c["case_id"] for c in cases} - verdicts.keys())
    assert not missing, f"un-adjudicated cases: {missing}"

    crosstab: Counter[tuple[str, str]] = Counter()
    csv_rows = []
    for c in cases:
        v = verdicts[c["case_id"]]
        c["verdict"] = v["verdict"]
        c["verdict_reason"] = v["reason"]
        crosstab[(c["mechanism"], v["verdict"])] += 1
        csv_rows.append({
            "case_id": c["case_id"],
            "letter": c["letter_id"],
            "mechanism": c["mechanism"],
            "verdict": v["verdict"],
            "missed_text": c["gold_missed"]["text"],
            "missed_state": c["gold_missed"]["state"],
            "cross_entity_overlap": c["cross_entity_overlap"],
            "reason": v["reason"],
        })

    mech_counts = Counter(c["mechanism"] for c in cases)
    verdict_counts = Counter(c["verdict"] for c in cases)
    total = len(cases)
    h1, h2 = mech_counts["H1_CARDINALITY"], mech_counts["H2_GENUINE_DIVERGENCE"]

    h1_gold_right = crosstab[("H1_CARDINALITY", "GOLD_RIGHT")]
    h2_gold_right = crosstab[("H2_GENUINE_DIVERGENCE", "GOLD_RIGHT")]
    h2_model_defensible = crosstab[("H2_GENUINE_DIVERGENCE", "MODEL_DEFENSIBLE")]
    h2_both_defensible = crosstab[("H2_GENUINE_DIVERGENCE", "BOTH_DEFENSIBLE")]

    # Predeclared formula (plan Phase 3, mirrors Dx Phase 1 exactly): all of H1 is
    # "inflated" by construction (the model's text WAS retrieved, full stop); only
    # H2-and-GOLD_RIGHT is the strict "unambiguous real miss" bucket.
    inflated_strict = h1 + h2_model_defensible + h2_both_defensible
    genuine_strict = h2_gold_right

    # Plain verdict-only reading (unanticipated divergence worth reporting: SF's
    # H1_CARDINALITY bucket contains a much larger genuine-error share (16/49=32.7%)
    # than Dx's did (1/13=7.7%), so "all of H1 = inflated" is a much bigger
    # simplification here than it was for Dx).
    inflated_verdict_only = verdict_counts["MODEL_DEFENSIBLE"] + verdict_counts["BOTH_DEFENSIBLE"]
    genuine_verdict_only = verdict_counts["GOLD_RIGHT"]

    print("=== mechanism x verdict cross-tab (72 SeizureFrequency source_near FNs) ===")
    print(f"{'mechanism':<22}{'GOLD_RIGHT':>12}{'MODEL_DEFENSIBLE':>18}{'BOTH_DEFENSIBLE':>17}{'TOTAL':>8}")
    for m in MECHS:
        gr, md, bd = (crosstab[(m, v)] for v in VERDICTS)
        print(f"{m:<22}{gr:>12}{md:>18}{bd:>17}{mech_counts[m]:>8}")
    print(f"{'TOTAL':<22}{verdict_counts['GOLD_RIGHT']:>12}{verdict_counts['MODEL_DEFENSIBLE']:>18}"
          f"{verdict_counts['BOTH_DEFENSIBLE']:>17}{total:>8}")

    print(f"\n=== DECISION NUMBERS ===")
    print(f"[predeclared formula, mirrors Dx Phase 1] "
          f"H-inflated = {inflated_strict}/{total} = {inflated_strict/total:.1%}   "
          f"H-genuine = {genuine_strict}/{total} = {genuine_strict/total:.1%}")
    print(f"[plain verdict-only reading]               "
          f"H-inflated = {inflated_verdict_only}/{total} = {inflated_verdict_only/total:.1%}   "
          f"H-genuine = {genuine_verdict_only}/{total} = {genuine_verdict_only/total:.1%}")
    print(f"\nH1_CARDINALITY verdict split: GOLD_RIGHT={h1_gold_right}/{h1} "
          f"({h1_gold_right/h1:.1%}) -- the divergence driver between the two readings.")

    for label, inflated, genuine in (
        ("predeclared", inflated_strict, genuine_strict),
        ("verdict-only", inflated_verdict_only, genuine_verdict_only),
    ):
        share = inflated / total
        if share >= 0.50:
            line = "H-inflated CONFIRMED (>= 50%)"
        elif share < 0.30:
            line = "H-genuine stands (< 30%)"
        else:
            line = "PARTIAL result (30-50%)"
        print(f"VERDICT [{label}]: {line}")

    out_csv = OUT / "_adjudication.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        w.writerows(csv_rows)

    final = {
        "n_cases": total,
        "mechanism_counts": dict(mech_counts),
        "verdict_counts": dict(verdict_counts),
        "crosstab": {f"{m}|{v}": crosstab[(m, v)] for m in MECHS for v in VERDICTS},
        "h1_gold_right_subset": h1_gold_right,
        "inflated_strict": inflated_strict, "inflated_strict_share": inflated_strict / total,
        "genuine_strict": genuine_strict, "genuine_strict_share": genuine_strict / total,
        "inflated_verdict_only": inflated_verdict_only,
        "inflated_verdict_only_share": inflated_verdict_only / total,
        "genuine_verdict_only": genuine_verdict_only,
        "genuine_verdict_only_share": genuine_verdict_only / total,
        "cases": cases,
    }
    check_path = EXPERIMENTS / "exectv2_sf_evidence_recall_consolidation_check.json"
    existing = json.loads(check_path.read_text(encoding="utf-8"))
    existing.update(final)
    check_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"\nWrote {out_csv}")
    print(f"Wrote {check_path}")


if __name__ == "__main__":
    main()
