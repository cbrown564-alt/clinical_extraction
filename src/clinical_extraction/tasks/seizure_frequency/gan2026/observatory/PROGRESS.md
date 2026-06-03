# Observatory Backend — Progress Log

**Last updated:** 2026-06-03

## What was changed

### `/pipeline-families` endpoint — dynamically populated from registry
- **Before:** Hardcoded list of 7 families (2 deterministic aliases + 5 prompt modules). Many families with real run data were missing. The confusing `"Deterministic V1 (alias)"` existed with no registry entries.
- **After:** Reads all unique `pipeline_family` values from `experiments/registry.jsonl`. Each family gets:
  - `value` — the canonical family name
  - `label` — a concise human-readable name (see `FAMILY_SHORT_LABELS` in `api.py`)
  - `executable` — `true` only for `rules_only`
  - `kind` — `"rules_only" | "llm_only" | "hybrid"`
  - `has_replay_artifact` — whether any run has a `.jsonl` file
  - `run_count` — number of runs in the registry
- **Result:** 13 families are now exposed, all with accurate metadata.

### Short labels
Added `FAMILY_SHORT_LABELS` override map so the workbench dropdown shows concise names instead of the long prose `model_role` strings from the registry.

| Family | Label |
|--------|-------|
| `rules_only` | Deterministic V1 |
| `hybrid_rules_candidates_llm_adjudicator` | Hybrid Adjudicator |
| `llm_only_claim_table_selector` | Claim Table |
| `llm_structured_events` | Structured Events |
| `llm_heavy_clinical_frequency_reasoner` | LLM Heavy Reasoner |
| `llm_only_typed_adapter_reasoner` | Typed Adapter |
| `llm_only_typed_operations_reasoner` | Typed Operations |
| `llm_first_direct_extractor` | Direct Extractor |
| `llm_heavy_evidence_selection_with_deterministic_adapters` | LLM Heavy + Det |
| `hybrid_clinical_frequency_state_graph` | State Graph |
| `dspy_final_selection_adjudicator` | DSPY Adjudicator |
| `llm_only_minimal_evidence_selector` | Minimal Evidence |
| `llm_replacement_postprocessing_ablation` | Replacement Ablation |

### `EXECUTABLE_PIPELINES`
Removed the phantom `deterministic_v1` alias. Only `rules_only` is executable via `/run/note` and `/run/ablation`.

### Replay artifact selection (frontend)
- **Before:** `TraceControls.tsx` used `registry.runs.find()` which picked the first matching run. This often selected analysis-only runs with no JSONL artifact.
- **After:** Filters to runs that actually have `.jsonl` artifacts, then picks the one with the most rows (largest corpus).

### Trace adapters — 13 new families supported
Replaced the monolithic `traceAdapter.ts` with a modular `frontend/lib/traceAdapter/` directory:

| File | Families handled |
|------|-----------------|
| `deterministic.ts` | `rules_only` (live) |
| `hybrid.ts` | `hybrid_rules_candidates_llm_adjudicator` |
| `claimTable.ts` | `llm_only_claim_table_selector` |
| `decisionRecord.ts` | `llm_first_direct_extractor`, `dspy_final_selection_adjudicator` |
| `events.ts` | `llm_structured_events`, `llm_heavy_clinical_frequency_reasoner`, `llm_only_typed_adapter_reasoner` |
| `operations.ts` | `llm_only_typed_operations_reasoner` |
| `selectedFact.ts` | `llm_heavy_evidence_selection_with_deterministic_adapters`, `llm_only_simplified_selected_state_reasoner`, `llm_only_sparse_operands_selected_state_reasoner` |
| `stateGraph.ts` | `hybrid_clinical_frequency_state_graph` |
| `parallelHybrid.ts` | `hybrid_parallel_state_candidate_reasoner` |
| `minimal.ts` | `llm_only_minimal_evidence_selector` |
| `ablation.ts` | `llm_replacement_postprocessing_ablation` |

Unified dispatch in `index.ts` via `adaptTrace(row, family, record)`.

### Type safety
Added comprehensive TypeScript artifact interfaces in `frontend/lib/types.ts` for all 13 new families.

### Tests
- Added Jest + ts-jest to the frontend.
- Created `frontend/lib/traceAdapter/__tests__/traceAdapter.test.ts` with 18 tests covering all 16 pipeline families.
- All tests pass.

## Known issues / next steps

1. **Some families may still error on specific rows.** The unit tests use synthetic stubs. Real artifact rows can have null fields, parse errors, or unexpected schema variations that the adapters may not handle gracefully yet. Row-by-row testing against real JSONL data is needed.

2. **`hybrid_parallel_state_candidate_reasoner` is the most complex.** The adapter maps the multi-component structure into the 5-stage trace model, but a custom StageInspector view would better show the parallel component comparison (deterministic vs graph vs LLM candidate vs adjudicator).

3. **State-graph boundary-builder rows have no final label.** The adapter handles this with a placeholder message, but the UI could be more explicit about "diagnostic-only" rows.

4. **Frontend still needs a hard refresh** after backend restarts because React Query caches `pipelineFamilies` with `staleTime: Infinity`.

## Backend restart command

```bash
cd /Users/cobro/code/clinical-extraction
source .venv/bin/activate
PYTHONPATH=src uvicorn clinical_extraction.tasks.seizure_frequency.gan2026.observatory.api:app --reload --port 8000
```
