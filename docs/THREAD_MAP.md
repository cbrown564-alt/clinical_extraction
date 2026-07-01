# Documentation Thread Map

Five narrative threads span the documentation corpus. Pick one based on your
job; each path lists at most eight hops before the long tail (bucket READMEs,
registry rows, row-level case files).

**Control plane first:** [`README.md`](../README.md) → [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) → this map.

Full consolidation roadmap: [`docs/plans/ACTIVE_ROADMAP.md`](plans/ACTIVE_ROADMAP.md).

---

## T1 — Reliability & The Wall

**Question:** Where does confident over-reading live, and can forward-observable
signals route it without gold?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`CONTEXT.md`](../CONTEXT.md) § Reliability | Vocabulary: The Wall, irreducible residual, external risk score |
| 2 | [`docs/design/reliability_thesis.md`](design/reliability_thesis.md) | Project-level reliability claim and success criteria |
| 3 | [`docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`](research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md) | Definitive Gan accounting (P0.2, P2.1, V12 ceiling) |
| 4 | [`experiments/gan2026_reliability_master_scorecard_2026-06-17.md`](../experiments/gan2026_reliability_master_scorecard_2026-06-17.md) | Machine scorecard (aggregate evidence) |
| 5 | [`docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md`](research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md) | Cross-dataset feature inventory |
| 6 | [`docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`](experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md) | ExECTv2 SF wall-transfer probe |
| 7 | [`docs/research/paper_drafts/wall_transfer_cross_dataset_2026-06-27.md`](research/paper_drafts/wall_transfer_cross_dataset_2026-06-27.md) | Paper-facing C3 draft |
| 8 | [`docs/experiments/gan2026/README.md`](experiments/gan2026/README.md) | Long tail: validation750, rq_series, frozen_test |

**Start here if:** you are writing the reliability pillar or explaining why
abstention routing failed on binding residuals.

---

## T2 — Clinical recovery & capability-first scoring

**Question:** What is the headline score, and why is strict benchmark F1 not it?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) § Active Priorities | `clinical_headline` primary; benchmark/CUI diagnostic |
| 2 | [`docs/research/exectv2_gold_representation_and_scoring_principles_2026-06-17.md`](research/exectv2_gold_representation_and_scoring_principles_2026-06-17.md) | P1–P7 principles (target construction, duplicates) |
| 3 | [`docs/research/exectv2_benchmark_surface_overall_2026-06-18.md`](research/exectv2_benchmark_surface_overall_2026-06-18.md) | Like-for-like benchmark surface anchor (~0.39 dev140) |
| 4 | [`docs/research/paper_drafts/benchmark_reconciliation_sf_gold_quality_revision_2026-06-29.md`](research/paper_drafts/benchmark_reconciliation_sf_gold_quality_revision_2026-06-29.md) | SF gold-quality ceiling mechanism |
| 5 | [`docs/research/paper_drafts/benchmark_reconciliation_dx_gold_quality_revision_2026-06-30.md`](research/paper_drafts/benchmark_reconciliation_dx_gold_quality_revision_2026-06-30.md) | Diagnosis gold-quality ceiling mechanism |
| 6 | [`docs/decisions/0027-clinical-recovery-is-the-exectv2-headline-projection-is-an-artifact-layer.md`](decisions/0027-clinical-recovery-is-the-exectv2-headline-projection-is-an-artifact-layer.md) | ADR: headline vs projection |
| 7 | [`docs/decisions/0037-sf-state-profile-is-primary-clinical-metric.md`](decisions/0037-sf-state-profile-is-primary-clinical-metric.md) | ADR: SF `state_profile` for SF-family experiments |
| 8 | [`docs/experiments/exectv2/README.md`](experiments/exectv2/README.md) | Long tail: per-family iteration reports |

**Start here if:** you are interpreting F1 numbers, gold-quality row adjudication,
or the SF/Diagnosis “plateau” reframing.

---

## T3 — Architecture, portability & component evidence

**Question:** What does each pipeline stage own, and what does ablation prove?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`docs/design/architecture.md`](design/architecture.md) | Package layers and task boundaries |
| 2 | [`docs/design/component_evidence_attribution_architecture.md`](design/component_evidence_attribution_architecture.md) | Component ownership and promotion contract |
| 3 | [`docs/research/contribution_thesis.md`](research/contribution_thesis.md) | Three architecture families (rules / LLM-only / hybrid) |
| 4 | [`docs/research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md`](research/exectv2_final_key_family_architecture_synthesis_2026-06-18.md) | ExECTv2 dev140 architecture state |
| 5 | [`docs/decisions/0009-gan2026-staged-hybrid-assembly.md`](decisions/0009-gan2026-staged-hybrid-assembly.md) | Gan staged hybrid (not LLM-first) |
| 6 | [`docs/decisions/0032-clinical-finding-assembly-is-the-exectv2-plan11-spine.md`](decisions/0032-clinical-finding-assembly-is-the-exectv2-plan11-spine.md) | ExECT Plan 11 spine |
| 7 | [`docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`](experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md) | Cross-task component dividend |
| 8 | [`docs/design/README.md`](design/README.md) | Design spine index and ADR pointer |

**Start here if:** you are changing pipeline code, running component-off replay,
or comparing rules vs hybrid vs LLM-only.

---

## T4 — Paper closeout & claim boundaries

**Question:** What can the manuscript claim, and what evidence backs each claim?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`docs/research/paper_claims_evidence_review_2026-07-01.md`](research/paper_claims_evidence_review_2026-07-01.md) | Ranked gap analysis (load-bearing) |
| 2 | [`docs/plans/ACTIVE_ROADMAP.md`](plans/ACTIVE_ROADMAP.md) | Open paper/manuscript work only |
| 3 | [`docs/research/paper_manuscript_2026-06-26.md`](research/paper_manuscript_2026-06-26.md) | Markdown manuscript source |
| 4 | [`docs/experiments/final_artifact_index_2026-06-22.md`](experiments/final_artifact_index_2026-06-22.md) | Frozen hashes and claim boundaries |
| 5 | [`docs/research/supervisor_brief_conformance_audit_2026-07-01.md`](research/supervisor_brief_conformance_audit_2026-07-01.md) | Brief conformance table |
| 6 | [`docs/design/brief_role_crosswalk.md`](design/brief_role_crosswalk.md) | Brief roles → actual architecture |
| 7 | [`docs/research/closing_stage_research_critique_2026-06-27.md`](research/closing_stage_research_critique_2026-06-27.md) | Cross-strand gap analysis |
| 8 | [`literature/IEEE/IEEE-conference-template-062824/`](../literature/IEEE/IEEE-conference-template-062824/) | LaTeX draft (may lag markdown) |

**Start here if:** you are editing Results/Discussion, syncing IEEE LaTeX, or
checking whether a number is promotion-safe.

---

## T5 — Engineering integrity & experiment governance

**Question:** How do runs get registered, frozen, and retired?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`docs/NAVIGATION.md`](NAVIGATION.md) | Tier model and two-tree rule |
| 2 | [`docs/runbooks/documentation_lifecycle.md`](runbooks/documentation_lifecycle.md) | Where new docs go; archive policy |
| 3 | [`experiments/README.md`](../experiments/README.md) | Validation ladder and scan order |
| 4 | [`experiments/registry.jsonl`](../experiments/registry.jsonl) | Machine run registry |
| 5 | [`docs/REGENERATION.md`](REGENERATION.md) | Regenerating tracked artifacts |
| 6 | [`docs/reference/evidence_groundedness_metric.md`](reference/evidence_groundedness_metric.md) | Canonical evidence metric |
| 7 | [`docs/runbooks/gated_blockers_2026-06-18.md`](runbooks/gated_blockers_2026-06-18.md) | Holdout and full-200 gates |
| 8 | [`docs/plans/repo_simplification_plan_2026-06-22.md`](plans/repo_simplification_plan_2026-06-22.md) | Deferred cleanup policy |

**Start here if:** you are adding a predeclaration, fixing registry paths, or
planning archive/cleanup without breaking frozen evidence.

---

## Persona shortcuts

| Persona | Path |
| --- | --- |
| **New engineer** | README → NAVIGATION → THREAD_MAP (pick thread) → `architecture.md` → ACTIVE_ROADMAP |
| **Paper author** | PROJECT_STATUS → T4 path → T2 for scoring vocabulary |
| **Experiment runner** | T5 path → relevant thread (T2 or T3) → bucket README under `docs/experiments/` |

---

## Consolidation status

This map is **Wave 1** of the documentation consolidation program (2026-07-01).
Future waves will add canon documents (`PAPER_CANON`, `exectv2_evaluation_canon`,
workstream summaries) and stub redirects for absorbed sources. Frozen artifact
paths are never renamed — only linked from canon docs.
