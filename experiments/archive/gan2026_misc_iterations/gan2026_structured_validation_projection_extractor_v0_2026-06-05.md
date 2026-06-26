# Gan 2026 Structured Validation Projection Extractor v0

Validation-development projection-owner extractor smoke only. It loads validation note text in memory, writes no note text, suppresses matched controls plus the named no-regression row, uses no locked-test row-level artifacts, and does not authorize holdout-facing use.

## Decision

validation_projection_extractor_smoke_passed_undercoverage

## Summary

| Metric | Value |
| --- | ---: |
| rows | 47 |
| hard rows | 23 |
| control rows | 23 |
| no-regression rows | 1 |
| hard emit rows | 23 |
| control suppressed rows | 23 |
| no-regression suppressed rows | 1 |
| hard exact evidence rows | 23 |
| control reference retrievable rows | 21 |
| no-regression exact evidence rows | 1 |
| selected prediction-bearing rows | 23 |
| W->C rows | 23 |
| C->W rows | 0 |
| parse-ok plus exact-evidence rate | 1.0000 |
| validation smoke passed | True |
| frozen test audit ready | False |
| holdout authorized | False |

## Gate Failures

- `coverage_below_150`
- `w_to_c_below_60`

## Projection Owners

| Owner | Rows |
| --- | ---: |
| `boundary_projection_policy` | 27 |
| `cluster_projection_policy` | 10 |
| `rate_projection_policy` | 10 |

## Seed Families

| Family | Rows |
| --- | ---: |
| `cluster_completion` | 10 |
| `seizure_free_to_unknown` | 26 |
| `yearly_to_daily` | 10 |

## Next Step

Broaden validation hard opportunities before any frozen test450 protocol. Keep no-regression controls active and do not use locked-test row-level artifacts.

## Artifacts

- Extractor JSONL: `experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.jsonl`
