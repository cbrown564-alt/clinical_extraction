> **Status: ACTIVE, PRIOR VERDICT SUPERSEDED** — the 2026-07-13 re-audit found
> 26 full-suite failures, 1,224 repository-wide Ruff errors, 341 mypy errors,
> broad line-count allowlists, closed candidate code in the installed package,
> and broken artifact catalogs. See [`ACTIVE_ROADMAP.md`](ACTIVE_ROADMAP.md) P0.

# Thermo-Nuclear Code Quality Audit — Plan & Status

**Date:** 2026-06-26  
**Last updated:** 2026-06-27 (Wave C Sprint 7 complete; 8 commits `37046bd` … `3a39380`)  
**Scope:** Full-repo audit on `main` (not a single PR)  
**Standard:** [thermo-nuclear-code-quality-review](../../.claude/skills/thermo-nuclear-code-quality-review/SKILL.md) — structural simplification, code-judo moves, 1k-line file discipline, boundary cleanliness  
**Historical verdict:** **SUPERSEDED.** The earlier `APPROVE` assessment did not
survive the 2026-07-13 repository-wide checks. Current work is deletion-led
simplification, followed by full-suite, Ruff, and mypy repair on the reduced tree.

---

## Executive summary

The codebase is a **research instrument with a real UI**. Architectural intent is strong across both task families (ExECTv2, Gan2026): typed contracts, LLM/deterministic separation, replay-first experimentation, and unusually good test guardrails.

**Historical context:** Wave 3 (commits `f4753fd` … `14f046e`) delivered verifier pipelines, YAML kernels, frontend adapter kernel, and line-count gates. That work froze debt but did not finish monolith decomposition.

**This review cycle** ran six thermo-nuclear audit agents across the full repo, then executed remediation in Waves A–B (12 commits, `9d6ac46` … `45443be`) and **Wave C** (28 commits, `cac60f3` … `83b6ec1`). The audits were uniformly **CONDITIONAL REJECT** at the area level; remediation addressed the highest-leverage structural blockers.

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
| Wave C — LLM facades | Top-4 monoliths 2.3k–4.1k LOC each | Thin facades (45–94 LOC) + `pipelines/*` packages; YAML corpora for generation_selection |
| Wave C — Reports | 3 allowlisted monoliths at ceiling; validation clone cluster | `reliability/` + `component_ablation/` packages; `validation_audit_scaffold.py`; reliability goldens aligned |
| Wave C — Deterministic | `all_entities.py` 1,455 LOC; 3 SF repair stacks | `all_entities/` per-entity package; `sf_surface_registry` Phases 0–5 |
| Wave C — CI | Line-count on `src/` only | Tests tier ≤800 (21 allowlist); `backend-fast-tests` job (~145 tests) |
| Wave C-S6 — Gan runtime | `runner.py` 1,094 LOC switchboard | 108 LOC facade + `runners/` package + `agentic/run_driver.py` |
| Wave C-S6 — Quarantine | 14 frozen `artifact_analysis/` importers | 0 production importers; allowlist empty (`21da49a`) |
| Wave C-S6 — Diagnosis LLM | ~2.9k LOC parallel `llm_diagnosis_*` cluster | `pipelines/diagnosis_verification/` + thin facades (`6718200`) |
| Wave C-S6 — LLM submodules | `extract.py` 1,241; `prompt_builders.py` 1,282 | 50 / 71 LOC facades; YAML corpora + strategy modules (`da6a34f`) |
| Wave C-S6 — Deterministic | `lenses.py` 1,180 LOC monolith | `assembly/lenses/` per-entity package; `contract/text.py` (`3717dc5`) |
| Wave C-S6 — Frontend | `useObservatoryData` 641; `types.ts` 1,353 | Hook 270 LOC + adapters; domain type modules (`8ce784a`) |

**Primary debt remaining:** P3-2 entity-verifier / diagnosis-verifier YAML corpora; P3-1 agentic monolith migration onto `run_driver`; P1-8/P2-4 Observatory API contracts + gold audit store; allowlisted `structured/prompt_builders` (815) and `generation_selection/parsing` (640); pre-existing test drift (`component_owner`, score-ladder golden, `REPO_ROOT` on `component_ablation_replay`).

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
| Add Pydantic response models for high-traffic routes | ✅ Done | `37046bd`; `observatory/responses.py` |
| Gold audit atomic store + thin router | ✅ Done | `37046bd`; `gold_audit_store.py` |
| `run_ablation` async/job pattern or dev-only guard | 🔴 Open | |
| Consolidate split policy (`claim_policy` vs `mlflow_tracking` substring rules) | 🔴 Open | |

---

### 2. ExECTv2 deterministic / hybrid — CONDITIONAL REJECT → **improved**

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
| Collapse SF repair stacks into data-driven surface registry | ✅ Done | Phases 0–5 — `exectv2_sf_repair_stack_consolidation_design_2026-06-26.md`; `sf_surface_registry/`; shims removed `0f326aa` |
| Split `all_entities.py` per-entity modules | ✅ Done | `7d50904`; `deterministic/all_entities/` package; facade 25 LOC |
| Refactor `lenses.py` to thin convention adapters | ✅ Done | `3717dc5`; `assembly/lenses/` package; max `diagnosis.py` 397 LOC |
| Merge or relocate `target_projection/` (LLM-only consumer) | ✅ Done | Consolidated into `sf_surface_registry` Phase 3; legacy path deprecated |
| `normalize_phrase` → `contract/text.py` | ✅ Done | `3717dc5`; scoring re-export shims preserved |
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
| Invert all `generation_selection` letter runners into strategies | ✅ Done | `45443be`; then package split `f33d23d` — facade 94 LOC |
| Externalize prompt corpora to YAML (decision tables, verifier content, qwen_compact) | 🟡 Partial | P0-1 `cac60f3`: dedup decision tables + qwen_compact examples; entity_verifier content remains |
| `pipelines/clinical_findings/` 3-stage split | ✅ Done | `d8dc507`; facade 45 LOC; stages allowlisted |
| Merge diagnosis chain into `entity_verifier` or `diagnosis_verification/` | ✅ Done | `6718200`; `pipelines/diagnosis_verification/` + thin facades |
| Move deterministic `llm_sf_*` modules to `deterministic/` | ✅ Done | `210ca1c`; `sf_state_projection.py` + `sf_unknown_suppression.py` |
| Split `entity_verifier/*_content.py`; decouple scoring from prompts | ✅ Done | `11f2fbc` P3-2 — YAML corpora; med_inv 539 LOC allowlisted |
| Split `llm_target_indicators_single_call.py` LLM shell | ✅ Done | Facade 80 LOC + `pipelines/target_indicators_single_call/` |
| `generation_selection` + `structured` package splits | ✅ Done | `f33d23d`, `83b6ec1`; facades 94 / 85 LOC; submodules allowlisted |

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
| Wire `cross_model_reliability` to `catalog.yaml` | ✅ Done | `453bb2d`; extended `8839f88` into full package split |
| `validation_audit_scaffold.py` for robustness/calibration/review-routing | ✅ Done | `0cbb93a`; −92 net LOC across 4 files |
| Externalize `LAYER_DEFINITIONS` + `COMPONENT_OFF_DEFINITIONS` to YAML | ✅ Done | `8e2e96f`; `definitions.yaml` + Pydantic loader |
| Split `cross_model_reliability_analysis.py` (1,554 LOC) | ✅ Done | `8839f88` + `9cf1117`; facade 153 LOC |
| Split `component_ablation_replay.py` (1,474 LOC) | ✅ Done | `8839f88`; facade 99 LOC |
| Ban `main()` in report modules (policy) | ✅ Done | `30c8055`; 14 mains → `reports/cli/`; `test_reports_no_main.py` |
| Reliability golden tests + frontend mock JSON | ✅ Done | `51d754d`; ECE/review-burden aligned to live builder |
| Atomic multi-artifact write helper | ✅ Done | `b148fda`; `runners/artifact_io.py` |
| Thin `run_hybrid_benchmark_overall`, `run_phase7_audit` | ✅ Done | `b148fda`; report modules extracted |

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
| Route hybrid extraction through `canonical_stages.extract_stage` | ✅ Done | `ceb8178`; hybrid honors `use_state_graph_extract` |
| Collapse probe facades to one module | 🔴 Open | |
| Decompose `runner.py` per-architecture modules | ✅ Done | `befbfd7`; 108 LOC facade + `runners/` |
| `agentic/run_driver.py` shared split runner | ✅ Done | `befbfd7`; 191 LOC scaffold — monolith migration pending (P3-1) |
| Migrate legacy agentic monoliths via driver | 🟡 Partial | `83829de`; `fresh_evidence_reasoner` migrated; 12 remain |
| Quarantine `artifact_analysis/` from production imports | ✅ Done | `21da49a`; 0 importers (was 14 frozen at `8a8409a`) |
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
| Slice `useObservatoryData` → `lib/datasets/adapters/` | ✅ Done | `8ce784a`; hook 270 LOC + 3 adapters |
| `createComponentImpactSurface` factory (Gan/ExECTv2 dedup) | ✅ Done | `8ce784a`; `createComponentImpactSurface.tsx` |
| Extend line-count gate to `tests/**` ≤800 | ✅ Done | `1933397`; 21 megatest allowlist |
| Extend line-count gate to `frontend/` | ✅ Done | `86083a6`; 600 LOC tier |
| Pytest fast subset in CI | ✅ Done | `27d579b`; `backend-fast-tests` job (~145 tests) |
| Pre-commit hook for line-count gates | ✅ Done | `86083a6`; `.pre-commit-config.yaml` (opt-in) |

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

### Wave C — Sprint 1 (`cac60f3` … `a5e79b7`)

| Commit | Summary |
|--------|---------|
| `cac60f3` | Externalize generation_selection YAML corpora (P0-1) |
| `453bb2d` | Reliability run catalog.yaml (P0-4) |
| `1933397` | Tests tier line-count gate (P0-6) |
| `27d579b` | Backend-fast-tests CI job (P0-7) |
| `0cbb93a` | Validation audit scaffold + 3 report refactors (P0-3) |
| `a5e79b7` | Plan: Sprint 1 status |

### Wave C — Sprint 2 (`d8dc507` … `9cf1117`)

| Commit | Summary |
|--------|---------|
| `d8dc507` | Clinical findings 3-stage package (P0-2) |
| `ceb8178` | Hybrid → `canonical_stages.extract_stage` (P0-5) |
| `8839f88` | Split cross_model + component_ablation report monoliths (P1-6) |
| `9cf1117` | Re-export reliability helpers on facade |
| `51d754d` | Align reliability golden tests + frontend mock JSON |

### Wave C — Sprint 3 (`f56c299` … `7d50904`)

| Commit | Summary |
|--------|---------|
| `f56c299` | P1-1 SF repair stack design spike |
| `7d50904` | Split `all_entities` per-entity package (P1-2) |

### Wave C — Sprint 4 (`9a89200` … `ebf4246`)

| Commit | Summary |
|--------|---------|
| `9a89200` … `0f326aa` | SF `sf_surface_registry` Phases 0–5; shim removal |
| `4948262` | Remove stale line-count allowlist entries |
| `ebf4246` | Reconcile audit plan to repo reality |

### Wave C — Sprint 5 (`210ca1c` … `83b6ec1`)

| Commit | Summary |
|--------|---------|
| `210ca1c` | Move `llm_sf_*` to `deterministic/` (P1-4) |
| `8a8409a` | `artifact_analysis/` import quarantine gate (P2-1) |
| `30c8055` | Ban `main()` in reports; move to `reports/cli/` (P2-2) |
| `f33d23d` | Decompose generation_selection into package + facade |
| `83b6ec1` | Decompose structured key-entities into package + facade |

### Wave C — Sprint 7 (`37046bd` … `3a39380`)

| Commit | Summary |
|--------|---------|
| `37046bd` | Observatory Pydantic responses + gold audit store (P1-8, P2-4) |
| `11f2fbc` | Entity verifier YAML corpora (P3-2) |
| `4716fcb` | Structured prompt_builders + generation_selection parsing splits |
| `83829de` | `fresh_evidence_reasoner` → `run_driver` (P3-1 first) |
| `b148fda` | Atomic artifact writes + thin runners (P2-3) |
| `86083a6` | Frontend line-count gate + pre-commit hook (P2-7) |
| `3a39380` | Golden triage + drug lookup + component_owner (P3-7) |

### Wave C — Sprint 6 (`befbfd7` … `dd7c565`)

| Commit | Summary |
|--------|---------|
| `befbfd7` | Decompose Gan2026 runner + `agentic/run_driver.py` (P1-5) |
| `21da49a` | Remove all production `artifact_analysis/` importers (P2-1 complete) |
| `6718200` | Unify diagnosis chain under `pipelines/diagnosis_verification/` (P1-3) |
| `da6a34f` | Shrink clinical_findings extract + generation_selection prompt_builders |
| `3717dc5` | Split `assembly/lenses/` + `contract/text.py` (P1-2 complete) |
| `8e2e96f` | Externalize component_ablation definitions to YAML |
| `8ce784a` | Frontend adapters + types split + component-impact factory (P1-7, P2-6, P3-5) |
| `dd7c565` | Update line-count allowlists for Sprint 6 decompositions |

### Prior waves (reference)

| Wave | Commits | Summary |
|------|---------|---------|
| Wave 1–2 | `157321c` … `c5d80c1` | Claim policy, conventions, verifiers, AgenticStage scaffold |
| Wave 3 | `f4753fd` … `14f046e` | Registry dispatch, YAML kernels, line-count gates, megatest splits |
| Post-W3 | `fe85f4e` | CI workflow stub, scorer fix, workbench adapter |

---

## Open work — prioritized backlog

### P0 — Wave C Sprint 1–2 (complete)

| ID | Task | Area | Status |
|----|------|------|--------|
| P0-1 | YAML corpora: `generation_selection` decision tables + `qwen_compact` | ExECTv2 LLM | ✅ Done `cac60f3` — −716 LOC Python; YAML under `prompts/key_entities/` |
| P0-2 | `pipelines/clinical_findings/` 3-stage package | ExECTv2 LLM | ✅ Done `d8dc507` — facade 45 LOC |
| P0-3 | `validation_audit_scaffold.py` + wire 3 validation reports | Reports | ✅ Done `0cbb93a` |
| P0-4 | `cross_model_reliability` → `catalog.yaml` | Reports | ✅ Done `453bb2d` + `8839f88` |
| P0-5 | Route hybrid extraction through `canonical_stages.extract_stage` | Gan2026 | ✅ Done `ceb8178` |
| P0-6 | Extend line-count gate to `tests/**` ≤800 (frozen allowlist) | CI | ✅ Done `1933397` |
| P0-7 | Pytest fast subset in CI | CI | ✅ Done `27d579b` |

### P1 — Structural (multi-sprint)

| ID | Task | Area | Notes |
|----|------|------|-------|
| P1-1 | Merge SF repair stacks (rules + conventions + target_projection) | ExECTv2 det | ✅ Phases 0–5 complete — `exectv2_sf_repair_stack_consolidation_design_2026-06-26.md` |
| P1-2 | Split `all_entities.py` + thin `lenses.py` | ExECTv2 det | ✅ Done `3717dc5` — `all_entities/` + `assembly/lenses/` |
| P1-3 | Diagnosis verifier chain → single pipeline | ExECTv2 LLM | ✅ Done `6718200` — `pipelines/diagnosis_verification/` |
| P1-4 | Move `llm_sf_*` deterministic modules out of `llm/` | ExECTv2 LLM | ✅ Done `210ca1c` — `sf_state_projection` + `sf_unknown_suppression` → `deterministic/` |
| P1-5 | Decompose `runner.py` + `agentic/run_driver.py` | Gan2026 | ✅ Done `befbfd7` — facade 108 LOC; P3-1 migration open |
| P1-6 | Split `cross_model_reliability` + `component_ablation_replay` | Reports | ✅ Done `8839f88` — facades 153 / 99 LOC |
| P1-7 | Slice `useObservatoryData` to adapters | Frontend | ✅ Done `8ce784a` — hook 270 LOC |
| P1-8 | Observatory Pydantic response models | Observatory | ✅ Done `37046bd` |

### P2 — Quarantine & policy

| ID | Task | Area | Notes |
|----|------|------|-------|
| P2-1 | Freeze new production imports from `artifact_analysis/` | Gan2026 | ✅ Done `21da49a` — 0 importers (gate empty) |
| P2-2 | Ban `main()` in `reports/` modules | Reports | ✅ Done `30c8055` — 14 mains → `reports/cli/`; `test_reports_no_main.py` |
| P2-3 | Atomic artifact write helper for multi-file runners | Runners | ✅ Done `b148fda` |
| P2-4 | Gold audit dedicated store with atomic upsert | Observatory | ✅ Done `37046bd` |
| P2-5 | State graph promote-or-demote decision | Gan2026 | Architectural limbo |
| P2-6 | Split `frontend/lib/types.ts` by domain | Frontend | ✅ Done `8ce784a` — domain modules under `lib/types/` |
| P2-7 | Pre-commit line-count hook | CI | ✅ Done `86083a6` (opt-in) |

### P3 — Incremental / experimental

| ID | Task | Notes |
|----|------|-------|
| P3-1 | Migrate legacy agentic monoliths one-by-one via `run_driver` | ✅ Done `83829de` for `fresh_evidence_reasoner`; 12 remain |
| P3-2 | `entity_verifier` content → YAML per entity | ✅ Done `11f2fbc` — diagnosis/sf/med_inv corpora |
| P3-3 | Family-conditioned shared scaffold | ~2.2k LOC cluster |
| P3-4 | `conventions/seizure_frequency.py` table-driven rewrite | Superseded by P1-1 Phase 2 registry migration |
| P3-5 | `createComponentImpactSurface` factory | Frontend laboratory dedup | ✅ Done `8ce784a` |
| P3-6 | Continue megatest splits | `test_gan2026_normalize`, `test_exectv2_deterministic_sf`, etc. |
| P3-7 | Triage pre-existing red goldens | ✅ Done `3a39380` — drug lookup, component_owner, assembly/projection goldens |

---

## File-size watchlist (current)

| File / package | LOC | Status |
|----------------|----:|--------|
| `llm_only_key_entities_generation_selection.py` (facade) | **94** | ✅ → `pipelines/key_entities_generation_selection/` |
| `…/prompt_builders.py` (generation_selection) | **71** | ✅ Decomposed S6; strategy modules ≤446 LOC |
| `…/parsing.py` | 640 | 🟡 Allowlisted |
| `llm_only_key_entities_structured.py` (facade) | **85** | ✅ → `pipelines/key_entities_structured/` |
| `…/prompt_builders.py` (structured) | 815 | 🟡 Allowlisted |
| `llm_only_clinical_findings.py` (facade) | **45** | ✅ → `pipelines/clinical_findings/` |
| `…/extract.py` | **50** | ✅ Decomposed S6; corpus in YAML |
| Diagnosis verifier runtime | Removed 2026-07-14 | Closed candidate; retained model-transfer helpers now live in `llm/diagnosis_decomposer.py` |
| `llm_target_indicators_single_call.py` (facade) | **80** | ✅ → `pipelines/target_indicators_single_call/` |
| `cross_model_reliability_analysis.py` (facade) | **153** | ✅ → `reports/reliability/` |
| `component_ablation_replay.py` (facade) | **99** | ✅ → `reports/component_ablation/` |
| `deterministic/all_entities/` (package) | 1,624 | ✅ Split; max `prescription.py` 396 |
| `assembly/lenses/` (package) | 1,366 | ✅ Split; max `diagnosis.py` 397 |
| `runner.py` (Gan2026) | **108** | ✅ Decomposed S6 → `runners/` |
| `fresh_evidence_reasoner.py` | ~2,016 | 🟡 Legacy agentic |
| `clinical_assessment_assembly.py` | **139** | ✅ Decomposed |
| `gallery/page.tsx` | **26** | ✅ Thin shell |
| `observatory/helpers.py` | **54** | ✅ Paths only |
| `mlflow_registry_sync.py` | **399** | ✅ Under 500 |
| `llm_first_essential_evaluation.py` (facade) | **72** | ✅ Package split |
| `burden/frequency.py` | 706 | 🟡 Watch |

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
- [x] Gan hybrid uses `canonical_stages.extract_stage` (`ceb8178`)
- [x] Validation audit scaffold deduplicates 3 reliability reports (`0cbb93a`)
- [x] SF repair consolidated into `sf_surface_registry` (Phases 0–5)

### Still required for full APPROVE

- [x] ExECTv2 LLM top-4 **facades** each <500 LOC (94 / 85 / 45 / 80); package submodules >500 remain allowlisted
- [x] SF repair stacks consolidated into `sf_surface_registry` (Phases 0–5; shims removed `0f326aa`)
- [x] Report monolith facades shrunk — `cross_model_reliability` 153 + `reliability/` pkg; `component_ablation_replay` 99 + `component_ablation/` pkg
- [x] Gan `runner.py` decomposed (`befbfd7`); hybrid extract ✅ `ceb8178`
- [x] `artifact_analysis/` quarantined — 0 production importers (`21da49a`)
- [x] Test tier line-count gate + fast pytest subset in CI
- [x] Zero report modules with `main()` (`30c8055`)
- [x] Reliability validation goldens aligned to live builder (`51d754d`)

### Would trigger REJECT

- New 1k+ line modules without decomposition plan / allowlist justification
- New agentic variant without shared `run_driver` or `AgenticStage` path
- New production import from `artifact_analysis/`
- Re-introducing core → task package dependency inversions
- Allowlist ceiling **growth** without explicit justification

---

## Suggested Wave C roadmap

**Sprint 1 ✅** — P0-1, P0-3, P0-4, P0-6, P0-7  
**Sprint 2 ✅** — P0-2, P0-5, P1-6  
**Sprint 3 ✅** — P1-1 design spike (`f56c299`); P1-2 all_entities split (`7d50904`)  
**Sprint 4 ✅** — SF `sf_surface_registry` Phases 0–5 (`9a89200` … `0f326aa`); plan reconciliation (`ebf4246`)  
**Sprint 5 ✅** — P1-4, P2-1, P2-2; generation_selection + structured package splits; reliability goldens (`51d754d`)  

**Sprint 6 ✅** — P1-2 lenses, P1-3 diagnosis, P1-5 runner, P1-7 frontend hook, P2-1 importer removal, P2-6 types, P3-5 factory; LLM submodule shrink; component_ablation YAML (`befbfd7` … `dd7c565`)

**Sprint 7 ✅** — P1-8, P2-3, P2-4, P2-7, P3-1 (first monolith), P3-2, P3-7; structured/parsing submodule shrink; frontend line-count gate (`37046bd` … `3a39380`)

**Sprint 8 (next):** P3-1 remaining 12 agentic monoliths; P2-5 state graph decision; typed assembly row models; megatest splits (P3-6); collapse probe facades

---

## References

- Review skill: `.claude/skills/thermo-nuclear-code-quality-review/SKILL.md`
- Line-count gate: `scripts/check_line_counts.py`, `tests/test_line_count_gates.py`
- Related plans: `docs/plans/repo_simplification_plan_2026-06-22.md`, `docs/plans/exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md`, `docs/plans/exectv2_sf_repair_stack_consolidation_design_2026-06-26.md` (P1-1)
- Prior context: `PROJECT_STATUS.md`, `CONTEXT.md`
