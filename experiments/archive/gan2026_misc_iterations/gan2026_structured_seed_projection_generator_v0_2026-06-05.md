# Gan 2026 Structured Seed Projection Generator v0

Synthetic validation-development smoke for projection-owner-aware structured event generation. It writes no source note text, uses no locked-test artifacts, and is not benchmark evidence.

## Decision

promote_to_validation_projection_owner_panel

## Summary

| Metric | Value |
| --- | ---: |
| rows | 180 |
| hard rows | 90 |
| control rows | 90 |
| hard emit rows | 90 |
| control suppressed rows | 90 |
| exact evidence rows | 180 |
| projection-ownership explicit rows | 180 |
| source-note-text rows | 0 |
| expected action mismatches | 0 |

## Projection Owners

| Owner | Rows |
| --- | ---: |
| `boundary_projection_policy` | 60 |
| `cluster_projection_policy` | 60 |
| `rate_projection_policy` | 60 |

## Families

| Family | Rows |
| --- | ---: |
| `cluster_completion` | 60 |
| `seizure_free_to_unknown` | 60 |
| `yearly_to_daily` | 60 |

## Next Step

Port this projection-owner schema to validation hard/control expansion, including matched controls and the boundary C->W no-regression case. Do not write a frozen test450 protocol until validation gates pass.

## Artifacts

- Projection generator JSONL: `experiments/gan2026_structured_seed_projection_generator_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_seed_projection_generator_v0_2026-06-05.json`
- Source panel JSONL: `experiments/gan2026_structured_seed_expansion_panel_v0_2026-06-05.jsonl`
