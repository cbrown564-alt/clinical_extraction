# Gan 2026 Structured Validation Projection Panel v0

Validation-development projection-owner panel only. It combines saved validation seed hard/control rows with the named boundary no-regression case, writes no note text, uses no locked-test row-level artifacts, and does not authorize holdout-facing use.

## Decision

validation_projection_panel_ready_for_extractor_design

## Summary

| Metric | Value |
| --- | ---: |
| rows | 47 |
| hard rows | 23 |
| control rows | 23 |
| no-regression case rows | 1 |
| selected prediction-bearing rows | 24 |
| W->C rows | 23 |
| C->W rows | 1 |
| C->W rate | 0.0417 |
| parse-ok plus exact-evidence rate | 1.0000 |
| projection-ownership explicit rows | 47 |
| source-note-text rows | 0 |
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

Implement the validation projection-owner extractor smoke over this panel. Keep the boundary C->W row as a no-regression control and do not write a frozen test450 protocol until validation gates pass.

## Artifacts

- Panel JSONL: `experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_validation_projection_panel_v0_2026-06-05.json`
- Source seed panel JSONL: `experiments/gan2026_structured_seed_validation_panel_v0_2026-06-05.jsonl`
- Source projection audit JSONL: `experiments/gan2026_structured_event_projection_audit_v0_2026-06-05.jsonl`
