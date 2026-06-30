"""Canonical Diagnosis row-by-row analysis on EXACTLY the scored `clinical_headline` metric.

Mirrors ``experiments/exectv2_sf_canonical_row_analysis.py``'s pattern for the Diagnosis
family: for every dev140 letter, decompose Diagnosis (mis)matches against the OFFICIAL
clinical-headline Diagnosis scorer (``score_concept_identity(..., "Diagnosis").concept_only``
-- entity-agnostic recall pool, home-tagged precision), self-validate the per-letter
decomposition sums to the official aggregate, and write per-letter markdown substrate for
every disagreement letter for clinical adjudication (mirrors
``exectv2_sf_canonical_adjudication.py``'s GOLD_RIGHT / MODEL_DEFENSIBLE / BOTH_DEFENSIBLE
pattern).

This answers the question the GEPA single-model plateau synthesis reopened on 2026-06-28:
"the Diagnosis 'consolidation' finding is the same mechanism [as SF gold under/over-tagging],
so the architectural-gap framing is also in question" -- never chased down for Dx.

Zero new LLM calls: replays the already-cached GEPA per-family prediction jsonl (run_id
``exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628``, registry-confirmed
``clinical_headline_diagnosis_f1=0.6617``).

Outputs (to ``OUT`` dir, default ``_dx_canonical``):
* ``_index.json``   -- per-letter gold/missed/spurious concept keys + tp/fp/fn + reproduction check.
* ``_summary.json`` -- aggregate decomposition vs the official scorer + category breakdown.
* ``<letter>.md``   -- per-letter substrate (gold concepts, predicted concepts, note excerpt)
                       for every letter where Diagnosis missed or spurious is non-empty.

Usage:  uv run python experiments/exectv2_dx_canonical_row_analysis.py [OUT_DIR]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    is_epilepsy_seizure_type,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    concept_keys,
    score_concept_identity,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    _clinical_recovery_prf1,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_dx_canonical"


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


def _context(note: str, ann: ExectAnnotation, width: int = 55) -> str:
    note_low = note.lower()
    pos = -1
    span_len = 0
    if ann.start_index is not None and 0 <= ann.start_index < len(note):
        pos = ann.start_index
        span_len = (ann.end_index or pos) - pos
    else:
        for probe in (ann.raw_text or "", ann.text, ann.text.replace("-", " ")):
            if probe:
                pos = note_low.find(probe.lower()[:30])
                span_len = len(probe)
                if pos >= 0:
                    break
    if pos < 0:
        head = ann.text.replace("-", " ").split()[0] if ann.text else ""
        pos = note_low.find(head.lower()) if head else -1
        span_len = len(head)
        if pos < 0:
            return "(not located)"
    start = max(0, pos - width)
    end = min(len(note), pos + span_len + width)
    return "…" + " ".join(note[start:end].split()) + "…"


def _dx_category(concept: str) -> str:
    if concept == "epilepsy":
        return "generic 'epilepsy'"
    if is_epilepsy_seizure_type(concept):
        return "named seizure type"
    if "epilep" in concept:
        return "specific epilepsy syndrome"
    return "other"


def _anns_for_keys(annotations, keys: set) -> list[ExectAnnotation]:
    """Best-effort: map concept keys back to the annotation(s) whose canonicalized
    concept produced them, for context display."""
    out = []
    seen = set()
    for a in annotations:
        concept = canonicalize_diagnosis_concept(a.text)
        key = ("Diagnosis", concept)
        if key in keys and key not in seen:
            out.append(a)
            seen.add(key)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gold_letters = gepa_data.load_dev_letters()
    pred_by_id = _pred_letters(RUN_ID)
    empty_letter = lambda lid: ExectLetter(letter_id=lid, note_text="", annotations=())  # noqa: E731
    pred_letters = [pred_by_id.get(g.letter_id) or empty_letter(g.letter_id) for g in gold_letters]

    official = score_concept_identity(gold_letters, pred_letters, "Diagnosis").concept_only

    sum_precision_tp = sum_recall_tp = sum_pred_count = sum_gold_count = 0
    index = []
    cat_missed: Counter[str] = Counter()
    cat_spurious: Counter[str] = Counter()
    n_disagreement_letters = 0

    for g in gold_letters:
        p = pred_by_id.get(g.letter_id) or empty_letter(g.letter_id)

        gold_set = set(concept_keys(g.entities("Diagnosis"), "Diagnosis", "concept"))
        recall_pool = set(concept_keys(p.annotations, "Diagnosis", "concept"))
        home_set = set(concept_keys(p.entities("Diagnosis"), "Diagnosis", "concept"))

        recall_tp = len(gold_set & recall_pool)
        precision_tp = len(gold_set & home_set)
        missed = gold_set - recall_pool  # genuine FN: no overlapping prediction anywhere in the letter
        spurious = home_set - gold_set  # FP: home-tagged Diagnosis prediction with no gold match

        sum_recall_tp += recall_tp
        sum_precision_tp += precision_tp
        sum_pred_count += len(home_set)
        sum_gold_count += len(gold_set)

        for key in missed:
            cat_missed[_dx_category(key[1])] += 1
        for key in spurious:
            cat_spurious[_dx_category(key[1])] += 1

        rec = {
            "letter_id": g.letter_id,
            "gold_concepts": sorted(k[1] for k in gold_set),
            "missed_concepts": sorted(k[1] for k in missed),
            "spurious_concepts": sorted(k[1] for k in spurious),
            "recall_tp": recall_tp,
            "precision_tp": precision_tp,
            "gold_count": len(gold_set),
            "pred_count": len(home_set),
            "letter_exact": not missed and not spurious,
        }
        index.append(rec)

        if missed or spurious:
            n_disagreement_letters += 1
            write_substrate(OUT, g, p, rec, missed, spurious, gold_set, home_set)

    decomposed = _clinical_recovery_prf1(
        precision_tp=sum_precision_tp,
        recall_tp=sum_recall_tp,
        pred_count=sum_pred_count,
        gold_count=sum_gold_count,
    )
    decomposition_matches_official = (
        abs(decomposed.f1 - official.f1) < 1e-9
        and abs(decomposed.precision - official.precision) < 1e-9
        and abs(decomposed.recall - official.recall) < 1e-9
    )

    total_missed = sum(cat_missed.values())
    total_spurious = sum(cat_spurious.values())

    summary = {
        "run_id": RUN_ID,
        "n_letters": len(gold_letters),
        "official_concept_only": official.model_dump(),
        "decomposed_from_index": decomposed.model_dump(),
        "decomposition_matches_official": decomposition_matches_official,
        "n_disagreement_letters": n_disagreement_letters,
        "n_exact_letters": len(gold_letters) - n_disagreement_letters,
        "total_genuine_missed": total_missed,
        "total_spurious": total_spurious,
        "missed_by_category": dict(cat_missed.most_common()),
        "spurious_by_category": dict(cat_spurious.most_common()),
    }
    (OUT / "_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    print("=== CANONICAL DIAGNOSIS clinical_headline ANALYSIS ===")
    print(f"OFFICIAL  concept_only: P={official.precision:.4f} R={official.recall:.4f} F1={official.f1:.4f} "
          f"(precision_tp={official.precision_tp} recall_tp={official.recall_tp} "
          f"pred_count={official.pred_count} gold_count={official.gold_count})")
    print(f"DECOMPOSED from index : P={decomposed.precision:.4f} R={decomposed.recall:.4f} F1={decomposed.f1:.4f}")
    print(f"decomposition matches official: {decomposition_matches_official}")
    print(f"disagreement letters: {n_disagreement_letters}/{len(gold_letters)} "
          f"({n_disagreement_letters/len(gold_letters):.1%})")
    print(f"genuine missed (FN): {total_missed}  by category: {dict(cat_missed.most_common())}")
    print(f"spurious (FP)      : {total_spurious}  by category: {dict(cat_spurious.most_common())}")
    print(f"\nWrote per-letter substrate for {n_disagreement_letters} letters + "
          f"_index.json + _summary.json to {OUT}")


def write_substrate(out_dir, gold_letter, pred_letter, rec, missed, spurious, gold_set, home_set):
    missed_anns = _anns_for_keys(gold_letter.entities("Diagnosis"), missed)
    spurious_anns = _anns_for_keys(pred_letter.entities("Diagnosis"), spurious)

    lines = [
        f"# {gold_letter.letter_id} — gold={rec['gold_concepts']}",
        f"missed (FN, no overlapping prediction)={rec['missed_concepts']}",
        f"spurious (FP, home-tagged, no gold match)={rec['spurious_concepts']}\n",
        "## GOLD Diagnosis mentions",
    ]
    lines += [
        f"- {a.text!r} -> concept={canonicalize_diagnosis_concept(a.text)!r}"
        for a in gold_letter.entities("Diagnosis")
    ] or ["(none)"]
    lines += ["", "## PREDICTED Diagnosis mentions (home-tagged)"]
    lines += [
        f"- {a.text!r} -> concept={canonicalize_diagnosis_concept(a.text)!r}"
        for a in pred_letter.entities("Diagnosis")
    ] or ["(none)"]
    other_pred = [a for a in pred_letter.annotations if a.entity != "Diagnosis"]
    dx_like_other = [
        a for a in other_pred
        if ("Diagnosis", canonicalize_diagnosis_concept(a.text)) in gold_set
    ]
    if dx_like_other:
        lines += ["", "## PREDICTED under a DIFFERENT entity label that still covers a gold Dx concept"]
        lines += [f"- entity={a.entity!r} {a.text!r} -> concept={canonicalize_diagnosis_concept(a.text)!r}" for a in dx_like_other]

    lines += ["", "## Context for MISSED gold concepts"]
    lines += [f"- MISSED {canonicalize_diagnosis_concept(a.text)!r}: {_context(gold_letter.note_text, a)}" for a in missed_anns] or ["(none)"]
    lines += ["", "## Context for SPURIOUS predicted concepts"]
    lines += [f"- SPURIOUS {canonicalize_diagnosis_concept(a.text)!r}: {_context(gold_letter.note_text, a)}" for a in spurious_anns] or ["(none)"]

    lines += ["", "## FULL LETTER TEXT", "```", gold_letter.note_text, "```"]
    (out_dir / f"{gold_letter.letter_id}.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
