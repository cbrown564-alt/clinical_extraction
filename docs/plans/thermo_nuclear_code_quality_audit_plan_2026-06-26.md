# Thermo-Nuclear Code Quality Audit — Plan & Status

**Date:** 2026-06-26  
**Last updated:** 2026-06-26 (Wave 3 complete)  
**Scope:** Full-repo audit on `main` (not a single PR)  
**Standard:** [thermo-nuclear-code-quality-review](../../.claude/skills/thermo-nuclear-code-quality-review/SKILL.md) — structural simplification, code-judo moves, 1k-line file discipline, boundary cleanliness  
**Overall verdict:** **CONDITIONAL APPROVE** — Wave 3 remediation complete; residual monolith decomposition tracked via line-count allowlist

---

## Executive summary

The codebase is a **research instrument with a real UI**, not a greenfield product. Architectural intent is strong across both task families (ExECTv2, Gan2026): typed contracts, LLM/deterministic separation, replay-first experimentation, and unusually good test guardrails.

**Wave 3 (four sprints, commits `f4753fd` … `14f046e`)** finished the consolidation plan: verifier pipelines unified, LLM/deterministic boundaries cleaned, YAML kernels externalized, frontend adapter surfaces wired, regression gates added, and megatests split.

Primary debt remaining is **incremental monolith shrinkage** (ExECTv2 LLM top-4 still >500 LOC each, Gan assembly ~2.9k LOC) — now **frozen and gated** via `scripts/check_line_counts.py` allowlist rather than unbounded growth.

---

## Audit coverage (6 review agents)

| Area | Agent scope | Verdict |
|------|-------------|---------|
| Core + Observatory | `core/`, `observatory/` | CONDITIONAL → **improved** (facades Sprint 4) |
| ExECTv2 assembly/deterministic/hybrid | `assembly/`, `deterministic/`, `hybrid/`, `contract/` | CONDITIONAL → **improved** |
| ExECTv2 LLM | `exectv2/llm/` (~33k LOC) | CONDITIONAL REJECT → **improved** (registry + YAML + projection split) |
| ExECTv2 runners/reports | `runners/`, `reports/` | CONDITIONAL → **improved** (ablation YAML) |
| Gan2026 | `tasks/seizure_frequency/gan2026/` (~77k LOC) | CONDITIONAL → **improved** (probe split, AgenticStage) |
| Frontend + tests + scripts | `frontend/`, `tests/`, `scripts/` | **CONDITIONAL APPROVE** |

---

## Wave 1 — Completed (commits `157321c` … `2b1d2b4`)

See prior commit index. Claim policy, observatory routers, lens chain removal, Gan pipeline stages, frontend mock mode.

---

## Wave 2 — Completed (commits `be4ce84` … `c5d80c1`)

See prior commit index. Conventions/scoring packages, scorecard bootstrap, entity verifier (SF + investigations), AgenticStage scaffold, test helpers, DatasetRuntimeAdapter kernel.

---

## Wave 3 — Completed (commits `f4753fd` … `14f046e`)

### Sprint 1 — Delete complexity (`f4753fd`)

| Task | Status | Notes |
|------|--------|-------|
| Diagnosis + med_inv entity_verifier migration | ✅ Done | Thin facades; 93 tests pass |
| Target indicators → `deterministic/target_projection/` | ✅ Done | 36 projection/repair functions; monolith −1,019 LOC |
| Delete workbench ConfigStore dead path | ✅ Done | `useArchitectStore` only |

### Sprint 2 — Kernels (`2a5f83c`)

| Task | Status | Notes |
|------|--------|-------|
| `generation_selection` strategy registry | ✅ Done | 14 handlers; elif chain removed; import-time guard |
| Structured worked examples → YAML | ✅ Done | 49 examples; `structured.py` −1,203 LOC |
| Component ablation catalog → YAML | ✅ Done | 7 replay specs; pydantic validation |

### Sprint 3 — Boundaries (`357a1c4`)

| Task | Status | Notes |
|------|--------|-------|
| Assessment probe god-module split | ✅ Done | Assembly + signature + facades; probe facade 38 LOC |
| Migrate 2 agentic stages | ✅ Done | `direct_boundary_critic_rescue`, `structured_event_verifier` |
| Gallery/laboratory → runtime adapter | ✅ Done | `getRuntimeAdapter().surfaces.*` |

### Sprint 4 — Hardening (`14f046e`)

| Task | Status | Notes |
|------|--------|-------|
| CI line-count gates | ✅ Done | `scripts/check_line_counts.py` + `tests/test_line_count_gates.py`; 46-entry allowlist |
| Megatest splits (3 files) | ✅ Done | 7 new test modules; 544 tests collected (unchanged) |
| State graph optional producer | ✅ Done | `use_state_graph` seam; default off |
| Observatory task facades | ✅ Done | `gan2026/frontend_review.py`; routers facade-only |

---

## Post–Wave 3 follow-ups (in progress)

| Task | Status | Owner |
|------|--------|-------|
| GitHub Actions CI workflow | ⏳ In flight | `.github/workflows/ci.yml` |
| Fix `pred_count` report scorer bug | ⏳ In flight | `llm_first_essential_evaluation._aggregate_score_dicts` |
| Workbench → runtime adapter | ⏳ In flight | `app/workbench/page.tsx` |
| Fix `componentLadder.test.ts` drift | ⏳ In flight | 4 failing expectations vs 7 run-level entries |
| PyYAML in `pyproject.toml` | ⏳ Open | Used by prompt YAML loaders |
| Pre-commit hook for line-count gates | ⏳ Open | Optional |

---

## Tier A–C backlog (deferred beyond Wave 3)

These items remain for future sprints; they are **not blockers** for Wave 3 completion but prevent full thermo-nuclear APPROVE on monolith size.

### A1. ExECTv2 LLM monolith decomposition (partial)

| File | Lines (post-W3) | Status |
|------|----------------:|--------|
| `llm_only_key_entities_generation_selection.py` | ~5,285 | 🟡 Registry dispatch done; corpora remain |
| `llm_only_key_entities_structured.py` | ~2,606 | 🟡 YAML examples done; orchestrator remains |
| `llm_target_indicators_single_call.py` | ~2,352 | 🟡 Projection moved; LLM shell remains |
| `llm_only_clinical_findings.py` | ~3,295 | 🔴 Not started — 3-stage pipeline package |

### A2. Assessment assembly second pass

`clinical_assessment_assembly.py` (~2,928 LOC) — split normalization parsers into submodules.

### A3. Remaining agentic migrations

`fresh_evidence_reasoner`, `cross_model_structured_event_adjudicator`, etc. — incremental `AgenticStage` or freeze as experimental.

### B1–B4, C2–C4

Cross-model reliability YAML, conventions/seizure_frequency YAML, `useObservatoryData` hook, structured-event repair registry, traceAdapter registry, `useUrlState` primitive — unchanged from original plan.

---

## File-size watchlist (post–Wave 3)

| File | Lines | Status |
|------|------:|--------|
| `llm_only_key_entities_generation_selection.py` | ~5,285 | 🟡 Allowlisted; registry frozen |
| `llm_only_key_entities_structured.py` | ~2,606 | 🟡 Allowlisted; YAML examples |
| `llm_only_clinical_findings.py` | ~3,295 | 🔴 Allowlisted; not decomposed |
| `llm_target_indicators_single_call.py` | ~2,352 | 🟡 Allowlisted; projection split |
| `clinical_assessment_assembly.py` | ~2,928 | 🟡 Allowlisted; probe split |
| `llm_candidate_set_clinical_assessment_probe.py` | ~38 | ✅ Facade |
| `conventions/seizure_frequency.py` | ~1,728 | 🟡 YAML candidate |
| `fresh_evidence_reasoner.py` | ~2,026 | 🟡 Legacy agentic |
| `component_ablation_replay.py` | ~1,365 | 🟡 Catalog externalized |
| `observatory/routers/*.py` | thin | ✅ Facade imports |

Gate: `python scripts/check_line_counts.py` — fails on new violations or allowlist ceiling growth.

---

## Approval gates (thermo-nuclear bar)

**Wave 3 plan: complete.**

**Ready for full APPROVE when (residual):**

- [x] No triplicated claim-boundary / normalize / bootstrap logic
- [x] Observatory routers import task facades, not analysis monoliths (Gan + ExECT cached builders)
- [x] Reports do not import `scoring._*` private symbols
- [x] Frontend: no silent mock mode
- [x] Entity verifiers fully on `entity_verifier` pipeline (all four entities)
- [ ] ExECTv2 LLM top-4 monoliths each <500 LOC (partial — gated, not done)
- [ ] All explorer routes on runtime adapter (workbench pending)
- [ ] CI workflow running line-count gates on every PR (in flight)
- [ ] Zero pre-existing test failures in target-indicators megatest cluster (in flight)

**Would trigger REJECT if:**

- New 1k+ line modules added without decomposition plan / allowlist update
- New agentic variant without `AgenticStage` scaffold
- New `artifact_analysis` production imports from runner

---

## Commit index (remediation)

| Commit | Summary |
|--------|---------|
| `157321c` | Claim policy + Observatory routers |
| `984df32` | ExECTv2 LLM shared kernel |
| `bf2bf50` | Legacy lens chain removal |
| `f009335` | ExECTv2 CLI common |
| `1efda40` | Gan2026 pipeline stages |
| `2b1d2b4` | Frontend explicit mock mode |
| `be4ce84` | Conventions package |
| `6f3fc3b` | Scoring package |
| `e66e4f8` | Scorecard + bootstrap unification |
| `644f153` | Entity verifier (SF + investigations) |
| `32af32a` | Gan2026 AgenticStage |
| `9f23514` | Test helpers + megatest split |
| `c5d80c1` | DatasetRuntimeAdapter |
| `3376b83` | Audit plan + Wave 3 roadmap |
| `f4753fd` | Wave 3 Sprint 1: verifiers, target projection, ConfigStore |
| `2a5f83c` | Wave 3 Sprint 2: registry, YAML kernels, ablation catalog |
| `357a1c4` | Wave 3 Sprint 3: probe split, agentic stages, gallery/lab adapter |
| `14f046e` | Wave 3 Sprint 4: line-count gates, megatest splits, state graph, facades |

---

## References

- Review skill: `.claude/skills/thermo-nuclear-code-quality-review/SKILL.md`
- Related plans: `docs/plans/repo_simplification_plan_2026-06-22.md`, `docs/plans/exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md`
- Prior simplification context: `PROJECT_STATUS.md`, `CONTEXT.md`
