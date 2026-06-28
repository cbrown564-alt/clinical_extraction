"""Convention-tax analysis on saved GEPA predictions (zero-LLM, read-only).

Root-cause diagnostic for the multistage negative (2026-06-28): the dedup scoring
path keys the model's concept TEXT through a CLOSED hand-curated alias normalizer
(`deterministic/normalization.py`), so the model is scored on whether its surface
form matches gold's canonical surface — not on whether it captured the right
clinical concept. This script quantifies how much of the per-family headline gap is
that *convention/representation* tax (deterministically recoverable) versus genuine
clinical recall (the model's job), by comparing, per family:

* **headline** F1/P/R   — the canonical-key match the runner reports (concept+key).
* **source-near** F1/P/R — span-overlap match that IGNORES the canonical key, so a
  right-span / wrong-surface prediction still counts. (+ attribute-agreement rate.)

``source_near.recall - headline.recall`` ≈ the recall recoverable if surface
conventions were free. A finer Diagnosis pass counts headline-FN gold concepts that
DO have an overlapping predicted span (convention-miss) vs none (genuine recall-miss).

Usage:
    uv run python experiments/exectv2_convention_tax_analysis.py
    uv run python experiments/exectv2_convention_tax_analysis.py --run <run_id>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_prescription_components,
    semantic_config_for,
    source_near_diagnostic,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DEFAULT_RUN = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"

ENTITIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")


def _pred_letters(run_id: str) -> dict[str, ExectLetter]:
    rows = [
        json.loads(line)
        for line in (EXPERIMENTS / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    letters: dict[str, ExectLetter] = {}
    for row in rows:
        anns = tuple(
            ExectAnnotation(
                entity=m["entity"],
                text=m.get("text", ""),
                attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
            )
            for m in row.get("predicted_mentions", [])
        )
        letters[row["letter_id"]] = ExectLetter(letter_id=row["letter_id"], note_text="", annotations=anns)
    return letters


def _headline_prf(gold: list[ExectLetter], pred: list[ExectLetter]) -> dict[str, tuple[float, float, float]]:
    """Per-family canonical-key headline P/R/F1 (Dx=concept_negation)."""

    dx = score_concept_identity(gold, pred, "Diagnosis").concept_negation
    sf = score_frequency_state(gold, pred).clinical_headline
    rx = score_prescription_components(gold, pred).clinical_headline
    inv = score_investigations_components(gold, pred).clinical_headline
    out = {}
    for name, s in (("Diagnosis", dx), ("SeizureFrequency", sf), ("Prescription", rx), ("Investigations", inv)):
        out[name] = (s.precision, s.recall, s.f1)
    return out


def _fn_breakdown(gold: list[ExectLetter], pred: list[ExectLetter], entity: str, key_fn) -> dict[str, int]:
    """Of an entity's headline-FN gold units, how many have an overlapping pred span?

    convention-miss = the model emitted a same-entity mention whose normalized phrase
    overlaps the gold's, but the headline key did not reconcile them (recoverable by a
    better normalizer). genuine recall-miss = no overlapping predicted span at all.
    """

    pred_by_id = {letter.letter_id: letter for letter in pred}
    convention_miss = recall_miss = total_fn = 0
    for g in gold:
        p = pred_by_id.get(g.letter_id)
        gold_anns = list(g.entities(entity))
        pred_anns = list(p.entities(entity)) if p else []
        gold_keys = set(key_fn(gold_anns))
        pred_keys = set(key_fn(pred_anns))
        missed_keys = gold_keys - pred_keys
        if not missed_keys:
            continue
        pred_phrases = [normalize_phrase(a.text) for a in pred_anns if a.text]
        for ann in gold_anns:
            for key in key_fn([ann]):
                if key not in missed_keys:
                    continue
                total_fn += 1
                gp = normalize_phrase(ann.text)
                overlap = any(gp and (gp in pp or pp in gp) for pp in pred_phrases)
                if overlap:
                    convention_miss += 1
                else:
                    recall_miss += 1
    return {"total_fn": total_fn, "convention_miss": convention_miss, "recall_miss": recall_miss}


def _f1(tp: int, pred_n: int, gold_n: int) -> tuple[float, float, float]:
    p = tp / pred_n if pred_n else 0.0
    r = tp / gold_n if gold_n else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def _multiset_tp(gold_keys: list, pred_keys: list) -> int:
    from collections import Counter

    g, p = Counter(gold_keys), Counter(pred_keys)
    return sum(min(g[k], p[k]) for k in g)


def _diagnosis_cui_headroom(gold: list[ExectLetter], pred: list[ExectLetter]) -> None:
    """Mention-level Diagnosis match under three keys: canonical-text, CUI, union.

    Apples-to-apples (no compound splitting on either side), so it isolates how much
    of the gap a CUI-based normalizer recovers over the closed alias table. 'union'
    = match if EITHER the canonical alias concept OR the CUI reconciles (alias table
    AUGMENTED with CUI) — the realistic CUI-normalizer headroom.
    """

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
        canonicalize_diagnosis_concept,
    )

    def signature(a: ExectAnnotation) -> tuple:
        neg = a.attributes.get("Negation", "Affirmed")
        return (canonicalize_diagnosis_concept(a.text), neg, a.attributes.get("CUI") or None)

    pred_by_id = {letter.letter_id: letter for letter in pred}
    text_counts = [0, 0, 0]  # tp, pred_n, gold_n
    cui_counts = [0, 0, 0]
    union_counts = [0, 0, 0]
    pred_cui_cov = pred_total = 0
    for g in gold:
        p = pred_by_id.get(g.letter_id)
        gold_sigs = [signature(a) for a in g.entities("Diagnosis")]
        pred_sigs = [signature(a) for a in (p.entities("Diagnosis") if p else [])]
        pred_total += len(pred_sigs)
        pred_cui_cov += sum(1 for s in pred_sigs if s[2])

        # canonical-text-only multiset match
        text_counts[0] += _multiset_tp([(s[0], s[1]) for s in gold_sigs], [(s[0], s[1]) for s in pred_sigs])
        text_counts[1] += len(pred_sigs)
        text_counts[2] += len(gold_sigs)
        # CUI-only (mentions with a CUI on both sides)
        g_cui = [(s[2], s[1]) for s in gold_sigs if s[2]]
        p_cui = [(s[2], s[1]) for s in pred_sigs if s[2]]
        cui_counts[0] += _multiset_tp(g_cui, p_cui)
        cui_counts[1] += len(p_cui)
        cui_counts[2] += len(g_cui)
        # union: greedy one-to-one, match if canonical-text+neg OR CUI+neg agree
        used: set[int] = set()
        tp = 0
        for gs in gold_sigs:
            for j, ps in enumerate(pred_sigs):
                if j in used:
                    continue
                text_ok = gs[0] == ps[0] and gs[1] == ps[1]
                cui_ok = gs[2] is not None and gs[2] == ps[2] and gs[1] == ps[1]
                if text_ok or cui_ok:
                    used.add(j)
                    tp += 1
                    break
        union_counts[0] += tp
        union_counts[1] += len(pred_sigs)
        union_counts[2] += len(gold_sigs)

    print("## Diagnosis CUI headroom (mention-level, no split — isolates the normalizer)")
    print(f"  pred Dx CUI coverage: {pred_cui_cov}/{pred_total} "
          f"({100 * pred_cui_cov / pred_total:.0f}%)")
    print(f"  {'key':<16}{'P':>7}{'R':>7}{'F1':>7}")
    for name, c in (("canonical_text", text_counts), ("cui_only", cui_counts), ("union(alias+CUI)", union_counts)):
        p, r, f = _f1(c[0], c[1], c[2])
        print(f"  {name:<16}{p:>7.3f}{r:>7.3f}{f:>7.3f}")
    print("  (union = realistic alias+CUI normalizer ceiling; cui_only denom = mentions WITH a CUI)\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=DEFAULT_RUN)
    args = parser.parse_args()

    gold = gepa_data.load_dev_letters()
    pred_by_id = _pred_letters(args.run)
    pred = [pred_by_id.get(g.letter_id, ExectLetter(letter_id=g.letter_id, note_text="")) for g in gold]

    headline = _headline_prf(gold, pred)
    source_near = source_near_diagnostic(gold, pred, ENTITIES, semantic_config_for).per_entity

    print(f"# Convention-tax analysis — {args.run} (dev140, {len(gold)} letters)\n")
    header = f"{'family':<16}{'hl_P':>7}{'hl_R':>7}{'hl_F1':>7} | {'sn_P':>7}{'sn_R':>7}{'sn_F1':>7} | {'attr%':>7}{'taxR':>7}{'taxP':>7}"
    print(header)
    print("-" * len(header))
    for name in ENTITIES:
        hp, hr, hf = headline[name]
        sn = source_near[name]
        snp, snr, snf = sn.overlap.precision, sn.overlap.recall, sn.overlap.f1
        attr = sn.attribute_agreement_rate
        tax_r = snr - hr  # recall recoverable if surface conventions were free
        tax_p = snp - hp
        print(
            f"{name:<16}{hp:>7.3f}{hr:>7.3f}{hf:>7.3f} | {snp:>7.3f}{snr:>7.3f}{snf:>7.3f} | "
            f"{attr:>7.3f}{tax_r:>+7.3f}{tax_p:>+7.3f}"
        )

    print("\nhl = headline canonical-key match (what the runner reports)")
    print("sn = source-near span-overlap match (right span, IGNORES canonical key)")
    print("attr% = attribute agreement among span-overlapping pairs")
    print("taxR/taxP = sn - hl (recall/precision recoverable if conventions were free)\n")

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
        concept_keys,
        frequency_state_keys,
    )

    breakdowns = {
        "Diagnosis": _fn_breakdown(gold, pred, "Diagnosis", lambda a: concept_keys(a, "Diagnosis", "negation")),
        "SeizureFrequency": _fn_breakdown(
            gold, pred, "SeizureFrequency", lambda a: frequency_state_keys(a, "clinical_headline")
        ),
    }
    print("## Headline-FN breakdown (convention-recoverable vs genuine recall miss)")
    for entity, b in breakdowns.items():
        if not b["total_fn"]:
            continue
        conv_pct = 100 * b["convention_miss"] / b["total_fn"]
        print(f"  {entity:<16} FNs={b['total_fn']:>3}  convention-miss={b['convention_miss']:>3} "
              f"({conv_pct:.0f}%)  genuine-recall-miss={b['recall_miss']:>3} ({100 - conv_pct:.0f}%)")
    print()
    _diagnosis_cui_headroom(gold, pred)
    _normalized_rescore(gold, pred)


def _normalized_rescore(gold: list[ExectLetter], pred: list[ExectLetter]) -> None:
    """Re-score the preds after the in-sample concept normalizer (OPTIMISTIC ceiling).

    Builds the gold-derived stub normalizer, rewrites pred concept text to gold
    convention, and re-runs the official canonical headline. The lift over the raw
    number bounds what a (test-safe UMLS) normalizer could recover on these exact
    model facts. In-sample => dev-only, optimistic, NOT a deployable result.
    """

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.concept_normalizer import (
        InSampleConceptNormalizer,
        normalize_letter,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import _canonical_headline

    normalizer = InSampleConceptNormalizer.from_gold(gold)
    pred_norm = [normalize_letter(p, normalizer) for p in pred]

    before = _canonical_headline(gold, pred)
    after = _canonical_headline(gold, pred_norm)
    print("## Headline after in-sample concept normalizer (OPTIMISTIC ceiling, leaky/dev-only)")
    print(f"  {'':<16}{'before':>9}{'after':>9}{'delta':>9}")
    print(
        f"  {'overall_f1':<16}{before['overall_f1']:>9.3f}{after['overall_f1']:>9.3f}"
        f"{after['overall_f1'] - before['overall_f1']:>+9.3f}"
    )
    for fam in ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations"):
        b = before["per_family"][fam]
        a = after["per_family"][fam]
        print(f"  {fam:<16}{b:>9.3f}{a:>9.3f}{a - b:>+9.3f}")
    print(f"  precision      before {before['precision']:.3f} -> after {after['precision']:.3f}; "
          f"recall before {before['recall']:.3f} -> after {after['recall']:.3f}")
    print("  (ceiling vs v08 hybrid 0.9155; the gap that remains is genuine clinical recall)")


if __name__ == "__main__":
    main()
