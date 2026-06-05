# Gan 2026 Few-Shot Train-Exemplar Contract Test450 Aggregate Audit

Frozen locked-test aggregate-only audit for the few-shot train-exemplar contract over the combined switch-layer current label. This artifact omits test row ids, clinical text, raw model outputs, and row-level failures.

## Decision

does_not_meet_goal

## Artifacts

- Summary JSON: `experiments\gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_qwen36_35b_2026-06-05.json`
- Source artifact: `experiments\gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| test rows | 450 |
| raw base correct rows | 342 |
| combined current correct rows | 355 |
| final correct rows | 359 |
| raw base purist proxy | 0.7600 |
| combined current purist proxy | 0.7889 |
| final purist proxy | 0.7978 |
| combined changed rows | 17 |
| contract selected rows | 6 |
| fewshot call ok rows | 450 |
| fewshot parse ok rows | 178 |
| fewshot exact evidence rows | 412 |
| contract changed label precision | 0.8333 |

## Combined Transitions

| Value | Rows |
| --- | ---: |
| `C_to_C` | 342 |
| `W_to_C` | 13 |
| `W_to_W` | 95 |

## Contract Transitions

| Value | Rows |
| --- | ---: |
| `C_to_C` | 354 |
| `C_to_W` | 1 |
| `W_to_C` | 5 |
| `W_to_W` | 90 |

## Combined Families

| Value | Rows |
| --- | ---: |
| `det_state_exact` | 10 |
| `keep_current` | 433 |
| `llm_selector_exact` | 7 |

## Contract Families

| Value | Rows |
| --- | ---: |
| `cluster_per_cluster_completion` | 1 |
| `keep_current` | 444 |
| `multiple_daily_upgrade_from_single_daily` | 2 |
| `sf_current_to_unknown` | 3 |

## Inspection Boundary

No test row ids, clinical text, raw model outputs, or row-level failures are stored in this report.
