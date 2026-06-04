# Gan 2026 Selective Abstention-Pressure Review

Validation-development pressure review of staged-hybrid non-prediction rows. Blocked-candidate correctness is development accounting only; this artifact does not change router behavior, prompts, scorer policy, gold labels, locked-test behavior, verifier use, or benchmark-comparable claims.

## Summary

The review covers 34 residual non-prediction rows: 19 coverage-cost rows and 15 protective blocks.

## Review Lanes

| Lane | Rows |
| --- | ---: |
| `anchor_policy_needed` | 2 |
| `date_policy_needed` | 8 |
| `keep_nonprediction` | 9 |
| `trigger_release_candidate` | 2 |
| `trigger_sentinel_boundary_review` | 13 |

## Pressure Classes

| Class | Rows |
| --- | ---: |
| `coverage_cost` | 19 |
| `protective_block` | 15 |

## Next Step

Predeclare a gold-blinded trigger-context release rule and a frozen last-event date policy before changing prediction-bearing behavior.

## Artifacts

- Pressure review JSONL: `experiments/gan2026_staged_hybrid_selective_abstention_pressure_2026-06-04.jsonl`
- Pressure review summary JSON: `experiments/gan2026_staged_hybrid_selective_abstention_pressure_2026-06-04.json`

## Rows

| Row | Reason | Blocked label | Class | Lane |
| ---: | --- | --- | --- | --- |
| 3356 | `trigger_conditioned_frequency` | `seizure free for multiple year` | `protective_block` | `keep_nonprediction` |
| 3371 | `trigger_conditioned_frequency` | `unknown` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 3468 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 3469 | `trigger_conditioned_frequency` | `unknown` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 3482 | `trigger_conditioned_frequency` | `unknown` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 3493 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 4731 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 5490 | `missing_denominator_anchor` | `no seizure frequency reference` | `coverage_cost` | `anchor_policy_needed` |
| 5974 | `trigger_conditioned_frequency` | `seizure free for multiple year` | `protective_block` | `keep_nonprediction` |
| 5977 | `trigger_conditioned_frequency` | `multiple per 6 week` | `coverage_cost` | `trigger_release_candidate` |
| 5996 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 6077 | `trigger_conditioned_frequency` | `seizure free for 8 month` | `protective_block` | `keep_nonprediction` |
| 6087 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 6094 | `trigger_conditioned_frequency` | `3 per week` | `protective_block` | `keep_nonprediction` |
| 6131 | `trigger_conditioned_frequency` | `seizure free for 6 month` | `protective_block` | `keep_nonprediction` |
| 6153 | `trigger_conditioned_frequency` | `1 per 1 to 2 week` | `protective_block` | `keep_nonprediction` |
| 6319 | `trigger_conditioned_frequency` | `1 per week` | `coverage_cost` | `trigger_release_candidate` |
| 6321 | `trigger_conditioned_frequency` | `1 per day` | `protective_block` | `keep_nonprediction` |
| 6368 | `trigger_conditioned_frequency` | `1 per 1 to 2 week` | `protective_block` | `keep_nonprediction` |
| 7093 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 7168 | `trigger_conditioned_frequency` | `2 per year` | `protective_block` | `keep_nonprediction` |
| 9103 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 9877 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 9879 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 11216 | `last_event_boundary` | `seizure free for 4 month` | `protective_block` | `date_policy_needed` |
| 11254 | `last_event_boundary` | `seizure free for multiple year` | `protective_block` | `date_policy_needed` |
| 11259 | `last_event_boundary` | `seizure free for multiple year` | `protective_block` | `date_policy_needed` |
| 11262 | `last_event_boundary` | `unknown` | `coverage_cost` | `date_policy_needed` |
| 11272 | `last_event_boundary` | `seizure free for multiple year` | `protective_block` | `date_policy_needed` |
| 11282 | `last_event_boundary` | `unknown` | `coverage_cost` | `date_policy_needed` |
| 11337 | `trigger_conditioned_frequency` | `no seizure frequency reference` | `coverage_cost` | `trigger_sentinel_boundary_review` |
| 14040 | `missing_denominator_anchor` | `no seizure frequency reference` | `coverage_cost` | `anchor_policy_needed` |
| 14810 | `last_event_boundary` | `12 per month` | `protective_block` | `date_policy_needed` |
| 14821 | `last_event_boundary` | `17 per month` | `protective_block` | `date_policy_needed` |