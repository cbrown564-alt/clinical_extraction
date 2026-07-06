# Plain-Language Glossary

Last updated: 2026-07-06

**How to use this page**

- Lead with the **plain display name** in prose; give the internal codename in
  parentheses **once** when first introducing a term, then drop the codename unless
  you are pointing at a registry artifact or code path.
- **Gan** and **ExECT** terms look similar but often mean different things — check
  the task column before reusing a metaphor (especially *ceiling*, *floor*, *split*).
- For full vocabulary (~80 terms) and code-level types, see [`CONTEXT.md`](../../CONTEXT.md).
- Canon depth: [`docs/canon/05_ceilings_wall.md`](../canon/05_ceilings_wall.md),
  [`docs/canon/04_scoring.md`](../canon/04_scoring.md),
  [`docs/canon/10_paper_provenance.md`](../canon/10_paper_provenance.md).

---

## Metaphorical names

| Term | Plain definition | Recommended display name | Keep codename when… |
| --- | --- | --- | --- |
| **The Wall** | On Gan holdout, confident over-reading on ambiguous letters caps Purist accuracy around 84% because no inference-time signal separates abstain from emit. | **confident over-reading limit** (Gan) | Citing test450 numbers, wall-transfer probes, or `docs/canon/06_gan_clinical_policy.md`. |
| **Gold-quality ceiling** | On ExECT SF/Diagnosis, strict benchmark F1 mostly penalizes annotation shape and multiplicity, not missing clinical concepts. | **annotation-format ceiling** (ExECT) | Row adjudication artifacts, C1 claim text, or `state_profile` vs benchmark comparisons. |
| **Three families** | Every task variant is rules-only, LLM-only, or hybrid (rules + LLM with deterministic glue). | **architecture family** | Ablation tables, component-off replay, promotion gates. |
| **Plan 11** | ExECT production spine: per-family producers → lenses → finding store → headline projection. | **ExECT production pipeline** | ADR 0032, v08 ladder canon, assembly replay run IDs. |
| **Binding residual** | Gan rows where gold is “unknown” but the model emits a specific rate — the slice The Wall describes. | **binding residual** (keep) | Wall / P0.2 / P2.1 reliability writing; small-n by design. |
| **Irreducible residual** | Gan validation rows with no Purist-correct component and no routable forward signal (11 rows; 8/11 `band_unknown`). | **irreducible residual** (keep) | Splitting recoverable vs wall-fixed error on risk–coverage curves. |
| **Recoverable error** | Gan holdout mistakes that external risk signals can rank or shed before the irreducible plateau. | **recoverable error** | Risk–coverage and selective-action narratives only. |
| **External Risk Score** | Predeclared Gan composite (cross-model agreement + ambiguity flags) for ordering risky rows without gold. | **external risk score** | Feature inventory, validation750 router artifacts, wall-transfer AUROC tables. |
| **SF trap** | Rescoring the same SF predictions under `state_profile` lifts F1 without changing model output. | **representation rescoring trap** | Warning against invalid GEPA vs v08 comparisons. |
| **Two-tree rule** | Runnable artifacts live under `experiments/`; human narratives under `docs/experiments/`. | **two-tree documentation rule** | Doc lifecycle, registry hygiene, CI allowlists. |

---

## Version codes

| Code | Plain definition | Recommended display name | Keep codename when… |
| --- | --- | --- | --- |
| **V12** | Best Gan holdout comparator: multi-trace fresh-evidence hybrid reasoner (379/450 Purist); not production. | **best holdout comparator** (V12) | Frozen test450 tables, ceiling-vs-production gap, reasoner trace artifacts. |
| **v0_reference** | Promoted Gan production baseline: single GPT structured-event pass + deterministic render (364/450 Purist). | **production baseline** (`v0_reference`) | Registry run family, cross-model joins, decision 0018 citations. |
| **v08** | Frozen ExECT production control: holistic finding assembly with all four key families >0.900 on dev140. | **frozen production control** (v08) | Component ablation replays, promotion boundaries, ladder canon. |
| **v01–v07** | Superseded ExECT assembly iterations absorbed into the holistic ladder canon. | **prior assembly versions** | Historical ladder diffs only; do not cite as current control. |
| **rules_only** | Gan deterministic floor architecture with no LLM clinical facts (343/450 Purist). | **rules-only baseline** | Floor row in holdout tables; controlled lower bound, not a product path. |

---

## Pipeline components

| Component | Plain definition | Recommended display name | Keep codename when… |
| --- | --- | --- | --- |
| **Structured-event pass** | Gan LLM stage that emits clinical events before deterministic render and Purist scoring. | **structured-event extraction** | Gan spine diagrams, v0_reference lineage. |
| **Producer** | ExECT per-family LLM lane that emits JSONL candidate findings from the letter. | **family producer** | Plan 11 spine, component-off attribution. |
| **Family lens** | Deterministic transform (Dx / SF / Rx / Inv) that shapes producer output into clinical facts. | **family lens** | Lens-swap ablations, v08 replay layers. |
| **Finding store** | Canonical intermediate store of clinical findings before headline projection. | **clinical finding store** | Assembly object model, v01 structural replay. |
| **Headline projection** | Final format mapping from findings to scoreboard surfaces (`clinical_headline`, per-entity headlines). | **headline projection** | Scoring canon, SF representation discussions. |
| **Evidence validation gate** | Shared cross-task check that cited spans are grounded in source text; currently inert (Δ=0) on both tasks. | **evidence validation gate** | C2 ablation, `evidence_groundedness_metric.md`. |
| **Standard dictionary / normalize** | Shared lexical normalization layer with measurable cross-task dividend. | **shared normalization layer** | Cross-task ablation (+0.039 ExECT, +0.029 Gan). |
| **Safety-floor gate** | Selective deterministic guard that can override risky LLM outputs on matched predicates — not the rules-only floor. | **safety-floor gate** | `selective_safety_floor_gate_v0` replay, verifier experiments. |
| **Evidence Trace Check** | Gan deterministic fourth stage verifying evidence presence (ADR 0014). | **evidence trace check** | Distinct from hybrid “Verify” vocabulary in ExECT. |

---

## Scoring surfaces

| Surface | Plain definition | Recommended display name | Keep codename when… |
| --- | --- | --- | --- |
| **clinical_headline** | ExECT primary composite score for cross-entity clinical recovery (de-duplicated). | **primary clinical recovery score** | Scoreboards, model-swap full-200, ADR 0027. |
| **state_profile** | SF-only faithful state surface; primary for SF-family experiments (not the project headline). | **SF state profile** (`state_profile`) | SF ladder, GEPA arms, ADR 0037. |
| **Purist** | Strict Gan label match after render — primary Gan holdout metric. | **strict label match** (Purist) | test450 tables, wall ceiling percentages. |
| **Pragmatic** | Lenient Gan label match allowing controlled equivalence classes. | **lenient label match** (Pragmatic) | Secondary Gan readout; never substitute for Purist on holdout claims. |
| **Benchmark / CUI** | Strict phrase + attributes + CUI multiset — diagnostic comparability to published Fonferko-Shadrach figures. | **benchmark surface** | C1 reconciliation, dev140 0.39/0.70 vs paper 0.87/0.90 gap. |
| **phrase_only / semantic** | Lower layers of the nine-entity ladder isolating recall vs attribute gaps. | **phrase / semantic layers** | Per-entity deep dives; not headline numbers. |
| **evidence_grounded_rate** | Share of cited evidence strings present in the note (exact or repaired). | **evidence groundedness rate** | Cross-task validity metric; not clinical correctness. |

---

## Process & splits

| Term | Plain definition | Recommended display name | Keep codename when… |
| --- | --- | --- | --- |
| **validation750** | Gan primary development split — 750 locked validation letters for iteration and row review. | **Gan validation split** (750 rows) | Split manifest `gan2026_split_v1`, component ladder, P0.2 features. |
| **test450** | Gan locked holdout — 450 letters; aggregate-only inspection after freeze. | **Gan holdout** (450 rows) | Production/ceiling/floor table, frozen generalization audits. |
| **dev140** | ExECT development split — 140 letters for replay, ablations, and gold-quality adjudication. | **ExECT development split** (140 rows) | v08 control, component-off, C1 row analysis. |
| **full-200** | ExECT full corpus evaluation — 200 letters; aggregate-only for holdout-facing claims. | **ExECT full evaluation** (200 rows) | Model-swap JSON, C2/C4 aggregate claims; no casual row tuning. |
| **Forward-observable** | Any signal computable at inference from model outputs — never the hidden gold label. | **forward-observable signal** | Wall definition, feature inventory, abstention routing. |
| **Frozen aggregate audit** | Predeclared holdout run with fixed protocol; only published aggregates, not development tuning. | **frozen aggregate audit** | test450 / full-200 gates, `gated_blockers` runbook. |
| **Predeclare → ladder → freeze** | Experiment discipline: write intent, escalate split size, then lock before holdout. | **evaluation ladder discipline** | C5 claim, `experiments/README.md`, registry workflow. |
| **Component-off replay** | Re-score frozen artifacts with one layer removed to attribute impact. | **component-off replay** | C2 evidence, dev140 ladders, promotion boundaries. |

---

## Paper claims (C1–C5)

| ID | Plain definition | Recommended display name | Keep codename when… |
| --- | --- | --- | --- |
| **C1** | ExECT benchmark gap on SF/Dx is mostly gold noise and format mismatch, not model failure. | **gold-quality reconciliation claim** (C1) | Manuscript abstract/Methods; cite dev140 adjudication caveat. |
| **C2** | Shared format layers help both tasks; evidence gate is structurally inert. | **cross-task component dividend** (C2) | Ablation markdown, aggregate full-200 component-off. |
| **C3** | Gan wall mechanism partially transfers to ExECT SF binding slice (bounded, 6/9 checks). | **bounded wall transfer** (C3) | `exectv2_sf_wall_transfer_probe` artifacts; not definitive abstention product. |
| **C4** | Frozen same-core architecture reaches headline parity across models (DeepSeek ≥ GPT; Qwen diagnostic). | **model-agnostic architecture claim** (C4) | `exectv2_same_core_model_swap_full200` JSON; per-family table required. |
| **C5** | Project demonstrates evaluation discipline (panels, CV, regression catches, frozen audits). | **evaluation discipline claim** (C5) | Gan v0.7 regression, Gate 4 protocols — instances, not hypotheticals. |

---

## Disambiguation (ceiling / floor / plateau)

| Term | Plain definition | Recommended display name | Keep codename when… |
| --- | --- | --- | --- |
| **Ceiling (Gan)** | Best honest holdout under frozen protocol — V12 at 0.842 Purist; prior, not tuning target. | **holdout ceiling** (Gan) | Distinct from production 0.809; never conflate with ExECT. |
| **Ceiling (ExECT)** | Apparent F1 cap from annotation-format scoring, not irreducible model error (see gold-quality ceiling). | **annotation-format ceiling** (ExECT) | C1, SF/Dx row analyses; not The Wall. |
| **Floor (rules-only)** | Controlled Gan lower bound without LLM facts — rules_only at 0.762 Purist. | **rules-only baseline floor** | Holdout three-way table (floor / production / ceiling). |
| **Safety-floor gate** | Runtime guard layer that may block or replace specific risky predictions. | **safety-floor gate** | Never shorten to “floor” in prose — collides with rules-only baseline. |
| **Plateau** | Metric stops improving despite more tuning — e.g. GEPA ~0.73 dev140, risk–coverage irreducible tier ~17%. | **performance plateau** | Optimizer kill-criteria, P0.2 residual tier; not the same as ceiling. |
| **Saturation** | Validation prefix (25/50/250) no longer discriminates candidates near comparator ceiling. | **validation saturation** | Escalation to hard cases or frozen test audit per saturated-validation protocol. |

---

## Quick Gan vs ExECT map

| Concept | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Primary score | Purist / Pragmatic on **test450** | **`clinical_headline`** on **dev140** / **full-200** |
| Key negative | **The Wall** (confident over-reading) | **Gold-quality ceiling** (annotation format) |
| Production artifact | **`v0_reference`** (364/450) | **v08** holistic assembly |
| Best holdout comparator | **V12** (379/450) — not promoted | N/A — v08 is frozen control |
| Development split | **validation750** | **dev140** |
| Holdout / full eval | **test450** (aggregate-only) | **full-200** (aggregate-only) |

---

## Related documents

| Document | Role |
| --- | --- |
| [`CONTEXT.md`](../../CONTEXT.md) | Extended vocabulary and wikilink graph |
| [`docs/collaborator_onboarding.md`](../collaborator_onboarding.md) | New-collaborator entry point |
| [`docs/THREAD_MAP.md`](../THREAD_MAP.md) | Five narrative reading paths |
| [`docs/canon/05_ceilings_wall.md`](../canon/05_ceilings_wall.md) | Two-ceiling structural canon |
| [`docs/canon/10_paper_provenance.md`](../canon/10_paper_provenance.md) | C1–C5 claims register |
