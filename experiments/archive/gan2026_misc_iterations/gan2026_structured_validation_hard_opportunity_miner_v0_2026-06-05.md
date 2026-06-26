# Gan 2026 Structured Validation Hard Opportunity Miner v0

Validation-development hard-opportunity miner only. It uses validation gold labels to define development opportunities, writes no note text, uses no locked-test row-level artifacts, and does not authorize holdout-facing use.

## Decision

validation_hard_opportunity_surface_under_gate

## Summary

| Metric | Value |
| --- | ---: |
| rows | 79 |
| hard rows | 38 |
| control rows | 40 |
| no-regression rows | 1 |
| selected prediction-bearing rows | 38 |
| W->C rows | 38 |
| C->W rows | 0 |
| parse-ok plus exact-evidence rate | 0.6053 |
| W->C gate reachable on current surface | False |
| frozen test audit ready | False |
| holdout authorized | False |

## Gate Failures

- `coverage_below_150`
- `w_to_c_below_60`
- `parse_ok_exact_evidence_below_95_percent`

## Target Families

| Family | Rows |
| --- | ---: |
| `cluster_frequency` | 16 |
| `daily_frequency` | 16 |
| `monthly_frequency` | 2 |
| `no_reference` | 1 |
| `other_frequency` | 14 |
| `seizure_free` | 6 |
| `unknown` | 1 |
| `unknown_frequency` | 18 |
| `weekly_frequency` | 4 |
| `yearly_frequency` | 1 |

## Next Step

The current validation assembly does not expose enough residual misses to satisfy the 60 W->C gate if this surface remains fixed. Either lower the gate for validation-development diagnostics or change the base surface/objective before writing any frozen test protocol.

## Artifacts

- Miner JSONL: `experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_validation_hard_opportunity_miner_v0_2026-06-05.json`
- Source current candidate JSONL: `experiments/gan2026_untagged_nonprediction_release_candidate_v0_assembled_candidate_2026-06-05.jsonl`
- Source no-regression JSONL: `experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.jsonl`
