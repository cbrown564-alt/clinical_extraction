# Clinical Extraction Explorer: UI Review and Next Steps

This report details the recent architectural changes, critiques the current visual style and navigation flow, highlights component polish opportunities, and investigates potential performance bottlenecks.

---

## 1. Summary of Changes

The frontend has been reorganized to align directly with the primary user journey: **demonstrating how extraction pipelines work from micro (individual note) to macro (run comparison) levels**.

1.  **Rebranded Terminology**: Changed navigation labels and titles from the scientific motif to explicit names:
    *   `Workbench` $\rightarrow$ **Example Explorer** (Single patient note inspection)
    *   `Observatory` + `Review` $\rightarrow$ **Aggregate Performance** (Comparative run evaluations)
    *   `Laboratory` $\rightarrow$ **Component Impact** (Ablation sandbox & prompt diffs)
    *   `Gallery` $\rightarrow$ **Error Gallery** (Failure case analysis)
    *   `Gold Audit` $\rightarrow$ **Gold Label Audit** (Standalone validation dataset QA)
2.  **Dashboard Consolidation**: Merged the `/review` report builder and the `/observatory` visualization tabs (Generalisation Gap and Confusion Matrix) into a unified page under `/observatory` (labeled **Aggregate Performance**).
3.  **Deleted Duplicated Routes**: Removed the redundant `/review` route folder entirely.
4.  **Isolated Auditing**: Moved the `GoldAuditPanel` into its own standalone route (`/gold-audit`, labeled **Gold Label Audit**) to separate secondary data cleaning tasks from main demonstration flows.
5.  **Fixed UI and Style Bugs**:
    *   Corrected the missing `bg-primary` color in the `PaperTable` sparkline to `bg-deterministic-alt` (slate blue).
    *   Corrected the missing `text-primary` color in the `ConfusionMatrix` link to `text-deterministic` (teal) and updated its target name to `"Explorer"`.

---

## 2. Style & Nav Assessment

### Holistic Style
*   **The Good**: The application uses a beautifully structured color system based on a soft, warm off-white background (`#faf9f7`) and clear semantic color tokens (`deterministic` teal, `deterministic-alt` slate blue, `llm` amber, and `hybrid` purple). This immediately gives it a premium, deliberate feel.
*   **Consistency Gaps**:
    *   *Typography*: The app mixes fonts appropriately (JetBrains Mono for JSON/metrics, Source Serif for clinical notes, Inter for interface elements). However, font size hierarchies could be tighter. Some metrics use `text-2xl` while headers use `text-xs uppercase font-semibold`, creating a slight visual disconnect in information density.
    *   *Borders & Shading*: The "paper style" card borders (`border-border`) are consistent, but some tabs use varying hover states. For example, some buttons scale up on click (`active:scale-[0.98]`), while others transition background color. A single micro-animation design system should govern all buttons/tabs.

### User Journey Navigation
*   **Main Flow (Micro to Macro)**:
    1.  **Example Explorer** is the ideal entry point. It demonstrates step-by-step how a single patient note is parsed, candidates are extracted, normalized, selected, and scored.
    2.  If the developer wants to see if these rules hold up at scale, they switch to **Aggregate Performance** to compare runs.
    3.  To isolate where a specific run fails, they open the **Error Gallery**.
    4.  To tweak rule behaviors or prompt formatting to fix these failures, they use the **Component Impact** sandbox.
*   **Improvement Opportunity**: The links between pages should be more contextual. Currently, the Error Gallery links back to the Example Explorer via an `"Explorer"` link. We should introduce similar contextual deep-linking elsewhere. For example:
    *   Clicking a category confusion in the Confusion Matrix should deep-link directly to the **Error Gallery** filtered for that specific confusion pair.
    *   Clicking a rule in **Component Impact** should link to the **Example Explorer** showing which nodes in the current trace fired that rule.

---

## 3. Polish & Quality Review

To make the primary components feel exceptionally state-of-the-art, we should target the following:

*   **Clinical Note Highlighting**: In the Example Explorer and Gold Label Audit pages, highlighted text spans are styled with a flat background tint and thin underline. Replacing this with rounded, smooth, semi-transparent highlight pills with subtle enter animations would dramatically elevate the feel of the document reader.
*   **Confusion Matrix**: The matrix is currently rendered using flat HTML buttons with inline CSS opacity modifications. Replacing this grid with custom svg/canvas grids or styled layout-driven Flex containers with CSS tooltips and smooth hover scaling would look much more premium.
*   **Interactive Simulation States**: Running simulation ablations in the **Component Impact** page can take time. The current spinner is simple. Replacing it with a structured progress tracker (e.g., "Step 1: Parsing rule config...", "Step 2: Simulating run...") makes the tool feel active and robust.

---

## 4. Performance Deep Dive

A review of client-side state and rendering code reveals three critical performance bottlenecks:

### A. Dynamic Large-JSONL Processing (Main Thread Blocking)
*   **The Issue**: In `useObservatoryData.ts`, when a user selects a run, the raw JSONL content is fetched and computed entirely client-side:
    ```typescript
    const summary = computeSummary(entry, allRows);
    ```
    `computeSummary` iterates over all records to compute confusion matrices, TP/FP/FN rates, and F1 metrics.
*   **The Risk**: If a run contains the full test split (10,000 rows), this calculation runs on the main browser thread. This will block the thread for several hundred milliseconds, freezing the UI and triggering browser warning logs (Long Tasks).
*   **Recommendation**: Move the summarization to the backend API. The endpoint `/api/artifacts/{runId}` should return a pre-computed summary object containing metrics and matrix structures, rather than sending the raw rows of evaluation data to the client for summary computation.

### B. DOM Bloat in the Error Gallery
*   **The Issue**: In `gallery/page.tsx`, `SemanticErrorGroups` groups and renders rows that match the filter:
    ```typescript
    {groupRows.map((row) => ( ... ))}
    ```
*   **The Risk**: If multiple runs are selected or a large split is evaluated, `groupRows` can contain thousands of items. Rendering 1,000+ interactive, collapsible HTML elements simultaneously will crash browser scroll performance and cause severe lags during tab switches or filter selections (poor INP - Interaction to Next Paint).
*   **Recommendation**: Implement **list virtualization** (using a library like `@xyflow/react` or a lightweight virtual list helper) so that only the visible rows in the viewport are mounted in the DOM. Alternatively, add pagination or a client-side limit of 100 rows with a "Load more..." trigger.

### C. Large Memory Footprint
*   **The Issue**: The `useObservatoryData` hook caches raw rows in a state map:
    ```typescript
    const [summaries, setSummaries] = useState<Map<string, RunSummary>>(new Map());
    ```
*   **The Risk**: Keeping multiple datasets of thousands of rows with evidence string fragments and rationales in client memory will lead to high heap allocations and eventual tab crashes on low-spec client machines.
*   **Recommendation**: Modify the client state so that it only stores the high-level metrics for dashboard rendering. Detailed rows should only be fetched lazily when a specific page (like the Error Gallery) is active, and only in paginated chunks.

---

## 5. Next Steps

Based on this critique, here is the roadmap for UI simplification and quality improvements:

### Phase 0: Ultra-Critical Component Audit (What Deserves to Exist?)

Before polishing or optimising, we must ask: **does every page, tab, and component earn its place in the core user journey?** The frontend has accumulated features that are intellectually interesting but clinically superfluous. Complexity is not free — every tab adds decision fatigue, every component adds maintenance surface, and every superfluous data fetch worsens performance.

#### Navigation Level: 5 Pages → 4 Core + 1 Secondary
The primary journey is: *Example Explorer → Aggregate Performance → Error Gallery → Component Impact*. **Gold Label Audit** is a data-cleaning annotation tool, not a pipeline demonstration. It should not have equal billing in the top nav. Move it to a dropdown menu, a footer link, or contextually from the Example Explorer ("Audit gold labels for this note").

| Page | Verdict | Action |
|------|---------|--------|
| Example Explorer | **Essential** | Keep as primary entry point |
| Aggregate Performance | **Essential** | Keep, but slash tab count (see below) |
| Error Gallery | **Essential** | Keep, but virtualise lists |
| Component Impact | **Conditional** | Keep Rule Inventory tab; remove or hide the rest |
| Gold Label Audit | **Secondary** | Demote from top nav |

#### Aggregate Performance: 8 Tabs → 3 Core + Inline Actions
The `ReportBuilder` currently carries **eight tabs**. This is overwhelming. Most users selecting a few runs want to see: (1) how they compare, (2) where they confuse categories, and (3) whether they generalise. Everything else is diagnostic noise that belongs in expandable drawers or an advanced mode.

- **Run Comparison** — **Keep**. This is the anchor tab. Merge the `ExportPanel` into this view as a sticky header action ("Copy report" / "Download .md" buttons) rather than a separate tab. The Export tab currently duplicates Run Comparison and Error Taxonomy tables anyway.
- **Confusion Matrix** — **Keep**. But rebuild it properly (see Phase 2).
- **Generalisation Gap** — **Merge into Run Comparison**. It currently wastes a full tab to display "No test data available" for 80% of runs. Make it an inline expandable section within Run Comparison that only renders when `testMetrics` exist, or a toggle-able chart row beneath the comparison table.
- **Per-Label Performance** — **Remove as tab**. A 12-category × 4-metric × N-runs table is overwhelming and rarely the first thing a user needs. Collapse it into an "Advanced metrics" drawer within Run Comparison, or make it a downloadable CSV only.
- **Error Taxonomy** — **Remove entirely**. The Error Gallery exists for this exact purpose and does it better — with semantic grouping, severity scoring, evidence display, and filtering. A dry table of error counts per run is strictly worse.
- **Evidence Audit** — **Remove as tab**. Exact evidence rate, repair rate, and average evidence length are deep diagnostic metrics for pipeline authors, not demonstration viewers. Add them as optional columns in Run Comparison (hidden by default) or move to a diagnostics JSON export.
- **Hard Slices** — **Remove as tab**. This displays static slice definitions from the backend — essentially documentation. It does not change based on run selection and requires no interactive analysis. Move it to a help tooltip, a docs page, or a modal.
- **Export Report** — **Remove as tab**. Export is an action, not a view. The `ExportPanel` assembly widget should live as a persistent control in the Run Comparison header.

**Proposed tab bar:** `Run Comparison | Confusion Matrix`. That’s it. Generalisation Gap becomes an inline section. Everything else moves to drawers, CSV exports, or is deleted.

#### Component Impact: 3 Tabs → 1 Core + Optional Advanced Mode
The laboratory page has three tabs, but only one is load-bearing:

- **Rule Inventory** — **Essential**. The search, filter, group toggle, and simulation panel are the entire reason this page exists. Keep.
- **Co-Fire Matrix** — **Superfluous**. A static SVG grid showing which rule groups share portability levels. It is a visual curiosity, not a decision tool. It does not help a user decide which rules to toggle, it does not update based on simulation results, and the same information is already conveyed by portability badges in the Rule Inventory. **Remove.**
- **Prompt Diff** — **Superfluous / Niche**. Compares `PROMPT_POLICY_TAXONOMY` between prompt modules. The UI itself warns that most modules lack this taxonomy. When only 2 of 10+ modules have policy data, this tab is empty and confusing. Deep prompt archaeology belongs in a code diff tool or an "Advanced developer mode" toggle, not the main UI. **Remove or hide behind an advanced toggle.**

**Proposed tab bar:** Remove the tab bar entirely. The Rule Inventory + Simulation Panel is the page. If advanced features must survive, add a single "Show advanced" switch that reveals Co-Fire Matrix and Prompt Diff as secondary panels.

#### Error Gallery: 4 Sections → 3 (with caveats)
The gallery page is actually well-focused, but has one section that duplicates functionality:

- **Executive Summary** — **Keep**. The four-card summary (error rate, dominant error, top confusion, worst family) is exactly the right level of insight.
- **Error Distribution Bar** — **Keep**. The clickable stacked bar is an excellent filter control.
- **Dimensional Breakdowns** — **Split verdict**:
  - *Top Category Confusions* — **Keep with reservations**. It provides a quick ranked list of confused pairs, which is useful. However, it partially duplicates the Confusion Matrix. Keep it as a compact widget, but if space is tight, link to the Confusion Matrix instead.
  - *Errors by Pipeline Family* — **Remove**. If the user has already selected specific runs in Aggregate Performance, family-level aggregation is irrelevant. Worse, if they selected runs from only one family, this section is either empty or misleading. **Cut it.**
- **Semantic Error Groups** — **Keep, but virtualise**. This is the core of the gallery. The grouping by error type with collapsible sections is the right UX. The only problem is DOM bloat (already noted in §4B).

#### Example Explorer: Lean, but One Question Mark
The workbench is the most disciplined page. TraceControls, StageStrip, StageInspector, and NoteRenderer all serve clear, non-overlapping purposes. The five stages (Extract → Normalise → Select → Repair → Score) map directly to the pipeline architecture.

One component warrants scrutiny: **`AttributionWaterfall`** (rendered inside the Select stage). It displays a static visual of which pipeline families contributed to the final selection. If this is a decorative graphic that does not change based on the actual trace data, it is **cosmetic fluff**. Verify whether it shows live attribution data or is just a hardcoded diagram. If the latter, remove it or replace it with a simple text list of contributing rules.

#### Summary of Proposed Cuts
| Component / Tab | Current Location | Action | Rationale |
|-----------------|-----------------|--------|-----------|
| Gold Label Audit | Top nav | Demote to secondary | Not part of core demonstration flow |
| Per-Label Performance | Aggregate Performance tabs | Remove tab → drawer/CSV | Overwhelming detail; rarely first need |
| Error Taxonomy | Aggregate Performance tabs | Remove entirely | Error Gallery does this strictly better |
| Evidence Audit | Aggregate Performance tabs | Remove tab → optional columns | Deep diagnostic, not demo-critical |
| Hard Slices | Aggregate Performance tabs | Remove → docs/tooltip | Static reference data, not interactive |
| Export Report | Aggregate Performance tabs | Remove tab → header buttons | Export is an action, not a view |
| Generalisation Gap | Aggregate Performance tabs | Merge into Run Comparison | Most runs have no test data; wastes a tab |
| Co-Fire Matrix | Component Impact tabs | Remove | Visual curiosity, not a decision tool |
| Prompt Diff | Component Impact tabs | Remove / advanced toggle | Niche feature, empty for most modules |
| Errors by Pipeline Family | Error Gallery sections | Remove | Irrelevant when runs are pre-selected |
| AttributionWaterfall | Example Explorer / Select stage | Remove | Static decorative diagram, not data-driven |

**Estimated complexity reduction:** Removing 6+ tabs, 2 full pages-as-tabs, and 2 gallery sections would cut the active component surface by roughly **40%**, reduce the navigation decision space from 8 tab choices to 2, and eliminate several expensive data transformations (per-label metrics, evidence audits, error taxonomy tables) from the main thread.

### Phase 1: Streamline and Focus (Simplification)
1.  **Refine Empty States**: Ensure all pages have a unified, helpful empty state if no runs/notes are loaded, guiding users to select a baseline or load a patient note.
2.  **Contextual Navigation Linking**: Connect the tabs by passing state variables via URL search parameters (e.g., double-clicking a cell in the Confusion Matrix redirects to the Error Gallery with pre-selected filters).

### Phase 2: Premium Feel & Polish (High Quality)
1.  **Visual Highlight Polish**: Improve clinical note highlighting with smooth, premium styled CSS overlays.
2.  **Transition Effects**: Add subtle CSS transitions for collapsing drawers, tab switches, and card listings.
3.  **Virtualize Lists**: Integrate virtual rendering for the Error Gallery row items to keep scroll rates at a locked 60fps.

### Phase 3: Performance Refactor (Correctness & Scale)
1.  **Pre-compute Summaries**: Adapt the backend routes to serve metric summaries directly.
2.  **Lazy Data Loading**: Restructure `useObservatoryData` to fetch full row contents only when required by the Error Gallery or Example Explorer, rather than eager-loading all rows on selection.
