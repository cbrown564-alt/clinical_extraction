# Gan 2026 Structured Candidate Event Contract Panel

Validation-development structured candidate/event panel adapted from saved direct-labeler full-validation rows. This is a no-call analysis and does not inspect locked-test rows or authorize a frozen test audit.

## Decision

blocked_before_holdout

## Gate

| Metric | Value |
| --- | ---: |
| selected prediction-bearing rows | 539 |
| W->C rows | 26 |
| C->W rows | 121 |
| C->W rate | 0.2245 |
| parse-ok plus exact-evidence rate | 0.3469 |
| frozen test audit ready | False |

Gate failures: `w_to_c_below_60`, `c_to_w_above_5_percent`, `parse_ok_exact_evidence_below_95_percent`

## Panel

| Metric | Value |
| --- | ---: |
| rows | 750 |
| parse-ok rows | 221 |
| exact-evidence rows | 485 |
| contract-issue rows | 563 |

## Gate Transitions

| Transition | Prediction-Bearing Rows |
| --- | ---: |
| `C_to_C` | 379 |
| `C_to_W` | 121 |
| `W_to_C` | 26 |
| `W_to_W` | 13 |

## Source Transitions

These counts cover all 750 adapted source rows, including rows that were not prediction-bearing under the structured contract.

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 379 |
| `C_to_W` | 329 |
| `W_to_C` | 26 |
| `W_to_W` | 16 |

## Artifacts

- Panel JSONL: `experiments/gan2026_structured_candidate_event_contract_v0_direct_labeler_validation750_panel_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_candidate_event_contract_v0_direct_labeler_validation750_panel_2026-06-05.json`
- Source JSONL: `experiments/gan2026_direct_labeler_full_validation750_over_combined_current_gpt41_2026-06-05.jsonl`

## Inspection Boundary

No locked-test rows are read. Panel rows omit clinical note text.
