# Gan 2026 Structured Synthetic Hard Opportunity Panel v0

Synthetic development data for undercovered structured projection opportunity mechanisms. It is not validation750, not holdout, not benchmark evidence, and not a final-label promotion artifact.

## Decision

ready_for_structured_projection_generator_smoke

## Summary

| Metric | Value |
| --- | ---: |
| rows | 240 |
| hard rows | 120 |
| control rows | 120 |
| exact evidence rows | 240 |
| holdout authorized | False |

## Families

| Family | Total | Hard | Control |
| --- | ---: | ---: | ---: |
| `cluster_frequency` | 60 | 30 | 30 |
| `daily_frequency` | 60 | 30 | 30 |
| `other_frequency` | 60 | 30 | 30 |
| `unknown_frequency` | 60 | 30 | 30 |

## Projection Owners

| Owner | Rows |
| --- | ---: |
| `boundary_projection_policy` | 60 |
| `cluster_projection_policy` | 60 |
| `rate_projection_policy` | 120 |

## Next Step

Run a synthetic projection generator smoke over this panel. Promote only mechanism behavior that emits hard rows, suppresses matched controls, preserves exact evidence, and keeps projection ownership explicit.

## Artifacts

- Panel JSONL: `experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.json`
