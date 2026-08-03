# Retention slice: `frontend/public/mock-data/artifacts/` (Decision 0048)

**Date:** 2026-08-02  
**Base commit:** `d507e1bf210875683ff65a5d4f9a09e855954505` (main)  
**Slice branch:** `chore/retention-slice-frontend-mock-artifacts-2026-08-02`  
**Decision:** **KEEP** — active runtime and test loaders block deletion.

## Files examined

Seven tracked JSON files under `frontend/public/mock-data/artifacts/`:

| File | run_id stem | Approx role |
| --- | --- | --- |
| `exectv2_holistic_finding_assembly_v08_dev140.json` | exectv2 dev140 letter replay | ExECT letter-level replay + dev140 row policy |
| `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.json` | partial hybrid dev140 | Saved replay (not currently API-tested) |
| `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140.json` | deepseek reparse dev140 | Saved replay (not currently API-tested) |
| `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140.json` | qwen compact repair dev140 | Saved replay (not currently API-tested) |
| `gan2026_rules_only_v1_baseline_2026-05-31.json` | rules-only baseline | Saved replay (not currently API-tested) |
| `gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05.json` | staged assembly validation750 | **Explicit test fixture** |
| `gan2026_hybrid_rules_candidates_llm_adjudicator_validation50_gpt41mini_v02_live_2026-06-01.json` | hybrid adjudicator validation50 | Saved replay (not currently API-tested) |

## Reference search evidence

### Active loaders (block deletion)

1. **`src/clinical_extraction/trace_explorer/frontend_data.py`**
   - `FrontendDataStore.__init__` glob-loads every `artifacts/*.json` into `self._artifacts` (lines 60–64).
   - `artifact(run_id)` serves row-level replay from mock files when Gan dynamic discovery has no replay path (lines 140–158).
   - `_load_permitted_exect_letter_ids()` scans all `exectv2_*` artifact files to derive the dev140 letter allowlist used by qualified review, gold audit, and semantic-support review queues (lines 487–505). **Store construction fails without at least one exectv2 artifact containing dev140 letters.**

2. **`src/clinical_extraction/trace_explorer/api/routes_frontend.py`**
   - `GET /artifacts/{run_id}` delegates to `FrontendDataStore.artifact()` (lines 195–206).

3. **Frontend TS callers**
   - `frontend/lib/api/index.ts` — `fetchArtifact()` → `/artifacts/${runId}`.
   - `frontend/components/observatory/useObservatoryData.ts` — multiple `fetchArtifact` calls for run comparison.
   - `frontend/components/architect/TraceControls.tsx` — `fetchArtifact(matchingRun.run_id, jsonlPath, 100)` for replay row selection.

4. **Tests**
   - `tests/test_trace_explorer_frontend_api.py`:
     - `test_saved_artifact_replay_is_allowlisted_and_bounded` requests `gan2026_hybrid_multi_component_staged_assembly_v1_validation750_2026-06-05` (lines 274–282).
     - `test_gan_architectures_use_the_same_six_model_comparison_matrix` calls `/artifacts/{run_id}` for replayable Gan runs (lines 227–231).
     - `test_review_queues_and_writes_enforce_development_row_policy` and `test_semantic_support_review_*` depend on `_load_permitted_exect_letter_ids()` derived from exectv2 artifacts.

### Non-blocking mentions (do not require keeping files by themselves)

- `frontend/public/mock-data/registry.json` — lists the same run_ids with `experiments/` artifact paths, not `mock-data/artifacts/` paths.
- `frontend/public/mock-data/exectv2/component-transitions.json` — later removed
  with the unserved ExECT mock slice (2026-08-02 broader triage).
- `frontend/public/mock-data/exectv2/reliability-scorecard.json` — later removed
  with the stale per-dataset reliability scorecard (2026-08-03 cleanup).
- Experiment docs, configs, and archived JSONL under `experiments/` — separate from mock-data artifacts.

### Search commands run

```powershell
rg "mock-data/artifacts" --glob "*.{ts,tsx,js,jsx,py,md}"
rg "artifacts/.*\.json" --glob "*.{ts,tsx,js,jsx,py,md}"
rg "fetchArtifact|/artifacts/" frontend/
rg "_load_permitted_exect_letter_ids|\.artifact\(" src/
rg "gan2026_hybrid_multi_component_staged_assembly" tests/
```

No code path references the literal string `mock-data/artifacts`, but `FrontendDataStore` resolves the directory relative to the mock-data root at runtime.

## Delete-or-keep decision

**KEEP all seven files.**

Deletion would break:

- Trace explorer `/artifacts/{run_id}` replay for saved runs not covered by Gan dynamic discovery.
- ExECT dev140 letter allowlist derivation (qualified review, gold audit, semantic-support review row policy).
- `test_saved_artifact_replay_is_allowlisted_and_bounded` and dependent frontend API tests.

## Owner for future cleanup

| Concern | Owner |
| --- | --- |
| Artifact serving contract | `src/clinical_extraction/trace_explorer/frontend_data.py` + `routes_frontend.py` |
| Frontend replay consumers | `frontend/lib/api/index.ts`, `useObservatoryData.ts`, `TraceControls.tsx` |
| Test fixtures | `tests/test_trace_explorer_frontend_api.py` |
| Regeneration ledger | `docs/REGENERATION.md` (frontend/trace explorer row) |

**Prerequisite for a future delete slice:** refactor `FrontendDataStore` to derive permitted ExECT letter IDs and serve artifact replay from another governed source (e.g. `experiments/` JSONL via dynamic discovery, mirroring Gan validation750), then remove mock artifact copies and update tests.

## Commands run

```powershell
git checkout -b chore/retention-slice-frontend-mock-artifacts-2026-08-02
.venv\Scripts\python.exe -m pytest tests/test_trace_explorer_frontend_api.py -q
cd frontend && npm test -- lib/__tests__/componentLadder.test.ts lib/__tests__/exectv2RunOptions.test.ts
```

## Test results

| Suite | Result |
| --- | --- |
| `tests/test_trace_explorer_frontend_api.py` | 13 passed |
| `frontend/lib/__tests__/componentLadder.test.ts` | passed |
| `frontend/lib/__tests__/exectv2RunOptions.test.ts` | passed |

## Files deleted

None.
