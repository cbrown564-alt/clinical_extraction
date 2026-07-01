# ExECTv2 GEPA Canon — Closed Negative Program

Last updated: 2026-07-01

**Status: CLOSED** (SF representation reopened 2026-06-28; Dx answered 2026-06-30).  
No active GEPA optimization — see [`ACTIVE_ROADMAP.md`](../plans/ACTIVE_ROADMAP.md).

**Absorbs:**  
[`../research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`](../research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md),  
[`exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md`](exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md),  
[`exectv2_gepa_underperformance_investigation_2026-06-27.md`](exectv2_gepa_underperformance_investigation_2026-06-27.md),  
[`exectv2_sf_representation_not_recall_2026-06-28.md`](exectv2_sf_representation_not_recall_2026-06-28.md),  
[`exectv2_gepa_qwen_cross_model_2026-06-30.md`](exectv2_gepa_qwen_cross_model_2026-06-30.md),  
[`exectv2_gepa_verify_stage_credit_assignment_2026-07-01.md`](exectv2_gepa_verify_stage_credit_assignment_2026-07-01.md).

**Paper:** [`10_paper_provenance.md`](10_paper_provenance.md) § Three-way comparison  
**Hybrid baseline:** v08 dev140 **0.9155** `clinical_headline`

---

## Verdict

Single-pass LLM-only ExECTv2 (GEPA-optimized prompts) plateaus at **~0.731** (gpt-4.1-mini)
and **~0.654** (Qwen 3.6 35B) on dev140 `clinical_headline` — **~0.18–0.19 below**
the v08 multi-lane hybrid. This **completes the thesis §7 three-way comparison** as a
**negative result**: LLM-only does not reach hybrid; rules/hybrid architecture families
matter via **focused per-family producers**, not verify-stage magic.

---

## Plateau table (six configurations, ~0.73 ceiling)

| Configuration | dev140 headline F1 |
| --- | ---: |
| Monolith single instruction | 0.702–0.719 |
| **Per-family (4 instructions)** | **0.731** (best single-pass) |
| Multi-stage generate→verify | 0.7235 (failed kill +0.03) |
| Uniform recall-weight F-β=2 | 0.7213 |
| Per-family recall-weight | 0.7213 |
| CUI/UMLS re-score | 0.709 |

Headline **invariant** ~0.73 — precision/recall trade only shuffles between families.

---

## What was ruled out

| Lever | Result |
| --- | --- |
| Multi-stage verify | 0.7235; verify filtered recall; credit assignment mis-fed verifiers |
| Surface-convention tolerant re-score | +0.02 only (0.751) |
| Recall-weight objectives | No aggregate lift |
| Qwen cross-model | Underperforms mini; does not beat hand-tuned Qwen baseline |

**Verify-stage local credit assignment (2026-07-01):** multistage GEPA 0.7235→**0.7596**
(+0.036) — qualitative win, **missed kill criterion by 0.0014**; not a promotion path.

---

## Hybrid vs GEPA decomposition (corrected attribution)

Early framing: “producer evidence-recall gap, not verify/arbitrate.”  
**2026-06-30 EV-recall consolidation re-examination** revised per-family:

| Family | Gap character | Genuine retrieval? |
| --- | --- | --- |
| **Diagnosis** | 93.5% H-inflated | Mostly gold multiplicity (Dx row analysis: 85.2% artifact) |
| **SeizureFrequency** | 61–83% H-inflated | Representation/state_profile rescoring + gold multiplicity |
| **Prescription** | 52.2% typo/substring | Partly genuine (transcription breaks) |
| **Investigations** | 26–30% H-inflated | **Clean genuine-retrieval negative** |

**Hybrid wins via:** curated per-family LLM producers (+evidence recall 69%→87% on
decomposition artifact), deterministic recovery **+0.017 Dx-only** — not ensemble depth.

**Do not cite** blanket “0.18 genuine recall gap” without this table ([`10_paper_provenance.md`](10_paper_provenance.md)).

---

## SF: representation not recall

Same GEPA predictions under **`state_profile`** vs strict `clinical_headline`:
SF **0.592→0.713** without changing model output — granularity lottery + gold
per-type multiplicity. See SF representation doc and canonical row analysis.

---

## Qwen cross-model (2026-06-30)

Qwen 3.6 35B on identical GEPA architecture **underperforms** gpt-4.1-mini and does
not clear its own hand-tuned baseline. Operational policy: Qwen remains **diagnostic**
on same-core full-200 (0.8197 with repair v02).

---

## Manuscript actions (P0)

1. Replace §2.3 “acknowledged gap — three-way not run” with **closed negative** narrative.  
2. Include plateau table + per-family attribution table (above).  
3. Cross-link hybrid v08 as positive control in same subsection.  
4. Optional footnote: verify-stage credit assignment 0.7596 (narrow miss) — not headline.

---

## Plans (historical)

All `docs/plans/exectv2_gepa_*` marked HISTORICAL. Multistage scope **superseded**
by focused-lanes plan (executed).

---

## Related reading

- [`04_scoring.md`](04_scoring.md) — SF surface trap  
- [`CLOSEOUT_EVIDENCE_CANON.md`](07_exect_plan11.md) — v08 control  
- [`docs/THREAD_MAP.md`](../THREAD_MAP.md) T3
