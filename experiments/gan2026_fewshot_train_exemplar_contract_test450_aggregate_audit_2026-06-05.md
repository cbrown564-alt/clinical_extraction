# Gan 2026 Few-Shot Train-Exemplar Contract Test450 Aggregate Audit

Frozen locked-test aggregate-only audit for the few-shot train-exemplar contract over the combined switch-layer current label. This artifact omits test row ids, clinical text, raw model outputs, and row-level failures.

## Decision

does_not_meet_goal

## Artifacts

- Summary JSON: `experiments/gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_2026-06-05.json`
- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| test rows | 450 |
| raw base correct rows | 342 |
| combined current correct rows | 353 |
| final correct rows | 357 |
| raw base purist proxy | 0.7600 |
| combined current purist proxy | 0.7844 |
| final purist proxy | 0.7933 |
| combined changed rows | 35 |
| contract selected rows | 4 |
| fewshot call ok rows | 448 |
| fewshot parse ok rows | 158 |
| fewshot exact evidence rows | 408 |
| contract changed label precision | 1.0000 |

## Combined Transitions

| Value | Rows |
| --- | ---: |
| `C_to_C` | 340 |
| `C_to_W` | 2 |
| `W_to_C` | 13 |
| `W_to_W` | 95 |

## Contract Transitions

| Value | Rows |
| --- | ---: |
| `C_to_C` | 353 |
| `W_to_C` | 4 |
| `W_to_W` | 93 |

## Combined Families

| Value | Rows |
| --- | ---: |
| `det_state_exact` | 10 |
| `keep_current` | 415 |
| `llm_selector_exact` | 25 |

## Contract Families

| Value | Rows |
| --- | ---: |
| `keep_current` | 446 |
| `multiple_daily_upgrade_from_single_daily` | 1 |
| `sf_current_to_unknown` | 3 |

## Inspection Boundary

No test row ids, clinical text, raw model outputs, or row-level failures are stored in this report.
