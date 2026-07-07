"""GEPA vs hybrid: how much of the gap is deterministic letter-recovery of MISSED
information, vs re-keying evidence the model already retrieved? (zero-LLM, read-only)

Answers two questions on the two best saved runs (dev140):

  Q1  How much of the HYBRID's score comes from deterministic rules recovering
      information the LLM completely missed (read the letter, add a fact)?
        -> score the hybrid's own prediction_surfaces ladder
           (source_scored -> evidence_valid -> dictionary_normalized ->
            residual_benchmark_added -> final). The lift AFTER
            dictionary_normalized is deterministic letter-recovery; the lift up to
            it is evidence re-keying. Also counts net facts added by the recovery
            stage and their gold-match (TP) rate.

  Q2  How much can the GEPA architecture improve by RE-USING the evidence it already
      retrieved (perfect deterministic re-keyer, no new extraction)?
        -> the source_near text-overlap ceiling: a gold fact is creditable if the
           system retrieved ANY same-entity overlapping-text prediction. The lift
           from the strict headline F1 to this overlap F1 is the re-keying headroom;
           the residual (1 - overlap recall) is evidence the model never retrieved.

Strict headline aggregate is computed exactly as the GEPA metric / dedup runner
(micro-F1 over the four canonical clinical_headline family scorers).

Usage:
    uv run python experiments/exectv2_gepa_vs_hybrid_evidence_decomposition.py
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import (
    KEY_FAMILIES,
    _counts,
    _f1_from,
    _family_scores,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    score_frequency_state,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"

GEPA_RUN = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"
HYBRID_RUN = "exectv2_holistic_finding_assembly_v08_dev140_20260621"
HYBRID_SURFACES = [
    "source_scored",
    "evidence_valid",
    "dictionary_normalized",
    "residual_benchmark_added",
    "final",
]


def _letter_from_mentions(letter_id: str, mentions: list[dict]) -> ExectLetter:
    anns = tuple(
        ExectAnnotation(
            entity=m["entity"],
            text=m.get("text", ""),
            attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
        )
        for m in mentions
    )
    return ExectLetter(letter_id=letter_id, note_text="", annotations=anns)


def _load_jsonl(run_id: str) -> list[dict]:
    return [
        json.loads(line)
        for line in (EXPERIMENTS / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def gepa_predictions() -> dict[str, ExectLetter]:
    out: dict[str, ExectLetter] = {}
    for row in _load_jsonl(GEPA_RUN):
        out[row["letter_id"]] = _letter_from_mentions(
            row["letter_id"], row.get("predicted_mentions", [])
        )
    return out


def hybrid_surface_predictions(surface: str) -> dict[str, ExectLetter]:
    out: dict[str, ExectLetter] = {}
    for row in _load_jsonl(HYBRID_RUN):
        surf = (row.get("prediction_surfaces") or {}).get(surface)
        if surf is None:
            surf = row.get("predicted_mentions", [])
        out[row["letter_id"]] = _letter_from_mentions(row["letter_id"], surf)
    return out


# --------------------------------------------------------------------------- #
# Scoring                                                                      #
# --------------------------------------------------------------------------- #
def strict_headline(gold: list[ExectLetter], pred_by_id: dict[str, ExectLetter]):
    """Micro-F1 over the four clinical_headline families + per-family F1 (the real score)."""
    agg = [0, 0, 0, 0]
    fam = {f: [0, 0, 0, 0] for f in KEY_FAMILIES}
    for g in gold:
        p = pred_by_id.get(g.letter_id) or ExectLetter(g.letter_id, "", ())
        scores = _family_scores(g, p)
        for f in KEY_FAMILIES:
            c = _counts(scores[f])
            for i in range(4):
                fam[f][i] += c[i]
                agg[i] += c[i]
    # agg = [precision_tp, recall_tp, pred_count, gold_count]
    agg_recall = agg[1] / agg[3] if agg[3] else 0.0
    fam_recall = {f: (fam[f][1] / fam[f][3] if fam[f][3] else 0.0) for f in KEY_FAMILIES}
    return (
        _f1_from(*agg),
        {f: _f1_from(*fam[f]) for f in KEY_FAMILIES},
        agg,
        agg_recall,
        fam_recall,
        fam,
    )


def overlap_ceiling(gold: list[ExectLetter], pred_by_id: dict[str, ExectLetter]):
    """source_near text-overlap PRF1: credit any gold whose evidence was retrieved.

    Returns (overall_f1, overall_recall, overall_precision, attr_agreement_rate,
             per_family{f: (f1, recall, attr_rate)}).
    """
    preds = [pred_by_id.get(g.letter_id) or ExectLetter(g.letter_id, "", ()) for g in gold]
    diag = source_near_diagnostic(gold, preds, list(KEY_FAMILIES), benchmark_config_for)
    ov = diag.overall.overlap
    per = {}
    for f in KEY_FAMILIES:
        e = diag.per_entity[f]
        per[f] = (e.overlap.f1, e.overlap.recall, e.attribute_agreement_rate)
    return ov.f1, ov.recall, ov.precision, diag.overall.attribute_agreement_rate, per


def _key_set(mentions: list[dict]) -> set:
    return {
        (
            m["entity"],
            (m.get("text") or "").strip().lower(),
            tuple(sorted((str(k), str(v)) for k, v in (m.get("attributes") or {}).items())),
        )
        for m in mentions
    }


def recovery_stage_attribution(gold: list[ExectLetter]):
    """Net facts the deterministic recovery stage ADDS (dictionary_normalized ->
    final) and how many of those added facts land on a gold concept (TP)."""
    gold_by_id = {g.letter_id: g for g in gold}
    added_total = 0
    added_tp = 0
    dropped_total = 0
    for row in _load_jsonl(HYBRID_RUN):
        surfaces = row.get("prediction_surfaces") or {}
        before = surfaces.get("dictionary_normalized")
        after = surfaces.get("final")
        if before is None or after is None:
            continue
        before_keys = _key_set(before)
        added = [
            m
            for m in after
            if (
                m["entity"],
                (m.get("text") or "").strip().lower(),
                tuple(sorted((str(k), str(v)) for k, v in (m.get("attributes") or {}).items())),
            )
            not in before_keys
        ]
        dropped = len(before) - (len(after) - len(added))
        added_total += len(added)
        dropped_total += max(0, dropped)
        g = gold_by_id.get(row["letter_id"])
        if g is None or not added:
            continue
        # An added fact is a "hit" if its text overlaps a gold mention of the same entity.
        pred_letter = _letter_from_mentions(row["letter_id"], added)
        diag = source_near_diagnostic([g], [pred_letter], list(KEY_FAMILIES), benchmark_config_for)
        added_tp += diag.overall.overlap.tp
    return added_total, added_tp, dropped_total


def recall_deficit_decomposition(gold: list[ExectLetter], pred_by_id: dict[str, ExectLetter]):
    """Decompose each family's strict-headline FALSE NEGATIVES (the recall deficit)
    into: retrieved-but-mis-keyed (an overlapping same-family prediction exists, so
    re-using the evidence could recover it) vs genuinely-not-retrieved (no overlapping
    prediction at all). Nested by construction: we only inspect strict FNs.
    """
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
        normalize_phrase,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import (
        _family_unit_keys,
    )

    def _overlap(a: str, bs: list[str]) -> bool:
        return bool(a and any(b and (a in b or b in a) for b in bs))

    per = {
        f: {
            "fn": 0,
            "miskeyed": 0,
            "genuine": 0,
            "fp": 0,
            "fp_overlap": 0,
            # strict counts for the oracle re-key ceiling
            "ptp": 0,
            "rtp": 0,
            "pc": 0,
            "gc": 0,
        }
        for f in KEY_FAMILIES
    }
    for g in gold:
        p = pred_by_id.get(g.letter_id) or ExectLetter(g.letter_id, "", ())
        note = g.note_text
        for f in KEY_FAMILIES:
            gold_anns = list(g.entities(f))
            pred_anns = list(p.entities(f))
            gold_keys = set(_family_unit_keys(f, gold_anns, note))
            pred_keys = set(_family_unit_keys(f, pred_anns, note))
            missed = gold_keys - pred_keys
            spurious = pred_keys - gold_keys
            gold_phrases = [normalize_phrase(a.text) for a in gold_anns if a.text]
            pred_phrases = [normalize_phrase(a.text) for a in pred_anns if a.text]
            # recall side: missed gold units
            for ann in gold_anns:
                for key in _family_unit_keys(f, [ann], note):
                    if key not in missed:
                        continue
                    per[f]["fn"] += 1
                    if _overlap(normalize_phrase(ann.text), pred_phrases):
                        per[f]["miskeyed"] += 1
                    else:
                        per[f]["genuine"] += 1
            # precision side: spurious pred units
            for ann in pred_anns:
                for key in _family_unit_keys(f, [ann], note):
                    if key not in spurious:
                        continue
                    per[f]["fp"] += 1
                    if _overlap(normalize_phrase(ann.text), gold_phrases):
                        per[f]["fp_overlap"] += 1
    return per


def sf_state_profile(gold: list[ExectLetter], pred_by_id: dict[str, ExectLetter]) -> float:
    """The validated SF 'fair' metric (Gan per-letter state presence)."""
    agg = [0, 0, 0, 0]
    for g in gold:
        p = pred_by_id.get(g.letter_id) or ExectLetter(g.letter_id, "", ())
        s = score_frequency_state([g], [p]).state_profile
        agg[0] += s.tp  # precision_tp
        agg[1] += s.tp  # recall_tp
        agg[2] += s.tp + s.fp  # pred_count
        agg[3] += s.tp + s.fn  # gold_count
    return _f1_from(*agg)


# --------------------------------------------------------------------------- #
def main() -> None:
    gold = gepa_data.load_dev_letters()

    systems: dict[str, dict[str, ExectLetter]] = {
        "GEPA best (multifamily)": gepa_predictions(),
    }
    for surf in HYBRID_SURFACES:
        systems[f"hybrid::{surf}"] = hybrid_surface_predictions(surf)

    print(f"# GEPA vs hybrid evidence decomposition (dev140, {len(gold)} letters)\n")

    R: dict[str, dict] = {}
    for name, pred in systems.items():
        strict_f1, strict_fam, agg, agg_recall, fam_recall, fam_counts = strict_headline(gold, pred)
        ov_f1, ov_r, ov_p, attr_rate, ov_per = overlap_ceiling(gold, pred)
        sfp = sf_state_profile(gold, pred)
        R[name] = dict(
            strict_f1=strict_f1,
            strict_fam=strict_fam,
            agg=agg,
            agg_recall=agg_recall,
            fam_recall=fam_recall,
            fam_counts=fam_counts,
            sfp=sfp,
            ov_f1=ov_f1,
            ov_r=ov_r,
            ov_p=ov_p,
            attr_rate=attr_rate,
            ov_per=ov_per,
        )

    # --- Headline ladder ----------------------------------------------------- #
    print("## Strict headline aggregate F1 (the real score) + SF state_profile (fair SF)\n")
    print(f"{'system':<34}{'strict F1':>10}{'Dx':>7}{'SF':>7}{'Rx':>7}{'Inv':>7}{'SF_prof':>9}")
    for name, r in R.items():
        sfam = r["strict_fam"]
        print(
            f"{name:<34}{r['strict_f1']:>10.3f}{sfam['Diagnosis']:>7.3f}{sfam['SeizureFrequency']:>7.3f}"
            f"{sfam['Prescription']:>7.3f}{sfam['Investigations']:>7.3f}{r['sfp']:>9.3f}"
        )

    # --- Evidence-presence ceiling ------------------------------------------ #
    print(
        "\n## Evidence-presence ceiling (source_near same-entity text-overlap): "
        "credit any gold whose evidence was retrieved\n"
    )
    print(f"{'system':<34}{'ovlp F1':>9}{'ovlp R':>8}{'ovlp P':>8}{'attr-agree':>11}")
    for name, r in R.items():
        print(
            f"{name:<34}{r['ov_f1']:>9.3f}{r['ov_r']:>8.3f}{r['ov_p']:>8.3f}{r['attr_rate']:>11.3f}"
        )

    # --- Evidence captured by the LLM vs shuffled in deterministically ------- #
    print(
        "\n## Evidence-recall counts: LLM-captured vs deterministically recovered "
        "(gold mentions with overlapping retrieved evidence)\n"
    )
    print(f"{'system':<34}{'gold w/ ev':>11}{'/ total':>9}{'ev-recall':>11}")
    for name in ["GEPA best (multifamily)"] + [f"hybrid::{s}" for s in HYBRID_SURFACES]:
        preds = [systems[name].get(g.letter_id) or ExectLetter(g.letter_id, "", ()) for g in gold]
        ov = source_near_diagnostic(
            gold, preds, list(KEY_FAMILIES), benchmark_config_for
        ).overall.overlap
        print(f"{name:<34}{ov.tp:>11}{ov.tp + ov.fn:>9}{ov.recall:>11.3f}")
    print(
        "  hybrid LLM producers = `source_scored`; the deterministic stack's NET add to "
        "evidence-recall is `final` - `source_scored` (recovery adds, normalization re-keys)."
    )

    # --- Per-family recall decomposition (the cleanest Q2 view) -------------- #
    print("\n## Per-family RECALL: strict (keyed right) vs evidence-presence (retrieved)\n")
    print(
        f"{'system':<28}{'family':<16}{'strict R':>9}{'ev-recall':>10}{'mis-keyed':>10}{'not-retr':>9}"
    )
    for name in ("GEPA best (multifamily)", "hybrid::source_scored", "hybrid::final"):
        r = R[name]
        for f in KEY_FAMILIES:
            sr = r["fam_recall"][f]
            er = r["ov_per"][f][1]
            print(f"{name:<28}{f:<16}{sr:>9.3f}{er:>10.3f}{max(0, er - sr):>10.3f}{1 - er:>9.3f}")

    # --- The two decompositions --------------------------------------------- #
    g = R["GEPA best (multifamily)"]
    hyb_src = R["hybrid::source_scored"]
    hyb_dict = R["hybrid::dictionary_normalized"]
    hyb_final = R["hybrid::final"]

    print("\n## Q2 — GEPA: how much can re-using the evidence it ALREADY retrieved buy?")
    print(
        "   (strict-headline FALSE NEGATIVES split by whether overlapping evidence was retrieved)\n"
    )
    dec = recall_deficit_decomposition(gold, systems["GEPA best (multifamily)"])
    tot_fn = sum(d["fn"] for d in dec.values())
    tot_mk = sum(d["miskeyed"] for d in dec.values())
    tot_gn = sum(d["genuine"] for d in dec.values())
    print(f"{'family':<18}{'FN units':>9}{'mis-keyed':>11}{'genuine-miss':>14}")
    for f in KEY_FAMILIES:
        d = dec[f]
        print(f"{f:<18}{d['fn']:>9}{d['miskeyed']:>11}{d['genuine']:>14}")
    print(f"{'TOTAL':<18}{tot_fn:>9}{tot_mk:>11}{tot_gn:>14}")
    print(
        f"  => of GEPA's {tot_fn} missed gold units, {tot_mk} ({100 * tot_mk / tot_fn:.0f}%) have overlapping "
        f"retrieved evidence (re-keyable); {tot_gn} ({100 * tot_gn / tot_fn:.0f}%) are genuinely not retrieved."
    )

    # Oracle re-key ceiling: credit every mis-keyed FN and every overlapping spurious FP.
    o_agg = [0, 0, 0, 0]
    for f in KEY_FAMILIES:
        ptp, rtp, pc, gc = g["fam_counts"][f]
        d = dec[f]
        o_agg[0] += ptp + d["fp_overlap"]  # precision_tp + recovered spurious
        o_agg[1] += rtp + d["miskeyed"]  # recall_tp   + recovered misses
        o_agg[2] += pc
        o_agg[3] += gc
    oracle_f1 = _f1_from(*o_agg)
    print("\n  ORACLE re-key ceiling (perfect re-keyer of retrieved evidence, no new extraction):")
    print(
        f"    GEPA strict {g['strict_f1']:.3f} -> {oracle_f1:.3f}  (+{oracle_f1 - g['strict_f1']:.3f} upper bound)"
    )
    print(
        f"    The biggest validated slice is SF state representation: SF clinical_headline "
        f"{g['strict_fam']['SeizureFrequency']:.3f} -> state_profile {g['sfp']:.3f} "
        f"(+{g['sfp'] - g['strict_fam']['SeizureFrequency']:.3f})."
    )
    print(
        f"    Even at this oracle ceiling, {oracle_f1:.3f} < hybrid {hyb_final['strict_f1']:.3f}: "
        f"the residual {hyb_final['strict_f1'] - oracle_f1:.3f} is gold GEPA never retrieved."
    )

    added_total, added_tp, dropped_total = recovery_stage_attribution(gold)
    print("\n## Q1 — hybrid: how much of its score is DETERMINISTIC recovery of MISSED info?")
    print(
        f"  raw LLM producers (source_scored) F1 ...... {hyb_src['strict_f1']:.3f}   "
        f"(Dx {hyb_src['strict_fam']['Diagnosis']:.3f} / SF {hyb_src['strict_fam']['SeizureFrequency']:.3f} / "
        f"Rx {hyb_src['strict_fam']['Prescription']:.3f} / Inv {hyb_src['strict_fam']['Investigations']:.3f})"
    )
    print(
        f"  + deterministic RE-KEYING (dictionary_normalized) .. {hyb_dict['strict_f1']:.3f}   "
        f"(+{hyb_dict['strict_f1'] - hyb_src['strict_f1']:.3f}; re-uses retrieved evidence)"
    )
    print(
        f"  + deterministic letter-RECOVERY (final) ............ {hyb_final['strict_f1']:.3f}   "
        f"(+{hyb_final['strict_f1'] - hyb_dict['strict_f1']:.3f}; reads letter, adds missed facts)"
    )
    print(
        f"  net facts ADDED by recovery stage ......... {added_total}, "
        f"of which {added_tp} land on a gold concept "
        f"({100 * added_tp / added_total:.0f}% TP)"
        if added_total
        else "  (none added)"
    )
    print(f"  net facts dropped by cleanup .............. {dropped_total}")
    det_total = hyb_final["strict_f1"] - hyb_src["strict_f1"]
    det_recovery = hyb_final["strict_f1"] - hyb_dict["strict_f1"]
    print(
        f"  => deterministic stack contributes +{det_total:.3f} of the hybrid's {hyb_final['strict_f1']:.3f}; "
        f"only +{det_recovery:.3f} is letter-recovery of missed info (rest is re-keying)."
    )

    print(
        "\n## Cross-architecture: where the GEPA->hybrid gap of "
        f"{hyb_final['strict_f1'] - g['strict_f1']:.3f} lives"
    )
    print(
        f"  evidence the hybrid retrieves that GEPA does not: ev-recall "
        f"{g['ov_r']:.3f} -> {hyb_final['ov_r']:.3f} (+{hyb_final['ov_r'] - g['ov_r']:.3f})"
    )
    print(
        f"  the hybrid's deterministic stack is almost entirely Diagnosis re-keying/recovery: "
        f"Dx {hyb_src['strict_fam']['Diagnosis']:.3f} -> {hyb_final['strict_fam']['Diagnosis']:.3f}"
    )
    print(
        "  SF/Rx/Inv get ~zero from determinism — their hybrid edge is the focused LLM producers."
    )


if __name__ == "__main__":
    main()
