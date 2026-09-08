# Repository Migration Record: Phase 0 (Slices 1 & 2)

Date: 2026-09-08
Status: Slices 1 & 2 executed; Phase 0 underway.

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
  - `docs/paper/sections/methods.md` (lines 147, 210).
  - `docs/paper/sections/results.md` (line 650).
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
     - `docs/paper/README.md`, `docs/paper/sections/methods.md`, `docs/paper/sections/results.md`, and `README.md` (revert only the relocated publication paths).
  Never use `git checkout` of whole files as migration rollback, as doing so would risk clobbering concurrent or subsequent changes.

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
