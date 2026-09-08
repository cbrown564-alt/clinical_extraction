# Repository Migration Record: Phase 0 (Slice 1: P0.1–P0.3)

Date: 2026-09-08  
Status: Slice 1 executed; Phase 0 underway.

## 1. Scope
Tasks P0.1–P0.3 under the repository restructuring plan ([`ACTIVE_ROADMAP.md`](../../plans/ACTIVE_ROADMAP.md)):
- P0.1: Reproducible baseline capture (Git state, classification inventory, dirty file preservation, active-writer audit, documented checks in `.venv`).
- P0.2: Partial file-level disposition mapping covering the pinned move and group proposals, distinguishing exact reviewed moves from unresolved classifications.
- P0.3: Relocation of `examples/vllm_gan_three_letters.jsonl` to `examples/gan2026/vllm_gan_three_letters.jsonl`.

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

## 3. Exact Tracked Move (P0.3)
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
  2. Invert the 3 path substitutions in `VLLM.md` back to `examples/vllm_gan_three_letters.jsonl`:
     - Line 13: `examples/gan2026/vllm_gan_three_letters.jsonl` -> `examples/vllm_gan_three_letters.jsonl` (with link markdown restored)
     - Line 107: `--input examples/gan2026/vllm_gan_three_letters.jsonl` -> `--input examples/vllm_gan_three_letters.jsonl`
     - Line 229: `--input examples/gan2026/vllm_gan_three_letters.jsonl` -> `--input examples/vllm_gan_three_letters.jsonl`

## 4. Verification
- SHA256 byte parity verified against base commit `a7b5451b`.
- Note parsing and format validation verified via `clinical_extraction.operational.io.read_notes` (3 notes loaded, 0 errors).
- Operational CLI help verified via `python run.py --help`.
- Focused test suite verified: `pytest tests/test_operational_cli.py` (15/15 passed).
- Repository documentation hygiene verified: `python scripts/check_doc_hygiene.py` passed cleanly.
- Link integrity and whitespace checks verified.
