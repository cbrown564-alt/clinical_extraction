# Gan 2026 Validation750 Pre/Post Comparison

Date: 2026-06-07

Scope: side-by-side comparison of the reset-native `validation750` surface
before and after the four generalization tasks, using the frozen baseline
artifact, the saved post-task artifact, and a fresh replay from the current
workspace.

This is validation-development mechanics only. It is not a benchmark-comparable
claim.

## Artifacts Compared

- Pre baseline (frozen June 7 reset baseline):
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0.json`
- Saved post-task bundle (dated 2026-06-07):
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_2026-06-07.json`
- Saved post-task ablation for cluster-default rule:
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v6_repaired_recovered_ablated_2026-06-07.json`
- Fresh replay from the current workspace (run on 2026-06-07 during this comparison):
  `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_current_compare_2026-06-07.json`

## Top-Line Comparison

| Surface | Pre baseline | Saved post-task | Fresh current replay |
| --- | ---: | ---: | ---: |
| input assessment rows | 750 | 750 | 750 |
| projection rows | 750 | 750 | 750 |
| rendered labels | 580 | 580 | 580 |
| null renders | 170 | 170 | 170 |
| scored rows | 580 | 580 | 580 |
| Purist-correct scored rows | 488 | 504 | 498 |
| Purist accuracy on scored | 84.14% | 86.90% | 85.86% |
| Pragmatic-correct scored rows | 520 | 527 | 522 |
| Pragmatic accuracy on scored | 89.66% | 90.86% | 90.00% |
| exact normalized matches | 418 | 430 | 422 |
| routed rows | 73 | 73 | 68 |
| deterministic verification actions | 73 abstain | 73 abstain | 68 abstain |

## Pre -> Saved Post

The saved 2026-06-07 post-task artifact is a real improvement over the frozen
baseline while keeping coverage stable:

- Purist correct: `488 -> 504` (`+16`)
- Pragmatic correct: `520 -> 527` (`+7`)
- Exact normalized matches: `418 -> 430` (`+12`)
- Rendered rows, null renders, scored rows, and routed rows: unchanged

The row-level delta is narrow and interpretable:

- `38` rows changed label and/or correctness
- `19` Purist wrong-to-correct transitions
- `3` Purist correct-to-wrong regressions
- `14` rows changed rendered label without changing Purist correctness

Visible aggregate gains came from two promoted rules:

- `cluster_cadence_default_multiple_per_cluster_v0`
  - touched `30` rows
  - `13` Purist wrong-to-correct
  - `3` Purist correct-to-wrong
- `date_anchored_ytd_denominator_v0`
  - touched `8` rows
  - `6` Purist wrong-to-correct
  - `0` Purist correct-to-wrong

Representative improvements:

- row `5837`: `2 per 3 week -> 2 cluster per 3 week, multiple per cluster`
- row `9943`: `1 per 4 to 5 week -> 1 cluster per 4 to 5 week, multiple per cluster`
- row `12788`: `6 per year -> 6 per 4 month`
- row `12810`: `5 per year -> 5 per 2 month`

Representative regressions:

- row `187`: `1 per 7 to 9 day -> 1 cluster per 7 to 9 day, multiple per cluster`
- row `190`: `1 per 4 week -> 1 cluster per 4 week, multiple per cluster`
- row `5921`: `1 per 6 to 8 week -> 1 cluster per 6 to 8 week, multiple per cluster`

## Saved Post Ablation Read

Disabling `project_cluster_cadence_default_multiple_per_cluster` on the saved
post-task bundle gives:

- Purist correct: `504 -> 494` (`-10`)
- Pragmatic correct: `527 -> 525` (`-2`)
- Exact normalized matches: `430 -> 426` (`-4`)

That means the saved post-task lift splits as:

- `+10` Purist from the cluster-default component
- the remaining `+6` Purist over baseline from other active post-task changes

On the saved row-level diff, the remaining visible aggregate lift comes from
`date_anchored_ytd_denominator_v0`. G3 and G4 do not add a visible aggregate
score delta on this saved `validation750` replay, though they may still matter
for coverage, routing, or targeted slices.

## Fresh Current Replay

A fresh replay from the current workspace does **not** reproduce the stronger
saved post-task bundle.

Compared with the frozen baseline:

- Purist correct: `488 -> 498` (`+10`)
- Pragmatic correct: `520 -> 522` (`+2`)
- Exact normalized matches: `418 -> 422` (`+4`)
- Routed rows: `73 -> 68` (`-5`)

Compared with the saved post-task bundle:

- Purist correct: `504 -> 498` (`-6`)
- Pragmatic correct: `527 -> 522` (`-5`)
- Exact normalized matches: `430 -> 422` (`-8`)
- Routed rows: `73 -> 68` (`-5`)

The projection rule inventory explains most of the drift:

- Saved post-task replay includes:
  - `date_anchored_ytd_denominator_v0: 8`
  - `cluster_cadence_default_multiple_per_cluster_v0: 30`
- Fresh current replay includes:
  - `cluster_cadence_default_multiple_per_cluster_v0: 29`
  - `cyclic_pattern_with_explicit_operands_rendered_v0: 10`
  - `cyclic_window_pattern_routed_v0: 7`
  - `sleep_restricted_pattern_routed_v0: 3`
  - no `date_anchored_ytd_denominator_v0`

Interpretation:

- The current workspace replay preserves the cluster-default lift and adds G4
  route/representation behavior.
- The current workspace replay does not show active YTD projection usage on the
  full `validation750` surface, which is the main reason it falls short of the
  saved `504` Purist result.

## Bottom Line

There are two materially different post-task reads on 2026-06-07:

1. The saved post-task bundle improved `validation750` from `488` to `504`
   Purist-correct scored rows at unchanged coverage.
2. The current workspace replay improves the same frozen baseline only from
   `488` to `498`, while also reducing routed rows from `73` to `68`.

So the cleanest answer is:

- **pre** = `488 / 580` Purist-correct scored rows (`84.14%`)
- **saved post** = `504 / 580` (`86.90%`)
- **current post replay** = `498 / 580` (`85.86%`)

If the intent is to claim the full post-task result, the saved artifact supports
that claim. If the intent is to describe the code as it exists in the workspace
right now, the current replay supports only the lower `498 / 580` result.
