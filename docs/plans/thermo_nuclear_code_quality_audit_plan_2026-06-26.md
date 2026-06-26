# Thermo-Nuclear Code Quality Audit — Plan & Status

**Date:** 2026-06-26  
**Last updated:** 2026-06-26 (Wave C Sprint 5: P1-4 layer hygiene + P2-1 artifact_analysis import gate + gate #7 report main() removal)  
**Scope:** Full-repo audit on `main` (not a single PR)  
**Standard:** [thermo-nuclear-code-quality-review](../../.claude/skills/thermo-nuclear-code-quality-review/SKILL.md) — structural simplification, code-judo moves, 1k-line file discipline, boundary cleanliness  
**Overall verdict:** **CONDITIONAL APPROVE** — major layer inversions fixed and largest Gan/runtime monoliths decomposed; ExECTv2 LLM top-4 and report cluster remain gated debt

---

## Executive summary

The codebase is a **research instrument with a real UI**. Architectural intent is strong across both task families (ExECTv2, Gan2026): typed contracts, LLM/deterministic separation, replay-first experimentation, and unusually good test guardrails.

**Historical context:** Wave 3 (commits `f4753fd` … `14f046e`) delivered verifier pipelines, YAML kernels, frontend adapter kernel, and line-count gates. That work froze debt but did not finish monolith decomposition.

**This review cycle** ran six thermo-nuclear audit agents across the full repo, then executed two remediation waves (12 commits, `9d6ac46` … `45443be`). The audits were uniformly **CONDITIONAL REJECT** at the area level; remediation addressed the highest-leverage structural blockers.

### What changed in this cycle

| Theme | Before review | After remediation |
|-------|---------------|-------------------|
| Registry ownership | `RunRegistryEntry` lived under Gan2026; core imported task code | Canonical `core/registry.py`; 47 importers migrated |
| Gan assembly | 2,929 LOC god-module | 139 LOC orchestrator + `deterministic/assessment/*` |
| Gan projection | 1,373 LOC stage importing LLM probe | 4 modules; deterministic assembly call; CLI to experiments |
| ExECTv2 LLM dispatch | Strategy registry was relocation theater | 13 letter runners inverted into strategies; monolith −1,075 LOC |
| ExECTv2 boundaries | Hybrid imported `llm_only_single_pass`; triplicate drug tables | `contract/drug_lexicon.py`, `contract/repair.py`; assembly → scoring |
| MLflow sync | Dual plan types + experiment constants in core | Unified `MlflowSyncPlan`; core 770 → 399 LOC |
| Observatory | 366 LOC junk-drawer `helpers.py` | 54 LOC paths/settings; `observatory/gan2026/*` + `core/paths.py` |
| Reports | `llm_first` at gate violation; runner owned render | `reports/llm_first/` package; 72 LOC facade |
| Frontend | Gallery 1,005 LOC; `lib` imported from `app/` | Gallery 26 LOC; Gan surfaces in `components/gan2026/`; CI build/test/lint |

**Primary debt remaining:** ExECTv2 LLM top-4 still 2.3k–4.1k LOC each; report cluster (~17k LOC) still has 3 allowlisted monoliths at ceiling; Gan `runner.py` (1,103 LOC) and `artifact_analysis/` (~24k LOC) unaddressed; SF repair stacks consolidated into `sf_surface_registry` (Phases 0–5 complete) with legacy facades pending shim removal after one release cycle.

Gate: `python scripts/check_line_counts.py` — **OK** on current `main`.

---

## Review methodology

Six parallel read-only audit agents, each applying the thermo-nuclear standard:

1. Ambitious structural simplification (code-judo over polish)
2. 1k-line file discipline
3. No spaghetti special-case growth in shared paths
4. Direct code over magic; explicit type boundaries
5. Logic in canonical layer; reuse helpers
6. Flag sequential orchestration and non-atomic updates

Each agent delivered: verdict, top structural findings, code-judo opportunities, file-size inventory, boundary issues, prioritized remediation.

---

## Audit findings by area (2026-06-26)

### 1. Core + Observatory — CONDITIONAL REJECT → **improved**

**Findings (pre-remediation):**
- Core → Gan dependency inversion (`mlflow_registry_sync` imported `run_registry` from task package)
- Observatory was Gan2026 with ExECTv2 garnish; `helpers.py` junk drawer (365 LOC)
- Dual MLflow sync subsystems (`RegistryMlflowSyncPlan` vs `MlflowComparisonSyncPlan`)
- Experiment constants (`SAME_CORE_DEV140_*`) baked into core
- Gold audit non-atomic persistence in router layer

**Remediation status:**

| Task | Status | Commit / notes |
|------|--------|----------------|
| Promote `RunRegistryEntry` + `load_run_registry` to `core/registry.py` | ✅ Done | `9d6ac46` |
| Collapse MLflow sync into single `MlflowSyncPlan` | ✅ Done | `89f4477` |
| Evict `SAME_CORE_DEV140_*` from core | ✅ Done | `mlflow_comparison_groups.py` |
| Decompose `mlflow_registry_sync.py` below 500 LOC | ✅ Done | 399 LOC + 4 helper modules |
| Extract `core/paths.py` | ✅ Done | `2d3917a` |
| Restructure `observatory/helpers.py` → `observatory/gan2026/` | ✅ Done | helpers 366 → 54 LOC |
| Add Pydantic response models for high-traffic routes | 🔴 Open | Skipped to prioritize extraction |
| Gold audit atomic store + thin router | 🔴 Open | |
| `run_ablation` async/job pattern or dev-only guard | 🔴 Open | |
| Consolidate split policy (`claim_policy` vs `mlflow_tracking` substring rules) | 🔴 Open | |

---

### 2. ExECTv2 deterministic / hybrid — CONDITIONAL REJECT → **partial**

**Findings:**
- Three parallel SeizureFrequency repair stacks (`rules/`, `conventions/seizure_frequency.py` 1,728 LOC, `target_projection/` ~1,607 LOC)
- `all_entities.py` god-module (1,455 LOC); `lenses.py` (1,179 LOC) violates dictionary design
- Assembly imported reports (layer inversion)
- Hybrid imported repair utilities from `llm/`
- Drug alias tables triplicated

**Remediation status:**

| Task | Status | Commit / notes |
|------|--------|----------------|
| `contract/drug_lexicon.py` single source | ✅ Done | `75eefba` |
| `contract/repair.py` — `repair_attributes`, `check_evidence` | ✅ Done | hybrid off `llm_only_single_pass` |
| Assembly → reports inversion fix | ✅ Done | `scoring/reporting.py` facade |
| Collapse SF repair stacks into data-driven surface registry | ✅ Done | Phases 0–5 — `exectv2_sf_repair_stack_consolidation_design_2026-06-26.md`; dev140 SF F1 gate green |
| Split `all_entities.py` per-entity modules | 🔴 Open | |
| Refactor `lenses.py` to thin convention adapters | 🔴 Open | |
| Merge or relocate `target_projection/` (LLM-only consumer) | 🟡 Shimmed | Deprecated → `sf_surface_registry.adapters.projection`; Phase 3 catalog migration pending |
| `normalize_phrase` → `contract/text.py` | 🔴 Open | |
| Typed row models for assembly JSONL | 🔴 Open | |
| Single `PipelineStage` enum across deterministic/hybrid/assembly | 🔴 Open | |

---

### 3. ExECTv2 LLM — CONDITIONAL REJECT → **improved**

**Findings:**
- Top-4 monoliths held ~44% of layer LOC
- `generation_selection` registry inverted dependencies (strategies imported monolith privates)
- `entity_verifier` half-real: runner unified, content monoliths relocated
- Diagnosis verifier chain (~2.6k LOC) parallel to new pipeline
- `llm_only_single_pass.py` hidden god-module
- `llm_only_clinical_findings.py` undecomposed 3-stage pipeline (3,295 LOC)
- Deterministic modules mislabeled under `llm/` (`llm_sf_state_projection`, etc.)

**Remediation status:**

| Task | Status | Commit / notes |
|------|--------|----------------|
| Extract `shared/mention_pipeline.py` | ✅ Done | `39a34bc` |
| Mandate `shared/json_parse` in structured + generation_selection | ✅ Done | `39a34bc`, `45443be` |
| Invert all `generation_selection` letter runners into strategies | ✅ Done | `45443be`; monolith 5,209 → 4,134 |
| Externalize prompt corpora to YAML (decision tables, verifier content, qwen_compact) | 🔴 Open | 1 of ~8 corpora done (structured examples) |
| `pipelines/clinical_findings/` 3-stage split | 🔴 Open | Biggest single-file drop remaining |
| Merge diagnosis chain into `entity_verifier` or `diagnosis_verification/` | 🔴 Open | ~2.6k LOC parallel cluster |
| Move deterministic `llm_sf_*` modules to `deterministic/` | ✅ Done | `210ca1c`; `sf_state_projection.py` + `sf_unknown_suppression.py` (zero LLM calls) → `deterministic/` |
| Split `entity_verifier/*_content.py`; decouple scoring from prompts | 🔴 Open | |
| Split `llm_target_indicators_single_call.py` LLM shell | 🔴 Open | Projection already in deterministic |
| `generation_selection` monolith → ~300 LOC (prompt builders + row logic still inside) | 🟡 Partial | −1,075 LOC; builders remain |

---

### 4. ExECTv2 runners / reports — CONDITIONAL → **improved**

**Findings:**
- Reports ~2.8× runners LOC; 17 files >500 LOC
- Three allowlisted monoliths at ceiling; `llm_first` failing CI by 3 lines
- Fat runners embedding render/scorecard logic
- Validation-audit clone cluster (3× ~150–200 LOC duplication)
- Report `main()` functions turn reports into CLI apps

**Remediation status:**

| Task | Status | Commit / notes |
|------|--------|----------------|
| Unblock `llm_first` line-count gate (YAML triggers) | ✅ Done | `0f1acb7` |
| Move readout render + ledger from runner to report | ✅ Done | `llm_first_essential_readout.py` |
| `benchmark_constants.py` shared paper F1 targets | ✅ Done | `0f1acb7` |
| Decompose `llm_first` into `reports/llm_first/` package | ✅ Done | `e45bd32`; facade 72 LOC |
| Wire `cross_model_reliability` to `catalog.yaml` | 🔴 Open | Duplicate run tuples |
| `validation_audit_scaffold.py` for robustness/calibration/review-routing | 🔴 Open | |
| Externalize `LAYER_DEFINITIONS` + `COMPONENT_OFF_DEFINITIONS` to YAML | 🔴 Open | `component_ablation_replay` at ceiling |
| Split `cross_model_reliability_analysis.py` (1,554 LOC) | 🔴 Open | |
| Split `component_ablation_replay.py` (1,474 LOC) | 🔴 Open | |
| Ban `main()` in report modules (policy) | ✅ Done | `30c8055`; 14 mains → `reports/cli/`; `test_reports_no_main.py` enforces zero |
| Atomic multi-artifact write helper | 🔴 Open | |
| Thin `run_hybrid_benchmark_overall`, `run_phase7_audit` | 🔴 Open | |

---

### 5. Gan2026 — CONDITIONAL REJECT → **improved (runtime core)**

**Findings:**
- `clinical_assessment_assembly.py` true runtime god-module (2,695 LOC)
- `projection_render.py` misnamed batch policy engine (1,267 LOC)
- `runner.py` architecture switchboard (1,020 LOC)
- `artifact_analysis/` ~31% of package (~24k LOC) — research barnacle layer
- `AgenticStage` ~20% migrated; migrated files still huge
- Dual extraction paths; hybrid bypasses `canonical_stages.extract_stage`
- Probe triple-facade with `component_owner` lies

**Remediation status:**

| Task | Status | Commit / notes |
|------|--------|----------------|
| Split `clinical_assessment_assembly.py` by concern | ✅ Done | `887961e`; orchestrator 139 LOC |
| Parameterize `component_owner` on assembly | ✅ Done | callers pass correct owner |
| Split `projection_render` (semantics / render / gating) | ✅ Done | `4ec51da` |
| Fix projection → LLM probe layer inversion | ✅ Done | calls deterministic assembly |
| Split `burden_normalization.py` below 1k | ✅ Done | `234cd62`; `frequency.py` 706 LOC |
| Route hybrid extraction through `canonical_stages.extract_stage` | 🔴 Open | |
| Collapse probe facades to one module | 🔴 Open | |
| Decompose `runner.py` per-architecture modules | 🔴 Open | 1,103 LOC |
| `agentic/run_driver.py` shared split runner | 🔴 Open | |
| Migrate legacy agentic monoliths via driver | 🔴 Open | 14+ still inline `run_split` |
| Quarantine `artifact_analysis/` from production imports | 🟡 Frozen | `8a8409a`; import gate freezes 14 importers (no new ones); existing importer removal pending |
| State graph: promote to hybrid or demote to experiment-only | 🔴 Open | |
| Split `date_anchor_parsing.py` (789 LOC) if it grows | 🟡 Watch | Under 1k gate |

---

### 6. Frontend + tests + CI — CONDITIONAL REJECT → **CONDITIONAL APPROVE**

**Findings:**
- Gallery 1,005 LOC monolith; inverted `lib` → `app` imports
- `useObservatoryData` god-hook (~640 LOC)
- CI line-count only; no frontend enforcement
- Megatests ungated (2k+ LOC files)
- `componentLadder.test.ts` drift risk

**Remediation status:**

| Task | Status | Commit / notes |
|------|--------|----------------|
| Extract `GanErrorGallery`, `GanExampleExplorer` to `components/gan2026/` | ✅ Done | `529ac51` |
| Decompose gallery page | ✅ Done | 26 LOC shell |
| CI: `npm run build`, `jest`, `lint` | ✅ Done | `.github/workflows/ci.yml` |
| `componentLadder.test.ts` | ✅ Done | 34 tests pass |
| Workbench runtime adapter routing | ✅ Done | (prior `fe85f4e`) |
| Slice `useObservatoryData` → `lib/datasets/adapters/` | 🔴 Open | |
| `createComponentImpactSurface` factory (Gan/ExECTv2 dedup) | 🔴 Open | |
| Extend line-count gate to `frontend/` and `tests/` | 🔴 Open | |
| Split `frontend/lib/types.ts` (~1,352 LOC) | 🔴 Open | |
| Fix `useRunCatalog` double-mounting both datasets | 🔴 Open | |
| Megatest splits (next: `test_gan2026_normalize`, `test_exectv2_deterministic_sf`) | 🔴 Open | |
| Pytest fast subset in CI | 🔴 Open | |
| Pre-commit hook for line-count gates | 🔴 Open | Optional |

---

## Remediation commit index

### Wave A — Post-audit structural fixes (`9d6ac46` … `529ac51`)

| Commit | Summary |
|--------|---------|
| `9d6ac46` | Promote run registry types to `core/` |
| `887961e` | Split Gan clinical assessment assembly; `component_owner` |
| `4ec51da` | Split projection_render into semantics/render/gating |
| `39a34bc` | Extract mention pipeline; invert `two_stage` strategy |
| `0f1acb7` | Unblock llm_first gate; runner boundary; benchmark_constants |
| `529ac51` | Extract Gan gallery surfaces; frontend CI |

### Wave B — Post-audit depth pass (`234cd62` … `45443be`)

| Commit | Summary |
|--------|---------|
| `234cd62` | Split Gan burden normalization below 1k |
| `2d3917a` | Extract Observatory Gan helpers; `core/paths.py` |
| `e45bd32` | Decompose `llm_first` into `reports/llm_first/` |
| `75eefba` | Drug lexicon + `contract/repair.py`; hybrid boundary fix |
| `89f4477` | Unify MLflow sync plans; evict experiment constants |
| `45443be` | Invert all generation_selection strategies |

### Prior waves (reference)

| Wave | Commits | Summary |
|------|---------|---------|
| Wave 1–2 | `157321c` … `c5d80c1` | Claim policy, conventions, verifiers, AgenticStage scaffold |
| Wave 3 | `f4753fd` … `14f046e` | Registry dispatch, YAML kernels, line-count gates, megatest splits |
| Post-W3 | `fe85f4e` | CI workflow stub, scorer fix, workbench adapter |

---

## Open work — prioritized backlog

### P0 — Next sprint (high leverage, bounded)

| ID | Task | Area | Status |
|----|------|------|--------|
| P0-1 | YAML corpora: `generation_selection` decision tables + `qwen_compact` | ExECTv2 LLM | 🔴 Open — −500–800 LOC from 4,134 monolith |
| P0-2 | `pipelines/clinical_findings/` 3-stage package | ExECTv2 LLM | ✅ Done — facade 45 LOC; package extract/verify/finalize/projection/runner (sub-files allowlisted) |
| P0-3 | `validation_audit_scaffold.py` + wire 3 validation reports | Reports | 🔴 Open |
| P0-4 | `cross_model_reliability` → `catalog.yaml` | Reports | ✅ Done — `reports/reliability/` pkg + `catalog.yaml`; facade 153 LOC |
| P0-5 | Route hybrid extraction through `canonical_stages.extract_stage` | Gan2026 | 🔴 Open |
| P0-6 | Extend line-count gate to `tests/**` ≤800 (frozen allowlist) | CI | ✅ Done — `TESTS_ALLOWLIST` in `check_line_counts.py` + gate test |
| P0-7 | Pytest fast subset in CI | CI | ✅ Done — `backend-fast-tests` job in `ci.yml` |

### P1 — Structural (multi-sprint)

| ID | Task | Area | Notes |
|----|------|------|-------|
| P1-1 | Merge SF repair stacks (rules + conventions + target_projection) | ExECTv2 det | ✅ Phases 0–5 complete — `exectv2_sf_repair_stack_consolidation_design_2026-06-26.md` |
| P1-2 | Split `all_entities.py` + thin `lenses.py` | ExECTv2 det | Unblocks convention layer honesty |
| P1-3 | Diagnosis verifier chain → single pipeline | ExECTv2 LLM | ~2.6k LOC parallel story |
| P1-4 | Move `llm_sf_*` deterministic modules out of `llm/` | ExECTv2 LLM | ✅ Done `210ca1c` — `sf_state_projection` + `sf_unknown_suppression` → `deterministic/` |
| P1-5 | Decompose `runner.py` + `agentic/run_driver.py` | Gan2026 | Stop AgenticStage ceremony without shrink |
| P1-6 | Split `cross_model_reliability` + `component_ablation_replay` | Reports | ✅ Done — both → catalog-driven packages (`reliability/` 153, `component_ablation/` 110) |
| P1-7 | Slice `useObservatoryData` to adapters | Frontend | 640 LOC god-hook |
| P1-8 | Observatory Pydantic response models | Observatory | API contract clarity |

### P2 — Quarantine & policy

| ID | Task | Area | Notes |
|----|------|------|-------|
| P2-1 | Freeze new production imports from `artifact_analysis/` | Gan2026 | ✅ Done `8a8409a` — `check_artifact_analysis_imports.py` gate + CI step (14 frozen) |
| P2-2 | Ban `main()` in `reports/` modules | Reports | ✅ Done `30c8055` — 14 mains → `reports/cli/`; `test_reports_no_main.py` |
| P2-3 | Atomic artifact write helper for multi-file runners | Runners | |
| P2-4 | Gold audit dedicated store with atomic upsert | Observatory | |
| P2-5 | State graph promote-or-demote decision | Gan2026 | Architectural limbo |
| P2-6 | Split `frontend/lib/types.ts` by domain | Frontend | 1,352 LOC |
| P2-7 | Pre-commit line-count hook | CI | Optional |

### P3 — Incremental / experimental

| ID | Task | Notes |
|----|------|-------|
| P3-1 | Migrate legacy agentic monoliths one-by-one via `run_driver` | Start with `fresh_evidence_reasoner` (2,016 LOC) |
| P3-2 | `entity_verifier` content → YAML per entity | diagnosis 929, sf 851, med_inv 705 LOC |
| P3-3 | Family-conditioned shared scaffold | ~2.2k LOC cluster |
| P3-4 | `conventions/seizure_frequency.py` table-driven rewrite | Superseded by P1-1 Phase 2 registry migration |
| P3-5 | `createComponentImpactSurface` factory | Frontend laboratory dedup |
| P3-6 | Continue megatest splits | `test_gan2026_normalize`, `test_exectv2_deterministic_sf`, etc. |
| P3-7 | Triage pre-existing red goldens (independent of audit refactors) | `test_exectv2_standard_dictionary::test_normalize_drug_name…` (lamictal→lamotrigine); `test_exectv2_projection_gap_ledger…` (`projection_misses` 522→505, deterministic output drifted in an earlier cycle — confirm 505 is correct before updating golden) |

---

## File-size watchlist (current)

| File | LOC | Status |
|------|----:|--------|
| `llm_only_key_entities_generation_selection.py` | 4,134 | 🟡 Allowlisted; strategies inverted; builders + decision tables remain (P0-1) |
| `llm_only_clinical_findings.py` (facade) | **45** | ✅ Split into `pipelines/clinical_findings/` |
| `llm_only_key_entities_structured.py` | 2,606 | 🟡 Allowlisted; partial YAML |
| `llm_target_indicators_single_call.py` | 2,352 | 🟡 Allowlisted; projection split done |
| `cross_model_reliability_analysis.py` (facade) | **153** | ✅ Split into `reliability/` + catalog.yaml |
| `component_ablation_replay.py` (facade) | **110** | ✅ Split into `component_ablation/` + catalog.yaml |
| `conventions/seizure_frequency.py` | **(deleted)** | ✅ Consolidated into `sf_surface_registry` |
| `runner.py` (Gan2026) | 1,103 | 🟡 Allowlisted (P1-5) |
| `fresh_evidence_reasoner.py` | ~2,016 | 🟡 Legacy agentic |
| `clinical_assessment_assembly.py` | **139** | ✅ Decomposed |
| `gallery/page.tsx` | **26** | ✅ Thin shell |
| `observatory/helpers.py` | **54** | ✅ Paths only |
| `mlflow_registry_sync.py` | **399** | ✅ Under 500 |
| `llm_first_essential_evaluation.py` (facade) | **72** | ✅ Package split |
| `burden/frequency.py` | 706 | 🟡 Watch (next split candidate) |

Gate: `python scripts/check_line_counts.py` — fails on new violations or allowlist ceiling **growth** (shrinks always allowed).

---

## Approval gates (thermo-nuclear bar)

### Satisfied since review remediation

- [x] Core does not import Gan2026 task types for registry
- [x] Single MLflow sync plan type; experiment constants out of core
- [x] Observatory helpers are path/settings only; Gan logic in `observatory/gan2026/`
- [x] Gan assembly + projection_render decomposed; `component_owner` parameterized
- [x] Hybrid imports repair from `contract/`, not `llm_only_single_pass`
- [x] Single drug lexicon in `contract/drug_lexicon.py`
- [x] Assembly does not import reports directly
- [x] `generation_selection` strategies own letter runners (no monolith `_run_*_letter`)
- [x] `llm_first` decomposed; line-count gate passing
- [x] Frontend Gan surfaces in `components/`; gallery thin; CI build/test/lint
- [x] `mention_pipeline` extracted; `entity_verifier` uses shared kernel

### Still required for full APPROVE

- [ ] ExECTv2 LLM **3 monoliths** each <500 LOC — `generation_selection` 4,134, `key_entities_structured` 2,606, `target_indicators_single_call` 2,352 (`clinical_findings` ✅ split)
- [x] SF repair stacks: canonical `sf_surface_registry` (Phases 0–5); shared patterns + unique rule index; legacy `_legacy_impl` split below gate (Sprint 4). **Shim removal** pending one release cycle + import audit.
- [x] Report allowlisted monoliths shrunk with headroom — `cross_model_reliability` 1,554→153 + `reliability/` pkg; `component_ablation_replay` 1,474→110 + `component_ablation/` pkg (all files <500)
- [ ] Gan `runner.py` decomposed; hybrid uses canonical extract
- [~] `artifact_analysis/` quarantined from production paths — import gate **freezes** the 14 current importers (no new ones, `8a8409a`); full removal of existing importers (observatory ×2, `frontend_review.py`, `llm/assessment_probe_signature.py`, 10 `experiments/`) pending
- [x] Test tier line-count gate (`tests/**` ≤800) + fast pytest subset in CI
- [x] Zero report modules with `main()` (policy enforced) — 14 → `reports/cli/`; `test_reports_no_main.py` enforces (`30c8055`)

### Would trigger REJECT

- New 1k+ line modules without decomposition plan / allowlist justification
- New agentic variant without shared `run_driver` or `AgenticStage` path
- New production import from `artifact_analysis/`
- Re-introducing core → task package dependency inversions
- Allowlist ceiling **growth** without explicit justification

---

## Suggested Wave C roadmap

**Sprint 1 (1 week):** P0-1, P0-3, P0-4, P0-6, P0-7 — YAML corpora start, report scaffold, CI depth  
**Sprint 2 (1–2 weeks):** P0-2, P0-5, P1-6 — clinical_findings package, Gan hybrid extract, report monolith headroom  
**Sprint 3 (2–4 weeks):** ~~P1-1 design spike~~ ✅ + P1-2 + P1-1 Phase 0 parity harness — SF registry shadow tests, all_entities split  
**Sprint 4 (ongoing):** P1-5, P2-1, P3-* — Gan runner/agentic, artifact_analysis quarantine, incremental migrations

---

## References

- Review skill: `.claude/skills/thermo-nuclear-code-quality-review/SKILL.md`
- Line-count gate: `scripts/check_line_counts.py`, `tests/test_line_count_gates.py`
- Related plans: `docs/plans/repo_simplification_plan_2026-06-22.md`, `docs/plans/exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md`, `docs/plans/exectv2_sf_repair_stack_consolidation_design_2026-06-26.md` (P1-1)
- Prior context: `PROJECT_STATUS.md`, `CONTEXT.md`
