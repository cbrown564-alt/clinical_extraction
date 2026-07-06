# 05 — Ceilings & The Wall

Last updated: 2026-07-06

**Structural canon slot:** the two disjoint ceiling mechanisms — do not conflate.

> **Plain-language glossary (both ceilings)**
>
> **The Wall (Gan)** — On some hard seizure-frequency rows the model confidently picks a
> numeric rate when the honest answer is *unknown* (or the reverse). No
> **forward-observable** signal at prediction time separates abstaining from guessing a
> rate; only hidden gold can tell. Caps Purist accuracy around ~84%.
>
> **Gold-quality ceiling (ExECT)** — On dev140, many “errors” are metric/annotation
> disagreements (one consolidated clinical state vs multiple gold CUIs), not extractor
> mistakes. Adjusted adjudication lifts apparent F1 without changing model output.
>
> **Binding residual** — validation rows where no pipeline component is Purist-correct;
> the irreducible Wall slice (11 rows in the closeout).
>
> **Forward-observable** — anything visible at run time (model outputs, confidence,
> cross-model agreement) without peeking at gold labels.
>
> **Withhold-to-unknown vs emit-rate** — two failure modes on binding rows: stay at
> *unknown* vs output a specific frequency band/rate; they look alike to the model.
>
> **`band_unknown`** — Purist category for clinically unquantified burden; Wall over-reads
> often land here when the model emits a rate instead.

---

## Two ceilings (disjoint slices)

| Mechanism | Task / slice | Meaning | Primary canon |
| --- | --- | --- | --- |
| **The Wall** | Gan SF binding residual | Confident unknown↔rate over-reading; no forward-observable abstention signal separates withhold from emit | [`06_gan_clinical_policy.md`](06_gan_clinical_policy.md) § The Wall |
| **Gold-quality ceiling** | ExECT SF/Dx benchmark surface | Metric disagreements mostly annotation multiplicity / representation, not model error | [`04_scoring.md`](04_scoring.md) § Gold-quality |

Narratives converge (both limit apparent F1) but **live on different datasets and
scoring surfaces**. Paper claim C3 (wall transfer) and C1 (gold-quality) must stay
separated ([`10_paper_provenance.md`](10_paper_provenance.md)).

---

## The Wall (Gan)

**Definition:** On binding residual rows, every forward-observable feature fails to
separate withhold-to-unknown from emit-rate; only hidden gold distinguishes them.

| Program | Outcome |
| --- | --- |
| P0.2 risk–coverage | External Risk Score strongest leg; self-confidence degenerate |
| P2.1 semantic entropy | H0 publishable: over-reading is **confident** (entropy flat) |

**Irreducible residual:** 11 validation rows, 8/11 `band_unknown` — no Purist-correct
component without gold.

**Holdout ceiling:** **V12** = multi-trace fresh-evidence hybrid using the full GPT-4.1
reasoner on top of structured-event extraction; **379/450 = 0.842** test450 — best
holdout comparator, not the production default; prior, not a tuning target.

---

## Gold-quality ceiling (ExECT)

In plain terms: **SF** — the metric penalizes one consolidated clinical rate when gold
lists multiple per-type CUIs; most “misses” are representation, not wrong clinical reading.
**Dx** — gold often lists several equivalent diagnoses separately; the model’s merged read
is usually clinically right but scores as wrong until adjudication.

Row adjudication on dev140 disagreements (same pipeline caveat in Methods):

| Family | Metric F1 | Adjusted / clinically defensible | Genuine error share |
| --- | --- | --- | ---: |
| **SF** | 62.1% metric-defensible | 89.3% clinically defensible | 15/53 genuine |
| **Dx** | 0.6617 | 0.9501 adjusted | 14.8% genuine |

**SF representation trap:** GEPA same predictions under `state_profile` lift SF
0.592→0.713 without changing model output — not a recall gain.

Sources: SF canonical row analysis 2026-06-29; Dx canonical row analysis 2026-06-30.
Workstream canons: [`workstreams/SF_ADJUDICATOR_LADDER_CANON.md`](workstreams/SF_ADJUDICATOR_LADDER_CANON.md),
[`workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md`](workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md).

---

## Cross-task transfer (bounded — C3)

Wall-transfer probe on ExECT SF: **6/9 checks pass**; External Risk AUROC 0.764;
binding-slice abstention AUROC **0.676** (below 0.70 usefulness bar).

Source: `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`.

---

## Related reading

- [`docs/design/reliability_thesis.md`](../design/reliability_thesis.md)  
- [`docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md`](../research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md)  
- [`docs/THREAD_MAP.md`](../THREAD_MAP.md) T1 (Wall) and T2 (gold-quality)  
