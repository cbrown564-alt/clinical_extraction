# Regenerating Tracked Generated Artifacts

This note complements `.gitignore` hygiene: it lists generated files that remain
**intentionally tracked** for evidence or paper delivery, and how to refresh them.
It does not authorize deleting frozen evidence artifacts.

## Canonical indexes

| Artifact | Role | Regenerate |
| --- | --- | --- |
| `experiments/registry.jsonl` | Machine-readable run registry (claim-of-record) | Appended by `register_run(...)` in experiment drivers; edit only through registered runs |
| `experiments/RUN_INDEX.md` | Human scan of `registry.jsonl` | From repo root: `python -c "from pathlib import Path; from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import load_run_registry, write_run_registry_markdown; write_run_registry_markdown(load_run_registry(Path('experiments/registry.jsonl')), Path('experiments/RUN_INDEX.md'))"` |
| `docs/experiments/retained_evidence_manifest.json` | Selected paper-facing evidence with SHA-256 hashes | Update deliberately, then run `python scripts/check_retained_evidence_manifest.py` |

See also `experiments/README.md`, `docs/runbooks/mlflow_local_tracking.md`,
`docs/runbooks/documentation_lifecycle.md`, and
`docs/experiments/retained_evidence_manifest.md`.

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
**intentionally tracked** only when required by the retained manifest or a
surviving registered replay closure. They are not reproduced by a single
make target; rerun the named `experiments/build_*.py` driver or pipeline CLI
listed in the companion `.md` report and registry row.

`experiments/**/predictions*.csv`, `experiments/**/predictions*.json`, and
`experiments/**/traces/` stay untracked by default; add with `git add -f` only
when deliberately publishing a row-level artifact.

## Retained reference replay

The six paper-facing architecture cells are verified from current deterministic
code or saved model outputs without new model calls:

```sh
python scripts/verify_reference_evidence.py
```

The manifest also names the entry point, implementation, scorer, data contract,
configuration, and tests needed to regenerate each cell.

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
- Python caches: `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`
