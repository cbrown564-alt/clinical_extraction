# ExECT Diagnosis Family Ladder Canon

Last updated: 2026-07-01

**Scope:** June 2026 Diagnosis specialist iteration — verifier pilots v01–v05,
reconciler/decomposer branches, phase-2 panels, gold-quality row analysis.  
**Claim boundary:** Dev140 / dev25 development only unless noted frozen.

**Parent canons:** [`04_scoring.md`](../04_scoring.md) · [`05_ceilings_wall.md`](../05_ceilings_wall.md) · [`07_exect_plan11.md`](../07_exect_plan11.md)  
**Long tail:** 15 files in [`docs/experiments/exectv2/diagnosis/`](../../experiments/exectv2/diagnosis/) (stubbed)

---

## What this workstream tested

After the structured v0.5 single-prompt baseline (~0.569 Dx F1 on dev25), the Diagnosis
thread asked whether **multi-prompt verify/reconcile/decompose** lanes could reach the
0.8 family target without contaminating evidence gates.

Substrate: `exectv2_llm_only_key_entities_structured_v0.5` + `openai/gpt-4.1-mini`.

---

## Verifier pilot ladder (dev25 unless noted)

| Version | Dx clinical F1 | P | R | Gate | Decision |
| --- | ---: | ---: | ---: | --- | --- |
| v0.5 single structured | 0.569 | 0.554 | 0.585 | EV 0.9684 | Baseline |
| Verifier **v0.1** | 0.592 | 0.644 | 0.547 | EV 1.0000 | Useful; revise |
| Verifier **v0.2** | 0.619 | 0.682 | 0.566 | EV 1.0000 | Revise |
| Verifier **v0.3** | 0.701 | 0.773 | 0.641 | EV 1.0000 | Best so far; revise |
| Verifier **v0.4** | 0.768 | 0.826 | 0.717 | EV 1.0000 | Close to 0.8 target |
| Verifier **v0.5** | **0.837** | 0.911 | 0.774 | EV 1.0000 | **First to clear 0.8** on dev25 |

v0.5 improved precision sharply (0.826→0.911) while lifting recall (0.717→0.774).
Source-near overlap 0.840 F1. dev140 headline for v0.5 pilot context still ~0.633 —
transfer gap remained before holistic assembly absorbed Dx lanes.

---

## Reconciler / decomposer branches (dev140)

| Run | F1 | Outcome |
| --- | ---: | --- |
| Verifier v0.6 dev140 | 0.651 | Input to reconciler |
| Reconciler v0.1 dev140 | 0.658 | Kept flat vs verifier |
| Reconciler v0.2 dev140 | 0.647 | **Rejected** — precision fell, no recall gain |
| Decomposer v0.1 | (see report) | Candidate enumeration branch |

Reconciler v0.2 grouped concept families explicitly — helped dev25 pilot (0.844) but
**did not transfer** to dev140.

---

## Holistic assembly absorption

Diagnosis lenses in the v01→v08 ladder drove most Dx gains post-verifier era:

| Holistic version | Dx F1 | Primary delta |
| --- | ---: | --- |
| v01 | 0.7572 | Baseline holistic |
| v05 | 0.9083 | Dx phase4 stack |
| v08 (frozen) | 0.9083 | Production control |

See [`HOLISTIC_ASSEMBLY_LADDER_CANON.md`](HOLISTIC_ASSEMBLY_LADDER_CANON.md) and frozen
v08 report (not stubbed).

---

## Gold-quality ceiling (canonical row analysis — 2026-06-30)

Official `clinical_headline` scorer on dev140 (GEPA multifamily run substrate):

| Verdict | n | share |
| --- | ---: | ---: |
| GOLD_RIGHT (genuine model error) | 31 | 14.8% |
| MODEL_DEFENSIBLE (gold artifact) | 167 | 79.9% |
| BOTH_DEFENSIBLE (ambiguity) | 11 | 5.3% |

**Clinically-adjusted F1: 0.9501** vs metric **0.6617**.

**Manuscript (C1):** Diagnosis "consolidation gap" is substantially gold multiplicity,
mirroring SF mechanism B — not a pure architectural recall deficit.

Source: [`exectv2_dx_canonical_row_analysis_2026-06-30.md`](../../experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md).

---

## Phase-2 panel docs (2026-06-21)

Residual panel predeclaration + live/prompt-only dev32 runs — exploratory residual
characterization after verifier era; not promotion candidates.

---

## Reading order

1. This canon (ladder + gold-quality)  
2. Verifier v0.5 pilot report (best dev25 verifier)  
3. Dx canonical row analysis (C1 evidence)  
4. Holistic ladder canon → v08 frozen report  

---

## Related

- [`DIAGNOSIS_FAMILY_LADDER_CANON.md`](DIAGNOSIS_FAMILY_LADDER_CANON.md) (this doc)  
- [`../08_gepa.md`](../08_gepa.md) — Dx 93.5% H-inflated on GEPA decomposition  
- [`../10_paper_provenance.md`](../10_paper_provenance.md) C1  
