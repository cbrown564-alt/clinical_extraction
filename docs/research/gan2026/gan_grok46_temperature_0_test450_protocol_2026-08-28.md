# Protocol: Grok 4.6 `gan_llm_extract` on `test450` at temperature 0

Date: 2026-08-28
Status: complete; report
[gan_grok46_temperature_0_2026-08-28.md](gan_grok46_temperature_0_2026-08-28.md)
Owner: this file
Roster: [`paper_experiments/roster.json`](../../../paper_experiments/roster.json)
Related: [six-model roster](../../paper/decisions/six-model-roster.md),
[experiment environment](../../paper/experiment_environment.md),
[cell-3 roster fill](gan_cell3_roster_fill_protocol_2026-08-22.md)

## Question

Does Grok 4.6 complete living cell-3 Gan extract (`gan_llm_extract`)
on locked `test450` when temperature is `0` instead of the living
paper setting `1.0`?

A 2026-08-28 AI Gateway probe accepted `temperature=0`. This study
asks whether a full holdout extract also completes and what the
aggregate Purist stop is. It does not ask whether to change the
living Grok setting.

## Why it matters

Luna is pinned at `1.0` because the provider rejected `0`. Grok was
grouped with Luna in `ModelSpec` without a reject-at-0 record. A
holdout extract at `0` is the only matched evidence that the route
accepts that setting on the paper cell, not only on a one-token
probe.

## Data and row policy

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `test450` (`gan2026_split_v1` test) |
| Rows | 450 |
| Method | `gan_llm_extract` (cell 3 find) |
| Model | `grok46` / `xai/grok-4.6` |
| Candidate | temperature `0.0`; other living Grok fields unchanged |
| Comparator | living Grok temperature `1.0` (not overwritten) |
| Scorer | Purist accuracy; Pragmatic is secondary |
| Row policy | aggregate-only |
| Inspection | Do not inspect holdout identifiers, notes, predictions, evidence, or errors |

The runner may read locked notes only to make the frozen calls.

## Frozen condition

| Field | Value |
| --- | --- |
| Temperature | `0.0` (non-living; `--temperature 0`) |
| Reasoning | `low` |
| Max tokens | 5,000 |
| Cache | off |
| Transport | Vercel AI Gateway, sync |
| Work cell | `scratch/holdout/paper/gan_llm_extract/grok46/temperature_0/test450/` |

Do not write this run into the living Grok work cell or promote it
to `paper_experiments/`. Do not start later-stage LLM encode or
select. Do not retune from holdout rows.

## Stop rule

- **Answer:** extract completes with 450 scored rows and an
  aggregate Purist/Pragmatic summary.
- **Negative:** route rejects `0` or the run fails before a complete
  aggregate.
- **Not a promotion:** even a higher score stays a temperature
  ablation.

## Claim boundary

Diagnostic holdout ablation. Not a living roster change. Not a
matched latency or cost study. Not row-level mechanism evidence.
