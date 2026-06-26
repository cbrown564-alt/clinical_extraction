# Gan 2026 Selector v0.5 Boundary-Rescue Audit

Date: 2026-06-15

This is a validation-only audit over saved v0.5 selector rows. It isolates the new fresh-boundary-rescue actions added on top of v0.4. No model calls and no holdout rows are read.

## Summary

- All v0.5 changed actions: rows 40, changed 40, W->C 31, C->W 0, net 31, precision 0.775
- Fresh boundary rescue actions: rows 14, changed 14, W->C 14, C->W 0, net 14, precision 1.0
- Added actions versus v0.4: rows 14, changed 14, W->C 14, C->W 0, net 14, precision 1.0

## Rescue Type

| Gate | Rows | W->C | C->W | Net | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| `fresh_boundary_rescue_v0_5:deterministic_no_reference_to_fresh_seizure_free` | 3 | 3 | 0 | 3 | 1.0 |
| `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | 11 | 11 | 0 | 11 | 1.0 |

## Boundary Bands

| Band | Rows | W->C | C->W | Net | Precision |
| --- | ---: | ---: | ---: | ---: | ---: |
| `band_unknown` | 11 | 11 | 0 | 11 | 1.0 |
| `band_zero` | 3 | 3 | 0 | 3 | 1.0 |

## Validation Blocks

| Positions | Rows | W->C | C->W | Net |
| --- | ---: | ---: | ---: | ---: |
| `1-125` | 0 | 0 | 0 | 0 |
| `126-250` | 1 | 1 | 0 | 1 |
| `251-375` | 5 | 5 | 0 | 5 |
| `376-500` | 3 | 3 | 0 | 3 |
| `501-625` | 4 | 4 | 0 | 4 |
| `626-750` | 1 | 1 | 0 | 1 |

## Rescue Rows

| Source row | Gold | Deterministic | Fresh selected | Gate | Transition |
| ---: | --- | --- | --- | --- | --- |
| 3528 | `unknown` | `seizure free for multiple year` | `no seizure frequency reference` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 6077 | `unknown` | `seizure free for 8 month` | `no seizure frequency reference` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 6131 | `unknown` | `seizure free for 6 month` | `no seizure frequency reference` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 6244 | `unknown` | `seizure free for multiple year` | `unknown` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 6501 | `unknown` | `seizure free for multiple year` | `unknown` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 6987 | `unknown` | `seizure free for multiple year` | `unknown` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 9888 | `unknown` | `seizure free for multiple year` | `no seizure frequency reference` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 10618 | `unknown, 4 to 6 per cluster` | `seizure free for multiple year` | `no seizure frequency reference` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 11259 | `unknown` | `seizure free for multiple year` | `unknown` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 13843 | `seizure free for multiple month` | `no seizure frequency reference` | `seizure free for multiple year` | `fresh_boundary_rescue_v0_5:deterministic_no_reference_to_fresh_seizure_free` | `wrong_to_correct` |
| 13858 | `seizure free for multiple month` | `no seizure frequency reference` | `seizure free for multiple year` | `fresh_boundary_rescue_v0_5:deterministic_no_reference_to_fresh_seizure_free` | `wrong_to_correct` |
| 13889 | `seizure free for multiple month` | `no seizure frequency reference` | `seizure free for multiple year` | `fresh_boundary_rescue_v0_5:deterministic_no_reference_to_fresh_seizure_free` | `wrong_to_correct` |
| 14076 | `unknown` | `seizure free for multiple year` | `unknown` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |
| 15193 | `multiple per 13 month` | `seizure free for multiple year` | `unknown` | `fresh_boundary_rescue_v0_5:deterministic_seizure_free_to_fresh_uncertain_boundary` | `wrong_to_correct` |

## Interpretation

The v0.5 additions are clean on saved validation: all 14 fresh-boundary-rescue actions are wrong-to-correct with no correct-to-wrong regressions. The gains are concentrated in `band_unknown` and `band_zero`, matching the clinical rationale: deterministic seizure-free/no-reference boundary overreach is corrected by V12 fresh evidence.

Decision: revise, not freeze. This is validation-mined saved-output evidence, so it supports v0.5 as the next front-runner but does not authorize a holdout-facing protocol without targeted robustness evidence.
