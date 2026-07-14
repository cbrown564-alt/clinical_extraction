# Paper Canon — Claims, Evidence & Provenance

Last updated: 2026-07-14

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

## Surgery acceptance matrix (the retained paper story)

Repository surgery is complete only when every surviving statement below resolves
to present, hashed evidence and the smallest source/config/test closure needed to
reproduce it. A predeclared negative result may close an open study, but the claim
must then be weakened or removed. The desired direction of a result is never a
completion criterion.

| ID | Required story | Current evidence | Completion gate | State |
| --- | --- | --- | --- | --- |
| **S1** | One modular architecture evaluated on Gan seizure frequency and ExECT broad phenotyping | Shared core, task modules, and paper results exist | One documented stage map plus reproducible reference runs/replays for both tasks | Partial |
| **S2** | Deterministic, LLM-only, and hybrid forms with attributable strengths and weaknesses | Gan three-way table; ExECT deterministic/GEPA/hybrid evidence on development surfaces | Minimal two-task × three-family reference configurations, comparable score layers, and component-owner tables | Partial |
| **S3** | Complex multi-trace Gan ceiling is only modestly better than the single-call operational path, at materially higher cost/latency | Frozen Gan quality comparison: 379/450 vs 364/450 Purist | Matched call-count, token, cost, latency, model, hardware, cache, split, and scorer table | Partial |
| **S4** | Controlled six-model comparison across three hosted and three open/local models | Registered evidence for GPT-4.1-mini, DeepSeek, and Qwen 3.6:35b | Same frozen architecture/prompt/scorer over all six exact runtime identifiers; size/reasoning conclusion follows the data | Open |
| **S5** | Overconfident rate emission on ambiguous evidence is a recurring cross-model failure | Strong Gan Wall evidence; bounded ExECT transfer (6/9 checks) | Per-model unknown-vs-rate, confidence/calibration, and permitted mechanism analysis across the frozen model panel; primary literature provenance | Partial |
| **S6** | Evidence extraction, normalization, projection, schema validation, and evidence verification are explicit and ablatable | Normalization/projection deltas; evidence gate is score-inert on current representative replays | Every reference run emits the five stage records; each stage has a causal delta or an appropriate rejection/repair challenge test | Partial |
| **S7** | ExECT primary scoring matches entity type, normalized phrase, and clinical attributes; deterministic phrase/CUI/full-attribute-bundle engineering reproduces the paper-comparable surface | Primary clinical-recovery surface exists; current like-for-like result remains below the published result | Source-backed IAA-method check, scorer contract tests, full deterministic bundle implementation, and paper-comparable evaluator/run | Open |
| **S8** | Reliability is tested on both tasks: grounding, schema validity, calibration, abstention/review routing, consistency, and robustness | Both task scorecards exist; broad-task calibration remains weak and model confidence is unused | One matched scorecard plus out-of-sample model-confidence calibration and bounded routing verdict | Partial |
| **S9** | Annotation flaws and conventions are completely and transparently handled | Family ledgers and `experiments/gold_data_issues.jsonl` exist | One generated taxonomy/ledger with source evidence, scoring effect, handling, sensitivity analysis, and internal-vs-external review status for every cited case | Partial |

**Retention consequence:** keep one active control per task and the minimal
reference configuration or replay contract for each of the six task/family cells.
Do not retain the discarded candidates that led to those controls. The surgery
assessment's earlier “one ExECT path + one Gan path” wording is insufficient on
its own because it would not preserve S2.

Every evidence row must name dataset, split manifest, row-inspection policy,
scorer, model and role, prompt/program version, cache/replay mode, repair policy,
artifact path, and hash before its state can become complete.

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

ExECTv2 **LLM-only** (GEPA single-pass) plateaus ~**0.731** (mini) / ~**0.654** (Qwen) vs hybrid v08 **0.9189** (was 0.9155; corrected 2026-07-02, see `08_gepa.md`) on dev140 `clinical_headline`. This **is** the missing three-way leg — a **negative** result.

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
| Calibration | Full200 aggregate Brier 0.2225 vs base rate 0.2340 (Δ 0.0115), ECE 0.0587 after dev140-fit regularization repair | Promoted internal scoring rule; not deployment-ready probability calibration |
| Review routing | ~97% burden, ~90% catch | Review-nearly-everything, not low-burden triage |
| Binding unknown slice AUROC | 0.676 | Below 0.70 usefulness bar; H0 retained |

The 2026-07-07 signal probe tested the previously unused cross-model and
self-consistency features on dev140. Cross-model agreement did not generalize
(pooled AUROC 0.5958; no non-SF family above 0.70); self-consistency was
orthogonal but weak. Model-reported confidence remains unused, and a low-burden
review-routing operating point remains open.

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
| Selected evidence | [`retained_evidence_manifest.md`](../experiments/retained_evidence_manifest.md) | Verified JSON paths, hashes, sizes, and claim boundaries |

**Surgery authority rule:** the retained JSON manifest is now verified against
present files and registry metadata. It owns selected evidence. The registry
continues to own run lineage, and this claims register continues to own whether
the evidence is sufficient for a paper statement.

---

## Open gaps

Execution order is owned by [`ACTIVE_ROADMAP.md`](../plans/ACTIVE_ROADMAP.md).
The claim gaps that must remain visible here are:

1. Rebuild the retained evidence manifest and name the two-task × three-family reference set.
2. Produce the matched Gan quality/cost/latency comparison for S3.
3. Implement and evaluate deterministic phrase/CUI/full-attribute-bundle reproduction for S7.
4. Evaluate model-reported confidence for broad phenotyping and finish the bounded routing verdict for S8.
5. Consolidate annotation defects, conventions, scorer artifacts, and adjudication limits for S9.
6. After the reduced architecture is frozen, run the six-model S4 comparison and use it to close or revise S5.
7. Regenerate manuscript tables from retained evidence and re-sync the IEEE LaTeX source.

---

## Related reading

- [`../research/contribution_thesis.md`](../research/contribution_thesis.md) — experimental ontology (three families)
- [`../research/closing_stage_research_critique_2026-06-27.md`](../research/closing_stage_research_critique_2026-06-27.md) — cross-strand gaps
- [`../research/supervisor_brief_conformance_audit_2026-07-01.md`](../research/supervisor_brief_conformance_audit_2026-07-01.md) — brief alignment
- [`docs/THREAD_MAP.md`](../THREAD_MAP.md) T4 — paper reading path
