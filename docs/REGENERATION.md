# Regenerating Tracked Generated Artifacts

This note complements `.gitignore` hygiene: it lists generated files that remain
**intentionally tracked** for evidence or paper delivery, and how to refresh them.
It does not authorize deleting frozen evidence artifacts.

## Canonical indexes

| Artifact | Role | Regenerate |
| --- | --- | --- |
| `experiments/registry.jsonl` | Machine-readable run registry (claim-of-record) | Appended by `register_run(...)` in experiment drivers; edit only through registered runs |
| `experiments/RUN_INDEX.md` | Human scan of `registry.jsonl` | From repo root: `python -c "from pathlib import Path; from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import load_run_registry, write_run_registry_markdown; write_run_registry_markdown(load_run_registry(Path('experiments/registry.jsonl')), Path('experiments/RUN_INDEX.md'))"` |
| `docs/experiments/final_artifact_index_2026-06-22.md` | Frozen evidence spine with SHA-256 hashes | Manual update when canonical artifact paths or hashes change |

See also `experiments/README.md`, `docs/runbooks/mlflow_local_tracking.md`, and
`docs/experiments/final_artifact_index_2026-06-22.md`.

## Paper / LaTeX

| Artifact | Role | Regenerate |
| --- | --- | --- |
| `literature/IEEE/IEEE-conference-template-062824/IEEE-conference-template-062824.tex` | IEEE paper source | Edit directly |
| `literature/IEEE/IEEE-conference-template-062824/IEEE-conference-template-062824.pdf` | Checked-in compiled paper | `pdflatex` (or your editor build) in that directory |
| `literature/IEEE/IEEE-conference-template-062824/fig1.png` | Figure asset referenced by the draft | Export from TikZ/source as needed |

LaTeX auxiliaries (`*.aux`, `*.synctex.gz`, `literature/**/*.log`, etc.) are
gitignored. `IEEE-conference-template-062824.synctex.gz` is still tracked from
an earlier commit; prefer not to refresh it in git—rebuild locally only.

## Experiment evidence (large JSONL / JSON)

Registered full-run assemblies under `experiments/*.jsonl` (often 30–50 MB) are
**intentionally tracked** when indexed in `registry.jsonl` or
`final_artifact_index_2026-06-22.md`. They are not reproduced by a single
make target; rerun the named `experiments/build_*.py` driver or pipeline CLI
listed in the companion `.md` report and registry row.

`experiments/**/predictions*.csv`, `experiments/**/predictions*.json`, and
`experiments/**/traces/` stay untracked by default; add with `git add -f` only
when deliberately publishing a row-level artifact.

## Frontend derived mock data

`frontend/public/mock-data/` JSON files derived from indexed ExECTv2/Gan runs are
tracked for the observatory UI. Regenerate when the underlying registry row or
artifact index entry changes (see
`docs/plans/exectv2_frontend_dataset_integration_implementation_plan_2026-06-22.md`).

## Legacy tracked operational files (do not extend)

These paths predate current `.gitignore` rules and remain in git history only.
New runs should write under ignored `output/`, `logs/`, or `scratch/` instead.

- `battery_v07_progress.log`
- `experiments/*.stderr.log`, `experiments/*.stdout.log`, and a few `experiments/*.log` captures
- `output/*.log` and `output/playwright/*.png`
- `scratch/diagnostics.txt`, `scratch/out.txt`, `scratch/repair_candidate_set.py`, `scratch/test_clean.py`

## Local-only state (never commit)

- `mlruns/`, `mlflow.db*`, `logs/`
- `scratch/`, `output/` (new files)
- Python/JS caches: `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `frontend/node_modules/`, `frontend/.next/`
