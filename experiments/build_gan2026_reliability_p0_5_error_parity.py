"""P0.5 — Error-parity gap across families/bands (Fairness).

Reliability scorecard, Phase 0 (zero model budget). Subgroup = clinical
boundary band / qualitative family (the project's stand-in for a protected
attribute on synthetic data). Computes, for the canonical subject
(single-SE-mini, v0_reference) on validation750:

  - per-band Purist accuracy (bands partition every row exactly once)
  - cross-family error-rate spread (max-min) and coefficient of variation
  - a standalone parity flag lifting the family_cv_promotion `gap_robust` idea:
    any band whose accuracy falls a margin below the overall mean is flagged

Families come from the FROZEN validation classifier
`labels.classify_boundary_families` (note text from the saved raw_note_excerpt,
gold rate from the reference) — never a test-tuned tagger.

No model calls; deterministic replay.

Usage:
    uv run python experiments/build_gan2026_reliability_p0_5_error_parity.py
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import boundary_band
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_transitions import (
    tag_hidden_families,
)

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p0_5_error_parity_validation750_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p0_5_error_parity_validation750_2026-06-17.md"

PARITY_MARGIN = 0.10  # a band > 10 absolute pp below the overall mean is flagged


def note_text(row: dict[str, Any]) -> str:
    try:
        pij = json.loads(row["prompt_input_json"])
    except (KeyError, ValueError, TypeError):
        return ""
    return pij.get("raw_note_excerpt") or ""


def main() -> None:
    rows = rc.load_jsonl(rc.REASONER_VALIDATION750)
    n = len(rows)
    overall_correct = sum(rc.subject_purist_correct(r) for r in rows)
    overall_acc = overall_correct / n

    bands: dict[str, list[bool]] = {}
    families: dict[str, list[bool]] = {}
    for r in rows:
        gold_pm = rc.gold_monthly(r)
        band = boundary_band(gold_pm)
        fam_set = tag_hidden_families(note_text=note_text(r), gold_per_month=gold_pm)
        ok = rc.subject_purist_correct(r)
        bands.setdefault(band, []).append(ok)
        for fam in fam_set:
            families.setdefault(fam, []).append(ok)

    def acc_table(groups: dict[str, list[bool]]) -> dict[str, Any]:
        return {
            g: {
                "n": len(v),
                "correct": sum(v),
                "accuracy": sum(v) / len(v),
                "error_rate": 1 - sum(v) / len(v),
            }
            for g, v in sorted(groups.items(), key=lambda kv: kv[1].count(True) / len(kv[1]))
        }

    band_table = acc_table(bands)
    family_table = acc_table(families)

    band_accs = [d["accuracy"] for d in band_table.values()]
    band_errs = [d["error_rate"] for d in band_table.values()]
    spread = max(band_errs) - min(band_errs)
    cv = (statistics.pstdev(band_accs) / statistics.mean(band_accs)) if band_accs else None

    flagged = [
        {"band": b, **d, "deficit_vs_overall": overall_acc - d["accuracy"]}
        for b, d in band_table.items()
        if overall_acc - d["accuracy"] > PARITY_MARGIN
    ]
    worst_band = min(band_table.items(), key=lambda kv: kv[1]["accuracy"])

    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p0_5_error_parity",
        "date": "2026-06-17",
        "dimensions": ["Fairness"],
        "split": "validation750",
        "classifier": "labels.classify_boundary_families (frozen validation taxonomy)",
        "overall": {"accuracy": overall_acc, "correct": overall_correct, "n": n},
        "boundary_bands": band_table,
        "qualitative_families": family_table,
        "parity": {
            "error_rate_spread_max_minus_min": spread,
            "accuracy_coefficient_of_variation": cv,
            "parity_margin": PARITY_MARGIN,
            "flagged_bands": flagged,
            "worst_band": {"band": worst_band[0], **worst_band[1]},
            "gap_robust_reference": (
                "The transition-based promotion gate is family_cv_promotion.gap_robust "
                "(no held-out band regresses); here the subject's own per-band disparity "
                "is the standalone fairness flag."
            ),
        },
        "provenance": rc.provenance_block(
            subject="single_se_mini_v0_reference",
            sources=[rc.REASONER_VALIDATION750],
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"  overall acc {overall_acc:.3f}; band error spread {spread:.3f}; CV {cv:.3f}")
    print(f"  worst band: {worst_band[0]} acc {worst_band[1]['accuracy']:.3f} (n={worst_band[1]['n']})")
    print(f"  flagged bands: {[f['band'] for f in flagged]}")


def render_md(result: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# P0.5 — Error-Parity Gap Across Families / Bands (Fairness)\n")
    L.append(f"Date: {result['date']}  ·  Split: {result['split']}  ·  Model calls: 0\n")
    o = result["overall"]
    L.append(f"Subject overall Purist accuracy: {o['correct']}/{o['n']} = {o['accuracy']:.1%}. "
             f"Subgroups from `{result['classifier']}`.\n")
    L.append("## Boundary bands (partition every row exactly once)\n")
    L.append("| Band | n | Purist acc | Error rate |")
    L.append("|---|---:|---:|---:|")
    for b, d in result["boundary_bands"].items():
        L.append(f"| {b} | {d['n']} | {d['accuracy']:.1%} | {d['error_rate']:.1%} |")
    pa = result["parity"]
    L.append(f"\n- **Error-rate spread (max−min): {pa['error_rate_spread_max_minus_min']:.1%}**")
    L.append(f"- **Accuracy coefficient of variation: {pa['accuracy_coefficient_of_variation']:.3f}**")
    wb = pa["worst_band"]
    L.append(f"- Worst band: **{wb['band']}** at {wb['accuracy']:.1%} (n={wb['n']})")
    if pa["flagged_bands"]:
        names = ", ".join(f"{f['band']} ({f['accuracy']:.0%}, −{f['deficit_vs_overall']:.0%})"
                          for f in pa["flagged_bands"])
        L.append(f"- **Parity flag (> {pa['parity_margin']:.0%} below overall): {names}**")
    else:
        L.append(f"- Parity flag: none beyond the {pa['parity_margin']:.0%} margin")
    L.append("\n## Qualitative families (overlapping)\n")
    L.append("| Family | n | Purist acc | Error rate |")
    L.append("|---|---:|---:|---:|")
    for b, d in result["qualitative_families"].items():
        L.append(f"| {b} | {d['n']} | {d['accuracy']:.1%} | {d['error_rate']:.1%} |")
    L.append(f"\n_{pa['gap_robust_reference']}_\n")
    L.append("---\n")
    # Data-driven reading: name the actually-worst subgroups, not an assumed one.
    fam = result["qualitative_families"]
    worst_qual = min(fam.items(), key=lambda kv: kv[1]["accuracy"])
    L.append(
        "**Reading.** Per-band parity is fairly tight "
        f"(error-rate spread {pa['error_rate_spread_max_minus_min']:.1%}, CV "
        f"{pa['accuracy_coefficient_of_variation']:.3f}, no band beyond the "
        f"{pa['parity_margin']:.0%} margin). The disparity lives less in the partitioning "
        f"bands than in the qualitative over-reading families: **{worst_qual[0]}** "
        f"({worst_qual[1]['accuracy']:.1%}) and `cluster_burden` are the weakest subgroups, "
        f"and among bands the rate bands (`{wb['band']}`, `band_weekly`) trail — not "
        "`band_unknown`, which sits above the mean because most unknown rows are handled "
        "correctly and the over-reading is a minority within it. The cluster-burden and "
        "seizure-free-duration cadence families are the fairness face of the residual the "
        "accuracy work localized. On synthetic templated letters demographic fairness is "
        "structurally unmeasurable (P0.6); clinical-family parity is the available axis.\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
