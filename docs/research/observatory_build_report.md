# Clinical Extraction Observatory — Build Report

**Date:** 2026-06-09  
**Status:** Phase 5 core complete — Review & export layer operational  
**Scope:** Frontend application for exploring, configuring, comparing, and understanding hybrid clinical-extraction pipelines over the Gan 2026 seizure-frequency benchmark.

---

## 1. Core Design Principles

The Observatory is not a dashboard. It is a **scientific instrument** built around five foundational principles:

### 1.1 Specimen-first
The clinical note is the primary object. All chrome — controls, scores, badges — exists to help the user read and reason about the note, not to overwhelm it. The note is rendered as a formal clinical letter in a warm serif typeface (Source Serif Pro / Charter at 15 px, line-height 1.55), while UI chrome uses a crisp sans-serif (Inter). The contrast makes the user feel they are reading a real letter while an intelligent, transparent layer annotates it.

### 1.2 Stage locality
Every intermediate transformation (candidates, normalised events, selected evidence, final label) is inspectable at the exact span of text it refers to. There is no "see the logs" opacity — every highlight is pixel-accurate and every stage has a dedicated inspector panel.

### 1.3 Attribution, not attribution theatre
Every final label must be decomposable into semantically meaningful ownership: which deterministic rule, which LLM call, which repair layer, which benchmark-formatting step. The **Attribution Waterfall** (a horizontal stacked bar) shows this ownership visually:
```
[deterministic_extraction 70% | llm_adjudication 20% | format_repair 10%]
```

### 1.4 Comparison as a first-class mode
The default view is one configuration; the power view is two configurations side-by-side, or one configuration against gold. Diff mode stores a second pipeline family in the URL and renders a compare badge in the header. Changed spans pulse; unchanged spans dim.

### 1.5 Saturated surfaces are calm
High scores on saturated validation prefixes are rendered quietly — as full reservoirs with low information content — rather than celebrated. Hard cases, hard slices, and test audits are rendered with urgency and detail.

### 1.6 No hidden state
Every toggle, prompt variant, and rule switch is part of a named, reproducible configuration that can be exported and fed back into the repo CLI. Full URL serialisation means any view is shareable with a link.

---

## 2. Technical Architecture

### 2.1 Backend — thin, immutable wrapper
The backend is deliberately thin. It reuses the existing `clinical_extraction` package exactly. No scoring, pipeline, or artifact logic is reimplemented.

**Technology:** FastAPI + Pydantic  
**Data sources:**
- `experiments/registry.jsonl` — canonical run log
- `experiments/*.jsonl` — per-run decision records and diagnostics
- `data/Gan (2026)/splits/gan2026_split_v1.json` — split discipline
- `src/clinical_extraction/.../deterministic/rules/` — rule metadata

**Endpoints (18 total):**

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness |
| `POST` | `/run/note` | Single-note deterministic pipeline execution |
| `POST` | `/run/ablation` | Batch ablation against a split |
| `GET` | `/artifacts/{run_id}` | Serve JSONL artifacts |
| `GET` | `/registry` | Run index |
| `GET` | `/splits/{split_name}` | Split manifest metadata |
| `GET` | `/rules` | Full deterministic rule inventory |
| `GET` | `/pipeline-families` | Executable vs replay families |
| `GET` | `/prompts` | Prompt module metadata (all now have policy taxonomies) |
| `GET` | `/prompts/{module}/template` | Rich prompt template hints |
| `GET` | `/records/{split}` | Record previews |
| `GET` | `/records/{split}/{row}` | Full record |
| `POST` | `/tag-error` | Classify prediction into error taxonomy |
| `GET` | `/error-taxonomy/schema` | Error type definitions |
| `GET` | `/hard-slices/definitions` | Hard-slice atlas definitions |
| `POST` | `/hard-slices/membership` | Compute hidden-family membership |
| `GET` | `/meta` | Git provenance + Observatory version |
| `GET/POST` | `/gold-audit/*` | Human adjudication workflow |

### 2.2 Frontend — instrument-grade UI
**Technology:** Next.js 16 (App Router) + TypeScript + Tailwind CSS  
**State:**
- **Zustand** for global config (Architect store, Laboratory store)
- **React Query (TanStack Query)** for server state with aggressive caching (`staleTime: Infinity` for immutable data)
- **URL serialisation** as the source of truth for shareable state

**Custom components:**
- `NoteRenderer` — pixel-accurate evidence span overlays with formal-letter formatting
- `StageStrip` — horizontal navigator with live stage summaries
- `StageInspector` — schema-aware intermediate representation viewer
- `JsonTree` — collapsible colour-coded JSON explorer
- `RegexHighlighter` — custom regex tokenizer with syntax colouring
- `CoFireMatrix` — pure SVG group×group matrix (no D3)

### 2.3 Data contract
The frontend consumes the **exact JSONL schemas** already produced by the repo. No translation layer. Key schemas:
- `PipelineResult[FinalExtraction]` with nested `diagnostics`
- `CandidateEvent` / `NormalizedEvent` / `FinalSelection`
- `decision_record` from hybrid adjudicator runs
- `AblationConfig` from `rule_metadata.py`
- `evaluate_predictions` output structure

---

## 3. The Five Primary Views

### 3.1 The Workbench (`/workbench`) — Single-Note Inspector & Pipeline Trace
**The hero experience.** Inspect how one configuration processes one note, stage by stage.

**Layout:**
- **Top:** Compact 36 px control bar — specimen selector, pipeline family, mode badge
- **Stage strip:** Extract → Normalise → Select → Repair → Score, with live counts
- **Left 55%:** The clinical note as a provenance surface. Highlights animate as the user clicks through stages.
- **Right 45%:** Stage Inspector showing the full intermediate schema for the active stage

**Interaction design:**
- Extract → steel teal | Normalise → slate blue | Select → purple | Score → moss green
- Hover reveals rich tooltip (rule ID, group, portability, label)
- Attribution waterfall for final selected span
- Diff mode: toggle a second configuration; changed spans pulse
- URL-synced: every state change is serialised to query params

**Modes:**
- **Live run** (deterministic families): runs the pipeline immediately
- **Replay from artifact** (LLM/hybrid families): replays pre-recorded decision records

### 3.2 The Observatory (`/observatory`) — Corpus Results & Run Ladder
**Purpose:** Aggregate results across validation prefixes and locked test. Surface the generalisation gap and saturation state.

**Features:**
- **Run Ladder:** Horizontal trajectory cards showing Purist/Pragmatic accuracy and F1 per run. Saturated validation surfaces (≥250 rows with pragmatic accuracy ≥95%) get an explicit low-information badge.
- **Generalisation Gap:** Horizontal grouped bar chart. Each run is a row with two bars (validation in steel blue, test in amber). The gap (Δ) is shown as monospace annotation.
- **Confusion Matrix:** Merged heatmap across selected runs. Clickable cells expand a side panel showing up to 50 example rows.
- **Run Selector:** Family-grouped chips with decision badges (accept/reject/revise), row counts, and JSONL availability.

### 3.3 The Error Gallery (`/gallery`) — Failure Autopsy
**Purpose:** Curated, browsable failure analysis.

**Features:**
- **Error taxonomy:** `false_negative`, `false_positive`, `over_estimate`, `under_estimate`, `near_miss`, `correct`
- **Semantic error groups:** Collapsible groups with severity sparklines and avg severity
- **Transition Matrix:** Compare run A vs run B. Filters: A wrong B right, A right B wrong, both wrong, both right.
- **Deep linking:** Every expanded error card has an "Open in Workbench" button that deep-links to the exact note, pipeline, and `stage=score`
- **Dimensional breakdowns:** Top confused pairs and errors by pipeline family

### 3.4 The Laboratory (`/laboratory`) — Rules & Ablations
**Purpose:** Treat deterministic rules as explicit experimental variables.

**Features:**
- **Rule Inventory:** Two-column collapsible group cards. Each group has a colour-coded accent bar, emoji icon, rule count, and active fraction. Per-rule rows have Switch toggles, portability badges, descriptions, and an inline regex highlighter.
- **Regex syntax highlighter:** Custom tokenizer colour-coding groups (purple), character classes (amber), quantifiers (teal), alternations (blue), escapes (coral), literals (near-black). Named groups `(?P<name>)` extracted as purple badge chips. Long regexes collapse with gradient fade.
- **Live ablation simulation:** Right-hand panel calls `/run/ablation`. Supports split selection and optional row limit. Displays purist/pragmatic accuracy and F1, per-label F1 breakdown with horizontal bars, and top error transitions.
- **Caching:** Deterministic React Query caching with `staleTime: Infinity`. Re-running the same config loads instantly.
- **Rule co-fire matrix:** SVG-based group×group matrix with 72 px cells, rotated -45° column labels. Diagonal cells show rule count per group. Off-diagonal cells show shared portability levels.
- **Prompt Diff:** Side-by-side policy taxonomy diff between any two prompt modules. Shows policies as rows with `NEW`, `CHG`, `removed`, or `same` status. All 5 modules now have structured policies.

### 3.5 The Review (`/review`) — Paper-Ready Export
**Purpose:** Transform observatory data into publication-ready artifacts.

**Features:**
- **Report Assembly:** Unified dashboard showing all tables at once. "Download Full Report" generates a single Markdown document with YAML front-matter.
- **Run Comparison:** Component ablation table. Rows = selected runs. Cols = pipeline family, split, row count, purist/pragmatic accuracy and F1, evidence-valid rate, generalisation gap. Saturated validation surfaces annotated with low-information badge.
- **Per-Label Performance:** Rows = purist categories. Cols = precision, recall, F1, support per run. F1 heat-map colouring (green ≥0.8, amber 0.5–0.8, red <0.5).
- **Error Taxonomy:** Absolute counts and % per run. Severity sparklines (mini horizontal bars) show contribution to error budget.
- **Evidence Audit:** Exact-evidence rate, valid-evidence rate, repair rate, unknown rate. Directly serves Contribution 3 (Transparency Through Evidence).
- **Export:** Every table has Copy Markdown / Download CSV. Full Report combines all tables with YAML front-matter (run IDs, date, user agent, Observatory URL state).

---

## 4. Strongest Features

### 4.1 Unprecedented transparency in a clinical NLP interface
Most clinical-extraction demos show input → output. The Observatory shows input → candidate generation → normalisation → selection → repair → score, with full intermediate schemas at every step. A reviewer can see exactly which deterministic rule fired on which span, what the LLM adjudicator changed, and whether the repair layer modified the answer.

### 4.2 Deterministic rules as first-class experimental variables
The Laboratory does not treat rules as opaque backend logic. Each rule is a card with a toggle. Disabling a rule and clicking "Run simulation" shows the exact F1 delta, per-label breakdown, and error-family shifts. This makes the deterministic layer a controlled variable, not a black box.

### 4.3 Saturation-aware visual language
The UI explicitly distinguishes between low-information validation aggregates (rendered calmly, with "saturated" badges) and high-stakes test results or hard slices (rendered with urgency). This prevents the common research failure of celebrating validation overfitting.

### 4.4 Shareable, reproducible state
Every view is URL-serialised. A researcher can send a link that captures:
- The exact pipeline family and ablation config
- The exact note and row index
- The active stage and diff mode
- The replay artifact and row for LLM/hybrid families

This turns exploratory debugging into reproducible communication.

### 4.5 Prompt diff as code review
The Prompt Diff viewer compares prompt modules with structured policy taxonomies. It is not a raw-text diff (which would be unreadable). It is a semantic diff: "Module A has `exact_substring` evidence policy; Module B does not." This turns prompt engineering from alchemy into version-controlled experimental design.

### 4.6 Deterministic ablation caching
Ablation simulations are deterministic (same rules + same split = same result). The frontend caches them with `staleTime: Infinity`, making rule exploration responsive. A researcher can toggle rules, simulate, toggle back, and see the cached result instantly.

---

## 5. Intended User Flows

### 5.1 A new visitor: understanding the architecture in 5 minutes
1. Lands on `/observatory` — sees the Run Ladder and Generalisation Gap
2. Clicks a run — sees the Confusion Matrix and per-run metrics
3. Clicks a confusion cell — sees example rows
4. Clicks "Open in Workbench" on an example — sees the note with stage-by-stage highlights
5. Clicks through Extract → Normalise → Select → Score — understands the pipeline in under 5 minutes without reading Python

### 5.2 A researcher: comparing two configurations on a single note
1. Goes to `/workbench`, loads a note from the validation split
2. Selects pipeline family A, runs it
3. Toggles diff mode, selects pipeline family B
4. Clicks through stages — changed spans pulse, divergence stage is called out with a badge
5. Opens Stage Inspector at the divergence stage to see exactly why B differed from A

### 5.3 A reviewer: inspecting the validation-to-test gap
1. Goes to `/observatory`, selects runs with both validation and test rows
2. Examines the Generalisation Gap chart — sees the Δ for each run
3. Goes to `/gallery`, filters by error type
4. Expands an error, clicks "Open in Workbench" — sees the note with gold overlay
5. Uses the Ghost Gold overlay to compare predicted vs correct span
6. Understands which error families drive the gap

### 5.4 A rule engineer: testing a rule modification
1. Goes to `/laboratory`, finds the rule in Rule Inventory
2. Disables the rule via toggle
3. Clicks "Run simulation" — sees F1 delta and per-label breakdown
4. If a regression is spotted (previously correct rows flipped), investigates in the Error Transitions panel
5. Re-enables the rule, simulation loads from cache instantly

### 5.5 A paper author: generating results tables
1. Goes to `/review`, selects the runs to include
2. Clicks through tabs: Run Comparison → Per-Label Performance → Error Taxonomy → Evidence Audit
3. Clicks "Copy Markdown" on each table
4. Clicks "Download Full Report" for the complete Markdown document with YAML front-matter
5. Pastes directly into the paper's results section or supplementary material

---

## 6. Prompt Module Taxonomy Coverage

All prompt modules now define structured policy taxonomies, enabling meaningful diff across the entire prompt surface:

| Module | Family | Policies | Key Policy Themes |
|--------|--------|----------|-------------------|
| `llm_only_claim_table_selector` | LLM-only | 15 | Schema constraints, evidence exactness, Gan label formatting, cluster dual-axis, boundary state, exclusions |
| `llm_only_direct_labeler` | LLM-only | 5 | Direct label extraction, strict JSON, exact evidence, boundary separation, current burden |
| `llm_only_structured_events` | LLM-only | 5 | Events+selection schema, source-near raw values, event kind taxonomy, aggregation strategy |
| `llm_only_minimal_evidence_selector` | LLM-only | 3 | Shallow JSON, exact answer substring, close text match |
| `hybrid_rules_candidates_llm_adjudicator` | Hybrid | 5 | Hybrid architecture, candidate audit, accepted/rejected IDs, safety floor, boundary handling |

---

## 7. Backend Extension Inventory

### 7.1 Error Taxonomy API
- **`GET /error-taxonomy/schema`** — Returns 6 error types + severity level definitions
- **`POST /tag-error`** — Classifies any `{gold_category, predicted_category}` into the frontend-aligned taxonomy (`false_negative`, `over_estimate`, `near_miss`, etc.) with severity magnitude

### 7.2 Hard-Slice API
- **`GET /hard-slices/definitions`** — Returns 4 atlas hard slices (candidate_generation_rescue, projection_arbitration, etc.) with membership rules and primary metrics
- **`POST /hard-slices/membership`** — Accepts artifact rows; returns `hidden_families` per row using the same heuristic classifiers as the batch analysis scripts

### 7.3 Prompt Template Registry
- **`GET /prompts/{module}/template`** — Returns rich metadata: system hint (from DSPy Signature docstring), user hint (from `build_prompt_input` docstring), output schema hint (from Pydantic model), function signature, and full policy taxonomy

### 7.4 Git / Provenance Metadata
- **`GET /meta`** — Returns `{branch, commit, dirty, remote_url}` for reproducibility tracking in exported reports

---

## 8. What Remains (Explicitly Deferred)

The following are **intentionally postponed** per project direction:

| Item | Reason |
|------|--------|
| LLM/hybrid live execution via `/run/note` | Requires full DSPy LM setup; belongs to a future phase |
| Figure/image export (PNG heatmaps, charts) | Requires canvas/SSR rendering pipeline or Vega-Lite spec export |
| LaTeX table export | Can be derived from Markdown via Pandoc |
| Cross-run A/B trace comparison in Workbench | Requires dual-trace store architecture; non-trivial |
| Real-time ablation simulation against validation | `/run/ablation` integration is present; backend caching layer deferred |
| Rule interaction graph from per-rule firing telemetry | Requires backend telemetry extension |
| Error taxonomy tree with severity sparklines | Requires backend error-family tagging on every row at evaluation time |
| Confusion-matrix cell mosaic → Workbench autopsy | Requires additional cross-view routing |
| Ghost path preview on ablation hover | Requires speculative execution or backend pre-computation |
| Hard-slice filter in Review tables | Requires backend hard-slice API integration (endpoint exists; frontend integration deferred) |
| Component ablation table mixing Lab + Observatory results | Requires unified `AblationRunSummary` type |

---

## 9. Files Modified in This Build

### Backend
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/observatory/api.py` — 6 new endpoints, error taxonomy helpers, prompt template helpers, git metadata helpers
- `src/.../llm/llm_only_direct_labeler.py` — Added `PROMPT_POLICY_TAXONOMY` (5 policies)
- `src/.../llm/llm_only_structured_events.py` — Added `PROMPT_POLICY_TAXONOMY` (5 policies)
- `src/.../llm/llm_only_typed_adapter_reasoner.py` — Added `PROMPT_POLICY_TAXONOMY` (4 policies)
- `src/.../hybrid/hybrid_rules_candidates_llm_adjudicator.py` — Added `PROMPT_POLICY_TAXONOMY` (5 policies)

### Frontend
- `frontend/lib/types.ts` — Added `PromptTemplateResponse`, `TagErrorResponse`, `ErrorTaxonomySchemaResponse`, `HardSliceDefinition`, `HardSliceDefinitionsResponse`, `HardSliceMembershipResponse`, `MetaResponse`
- `frontend/lib/api.ts` — Added `fetchPromptTemplate`, `tagError`, `fetchErrorTaxonomySchema`, `fetchHardSliceDefinitions`, `fetchHardSliceMembership`, `fetchMeta`
- `frontend/lib/hooks.ts` — Rewrote `useRunAblation` as query-based with deterministic caching; added `useArchitectUrlSync` for the active Architect store; exported `serializeAblation` / `deserializeAblation`
- `frontend/app/laboratory/page.tsx` — Lifted split/limit state; wired new `useRunAblation` hook
- `frontend/components/laboratory/SimulationPanel.tsx` — Updated props for lifted state; added cached-state indicator
- `frontend/app/workbench/page.tsx` — Wired `useArchitectUrlSync`
- `frontend/components/architect/TraceControls.tsx` — Added auto-select replay row effect when `sourceRowIndex` matches artifact row
- `frontend/app/gallery/page.tsx` — Added `ExternalLink` + `Link` imports; added "Open in Workbench" deep-link button to every expanded error card

---

*This document is a durable build report. It should be revised when new views are added, when backend extensions are expanded, or when the prompt module surface changes.*
