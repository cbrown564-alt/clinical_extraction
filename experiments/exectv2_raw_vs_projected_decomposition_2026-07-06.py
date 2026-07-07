"""Raw-vs-projected decomposition (item 5 of predecessor-synthesis follow-ups).

ZERO LLM CALLS. A read of registry-tracked assembly artifacts -- no live
predictions, no re-scoring, no split risk.

Motivation (dspy predecessor finding). dspy's most uncomfortable finding for us:
raw S1 extraction is 68.6% micro-F1; after benchmark bridges the same surface
reaches 92.3% -- a ~24-point bridge contribution "too large to call raw
extraction 'solved.'" dissertation-recursive reinforces this with its
"scorer was materially broken for the first half of the project" story.
Our `clinical_headline` 0.9189 (dev140) / 0.8680 (full-200) is a de-duplicated,
projection-bearing recovery surface. **How much of it is raw producer emission
vs deterministic lens vs bridge?** This probe answers that per family, surfacing
the decomposition rather than hiding it -- the research-protocol
attribution-discipline deliverable ("an LLM-first claim requires showing what
the model selected before deterministic semantic repair").

What this probe is NOT. It is not a fresh measurement and not a re-run. The
three surfaces below are ALREADY computed through the same family scorers and
persisted in the registry-tracked P7 treatment artifacts
(`score_ladder.raw_lane_score` / `score_ladder.materialized_surfaces.residual_benchmark_added`
/ `score_ladder.headline_target`). This probe reads them, packages them as a
per-family table, computes the gaps, and re-validates that the headline column
reproduces the cited 0.9189 / 0.8680 (a self-check that the artifact is the
right one).

Three surfaces (in pipeline order, each scored through the same family scorers):
  1. ``RAW`` -- ``score_ladder.raw_lane_score``. The producer-lane's selected
     facts as emitted to the assembly (provenance ``emitted_raw_candidate``),
     pre-lens, pre-bridge, pre-projection. **CAVEAT (surfaced in the doc, not
     hidden): "raw" is post-producer, not raw vanilla-LLM.** The dev140 Dx/SF/Inv
     producers are themselves hybrid routes; only Rx's producer is fully
     deterministic. This is the prediction-bearing layer's emission before
     deterministic semantic repair -- the surface the attribution rule asks
     for -- but it is not commensurable with dspy's single-call "raw S1."
  2. ``POST_LENS`` -- ``score_ladder.materialized_surfaces.residual_benchmark_added``.
     After deterministic reconciliation (dictionary lens + residual benchmark
     add), pre-bridge. Scored ``projected=False``.
  3. ``HEADLINE`` -- ``score_ladder.headline_target``. The cited
     ``clinical_headline``: post-bridge + de-dup + CUI projection (``projected=True``).

Split discipline: dev140 + full-200 are both fine -- this reads registry-tracked
aggregate scores only, no live predictions and no row-level full-200 inspection.
Per claim_policy full-200 is aggregate-only; the source JSON already contains
only aggregate tp/fp/fn, so no row-level boundary is crossed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"

# Registry-tracked P7 treatment artifacts -- the runs that produced the cited
# 0.9189 dev140 / 0.8680 full-200 `clinical_headline` (registry ids
# exectv2_holistic_finding_assembly_v08_{dev140,full200}_p7fix_gpt41mini_20260702).
SOURCE_ARTIFACTS = {
    "dev140": EXPERIMENTS
    / "exectv2_holistic_finding_assembly_v08_dev140_p7_treatment_20260702.json",
    "full200": EXPERIMENTS
    / "exectv2_holistic_finding_assembly_v08_full200_p7_treatment_20260702.json",
}

# The cited overall `clinical_headline` this decomposition decomposes. Stated for
# the self-check only (the probe re-derives everything from the JSON).
CITED_OVERALL_HEADLINE = {
    "dev140": 0.9189,
    "full200": 0.8680,
}

FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")

# score_ladder keys that hold the three surfaces.
RAW_KEY = "raw_lane_score"
POST_LENS_KEY = ("materialized_surfaces", "residual_benchmark_added")
HEADLINE_KEY = "headline_target"

# Per-family headline-lift mechanism, stated once here so the doc and the JSON
# agree. This is the attribution story -- WHICH deterministic stage owns the lift
# -- and it is family-specific (not the flat "bridge contributes ~24pp" dspy
# framing).
MECHANISM = {
    "Diagnosis": (
        "Deterministic dictionary lens (drop generic 'epilepsy', rewrite "
        "conventions, add residual + generic-epilepsy companion). post-lens == "
        "headline; the entire lift is stage 2."
    ),
    "SeizureFrequency": (
        "CUI-projection bridge + de-dup. post-lens == raw; the entire lift is "
        "stage 3 (SF's frequency-type key uses CUI as seizure-type identity, so "
        "the CUI bridge materially changes SF scoring). This is the "
        "projection-heavy number dspy warns about."
    ),
    "Prescription": (
        "None. Raw == headline (the deterministic-owned ceiling item 4 "
        "confirmed; the producer's emission carries through unchanged)."
    ),
    "Investigations": (
        "None. Raw == headline (hybrid arbitration's output carries through unchanged)."
    ),
}


def _dig(obj: dict[str, Any], path: tuple[str, ...] | str) -> dict[str, Any]:
    """Walk a nested dict by a dotted path (tuple) or return obj[path] (str)."""

    if isinstance(path, str):
        return obj[path]
    cur: Any = obj
    for key in path:
        cur = cur[key]
    return cur


def _prf1_row(d: dict[str, Any]) -> dict[str, Any]:
    return {
        "f1": round(float(d["f1"]), 4),
        "precision": round(float(d["precision"]), 4),
        "recall": round(float(d["recall"]), 4),
        "tp": int(d.get("tp", d.get("precision_tp", 0))),
        "fp": int(d.get("fp", 0)),
        "fn": int(d.get("fn", 0)),
    }


def _surface_row(score_ladder: dict[str, Any], family: str, surface_key: object) -> dict[str, Any]:
    surface = _dig(score_ladder, surface_key)  # type: ignore[arg-type]
    by = surface["by_indicator"][family]
    return _prf1_row(by)


def _overall_row(score_ladder: dict[str, Any], surface_key: object) -> dict[str, Any]:
    surface = _dig(score_ladder, surface_key)  # type: ignore[arg-type]
    return _prf1_row(surface["overall"])


def decompose_split(split: str) -> dict[str, Any]:
    """Read one split's artifact and build the per-family + overall table.

    Re-validates that the headline column reproduces the cited overall number.
    """

    path = SOURCE_ARTIFACTS[split]
    if not path.exists():
        raise SystemExit(f"missing registry-tracked artifact: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    score_ladder = data["score_ladder"]

    families_out: list[dict[str, Any]] = []
    for family in FAMILIES:
        raw = _surface_row(score_ladder, family, RAW_KEY)
        post = _surface_row(score_ladder, family, POST_LENS_KEY)
        head = _surface_row(score_ladder, family, HEADLINE_KEY)
        families_out.append(
            {
                "family": family,
                "raw": raw,
                "post_lens": post,
                "headline": head,
                "gap_raw_to_post": round(post["f1"] - raw["f1"], 4),
                "gap_post_to_headline": round(head["f1"] - post["f1"], 4),
                "gap_raw_to_headline": round(head["f1"] - raw["f1"], 4),
                "mechanism": MECHANISM[family],
            }
        )

    overall_raw = _overall_row(score_ladder, RAW_KEY)
    overall_post = _overall_row(score_ladder, POST_LENS_KEY)
    overall_head = _overall_row(score_ladder, HEADLINE_KEY)

    # Self-check: the headline overall must reproduce the cited number.
    cited = CITED_OVERALL_HEADLINE[split]
    reproduced = round(overall_head["f1"], 4)
    if reproduced != cited:
        raise SystemExit(
            f"SELF-CHECK FAILED on {split}: headline overall {reproduced} != cited "
            f"{cited}. Wrong artifact, or the cited number moved and this probe's "
            f"CITED_OVERALL_HEADLINE must be updated."
        )

    return {
        "label": f"{split} ({data.get('row_count', '?')} letters)"
        if "row_count" in data
        else split,
        "source_artifact": str(path.relative_to(ROOT)),
        "registry_id": f"exectv2_holistic_finding_assembly_v08_{split}_p7fix_gpt41mini_20260702",
        "cited_overall_headline": cited,
        "headline_self_check": "PASS",
        "by_family": families_out,
        "overall": {
            "raw": overall_raw,
            "post_lens": overall_post,
            "headline": overall_head,
            "gap_raw_to_post": round(overall_post["f1"] - overall_raw["f1"], 4),
            "gap_post_to_headline": round(overall_head["f1"] - overall_post["f1"], 4),
            "gap_raw_to_headline": round(overall_head["f1"] - overall_raw["f1"], 4),
        },
    }


def _print_table(split_label: str, split_out: dict[str, Any]) -> None:
    cited = split_out["cited_overall_headline"]
    print(f"\n--- {split_label} (cited overall headline = {cited}) ---")
    print(
        f"  {'family':<18s} {'RAW':>8s} {'POSTLENS':>8s} {'HEADLINE':>8s} "
        f"{'R->P':>8s} {'P->H':>8s} {'R->H':>8s}"
    )
    for fam in split_out["by_family"]:
        print(
            f"  {fam['family']:<18s} {fam['raw']['f1']:8.4f} {fam['post_lens']['f1']:8.4f} "
            f"{fam['headline']['f1']:8.4f} {fam['gap_raw_to_post']:+8.4f} "
            f"{fam['gap_post_to_headline']:+8.4f} {fam['gap_raw_to_headline']:+8.4f}"
        )
    ov = split_out["overall"]
    print(
        f"  {'OVERALL':<18s} {ov['raw']['f1']:8.4f} {ov['post_lens']['f1']:8.4f} "
        f"{ov['headline']['f1']:8.4f} {ov['gap_raw_to_post']:+8.4f} "
        f"{ov['gap_post_to_headline']:+8.4f} {ov['gap_raw_to_headline']:+8.4f}"
    )
    print(f"  headline self-check: {split_out['headline_self_check']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--splits",
        default="dev140,full200",
        help="comma-separated subset of {dev140, full200}",
    )
    parser.add_argument(
        "--allow-non-dev140",
        action="store_true",
        help="acknowledge full-200 is aggregate-only (required to read full200)",
    )
    args = parser.parse_args()
    splits = [s.strip() for s in args.splits.split(",") if s.strip()]
    if "full200" in splits and not args.allow_non_dev140:
        raise SystemExit(
            "full200 is aggregate-only per claim_policy; pass --allow-non-dev140 to acknowledge."
        )

    print("=" * 78)
    print("Raw-vs-projected decomposition (zero LLM calls; reads registry-tracked artifacts)")
    print("=" * 78)

    results: dict[str, Any] = {
        "run_meta": {
            "probe": "exectv2_raw_vs_projected_decomposition",
            "llm_calls": 0,
            "model": "(model-independent; reads existing artifacts)",
            "surfaces": ["raw", "post_lens", "headline"],
            "surface_definitions": {
                "raw": (
                    "score_ladder.raw_lane_score -- producer-lane emission pre-lens "
                    "(provenance emitted_raw_candidate). CAVEAT: post-producer, not "
                    "raw vanilla-LLM; the dev140 Dx/SF/Inv producers are hybrid routes."
                ),
                "post_lens": (
                    "score_ladder.materialized_surfaces.residual_benchmark_added -- "
                    "after deterministic reconciliation, pre-bridge (projected=False)."
                ),
                "headline": (
                    "score_ladder.headline_target -- cited clinical_headline, post-bridge "
                    "+ de-dup + CUI projection (projected=True)."
                ),
            },
            "attribution_rule": (
                "Per research-protocol attribution rule: an LLM-first claim requires "
                "showing what the model selected before deterministic semantic repair. "
                "RAW is that surface (modulo the post-producer caveat)."
            ),
            "note": (
                "This is an attribution-discipline reporting deliverable, not a fresh "
                "measurement. The three surfaces were already computed through the same "
                "family scorers in the registry-tracked P7 treatment runs; this probe "
                "reads them, packages the per-family table, and re-validates the headline."
            ),
        },
        "splits": {},
    }

    for split in splits:
        split_out = decompose_split(split)
        results["splits"][split] = split_out
        _print_table(split_out["label"], split_out)

    out_path = EXPERIMENTS / "exectv2_raw_vs_projected_decomposition_2026-07-06.json"
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
