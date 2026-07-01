# Paper Canon — Claims, Evidence & Provenance

Last updated: 2026-07-01

**Working manuscript:** [`../research/paper_manuscript_2026-06-26.md`](../research/paper_manuscript_2026-06-26.md)  
**IEEE LaTeX:** [`literature/IEEE/IEEE-conference-template-062824/`](../../literature/IEEE/IEEE-conference-template-062824/) (lags markdown as of 2026-06-30)  
**Gap analysis source:** [`../research/paper_claims_evidence_review_2026-07-01.md`](../research/paper_claims_evidence_review_2026-07-01.md)  
**Open work:** [`docs/plans/ACTIVE_ROADMAP.md`](../plans/ACTIVE_ROADMAP.md) P0

This document is the **claims register** — what the paper may assert, what evidence
backs each claim, and what remains blocked. It absorbs the claims-review analysis and
routes to frozen artifacts via the provenance index below.

---

## Pivot framing (read first)

Original [`reliability_thesis.md`](../design/reliability_thesis.md) §7 success criteria
(beat published 0.87/0.90 benchmark with three architecture families) are **not met**.
The manuscript pivots to **capability-first claims (C1–C5)** rather than benchmark
dominance. That pivot is defensible if C1 (gold-quality reconciliation) and the
evaluation-discipline story (C5) are written with correct boundaries.

Two **ceiling mechanisms** on disjoint slices must not be conflated:

| Mechanism | Task / slice | Meaning |
| --- | --- | --- |
| **The Wall** | Gan SF binding residual | Confident unknown↔rate over-reading; no forward-observable abstention signal |
| **Gold-quality ceiling** | ExECT SF/Dx benchmark surface | Metric disagreements mostly annotation multiplicity, not model error |

See [`04_scoring.md`](04_scoring.md) and
[`06_gan_clinical_policy.md`](06_gan_clinical_policy.md).

---

## Capability claims register (C1–C5)

| ID | Claim (short) | Strength | Primary evidence | Claim boundary |
| --- | --- | --- | --- | --- |
| **C1** | Benchmark gap is substantially gold noise on SF/Dx, not model deficit | Soft, load-bearing | SF row analysis 2026-06-29; Dx row analysis 2026-06-30; benchmark reconciliation drafts | Dev140 adjudication by same pipeline — circularity caveat required in Methods |
| **C2** | Shared format layers + inert evidence gate; cross-task component dividend | Strong | `cross_task_shared_component_ablation_2026-06-27.md`; component-off full200 | Aggregate full-200; gate Δ=0 both tasks |
| **C3** | Wall mechanism transfers to ExECT SF (bounded) | Strong but bounded | `exectv2_sf_wall_transfer_probe_2026-06-27.md`; wall transfer draft | Small-n binding slice; suggestive not definitive |
| **C4** | Model-agnostic architecture (DeepSeek ≥ GPT on frozen core) | Strong, asymmetric | `exectv2_same_core_model_swap_full200_20260625.json` | Qwen 0.8197 diagnostic — explain in text, not headline range |
| **C5** | Evaluation discipline (panels, CV, frozen aggregate audits) | Strong | Gan v0.7 regression catch; Gate 4 protocols; predeclarations | Demonstrated instances, not hypothetical |

### C1 detail — gold-quality ceiling

| Family | Metric F1 / rate | Adjusted / clinically defensible | Genuine model error share |
| --- | --- | --- | --- |
| SeizureFrequency | 62.1% metric-defensible (dev140) | 89.3% clinically defensible | 15/53 metric-errors genuine |
| Diagnosis | 0.6617 F1 | 0.9501 adjusted | 14.8% genuine; 85.2% gold multiplicity |

**Sources:** `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`; `docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md`.

**Reviewer risk:** Same team adjudicates gold quality of system output. Strengthen with blinded re-adjudication / IRR if possible before submission.

### C2 detail — cross-task ablation (propagate to manuscript)

`docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`:

- `evidence_validation` gate: **Δ=0.0000** ExECTv2 dev140 and Gan validation750 (structurally inert).
- `standard_dictionary` / Gan normalize: **+0.0389** ExECTv2, **+0.0293** Gan.

**Manuscript action:** Remove stale D.5 "not yet executed at cross-task scope" — it is done.

### C4 detail — full-200 same-core (`clinical_headline`)

| Model | Overall | SF | Notes |
| --- | ---: | ---: | --- |
| GPT-4.1-mini | 0.8356 | 0.7525 | Development model |
| DeepSeek | 0.8566 | 0.7602 | Leads overall; 1 accepted Dx caveat |
| Qwen repair v02 | 0.8197 | 0.7020 | Diagnostic; not promotion candidate |

**Do not claim:** Qwen leads; uniform model-agnostic victory without per-family table.

### C3 detail — wall transfer (6/9 checks)

External Risk AUROC 0.764 on ExECT SF probe; binding-slice abstention AUROC 0.676 (below 0.70 bar). Pre-registered probe — report mixed verdict honestly.

---

## Three-way architecture comparison (thesis §7 gap — now measured)

ExECTv2 **LLM-only** (GEPA single-pass) plateaus ~**0.731** (mini) / ~**0.654** (Qwen) vs hybrid v08 **0.9155** on dev140 `clinical_headline`. This **is** the missing three-way leg — a **negative** result.

**Per-family GEPA attribution (corrected 2026-06-30):**

| Family | "Evidence-recall gap" character |
| --- | --- |
| Diagnosis | 93.5% H-inflated (gold multiplicity) |
| SeizureFrequency | 61–83% H-inflated; state_profile rescoring lifts same preds |
| Prescription | 52.2% typo/substring mechanism — partly genuine |
| Investigations | Clean genuine-retrieval negative (~26–30% H-inflated) |

Full write-up: [`08_gepa.md`](08_gepa.md). **Do not** import blanket "producer evidence-recall" without per-family table.

---

## Reliability pillar — honest negatives

| Signal | Result | Paper language |
| --- | --- | --- |
| Calibration | Brier Δ 0.0142 vs base rate | Not deployment-ready |
| Review routing | ~97% burden, ~90% catch | Review-nearly-everything, not low-burden triage |
| Binding unknown slice AUROC | 0.676 | Below 0.70 usefulness bar; H0 retained |

Cross-model agreement exists in artifacts but is **unused** for ExECT triage except SF wall probe — see calibration plan for optional strengthening (framing-only in P0 closure plan).

---

## Do not use as claims

Preserve manuscript "Do Not Use" list; canon adds:

- Row-level test450 / full-200 inspection beyond predeclared aggregate audits
- Consensus/fresh selector promotion (CUT)
- LLM-only dedup as production control (~0.73 vs ~0.92 hybrid)
- Unqualified "beat 0.87/0.90 benchmark"
- Blanket GEPA root-cause without per-family inflation table
- Qwen in abstract headline range without explanation

---

## Provenance index (manuscript sections → artifacts)

| Manuscript topic | Canon / evaluation doc | Frozen artifact (examples) |
| --- | --- | --- |
| ExECT headline scores | [`04_scoring.md`](04_scoring.md) | v08 full200 gpt41mini JSON |
| Architecture comparison | [`CLOSEOUT_EVIDENCE_CANON.md`](07_exect_plan11.md) | `final_architecture_selection_2026-06-22.md` |
| Gan SF / Wall | [`06_gan_clinical_policy.md`](06_gan_clinical_policy.md) | reliability master scorecard |
| Component impact | evaluation canon §Component layers | `exectv2_component_off_replay_full200_20260626.json` |
| GEPA negative | [`08_gepa.md`](08_gepa.md) | GEPA dev140 scorecards |
| Claim boundaries | [`final_artifact_index_2026-06-22.md`](../experiments/final_artifact_index_2026-06-22.md) | SHA-256 table |

**Authority stack:** frozen artifact index > this canon > ADR > research synthesis > registry row.

---

## Open gaps (P0 manuscript work)

From [`manuscript_evidence_gaps_closure_plan_2026-07-01.md`](../plans/manuscript_evidence_gaps_closure_plan_2026-07-01.md):

1. Write GEPA three-way negative into §2.3 / Results (with per-family attribution).
2. Propagate cross-task ablation (remove stale S1 limitation).
3. Extend C1 to Dx in abstract/§1 (SF + Dx gold-quality).
4. Explain Qwen asymmetry in model-agnostic section.
5. Tighten calibration/abstention framing (no new runs unless calibration plan authorizes).

**LaTeX sync:** Re-sync IEEE draft with 2026-06-29/30 markdown revisions before camera-ready.

---

## Related reading

- [`../research/contribution_thesis.md`](../research/contribution_thesis.md) — experimental ontology (three families)
- [`../research/closing_stage_research_critique_2026-06-27.md`](../research/closing_stage_research_critique_2026-06-27.md) — cross-strand gaps
- [`../research/supervisor_brief_conformance_audit_2026-07-01.md`](../research/supervisor_brief_conformance_audit_2026-07-01.md) — brief alignment
- [`docs/THREAD_MAP.md`](../THREAD_MAP.md) T4 — paper reading path
