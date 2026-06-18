# Gan 2026 Repo Consolidation And Cleanup Plan

Date: 2026-06-07

Author: Claude

Status: completed execution record — originally a catalog-first,
dependency-audited cleanup plan; Phases A-G are now complete as of
2026-06-07. Historical deletions were performed through git-tracked lineage
batches, not destructive bulk operations.

---

## 1. Objective

The project has been in a long rapid-iteration phase and now contains, by a
fresh survey of `src/clinical_extraction/tasks/seizure_frequency/gan2026/`:

- **4 distinct hybrid/staged architecture lines** (`staged_hybrid_assembly`
  v0, `staged_assembly_v1`, `hybrid_parallel_state_candidate_reasoner`,
  `hybrid_rules_candidates_llm_adjudicator`) plus the current canonical
  `reset_clinical_assessment_pipeline`;
- **~25 files / 728 KB** under `llm/`, including 11 standalone
  `llm_only_*` experiments with no unified runner;
- **76 files** under `artifact_analysis/`, with heavy purpose-overlap in at
  least 9 clusters (ablation, verification/routing, boundary/seizure-free,
  candidate/state, projection/render/scoring, RQ-panels, validation surfaces,
  hidden-family/repair-policy, pressure/policy-routing);
- **~80 test files** mirroring this sprawl;
- a long tail of dated, narrowly-scoped research docs (the `Done Recently`
  section of `PROJECT_STATUS.md` alone lists dozens).

The objective is to end this phase deliberately: choose the **three
canonical architectures** (deterministic, fully-LLM, hybrid) plus their
shared infrastructure, remove everything else, consolidate the surviving
documentation into a small set of lineage summaries, and make what remains
DRY — one runner framework, one reporting framework, one CLI surface —
rather than one-off-per-architecture copies of each.

This is explicitly **not** a "keep everything just in case" exercise. The
user has been clear: prior architectures served their purpose by generating
evidence and shaping the path; that contribution should be *summarized in
documentation*, and the code/artifacts themselves should be removed, not
preserved as dead weight.

---

## 2. Sequencing: Where This Sits Relative To The Other Two Workstreams

The user asked explicitly whether cleanup should come before or after the
comparison study and the thesis assessment. The answer is **neither, in
full** — it is a **select → clean → iterate** loop:

1. **First**, make the *minimal* selection decision needed to know what to
   keep: name one canonical runner per architecture. This is exactly
   [[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
   Section 2 (Phase 0) — it is a *light*, structural decision, not the full
   comparison study. Do it once, here, and let the comparison plan consume
   the result.
2. **Then**, do the cleanup described in this plan (Phases A-G below) on the
   chosen representatives plus shared infrastructure. This is the right
   moment because: (a) we now know what to keep, so nothing useful is
   deleted by mistake; (b) doing it now means the upcoming comparison study
   and thesis assessment are built on a clean, DRY substrate instead of
   further entrenching duplicated infrastructure that would just need
   re-cleaning later.
3. **Then**, run the full comparison
   ([[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]])
   and thesis assessment
   ([[gan2026_evidence_grounded_thesis_assessment_plan]]) on the cleaned
   codebase. Their outputs become the **final, canonical, kept artifacts** —
   not throwaway experiments layered on top of a mess that still needs
   cleaning afterward.

**Rationale against the alternatives**: cleaning up *before* any selection
decision risks deleting something that turns out to matter once the
comparison runs (e.g., discovering mid-study that
`hybrid_parallel_state_candidate_reasoner` actually contains the only
working comparator for a needed condition). Doing the *full* comparison and
thesis study *before* any cleanup means building new canonical artifacts on
top of — and further duplicating — the very infrastructure that needs
consolidating, which doubles the eventual cleanup cost and risks the new
artifacts inheriting the same sprawl. The light-selection-first sequencing
avoids both failure modes.

---

## 3. Phase A — Catalog And Categorize

Build one master inventory (a single machine-readable table, e.g. JSON or
CSV, plus a markdown summary) with one row per file/module under the
`gan2026` tree, with columns:

- path
- architecture lineage: `deterministic` / `llm-only` / `hybrid-staged-v0` /
  `hybrid-staged-v1` / `hybrid-parallel-state` / `hybrid-rules-adjudicator` /
  `hybrid-reset-current` / `shared-infrastructure` / `unclear`
- role: runner / contract-schema / component / analyzer / report / test /
  doc / experiment-artifact
- status (filled in during Phase B/C): `canonical` / `superseded-candidate`
  / `shared-keep` / `needs-decision`

The survey already performed for this planning round (directory map, runner
list, artifact-analysis duplication clusters, test grouping) is the seed
data for this catalog — it does not need to be redone, only formalized into
the structured table.

This catalog is also exactly the input
[[gan2026_evidence_grounded_thesis_assessment_plan]] Phase 1 needs for its
own analyzer-to-thesis-axis mapping. **Do this survey once and let both
workstreams consume it** — do not let two parallel catalogs drift apart.

---

## 4. Phase B — Canonical Selection

For each of the three architecture types, name exactly one canonical
runner (this *is*
[[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
Section 2, restated here as the cleanup-facing decision):

| Architecture | Canonical choice | Rationale |
| --- | --- | --- |
| Deterministic | `pipeline_v1.py` (`Gan2026PipelineV1`) | the only fully-deterministic runner that exists; default canonical, subject to the de-overfitting refinement in the comparison plan |
| Hybrid | `hybrid/reset_clinical_assessment_pipeline.py` | already explicitly named the "current focus" / canonical reset architecture in `PROJECT_STATUS.md` |
| Fully LLM | **to be assembled** — no single runner exists yet; pick one `llm_only_*` module as the Select-stage front end (recommended: `hybrid_structured_events` or `llm_only_minimal_evidence_selector`, per the comparison plan's "Option A" recommendation) and chain it through the existing deterministic Normalize→Render→Score→Route→Decision stages | produces the one comparable artifact shape needed by both other workstreams |

**Everything else in the hybrid/staged lineage is a superseded-candidate**,
pending the dependency audit in Phase C:

- `hybrid/staged_hybrid_assembly.py` (v0)
- `hybrid/staged_assembly_v1.py` (v1)
- `hybrid/hybrid_parallel_state_candidate_reasoner.py`
- `hybrid/hybrid_rules_candidates_llm_adjudicator.py`
- `hybrid/hybrid_adjudicator_parser.py` (support module for the above)

**The 10 non-canonical `llm_only_*` modules** become superseded-candidates
once one is chosen as canonical — *unless* the comparison plan's "Option B"
(maximal-LLM comparator, see that plan Section 2) is judged necessary, in
which case exactly one more survives as the second comparator and the
remaining ~9 become candidates.

---

## 5. Phase C — Dependency Audit

For every file marked `superseded-candidate` in Phase B, before proposing
removal, check and record:

1. **Import graph**: does any *kept* module import from it? (grep for the
   module path / class names)
2. **CLI registry**: is it registered in `cli/llm_pipeline_cli.py`?
3. **Test coverage**: which files in `tests/test_gan2026_*.py` exercise it
   directly?
4. **Observatory / registry**: is it referenced in `experiments/registry.jsonl`,
   `observatory/api.py`'s `/pipeline-families`, or the frontend
   `traceAdapter`?
5. **Documentation**: which `docs/research/*.md` and `PROJECT_STATUS.md`
   entries describe it as current (versus historical)?

Each file gets a removal-readiness verdict:

- **safe-to-remove**: no live dependents found
- **needs-test-removal-first**: tests reference it; remove tests in the same
  batch
- **needs-doc-archival-first**: described as current somewhere; fold its
  contribution into the Phase D lineage doc, then update/retire the
  reference
- **needs-registry-update-first**: still wired into CLI/observatory; unwire
  before removing
- **blocked — has live dependents**: a kept canonical module actually
  depends on it; this is itself a finding (it means the "superseded"
  candidate is not actually superseded, and either the canonical choice in
  Phase B needs revisiting, or the dependency needs to be ported into the
  canonical line first)

---

## 6. Phase D — Historical Documentation Consolidation

Per the user's explicit instruction: **keep some documentation summarizing
prior architectures' contributions; remove the rest** (code, docs, and
artifacts alike).

Plan:

1. Write **one** consolidated document —
   `gan2026_architecture_lineage_and_retired_approaches_<date>.md` — that
   gives each retired line a short, durable summary: what it tried, what it
   taught the project, and what (if anything) of its approach survived into
   the canonical lines. For example: *"`staged_assembly_v1` introduced the
   h5/h6/h9/h10 policy-marker pattern; this was superseded by the reset
   pipeline's named-stage-ownership model, which generalizes the same idea
   without bespoke marker codes."*
2. Once that lineage doc exists and is reviewed, the dozens of scattered
   dated research docs that describe now-retired architectures' internals
   (not their lasting contribution) become removable — their *load-bearing
   content* has been compressed into the lineage doc, and their narrow,
   point-in-time content has served its purpose.
3. Apply the same compression logic to `PROJECT_STATUS.md`'s `Done Recently`
   section over time: once an entry's contribution is captured in a lineage
   or synthesis document, the long-form entry can be trimmed to a one-line
   pointer.

This phase is what makes the removal in Phase E defensible: nothing is lost,
it is *compressed* — exactly mirroring what the user described prior
architectures as having already done for the project ("they served the
purpose of providing evidence and shaping our path").

---

## 7. Phase E — Removal

Execute removals in **small, reviewable, single-lineage batches** — not one
giant deletion commit:

1. One architecture lineage at a time (e.g., all of `staged_assembly_v1` and
   its exclusive test/doc/registry dependents in one batch).
2. Run the full test suite between batches; confirm green before proceeding
   to the next lineage.
3. Use `git rm` so history is preserved and the change is reviewable as a
   normal diff — never bulk-delete outside git or rewrite history.
4. Update `PROJECT_STATUS.md` and the observatory registry as part of the
   same batch that removes the corresponding code, so the repo never sits in
   an inconsistent "doc says X exists but code doesn't" state.

---

## 8. Phase F — DRY-ification Of Shared Infrastructure

Once only the three canonical architectures (plus their lineage-summary
docs) remain, generalize the shared mechanics that are currently duplicated
per-architecture:

1. **Pipeline runners**: `reset_clinical_assessment_pipeline.py` already
   demonstrates the right shape — compose named stage-builders into one
   replayable bundle with a shared artifact contract. Generalize this into
   one runner framework parameterized by *which stage is LLM-owned versus
   deterministic*, so the deterministic, hybrid, and fully-LLM runners become
   three configurations of one framework rather than three separate
   code-bases. This directly produces the comparable-artifact-shape
   requirement that
   [[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
   needs.
2. **Reporting / artifact analysis**: collapse each overlap cluster found in
   the survey into one parameterized analyzer reusing `reports/base.py`:
   - the ~12 ablation analyzers → one scoped-ablation analyzer
   - the ~10 boundary/seizure-free analyzers → one diagnostic module with
     named scopes
   - the ~11 candidate/state analyzers → one candidate-state matrix module
   - the ~5 projection/render/scoring analyzers → one projection-scoring
     module (this becomes the natural home for the
     [[gan2026_evidence_grounded_thesis_assessment_plan]] scorecard
     aggregation, too — build it there rather than as a 77th file)
3. **CLI**: collapse the registry-of-standalone-scripts pattern in
   `cli/llm_pipeline_cli.py` into entries that point at the new unified
   runner framework's three configurations, rather than at a long list of
   individually-bespoke experiment scripts.

---

## 9. Phase G — Verification And Sign-Off

Completed on 2026-06-07:

- Full Python suite green at sign-off: `997 passed`.
- Observatory `/pipeline-families` now exposes exactly the canonical families
  plus explicitly retained registry-backed comparators:
  - canonical: `rules_only`, `llm_only_direct_labeler`,
    `hybrid_structured_events`, `reset_clinical_assessment_pipeline`;
  - retained comparators:
    `dspy_final_selection_adjudicator`,
    `hybrid_clinical_frequency_state_graph`, `llm_first_direct_extractor`,
    `llm_heavy_clinical_frequency_reasoner`,
    `llm_heavy_evidence_selection_with_deterministic_adapters`,
    `llm_replacement_postprocessing_ablation`, and
    `llm_structured_events`.
  Retired and unreviewed registry strings remain queryable through
  `/registry` but are filtered out of active `/pipeline-families`.
- `PROJECT_STATUS.md` now describes the post-cleanup baseline: retired
  lineages are historical-only, canonical runner work continues on the shared
  runner/CLI surface, and the lineage doc is the pointer to removed
  architecture history.
- Closing accounting:
  - Phase E removal batches deleted `159` tracked files and reduced the tree
    by a net `56,476` lines across the five lineage-removal commits.
  - Phase F replaced `32` surveyed overlap-cluster memberships with four
    official cluster-level analyzer modules:
    `scoped_ablation_analyzer`, `boundary_diagnostic`,
    `candidate_state_matrix`, and `projection_scoring`.
  - The resulting DRY framework is `gan2026.runner` for pipeline/CLI
    configuration plus the Phase F analyzer registry in
    `artifact_analysis/__init__.py`. Remaining `artifact_analysis/` files are
    retained source-specific producers, narrow diagnostics, or historical-read
    helpers, not competing cluster-level APIs.

---

## 10. Guardrails

- **Catalog and audit before any deletion.** Phases A-C produce a written,
  reviewable proposal; nothing is removed until that proposal is reviewed.
- **Compress, don't discard, the lessons.** Phase D must complete — and be
  reviewed — before Phase E begins for any lineage whose contribution is not
  yet captured elsewhere.
- **No destructive bulk operations.** Batch by lineage, use `git rm`,
  preserve history, run tests between batches.
- **If Phase C finds a live dependency on a "superseded" module**, treat that
  as a signal to revisit the Phase B canonical choice — don't just keep the
  dependency around as an exception. A canonical architecture that secretly
  depends on a "retired" one is not actually canonical yet.
- **Run the `thermo-nuclear-code-quality-review` skill on each Phase E/F
  batch before it lands.** Phase F in particular is exactly the kind of
  DRY-ification (collapsing ~76 analyzers and multiple runner copies into
  parameterized frameworks) where it's easy to trade one form of sprawl for
  another — bespoke wrappers, file-size explosions, ad-hoc dispatch
  conditionals. Invoke the skill on each consolidation/removal batch's diff
  to keep the result genuinely simpler, not just rearranged.

---

## 11. Resolved Questions

1. The consolidated reporting framework was built before the three-way
   comparison study. The comparison study can now use the Phase F runner and
   analyzer registries as its first real downstream consumer.
2. Test consolidation stayed conservative. Mirrored tests for deleted lineage
   code were removed with their owning files; surviving tests were retained or
   retargeted, and a new Phase F consolidation test pins the official analyzer
   registry instead of deleting narrow diagnostic coverage.
3. The fully-LLM surface was selected before removal: `llm_only_direct_labeler`
   remains the one-shot baseline and `hybrid_structured_events` is the
   canonical structured fully-LLM runner. Other `llm_only_*` experiments are
   documented through the lineage summary and recoverable from git history if
   a future study needs them.
