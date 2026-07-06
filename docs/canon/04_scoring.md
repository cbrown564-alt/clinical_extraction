# ExECTv2 Evaluation Canon — Gold, Surfaces & Scoring

Last updated: 2026-07-06

**Absorbs (detail in source stubs):**  
[`../research/exectv2_gold_representation_and_scoring_principles_2026-06-17.md`](../research/exectv2_gold_representation_and_scoring_principles_2026-06-17.md),  
[`../research/exectv2_benchmark_surface_overall_2026-06-18.md`](../research/exectv2_benchmark_surface_overall_2026-06-18.md),  
[`../research/exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md`](../research/exectv2_all_entities_scoring_mechanics_deep_dive_2026-06-12.md),  
gold-quality revisions in [`../research/paper_drafts/`](../research/paper_drafts/),  
[`../research/exectv2_cost_quality_matched_split_table_2026-07-01.md`](../research/exectv2_cost_quality_matched_split_table_2026-07-01.md).

**Paper claims:** [`10_paper_provenance.md`](10_paper_provenance.md) C1, C2, C4.  
**Architecture context:** [`../research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md`](../research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md).

> **Plain-language primer**
>
> **`clinical_headline`** — the project's primary scoreboard: did we recover the right
> clinical facts across Diagnosis, SeizureFrequency, Prescription, and Investigations,
> after de-duplication?
>
> **Benchmark surface** — a stricter, paper-comparable layer (exact normalized phrase +
> attributes + UMLS CUI). Useful for like-for-like comparison to Fonferko-Shadrach; often
> *lower* than clinical recovery when hybrids change output format without changing clinical
> meaning.
>
> **`state_profile`** (`frequency_state_faithful`) — SeizureFrequency-only scoring that
> matches consolidated clinical burden (one rate/state per letter), not per-type CUI
> multiplicity. **Primary metric for SF-family experiments** (ADR 0037).
>
> **Why multiple F1 numbers?** Target representation, scorer design, and extractor output
> unit are fused unless you report the layer ladder (`phrase_only` → `semantic` →
> `benchmark`). Never quote benchmark F1 alone as “extractor quality.”

---

## Bottom line

A single ExECTv2 F1 number **fuses three layers** — target representation, scorer
design, and extractor output unit. The project’s headline surface is **clinical
recovery** (`clinical_headline` composite and per-entity headlines); the **benchmark
surface** (exact phrase + all attributes + CUI) is a **diagnostic/comparability**
layer, not the primary scoreboard.

Like-for-like benchmark overall on dev140: **0.3877 item / 0.6972 letter** vs paper
headline **0.87 / 0.90** — gap is mostly format fidelity, not concept absence.
Hybrid clinical-recovery gains can **lower** benchmark overall (SF: 0.692 rules vs
0.347 hybrid on benchmark cell).

---

## Scoring surface hierarchy

### Layer ladder (all nine entities)

| Layer | Question it answers | Use |
| --- | --- | --- |
| **phrase_only** | Did we find a phrase at the chosen gold altitude? | Target/recall diagnostic |
| **semantic** | Correct concept + attributes minus CUI? | Architecture-comparable on dev |
| **benchmark** | Exact normalized phrase + attributes + CUI? | Like-for-like vs Fonferko-Shadrach headline |

Always report the ladder; never quote benchmark F1 alone as “extractor quality.”

### Headline surfaces (Plan 11 / v08)

| Surface | Scope | When to use |
| --- | --- | --- |
| **`clinical_headline`** | Cross-entity composite; de-duplicated clinical recovery | Primary project scoreboard (ADR 0027) |
| **Per-entity headline** | e.g. concept-identity (Dx), regimen (Rx) | Family-specific readouts |
| **`state_profile`** (`frequency_state_faithful`) | SeizureFrequency only | **Primary for SF-family experiments** (ADR 0037) |
| **benchmark / CUI companions** | Strict mention multiset | Diagnostic; antagonistic to hybrid on some families |

**SF trap:** Comparing GEPA `state_profile` to v08 `clinical_headline` without mapping
is invalid. Same predictions rescored under `state_profile` can lift SF ~0.592→0.713
(representation, not recall).

### Component / attribution layers (ExECTv2)

From `definitions.yaml` and component-off replay:

1. **Producer / raw lane** — LLM candidate emission  
2. **Integrity guards** — `evidence_valid` (often **inert**, Δ=0 on current stacks)  
3. **Dictionary / residual semantic lenses** — prediction-bearing when identity changes  
4. **Headline projection** — format-only when clinical fact unchanged  

**Cross-task:** Evidence gate inert on both ExECT dev140 and Gan validation750
(`cross_task_shared_component_ablation_2026-06-27.md`).

---

## Gold principles (P1–P7 summary)

| # | Principle | Implication for evaluation |
| --- | --- | --- |
| **P1** | Gold has raw span (`text`) vs clean concept (`CUIPhrase`) at different altitudes | Per-entity target choice swings F1 by tens of points |
| **P2** | CSV column layout varies by entity file | Reason in field names, not column indices |
| **P3** | Offsets corrupt for matching, valid for instance distinctness | De-duplication uses span keys, not gold alignment |
| **P4** | Benchmark F1 fuses target + scorer + extractor | Attribute gaps vs CUI gaps vs recall gaps need layer split |
| **P5** | Recall ceiling lifts only when extraction unit matches annotation unit | SF state vs per-type CUI multiplicity |
| **P6** | Per-entity heterogeneity is the rule | No universal scorer story |
| **P7** | Obvious fixes often net-negative per entity | Measure before shipping |

Full derivations and counts: source gold-principles doc (stubbed).  
Append-only evidence log: [`../research/exectv2_data_discoveries_log.md`](../research/exectv2_data_discoveries_log.md) — **do not merge away**.

---

## Gold-quality ceiling (C1 mechanism)

Row adjudication on dev140 disagreements:

| Family | Mechanism | Adjusted headline |
| --- | --- | --- |
| **SF** | Metric counts per-type CUI multiplicity; model consolidates clinically | 89.3% clinically defensible vs 62.1% metric |
| **Dx** | Gold lists multiple equivalent diagnoses; model merges | F1 0.6617 → 0.9501 adjusted |

**Methods caveat:** Adjudication uses project pipeline; label as internally adjudicated.

Case files: `docs/research/error_analysis/sf_ev_recall/` (EV recall); Dx uses canonical row analysis only (no separate case bucket).

---

## Key dev140 numbers (clinical recovery vs benchmark)

### Key-family clinical recovery (2026-06-18 synthesis)

| Family | F1 (clinical) | Status |
| --- | ---: | --- |
| Investigations | 0.872 | Clears target |
| Prescription | 0.817 | Clears target |
| SeizureFrequency | 0.782 | Partial |
| Diagnosis | 0.658 | Ceiling (pre gold-quality revision) |

Post gold-quality revision, Dx adjusted F1 ~0.95 — see PAPER_CANON C1.

### Benchmark surface (like-for-like)

| Architecture | Benchmark item F1 | vs paper 0.87 |
| --- | ---: | ---: |
| Best-of rules+hybrid Inv | 0.3877 | −0.48 |
| All-hybrid four verifiers | 0.3100 | −0.56 |

Hybrid **raises** phrase-only/semantic but **lowers** benchmark on SF cell.

---

## Full-200 frozen aggregates (promotion-safe citations)

From [`CLOSEOUT_EVIDENCE_CANON.md`](07_exect_plan11.md):

| Run | GPT-4.1-mini | DeepSeek | Qwen |
| --- | ---: | ---: | ---: |
| Same-core `clinical_headline` | 0.8356 | 0.8566 | 0.8197 |

Component-off full200: dictionary +0.019–0.029; headline projection +0.030–0.035
(aggregate-only, predeclared).

---

## Claim boundaries (`claim_policy.py`)

| Split tag | Row inspection | Typical use |
| --- | --- | --- |
| **dev140** | Allowed | v08 control, GEPA, ablations |
| **validation750** | Allowed | Gan component ladder |
| **full200 / test450** | **Forbidden** (aggregate only) | Model swap, holdout audits |
| **fixture / smoke** | Panel rules | Agentic hard panel (filter empty-gold letters) |

Replay modes (live / no-call / saved-output) affect causal strength — see RUN_INDEX conventions.

---

## ADR anchors

- **0027** — Clinical recovery headline; projection is artifact layer  
- **0030** — Four exact indicators drive Plan 11 optimization scope  
- **0032** — Clinical finding assembly spine  
- **0037** — SF `state_profile` primary for SF experiments  

---

## Related reading

- [`10_paper_provenance.md`](10_paper_provenance.md) — what to claim in the paper  
- [`08_gepa.md`](08_gepa.md) — LLM-only ceiling  
- [`docs/reference/evidence_groundedness_metric.md`](../reference/evidence_groundedness_metric.md)  
- [`docs/THREAD_MAP.md`](../THREAD_MAP.md) T2
