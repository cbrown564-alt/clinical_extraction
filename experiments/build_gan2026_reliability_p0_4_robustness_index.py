"""P0.4 — Robustness index + invariance flip-rate.

Reliability scorecard, Phase 0 (zero model budget). Re-aggregates the saved
adversarial-battery JSONs into a continuous robustness index per candidate:

  - per-panel pass fraction (A minimal-pairs / B source-near / C OOD) + overall
  - minimal-pair both-sides-correct consistency rate (Panel A)
  - the directional overfit gap = quantify-side accuracy - unknown-side accuracy
    on Panel A (the over-reading asymmetry the battery was designed to expose)
  - a composite robustness index in [0,1]

Invariance flip-rate note: the saved Panel-B/C cases are standalone source-near /
OOD letters with no paired *original* twin (every `pair` is null), so a literal
original<->perturbed paraphrase flip-rate is NOT computable from this artifact.
The available invariance signal is the Panel-A minimal-pair consistency
(both-sides-correct vs flip-to-overfit). A true paraphrase flip-rate on real rows
is P2.3 (needs model budget + freeze-warden). This limitation is reported, not
papered over.

No model calls; deterministic re-aggregation.

Usage:
    uv run python experiments/build_gan2026_reliability_p0_4_robustness_index.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p0_4_robustness_index_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p0_4_robustness_index_2026-06-17.md"


def _panel_pass(panel: dict[str, Any]) -> tuple[int, int]:
    return int(panel.get("purist_correct", 0)), int(panel.get("cases", 0))


def _side_accuracy(records: list[dict[str, Any]], key: str) -> tuple[int, int]:
    correct = total = 0
    for r in records:
        v = r.get(key)
        if v is None:
            continue
        total += 1
        correct += int(bool(v))
    return correct, total


def analyse_candidate(name: str, path: Path) -> dict[str, Any]:
    d = rc.load_json(path)
    panels = d["panels"]
    a, b, c = panels["A_minimal_pairs"], panels["B_source_near_perturbations"], panels["C_kcl_style_ood"]
    ac, an = _panel_pass(a)
    bc, bn = _panel_pass(b)
    cc, cn = _panel_pass(c)
    overall_c, overall_n = ac + bc + cc, an + bn + cn

    pairs = a["pairs"]
    both_correct = int(pairs.get("both_correct_pairs", 0))
    npairs = int(pairs.get("pairs", 0))
    overfit_only = int(pairs.get("overfit_only_pairs", 0))
    records = pairs.get("records", [])
    uk_c, uk_n = _side_accuracy(records, "unknown_side_correct")
    qt_c, qt_n = _side_accuracy(records, "quantify_side_correct")
    unknown_acc = uk_c / uk_n if uk_n else None
    quantify_acc = qt_c / qt_n if qt_n else None
    overfit_gap = (quantify_acc - unknown_acc) if (unknown_acc is not None and quantify_acc is not None) else None

    consistency = both_correct / npairs if npairs else None
    overall_pass = overall_c / overall_n if overall_n else 0.0
    # Composite robustness index: mean of overall pass, minimal-pair consistency,
    # and (1 - positive overfit gap). All in [0,1]; predeclared equal weights.
    gap_term = 1 - max(0.0, overfit_gap) if overfit_gap is not None else 1.0
    parts = [overall_pass, consistency if consistency is not None else overall_pass, gap_term]
    index = sum(parts) / len(parts)

    return {
        "candidate": name,
        "candidate_label": d.get("candidate"),
        "panels": {
            "A_minimal_pairs": {"pass": ac, "cases": an, "rate": ac / an if an else None},
            "B_source_near": {"pass": bc, "cases": bn, "rate": bc / bn if bn else None},
            "C_kcl_ood": {"pass": cc, "cases": cn, "rate": cc / cn if cn else None},
            "overall": {"pass": overall_c, "cases": overall_n, "rate": overall_pass},
        },
        "minimal_pair_consistency": {
            "both_correct_pairs": both_correct,
            "pairs": npairs,
            "rate": consistency,
            "overfit_only_pairs": overfit_only,
            "flip_to_overfit_rate": overfit_only / npairs if npairs else None,
        },
        "overfit_gap": {
            "unknown_side_accuracy": unknown_acc,
            "quantify_side_accuracy": quantify_acc,
            "gap_quantify_minus_unknown": overfit_gap,
        },
        "robustness_index": index,
    }


def main() -> None:
    candidates = [analyse_candidate(name, path) for name, path in rc.ROBUSTNESS_BATTERY.items()]
    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p0_4_robustness_index",
        "date": "2026-06-17",
        "dimensions": ["Robustness"],
        "robustness_index_formula": "mean(overall_pass, minimal_pair_consistency, 1 - max(0, quantify_minus_unknown_gap))",
        "invariance_flip_rate_note": (
            "Panel B/C cases are standalone (pair=null); a literal original<->perturbed "
            "paraphrase flip-rate is not computable from the saved artifact. Panel-A "
            "flip_to_overfit_rate is the available invariance signal; true paraphrase "
            "flip-rate on real rows is P2.3 (budgeted)."
        ),
        "provenance": rc.provenance_block(
            subject="adversarial_battery_candidates_gpt41mini",
            sources=list(rc.ROBUSTNESS_BATTERY.values()) + [rc.ROBUSTNESS_CASES],
        ),
        "candidates": candidates,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    for c in candidates:
        o = c["panels"]["overall"]
        print(f"  {c['candidate']:<18} overall {o['pass']}/{o['cases']} ({o['rate']:.0%}) "
              f"consistency {c['minimal_pair_consistency']['rate']} "
              f"overfit_gap {c['overfit_gap']['gap_quantify_minus_unknown']} "
              f"index {c['robustness_index']:.3f}")


def render_md(result: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# P0.4 — Robustness Index + Invariance Flip-Rate\n")
    L.append(f"Date: {result['date']}  ·  Model calls: 0\n")
    L.append(f"Robustness index = `{result['robustness_index_formula']}` (equal weights, predeclared).\n")
    L.append("| Candidate | A | B | C | Overall | Min-pair consistency | Overfit gap | **Index** |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for c in result["candidates"]:
        p = c["panels"]
        mp = c["minimal_pair_consistency"]
        gap = c["overfit_gap"]["gap_quantify_minus_unknown"]
        L.append(
            f"| {c['candidate']} | {p['A_minimal_pairs']['pass']}/{p['A_minimal_pairs']['cases']} | "
            f"{p['B_source_near']['pass']}/{p['B_source_near']['cases']} | "
            f"{p['C_kcl_ood']['pass']}/{p['C_kcl_ood']['cases']} | "
            f"{p['overall']['pass']}/{p['overall']['cases']} ({p['overall']['rate']:.0%}) | "
            f"{mp['both_correct_pairs']}/{mp['pairs']}"
            f"{f' ({mp['rate']:.0%})' if mp['rate'] is not None else ''} | "
            f"{gap:+.2f} | **{c['robustness_index']:.3f}** |"
        )
    L.append(f"\n_{result['invariance_flip_rate_note']}_\n")
    L.append("---\n")
    L.append(
        "**Reading.** The index ranks the candidates the same way the binary `transfers` "
        "verdict did, but on a continuum: the overfit gap (quantify-side minus unknown-side "
        "accuracy) is the single most diagnostic leg — a positive gap is the over-reading "
        "signature, and it is exactly what flagged the v0.6 evidence variant overfit before "
        "it scored 351/450 on frozen test. A high OOD pass rate with a large overfit gap "
        "(the v0.7 pattern) shows panel pass is necessary but not sufficient.\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
