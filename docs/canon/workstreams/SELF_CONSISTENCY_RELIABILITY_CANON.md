# ExECT Self-Consistency & Entropy Reliability Canon

Last updated: 2026-07-01

**Scope:** GPT-4.1-mini 2-call lean-candidate self-consistency panels (June 2026).  
**Claim boundary:** Aggregate-only readouts; not per-letter entropy routing for deployment.

**Parent canon:** [`09_cross_task_reliability.md`](../09_cross_task_reliability.md)  
**Long tail:** 13 files under [`docs/experiments/exectv2/reliability/`](../../experiments/exectv2/reliability/) (stubbed)

---

## What this workstream tested

Under the accepted simplification candidate (`exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`),
how stable are per-family clinical-headline cells across repeated live calls?

Two panel designs:

| Panel | Temperatures | Purpose |
| --- | --- | --- |
| **entropy_dev140_temps** | 0.3, 0.5, 0.7, 1.0 × 4 repeats | Semantic stability (Gan P2.1 analogue) |
| **hard50_temp0** | 0.0 × 4 repeats | Temp-0 reproducibility on hard subset |
| smoke1_temp0 | 0.0 × 2 repeats | Pipeline smoke (1 row — not evidentiary) |

---

## Primary readout — entropy_dev140_temps

Source: [`exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_20260625.md`](../../experiments/exectv2/reliability/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_20260625.md)

| Metric | Value |
| --- | ---: |
| Rows / family cells | 140 / 560 |
| Exact family-cell agreement | **0.8857** |
| Mean pairwise Jaccard | 0.9284 |
| Mean semantic entropy | **0.1905** |
| Non-zero entropy cells | 107 |

### Per-family stability

| Family | Exact agreement | Mean entropy |
| --- | ---: | ---: |
| Diagnosis | 0.8155 | 0.3069 |
| SeizureFrequency | 0.8333 | 0.2792 |
| Prescription | 1.0000 | 0.0000 |
| Investigations | 0.8940 | 0.1757 |

Prescription is fully stable across repeats; Dx/SF carry most entropy.

---

## Majority agreement vs correctness

| Majority bucket | Cells | Majority exact-correct | Accuracy |
| --- | ---: | ---: | ---: |
| **4/4 unanimous** | 453 | 359 | **0.7925** |
| 3/4 | 68 | 24 | 0.3529 |
| 2/4 | 36 | 16 | 0.4444 |
| 1/4 | 3 | 1 | 0.3333 |

**Key insight:** High agreement ≠ correctness. Unanimous-but-wrong cells mirror
Gan's confident over-read residual — agreement measures **decision stability**, not
clinical accuracy.

---

## hard50_temp0 panel (reproducibility)

| Metric | Value |
| --- | ---: |
| Rows | 50 |
| Exact agreement | 0.9217 |
| Mean entropy | 0.1261 |

Higher agreement at temp-0 — measures call-to-call reproducibility, not semantic
breadth under sampling.

---

## Producer raw-output variation

Across entropy panel repeats:

| Producer | Mean unique raw outputs / row |
| --- | ---: |
| structured_key_family_event_ledger | 3.95 |
| diagnosis_decomposer | 3.75 |

Raw outputs vary; stable headline cells reflect **downstream assembly decisions**,
not cache reuse.

---

## Run health

All four entropy panel assembly JSONL rows: 140 rows, 0 call failures, 0 parse
failures, evidence validity **1.0000**.

---

## Paper / closeout usage

Recorded on reliability scorecard (2026-06-21) as **0.8857 aggregate agreement**
— report with majority-correctness caveat ([`07_exect_plan11.md`](../07_exect_plan11.md)
§ Reliability annex). Not promoted as deployment routing signal (calibration/review
routing remain weak pillars per [`10_paper_provenance.md`](../10_paper_provenance.md)).

---

## Shard files (assembly repeats)

Individual repeat assembly markdown files (`*_r1_temp0p3_*`, `*_hard50_*`, etc.)
are stubbed navigation tails — metrics live in parent panel readouts above.

---

## Related

- [`09_cross_task_reliability.md`](../09_cross_task_reliability.md)  
- [`06_gan_clinical_policy.md`](../06_gan_clinical_policy.md) § P2.1 entropy  
- [`07_exect_plan11.md`](../07_exect_plan11.md) § Simplification frontier  
