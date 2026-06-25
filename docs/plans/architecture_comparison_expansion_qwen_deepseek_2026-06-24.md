# Architecture Comparison Expansion — Qwen/DeepSeek + Registry-Driven Labels

Date: 2026-06-24
Status: active follow-up, not yet started; sequenced after paper/results and same-core full-200 predeclaration work
Scope: Gan 2026 **and** ExECTv2 — the Example Explorer pipeline/architecture
dropdown and the Component Impact comparison.

Rationalisation status, 2026-06-25: still active, but below the immediate
paper/results and same-core full-200-predeclaration work. Implement as the
registry-driven run-surfacing phase in
`docs/plans/recent_plan_rationalisation_2026-06-25.md`.

## Why this exists

On 2026-06-24 the Gan Example Explorer dropdown was trimmed to the three
canonical architectures so it matches the Component Impact comparison
(deterministic / hybrid / LLM-only). That trim is deliberately minimal: it
hardcodes the three families in `CANONICAL_PIPELINE_FAMILIES`
(`src/clinical_extraction/observatory/api.py`) and surfaces one entry per
*pipeline family*. Two things are left undone, captured here:

1. **Per-model comparators.** Qwen and DeepSeek runs of the same architectures
   already exist in the registry but are invisible — they collapse into the
   single `llm_only_canonical_pipeline` family entry, and the Explorer's
   replay-row picker chooses *whichever same-family run has the most rows*
   (a gpt-4.1-mini vs deepseek tie at 750 rows is currently broken only by
   registry order). We want them surfaced as distinct, labelled comparators.
2. **Registry-driven labelling.** Display labels and the control/diagnostic
   decision role are hardcoded in the API (Gan) and in mock JSON. They should
   live on the registry record so the Explorer dropdown and the Component
   Impact comparison read one source of truth and never drift.

ExECTv2 is already most of the way there: its runs surface
(`/exectv2/runs`, `mock-data/exectv2/runs.json`) lists v08 control, v09 hybrid,
**DeepSeek v0.9.16**, and **Qwen v0.9.22** as distinct runs, each with a
`label`, `model`, and `decision`. The goal is to bring Gan up to that model and
make both registry-driven.

## Current state (2026-06-24)

| Surface | Gan | ExECTv2 |
| --- | --- | --- |
| Explorer dropdown source | `/pipeline-families` → 3 canonical families (hardcoded) | `/exectv2/runs` → per-run list |
| Per-model comparators surfaced | no (qwen/deepseek hidden in registry) | yes (deepseek + qwen runs) |
| Label source | hardcoded in `CANONICAL_PIPELINE_FAMILIES` + mock | per-run `label` field |
| Decision role (control/diagnostic) | only on Component Impact payload | on both runs + ablation |
| Replay-run selection | "most rows in family" (ambiguous on ties) | explicit `run_id` |

Registry runs that exist today but are not surfaced as Gan comparators
(examples):

- `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08`
- (DeepSeek/Qwen hybrid + deterministic variants as they are produced)

## Target design

### 1. Registry is the source of truth

Add optional display/curation fields to the Gan run-registry record
(`src/clinical_extraction/tasks/seizure_frequency/gan2026/experiments/run_registry.py`)
and mirror the concept in the ExECTv2 run index:

| Field | Meaning |
| --- | --- |
| `surface_as_architecture: bool` | surface this run in the Explorer dropdown + Component Impact |
| `display_label: str` | the human label both surfaces show (e.g. "LLM-only · GPT-4.1-mini") |
| `architecture_family: str` | the canonical family it belongs to (deterministic / hybrid / llm_only) |
| `decision: control \| diagnostic \| ...` | already present; reused as the comparison role |

`model` is already on the record and disambiguates gpt-4.1-mini / deepseek /
qwen. The label convention should be **`<architecture> · <model>`** so the
dropdown reads, e.g.:

```
Deterministic canonical
Hybrid (LLM extract) · GPT-4.1-mini
Hybrid (LLM extract) · DeepSeek
Hybrid (LLM extract) · Qwen
LLM-only (rules in prompt) · GPT-4.1-mini
LLM-only (rules in prompt) · DeepSeek
LLM-only (rules in prompt) · Qwen
```

### 2. Backend: surface runs, not just families

- `_build_pipeline_families` (Gan) becomes a *run-surfacing* builder: it reads
  `surface_as_architecture` runs from the registry, emits one dropdown entry per
  run with `value = run_id` (not family), `label = display_label`,
  `kind = architecture_family`, plus `model`/`decision`. The hardcoded
  `CANONICAL_PIPELINE_FAMILIES` dict is replaced by registry curation.
- Replace the "most rows in family" replay picker with explicit `run_id`
  selection (the dropdown value *is* the run), removing the gpt-4.1-mini/deepseek
  tie ambiguity in `TraceControls`.
- Keep the executable deterministic line (`rules_only`) live/runnable; replay
  lines carry their `run_id`'s JSONL.
- ExECTv2: extend `/exectv2/runs` (or its registry) with the same
  `surface_as_architecture` + `display_label` curation so its run list is driven
  the same way rather than by the mock file.

### 3. Frontend

- Gan `TraceControls`: dropdown options keyed by `run_id`; selecting a run loads
  that run's artifact directly (no family-level "best run" heuristic). The trace
  adapter dispatch stays keyed on `architecture_family` (the
  `llm_only_canonical_pipeline` decision-record adapter, the
  `hybrid_structured_events` events adapter, etc.) so DeepSeek/Qwen variants of a
  family reuse the existing adapter — verified that the DeepSeek llm-only artifact
  shares the gpt-4.1-mini decision-record shape.
- Component Impact already renders per-architecture rows; once the registry
  carries qwen/deepseek as surfaced architectures, regenerate the Gan
  component-ablation payload to include them (one ladder per surfaced run).
- Unify labels: Component Impact and the Explorer both read `display_label`, so
  "Hybrid (LLM extract)" etc. are identical across surfaces.

### 4. Holdout hygiene

Surfacing is validation-only. `test450` frozen-audit runs must **not** get
`surface_as_architecture: true`. The Component Impact claim boundary
(`docs/design/gan2026_component_ablation_contract_2026-06-24.md`) is unchanged:
replay-only, aggregate, validation-750, no model calls.

## Work breakdown

1. **Registry schema** — add `surface_as_architecture`, `display_label`,
   `architecture_family` to the Gan run record (+ ExECTv2 equivalent); backfill
   the three current Gan architectures and the qwen/deepseek runs. Migration:
   `experiments/_reconcile_run_registry.py`.
2. **Backend** — rewrite `_build_pipeline_families` to surface curated runs;
   update `/exectv2/runs` to read curation; update the API test
   (`tests/test_observatory_api.py`) to assert run-level surfacing.
3. **Frontend** — `run_id`-keyed Explorer dropdown + direct-run replay; remove
   the "most rows" picker; verify adapters for deepseek/qwen variants.
4. **Component Impact regen** — extend the Gan stage-ladder generator
   (`artifact_analysis/component_stage_ladder.py`) to emit qwen/deepseek ladders;
   refresh `mock-data/gan2026/component-ablation.json`.
5. **Labels** — collapse hardcoded labels (Gan `CANONICAL_PIPELINE_FAMILIES`,
   both mock files) onto registry `display_label`; one naming convention across
   Gan + ExECTv2.
6. **Tests** — run-level surfacing test, holdout-exclusion test, adapter
   coverage for a deepseek/qwen variant.

## Open questions

- Do we want **all** model × architecture cells, or only the cells we actually
  ran (sparse grid)? Sparse is simpler and matches ExECTv2.
- Label convention: `<architecture> · <model>` vs `<model> <architecture>` —
  pick one and apply to both tasks.
- Should the deterministic line ever have non-gpt comparators? (It has no model,
  so likely a single row regardless.)

## Not in scope here (already done 2026-06-24)

- Trimming the Gan Explorer dropdown to the three canonical architectures.
- Wiring the `llm_only_canonical_pipeline` replay adapter (reuses the
  decision-record adapter).
