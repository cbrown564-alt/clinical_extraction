# Gan 2026 Structured Validation Projection Port Panel v0

Validation-development hard/control port of the passing synthetic structured projection mechanisms. It keeps only exact-evidence rows, balances matched controls by target family, writes no note text, uses no locked-test row-level artifacts, and does not authorize holdout use.

## Decision

validation_projection_port_panel_ready_for_extractor_smoke_undercoverage

## Summary

| Metric | Value |
| --- | ---: |
| rows | 47 |
| hard rows | 23 |
| control rows | 23 |
| no-regression rows | 1 |
| selected prediction-bearing rows | 23 |
| W->C rows | 23 |
| C->W rows | 0 |
| parse-ok plus exact-evidence rate | 1.0000 |
| exact evidence rows | 47 |
| projection-ownership explicit rows | 47 |
| source-note-text rows | 0 |
| frozen test audit ready | False |
| holdout authorized | False |

## Gate Failures

- `coverage_below_150`
- `w_to_c_below_60`

## Target Families

| Family | Hard | Control |
| --- | ---: | ---: |
| `cluster_frequency` | 2 | 2 |
| `daily_frequency` | 7 | 7 |
| `other_frequency` | 5 | 5 |
| `seizure_free` | 2 | 2 |
| `unknown_frequency` | 6 | 6 |
| `weekly_frequency` | 1 | 1 |

## Projection Owners

| Owner | Rows |
| --- | ---: |
| `boundary_projection_policy` | 17 |
| `cluster_projection_policy` | 4 |
| `rate_projection_policy` | 26 |

## Next Step

Run an extractor smoke over this exact-evidence validation port panel. Treat it as mechanism diagnostics only unless coverage and W->C gates are changed by a written protocol.

## Artifacts

- Panel JSONL: `experiments/gan2026_structured_validation_projection_port_panel_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_validation_projection_port_panel_v0_2026-06-05.json`
- Source miner JSONL: `experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.jsonl`
