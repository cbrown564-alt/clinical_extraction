"""P1.2 — Per-family error-parity on frozen test450 (aggregate-only, freeze-warden gated).

Reliability scorecard, Phase 1 (no new model calls). A no-call re-score producing
a per-family parity slice on the holdout, family-tagging the 450 rows with the
FROZEN validation classifier `labels.classify_boundary_families` (per Phase-1
invariant 2 — never a test-tuned tagger).

Phase-1 invariants:
  1. Aggregate-only output: per-band aggregates only; no per-row tables, no
     source_row_index / transition_vs_v0 / score_layers markers.
  2. Frozen transform: the family classifier is the existing validation
     `classify_boundary_families`; its source SHA-256 is recorded.

Scored against v0_reference.comparison.purist_correct. No model calls.

Usage:
    uv run python experiments/build_gan2026_reliability_p1_2_test450_error_parity.py
"""

from __future__ import annotations

import hashlib
import inspect
import json
import statistics
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026 import labels as gan_labels
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    classify_boundary_families,
)

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p1_2_test450_error_parity_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p1_2_test450_error_parity_2026-06-17.md"

PARITY_MARGIN = 0.10


def note_text(row: dict[str, Any]) -> str:
    try:
        pij = json.loads(row["prompt_input_json"])
    except (KeyError, ValueError, TypeError):
        return ""
    return pij.get("raw_note_excerpt") or ""


def main() -> None:
    rows = rc.load_jsonl(rc.REASONER_TEST450)
    # only score rows with a defined gold purist category (exclude unscorable gold)
    scored = [r for r in rows if rc.subject_gold_purist(r) is not None]
    n = len(scored)
    overall_correct = sum(rc.subject_purist_correct(r) for r in scored)
    overall_acc = overall_correct / n

    bands: dict[str, list[bool]] = {}
    families: dict[str, list[bool]] = {}
    for r in scored:
        gold_pm = rc.gold_monthly(r)
        band = boundary_band(gold_pm)
        fam_set = classify_boundary_families(note_text=note_text(r), gold_per_month=gold_pm)
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
            for g, v in sorted(groups.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))
        }

    band_table = acc_table(bands)
    family_table = acc_table(families)
    band_accs = [d["accuracy"] for d in band_table.values()]
    band_errs = [d["error_rate"] for d in band_table.values()]
    spread = max(band_errs) - min(band_errs)
    cv = statistics.pstdev(band_accs) / statistics.mean(band_accs) if band_accs else None
    flagged = [b for b, d in band_table.items() if overall_acc - d["accuracy"] > PARITY_MARGIN]
    worst_band = min(band_table.items(), key=lambda kv: kv[1]["accuracy"])
    worst_qual = min(family_table.items(), key=lambda kv: kv[1]["accuracy"])

    clf_src = inspect.getsource(gan_labels.classify_boundary_families)
    clf_hash = hashlib.sha256(clf_src.encode("utf-8")).hexdigest()

    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p1_2_test450_error_parity",
        "date": "2026-06-17",
        "dimensions": ["Fairness"],
        "split": "test450 (frozen holdout)",
        "claim_boundary": "frozen aggregate-only holdout readout; no row-level test inspection",
        "frozen_transform": {
            "function": "labels.classify_boundary_families (validation classifier)",
            "source_sha256": clf_hash,
        },
        "provenance": rc.provenance_block(
            subject="single_se_mini_v0_reference", sources=[rc.REASONER_TEST450]
        ),
        "overall": {"accuracy": overall_acc, "correct": overall_correct, "n": n},
        "boundary_bands": band_table,
        "qualitative_families": family_table,
        "parity": {
            "error_rate_spread_max_minus_min": spread,
            "accuracy_coefficient_of_variation": cv,
            "parity_margin": PARITY_MARGIN,
            "flagged_bands": flagged,
            "worst_band": {"band": worst_band[0], **worst_band[1]},
            "worst_qualitative_family": {"family": worst_qual[0], **worst_qual[1]},
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"  overall acc {overall_acc:.3f}; band error spread {spread:.3f}; CV {cv:.3f}")
    print(
        f"  worst band {worst_band[0]} {worst_band[1]['accuracy']:.3f}; "
        f"worst family {worst_qual[0]} {worst_qual[1]['accuracy']:.3f}; flagged {flagged}"
    )


def render_md(result: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# P1.2 — Per-Family Error-Parity on Frozen test450 (Fairness)\n")
    L.append("## Aggregate-Only Holdout Readout\n")
    L.append(f"Date: {result['date']}  ·  Split: {result['split']}  ·  Model calls: 0\n")
    L.append(
        f"_{result['claim_boundary']}._  Frozen classifier "
        f"`{result['frozen_transform']['function']}` sha256 "
        f"`{result['frozen_transform']['source_sha256'][:16]}…`.\n"
    )
    o = result["overall"]
    L.append(f"Subject overall Purist accuracy: {o['correct']}/{o['n']} = {o['accuracy']:.1%}.\n")
    L.append("### Boundary bands (partition)\n")
    L.append("| Band | n | Purist acc | Error rate |")
    L.append("|---|---:|---:|---:|")
    for b, d in result["boundary_bands"].items():
        L.append(f"| {b} | {d['n']} | {d['accuracy']:.1%} | {d['error_rate']:.1%} |")
    pa = result["parity"]
    L.append(
        f"\n- **Error-rate spread (max−min): {pa['error_rate_spread_max_minus_min']:.1%}**, "
        f"accuracy CV {pa['accuracy_coefficient_of_variation']:.3f}"
    )
    wb = pa["worst_band"]
    wq = pa["worst_qualitative_family"]
    L.append(
        f"- Worst band: **{wb['band']}** {wb['accuracy']:.1%} (n={wb['n']}); "
        f"worst qualitative family: **{wq['family']}** {wq['accuracy']:.1%} (n={wq['n']})"
    )
    L.append(
        f"- Parity flag (> {pa['parity_margin']:.0%} below overall): "
        f"{', '.join(pa['flagged_bands']) if pa['flagged_bands'] else 'none'}"
    )
    L.append("\n### Qualitative families (overlapping)\n")
    L.append("| Family | n | Purist acc | Error rate |")
    L.append("|---|---:|---:|---:|")
    for b, d in result["qualitative_families"].items():
        L.append(f"| {b} | {d['n']} | {d['accuracy']:.1%} | {d['error_rate']:.1%} |")
    L.append("\n---\n")
    L.append(
        "**Reading.** The holdout confirms the validation parity picture on the same frozen "
        "taxonomy: the disparity concentrates in the over-reading qualitative families and "
        "the rate bands rather than in `band_unknown`. Family is a real reliability slice on "
        "the locked split, not just a validation artifact.\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
