"""Phase 0+1 of
``docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md``.

Question: does the SAME gold-consolidation mechanism that inflates the scored
``clinical_headline`` Diagnosis gap (85.2% of disagreements are gold multiplicity, per
``exectv2_dx_canonical_row_analysis.py`` + its adjudication) ALSO inflate the
``source_near`` evidence-recall gap that the GEPA-vs-hybrid evidence-decomposition doc
used to justify a "build more retrieval lanes" prioritization?

Method: take the 92 Diagnosis ``missed_concepts`` from ``_dx_canonical/_index.json``
(clinical_headline FNs, concept-key matching, entity-agnostic recall pool), map each
back to its underlying gold ``ExectAnnotation``(s), and run the EXACT
``_first_overlapping_prediction`` phrase-substring logic ``source_near`` uses (home-
tagged Diagnosis predictions only) twice per annotation:

  1. respecting ``used_pred`` in the same per-letter traversal order
     ``_source_near_entity`` uses (the official mechanism) -- isolates whether this
     concept is ALSO a source_near FN, or whether the looser phrase-overlap match
     already counts it as a source_near TP despite being a concept-key miss.
  2. ignoring ``used_pred`` (fresh empty set per annotation) -- does ANY home-tagged
     Diagnosis prediction phrase-overlap exist at all, regardless of cardinality.

Classification per (letter, missed concept):
  H1_CARDINALITY        -- overlap exists ignoring used_pred, absent respecting it.
  H2_GENUINE_DIVERGENCE -- no overlap exists either way.
  NOT_SOURCE_NEAR_FN    -- matched even respecting used_pred (not an FN under
                           source_near at all -- informational, not part of H1/H2).

Cross-tabulated against the existing Dx adjudication verdict (``GOLD_RIGHT`` /
``MODEL_DEFENSIBLE`` / ``BOTH_DEFENSIBLE``) for that exact (letter, MISSED, concept)
triple. Reports the plan's kill-criterion number: the share of the 92 misses in
H1_CARDINALITY + (H2_GENUINE_DIVERGENCE and MODEL_DEFENSIBLE/BOTH_DEFENSIBLE) vs the
share in H2_GENUINE_DIVERGENCE and GOLD_RIGHT (the only unambiguous "real,
attributable retrieval miss" bucket).

Zero new LLM calls -- replays the cached GEPA per-family prediction jsonl
(``exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628``) and reuses
``_dx_canonical/_index.json`` + ``_adjudication.csv`` (today's Dx adjudication).

Usage: uv run python experiments/exectv2_dx_evidence_recall_consolidation_check.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    _first_overlapping_prediction,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DX_CANONICAL = ROOT / "_dx_canonical"
RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"

H1_CARDINALITY = "H1_CARDINALITY"
H2_GENUINE_DIVERGENCE = "H2_GENUINE_DIVERGENCE"
NOT_SOURCE_NEAR_FN = "NOT_SOURCE_NEAR_FN"


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


def _anns_for_concept(annotations, concept: str) -> list[ExectAnnotation]:
    return [a for a in annotations if canonicalize_diagnosis_concept(a.text) == concept]


def _respecting_used_pred_trace(
    gold_anns: list[ExectAnnotation], pred_anns: list[ExectAnnotation]
) -> list[int | None]:
    """Mirror ``_source_near_entity``'s per-letter loop exactly: shared ``used_pred``
    state across gold annotations processed in order. Returns the matched pred index
    (or None) per gold annotation, aligned with ``gold_anns``."""
    used_pred: set[int] = set()
    trace: list[int | None] = []
    for gold in gold_anns:
        pred_index = _first_overlapping_prediction(gold, pred_anns, used_pred)
        trace.append(pred_index)
        if pred_index is not None:
            used_pred.add(pred_index)
    return trace


def _ignoring_used_pred_match(gold: ExectAnnotation, pred_anns: list[ExectAnnotation]) -> bool:
    return _first_overlapping_prediction(gold, pred_anns, set()) is not None


def _any_entity_overlap(gold: ExectAnnotation, all_pred_anns: list[ExectAnnotation]) -> bool:
    gold_phrase = normalize_phrase(gold.text)
    if not gold_phrase:
        return False
    for pred in all_pred_anns:
        pred_phrase = normalize_phrase(pred.text)
        if pred_phrase and (gold_phrase in pred_phrase or pred_phrase in gold_phrase):
            return True
    return False


def load_adjudication() -> dict[tuple[str, str], str]:
    rows = list(csv.DictReader((DX_CANONICAL / "_adjudication.csv").open(encoding="utf-8")))
    return {(r["letter"], r["concept"]): r["verdict"] for r in rows if r["direction"] == "MISSED"}


def main() -> None:
    gold_letters = gepa_data.load_dev_letters()
    pred_by_id = _pred_letters(RUN_ID)
    empty_letter = lambda lid: ExectLetter(letter_id=lid, note_text="", annotations=())  # noqa: E731

    index = json.loads((DX_CANONICAL / "_index.json").read_text(encoding="utf-8"))
    verdicts = load_adjudication()

    # --- Phase 0: self-validation gate -------------------------------------- #
    pred_letters = [pred_by_id.get(g.letter_id) or empty_letter(g.letter_id) for g in gold_letters]
    official_sn = source_near_diagnostic(
        gold_letters, pred_letters, ["Diagnosis"], benchmark_config_for
    )
    official_dx = official_sn.per_entity["Diagnosis"]

    own_tp = own_fn = 0
    for g in gold_letters:
        p = pred_by_id.get(g.letter_id) or empty_letter(g.letter_id)
        gold_anns = list(g.entities("Diagnosis"))
        pred_anns = list(p.entities("Diagnosis"))
        trace = _respecting_used_pred_trace(gold_anns, pred_anns)
        own_tp += sum(1 for t in trace if t is not None)
        own_fn += sum(1 for t in trace if t is None)

    gate_pass = own_tp == official_dx.overlap.tp and own_fn == official_dx.overlap.fn
    print("=== PHASE 0: self-validation gate ===")
    print(
        f"official source_near Diagnosis: tp={official_dx.overlap.tp} fn={official_dx.overlap.fn} "
        f"recall={official_dx.overlap.recall:.4f}"
    )
    print(f"own trace reproduction        : tp={own_tp} fn={own_fn}")
    print(f"GATE {'PASS' if gate_pass else 'FAIL'}")
    if not gate_pass:
        raise SystemExit(
            "Phase 0 gate failed -- own _first_overlapping_prediction trace does not "
            "reproduce the official source_near Diagnosis tp/fn. Stopping before Phase 1."
        )

    # --- Phase 1: the decomposition ------------------------------------------ #
    rows_out = []
    mechanism_counts: Counter[str] = Counter()
    crosstab: Counter[tuple[str, str]] = Counter()
    cross_entity_flags = 0  # informational only, not folded into H1/H2

    for letter_rec in index:
        letter_id = letter_rec["letter_id"]
        missed_concepts = letter_rec["missed_concepts"]
        if not missed_concepts:
            continue

        gold_letter = next(g for g in gold_letters if g.letter_id == letter_id)
        pred_letter = pred_by_id.get(letter_id) or empty_letter(letter_id)
        gold_anns = list(gold_letter.entities("Diagnosis"))
        pred_anns = list(pred_letter.entities("Diagnosis"))
        all_pred_anns = list(pred_letter.annotations)

        respecting_trace = _respecting_used_pred_trace(gold_anns, pred_anns)
        ann_index = {id(a): i for i, a in enumerate(gold_anns)}

        for concept in missed_concepts:
            concept_anns = _anns_for_concept(gold_anns, concept)
            if not concept_anns:
                # Shouldn't happen (missed_concepts is derived from these same gold
                # annotations), but guard rather than silently mis-tabulate.
                continue

            matched_respecting = any(
                respecting_trace[ann_index[id(a)]] is not None for a in concept_anns
            )
            matched_ignoring = any(_ignoring_used_pred_match(a, pred_anns) for a in concept_anns)

            if matched_respecting:
                mechanism = NOT_SOURCE_NEAR_FN
            elif matched_ignoring:
                mechanism = H1_CARDINALITY
            else:
                mechanism = H2_GENUINE_DIVERGENCE

            verdict = verdicts.get((letter_id, concept), "UNKNOWN")
            mechanism_counts[mechanism] += 1
            crosstab[(mechanism, verdict)] += 1

            if mechanism == H2_GENUINE_DIVERGENCE:
                if any(_any_entity_overlap(a, all_pred_anns) for a in concept_anns):
                    cross_entity_flags += 1

            rows_out.append(
                {
                    "letter_id": letter_id,
                    "concept": concept,
                    "mechanism": mechanism,
                    "adjudication_verdict": verdict,
                }
            )

    total = sum(mechanism_counts.values())
    assert total == 92, f"expected 92 missed concepts, classified {total}"

    h1 = mechanism_counts[H1_CARDINALITY]
    h2 = mechanism_counts[H2_GENUINE_DIVERGENCE]
    not_fn = mechanism_counts[NOT_SOURCE_NEAR_FN]

    h2_gold_right = crosstab[(H2_GENUINE_DIVERGENCE, "GOLD_RIGHT")]
    h2_model_defensible = crosstab[(H2_GENUINE_DIVERGENCE, "MODEL_DEFENSIBLE")]
    h2_both_defensible = crosstab[(H2_GENUINE_DIVERGENCE, "BOTH_DEFENSIBLE")]

    inflated_bucket = h1 + not_fn + h2_model_defensible + h2_both_defensible
    genuine_bucket = h2_gold_right
    inflated_bucket + genuine_bucket
    inflated_share = inflated_bucket / total
    genuine_share = genuine_bucket / total

    print("\n=== PHASE 1: mechanism x verdict cross-tab (92 Diagnosis missed_concepts) ===")
    print(
        f"{'mechanism':<22}{'GOLD_RIGHT':>12}{'MODEL_DEFENSIBLE':>18}{'BOTH_DEFENSIBLE':>17}{'UNKNOWN':>9}{'TOTAL':>8}"
    )
    for mech in (H1_CARDINALITY, H2_GENUINE_DIVERGENCE, NOT_SOURCE_NEAR_FN):
        gr = crosstab[(mech, "GOLD_RIGHT")]
        md = crosstab[(mech, "MODEL_DEFENSIBLE")]
        bd = crosstab[(mech, "BOTH_DEFENSIBLE")]
        uk = crosstab[(mech, "UNKNOWN")]
        print(f"{mech:<22}{gr:>12}{md:>18}{bd:>17}{uk:>9}{mechanism_counts[mech]:>8}")
    print(f"{'TOTAL':<22}{'':>12}{'':>18}{'':>17}{'':>9}{total:>8}")

    print(
        f"\nmechanism marginals: H1_CARDINALITY={h1} ({h1 / total:.1%})  "
        f"H2_GENUINE_DIVERGENCE={h2} ({h2 / total:.1%})  NOT_SOURCE_NEAR_FN={not_fn} ({not_fn / total:.1%})"
    )
    print(
        "  (NOT_SOURCE_NEAR_FN = concept-key miss under clinical_headline that is ALREADY a "
        "source_near TP -- the looser phrase-overlap match credits it despite the concept-key miss)"
    )
    print(
        f"cross-entity overlap among H2 cases (informational, not folded into split): "
        f"{cross_entity_flags}/{h2}"
    )

    print("\n=== DECISION NUMBER (plan section 3 kill-criterion) ===")
    print(
        f"H-inflated bucket (H1 + NOT_SOURCE_NEAR_FN + H2-but-MODEL_DEFENSIBLE/BOTH_DEFENSIBLE): "
        f"{inflated_bucket}/{total} = {inflated_share:.1%}"
    )
    print(
        f"H-genuine bucket  (H2_GENUINE_DIVERGENCE and GOLD_RIGHT, the unambiguous real-miss bucket): "
        f"{genuine_bucket}/{total} = {genuine_share:.1%}"
    )
    if inflated_share >= 0.50:
        verdict_line = "H-inflated CONFIRMED (>= 50%)"
    elif inflated_share < 0.30:
        verdict_line = "H-genuine stands (< 30%)"
    else:
        verdict_line = "PARTIAL result (30-50%) -- report both numbers, no forced binary verdict"
    print(f"VERDICT: {verdict_line}")

    out = {
        "run_id": RUN_ID,
        "phase0_gate_pass": gate_pass,
        "official_source_near_diagnosis": official_dx.model_dump(),
        "n_missed_concepts": total,
        "mechanism_counts": dict(mechanism_counts),
        "crosstab": {f"{m}|{v}": c for (m, v), c in crosstab.items()},
        "cross_entity_overlap_among_h2": cross_entity_flags,
        "inflated_bucket": inflated_bucket,
        "inflated_share": inflated_share,
        "genuine_bucket": genuine_bucket,
        "genuine_share": genuine_share,
        "verdict": verdict_line,
        "rows": rows_out,
    }
    out_path = EXPERIMENTS / "exectv2_dx_evidence_recall_consolidation_check.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
