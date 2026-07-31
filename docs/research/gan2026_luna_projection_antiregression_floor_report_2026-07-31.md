# Luna projection + anti-regression floor on `validation750`

Date: 2026-07-31  
Status: development answer; absorbed into final Gan LLM-with-rules ruleset  
Protocol: [floor protocol](../experiments/gan2026/gan2026_luna_projection_antiregression_floor_protocol_2026-07-31.md)

## Answer

A narrow deterministic floor recovers the shared projection and repair-regression
failures that prompt variants A/B/C could not fix. No-call replay of saved Luna
raw outputs through `hybrid_full_stack` with the floor yields net Purist gains
on all three variants, rescues the named exemplars 1030, 2459, 2932, 5837,
10097, and 10237 on every variant, and cuts the 48-row persistent residual by
7–8 rows. Dated-count demotions to `no_reference` (14587, 14628) remain open.

## What changed

| Module | Change | Portability |
| --- | --- | --- |
| Benchmark repair | `N or M per …` → `N to M per …` | `benchmark_format` |
| Benchmark repair | `N clusters over/in M weeks` → dual cluster label | `benchmark_format` |
| Benchmark repair | cadence-only `N cluster per period` → `, multiple per cluster` instead of `unknown` | `benchmark_format` |
| Evidence derivation | keep `or`-ranges from collapsing to one endpoint | `seizure_frequency` |
| Hybrid repair stack | block monthly-diary overwrite of selected seizure-free or day/week rates | `seizure_frequency` |

Prompt text, schema, scorers, and the frozen six-model panel were not changed.

## Results (no-call Luna A/B/C replay)

| Variant | Before | After | Δ | W→C | C→W | Persistent-48 rescued |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A `v0.5` | 646/750 | 657/750 | +11 | 15 | 4 | 7 |
| B `luna_rate` | 656/750 | 664/750 | +8 | 10 | 2 | 7 |
| C `luna_current` | 666/750 | 673/750 | +7 | 10 | 3 | 8 |

Named exemplars after floor (all three variants unless noted):

| Row | Gold | Before | After |
| ---: | --- | --- | --- |
| 1030 | `1 to 3 per month` | `1 per month` | `1 to 3 per month` |
| 2459 | `7 to 9 per 2 week` | `5 per 5 month` | `7 to 9 per 2 week` |
| 2932 | `seizure free for 9 month` | `13 per 2 month` | `seizure free for multiple year` |
| 5837 | `2 cluster per 3 week, …` | `unknown` | dual cluster label |
| 10097 | `3 cluster per month, …` | `unknown` | dual cluster label |
| 10237 | `4 cluster per month, …` | `unknown` | dual cluster label |
| 14587 / 14628 | dated counts | `no seizure frequency reference` | unchanged |

## Mechanism

1. **Projection, not new clinical selection.** Luna already selected the right
   span for the cluster/range rescues; the floor only makes the label scorer-
   legal.
2. **Anti-regression restores model selection.** Monthly-diary aggregation had
   been overwriting correct seizure-free and fortnight rates. Guarding those
   selected labels recovers 2459 and 2932 without a prompt change.
3. **Residual remains selection-heavy.** Competing rates, false seizure-free
   versus unknown, and `no_reference` demotions of dated counts are mostly
   untouched. The floor does not dissolve the full 48-row core.

## Regressions

Small correct-to-wrong counts remain (2–4 per variant). Observed patterns:

- cadence projection on gold-`unknown, multiple per cluster` rows;
- a few diary/interval interactions outside the protected day/week and
  seizure-free predicates.

Net gain stays positive on every variant. These regressions are development
watch items, not a stop-rule failure.

## Artifacts

- [replay_summary.json](../../experiments/gan2026_luna_projection_antiregression_floor_20260731/replay_summary.json)
- [changed_rows.jsonl](../../experiments/gan2026_luna_projection_antiregression_floor_20260731/changed_rows.jsonl)
- Tests: `tests/test_gan2026_projection_antiregression_floor.py`

## Claim boundary

Development hybrid artifact from no-call replay of saved Luna A/B/C
`validation750` outputs. Not holdout evidence, not clinical validation, and
not authorization to retarget the frozen six-model v0.5 panel in place.
`test450` was not inspected.

## Decision / next

Answer under the protocol stop rule. This floor is retained in the **final Gan
LLM-with-rules ruleset** (2026-07-31), together with dated-count / competing-
rate floors and narrow cross-model guards:
[dated-count report](gan2026_luna_dated_count_competing_rate_report_2026-07-31.md),
[six-model comparison](six_model_comparison_report_2026-07-18.md).
