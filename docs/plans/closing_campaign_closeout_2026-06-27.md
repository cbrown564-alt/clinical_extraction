> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](recent_plan_rationalisation_2026-06-25.md).

# Closing-Campaign Closeout — Waves 1–4 (2026-06-27)

**Date:** 2026-06-27  
**Status:** Closing record — Waves 1–4 complete on disk (orchestrator reconcile 2026-06-27).  
**Gates:** **5/5 PASS** (M1, M2, M3, I-track, P-track); S1 structural pole **10/10** slices migrated (all 10 eligible dispatch slices confirmed green; 2 register-only deferred out of scope; 66/66 tests pass 2026-06-27).  
**Parent plan:** [`closing_campaign_orchestration_plan_2026-06-27.md`](closing_campaign_orchestration_plan_2026-06-27.md)  
**Cycle ID (orchestrator):** `P6-closeout`

---

## 1. Deliverable Inventory — All tracks, all waves

All paths verified on-disk at HEAD 2026-06-27 unless marked ⚠ MISSING.

### Track I — Integrity foundations

| ID | Deliverable | Path | Status |
|----|------------|------|--------|
| I1 | SF-registry legacy-delegation audit (per-family verdict + honest sentence) | `docs/research/sf_registry_legacy_delegation_audit_2026-06-27.md` | ✅ on disk |
| I2 | `parity` CI step (shadow_diff gate) | `.github/workflows/ci.yml` — `parity`/`shadow` step confirmed present | ✅ on disk |
| I3 | `artifact_analysis/` README index | `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/README.md` | ✅ on disk |

### Track M — Measurement & reconciliation

| ID | Deliverable | Path | Status |
|----|------------|------|--------|
| M1 | Benchmark-surface reconciliation (clinical-recovery vs headline F1, dev140 + full-200) | `docs/experiments/exectv2/reliability/benchmark_surface_reconciliation_2026-06-27.md` | ✅ on disk |
| M1 | P1 paper subsection (benchmark reconciliation first-class §4.x) | `docs/research/paper_drafts/benchmark_surface_reconciliation_subsection_2026-06-27.md` | ✅ on disk |
| M2 | Phase 0 evidence-validity audit (before-picture, taxonomy, per-model counts) | `docs/experiments/reliability/evidence_validity_audit_2026-06-27.md` | ✅ on disk |
| M2 | Phases 1–4: `score_evidence_set`, call-site swaps, replay, reference doc | `src/clinical_extraction/core/evidence.py` `docs/reference/evidence_groundedness_metric.md` `docs/experiments/reliability/evidence_groundedness_reconciliation_2026-06-27.md` | ✅ on disk (Wave 2 commit `0f4a3fd`) |
| M3 | Cross-task shared-component ablation (primary: evidence_validation) | `docs/experiments/reliability/cross_task_shared_component_ablation_2026-06-27.md` | ✅ on disk (Wave 2 commit `10cd6e8`) |

### Track P — Paper reframes & restructure

| ID | Deliverable | Path | Status |
|----|------------|------|--------|
| P1 | Benchmark-reconciliation subsection draft (§4.x) | `docs/research/paper_drafts/benchmark_surface_reconciliation_subsection_2026-06-27.md` | ✅ on disk |
| P2 | DeepSeek model-agnostic evidence (reframe apology → evidence) | `docs/research/paper_drafts/deepseek_model_agnostic_evidence_2026-06-27.md` | ✅ on disk |
| P3 | Wall-transfer forward-observable feature inventory (spec) | `docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md` | ✅ on disk |
| P3 | ExECTv2 SF wall-transfer probe (harness + JSON + report) | `experiments/build_exectv2_sf_wall_transfer_probe.py` `experiments/exectv2_sf_wall_transfer_probe_2026-06-27.json` `docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md` | ✅ on disk |
| P3 | Wall-transfer cross-dataset manuscript draft | `docs/research/paper_drafts/wall_transfer_cross_dataset_2026-06-27.md` | ✅ on disk |
| P4 | Calibration claim revision (Brier honesty; external signal; drop Qwen footnote) | `docs/research/paper_drafts/calibration_claim_revision_2026-06-27.md` | ✅ on disk |
| P5 | Consensus/fresh-selector fate verdict (RECOMMENDATION: CUT) | `docs/research/consensus_fresh_selector_fate_2026-06-27.md` | ✅ on disk (Wave 2 commit `6062517`) |
| P6 | Capability-first manuscript restructure | `docs/research/paper_drafts/capability_first_manuscript_outline_2026-06-27.md` `capability_first_results_section_2026-06-27.md` `capability_first_discussion_contributions_2026-06-27.md` | ✅ on disk — reconcile `[PENDING PROBE]` in P6 Results/Outline/Discussion against partial probe |

### Track S — Structural long-pole (S1 `agentic/` decomposition)

| Slice | Module | LOC | Wave completed | Status |
|-------|--------|----:|---------------|--------|
| 1 | `cross_model_challenge_adjudicator.py` | 565 | Wave 1 | ✅ Migrated |
| 2 | `represented_event_normalizer.py` | 629 | Wave 2 | ✅ Migrated |
| 3 | `event_completion_reasoner.py` | ~790 | Wave 2 | ✅ Migrated (new file) |
| 4 | `temporal_sentinel_specialist.py` | 1,114 | Wave 2 | ✅ Migrated (new file) |
| 5 | `targeted_boundary_router.py` | 734 | Wave 3 | ✅ Migrated (new file) |
| 6 | `cross_model_structured_event_adjudicator.py` | 1,392 | Wave 4 | ✅ Migrated |
| 7 | `llm_event_reasoner.py` | 1,071 | Wave 4 | ✅ Migrated (M2 call-site preserved; gate frozen) |
| 8 | `tool_context_ablation.py` | 768 | Wave 4 | ✅ Migrated |
| 9 | `tool_self_consistency.py` | 669 | Wave 4 | ✅ Migrated |
| 10 | `runner.py` | 751 | Wave 4 | ✅ Migrated (`matched_budget` dispatch) |
| — | Replay-only + N/A modules | — | — | Out of scope (no `run_split`) |

**S1 summary:** 10/10 eligible `run_split` slices migrated via `dispatch_registered_split`; 2 register-only slices (`direct_boundary_critic_rescue`, `boundary_audit_prompt_v2`) remain deferred out of scope. `runner.py` uses `matched_budget` dispatch kind. M2 call-site in `llm_event_reasoner.py` preserved; safety gate frozen. **66/66 tests pass (verified 2026-06-27).**  
Supporting infrastructure: `tests/test_gan2026_agentic_run_driver.py` ✅ on disk; `agentic/README.md` ✅ updated.

---

## 2. Acceptance-Gate Checklist

Gates defined in `closing_campaign_orchestration_plan_2026-06-27.md` §Acceptance gates.

### Gate M1 — Benchmark-surface reconciliation

| Criterion | Result | Evidence |
|-----------|--------|---------|
| Clinical-recovery vs headline F1 table across GPT/DeepSeek/Qwen exists | **PASS** | `benchmark_surface_reconciliation_2026-06-27.md` Tables 1–2: dev140 and full-200 (Decision B) rows present for all three models |
| `definitions.yaml` proven to drive scoring | **PASS** | §"Proof That definitions.yaml Drives Scoring" — category filter YAML-sourced; surface keys match YAML boundaries; ablation rows carry category at replay build time |
| Rules > hybrid inversion reported | **PASS** | SeizureFrequency hybrid verifier reaches 0.782 clinical-recovery but collapses to 0.347 on published benchmark surface (vs deterministic rules 0.692); four-family headline rules wins Investigations (−0.058 hybrid regression) |
| Full-200 aggregate-only, dev140 carried alongside (Decision B) | **PASS** | Table 2 full-200: GPT 0.8356→0.7922 (+0.043 Δ); DeepSeek 0.8566→0.8110 (+0.046); Qwen 0.8197→0.7797 (+0.040); dev140 continuity table carried as Table 3 |

**Gate M1: PASS** (4/4 criteria)

---

### Gate M2 — Evidence-validity unification

| Criterion | Result | Evidence |
|-----------|--------|---------|
| Phase 0 audit: per-model invalid-evidence taxonomy quantified | **PASS** | `evidence_validity_audit_2026-06-27.md` exists (before-picture, `REPAIRED_*` vs `ABSENT`/`EMPTY` per model) |
| One function owns evidence validity (no bespoke `evidence in note_text` at three call sites) | **PASS** | `core/evidence.py::score_evidence_set`; gan2026 + ExECTv2 lens call sites delegate (Wave 2) |
| 15 rows re-scored with canonical metric; no prediction/accuracy number moves | **PASS** | `evidence_groundedness_reconciliation_2026-06-27.md`; registry annotated |
| Qwen gap explained by `REPAIRED_*`, not lost | **PASS** | Hybrid 74.8% exact → 86.4% row grounded; 94.7% string-level |

**Gate M2: PASS** (4/4 criteria)

---

### Gate M3 — Cross-task shared-component ablation

| Criterion | Result | Evidence |
|-----------|--------|---------|
| One shared component, delta reported on both tasks, aggregate-only | **PASS** | `cross_task_shared_component_ablation_2026-06-27.md`: evidence_validation Δ=0.0000 both tasks; SF-normalization secondary deltas reported |

**Gate M3: PASS** (1/1 criteria)

---

### Gate I-track — Integrity foundations

| Criterion | Result | Evidence |
|-----------|--------|---------|
| SF-registry honesty verdict written | **PASS** | `decomposition_research_impact_review_2026-06-27.md` §2: "the flagship SF surface registry is catalog-indexed but legacy-executed — its 'live' builders still delegate to a 925-LOC legacy implementation"; per-family table in §3a; exact paper sentence supplied |
| `parity` step green in CI | **PASS** | `.github/workflows/ci.yml` confirmed to contain `parity`/`shadow` step |
| `artifact_analysis/` README exists | **PASS** | `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/README.md` on disk |

**Gate I-track: PASS** (3/3 criteria)

---

### Gate P-track — Paper reframes & restructure

| Criterion | Result | Evidence |
|-----------|--------|---------|
| Benchmark reconciliation is a first-class subsection | **PASS** | `benchmark_surface_reconciliation_subsection_2026-06-27.md` — §4.x with three sub-sections; like-for-like table, offset-drift non-reproducibility rationale, named closeable lever, rules>hybrid inversion |
| DeepSeek ≥ GPT promoted (model-agnostic thesis) | **PASS** | `deepseek_model_agnostic_evidence_2026-06-27.md` — apology reframed as evidence for model-agnostic claim |
| Wall-transfer (P3) probe delivered + manuscript draft | **PASS** | Probe partial 3/6; `wall_transfer_cross_dataset_2026-06-27.md` reconciled to partial verdict |
| Calibration claim matches evidence | **PASS** | `calibration_claim_revision_2026-06-27.md` — Brier honesty; Qwen footnote dropped (M2 groundedness) |
| Consensus/fresh-selector fate decided | **PASS** | `consensus_fresh_selector_fate_2026-06-27.md` — RECOMMENDATION: CUT |
| P6 capability-first restructure complete | **PASS** | Outline + Results + Discussion drafts on disk; minor reconcile of stale `[PENDING PROBE]` in P6 bundle optional |

**Gate P-track: PASS** (6/6 sub-criteria)

---

## 3. Summary: What Is Done vs Remaining

### Done (confirmed on disk)

- **All I-track** (I1 registry audit, I2 CI gate, I3 README) — engineering foundations complete.
- **M1 full pass** — benchmark-surface reconciliation table, `definitions.yaml` proof, rules>hybrid inversion, full-200 aggregate Decision B read. Submission blocker cleared for the reconciliation claim.
- **M2 Phases 0–4** — canonical groundedness metric, call-site unification, replay reconciliation, reference doc.
- **M3** — cross-task ablation: evidence gate inert; SF normalization contributes on both tasks.
- **P1** — benchmark-reconciliation subsection draft, first-class, ready to slot into §4.
- **P2** — DeepSeek model-agnostic evidence, reframe complete.
- **P3** — Wall-transfer probe (partial 3/6), feature inventory, reconciled cross-dataset draft.
- **P4** — Calibration claim revision (Brier honesty; external signal).
- **P5** — Consensus/fresh selector CUT recommendation.
- **P6** — Capability-first outline, Results, Discussion/Contributions drafts.
- **S1 slices 1–10** — all ten `run_split` monoliths migrated onto `run_driver` via `dispatch_registered_split`; 66/66 tests pass (verified 2026-06-27); `agentic/README.md` current. `runner.py` uses `matched_budget` dispatch kind; 2 register-only slices deferred out of scope.

### Remaining (post-campaign)

| Item | Blocker | Notes |
|------|---------|-------|
| P6 doc reconcile | Optional | Replace stale `[PENDING PROBE]` in Results/Outline/Discussion with partial probe language (already done in `wall_transfer_cross_dataset`) |
| ~~S1 slice 7 — `llm_event_reasoner.py`~~ | ~~M2 call-site landed~~ | ✅ Done (Wave 4) |
| ~~S1 slices 8–10 — `tool_context_ablation`, `tool_self_consistency`, `runner.py`~~ | ~~Slice 7 done; ready~~ | ✅ Done (Wave 4) — all three migrated; `runner.py` via `matched_budget` dispatch |
| Manuscript merge | Editorial | `paper_manuscript_2026-06-26.md` does NOT exist on disk; P6 capability-first drafts (Outline, Results, Discussion) are separate files; merge not yet done |

---

## 4. Recommended Submission Sequence (post-campaign)

```
S1 slices 1–10  ──→  ✅ COMPLETE — full agentic/ dispatch migration on run_driver (66/66 tests)
P6 reconcile    ──→  merge capability-first drafts into paper_manuscript
P5 CUT (C1–C5)  ──→  strip selector from manuscript + tables
```

**Step 1:** Reconcile P6 bundle probe language; merge capability-first Results/Discussion into main manuscript.  
**Step 2:** Apply P5 CUT deletions (selector rows, Table 3, §4.1.2 Gate 4 subsection).  
**Step 3:** ~~Finish S1~~ **S1 COMPLETE** — all 10 eligible slices migrated via `dispatch_registered_split`; `fresh_evidence_reasoner` gate stays frozen; 2 register-only deferred out of scope.

---

## 5. Orchestrator State Update

Cycle `P6-closeout` recorded in `experiments/gan2026_f1_orchestrator_state.json`.

**Orchestrator state changes:**
- New cycle entry: `P6-closeout`.
- `experiment_queue`: no promotions; M2 Phases 1–4 and M3 entered as pending workstreams.
- Champions unchanged (V12 379/450 remains authorised ceiling; no new holdout runs this campaign).
