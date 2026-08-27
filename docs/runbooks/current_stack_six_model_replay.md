# Current-stack six-model hybrid replay

Repeatable no-call readout of the selected six-model `llm_with_rules` cells
through HEAD repairs. This is the procedure to run again after a repair lands.

Owners: [Decision 0050](../decisions/0050-current-stack-hybrid-primary-fills.md)
(policy), `paper_experiments/current_stack/` (inventory and living numbers).

Do not make new model calls. Do not inspect locked holdout rows. Do not
overwrite retained-evidence live-run packages.

## Layout

```
paper_experiments/current_stack/
  SOURCES.json                 selected sidecars and DeepSeek 0731 identity
  sidecars/                    stripped holdout replay inputs (not scratch)
    gan_test450/*.jsonl
    exect_test60/*.jsonl
  latest/                      living machine owner — point charts here
    replay_summary.json
    panel_aggregate.json
    fills.json                 the small primary-number table
    promote_checklist.md
  runs/YYYYMMDD/               dated snapshot of that latest/ tree
scratch/validation/current_stack/
  latest/                      gitignored row-level replay scratch
```

`SOURCES.json` is the only place that names which jsonl is selected for each
model. Holdout replay inputs live under `sidecars/`, stripped of note text,
gold, and prompt payloads. `scratch/holdout/` remains the operational dump;
do not depend on it for remasure. DeepSeek holdout is the **0731** sidecars.
Pre-0731 trees stay in the inventory as `selected: false`.

## One command

From the repo root, with `.venv` active:

```powershell
.venv\Scripts\python.exe scripts/run_current_stack.py all
```

That is five stages. You can run them separately:

| Stage | What it does | Model calls |
| --- | --- | --- |
| `check` | Confirm every selected source file exists | none |
| `measure` | Replay saved raws / structured sidecars through HEAD | none (reuse only) |
| `assemble` | Write `fills.json` and the living panel | none |
| `exhibits` | Rebuild comparison-report SVG/PNG from the living panel | none |
| `snapshot` | Copy `latest/` to `runs/YYYYMMDD/` | none |
| `promote-checklist` | Print the claim-owner list and the new Sol / six-model numbers | none |

`measure` is the long step (Gan `test450` is 2,700+ rows). Resume is safe:
existing scratch rows are reused unless you pass `--overwrite`.

Skip an expensive remasure when you only need to rebuild the panel or charts:

```powershell
.venv\Scripts\python.exe scripts/run_current_stack.py assemble
.venv\Scripts\python.exe scripts/run_current_stack.py exhibits
```

Optional Gan `dev750` v0.7 development readout is **not** in `all`. It is
still `python scripts/replay_gan2026_six_model_current_stack_dev750.py`. Row
artifacts live in
`experiments/gan2026_six_model_current_stack_dev750_replay_20260813/` and
are the workbench default for hybrid `dev750`. That readout is not the
selected v0.5 development panel.

## After the machine run: promote

`assemble` writes numbers. It does **not** edit canon, README, or the paper
stories. That remains an explicit claim step.

1. Read `paper_experiments/current_stack/latest/fills.json`.
2. Read `paper_experiments/current_stack/latest/promote_checklist.md`.
3. Update those living owners, or decide the new readout stays a measurement
   and does not replace the previous primary fills.
4. Update `PROJECT_STATUS.md` after the evidence owner (`fills.json`).
5. Do not change rules-only or LLM-only fills. They are not in this replay.
6. Do not rewrite retained-evidence `result_summary` for the original live runs.

Sol remains the Decision 0046 method-identity row even if another model scores
higher on the six-model table.

## Claim boundary

No-call current-repair evidence. Holdout cells are aggregate-only. Development
`dev140` may keep letter-level sidecars under `latest/` only if they stay off
the locked-aggregate safety list (they belong in scratch, not in
`replay_summary.json`). Scores are not interchangeable across tasks.
