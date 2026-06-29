"""Canonical per-row clinical adjudication of the 53 stage-2 SF disagreement letters.

Each verdict is a clinical judgment made from the full letter + gold SF mentions +
gold Diagnosis (category/certainty/negation) + the model's stage-1/stage-2 facts, under
the *direction-blind* ``state_profile`` metric. Set in stone here so the tally is computed,
not hand-counted. See docs/experiments/exectv2/seizure_frequency/
exectv2_sf_canonical_metric_row_analysis_2026-06-29.md for the prose.

verdict ∈ {GOLD_RIGHT, BOTH_DEFENSIBLE, MODEL_DEFENSIBLE}
  GOLD_RIGHT       — genuine model error (gold is clinically correct).
  MODEL_DEFENSIBLE — model is clinically correct; the score is wrong because gold
                     under-annotated the stated frequency OR redundantly double-tagged a
                     type (rate + qualitative) that the metric's state-set then penalizes.
  BOTH_DEFENSIBLE  — genuine IAA-0.47 ambiguity, or a gold temporal convention
                     (historical-dated-count = active-rate; last-event = seizure-free).
mechanism — the error mechanism (see doc §6).
verify    — "" | "regression" (verify dropped a correct stage-1 fact) | "fix".
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# letter: (verdict, mechanism, verify_flag, one-line reason)
VERDICTS: dict[str, tuple[str, str, str, str]] = {
    # ---- gold=[] over-emission (22) ----
    "EA0014": ("GOLD_RIGHT", "over-call-changed", "", "‘continues to get seizures’ — no rate, no explicit direction; model stamped changed/increased (unsupported)."),
    "EA0016": ("GOLD_RIGHT", "single-event-as-rate", "", "single first focal event (SingleSeizure dx, no epilepsy); not a frequency."),
    "EA0018": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "definite epilepsy; ‘episodes around twice a week’ stated — gold annotated nothing."),
    "EA0021": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "complex partial sz c5, abnormal EEG; ‘occur 4 to 5 times a year’ — gold annotated nothing."),
    "EA0040": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "symptomatic epilepsy c5 on 2 AEDs; ‘three or four further episodes’ — gold annotated nothing."),
    "EA0043": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "Epilepsy c5; ‘4 events… roughly every year since 15’ — recurrent rate gold omitted."),
    "EA0045": ("BOTH_DEFENSIBLE", "characterisation-stage", "", "focal epilepsy c5 but day-dream/nocturnal events under characterisation; semi-quantified."),
    "EA0092": ("BOTH_DEFENSIBLE", "resolved-event", "", "genetic epilepsy c5; ‘further cluster… controlled rapidly’ — current but resolved."),
    "EA0104": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "simple-partial c5; ‘smaller versions… several times per week’ current rate gold omitted (seizure-free part is historical)."),
    "EA0109": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "focal/temporal sz c5; ‘2-3 times a week for 6 months’ explicit current rate + increase, gold omitted both."),
    "EA0114": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "focal epilepsy c5; ‘a couple of focal impaired awareness seizures’ current events gold omitted."),
    "EA0116": ("BOTH_DEFENSIBLE", "first-seizure-clinic", "", "Virtual First Seizure Clinic; ‘few episodes from sleep’ establishing events."),
    "EA0141": ("GOLD_RIGHT", "lifetime-count-as-rate", "", "new dx; model keyed ‘at least three seizures he has epilepsy’ — a lifetime diagnostic count, not a current rate."),
    "EA0146": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "Epilepsy c5; ‘6 of these during the last year’ + ‘few times every month’ — explicit rates gold omitted."),
    "EA0153": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "focal epilepsy c5; ‘episodes for 6 years, 1-2 per month’ — recurrent rate gold omitted (MRI/EEG pending)."),
    "EA0160": ("GOLD_RIGHT", "non-epileptic-over-emission", "", "events ‘probably anxiety… non-epileptic attacks’; model tagged seizure-free on functional events."),
    "EA0164": ("BOTH_DEFENSIBLE", "new-diagnosis", "", "epilepsy unclassified (new dx); ‘five episodes of LOC in last few months’ establishing events."),
    "EA0166": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "JME c5; ‘jerks… still occurring around once a month’ — explicit current rate gold omitted."),
    "EA0171": ("BOTH_DEFENSIBLE", "new-diagnosis-free", "", "Epilepsy probable focal (new dx); ‘since lamotrigine no further episodes’ — seizure-free state, gold omitted."),
    "EA0172": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "refractory focal epilepsy c5; ‘ongoing seizures… most days’ — active high frequency gold omitted (vague count)."),
    "EA0183": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "epilepsy c5 (same patient text as EA0021); ‘occur 4 to 5 times a year’ gold omitted."),
    "EA0200": ("GOLD_RIGHT", "new-diagnosis-events", "", "new GGE dx; ‘two events of LOC were GTC’ — establishing events at first diagnosis, not a treated rate."),
    # ---- recall misses (model missed a gold state), gold non-empty ----
    "EA0005": ("MODEL_DEFENSIBLE", "gold-multiplicity", "", "gold tags GTC seizure-free AND generic seizures active-rate (2/yr); model emitted the rate, missed the per-type free tag."),
    "EA0011": ("MODEL_DEFENSIBLE", "gold-multiplicity", "", "gold double-tags FBTC as seizure-free AND changed/Infrequent; model has rate+free, missed the qualitative Infrequent."),
    "EA0022": ("BOTH_DEFENSIBLE", "controlled=infrequent-vs-free", "", "‘completely under control’ — gold = changed/Infrequent + free; model = free. IAA coin-flip."),
    "EA0038": ("GOLD_RIGHT", "missed-current-event", "", "recent GTC at home = gold active-rate; model tagged the 3-yr-prior free period + a change, missed the current event."),
    "EA0046": ("BOTH_DEFENSIBLE", "last-event-convention", "", "‘FBTC, last event Oct 2019’ — gold = seizure-free (last-event), model = active-rate."),
    "EA0056": ("MODEL_DEFENSIBLE", "gold-multiplicity", "", "gold tags the stopped 2ary-gen type seizure-free per-type; model emitted the two active rates."),
    "EA0059": ("BOTH_DEFENSIBLE", "well-controlled=infrequent", "regression", "‘seizures well controlled’ — gold changed/Infrequent; stage-1 had it, verify dropped it (now free-only)."),
    "EA0068": ("MODEL_DEFENSIBLE", "gold-header-adjective", "", "gold tags the dx-header word ‘Infrequent focal seizures’ as a changed state; model reasonably did not."),
    "EA0082": ("MODEL_DEFENSIBLE", "gold-multiplicity", "", "gold double-tags absences active-rate(2-3/day) AND changed/Frequent; model has the rate."),
    "EA0102": ("GOLD_RIGHT", "verify-dropped-correct", "regression", "gold seizure-free (5yr); stage-1 had it, verify DROPPED it (PNES non-epileptic suppression) → empty."),
    "EA0106": ("MODEL_DEFENSIBLE", "gold-multiplicity", "", "gold per-type: active-rate + changed/Frequent + FBTC seizure-free; model emitted the active rate only."),
    "EA0108": ("MODEL_DEFENSIBLE", "gold-multiplicity", "", "gold double-tags seizures active-rate(2-3/mo) AND changed/Increased; model has the rate (increase is real but redundant)."),
    "EA0120": ("GOLD_RIGHT", "verify-dropped-correct", "regression", "gold seizure-free (‘no further seizures since last appt’); stage-1 had it, verify DROPPED it → empty."),
    "EA0121": ("BOTH_DEFENSIBLE", "gold-odd-key", "", "gold tags ‘frequent seizures’ changed/Frequent + FBTC seizure-free(Lo/Hi 0-3); model emitted the frequent + the 2-3/mo rate."),
    "EA0123": ("BOTH_DEFENSIBLE", "decrease-real-free-historical", "", "gold = active-rate + changed/Decreased(‘reduced from once a year’); model = rate + a HISTORICAL ‘4 years without’ free."),
    "EA0136": ("GOLD_RIGHT", "syncope-as-active", "", "model tagged the low-BP/syncope ‘few times a year’ events as active-rate; missed gold changed/Same (‘remain well controlled’)."),
    "EA0139": ("BOTH_DEFENSIBLE", "recurrence-rate-vs-changed", "", "‘further GTC since I last saw him, an episode in September’ — no number, no direction word; gold keys active-rate, model keys changed (same fact)."),
    "EA0182": ("BOTH_DEFENSIBLE", "last-event-convention", "", "only probable TLE (c3/c4); ‘a single seizure some 3 weeks ago’ — gold = seizure-free (last-event convention), model = active-rate (lone event as a rate)."),
    "EA0137": ("MODEL_DEFENSIBLE", "gold-multiplicity", "", "gold per-type seizure-free + 2ary-gen active-rate(2/yr); model emitted the active rate, missed the per-type free."),
    "EA0186": ("BOTH_DEFENSIBLE", "stopped-free-vs-changed", "", "focal-motor ‘frequent before medication, last event 10 months ago’ — gold = seizure-free, model = changed (same reality)."),
    "EA0198": ("MODEL_DEFENSIBLE", "gold-multiplicity", "", "gold double-tags active-rate AND changed/Increased(‘this increase in seizures frequency’); model has the rate."),
    # ---- precision over-emission (model added a spurious state), gold non-empty ----
    "EA0006": ("BOTH_DEFENSIBLE", "historical=active-convention", "", "‘remains seizure free’ now vs ‘2 GTC in 2014’ — gold tags the historical dated count active-rate; model tags current seizure-free."),
    "EA0010": ("GOLD_RIGHT", "stable-as-changed", "", "no seizures since teens, ‘stable from epilepsy point of view’ = gold seizure-free; model over-read ‘stable’ as changed."),
    "EA0087": ("GOLD_RIGHT", "inter-event-gap-as-free", "", "patient having MORE GTCs (4 in 3 weeks); model over-read ‘up to five weeks seizure free’ between events as a free state."),
    "EA0096": ("GOLD_RIGHT", "clinic-exam-as-free", "", "model tagged ‘I saw no overt seizures’ (today’s exam) as seizure-free; the child’s control had deteriorated."),
    "EA0135": ("GOLD_RIGHT", "superseded-free-period", "", "‘6 months without seizures’ then a cluster; model tagged the now-superseded free period seizure-free."),
    "EA0143": ("GOLD_RIGHT", "historical-rate-as-current", "", "‘used to happen weekly’ but ‘last event >5 years ago’; model tagged the historical weekly rate active-rate."),
    "EA0151": ("BOTH_DEFENSIBLE", "cluster-as-deterioration", "", "‘cluster of 5… unusual as before well controlled’ — model’s ‘changed’ is a defensible deterioration; gold tags only the rate."),
    "EA0158": ("GOLD_RIGHT", "changed-on-stable-rate", "", "two stable rates ‘continued ever since’; model over-called changed with no explicit direction in text."),
    "EA0162": ("BOTH_DEFENSIBLE", "provoked-cluster-discounted", "", "alcohol-provoked ‘cluster of three’ in Dec; gold discounts as seizure-free, model tags active-rate."),
    "EA0197": ("MODEL_DEFENSIBLE", "gold-under-annotation", "", "‘baseline 1-2/yr… got a bit worse, now 1-2/month’ — explicit worsening; gold tagged only active-rate, model added the real change."),
}


def main() -> None:
    idx = {r["letter_id"]: r for r in json.loads((ROOT / "_sf_canonical/_index.json").read_text(encoding="utf-8"))}
    wrong = sorted(lid for lid, r in idx.items() if not r["s2_exact"])
    missing = [lid for lid in wrong if lid not in VERDICTS]
    extra = [lid for lid in VERDICTS if lid not in wrong]
    assert not missing, f"un-adjudicated wrong letters: {missing}"
    assert not extra, f"verdicts for non-wrong letters: {extra}"

    rows = []
    for lid in wrong:
        v, mech, vf, reason = VERDICTS[lid]
        r = idx[lid]
        rows.append({
            "letter": lid, "verdict": v, "mechanism": mech, "verify": vf,
            "gold": "|".join(r["gold_states"]) or "(none)",
            "s1": "|".join(r["s1_states"]) or "(none)",
            "s2": "|".join(r["s2_states"]) or "(none)",
            "missed": "|".join(r["s2_missed"]), "spurious": "|".join(r["s2_spurious"]),
            "train": "T" if r["in_trainset"] else "v", "reason": reason,
        })

    out = ROOT / "_sf_canonical/_adjudication.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    vc = Counter(r["verdict"] for r in rows)
    gold_empty = [r for r in rows if r["gold"] == "(none)"]
    regressions = [r["letter"] for r in rows if r["verify"] == "regression"]
    n = len(idx)
    n_wrong = len(rows)
    n_exact = n - n_wrong
    defensible = vc["MODEL_DEFENSIBLE"] + vc["BOTH_DEFENSIBLE"]
    print(f"stage-2 wrong letters adjudicated: {n_wrong}/{n}\n")
    print("VERDICT TALLY (of the 53 metric-errors):")
    for k in ("GOLD_RIGHT", "BOTH_DEFENSIBLE", "MODEL_DEFENSIBLE"):
        print(f"  {k:18s} {vc[k]:2d}  ({vc[k]/n_wrong:.0%})")
    print(f"\n  -> genuine model error (GOLD_RIGHT)        : {vc['GOLD_RIGHT']}/{n_wrong} ({vc['GOLD_RIGHT']/n_wrong:.0%})")
    print(f"  -> NOT a model mistake (MODEL+BOTH)         : {defensible}/{n_wrong} ({defensible/n_wrong:.0%})")
    print(f"\ngold=[] over-emission letters: {len(gold_empty)}; of these:")
    ge = Counter(r["verdict"] for r in gold_empty)
    for k in ("GOLD_RIGHT", "BOTH_DEFENSIBLE", "MODEL_DEFENSIBLE"):
        print(f"    {k:18s} {ge[k]}")
    print(f"\nverify regressions (verify dropped a correct stage-1 fact): {regressions}")
    print(f"\nMETRIC per-letter accuracy (stage-2)         : {n_exact}/{n} = {n_exact/n:.1%}")
    print(f"CLINICALLY-DEFENSIBLE per-letter accuracy     : {(n_exact+defensible)}/{n} = {(n_exact+defensible)/n:.1%}")
    print(f"  (= metric-correct {n_exact} + model-right-but-scored-wrong {defensible})")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
