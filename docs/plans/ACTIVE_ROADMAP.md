# Active Roadmap

Last updated: 2026-07-14

This file records current work. Individual plans under `docs/plans/` remain as
historical design records; each carries a status banner pointing here.

**Thread-based reading:** [`docs/THREAD_MAP.md`](../THREAD_MAP.md)

**Current status and evidence:** [`PROJECT_STATUS.md`](../../PROJECT_STATUS.md)

**Surgery findings and deletion rules:**
[`repository_surgery_assessment_2026-07-14.md`](../research/maintenance/repository_surgery_assessment_2026-07-14.md)

**Plan triage archive:** [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md)

---

## Active objective

Complete the deletion-led repository surgery, then close the four research
follow-ups against the retained architecture. The reduced system must preserve
one active control per task plus minimal deterministic, LLM-only, and hybrid
reference configurations for both tasks. Gan `test450` remains an
author-uninspected, aggregate-only holdout. ExECT full200 is a
development-inclusive audit, not an independent holdout. GEPA optimization is
closed; its LLM-only result remains a reference comparator.

---

## P0 — Do now (repository surgery)

| Item | Owner doc | Action |
| --- | --- | --- |
| **Freeze retained paper story** | [`docs/canon/10_paper_provenance.md`](../canon/10_paper_provenance.md) | Keep the S1–S9 acceptance matrix current; no deletion may remove required proof |
| **Evidence manifest repair** | [`repo_simplification_plan_2026-06-22.md`](repo_simplification_plan_2026-06-22.md) | Manifest rebuilt with present hashes; external large-artifact storage remains open |
| **Minimal reference system** | [`PROJECT_STATUS.md`](../../PROJECT_STATUS.md) | Six cells now have exact source/config/scorer/test closure and passing no-call replay |
| **Delete closed work** | [`repo_simplification_plan_2026-06-22.md`](repo_simplification_plan_2026-06-22.md) | Remove closed candidates, their configs, reports, artifacts, and tests together |
| **Frontend / Observatory scope** | [`repository_surgery_assessment_2026-07-14.md`](../research/maintenance/repository_surgery_assessment_2026-07-14.md) | Removed: neither product was required by the retained contribution or evidence closure |
| **Restore real quality gates** | [`thermo_nuclear_code_quality_audit_plan_2026-06-26.md`](thermo_nuclear_code_quality_audit_plan_2026-06-26.md) | Make full pytest, Ruff, and mypy green on the reduced tree; remove historical allowlist exemptions |

---

## P1 — Next (close evidence gaps on the reduced tree)

| Item | Owner doc | Action |
| --- | --- | --- |
| **Gan efficiency comparison (S3)** | [`docs/canon/10_paper_provenance.md`](../canon/10_paper_provenance.md) | Match quality with calls, tokens, cost, latency, model, hardware, cache, split, and scorer |
| **Phrase/CUI/attribute-bundle reproduction (S7)** | [`docs/canon/04_scoring.md`](../canon/04_scoring.md) | Re-prioritize deterministic paper-surface engineering and run a paper-comparable evaluation |
| **Broad confidence calibration (S8)** | [`calibration_abstention_review_routing_strengthening_plan_2026-07-01.md`](calibration_abstention_review_routing_strengthening_plan_2026-07-01.md) | Evaluate model-reported confidence out of sample; preserve a negative result if confidence is degenerate |
| **Annotation evidence consolidation (S9)** | [`docs/canon/10_paper_provenance.md`](../canon/10_paper_provenance.md) | Generate one complete ledger/taxonomy with scoring effects, handling, sensitivity, and review status |
| **Manuscript evidence sync** | [`docs/research/paper_manuscript_2026-06-26.md`](../research/paper_manuscript_2026-06-26.md) | Regenerate tables and reconcile stale calibration, comparator, and gold-adjudication language |

---

## P2 — After cleanup (fresh model calls require predeclaration)

| Item | Owner doc | Action |
| --- | --- | --- |
| **Six-model frozen comparison (S4/S5)** | [`docs/design/model_strategy.md`](../design/model_strategy.md) | Run the same frozen architecture/prompt/scorer with the six exact runtime models; conclude from the observed result, not the preferred ordering |
| **Final reliability table** | [`docs/canon/09_cross_task_reliability.md`](../canon/09_cross_task_reliability.md) | Consolidate both tasks and the six-model failure/calibration analysis with bounded claim language |
| **Fresh-checkout closeout** | [`repository_surgery_assessment_2026-07-14.md`](../research/maintenance/repository_surgery_assessment_2026-07-14.md) | Install, replay both tasks, rebuild every surviving paper table, verify hashes and split barriers, then run the full quality suite |

---

## Explicitly not active

- **GEPA optimization** — closed negative (`docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`)
- **Gan holdout tuning** — frozen; aggregate citation only
- **LLM-only dedup as production control** — plateau ~0.73 vs v08 ~0.92; diagnostic only
- **Making the consensus/fresh selector the default** — CUT (`docs/research/consensus_fresh_selector_fate_2026-06-27.md`)
- **MLflow expansion** — optional mirror, not part of the retained contribution
- **Dissertation document** — out of scope; IEEE paper is deliverable (`supervisor_brief_gap_closure_plan` Phase D)

---

## Completed workstreams (historical pointers)

| Workstream | Closeout |
| --- | --- |
| Closing campaign (2026-06-27) | [`closing_campaign_closeout_2026-06-27.md`](closing_campaign_closeout_2026-06-27.md) |
| Supervisor brief gap closure | [`supervisor_brief_gap_closure_plan_2026-07-01.md`](supervisor_brief_gap_closure_plan_2026-07-01.md) |
| Evidence groundedness unification | [`evidence_validity_unification_plan_2026-06-27.md`](evidence_validity_unification_plan_2026-06-27.md) → `core/evidence.py`, [`docs/reference/evidence_groundedness_metric.md`](../reference/evidence_groundedness_metric.md) |
| Same-core development-inclusive full200 aggregate | [`exectv2_same_core_model_swap_architecture_freeze_plan_2026-06-25.md`](exectv2_same_core_model_swap_architecture_freeze_plan_2026-06-25.md) |
| ExECTv2 v08 holistic assembly | [`docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`](../experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md) |
| GEPA program | [`exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md`](exectv2_gepa_focused_lanes_recall_plan_2026-06-28.md) |

---

## Plan index by status

| Status | Plans |
| --- | --- |
| **ACTIVE** | `ACTIVE_ROADMAP.md` (this file), `repo_simplification_plan_2026-06-22.md`, `thermo_nuclear_code_quality_audit_plan_2026-06-26.md` |
| **DEFERRED UNTIL REDUCED TREE** | `calibration_abstention_review_routing_strengthening_plan_2026-07-01.md` and the S4–S9 studies named above |
| **HISTORICAL** | All other plans under `docs/plans/` including `exectv2/00–13` — see status banner on each file |
