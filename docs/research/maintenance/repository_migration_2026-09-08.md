# Repository Migration Record: Phase 0

Date: 2026-09-08
Status: Seven slices implemented to varying scope; review corrections and retained paths recorded below. Broad Phase 0 closure is not claimed.

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
  - `python scripts/check_doc_hygiene.py`: PASS.
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
- Repository documentation hygiene verified: `python scripts/check_doc_hygiene.py` passed cleanly (doc-hygiene gates: OK).
- Git diff formatting verified: `git diff --check` passed with 0 errors; no unintended trailing whitespace.
- Documentation link integrity verified across changed files.

### Slice 3 Verification Evidence
- Pre-move base commit byte hashes and Git blob IDs verified against Git base `ed4f956f`.
- Absence of code/test callers confirmed prior to move; verified no hash pins in `docs/experiments/retained_evidence_manifest.json` for the four moved plans or modified incoming-reference documents. Manifest bytes preserved intact.
- Archival notice banners and rebased relative links verified across all four moved files.
- Incoming Markdown links in `docs/THREAD_MAP.md` (tracked), `docs/history/decisions/0055-*.md`, and `docs/research/exectv2/` (11 files) verified.
- Sole active plan invariant confirmed: `docs/plans/ACTIVE_ROADMAP.md` is the only file remaining in `docs/plans/`.
- Repository documentation hygiene verified: `.venv/bin/python scripts/check_doc_hygiene.py` passed cleanly (doc-hygiene gates: OK).
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
