# Thermo-Nuclear Code Quality Audit — Plan & Status

**Date:** 2026-06-26  
**Scope:** Full-repo audit on `main` (not a single PR)  
**Standard:** [thermo-nuclear-code-quality-review](../../.claude/skills/thermo-nuclear-code-quality-review/SKILL.md) — structural simplification, code-judo moves, 1k-line file discipline, boundary cleanliness  
**Overall verdict:** **CONDITIONAL APPROVE** — sound research architecture; consolidation sprint substantially advanced but not finished

---

## Executive summary

The codebase is a **research instrument with a real UI**, not a greenfield product. Architectural intent is strong across both task families (ExECTv2, Gan2026): typed contracts, LLM/deterministic separation, replay-first experimentation, and unusually good test guardrails.

The primary debt is **packaging, not science**:

- Monolith modules (especially ExECTv2 LLM)
- Inverted dependencies (observatory → tasks; Gan runner → artifact_analysis — partially fixed)
- Triplicated policy/helpers (claim boundaries, normalize_phrase, scorecards, DSPy scaffolds)
- Half-landed refactors (v09 dictionary path, frontend dataset kernel)

Two implementation waves addressed the highest-leverage items. **13 commits** on `main` (`157321c` … `c5d80c1`) implement remediation without changing research semantics.

---

## Audit coverage (6 review agents)

| Area | Agent scope | Verdict |
|------|-------------|---------|
| Core + Observatory | `core/`, `observatory/` | CONDITIONAL |
| ExECTv2 assembly/deterministic/hybrid | `assembly/`, `deterministic/`, `hybrid/`, `contract/` | CONDITIONAL REJECT → improved |
| ExECTv2 LLM | `exectv2/llm/` (~33k LOC) | CONDITIONAL REJECT |
| ExECTv2 runners/reports | `runners/`, `reports/` | CONDITIONAL |
| Gan2026 | `tasks/seizure_frequency/gan2026/` (~77k LOC) | CONDITIONAL |
| Frontend + tests + scripts | `frontend/`, `tests/`, `scripts/` | CONDITIONAL APPROVE |

Cross-cutting themes from all six reviews:

1. **Intent vs packaging** — boundaries are documented and mostly honored; files grew faster than abstractions.
2. **Duplication at seams** — policy, parsing, scorecards, verifier scaffolds, medication aliases.
3. **Wrong-layer imports** — shared paths knowing too much about task trees.
4. **File-size crisis** — worst in ExECTv2 LLM; several Gan2026 agentic/LLM modules still >1k lines.
5. **Genuinely good** — `core/evidence`, `run_resume`, `contract/` layers, `schema_repair`, `selected_evidence/`, frontend dataset kernel + `componentLadder`, test discipline.

---

## Wave 1 — Completed (commits `157321c` … `2b1d2b4`)

### P0 — Shared infrastructure

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| Centralize claim-boundary policy | ✅ Done | `157321c` | `core/claim_policy.py`; MLflow, registry, fresh-evidence unified |
| Split `observatory/api.py` into routers | ✅ Done | `157321c` | `routers/{exectv2,gan2026,registry,gold_audit,meta}`; `cached_json_route` factory |
| Gold-audit atomic upsert | ✅ Done | `157321c` | Read-merge-rewrite via `gold_audit_active_sampler` |
| Delete dead observatory helpers | ✅ Done | `157321c` | `_decision_key`, `_llm_family_payload` removed |
| Narrow `PipelineFamily` to executable set | ✅ Done | `157321c` | `Literal["rules_only"]` + comment on registry-backed families |
| ExECTv2 LLM shared kernel (phase 0) | ✅ Done | `984df32` | `llm/shared/{json_parse,dspy_runner,reporting}.py`; 4 modules migrated |

### P1 — ExECTv2 structure

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| Delete legacy v03–v05 diagnosis lens chain | ✅ Done | `bf2bf50` | −751 lines from `lenses.py`; `lens_ops.py`; manifest shims to v09 |
| Data-driven `lens_from_manifest` | ✅ Done | `bf2bf50` | Dictionary lens dict lookup |
| Unify hybrid verify gates | ✅ Done | `bf2bf50` | `verify_route.py` → thin wrapper over `all_entity_gate` |
| ExECTv2 CLI common module | ✅ Done | `f009335` | `exectv2/cli/common.py`; 4 verifier runners ~27 LOC each |
| Shared JSONL loader in runners | ✅ Done | `f009335` | reliability + CUI diagnostic runners |

### P1 — Gan2026 structure

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| Promote pipeline stages out of `artifact_analysis/` | ✅ Done | `1efda40` | `pipeline/stages/` + `pipeline/replay_io.py`; compat shims |
| Extract `AssessmentDraft` contract types | ✅ Done | `1efda40` | `contract/assessment_draft.py` |

### P2 — Frontend

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| Split `api.ts`; explicit mock mode | ✅ Done | `2b1d2b4` | `lib/api/{client,mock,mockMode,index}.ts`; `MockModeBanner` |
| Remove silent fetch→mock fallback | ✅ Done | `2b1d2b4` | Env `NEXT_PUBLIC_MOCK_API=1` or one-time health-check gate |

---

## Wave 2 — Completed (commits `be4ce84` … `c5d80c1`)

### ExECTv2 deterministic + scoring

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| Split `standard_dictionary.py` | ✅ Done | `be4ce84` | `deterministic/conventions/` (6 modules); 35-line facade |
| Split `scoring.py` into package | ✅ Done | `6f3fc3b` | `scoring/{normalize,match,prescription,...}`; single `normalize_phrase` |
| Align `normalization.py` with scoring owner | ✅ Done | `6f3fc3b` | Imports `normalize_phrase` from `scoring.normalize` |

**Residual from conventions split:** `conventions/seizure_frequency.py` still **~1,728 lines** (data-heavy; candidate for YAML externalization).

### Scorecards + bootstrap

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| Unified cluster bootstrap | ✅ Done | `e66e4f8` | `scoring/bootstrap.py` |
| Shared scorecard serialization | ✅ Done | `e66e4f8` | `reports/scorecard_core.py` |
| Refactor 3 report scorecards + phase7 + hybrid benchmark | ✅ Done | `e66e4f8` | Single bootstrap + PRF1/recovery dict helpers |
| Public scoring key helpers | ✅ Done | `e66e4f8` | `concept_keys`, `frequency_state_keys`, etc.; no `_` imports in reports |

**Residual:** `component_ablation_replay.py` (~1,464) and `cross_model_reliability_analysis.py` (~1,422) still embed hardcoded experiment catalogs — externalize to YAML + schema validation.

### ExECTv2 LLM verifiers

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| `entity_verifier` parameterized pipeline | ✅ Partial | `644f153` | SF + investigations migrated |
| Diagnosis verifier migration | ⏳ Stub only | `644f153` | `diagnosis.py` points at legacy (decomposer/reconciler depend on it) |
| Med/inv verifier migration | ⏳ Stub only | `644f153` | `med_inv.py` stub |

### Gan2026 agentic

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| `AgenticStage` protocol + shared scaffold | ✅ Done | `32af32a` | `agentic/stage_protocol.py` (~330 LOC) |
| Migrate `confidence_reviewer` | ✅ Done | `32af32a` | |
| Migrate `boundary_audit_prompt_v2` | ✅ Done | `32af32a` | |
| Document legacy agentic modules | ✅ Done | `32af32a` | `agentic/README.md` |

### Tests + frontend data plane

| Task | Status | Commit | Notes |
|------|--------|--------|-------|
| `tests/helpers/prompt_hygiene.py` | ✅ Done | `9f23514` | `FORBIDDEN_PHRASES`, leak checks |
| `tests/conftest.py` fixtures | ✅ Done | `9f23514` | `repo_root`, `tmp_experiments` |
| Megatest split (proof) | ✅ Partial | `9f23514` | `test_gan2026_pipeline_v1_validation.py` (~37 tests extracted) |
| `DatasetRuntimeAdapter` | ✅ Partial | `c5d80c1` | `lib/datasets/runtime.ts`; observatory route migrated |
| Gallery/workbench on adapter | ⏳ Wiring only | `c5d80c1` | Export hooks added; routes still use local branches |

---

## Wave 3 — Open work (prioritized)

### Tier A — Blockers for “canonical pipeline” status

#### A1. ExECTv2 LLM monolith decomposition

**Problem:** Four files = 47% of `exectv2/llm/` (~15k LOC). Prompt corpora, orchestration, and post-LLM policy are co-located.

| File | Lines | Target decomposition |
|------|------:|-------------------|
| `llm_only_key_entities_generation_selection.py` | ~5,327 | Strategy plugin registry under `llm/pipelines/generation_selection/` |
| `llm_only_key_entities_structured.py` | ~3,652 | `prompts/` + `schemas/structured_events.py` + thin orchestrator |
| `llm_target_indicators_single_call.py` | ~3,371 | Move `_project_*` / `_repair_*` to `deterministic/target_projection/` |
| `llm_only_clinical_findings.py` | ~3,146 | 3-stage pipeline package (`extract`, `verify`, `finalize`) |

**Concrete steps:**

1. Add CI line-count gate (max ~500 LOC per `exectv2/llm/*.py` excluding `prompts/` data).
2. Freeze new `CallStrategy` variants in the monolith; only add via registry.
3. Externalize `_worked_examples()` to `llm/prompts/**/*.yaml` (start with structured + verifiers).
4. Move `structured._*` private imports to public `prompts/key_entities/vocab.py`.
5. Consolidate remaining `_extract_json_object` copies through `llm/shared/json_parse.py`.

**Acceptance:** Top-4 files each <500 LOC; no new duplicate JSON parsers; generation_selection uses dict dispatch not `elif` chains.

#### A2. Split `llm_candidate_set_clinical_assessment_probe.py` (Gan2026)

**Problem:** 3,621-line god module — DSPy + assembly + 15+ `_repair_*` + CLI.

**Target layout (from review J2):**

```
llm/assessment_probe_signature.py   # DSPy + run_split driver
deterministic/clinical_assessment_assembly.py  # assemble + repairs
contract/assessment_draft.py        # ✅ already extracted
llm/assessment_probe.py             # thin wrapper
```

**Acceptance:** No deterministic staging imports from LLM probe module; assembly tests pass.

#### A3. Complete verifier + agentic migrations

| Module | Action |
|--------|--------|
| `llm_diagnosis_verifier.py` | Migrate to `entity_verifier` without breaking decomposer/reconciler imports |
| `llm_med_inv_verifier.py` | Full migration |
| `fresh_evidence_reasoner.py` | Incremental `AgenticStage` migration or freeze as experimental-only |
| `cross_model_structured_event_adjudicator.py` | Same |
| `direct_boundary_critic_rescue.py` | Same |

---

### Tier B — High leverage, lower risk

#### B1. Report monolith externalization

Split and externalize configs for:

- `reports/component_ablation_replay.py` → `component_ablation/{catalog.yaml,compute.py,render.py}`
- `reports/cross_model_reliability_analysis.py` → same pattern

Move `run_llm_first_essential_evaluation.render_markdown` into report module (fat runner cleanup).

**Acceptance:** Experiment path changes are config diffs, not Python edits.

#### B2. Conventions data externalization

- `conventions/seizure_frequency.py` (~1,728 lines) → `conventions/data/seizure_frequency.yaml` + thin query API
- `benchmark_projection.py` lexicon → YAML candidate

#### B3. Frontend data-plane completion

| Route | Current | Target |
|-------|---------|--------|
| `app/observatory/page.tsx` | ✅ `getRuntimeAdapter` | — |
| `app/gallery/page.tsx` | `if (exectv2)` branch | `adapter.surfaces.ExampleExplorer` |
| `app/workbench/page.tsx` | dual store legacy | single architect store; delete `useConfigStore` dead path |
| `app/laboratory/page.tsx` | branch | adapter surfaces |
| `useObservatoryData` (~640 LOC) | inline artifact fetch ×3 | `useArtifactSummaries` shared hook |

**Acceptance:** No route-level `if (dataset === "exectv2")` for surface dispatch; unified run-selection storage key.

#### B4. Test suite consolidation

| Task | Detail |
|------|--------|
| Expand `tests/helpers/` | Shared letter fixtures, mock registry builders, JSONL adapters |
| Megatest splits | `test_exectv2_target_indicators_single_call.py` (~3.2k), `test_gan2026_clinical_assessment_projection_render.py` (~3.3k), remaining `pipeline_v1` clusters |
| Frontend tests | `extractRowScore` golden rows; `useExectv2Selection` URL/localStorage; fix 4 failing `componentLadder.test.ts` mock drift |

---

### Tier C — Architecture completion

#### C1. Gan2026 state graph integration

`state_graph/` is well-designed but off the production path. Wire optional `state_graph.extract_stage()` behind `deterministic_canonical_stages` seam; `SourceType = "state_graph_node"` already exists in contract.

#### C2. Unified structured-event repair registry

Move inline repairs from `hybrid_structured_events.parse_structured_json()` into shared registry keyed by `StructuredRepairConfig` — same registry `component_stage_ladder` documents.

#### C3. traceAdapter registry (frontend)

Replace string family sets in `traceAdapter/index.ts` with declarative map (possibly generated from backend pipeline family metadata).

#### C4. URL sync primitive (frontend)

Collapse five `use*UrlSync` copies in `hooks.ts` (~540 LOC) into one `useUrlState` primitive.

#### C5. Observatory service facades

Observatory routers should depend on stable task **facades** (cached report builders, registry readers), not deep imports from rule clusters and pipeline implementations. Incrementally introduce `tasks/*/frontend_review.py`-style facades per domain.

---

## File-size watchlist (post-remediation)

| File | Lines | Status |
|------|------:|--------|
| `llm_only_key_entities_generation_selection.py` | ~5,327 | 🔴 Blocker |
| `llm_only_key_entities_structured.py` | ~3,652 | 🔴 Blocker |
| `llm_candidate_set_clinical_assessment_probe.py` | ~3,621 | 🔴 Blocker |
| `llm_target_indicators_single_call.py` | ~3,371 | 🔴 Blocker |
| `conventions/seizure_frequency.py` | ~1,728 | 🟡 Watch |
| `assembly/lenses.py` | ~1,179 | 🟡 Improved (was 1,930) |
| `fresh_evidence_reasoner.py` | ~2,026 | 🟡 Legacy agentic |
| `component_ablation_replay.py` | ~1,464 | 🟡 Externalize catalog |
| `frontend/lib/types.ts` | ~1,233 | 🟡 Split by domain |
| `observatory/api.py` | thin | ✅ Fixed |

---

## Suggested execution order (Wave 3)

```
Sprint 1 (delete complexity)
├── Complete diagnosis + med_inv verifier migration
├── Move target_indicators projection policy → deterministic/
└── Delete dead frontend workbench config store

Sprint 2 (kernels)
├── generation_selection strategy registry (freeze monolith)
├── Externalize structured worked examples → YAML
└── component_ablation catalog → YAML

Sprint 3 (boundaries)
├── assessment_probe god-module split
├── Migrate 2 more agentic stages
└── Gallery/laboratory → DatasetRuntimeAdapter

Sprint 4 (hardening)
├── CI line-count gates
├── Megatest splits (2–3 more files)
├── state_graph optional producer
└── observatory task facades
```

---

## Approval gates (thermo-nuclear bar)

**Ready for APPROVE when:**

- [ ] No production Python file >1,000 lines without documented justification
- [ ] No triplicated claim-boundary / normalize / bootstrap logic
- [ ] Observatory and Gan runner import facades, not analysis monoliths
- [ ] ExECTv2 LLM top-4 monoliths decomposed
- [ ] Frontend: no silent mock mode; all explorer routes on runtime adapter
- [ ] Reports do not import `scoring._*` private symbols

**Would trigger REJECT if:**

- New 1k+ line modules added without decomposition plan
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

---

## References

- Review skill: `.claude/skills/thermo-nuclear-code-quality-review/SKILL.md`
- Related plans: `docs/plans/repo_simplification_plan_2026-06-22.md`, `docs/plans/exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md`
- Prior simplification context: `PROJECT_STATUS.md`, `CONTEXT.md`
