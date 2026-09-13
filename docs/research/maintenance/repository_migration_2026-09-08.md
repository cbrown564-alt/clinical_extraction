# Repository Migration Record: Phase 0

Date: 2026-09-08
Status (2026-09-13): selected Phase 0 migration and reconstruction implemented;
section 9 owns final verification and deliberate retained-path exceptions.
Sections 1–8 preserve their dated progress and review corrections.

## 1. Scope
Tasks under the repository restructuring plan ([`ACTIVE_ROADMAP.md`](../../plans/ACTIVE_ROADMAP.md)):
- **Slice 1 (P0.1–P0.3)**:
  - P0.1: Reproducible baseline capture (Git state, classification inventory, dirty file preservation, active-writer audit, documented checks in `.venv`).
  - P0.2: Partial file-level disposition mapping covering the pinned move and group proposals, distinguishing exact reviewed moves from unresolved classifications.
  - P0.3: Relocation of `examples/vllm_gan_three_letters.jsonl` to `examples/gan2026/vllm_gan_three_letters.jsonl`.
- **Slice 2 (P0.4 Publication Materials)**:
  - Move 55 tracked files in `paper/` intact to `publications/dissertation/`, preserving bytes and Git visibility.
  - Retain substructure (`draft/`, `supporting materials/`, `template/`, `archive/`).
  - Add `publications/README.md` and `publications/dissertation/README.md`.
  - Update filesystem readers (`FIGURE_DIR` in `src/clinical_extraction/paper/gan_result_figures.py`, template path in `tests/test_gan_extract_label_forms_prompt.py`).
  - Update active Markdown links pointing into `paper/`.
  - Record `frontend/lib/demoResults.ts` provenance comment as historical provenance without introducing symlinks.
  - Verify TeX build behavior pre- and post-move under isolated output directories (`scratch/agy-phase0/publication-build/`).
- **Slice 3 (P0.4 Plan Archive)**:
  - Move four obsolete historical plans from `docs/plans/` to `docs/history/plans/` retaining filenames: `assembly_line_one_fact_2026-08-18.md`, `exect_llm_representation_and_hybrid_revaluation_2026-08-16.md`, `exect_prompt_fundamentals_2026-08-16.md`, `paper_final_repo_scope_2026-08-17.md`.
  - Confirm no code/test runtime consumers or retained-evidence hash pins depend on them.
  - Add standardized archival notice banners linking `docs/plans/ACTIVE_ROADMAP.md` and reaffirming safeguards.
  - Rebase internal relative links within moved files.
  - Update incoming references across documentation (`docs/THREAD_MAP.md`, `docs/history/decisions/0055-*.md`, research notes in `docs/research/exectv2/`).
  - Update `docs/README.md` and `docs/NAVIGATION.md` to reflect the move and planned status of remaining documentation.
  - Ensure `docs/plans/ACTIVE_ROADMAP.md` remains the sole active plan under `docs/plans/`.

## 2. Baseline Outcomes (P0.1)
- Git commit base: `a7b5451b` (Plan longitudinal epilepsy benchmark and repository migration).
- Preserved dirty state: 21 dirty/untracked user frontend files and deleted `FES.out` / `FES.pdf` were hashed and preserved without modification or reset.
- Active-writer audit:
  - PID 26725 (`python -m clinical_extraction.paper run --method gan_llm_extract_encode_select --model deepseek_v4_flash --split dev750 --live --work-leaf 20260905`) was identified as a live runner targeting `experiments/paper/gan_llm_extract_encode_select/deepseek_v4_flash/20260905/`.
  - Under a conservative rule, this run directory is kept in place while the process is live. (Note: A writer in that run directory does not imply all `paper_experiments/` paths are blocked; individual dependencies must be assessed before subsequent moves).
  - Limits of observability: Confirmed to local host processes via `ps` and `lsof`. File presence on disk alone does not prove external/hosted runs have completed.
- Baseline check results:
  - `python scripts/checks/check_doc_hygiene.py`: PASS.
  - `python -m mypy src`: PASS (399 files checked).
  - `python -m ruff check src tests`: Pre-existing failures (7 errors across 2 files).
  - `python -m pytest`: 771 passed, 9 failed out of 780 tests (pre-existing failures categorized into doc manifests, ExECT fact lineage lens, paper runner model roster metadata, reference evidence replay, and frontend API fixtures). Raw logs preserved locally at `scratch/agy-phase0/baseline/`.
  - Check side-effect note: The baseline pytest run temporarily updated `generated_on` in `paper_experiments/exect/rungs/gemini37flash/dev140/comparison.json`. That file was restored to its exact base commit bytes (`git checkout` on that single path). Future full-suite runs must monitor this path. Saved output final byte preservation was maintained.

## 3. Exact Tracked Moves

### Slice 1 (P0.3)
- Source: `examples/vllm_gan_three_letters.jsonl`
- Destination: `examples/gan2026/vllm_gan_three_letters.jsonl`
- Content SHA256: `a58a65142a23cf1b0b376a9d5067d0cda1b12238a24f2e3d524d6e154480cad8` (3 notes, 731 bytes, byte-for-byte preserved against `a7b5451b`).
- Updated callers: `VLLM.md` (intro link and operational walkthrough commands).
- Rollback procedure:
  To reverse this slice without overwriting any user or subsequent edits:
  1. Move the file back:
     ```sh
     mv examples/gan2026/vllm_gan_three_letters.jsonl examples/vllm_gan_three_letters.jsonl
     rmdir examples/gan2026
     ```
  2. Invert the 3 path substitutions in `VLLM.md` back to `examples/vllm_gan_three_letters.jsonl` (lines 13, 107, 229), preserving any subsequent edits made to that file.

### Slice 2 (P0.4 Publication Materials)
- Source: `paper/` (55 tracked files)
- Destination: `publications/dissertation/`
- Byte verification: Exact SHA256 matches for all 55 files against base commit `9f4d1ae6`.
- Detailed per-file map: Recorded in `scratch/agy-phase0/dissertation_file_map.json` and `scratch/agy-phase0/migration_mapping.md`.
- Updated filesystem readers:
  - `src/clinical_extraction/paper/gan_result_figures.py`: `FIGURE_DIR` set to `ROOT / "publications/dissertation/draft"`.
  - `tests/test_gan_extract_label_forms_prompt.py`: `SUPPORTING_EXTRACT_TEMPLATE` set to `publications/dissertation/supporting materials/gan_llm_extract_prompt_template.json`.
- Updated active Markdown documentation links:
  - `docs/paper/README.md` (lines 63, 88).
  - `publications/dissertation/notes/sections/methods.md` (lines 147, 210).
  - `publications/dissertation/notes/sections/results.md` (line 650).
  - Root `README.md` (layout overview and tracked descriptions).
- Historical provenance notes:
  - `frontend/lib/demoResults.ts` (lines 2-3) references old PDF paths in comments; preserved untouched as historical provenance.
- Rollback procedure:
  Review the slice commit and reverse only its moves and path edits, preserving any subsequent edits and unrelated work across the repository:
  1. Move `publications/dissertation/` back to `paper/`.
  2. Remove only the two introduced files (`publications/README.md` and `publications/dissertation/README.md`) after checking they have no subsequent edits, then remove the empty `publications/` directory.
  3. Revert only the specific path updates in callers and documentation:
     - `src/clinical_extraction/paper/gan_result_figures.py` (`FIGURE_DIR` back to `ROOT / "paper/draft"`)
     - `tests/test_gan_extract_label_forms_prompt.py` (`SUPPORTING_EXTRACT_TEMPLATE` back to `paper/supporting materials/...`)
     - `docs/paper/README.md`, `publications/dissertation/notes/sections/methods.md`, `publications/dissertation/notes/sections/results.md`, and `README.md` (revert only the relocated publication paths).
   Never use `git checkout` of whole files as migration rollback, as doing so would risk clobbering concurrent or subsequent changes.

### Slice 3 (P0.4 Plan Archive)
- Pre-move base commit: `ed4f956f` (Organize dissertation materials under publications).
- Moved historical plans:
  - `docs/plans/assembly_line_one_fact_2026-08-18.md` -> `docs/history/plans/assembly_line_one_fact_2026-08-18.md` (pre-move SHA256: `f1f0b98c51bbcb1d05662ab112fd7e1ac0ea7fdf6204afb300dd83e60c83ca20`, git blob: `dd0647342dbf6ead64f26562d0e4e2823cf4089c`)
  - `docs/plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md` -> `docs/history/plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md` (pre-move SHA256: `30b1fcbd47ab29c739fe324a39fa00f6fd20c9aea189befa007403da9af927b3`, git blob: `3c52bdee7de23ffba710c8cd06c7203d2c5f03f6`)
  - `docs/plans/exect_prompt_fundamentals_2026-08-16.md` -> `docs/history/plans/exect_prompt_fundamentals_2026-08-16.md` (pre-move SHA256: `200831a4067eefe55780048059c97abc22e6a8cda369edece857c1ec496e7a91`, git blob: `668e2a19973f8c65a988529294bc2eaa9d45a42f`)
  - `docs/plans/paper_final_repo_scope_2026-08-17.md` -> `docs/history/plans/paper_final_repo_scope_2026-08-17.md` (pre-move SHA256: `c6f7294d90ab56339809d87c92b24fbbccf3a9c75701ecf57daa40b64e2c83d9`, git blob: `4d4c643078b54644a986315b19293c421737369f`)
- Updated callers and readers:
  - `docs/THREAD_MAP.md` (tracked in Git; lines 88-89 updated).
  - `docs/history/decisions/0055-exect-semantic-inventory-and-method-contracts.md` (lines 10, 171).
  - 11 research notes in `docs/research/exectv2/` referencing `exect_llm_representation` and `exect_prompt_fundamentals`.
  - `docs/README.md` (updated description of `docs/paper/` to `(migration planned)` and `history/` to note archived plans).
  - `docs/NAVIGATION.md` (added row for historical plans).
- Rollback procedure:
  Review the slice commit and reverse only its moves and path edits, preserving subsequent edits and unrelated work:
  1. Move the four files back from `docs/history/plans/` to `docs/plans/`.
  2. Remove the top archival notice blocks from the four files and restore relative links to `../` (or inspect the slice commit diff to reverse only the text edits to those four files).
  3. Revert only the updated plan paths in `docs/THREAD_MAP.md`, `docs/history/decisions/0055-*.md`, and `docs/research/exectv2/*.md`.
  4. In `docs/README.md` and `docs/NAVIGATION.md`, revert the specific lines referencing `history/plans/`.
  5. Remove `docs/history/plans/` directory if empty.
  Never use `git checkout` of whole files as migration rollback.

## 4. Verification

### Slice 1 Verification Evidence
- SHA256 byte parity verified against base commit `a7b5451b` (`a58a6514...`).
- Note parsing and format validation verified via `clinical_extraction.operational.io.read_notes` (3 notes loaded, 0 errors).
- Operational CLI help verified via `python run.py --help`.
- Focused test suite verified: `pytest tests/test_operational_cli.py` (15/15 passed).

### Slice 2 Verification Evidence
- SHA256 byte parity verified for all 55 moved files (55/55 exact matches against base commit `9f4d1ae6`).
- Focused test suites verified in `.venv`:
  - `pytest tests/test_gan_extract_label_forms_prompt.py`: 6/6 passed.
  - `pytest tests/test_gan_result_figures.py`: 11/11 passed.
- LaTeX compilation verified:
  - `Extract, then decide.tex`: Two passes with pdflatex produce a 10-page PDF matching pre-move build text/fonts identically.
  - `Supporting materials.tex`: Rebuild fails with nonzero exit due to `inventory.png` missing from this checkout (known baseline failure), producing a 15-page document. Pre-move and post-move rebuild streams/text are identical, confirming no move regressions, but this defective rebuild does not match the preserved 16-page PDF.
  - Visual page sanity renders of selected pages (pages 1-2) verified via `pdftoppm`.
- Repository documentation hygiene verified: `python scripts/checks/check_doc_hygiene.py` passed cleanly (doc-hygiene gates: OK).
- Git diff formatting verified: `git diff --check` passed with 0 errors; no unintended trailing whitespace.
- Documentation link integrity verified across changed files.

### Slice 3 Verification Evidence
- Pre-move base commit byte hashes and Git blob IDs verified against Git base `ed4f956f`.
- Absence of code/test callers confirmed prior to move; verified no hash pins in `docs/experiments/retained_evidence_manifest.json` for the four moved plans or modified incoming-reference documents. Manifest bytes preserved intact.
- Archival notice banners and rebased relative links verified across all four moved files.
- Incoming Markdown links in `docs/THREAD_MAP.md` (tracked), `docs/history/decisions/0055-*.md`, and `docs/research/exectv2/` (11 files) verified.
- Sole active plan invariant confirmed: `docs/plans/ACTIVE_ROADMAP.md` is the only file remaining in `docs/plans/`.
- Repository documentation hygiene verified: `.venv/bin/python scripts/checks/check_doc_hygiene.py` passed cleanly (doc-hygiene gates: OK).
- Git diff formatting verified: `git diff --check` passed cleanly across all repository files with 0 errors; trailing two-space breaks on changed lines replaced with explicit backslash breaks or removed.
- Link target existence verified: Across all modified docs and four moved plans (311 relative links), no newly broken links were introduced. Exactly one pre-existing missing target remains in tracked `docs/THREAD_MAP.md` -> `research/artifacts/rescue_source_provenance_2026-08-13.html` (unchanged by this slice; historical artifact not regenerated).
- Runtime verification: No runtime code or tests executed, as this is a documentation-only archival slice with no code/pipeline changes.


## 5. Slices 4–7 and review corrections (2026-09-09)

Git commits identify the exact tracked move/change mappings:

- `27678056`: canon and numbered decisions archived under `docs/history/`.
- `16337a89`: research notes and manuscript sections rehomed; benchmark entries added.
- `aba0a42f`: results moved to `results/letter-benchmarks/`; compatibility symlink added.
- `fc348197`: destination README scaffolding and `/runs/` ignore rule added.

These commits do not prove that source corpora, local runs or helpers were moved.
The roadmap's retained-path section owns those exceptions and the symlink removal
condition. The earlier claim of complete restructuring across all targets was
withdrawn after review. Full classification and local per-file mapping remain
unfinished; existing publication mapping and baseline records remain applicable.

Review corrections in the working tree:

- Restore the ExECT Gemini development rung comparison to its original bytes;
  the migration had changed only `generated_on` from August 29 to September 9.
- Use the canonical results path in current Python callers, scripts, frontend API
  routes and path fixtures. Preserve schema identifiers and saved artifact paths.
  The root resolver no longer falls back to a different writable directory.
- Rebase the results README's documentation links for its new depth.
- Narrow the roadmap and local status claims to implemented work and explicit
  retained-path exceptions. No private data/run move or benchmark regeneration
  is part of these corrections.

Verification results for these corrections are recorded below after checks finish.

### Correction verification

On 2026-09-09 in the working tree (including pre-existing unrelated user edits):

- Full always-on `python -m pytest -q`: 781 passed; one upstream deprecation warning.
- `python -m ruff check src tests`, `python -m mypy src`, documentation hygiene,
  and `git diff --check`: passed.
- Frontend `npm test -- --runInBand`: 24 suites / 163 tests passed;
  `npx tsc --noEmit`: passed.
- The replay path assertion first failed against the old path, then passed after
  migration. Existing fixture-based promotion tests exercise the canonical tree
  without a compatibility symlink.
- The full suite exposed the known development replay timestamp side effect.
  Redirected that test's output to `tmp_path` and restored original saved bytes;
  the focused ExECT replay file was rerun after this isolation change.
- Direct requests to the existing local frontend returned HTTP 200 and valid JSON
  for Gan/ExECT panels, the five-cell grid and pipeline families. The grid reports
  its canonical results source. No browser visual review was needed for path-only
  API edits; user-authored UI changes were outside this task.
- Machine artifact Git blob hashes match the pre-migration `a7b5451b` tree.
  The results README is deliberately excluded because its links were repaired.
- A generated teaching document modified by checks was restored to its pre-check
  bytes; unrelated clinical changes are not incorporated into this migration.

These checks do not establish clinical validation or complete historical document
classification. PDF builds were not repeated because publication assets did not
change. No model calls, source-data moves or locked-row error inspection occurred.

## 6. Staged reconstruction compatibility slice (2026-09-13)

The reconstruction began at Git base `b005d6d0` in an already dirty working tree.
Existing documentation, longitudinal, frontend and result work was preserved. A
local process audit immediately before final verification found no matching model,
generation or pytest writer. The earlier per-file migration and local-only path
inventory above remains authoritative; no data, experiment, scratch, literature,
media, credential or saved-result path moved in this slice.

Implemented boundaries:

- added task-neutral immutable source/request/artifact/lifecycle records under
  `src/clinical_extraction/core/artifacts.py`;
- moved shared DSPy provider construction to `core/dspy_runtime.py`, retained the
  Gan import as a compatibility wrapper, and changed ExECT callers to the shared
  path;
- added explicit Gan and ExECT artifact paths beside their historical runners,
  preserving task-owned parsers, projections, scorers and defaults;
- added a longitudinal adapter over existing assertions/links, with source/date
  identity checks, cutoff handling and immutable decision records;
- added focused acceptance coverage in `tests/test_extraction_artifacts.py`.

No historical runner delegates to the new path yet, so rollback is additive:
remove the new artifact entry points and their tests, point the four provider
imports back through the retained Gan wrapper, then remove the two new `core`
modules only after checking that no subsequent caller uses them. Source and saved
response bytes require no rollback. Do not revert whole files that contain other
user work.

Verification in the repository `.venv`: 13 artifact acceptance tests and the
119-test Gan/ExECT/operational compatibility selection passed. Full always-on
pytest passed 823 tests with the two already known unrelated documentation/
inventory expectation failures. Ruff passed across `src tests`; mypy passed across
411 source files; documentation hygiene and `git diff --check` passed. Independent
Astra review reproduced seven initial provenance/failure defects and one projection-
origin ambiguity; the corrected no-call probes passed and the final review found
no blocker for the bounded slice.

No model call, locked-row inspection, benchmark/result regeneration, frontend
change or clinical-schema change occurred. Package/public-checkout verification
was not run because the configured build backend is absent from the repository
environment. The different-domain R5 task is unselected. Persisted registry/resume
integration and full R6 consolidation remain separately scoped.

## 7. Legacy support investigation (2026-09-13)

Status: Conor approved L1–L7, L9 and L10; L8 is retained. Approval includes moving
required portions of `paper/` and `trace_explorer/` to their functional owners
before deleting obsolete code and old namespaces. The architecture owner records
the destination map. No code, command, artifact, data or compatibility path has
been removed by this investigation or decision update. Conor selected research-paper
tables for R5, deferring its full implementation, and put reconstruction and
migration before further programme research. The roadmap owns that decision;
the architecture document owns its foundation requirements.

### Scope and evidence limits

Inspected the current working tree: package entry points, operational and paper
CLIs, task runners and facades, shared registry/resume helpers, scripts, CI,
frontend routing, relevant tests and active documentation. Used source searches
and Python AST inspection of `src/`, `tests/` and `scripts/` for callers. This
identifies in-repository consumers, not usage on other machines or dynamically
constructed calls. Historical/private run contents and locked rows were not read.
No model, queue, scoring run or broad artifact regeneration was executed.

The important distinction is between maintaining an old way to launch a new run
and retaining the ability to read, explain and replay an existing result. Many
command aliases and wrappers can go while the latter remains supported. A name
containing `legacy` is not sufficient evidence that its implementation is unused.

### Approved dispositions and original investigation

Paths below are repository-relative. Removal means a future coordinated change,
including the listed consumers and checks. The recommendations below retain the
investigation's reasoning; the status above and decision below record Conor's
subsequent approval, with L8 explicitly kept.

| ID | Candidate and evidence | Recommendation and consequence |
| --- | --- | --- |
| L1 | Three `_legacy_run_split` bodies in `gan2026/llm/llm.py`, `gan2026/llm/hybrid_structured_events.py` and ExECT `llm/pipelines/key_entities_structured/runner.py`. Their public `run_split` functions already delegate to canonical orchestration. References to the old bodies are in `scripts/check_canonical_orchestrator_parity.py` and `scripts/check_canonical_orchestrator_development_parity.py`; the latter also passes functions as callbacks. | Remove the duplicate execution bodies after replacing old-versus-new checks with pinned no-call request/output expectations. Keep parsers, prompt builders and reporting helpers still called by current orchestration. This removes duplicate code, not deterministic/hybrid methods. |
| L2 | Gan `llm_config.py` delegates provider construction to `core/dspy_runtime.py`; `contract/label_parser.py` re-exports shared epilepsy normalisation. ExECT `llm/llm_only_key_entities_structured.py` re-exports its package, including private helpers. `paper/lm.py`, Gan runners, paper modules, scripts and tests still use these facades. | Remove old import paths after redirecting callers to actual owners. Move monkeypatch tests to the new provider owner. The ExECT package documents an import-order cycle, so verify fresh-process imports while narrowing exports. No outside Python-import compatibility guarantee. |
| L3 | `gan2026/runner.py` combines re-exports with `Gan2026PipelineRunner`; `pipeline_v1.py::Gan2026PipelineV1` constructs it. Tests call both; current deterministic stages import helper types/functions from `pipeline_v1.py`. | Retire redundant runner classes/facades after moving callers to the chosen execution API. Do not delete `pipeline_v1.py` wholesale: its candidate types and helpers still have production callers. Removes an old object-oriented entry point without removing the deterministic baseline. |
| L4 | `pyproject.toml` exposes `gan2026-llm-experiment`; Gan has a separate split/checkpoint CLI and ExECT has `cli/rules.py` and shared CLI helpers. `clinical-extract` handles ordinary input notes; `paper/cli.py` separately handles run, verify, replay, reparse and result promotion. The older Gan command appears in the Windows vLLM runbook. | Consolidate user entry points around one command with distinct extraction, evaluation and saved-result operations. Retire task-specific launchers after preserving necessary split guards, runtime controls, checkpoint/resume and reports. The operational CLI alone does not yet replace benchmark evaluation. Old command lines would need updating. |
| L5 | Gan `runners/naming.py`, ExECT `runners/naming.py` and `paper/methods.py` accept multiple method names. Examples: `hybrid_structured_events`, `llm_pre_post`, `exect_llm_inventory`, `exect_llm_extract_filtered`. Some names also identify persisted results. | Accept one canonical name per method for new execution. Keep historical names only in saved-result readers and explicit import adapters; preserve stored IDs. Separate the launch-name change from prompt/scorer meaning. Update configs, tests and current documentation together. |
| L6 | `scripts/run_deepseek_cell3_overnight.sh`, `scripts/run_gan_deepseek_living_low.sh` and `scripts/run_paper_local_queue.ps1` encode dated model queues rather than current programme tasks. The overnight and PowerShell queues include holdout jobs. The roadmap separately records a GEPA launcher whose imported implementation was removed. | Retire these from supported runnable tooling; retain source in history or the appropriate historical study archive where it explains a run. Do not restore GEPA execution just to make an old launcher run. Preserve associated outputs, instructions and provenance. Archive other study scripts only after file-level consumer classification; do not bulk-delete `scripts/`. |
| L7 | Tracked `paper_experiments` symlink points to `results/letter-benchmarks`. `core/paths.py` writes only to the canonical location; historical saved paths still depend on the old name. | Remove after implementing a read-time old-to-new path resolver and verifying replay/API behavior in a checkout without the symlink. Keep saved record bytes unchanged. External filesystem consumers of the old path would need updating. |
| L8 | `run.py` bootstraps `src` and rewrites flat Gan flags via `operational/script_argv.py`; `requirements.txt` duplicates runtime dependencies. README and `VLLM.md` explicitly offer this no-install HPC/vLLM workflow. | Retire if installation with `pip install -e .` or a wheel is acceptable on target machines. Otherwise retain this small launcher deliberately. This is a real workflow choice, not dead code: removal ends the documented no-install route and requires rewriting the walkthrough. |
| L9 | `paper/methods.py` exposes old ablations and multi-call methods as live options; `paper/cli.py` mixes live execution with replay, scoring and result writers. Paper modules also supply prompt/parser, saved-row hydration and UI data functions. | Retire the old live experiment dispatcher and closed-study launch presets after required current methods move to versioned task profiles. Retain saved-result verification/replay/scorers and methods used by the demo. Do not delete the `paper` package as a unit. Conor should explicitly decide whether fresh execution of historical methods remains supported. |
| L10 | `core/registry.py` contains old phase-specific decisions and architecture categories; `core/run_resume.py` keys completion by row ID and `merge_rows` uses last-write-wins. ExECT orchestration still calls those resume helpers; registry consumers include retained-evidence and report code. | Replace the new-run dependence on historical registry vocabulary and row-key-only resume with the artifact lifecycle and exact request identity. Retain a reader for old registry records; remove old helpers only after all execution callers move. Failure accounting and retries must remain explicit. This is replacement work, not immediate deletion. |

### Support to retain unless the intended experience changes

- Task-owned Gan/ExECT scorers, saved prompt versions, projections and necessary
  clinical rules. New extraction adapters still call existing parsers and prompt
  builders. Removing rule-heavy methods from the main paper comparison does not
  make their replay or teaching implementation unused.
- `paper/comparison_contract.py::adapt_legacy_comparison` and
  `paper/cells.py::cell_id_from_legacy_rung`: current panels, five-cell views and
  answer-state reconstruction consume them. Keep these read adapters unless an
  equally faithful replacement can read the retained bytes.
- `trace_explorer`: `frontend/next.config.ts` routes local API requests to the
  Python service; `api/app.py` registers catalog, trace and frontend routes, and
  stores reviews. `frontend_data.py` imports saved-row hydration from `paper/`;
  ExECT paper replay imports `_frontend_letter` in the other direction. This is
  coupling to remove, not evidence that the API is obsolete. Extract shared data
  conversion before retiring any route. Preserve `/demo`, `/workbench` and
  `/longitudinal` unless Conor separately chooses to remove an experience.
- Raw outputs, issued publication assets, source IDs, splits, protected local
  material and review records. Removing executable support does not authorise
  deleting these records or relabelling their clinical meaning.

### Additional findings and verification

- Both canonical-orchestrator parity scripts import
  `gan2026.llm.llm_only_canonical_pipeline`, which is absent in this checkout.
  A fresh `.venv` import probe reproduced `ModuleNotFoundError`; the current
  `gan2026.llm.llm` import succeeds. Replace the stale parity mechanism under L1
  rather than requiring a resurrected module alias. These scripts were not run
  against corpora.
- The ExECT facade exists at `exectv2/llm/llm_only_key_entities_structured.py`,
  not under its `pipelines/` directory. A guessed nested-path probe failed;
  subsequent source inspection and pytest collection confirmed the actual path.
  No ExECT missing-module defect is inferred from that probe.
- `observatory/` has no tracked source files or current source implementation;
  only local bytecode residue was found. It should cease appearing as an active
  package in current documentation. This is not another server to migrate or a
  meaningful code-removal saving; no cache was deleted.
- Gan `experiments/artifact_io.py::load_raw_outputs_by_source_index` is a forwarding
  function with no external import/call found in the inspected Python trees.
  Current callers use `pipeline/replay_io.py`. It is a small L2 removal candidate;
  the containing JSONL IO module still has many Gan and ExECT consumers.
- `.venv/bin/python -m pytest --collect-only -q tests/test_paper_runner.py
  tests/test_exectv2_llm_only_parsing.py` collected 21 tests successfully. This
  verifies collection of relevant current imports, not execution or replay parity.
  No full backend/frontend suite was rerun for this investigation.
- Documentation hygiene and `git diff --check` passed. Local Markdown link targets
  in the roadmap, architecture, migration record, navigation and local status all
  exist. These checks do not establish that proposed removals are safe to execute.

Final decision (2026-09-13): Conor approved L1–L7, L9 and L10 as coordinated removals
or replacements, retaining saved-result replay and demonstration behavior.
L8 stays: `run.py`, `requirements.txt` and the no-install HPC/vLLM workflow remain
supported. Move required code to its functional owner, then delete the rest;
neither the `paper` nor `trace_explorer` namespace needs permanent import support.
The [architecture destination map](../../design/architecture.md#reconstruction-destinations-after-the-legacy-support-decision)
defines the boundaries. Implementation must capture current dirty files, map
actual callers and verify each replacement before deleting its predecessor.
No source moves or removals have been performed in this decision update.


## 8. Documentation reduction (2026-09-13)

Conor approved a smaller checkout documentation set, including deletion rather
than automatic archiving of superseded tracked narrative. The active roadmap
owns completion scope; the documentation lifecycle owns retention rules.

First cut: remove the old Assembly Line UI build plan and August paper-final
repository scope. Both are superseded planning prose, unchanged from the recovery
commit below. Current programme scope belongs to the active roadmap; current UI
behaviour belongs to source and tests. Repository reference searches found only
historical move records and roadmap history, with no code, test, manifest or
current Markdown-link consumers. Those historical move records remain accurate
as dated records; their paths are no longer current files.

| Removed file under `docs/history/plans/` | Lines removed | SHA256 |
| --- | ---: | --- |
| `assembly_line_one_fact_2026-08-18.md` | 163 | `3ff2133bd2fbddccca3550943704541c56d3c1240da4e6ec69dea05abb943077` |
| `paper_final_repo_scope_2026-08-17.md` | 260 | `667823757dac0315870562758fd0486850461c6cc54cac13bab744a4804aba6c` |

Recovery: `git show b005d6d020e525d657d5d9f018c0f019bff777a5:<original-path>`.
This cut removes 2 Markdown files and 423 lines of obsolete
plans, without adding replacement archive files. The two ExECT plans remain
pending classification because they contain study-specific rationale and links
to retained research. No study protocols, results, generated reference files or
local-only material were removed. This is the first applied cut, not completion
of the broader study-document review.

Verification: documentation hygiene and `git diff --check` passed. Both removed
files matched the recovery commit byte-for-byte before deletion. Runtime tests
were not run because this cut changes only guidance and unused historical prose.

## 9. Applied reconstruction and migration (2026-09-13)

Conor authorised completion after approving L1–L7/L9/L10 and keeping L8.
The selected code and repository migration is implemented. The
[file disposition manifest](repository_migration_2026-09-13.json) records 212
original-to-final file moves, 18 removed files, baseline hashes, final hashes and
343 retained study documents with their named purposes. It is a migration mapping,
not a new research evidence register. Earlier sections describe their dated states.

### Implemented boundaries and behavior

- Shared source/request identity, immutable artifacts, provider mechanics and
  JSONL IO live in `core`. SQLite stores captures and execution manifests with
  complete request/runtime/program identity. Offline replay refuses changed
  inputs, preserves failures and never constructs a provider. Retry is explicit;
  prior failed execution records remain available. Longitudinal reloading restores
  typed content so the same saved assertions support both historical policies.
- Gan and ExECT saved-response hydration, projections, scorers and comparisons
  have task-owned evaluation modules. Shared metrics live in `evaluation`;
  historical five-cell, registry, roster and split-policy vocabulary is explicitly
  scoped to `evaluation/letter_benchmarks`, outside `core`.
- `inspection` owns HTTP routes, frontend adapters and review storage. Evaluation
  no longer imports inspection. Existing API URLs and `.trace_explorer` local
  review/index storage remain stable; the old Python namespaces are retired.
- The supported command is `clinical-extract`: extraction, exact replay,
  operational methods, benchmark runners, saved-result evaluation, inspection
  and indexing. Canonical method names are accepted for new runs; saved-record
  readers retain historical identifiers. Gan benchmark defaults write under
  `runs/benchmarks/gan`; ExECT accepts explicit output paths and retains its
  development-only guard, runtime controls and strict checkpoint resume.
- Removed duplicate legacy split bodies, provider/normalisation/import facades,
  redundant Gan runner classes, dated queues, the old live paper dispatcher and
  the `paper_experiments` symlink. Historical paths are resolved at read time;
  saved record bytes and method IDs are not rewritten. ExECT's retained checkpoint
  reader rejects duplicate IDs and requires matching source hashes and runtime/
  prompt provenance. New artifact execution does not depend on row-key resume.
- `run.py`, `requirements.txt` and the no-install HPC/vLLM workflow remain (L8).
  Research-paper tables remain R5; generic source identity, task-owned content and
  multiple evidence references are foundations, while table locators, parsing/OCR
  and the complete table workflow are deferred.

### Repository and documentation disposition

Helpers now live under `scripts/checks`, `scripts/benchmarks`,
`scripts/publications` and the existing `scripts/longitudinal`. CI, pre-commit,
imports and current command documentation use those paths. Dissertation methods
and claims moved beside the manuscript into `publications/dissertation/notes`;
shared holdout and pytest safeguards have benchmark/runbook owners.

The 73 former experiment Markdown records (10,459 lines before and after) are
original protocols, scoring rationale or result interpretation. They were classified for continuing study
use and moved under `docs/research/{gan2026,exectv2,shared}`, rather than retaining
another blanket archive. Together with existing study records, the final
classification keeps 343 documents (147 Gan, 139 ExECT, 57 shared); the manifest
records each title and role. No exact duplicate bodies were found. Keeping these
records does not reactivate their queues. Two old ExECT plans remain historical
references for prompt/representation rationale and their linked study sequence.

Two stale generated ExECT method/diagram pages were removed (349 + 77 lines;
2 files / 426 lines before, 0 after). The current generator and manifest own
their replacements. The earlier two-plan deletion in section 8
remains applied. Incoming links and publication-note links now resolve to current
owners. Remaining unavailable references in historical study prose refer to
pre-existing missing local artifacts or retired records; no replacement evidence
has been invented. Issued PDFs and their TeX/assets were not changed or rebuilt.

Private `data` source/split paths, historical `experiments` runs, protected scratch,
local reading/media copies and `.trace_explorer` review state remain at their
existing paths and keep their ignore boundaries. Their embedded provenance or
sole-copy status makes a cosmetic relocation counterproductive. The roadmap
records these bounded retained-path exceptions. New artifact captures use
`runs/extraction`; no raw corpus, credentials or protected run was exported.

### Recovery and verification

Before editing, the dirty working tree was inventoried and preserved locally in
`scratch/reconstruction-2026-09-13/before`, with SHA256 values in
`baseline_hashes.json`, the starting revision in `git-head.txt`, and move maps and
check logs beside them. Recovery of a pre-existing dirty file must use that
snapshot, not overwrite it with HEAD. The public disposition manifest records
hashes and paths without embedding private source contents. No reset, clean or
rewrite of unrelated work was used. The active-writer check found no matching
model/generation job; two old TeX processes were left alone and manuscript assets
were not moved by this slice.

Verification uses the repository `.venv`, no paid model calls and no locked-row
failure inspection. The two baseline failures (stale generated teaching prose and
an inventory expectation omitting six already-present cells) were repaired
without editing benchmark results. Acceptance includes the always-on Python
suite, Ruff, mypy, fresh-process imports, installed wheel in a clean public tree,
frontend tests/build, browser interaction and documentation hygiene. Final outcomes are recorded below.


| Check | Final outcome |
| --- | --- |
| `.venv/bin/python -m pytest -q` | 824 passed; always-on tier; both baseline failures resolved |
| `.venv/bin/ruff check src tests` | Passed |
| `.venv/bin/mypy src` | Passed across 410 source files |
| Fresh-process imports and dependency audit | Seven independent imports passed; no old namespace imports, no task/evaluation dependency in `core`, no inspection dependency in evaluation |
| Wheel build and installation | Built with Hatch; installed into an isolated target and imported from that target |
| Clean public-checkout test | 736 passed, 88 corpus-dependent skips; private data/run trees absent; wheel import location asserted |
| No-install HPC launcher | Five dedicated tests passed; `run.py --help` passed; obsolete console scripts absent after editable reinstall |
| Supported command help | Evaluation and both benchmark dispatchers passed |
| Frontend | 26 suites / 167 tests passed; Next production build passed |
| Browser QA | Demo extraction → decision, loaded validation workbench trace, longitudinal visit → retrospective policy change all exercised |
| Documentation | Hygiene and whitespace checks passed; generated reference matched the passing suite; active owner/publication-note links repaired |
| Preservation | 1,371 baseline evidence/example/asset/publication files checked. No machine evidence or issued asset changed; only four publication-note link repairs and the main result README changed |

Frozen result documentation snapshots were restored to their exact baseline
bytes after the link audit; their historical relative links are not rewritten.
All 135 examples and 123 frontend assets are byte-identical. Of 1,050 result
files, only the navigation README changed. Issued PDFs, TeX and publication
assets remain identical. No model call, locked-row failure review, new scientific
result, deployment or full research-table implementation occurred. The optional
deep tier was not run; the documented always-on firewall and the relevant full
engineering checks passed. Temporary browser/API verification servers were stopped.
