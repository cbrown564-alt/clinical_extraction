# ExECTv2 Frontend Dataset Integration Implementation Plan

Date: 2026-06-22

Status: implemented (frontend integration delivered 2026-06-22)

Scope: replace the current ExECTv2-as-separate-page direction with a
dataset-aware explorer architecture. ExECTv2 should be selectable as a sticky
dataset option in the top-right app shell, and that selection should drive the
Example Explorer, Aggregate Performance, Component Impact, and Error Gallery
surfaces.

This plan supersedes treating `/exectv2` as the destination experience. The
current `/exectv2` route and generated mock data remain useful as a prototype
and data source while the integrated dataset model is built.

## Implementation Status (2026-06-22)

Delivered. ExECTv2 is now a first-class dataset selectable from a sticky
top-right switcher that drives all four review surfaces. Gan behaviour and URLs
are unchanged.

What was built:

- **Dataset kernel** (`frontend/lib/datasets/`): shared contracts (`types.ts`),
  `gan2026` and `exectv2` descriptors, `registry.ts`, URL/`datasetId` helpers
  (`url.ts`, `surfaceHref`), and a URL+localStorage-synced `useActiveDataset` /
  `useDatasetNavigation` hook (`useDataset.ts`). Bare Gan URLs resolve to
  `gan2026` (default); `?dataset=` wins; last choice persists in localStorage.
- **Sticky switcher** (`components/shell/DatasetSwitcher.tsx`) in the app-shell
  Navbar top-right; ExECTv2 removed from the primary nav; surface links preserve
  the active dataset.
- **ExECTv2 adapters** (`lib/datasets/adapters/`): `exectv2Errors.ts` derives
  mention-level residuals (FP / FN / attribute-mismatch / evidence-invalid) by
  gold↔predicted matching with exact-quote + CUI awareness; `exectv2Components.ts`
  summarises component provenance and computes v08→v09 family deltas.
- **Four ExECTv2 surfaces** (`components/exectv2/`): Example Explorer, Aggregate
  Performance, Component Impact, Error Gallery, sharing run/letter/family URL
  state and cross-surface deep links.
- **Dataset routing**: `workbench`, `observatory`, `laboratory`, `gallery` pages
  branch on the active dataset; `/exectv2` redirects to
  `/workbench?dataset=exectv2`, forwarding any selection.

Scoping decisions (deltas from the suggestions below):

- **Data layout**: ExECTv2 surfaces read the existing
  `public/mock-data/exectv2/runs.json` (which already carries runs, letters,
  mentions, evidence, metrics, and operational fields). Errors and component
  summaries are derived client-side via adapters rather than from pre-sharded
  `errors/` and `components/` files. The data API is abstracted behind the
  adapter/hook layer, so re-sharding into the dataset-indexed static layout
  remains a clean, additive follow-up — not required for the surfaces to work.
- **Gan surfaces** are routed-to, not internally refactored: branching happens at
  the page level so the battle-tested Gan components and URLs are untouched
  (lowest-risk path to "Option C").

Phase B — index-driven generator (delivered): `scripts/build_exectv2_frontend_mock_data.py`
no longer hardcodes a run list. It parses the canonical runs directly from
`docs/experiments/final_artifact_index_*.md` (each `### ExECTv2 …` section under
`## Canonical Artifact Groups`), so incorporating a new architecture is "edit the
index, re-run the generator" — no script change. It auto-discovers the newest
index, validates that referenced artifacts exist, and is covered by
`tests/test_build_exectv2_frontend_mock_data.py`. The remaining optional Phase B
item is re-sharding the single `runs.json` into the dataset-indexed static layout.

Verification: `npx tsc --noEmit` clean; `npm run build` prerenders all routes;
24/24 frontend Jest tests pass (12 new dataset-kernel/adapter tests) plus 6 new
Python generator tests; new code is ESLint-clean (remaining repo lint errors are
pre-existing `any` debt in `lib/api.ts` and `lib/hooks.ts`); dev-server smoke
test returns 200 for all dataset-aware routes.

## Core Decision

The frontend should have stable review surfaces and swappable datasets.

Stable surfaces:

- Example Explorer: inspect one specimen and one run in detail.
- Aggregate Performance: compare runs and headline metrics.
- Component Impact: inspect which system components change predictions or
  reliability.
- Error Gallery: review residual errors, filtered by run, family, component, and
  error class.

Datasets:

- `gan2026`: seizure-frequency extraction and reliability analysis.
- `exectv2`: four-family key clinical finding extraction across Diagnosis,
  SeizureFrequency, Prescription, and Investigations.

The dataset switcher should sit in the app shell, visually sticky in the top
right. It should not be a normal nav tab. Changing dataset changes the available
runs, rows, metrics, components, error taxonomy, stage labels, and page copy for
all four surfaces.

## Why The Current Direction Is Not Enough

The Phase 0 `/exectv2` route proves that ExECTv2 artifacts can be loaded and
rendered, but it creates a parallel app shape. That makes ExECTv2 look like a
side feature instead of a second dataset inside the same review instrument.

Problems to fix:

- The workbench state model is Gan-specific: `split`, `sourceRowIndex`,
  `pipelineFamily`, seizure-frequency categories, and stage assumptions are
  embedded in hooks and components.
- Aggregate summaries currently expect Gan-style Purist/Pragmatic category
  logic and fixed confusion buckets.
- Component-impact surfaces are organized around Gan rule families rather than
  a generic component/lens/architecture concept.
- The error gallery assumes seizure-frequency label transitions rather than a
  dataset-owned error taxonomy.
- `/exectv2` duplicates review patterns instead of standardizing them.

The integration target is therefore a shared dataset/task kernel with
dataset-specific adapters, not a larger ExECTv2 tab.

## Alternatives Considered

### Option A - Keep `/exectv2` As A Separate Page

Rejected.

This is fast but structurally wrong. It duplicates explorer logic, hides
ExECTv2 outside the main review workflow, and prevents direct comparison of how
the same app surfaces behave across Gan and ExECTv2.

### Option B - Add A Dataset Query Parameter With Conditional UI

Insufficient.

Adding `?dataset=exectv2` without changing the underlying contracts would leave
Gan concepts in the center. ExECTv2 data would still be forced through
seizure-frequency-shaped records, category names, stage labels, and gallery
logic.

### Option C - Build A Dataset Kernel And Dataset Adapters

Recommended.

Define shared frontend concepts once, then let Gan and ExECTv2 provide
adapters, metrics, component definitions, error taxonomies, and render hints.
This preserves the existing app surfaces while making ExECTv2 first-class.

## Standardized Concepts

The following concepts become shared frontend language.

| Concept | Shared meaning | Gan 2026 mapping | ExECTv2 mapping |
| --- | --- | --- | --- |
| Dataset | A task/data family selectable in the app shell | `gan2026` | `exectv2` |
| Specimen | One reviewable source item | note row | letter |
| Specimen ref | URL-safe item reference | `split` + `sourceRowIndex` | split/stage + `letterId` |
| Run | One model/pipeline/config result set | pipeline family + artifact | assembly candidate/artifact |
| Prediction | Model/system output for a specimen | selected seizure-frequency label/events | predicted entity mentions |
| Gold | Reference answer for a specimen | gold label/category | gold mentions by family |
| Evidence | Source text supporting a prediction | evidence snippet/selected event | exact evidence span/quote |
| Stage | Trace step in a run | extract, normalise, select, repair, score | source, propose, lens, assemble, score |
| Component | Prediction-bearing system part | prompt, deterministic rule, repair, scorer | producer lane, dictionary, semantic lens, assembler, scorer |
| Metric | Quantitative result | accuracy/F1 by category or view | overall/family F1, active-rate, exact evidence, parse/call reliability |
| Error class | Dataset-owned residual taxonomy | wrong category, false active rate, missing label, etc. | FP, FN, attribute mismatch, evidence invalid, component owner issue |
| Claim boundary | What the run can support | dev/test/holdout guardrail | dev25/dev140/full-200/holdout guardrail |

These concepts should be represented in TypeScript rather than only in
component-local assumptions.

## Proposed Frontend Contracts

Add a dataset module layer under `frontend/lib/datasets/`.

Suggested files:

- `frontend/lib/datasets/types.ts`
- `frontend/lib/datasets/registry.ts`
- `frontend/lib/datasets/gan2026.ts`
- `frontend/lib/datasets/exectv2.ts`
- `frontend/lib/datasets/url.ts`
- `frontend/lib/datasets/adapters/gan2026Trace.ts`
- `frontend/lib/datasets/adapters/exectv2Trace.ts`
- `frontend/lib/datasets/adapters/exectv2Errors.ts`

Core interfaces:

```ts
export type DatasetId = "gan2026" | "exectv2";

export interface DatasetDescriptor {
  id: DatasetId;
  label: string;
  shortLabel: string;
  specimenLabel: string;
  defaultSurface: ExplorerSurface;
  defaultSplit: string;
  supports: DatasetSurfaceSupport;
  families: TaskFamilyDescriptor[];
  metrics: MetricDescriptor[];
  components: ComponentDescriptor[];
  errorTaxonomy: ErrorClassDescriptor[];
}

export interface SpecimenRef {
  datasetId: DatasetId;
  split: string;
  sourceRowIndex?: number;
  letterId?: string;
}

export interface RunDescriptor {
  datasetId: DatasetId;
  runId: string;
  label: string;
  model: string;
  architectureFamily: string;
  split: string;
  rowCount: number;
  artifactPath: string;
  claimBoundary: string;
  decision: "control" | "simplification" | "diagnostic" | "pending" | "superseded";
}

export interface SpecimenRecord {
  ref: SpecimenRef;
  title: string;
  sourceText: string;
  metadata: Record<string, string | number | boolean | null>;
  gold: TaskAnnotation[];
  predictions: TaskAnnotation[];
  evidence: EvidenceSpan[];
  scores: SpecimenScore[];
}

export interface TaskTrace {
  datasetId: DatasetId;
  runId: string;
  specimenRef: SpecimenRef;
  stages: TraceStage[];
  finalPrediction: TaskAnnotation[];
  gold: TaskAnnotation[];
  scores: SpecimenScore[];
}
```

The exact names can change during implementation, but these contracts should be
explicit enough that components stop importing Gan-only assumptions.

## URL And State Model

The dataset should be globally addressable.

Recommended URL pattern:

- `/workbench?dataset=gan2026&split=validation&row=10`
- `/workbench?dataset=exectv2&split=dev140&letter=...&run=...`
- `/observatory?dataset=exectv2&run=...`
- `/laboratory?dataset=exectv2&run=...&component=...`
- `/gallery?dataset=exectv2&run=...&family=Diagnosis`

Compatibility rules:

- Old Gan URLs without `dataset` default to `gan2026`.
- If a URL contains `row` but no `letter`, interpret it through the active
  dataset adapter.
- Store the last selected dataset in local storage for app-shell persistence.
- URL value wins over local storage when present.
- Dataset switching preserves the current surface but resets incompatible item
  selectors to dataset defaults.

State changes:

- Add `datasetId` to the global UI/config store.
- Move split, run, specimen, and family selection behind dataset-aware selectors.
- Replace `sourceRowIndex` as a universal concept with `SpecimenRef`.
- Keep Gan aliases where needed for backward compatibility during migration.

## App Shell And Sticky Dataset Switcher

Add a compact dataset switcher in the top-right app shell, separate from the
main nav.

Behavior:

- Always visible on desktop.
- Sticky at the top-right when the page scrolls.
- On mobile, collapse to a compact select/menu in the top bar.
- Shows current dataset label and a short status summary, for example
  `Gan 2026` or `ExECTv2`.
- Switching dataset updates URL, store state, and active surface data together.

Design:

- Treat it like a context selector, not a promotional badge.
- Keep it dense and utilitarian.
- Include diagnostic status in run selectors, not in the dataset switcher.
- Avoid making ExECTv2 a top-level nav tab once integration is complete.

## Data Layout

Phase 0 can stay static-file first. A backend API can follow the same shapes.

Suggested static layout:

```text
frontend/public/mock-data/datasets/index.json
frontend/public/mock-data/datasets/gan2026/runs.json
frontend/public/mock-data/datasets/gan2026/specimens-validation.json
frontend/public/mock-data/datasets/gan2026/artifacts/<run-id>.json
frontend/public/mock-data/datasets/gan2026/errors/<run-id>.json
frontend/public/mock-data/datasets/exectv2/runs.json
frontend/public/mock-data/datasets/exectv2/specimens-dev140.json
frontend/public/mock-data/datasets/exectv2/specimens-dev25.json
frontend/public/mock-data/datasets/exectv2/artifacts/<run-id>.json
frontend/public/mock-data/datasets/exectv2/errors/<run-id>.json
frontend/public/mock-data/datasets/exectv2/components/<run-id>.json
```

The existing registry can be bridged temporarily, but the target should be a
dataset-indexed data layout.

Generator work:

- Keep `scripts/build_exectv2_frontend_mock_data.py` as the seed.
- Extend it to emit dataset-native files instead of one route-specific blob.
- Add a Gan generator or adapter shim so both datasets use the same frontend
  loading path.
- Validate generated JSON with lightweight schema checks before build.

## Surface 1 - Example Explorer

Current route: `/workbench`

Target: one explorer with dataset-owned specimen and trace semantics.

Gan behavior:

- Preserve current validation/train/test row navigation.
- Preserve live/replay trace loading.
- Preserve extract/normalise/select/repair/score stage language.
- Preserve note rendering and seizure-frequency final-label inspection.

ExECTv2 behavior:

- Navigate by `letterId` and split/stage (`dev25`, `dev140`, later full-200 or
  holdout only under protocol).
- Select run from the ExECTv2 architecture set:
  - v08 GPT-4.1-mini performance control;
  - v09 partial hybrid simplification control;
  - DeepSeek diagnostic comparator;
  - Qwen diagnostic comparator.
- Render source letter text with evidence highlights.
- Show gold and predicted mentions grouped by:
  - Diagnosis;
  - SeizureFrequency;
  - Prescription;
  - Investigations.
- Show mention attributes where available, including CUI/CUIPhrase,
  certainty/status, active-rate detail, current-vs-plan information, result
  state, source lane, component owner, and evidence validity.
- Use ExECTv2 stages such as source, propose, lens, assemble, score. If the UI
  keeps five generic columns, map them through adapter-provided stage labels.

Acceptance criteria:

- `/workbench?dataset=gan2026&split=validation&row=10` still works.
- `/workbench?dataset=exectv2&split=dev140&letter=<id>` opens an ExECTv2 letter.
- No ExECTv2 record is forced into Gan seizure-frequency categories.
- Evidence highlighting works from exact text matching even without offsets.
- Run switching preserves the same letter when the selected run covers it.

## Surface 2 - Aggregate Performance

Current route: `/observatory`

Target: one aggregate page with dataset-owned metric packs.

Gan behavior:

- Preserve current run comparison tables.
- Preserve Purist/Pragmatic and seizure-frequency aggregate summaries.
- Preserve existing report builder behavior unless rewritten behind an adapter.

ExECTv2 behavior:

- Show run comparison across selected ExECTv2 architectures.
- Headline columns:
  - overall clinical headline F1;
  - Diagnosis F1;
  - SeizureFrequency F1;
  - Prescription F1;
  - Investigations F1;
  - exact evidence rate;
  - call failures;
  - parse/schema failures;
  - row count and split;
  - decision and claim boundary.
- Make controls visually distinct from diagnostics even when both are dev140.
  The final DeepSeek/Qwen dev140 rows should not look promoted merely because
  they share the control split.
- Add family-level details for active-rate or strict companion surfaces where
  available.
- Link aggregate rows to the Example Explorer and Error Gallery with the active
  dataset preserved.

Acceptance criteria:

- Gan aggregate metrics remain unchanged.
- ExECTv2 aggregate view reproduces the selected architecture set from the
  final artifact index.
- Diagnostic runs are not displayed as promoted replacements.
- Metrics are label-safe: ExECTv2 family F1 is not renamed into Gan category
  accuracy.

## Surface 3 - Component Impact

Current route: `/laboratory`

Target: one component-impact surface with dataset-owned component definitions.

Gan behavior:

- Preserve rule inventory, ablation simulation, and seizure-frequency repair
  interpretation.
- Keep deterministic rule effects tied to Gan labels and candidate events.

ExECTv2 behavior:

- Rename the conceptual layer from "rules only" to "components".
- Track component types:
  - LLM producer lane;
  - deterministic dictionary;
  - semantic lens;
  - assembly/merge logic;
  - evidence validation;
  - scorer surface.
- Show v08 versus v09 partial hybrid deltas by family.
- Show pure single-pass, partial hybrid, DeepSeek, and Qwen diagnostic rows as
  architecture/component comparisons where artifacts exist.
- Attribute component impact to the family it affects:
  - Diagnosis hierarchy/assertion ownership;
  - SeizureFrequency active-rate fidelity;
  - Prescription current medication versus plan ambiguity;
  - Investigations result-state and test-result ownership.
- Separate benchmark-format repairs from clinically prediction-bearing repairs.

Acceptance criteria:

- Gan rule simulation still works.
- ExECTv2 component impact can explain why v09 partial hybrid remains above
  0.900 overall while losing Investigations headroom.
- The surface distinguishes deterministic formatting from semantic add/drop or
  replace actions.
- Component labels match the architecture memo and reliability scorecard.

## Surface 4 - Error Gallery

Current route: `/gallery`

Target: one gallery with dataset-owned error taxonomies and filters.

Gan behavior:

- Preserve current confusion and category transition views.
- Preserve links back to workbench rows.

ExECTv2 behavior:

- Use ExECTv2 error classes:
  - false positive mention;
  - false negative mention;
  - wrong family;
  - wrong CUI or CUIPhrase;
  - assertion/status mismatch;
  - active-rate mismatch;
  - current medication versus plan mismatch;
  - investigation result-state mismatch;
  - invalid or weak evidence;
  - component ownership/provenance issue;
  - call/parse/schema failure.
- Filters:
  - run;
  - split;
  - family;
  - error class;
  - component owner;
  - model;
  - diagnostic/control decision.
- Rows should link to the Example Explorer with dataset/run/letter preserved.
- The gallery should include gold and predicted mention snippets, evidence text,
  component owner, and score contribution where available.

Acceptance criteria:

- Gan gallery behavior remains intact.
- ExECTv2 errors are reviewable without translating them into seizure-frequency
  transitions.
- A reviewer can start from an aggregate family weakness and reach the relevant
  ExECTv2 letter examples in two clicks.

## Implementation Phases

### Phase A - Dataset Kernel

Goal: introduce dataset descriptors and shared contracts without changing page
behavior.

Tasks:

- Add dataset TypeScript contracts.
- Add Gan and ExECTv2 dataset descriptors.
- Add `datasetId` to URL/store state.
- Add compatibility helpers for old Gan URLs.
- Add schema validation for dataset static files.

Deliverable:

- Components can ask "what dataset is active?" and "what does this dataset
  support?" without any visible UI change.

### Phase B - Data Adapter Migration

Goal: make both Gan and ExECTv2 load through the same dataset-aware API layer.

Tasks:

- Add dataset-indexed static mock-data layout.
- Refactor API helpers to accept `datasetId`.
- Extend ExECTv2 mock generator to output runs, specimens, aggregate metrics,
  component summaries, and error rows.
- Add a Gan adapter shim over existing registry/artifacts.
- Add adapter tests for both datasets.

Deliverable:

- `fetchRuns(datasetId)`, `fetchSpecimens(datasetId, split)`,
  `fetchAggregate(datasetId, runId)`, `fetchComponents(datasetId, runId)`, and
  `fetchErrors(datasetId, runId)` work for both datasets.

### Phase C - Sticky Dataset Switcher

Goal: make dataset selection a first-class app-shell control.

Tasks:

- Add top-right dataset switcher to the shared nav/app shell.
- Persist selection in URL and local storage.
- Reset incompatible selectors when switching datasets.
- Remove ExECTv2 from primary nav once the integrated surfaces are ready.
- Keep `/exectv2` as a temporary redirect or legacy prototype during migration.

Deliverable:

- Users can switch between Gan 2026 and ExECTv2 from any main surface.

### Phase D - Example Explorer Integration

Goal: refactor `/workbench` around `SpecimenRef`, `RunDescriptor`, and
`TaskTrace`.

Tasks:

- Replace universal `sourceRowIndex` assumptions with `SpecimenRef`.
- Split Gan and ExECTv2 trace adapters.
- Add ExECTv2 mention rendering in the existing note/letter viewer area.
- Add ExECTv2 run selector and family filters.
- Preserve old Gan workbench URLs.

Deliverable:

- The workbench is the Example Explorer for both datasets.

### Phase E - Aggregate Performance Integration

Goal: make `/observatory` render dataset metric packs.

Tasks:

- Replace Gan-only summary assumptions with metric descriptors.
- Add ExECTv2 run comparison table.
- Add dataset-specific detail panels through adapter components.
- Add links from aggregate rows to workbench and gallery.

Deliverable:

- Aggregate Performance supports ExECTv2 controls and diagnostics in the same
  surface as Gan.

### Phase F - Component Impact Integration

Goal: refactor `/laboratory` into a dataset-aware component-impact surface.

Tasks:

- Rename internal concepts from rule-only to component-aware where appropriate.
- Preserve Gan rule inventory through a Gan component adapter.
- Add ExECTv2 component summaries and architecture deltas.
- Connect components to error-gallery filters.

Deliverable:

- Component Impact explains both Gan rules and ExECTv2 lenses/lanes through a
  shared interface.

### Phase G - Error Gallery Integration

Goal: make `/gallery` render dataset error taxonomies.

Tasks:

- Add generic error row contracts.
- Add ExECTv2 error adapter from error ledgers and assembly artifacts.
- Add dataset-owned filters.
- Preserve workbench links with dataset/run/specimen refs.

Deliverable:

- Error Gallery supports both Gan category transitions and ExECTv2 mention-level
  errors.

### Phase H - Retire The Standalone ExECTv2 Destination

Goal: remove the conceptual fork once integration is complete.

Tasks:

- Redirect `/exectv2` to the most relevant integrated surface, likely
  `/workbench?dataset=exectv2`.
- Keep any ExECTv2-specific helpers or components that were generalized.
- Delete route-only UI duplication after all four surfaces cover ExECTv2.
- Update docs and screenshots.

Deliverable:

- ExECTv2 lives in the explorer as a dataset, not as a tab.

### Phase I - Verification And Polish

Goal: prove the migration did not break Gan and that ExECTv2 is complete enough
for review.

Tasks:

- Run `npx tsc --noEmit`.
- Run `npm run build`.
- Run lint or document pre-existing lint debt.
- Add focused unit tests for URL parsing, dataset descriptors, adapters, and
  generated mock-data validation.
- Add browser smoke checks for:
  - Gan workbench old URL;
  - ExECTv2 workbench URL;
  - Gan observatory;
  - ExECTv2 aggregate performance;
  - ExECTv2 component impact;
  - ExECTv2 error gallery.

Deliverable:

- A reviewable frontend where both datasets work from the same app shell and
  main surfaces.

## Migration Strategy

Use a bridging period.

1. Add dataset contracts while leaving current pages visually unchanged.
2. Teach data loading to accept `datasetId`.
3. Add the dataset switcher behind the existing routes.
4. Integrate one surface at a time, starting with the Example Explorer.
5. Keep `/exectv2` available until all four surfaces have ExECTv2 coverage.
6. Redirect or retire `/exectv2` after acceptance criteria pass.

This keeps Gan review stable while ExECTv2 moves into the shared architecture.

## Testing Strategy

Required tests:

- Dataset descriptor validation:
  - both datasets declare required surfaces;
  - each metric/component/error class has stable IDs and labels.
- URL compatibility:
  - old Gan URLs still parse;
  - ExECTv2 URLs preserve `letterId` and `runId`;
  - dataset switching resets incompatible selectors.
- Adapter tests:
  - Gan artifacts still produce current summary shapes;
  - ExECTv2 assembly artifacts produce specimens, mentions, evidence, scores,
    component summaries, and error rows.
- Generator tests:
  - generated ExECTv2 static data contains all selected runs;
  - diagnostic rows are not mixed into controls, including dev140 diagnostics;
  - required family metrics exist.
- Build checks:
  - `npx tsc --noEmit`;
  - `npm run build`;
  - lint when unrelated existing lint debt is either fixed or documented.

Browser checks:

- The sticky dataset switcher is visible in the top-right on desktop.
- Dataset switching preserves the current surface.
- Gan and ExECTv2 use different labels, filters, and metric names.
- Workbench links from aggregate and gallery preserve the active dataset.

## Acceptance Criteria

The integration is complete when:

- A sticky top-right dataset switcher is available across the app.
- `gan2026` and `exectv2` are both selectable datasets.
- Example Explorer supports Gan notes and ExECTv2 letters.
- Aggregate Performance supports Gan metrics and ExECTv2 family/model metrics.
- Component Impact supports Gan rules and ExECTv2 components/lenses/lanes.
- Error Gallery supports Gan category transitions and ExECTv2 mention-level
  residuals.
- Existing Gan URLs keep working.
- ExECTv2 runs are labeled with correct control, simplification, diagnostic, or
  pending status.
- ExECTv2 data is not coerced into Gan seizure-frequency category concepts.
- `/exectv2` is no longer the primary ExECTv2 review destination.

## Non-Goals

- No new live ExECTv2 model calls are required for this frontend integration.
- No full-200 or holdout row-level ExECTv2 inspection is authorized by this
  plan.
- No benchmark claim is added by making ExECTv2 visible in the frontend.
- No backend service is required for the first integrated implementation; static
  mock data is acceptable if the contracts match a future API.
- No destructive repo cleanup is part of this work.

## Risks And Mitigations

Risk: Gan-specific assumptions are deeper than expected.

Mitigation: migrate one surface at a time and keep old Gan URL tests green.

Risk: ExECTv2 component impact does not match Gan rule simulation exactly.

Mitigation: standardize on "component impact" rather than "rule simulation" as
the shared surface, with dataset-specific panels.

Risk: ExECTv2 evidence spans lack offsets.

Mitigation: use exact quote matching for Phase 1, then add offsets if the data
pipeline can provide them.

Risk: diagnostic rows are visually mixed with dev140 controls.

Mitigation: make split, row count, decision, and claim boundary required run
metadata, and treat decision status as a first-class visual filter.

Risk: generated static JSON becomes too large.

Mitigation: start with selected canonical runs and compact per-surface files,
then lazy-load specimens and errors by split/run.

Risk: pre-existing lint debt obscures verification.

Mitigation: record whether lint failures predate the integration and require
typecheck/build to pass.

## Recommended First Implementation Slice

Start with the smallest slice that proves the architecture:

1. Add dataset descriptors and URL/store `datasetId`.
2. Add sticky dataset switcher with Gan as the default.
3. Move ExECTv2 generated data into dataset-indexed mock files.
4. Refactor `/workbench` to resolve a dataset-specific `SpecimenRef`.
5. Render one ExECTv2 v08 dev140 letter in the workbench with gold/predicted
   mentions and evidence.
6. Preserve the old Gan workbench URL and behavior.

Once that works, expand in order:

1. ExECTv2 aggregate performance.
2. ExECTv2 error gallery.
3. ExECTv2 component impact.
4. `/exectv2` redirect/retirement.

This sequence proves the hardest abstraction first while limiting the blast
radius.
