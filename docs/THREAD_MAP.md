# Documentation Thread Map

Five narrative threads span the documentation corpus. Pick one based on your
job; each path lists at most eight hops before the long tail (bucket READMEs,
registry rows, row-level case files).

**Read first:** [`README.md`](../README.md) → [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) → this map.

| Don't know which thread? | Start with [`collaborator_onboarding.md`](collaborator_onboarding.md) / [`.html`](collaborator_onboarding.html), then return here. |
| --- | --- |

Full consolidation roadmap: [`docs/plans/ACTIVE_ROADMAP.md`](plans/ACTIVE_ROADMAP.md).

---

## T1 — Reliability & The Wall

*Confident over-reading on ambiguous seizure-frequency letters.*

**Question:** Where does confident over-reading live, and can forward-observable
signals route it without gold?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`CONTEXT.md`](../CONTEXT.md) § Reliability | Vocabulary: The Wall, irreducible residual, external risk score |
| 2 | [`docs/canon/06_gan_clinical_policy.md`](canon/06_gan_clinical_policy.md) | **Canon:** architecture arc, frozen recommendation, The Wall |
| 3 | [`docs/design/reliability_thesis.md`](design/reliability_thesis.md) | Project-level reliability claim and success criteria |
| 4 | [`experiments/gan2026_reliability_master_scorecard_2026-06-17.md`](../experiments/gan2026_reliability_master_scorecard_2026-06-17.md) | Machine scorecard (aggregate evidence) |
| 5 | [`docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md`](research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md) | Cross-dataset feature inventory |
| 6 | [`docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md`](experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md) | ExECTv2 SF wall-transfer probe |
| 7 | [`docs/canon/10_paper_provenance.md`](canon/10_paper_provenance.md) § C3 | Paper claim boundary for wall transfer |
| 8 | [`docs/experiments/gan2026/VALIDATION750_CANON.md`](experiments/gan2026/VALIDATION750_CANON.md) | Workstream canon; rq_series via COMPONENT_MECHANICS |

**Start here if:** you are writing the reliability pillar or explaining why
abstention routing failed on binding residuals.

---

## T2 — Clinical recovery & capability-first scoring

**Question:** What is the headline score, and why is strict benchmark F1 not it?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`PROJECT_STATUS.md`](../PROJECT_STATUS.md) § Active Priorities | `clinical_headline` primary; benchmark/CUI diagnostic |
| 2 | [`docs/canon/04_scoring.md`](canon/04_scoring.md) | **Canon:** P1–P7, metric hierarchy, gold-quality ceiling |
| 3 | [`docs/canon/10_paper_provenance.md`](canon/10_paper_provenance.md) § C1 | Claim register for SF/Dx gold-quality |
| 4 | [`docs/canon/README.md`](canon/README.md#gold-case-ledger-generated-per-family) § Gold case ledger | Generated, per-family genuine-vs-gold mechanism breakdown for all 4 `KEY_FAMILIES`, including Prescription and Investigations |
| 5 | [`docs/decisions/0027-clinical-recovery-is-the-exectv2-headline-projection-is-an-artifact-layer.md`](decisions/0027-clinical-recovery-is-the-exectv2-headline-projection-is-an-artifact-layer.md) | ADR: headline vs projection |
| 6 | [`docs/decisions/0037-sf-state-profile-is-primary-clinical-metric.md`](decisions/0037-sf-state-profile-is-primary-clinical-metric.md) | ADR: SF `state_profile` for SF-family experiments |
| 7 | [`docs/experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md`](experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md) | v01→v08 assembly ladder (v08 frozen) |
| 8 | [`docs/canon/08_gepa.md`](canon/08_gepa.md) | LLM-only ceiling (three-way negative) |

**Start here if:** you are interpreting F1 numbers, gold-quality row adjudication,
or the SF/Diagnosis “plateau” reframing.

---

## T3 — Architecture, portability & component evidence

**Question:** What does each pipeline stage own, and what does ablation prove?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`docs/design/architecture.md`](design/architecture.md) | Package layers and task boundaries |
| 2 | [`docs/design/component_evidence_attribution_architecture.md`](design/component_evidence_attribution_architecture.md) | Component ownership and evidence required before a candidate becomes the default |
| 3 | [`docs/research/contribution_thesis.md`](research/contribution_thesis.md) | Three architecture families (rules / LLM-only / hybrid) |
| 4 | [`docs/canon/07_exect_plan11.md`](canon/07_exect_plan11.md) | Selected architectures and full-200 evidence |
| 5 | [`docs/canon/08_gepa.md`](canon/08_gepa.md) | LLM-only vs hybrid (closed negative) |
| 6 | [`docs/decisions/0009-gan2026-staged-hybrid-assembly.md`](decisions/0009-gan2026-staged-hybrid-assembly.md) | Gan staged hybrid (not LLM-first) |
| 7 | [`docs/decisions/0032-clinical-finding-assembly-is-the-exectv2-plan11-spine.md`](decisions/0032-clinical-finding-assembly-is-the-exectv2-plan11-spine.md) | ExECT Plan 11 pipeline |
| 8 | [`docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md`](experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md) | Cross-task component dividend |

**Start here if:** you are changing pipeline code, running component-off replay,
or comparing rules vs hybrid vs LLM-only.

---

## T4 — Paper closeout & claim boundaries

**Question:** What can the manuscript claim, and what evidence backs each claim?

| Hop | Document | Why |
| --- | --- | --- |
| 1 | [`docs/canon/10_paper_provenance.md`](canon/10_paper_provenance.md) | **Canon:** C1–C5 claims register and provenance |
| 2 | [`docs/plans/ACTIVE_ROADMAP.md`](plans/ACTIVE_ROADMAP.md) | Open paper/manuscript work only |
| 3 | [`docs/research/paper_manuscript_2026-06-26.md`](research/paper_manuscript_2026-06-26.md) | Markdown manuscript source |
| 4 | [`docs/experiments/final_artifact_index_2026-06-22.md`](experiments/final_artifact_index_2026-06-22.md) | Frozen hashes and claim boundaries |
| 5 | [`docs/canon/04_scoring.md`](canon/04_scoring.md) | Scoring surfaces and gold-quality |
| 6 | [`docs/canon/07_exect_plan11.md`](canon/07_exect_plan11.md) | Frozen experiment evidence tables |
| 7 | [`docs/research/paper_claims_evidence_review_2026-07-01.md`](research/paper_claims_evidence_review_2026-07-01.md) | Detailed gap analysis (companion) |
| 8 | [`literature/IEEE/IEEE-conference-template-062824/`](../literature/IEEE/IEEE-conference-template-062824/) | LaTeX draft (may lag markdown) |

**Start here if:** you are editing Results/Discussion, syncing IEEE LaTeX, or
checking whether a number can support a paper claim.

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
| **Don't know which thread?** | [`collaborator_onboarding.md`](collaborator_onboarding.md) / [`.html`](collaborator_onboarding.html) first → return here |
| **New collaborator** | [`collaborator_onboarding.md`](collaborator_onboarding.md) / [`.html`](collaborator_onboarding.html) → THREAD_MAP (pick thread) |
| **New engineer** | `collaborator_onboarding.md` / `.html` → README → NAVIGATION → THREAD_MAP (pick thread) → `architecture.md` → ACTIVE_ROADMAP |
| **Paper author** | [`canon/10_paper_provenance.md`](canon/10_paper_provenance.md) → [`canon/04_scoring.md`](canon/04_scoring.md) → [`canon/07_exect_plan11.md`](canon/07_exect_plan11.md) → [`canon/06_gan_clinical_policy.md`](canon/06_gan_clinical_policy.md) |
| **Experiment runner** | T5 path → relevant thread (T2 or T3) → bucket README under `docs/experiments/` |

---

## Consolidation status

**Wave 1 (2026-07-01):** THREAD_MAP, ACTIVE_ROADMAP, plan status headers, control-plane alignment.

**Wave 2 (2026-07-01):** Five canon documents:

| Canon | Path |
| --- | --- |
| Paper claims & provenance | [`canon/10_paper_provenance.md`](canon/10_paper_provenance.md) |
| ExECT evaluation & surfaces | [`canon/04_scoring.md`](canon/04_scoring.md) |
| Gan closeout & The Wall | [`canon/06_gan_clinical_policy.md`](canon/06_gan_clinical_policy.md) |
| ExECT closeout evidence | [`canon/07_exect_plan11.md`](canon/07_exect_plan11.md) |
| GEPA negative program | [`canon/08_gepa.md`](canon/08_gepa.md) |

**Wave 3 (2026-07-01):** Workstream canons + routing index:

| Workstream canon | Path |
| --- | --- |
| Gan validation750 | [`experiments/gan2026/VALIDATION750_CANON.md`](experiments/gan2026/VALIDATION750_CANON.md) |
| Gan RQ1–RQ10 | [`experiments/gan2026/COMPONENT_MECHANICS_CANON.md`](experiments/gan2026/COMPONENT_MECHANICS_CANON.md) |
| ExECT holistic ladder | [`experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md`](experiments/exectv2/key_entities/HOLISTIC_ASSEMBLY_LADDER_CANON.md) |
| Canon index | [`canon/README.md`](canon/README.md) |
| Archive policy | [`archive/README.md`](archive/README.md) |

**Wave 4 (2026-07-01):** Structural migration to `docs/canon/01–10`; workstream
canons for Diagnosis, SF, self-consistency; 75 iteration files archived under
`docs/archive/experiments/` with redirect stubs.

| Structural canon | Path |
| --- | --- |
| 01 System architecture | [`canon/01_system_architecture.md`](canon/01_system_architecture.md) |
| 02 Pipeline stages | [`canon/02_pipeline_spine.md`](canon/02_pipeline_spine.md) |
| 03 Evidence / frozen | [`canon/03_evidence_claims_frozen.md`](canon/03_evidence_claims_frozen.md) |
| 04 Scoring | [`canon/04_scoring.md`](canon/04_scoring.md) |
| 05 Ceilings / Wall | [`canon/05_ceilings_wall.md`](canon/05_ceilings_wall.md) |
| 06 Gan policy | [`canon/06_gan_clinical_policy.md`](canon/06_gan_clinical_policy.md) |
| 07 ExECT Plan 11 | [`canon/07_exect_plan11.md`](canon/07_exect_plan11.md) |
| 08 GEPA | [`canon/08_gepa.md`](canon/08_gepa.md) |
| 09 Cross-task reliability | [`canon/09_cross_task_reliability.md`](canon/09_cross_task_reliability.md) |
| 10 Paper / provenance | [`canon/10_paper_provenance.md`](canon/10_paper_provenance.md) |

| Wave 4 workstream canon | Path |
| --- | --- |
| Diagnosis family ladder | [`canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md`](canon/workstreams/DIAGNOSIS_FAMILY_LADDER_CANON.md) |
| SF adjudicator ladder | [`canon/workstreams/SF_ADJUDICATOR_LADDER_CANON.md`](canon/workstreams/SF_ADJUDICATOR_LADDER_CANON.md) |
| Self-consistency / entropy | [`canon/workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md`](canon/workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md) |

Legacy paths (`research/PAPER_CANON.md`, etc.) redirect to numbered canons.
