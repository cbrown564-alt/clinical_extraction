"""Deterministic exhaustiveness probe (zero-LLM) on saved GEPA predictions.

The genuine-recall gap is dominated by the gold's exhaustive multi-concept
convention: gold tags every co-present concept (generic 'epilepsy' + specific
syndrome + ...), while the model consolidates. This probe bounds how much of that
gap is recoverable MECHANICALLY (no model, no leak) by expanding each predicted
Diagnosis concept UP the existing ``DIAGNOSIS_PARENT`` hierarchy (e.g. temporal
lobe epilepsy -> focal epilepsy -> epilepsy), then re-scoring the canonical
headline. The lift is the parent-multiplicity share of the recall gap; whatever
remains needs genuine detection (the model's job), e.g. SF seizure-free/changed
states, which are not parent-expandable.

Usage:
    uv run python experiments/exectv2_exhaustiveness_probe.py
"""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    DIAGNOSIS_PARENT,
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.run_gepa import _canonical_headline

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DEFAULT_RUN = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"


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
        letters[row["letter_id"]] = ExectLetter(
            letter_id=row["letter_id"], note_text="", annotations=anns
        )
    return letters


def _ancestors(concept: str) -> list[str]:
    chain: list[str] = []
    seen = {concept}
    node = concept
    while node in DIAGNOSIS_PARENT:
        node = DIAGNOSIS_PARENT[node]
        if node in seen:
            break
        seen.add(node)
        chain.append(node)
    return chain


def _expand_letter(letter: ExectLetter) -> ExectLetter:
    """Add parent-concept Diagnosis mentions for each predicted specific syndrome."""

    existing = {
        (canonicalize_diagnosis_concept(a.text), a.attributes.get("Negation", "Affirmed"))
        for a in letter.entities("Diagnosis")
    }
    added: list[ExectAnnotation] = []
    for ann in letter.entities("Diagnosis"):
        negation = ann.attributes.get("Negation", "Affirmed")
        for parent in _ancestors(canonicalize_diagnosis_concept(ann.text)):
            key = (parent, negation)
            if key in existing:
                continue
            existing.add(key)
            added.append(
                replace(ann, text=parent, attributes={**dict(ann.attributes), "Negation": negation})
            )
    if not added:
        return letter
    return ExectLetter(
        letter_id=letter.letter_id,
        note_text=letter.note_text,
        annotations=(*letter.annotations, *added),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default=DEFAULT_RUN)
    args = parser.parse_args()

    gold = gepa_data.load_dev_letters()
    pred_by_id = _pred_letters(args.run)
    pred = [
        pred_by_id.get(g.letter_id, ExectLetter(letter_id=g.letter_id, note_text="")) for g in gold
    ]
    pred_expanded = [_expand_letter(p) for p in pred]

    n_added = sum(
        len(e.annotations) - len(p.annotations) for p, e in zip(pred, pred_expanded, strict=True)
    )
    before = _canonical_headline(gold, pred)
    after = _canonical_headline(gold, pred_expanded)

    print(f"# Deterministic exhaustiveness probe (parent expansion) — {args.run} (dev140)\n")
    print(
        f"Added {n_added} parent-concept Diagnosis mentions across {len(gold)} letters "
        "(deployable, no gold leak).\n"
    )
    print(f"  {'':<16}{'before':>9}{'after':>9}{'delta':>9}")
    print(
        f"  {'overall_f1':<16}{before['overall_f1']:>9.3f}{after['overall_f1']:>9.3f}"
        f"{after['overall_f1'] - before['overall_f1']:>+9.3f}"
    )
    for fam in ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations"):
        b, a = before["per_family"][fam], after["per_family"][fam]
        print(f"  {fam:<16}{b:>9.3f}{a:>9.3f}{a - b:>+9.3f}")
    print(
        f"  Diagnosis P/R   before {before['per_family']['Diagnosis']:.3f} "
        f"(P {before['precision']:.3f} R {before['recall']:.3f}) -> "
        f"after P {after['precision']:.3f} R {after['recall']:.3f}"
    )
    print("\n  (lift = parent-multiplicity share of the recall gap; the rest needs genuine")
    print("   detection — SF seizure-free/changed states are NOT parent-expandable)")


if __name__ == "__main__":
    main()
