# Clinical Extraction Observatory

**Status:** Phase 1 complete — all Phase 1 features implemented; ready for Phase 2  
**Last updated:** 2026-06-02  
**Scope:** Frontend application for exploring, configuring, comparing, and understanding hybrid clinical-extraction pipelines.  
**Backend dependency:** Reuses existing `clinical_extraction` package, JSONL artifacts, run registry, and split protocol without modification. Backend extensions are noted but deferred.

---

## 1. Purpose & Vision

The Observatory is a web application that transforms the research codebase into an interactive, transparent lens for clinical extraction. A user should be able to:

1. Choose a task (e.g., seizure-frequency extraction).
2. Choose an architecture family (e.g., `rules_only`, `llm_only`, `hybrid`).
3. Configure an implementation (toggle rules, select prompt variants, set model and temperature).
4. Inspect a visual, stage-by-stage representation of how that configuration processes an example record.
5. View results across dataset surfaces (validation 25/50/250/750, locked test).
6. Explore comprehensive error analysis on the validation set.
7. See exactly how a configuration annotates a clinical note, with evidence provenance at every stage.

The app must make the modular approach absolutely clear, make the generalisation gap explicit and easier to reason about, provide unparalleled transparency, and demonstrate deterministic rules as controlled experimental variables.

### Success criteria

- A new visitor can understand the pipeline architecture in under five minutes without reading Python code.
- A researcher can compare two configurations on a single note and see precisely which stage caused a divergence.
- A reviewer can inspect the validation-to-test gap and understand *which error families* drive it.
- The UI makes saturation explicit: near-ceiling validation scores are not celebrated; they are rendered as full reservoirs with low information content.

---

## 2. Design Principles

1. **Specimen-first.** The clinical note is the primary object. All chrome exists to help the user read and reason about the note, not to overwhelm it.
2. **Stage locality.** Every intermediate transformation (candidates, normalised events, selected evidence, final label) is inspectable at the exact span of text it refers to.
3. **Attribution, not attribution theatre.** Every final label must be decomposable into semantically meaningful ownership: which deterministic rule, which LLM call, which repair layer, which benchmark-formatting step.
4. **Comparison as a first-class mode.** The default view is one configuration; the power view is two configurations side-by-side, or one configuration against gold.
5. **Saturated surfaces are calm.** High scores on saturated validation prefixes are rendered quietly. Hard cases, hard slices, and test audits are rendered with urgency and detail.
6. **No hidden state.** Every toggle, prompt variant, and rule switch is part of a named, reproducible configuration that can be exported and fed back into the repo CLI.

---

## 3. Core Metaphor: The Pipeline Observatory

The clinical note is a **specimen slide**. The pipeline is an **adjustable instrument** on a laboratory workbench.

- **Raw text** = the unmounted slide.
- **Deterministic rules** = precision mechanical stages (calibrated, inspectable, toggleable).
- **LLM components** = adaptive optical lenses (powerful but requiring interpretation).
- **Evidence spans** = fluorescent tags that light up under specific filters.
- **Ablations** = removing lenses or stages to see what the instrument misses.
- **Gold labels** = a senior clinician's annotation in the margin, available as a "ghost" overlay.

The interface should feel like a high-end scientific instrument: clean, authoritative, with clear affordances for zooming in and peeling back layers.

---

## 4. The Five Primary Views

### 4.1 The Workbench (Single-Note Inspector)

**Purpose:** The hero experience. Inspect how one configuration processes one note, stage by stage, with rich inline annotation.

**Layout:**
- **Left 60%:** The clinical note rendered as a formal letter. This is a **provenance surface**, not plain text.
- **Right 40%:** A vertical **Stage Navigator** showing the pipeline as a stack of detachable, expandable cards.

**Interaction design:**
- As the user clicks through stages (`Extract` → `Normalize` → `Select` → `Repair` → `Score`), the note text animates highlights to show exactly which spans were touched at that stage.
- Each extracted span is highlighted with a **light background tint + matching underline** in the stage's colour:
  - **Extract** → steel teal (`deterministic`)
  - **Normalise** → slate blue (`deterministic-alt`)
  - **Select** → purple (`hybrid`)
  - **Score** → moss green (`success`)
  - Warm amber for LLM-generated spans (future).
  - Coral for repair-modified spans (future).
- Hovering a span reveals its tooltip (rule ID, label) via native `title`.
- Full floating cards with rule ID, match groups, portability badge, and rationale are deferred.
- **Attribution waterfall:** For the final selected span, a horizontal stacked bar shows semantic ownership (`deterministic_extraction` | `llm_adjudication` | `format_repair` | `benchmark_normalisation`).
- **Diff mode:** Toggle a second configuration. Changed spans pulse; unchanged spans dim. Divergence at a specific stage is called out with a stage-level badge.

**Data consumed:**
- `GanRecord.note_text`
- `PipelineResult.diagnostics` (candidate events, normalised events, final selection)
- `decision_record` (for hybrid architectures)
- Evidence spans with `start_char` / `end_char`

**Key detail:** The note uses a warm, readable serif (Source Serif Pro or Charter) at 16 px with generous line height. UI chrome uses a crisp sans-serif. The contrast makes the user feel they are reading a real letter while an intelligent layer annotates it.

---

### 4.2 The Architect (Pipeline Composer)

**Purpose:** Visually assemble, configure, and name pipeline architectures. Toggle rules and prompt variants and see what would change.

**Layout:**
- **Canvas centre:** A left-to-right flow diagram.
- **Palette sidebar:** Draggable node types (Extractor, Normaliser, Selector, Validator, Repair, Scorer) grouped by family.

**Nodes:**
- Rounded rectangles, colour-coded:
  - `rules_only` = cool steel/teal (`#2a6f6f`)
  - `llm_only` = warm amber/gold (`#d97706`)
  - `hybrid` = controlled purple (`#7c3aed`) at the interface
- Each node shows its component name and a live "activity ring" (how many active rules or prompts inside).

**Edges:**
- Animated data-flow lines. Thicker = more candidates/events flowing through.
- Red pulse = validation errors introduced at that edge.

**Configuration affordances:**
- Clicking a node expands a **drawer** with toggles for every rule group, prompt variant, and repair policy. Toggles are sorted by portability (general → task-specific → dataset-specific → benchmark-format).
- **Ghost paths:** Hovering an ablation toggle previews the ablated path as a faint ghost without committing.
- **Architecture comparator:** Save two architectures as "A" and "B" cards above the canvas. The entire app enters comparison mode.

**Data consumed:**
- `AblationConfig` schema
- Rule metadata from `deterministic/rule_metadata.py`
- Prompt version taxonomy from LLM modules

---

### 4.3 The Observatory (Corpus Results & Run Ladder)

**Purpose:** Aggregate results across validation prefixes and locked test. Surface the generalisation gap and saturation state.

**Layout:**
- **Top:** The **Run Ladder** as a flight trajectory.
  - Nodes: 25 (smoke) → 50 (signal) → 250 (decision gate) → 750 (rare full) → Test (locked holdout).
  - Each node is a mission badge showing Purist F1 and Pragmatic F1.
  - **Saturated surfaces** (comparator near ceiling) are rendered with a translucent "full moon" glow—beautiful but explicitly labelled *low-information*.
  - **Hard panels** and **test audits** glow sharper and brighter.
  - Hover reveals run metadata: model, prompt version, git commit, working-tree note.

- **Middle:** The **Generalisation Gap** as a physical gorge.
  - Left cliff = validation aggregate.
  - Right cliff = test aggregate.
  - The distance between them is the gap, coloured by error family (temporal conflict = blue, seizure-free boundary = green, etc.).
  - Clicking a bridge segment filters the Error Gallery to exactly those rows.

- **Bottom:** An interactive **confusion matrix heatmap**.
  - Cells sized by support.
  - Clicking a cell expands into a mosaic of note cards from that confusion cell.
  - Off-diagonal cells have an "autopsy" icon linking to the stage-by-stage failure trace.

**Data consumed:**
- `experiments/registry.jsonl`
- JSONL artifacts per run
- `evaluate_predictions` output (micro/macro/weighted/per-label)

---

### 4.4 The Error Gallery (Failure Autopsy)

**Purpose:** Curated, browsable failure analysis. Understand *why* a configuration failed and compare architectures on their actual mistakes.

**Layout:**
- **Left sidebar:** Error taxonomy as a collapsible tree.
  - Categories: Temporal Conflict, Seizure-Free Boundary, Cluster/Diary Miss, No-Reference vs. Unknown, Proxy/Boundary Gate, etc.
  - Each category shows a count and a "severity sparkline" (contribution to the generalisation gap).
- **Main grid:** **Specimen cards**—one per error.
  - Excerpt, gold label, predicted label, and a mini stage-trace (3–4 coloured dots; the divergence stage is enlarged and red).
- **Autopsy view:** Opens a full Workbench for that note, with the first divergence stage pre-highlighted and a side-by-side comparison to the gold path.

**Comparison mode:**
- Select two architectures. The gallery becomes a **transition matrix**.
- Filter: "Show rows where Architecture A got wrong and Architecture B got right."
- Each card shows both traces, with the correcting stage annotated.

**Data consumed:**
- Row-level error analysis artifacts (e.g., `experiments/*_failure_review_*.md` and JSONL decision records)
- Per-record `y_true`, `y_pred`, `method`

---

### 4.5 The Rule Laboratory (Controlled Variables)

**Purpose:** Treat deterministic rules as explicit experimental variables. Toggle, simulate, and understand impact.

**Layout:**
- **Rule inventory:** Filterable card grid of every rule.
  - Rule ID, regex preview on hover, portability badge, test coverage, on/off toggle.
  - Border colour by rule group (rate = blue, temporal = green, diary = purple, benchmark repair = gray).
- **Live ablation panel:** Toggle rules, click "Simulate." The app runs against validation and returns:
  - Score delta (±F1)
  - Error family shifts
  - Regression alert if previously correct rows flipped
- **Rule interaction graph:** Force-directed graph showing which rules co-fire. Thick edges = rule clusters; isolated nodes = portability candidates.

**Data consumed:**
- `deterministic/rules/` metadata
- `AblationConfig` and simulation results
- Per-rule firing counts from diagnostics

---

## 5. UI Patterns for Transparency & Modularity

### 5.1 The Stage Lens Zoom
Like microscope objectives (4× → 10× → 40× → 100×):
- **4× (Raw):** Just the note, no highlights.
- **10× (Extract):** Candidate spans highlighted with rule IDs.
- **40× (Normalise):** Normalised values floating above spans.
- **100× (Select):** Only selected evidence remains bright; rejected candidates fade to 20%.
- **Oil immersion (Score):** Gold label appears as a ghost overlay; mismatches pulse.

### 5.2 The Attribution Waterfall
For any final label, a horizontal stacked bar showing semantic ownership:
```
[deterministic_extraction 70% | llm_adjudication 20% | format_repair 10%]
```
If the LLM segment is wide but deterministic found no candidates, the user immediately sees the pipeline is LLM-dependent for that case.

### 5.3 The Generalisation Thermometer
A vertical thermometer beside each result set:
- **Green zone:** Validation aggregates with known saturation.
- **Yellow zone:** Hard-slice and synthetic panel results.
- **Red zone:** Locked test results.
The mercury level only reaches "green" for validation; test results get a more solemn visual treatment to reinforce split discipline.

### 5.4 The Prompt Variant Diff
For LLM architectures, switching prompt versions shows a **unified diff** of the templates. Changed instructions highlighted; schema constraints shown as before/after JSON. Prompt engineering becomes code review, not alchemy.

### 5.5 The Ghost Gold Overlay
Toggle the gold label as faint, elegant handwriting in the margin.
- Match = calm green ghost.
- Mismatch = ghost points to the correct span with a thin line; predicted span is coral.
This transforms error analysis from spreadsheet work into a **reading experience**.

---

## 6. Visual Design System

### 6.1 Palette

| Role | Hex | Usage |
|------|-----|-------|
| Background | `#faf9f7` | Warm clinical white with subtle grid lines |
| Deterministic | `#2a6f6f` | Steel teal; precision, mechanical reliability |
| Deterministic alt | `#4a6fa5` | Slate blue for secondary rule groups |
| LLM | `#d97706` | Amber; adaptive intelligence |
| LLM alt | `#f59e0b` | Warm gold for highlights |
| Hybrid interface | `#7c3aed` | Purple only where teal and amber meet |
| Error | `#e07a5f` | Muted coral; research failure, not ICU alarm |
| Error alt | `#f4a261` | Sage warning tones |
| Success | `#81b29a` | Soft moss green; restrained celebration |
| Text primary | `#1a1a1a` | Near-black for UI chrome |
| Text secondary | `#6b7280` | Gray for metadata, timestamps, commit hashes |
| Gold ghost | `#d4af37` | Faint gold for gold-label overlay |

### 6.2 Typography

| Role | Font | Size | Weight |
|------|------|------|--------|
| Clinical notes | Source Serif Pro or Charter | 16 px | 400 |
| UI / data | Inter or SF Pro | 14 px | 400–600 |
| Monospace | JetBrains Mono | 12–13 px | 400 |
| Stage headers | Inter | 11 px | 600 uppercase |

Line height for clinical notes: 1.6. UI elements: 1.4.

### 6.3 Motion

- **Highlight activation:** Fluorescent-tag effect—quick fade-in (~150 ms) with a subtle glow.
- **Stage transitions:** Lens-swap metaphor: note stays fixed; annotation layer cross-fades (~200 ms).
- **Score updates:** Count-up with settling effect, like a precision balance.
- **Saturated surfaces:** Slow, ambient pulse (not celebratory; more like a full reservoir gently breathing).

---

## 7. Technical Architecture

### 7.1 Backend (unchanged + thin FastAPI wrapper)

The backend reuses the existing `clinical_extraction` package exactly. No scoring, pipeline, or artifact logic is reimplemented.

**Endpoints:**

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/run/note` | Run any configured pipeline on a single note; return full `PipelineResult` diagnostics |
| `POST` | `/run/ablation` | Run a batch with a specific `AblationConfig` against a split |
| `GET` | `/artifacts/{run_id}` | Serve a JSONL artifact from `experiments/` |
| `GET` | `/registry` | Index of all runs from `experiments/registry.jsonl` |
| `GET` | `/splits/{split_name}` | Row indices and metadata for a split manifest |
| `GET` | `/rules` | Inventory of all deterministic rules with metadata |
| `GET` | `/prompts` | Inventory of prompt versions and policy taxonomies |
| `GET` | `/records/{split_name}` | Lightweight list of all records in a split (index, gold label, preview) |
| `GET` | `/records/{split_name}/{source_row_index}` | Full record for a single row (note text, gold label, metadata) |

**Data sources:**
- `experiments/registry.jsonl` — canonical run log
- `experiments/*.jsonl` — per-run decision records and diagnostics
- `data/Gan (2026)/splits/gan2026_split_v1.json` — split discipline
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic/rules/` — rule metadata

### 7.2 Frontend

- **Framework:** Next.js 14+ (App Router) + TypeScript + Tailwind CSS
- **State management:** Zustand for global config comparison mode; React Query for server state
- **Pipeline canvas:** React Flow for the Architect view
- **Custom visualisations:** D3.js for confusion matrix, generalisation gap, rule interaction graph, and run ladder
- **Virtualised lists:** React Virtuoso for the Error Gallery
- **Note rendering:** Custom `NoteRenderer` component that takes raw text + evidence spans with `start_char`/`end_char` and renders them as absolutely-positioned highlight layers. This is critical for pixel-accurate evidence visualisation.

### 7.3 Data contract (Frontend ↔ Backend)

The frontend consumes the **exact JSONL schemas** already produced by the repo. No translation layer.

Key schemas consumed:
- `PipelineResult[FinalExtraction]` with nested `diagnostics`
- `CandidateEvent` / `NormalizedEvent` / `FinalSelection` from `pipeline_v1.py`
- `decision_record` from hybrid adjudicator runs
- `AblationConfig` from `rule_metadata.py`
- `evaluate_predictions` output structure

**Configuration serialisation:**
Any UI toggle state must serialise to a named config object that can be:
1. Saved as a URL parameter for sharing.
2. Exported as JSON and fed into `gan2026-llm-experiment --pipeline ...` or deterministic V1 ablation CLI.
3. Versioned and stored in localStorage for quick recall.

---

## 8. Implementation Phasing

### Phase 1: The Specimen (Single-Note Workbench)
**Goal:** A powerful internal debugging and demo tool.

**Implemented:**
- ✅ FastAPI backend scaffold (`create_app`) with all Phase 1 endpoints
- ✅ Next.js 16 frontend scaffold under `frontend/` with Tailwind CSS
- ✅ `NoteRenderer` with evidence span overlays, formal-letter formatting, and `\n` unescaping
- ✅ Stage navigator with expandable cards, active-stage accent bars, and stage-specific highlight colours
- ✅ Dataset loading workflow — split selector + row picker loads real Gan 2026 records
- ✅ Attribution waterfall (currently deterministic-only; ready for hybrid/LLM attribution)
- ✅ Gold label text display below note (available from dataset record or pipeline run)
- ✅ React Query + Zustand data layer with typed API wrappers
- ✅ **Ghost Gold overlay** — margin-styled box with match/mismatch colouring (green for match, coral for mismatch, gold when unknown)
- ✅ **Rich hover cards** — Radix Tooltip floating cards showing rule ID, group, portability, and label for every highlighted span
- ✅ **Pipeline family selector** — dynamically populated from `/pipeline-families`; all families visible with executable vs introspection-only badges; non-executable pipelines disabled at run time
- ✅ **Diff mode (A vs B)** — toggle in config panel selects a second pipeline family; compare badge appears in header; URL-synced
- ✅ **URL serialisation** — full config state (pipeline, split, row, note text, ablation toggles, stage, gold overlay, diff mode) serialised to query params and restored on load; shareable links
- ✅ **Rule toggles in UI** — per-group and per-rule on/off toggles in the config panel with live visual feedback

**Rudimentary / deferred to Phase 2–4:**
- 🟡 Thin line from Ghost Gold overlay pointing to the correct span (requires per-span gold evidence mapping)
- 🟡 Side-by-side span diff visualization in the note surface (diff mode stores config B but does not yet render overlay diffs)
- 🟡 LLM and hybrid pipelines are not yet executable via `/run/note` (backend uses `EXECUTABLE_PIPELINES` gate; requires DSPy LM setup)

### Phase 2: The Architect (Pipeline Composer)
- React Flow canvas with draggable nodes.
- Wire `AblationConfig` toggles to UI.
- Architecture comparison mode (A vs B).
- Export named config to JSON.

### Phase 3: The Observatory (Corpus & Ladder)
- Index `experiments/registry.jsonl` and existing JSONL artifacts.
- Run ladder visualisation with saturation indicators.
- Confusion matrix heatmap with expandable cell mosaics.
- Generalisation Gap gorge visualisation.

### Phase 4: The Laboratory (Rules & Ablations)
- Rule inventory with live simulation.
- Rule interaction graph.
- Error Gallery with taxonomy filtering and transition matrix.
- Prompt variant diff viewer.

### Phase 5: The Review (Paper-Ready Export)
- Exportable component ablation tables.
- Exportable error taxonomy summaries.
- Evidence-validity rate summaries.
- Per-label purist/pragmatic performance tables.
- Designed to generate the exact tables and figures described in `docs/research/contribution_thesis.md`.

---

## 9. Open Questions & Deferred Backend Extensions

The following are *not* required for Phase 1–2 but are noted for future backend design when the UI demands deeper composability:

1. **Finer-grained rule firing telemetry.** The UI wants to show *which exact rule* fired on *which exact span* for every candidate. Current diagnostics provide this for V1; LLM-only pipelines may need structured `rule_suggestions` or `repair_trace` fields.
2. **Standardised error taxonomy tagging.** The Error Gallery would benefit from a programmatic error taxonomy (e.g., `temporal_conflict`, `seizure_free_boundary`) attached to each row at evaluation time, not only in Markdown reports.
3. **Hard-slice reproducibility API.** Validation hard slices are currently defined in analysis scripts. A backend endpoint that returns row IDs for a named hard slice (e.g., `temporal_conflict_slice_v1`) would let the UI filter without reimplementing slice logic.
4. **LLM prompt template registry.** Prompts are currently embedded in Python modules. A registry endpoint (or a YAML/JSON prompt manifest) would let the Architect view list variants without importing Python.
5. **Real-time ablation simulation caching.** Running a full validation ablation on every toggle is expensive. A lightweight result-cache keyed by `AblationConfig` hash would make the Rule Laboratory responsive.
6. **Cross-run diff at the record level.** The Error Gallery's transition matrix needs to align records across two JSONL artifacts by `source_row_index`. This is trivial if both artifacts include stable indices; it should be enforced as an output contract.

**Decision:** None of the above blocks initial development. The frontend should be built against the *current* artifact schemas, and backend extensions should be added only when a specific UI pattern proves impossible without them.

---

## 10. Appendices

### A. Glossary

| Term | Meaning in this document |
|------|--------------------------|
| Specimen | A single clinical note under inspection |
| Stage | One transformation step in the pipeline (Extract, Normalise, Select, Repair, Score) |
| Ghost path | A preview of what would change if an ablation were applied |
| Specimen card | A compact UI card representing one record in the Error Gallery |
| Saturation | A validation surface where the comparator is near ceiling and aggregate F1 is low-information |
| Ghost Gold | The gold-label overlay on a note, rendered as faint handwriting |
| Attribution waterfall | A stacked bar showing semantic ownership of a final label |

### B. Related Documents

- `docs/research/contribution_thesis.md` — research claims the Observatory should make tangible
- `docs/design/data_contract.md` — Gan 2026 data contract
- `docs/design/gan2026_split_protocol.md` — split discipline that the Observatory must visually enforce
- `docs/design/gan2026_saturated_validation_protocol.md` — saturation language that the Observatory must surface
- `docs/decisions/0004-gan2026-package-organization.md` — package boundaries that inform Architect node families

### C. URL Structure (Proposed)

```
/                     → Landing / task selector
/workbench            → Single-note inspector (default empty, loadable)
/workbench?config=v1&note=1234&compare=v2
/architect            → Pipeline composer
/observatory          → Corpus results and run ladder
/observatory?runs=v1,v2,v3
/gallery              → Error gallery
/gallery?transition=a_wrong_b_right&arch_a=v1&arch_b=v2
/laboratory           → Rule inventory and ablation simulator
```

---

*This document is a durable plan. It should be revised when implementation discoveries change technical constraints, when backend extensions are made, or when user-testing reveals that a view or pattern is not achieving its transparency goal.*
