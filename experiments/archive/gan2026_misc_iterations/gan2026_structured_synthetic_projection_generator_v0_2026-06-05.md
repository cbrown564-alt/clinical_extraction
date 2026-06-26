# Gan 2026 Structured Synthetic Projection Generator v0

Synthetic development smoke for undercovered structured projection mechanisms. It requires hard emits, matched-control suppression, exact evidence, explicit projection ownership, no source note text in artifacts, and no locked-test row-level use.

## Decision

synthetic_projection_generator_smoke_passed

## Summary

| Metric | Value |
| --- | ---: |
| rows | 240 |
| hard rows | 120 |
| control rows | 120 |
| hard emit rows | 120 |
| control suppressed rows | 120 |
| exact evidence rows | 240 |
| projection-ownership explicit rows | 240 |
| source-note-text rows | 0 |
| expected action mismatches | 0 |

## Families

| Family | Rows |
| --- | ---: |
| `cluster_frequency` | 60 |
| `daily_frequency` | 60 |
| `other_frequency` | 60 |
| `unknown_frequency` | 60 |

## Projection Owners

| Owner | Rows |
| --- | ---: |
| `boundary_projection_policy` | 60 |
| `cluster_projection_policy` | 60 |
| `rate_projection_policy` | 120 |

## Next Step

Port only the passing high-precision mechanism behavior back to validation hard/control design; do not write a frozen test450 protocol until validation gates pass.

## Artifacts

- Projection generator JSONL: `experiments/gan2026_structured_synthetic_projection_generator_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_synthetic_projection_generator_v0_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_structured_synthetic_hard_opportunity_panel_v0_2026-06-05.jsonl`
