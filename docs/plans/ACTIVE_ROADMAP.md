# Active Roadmap

Last updated: 2026-07-01

**This is the single answer to “what are we doing now?”** Individual plans under
`docs/plans/` remain as historical design records; each carries a status banner
pointing here.

**Thread-based reading:** [`docs/THREAD_MAP.md`](../THREAD_MAP.md)  
**Live evidence stack:** [`PROJECT_STATUS.md`](../../PROJECT_STATUS.md)  
**Plan triage archive:** [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md)

---

## Active objective

ExECTv2 reliability/component-evidence phase; paper closeout on capability-first
claims (`clinical_headline` primary). Gan holdout evidence frozen. GEPA workstream
closed (negative result — LLM-only plateaus below hybrid).

---

## P0 — Do now (paper integrity)

| Item | Owner doc | Action |
| --- | --- | --- |
| **Manuscript evidence gaps (5 items)** | [`manuscript_evidence_gaps_closure_plan_2026-07-01.md`](manuscript_evidence_gaps_closure_plan_2026-07-01.md) | Close gaps from [`paper_claims_evidence_review_2026-07-01.md`](../research/paper_claims_evidence_review_2026-07-01.md): GEPA three-way write-up, cross-task ablation (already run 2026-06-27), SF+Dx gold-quality in abstract/§1, stale “gap” language |
| **IEEE LaTeX re-sync** | [`PROJECT_STATUS.md`](../../PROJECT_STATUS.md) § Now | Markdown manuscript includes 2026-06-30 Diagnosis gold-quality revision; LaTeX still at 2026-06-26 |
| **Documentation consolidation Wave 1** | [`docs/THREAD_MAP.md`](../THREAD_MAP.md) | Thread map + this roadmap + plan status headers (this PR) |

---

## P1 — Next (claims strengthening, no new model calls unless predeclared)

| Item | Owner doc | Action |
| --- | --- | --- |
| **Calibration / review-routing manuscript framing** | [`calibration_abstention_review_routing_strengthening_plan_2026-07-01.md`](calibration_abstention_review_routing_strengthening_plan_2026-07-01.md) | Honest weak-pillar language (Brier Δ 0.0142; binding-slice AUROC 0.676) — framing only unless plan authorizes new runs |
| **Documentation consolidation Wave 2** | (forthcoming work packages) | `PAPER_CANON.md`, `exectv2_evaluation_canon.md`, ExECT/Gan research canons — see THREAD_MAP consolidation note |
| **Predeclaration runbook** | (not yet written) | Template for frozen aggregate audits |

---

## P2 — Deferred (stable evidence spine first)

| Item | Owner doc | Action |
| --- | --- | --- |
| **Repo simplification / archive cleanup** | [`repo_simplification_plan_2026-06-22.md`](repo_simplification_plan_2026-06-22.md) | Freeze-and-index before delete; dedicated cleanup branch |
| **MLflow dry-run sync** | [`mlflow_experiment_observability_implementation_plan_2026-06-25.md`](mlflow_experiment_observability_implementation_plan_2026-06-25.md) | Phases 0–2 complete; optional mirror only — registry remains claim-of-record |
| **Thermo-nuclear code quality debt** | [`thermo_nuclear_code_quality_audit_plan_2026-06-26.md`](thermo_nuclear_code_quality_audit_plan_2026-06-26.md) | Incremental: agentic monoliths, YAML corpora — no big-bang refactor |
| **Experiment narrative consolidation** | THREAD_MAP T3/T1 long tails | Collapse validation750 / rq_series / holistic v01–v07 to workstream canons |

---

## Explicitly not active

- **GEPA optimization** — closed negative (`docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`)
- **Gan holdout tuning** — frozen; aggregate citation only
- **LLM-only dedup as production control** — plateau ~0.73 vs v08 ~0.92; diagnostic only
- **Consensus/fresh selector promotion** — CUT (`docs/research/consensus_fresh_selector_fate_2026-06-27.md`)
- **Dissertation document** — out of scope; IEEE paper is deliverable (`supervisor_brief_gap_closure_plan` Phase D)

---

## Completed workstreams (historical pointers)

| Workstream | Closeout |
| --- | --- |
| Closing campaign (2026-06-27) | [`closing_campaign_closeout_2026-06-27.md`](closing_campaign_closeout_2026-06-27.md) |
| Supervisor brief gap closure | [`supervisor_brief_gap_closure_plan_2026-07-01.md`](supervisor_brief_gap_closure_plan_2026-07-01.md) |
| Evidence groundedness unification | [`evidence_validity_unification_plan_2026-06-27.md`](evidence_validity_unification_plan_2026-06-27.md) → `core/evidence.py`, [`docs/reference/evidence_groundedness_metric.md`](../reference/evidence_groundedness_metric.md) |
| Same-core full-200 aggregate | [`exectv2_same_core_model_swap_architecture_freeze_plan_2026-06-25.md`](exectv2_same_core_model_swap_architecture_freeze_plan_2026-06-25.md) |
| ExECTv2 v08 holistic assembly | [`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`](../experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md) |
| GEPA program | [`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`](exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md) |

---

## Plan index by status

| Status | Plans |
| --- | --- |
| **ACTIVE** | `ACTIVE_ROADMAP.md` (this file), `manuscript_evidence_gaps_closure_plan_2026-07-01.md`, `calibration_abstention_review_routing_strengthening_plan_2026-07-01.md`, `recent_plan_rationalisation_2026-06-25.md` (triage index) |
| **DEFERRED** | `repo_simplification_plan_2026-06-22.md`, `mlflow_experiment_observability_implementation_plan_2026-06-25.md`, `thermo_nuclear_code_quality_audit_plan_2026-06-26.md` |
| **HISTORICAL** | All other plans under `docs/plans/` including `exectv2/00–13` — see status banner on each file |
