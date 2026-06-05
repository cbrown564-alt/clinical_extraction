# Gan 2026 Few-Shot Train-Exemplar Contract Test450 Aggregate Audit

Frozen locked-test aggregate-only audit for the few-shot train-exemplar contract over the combined switch-layer current label. This artifact omits test row ids, clinical text, raw model outputs, and row-level failures.

## Decision

does_not_meet_goal

## Artifacts

- Summary JSON: `experiments/gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_smoke1_2026-06-05.json`
- Source artifact: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_test450_gpt41mini_v0_deterministic_safety_floor_live_2026-06-03.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| test rows | 1 |
| raw base correct rows | 1 |
| combined current correct rows | 0 |
| final correct rows | 0 |
| raw base purist proxy | 1.0000 |
| combined current purist proxy | 0.0000 |
| final purist proxy | 0.0000 |
| combined changed rows | 1 |
| contract selected rows | 0 |
| fewshot call ok rows | 1 |
| fewshot parse ok rows | 0 |
| fewshot exact evidence rows | 1 |
| contract changed label precision | 0.0000 |

## Combined Transitions

| Value | Rows |
| --- | ---: |
| `C_to_W` | 1 |

## Contract Transitions

| Value | Rows |
| --- | ---: |
| `W_to_W` | 1 |

## Combined Families

| Value | Rows |
| --- | ---: |
| `llm_selector_exact` | 1 |

## Contract Families

| Value | Rows |
| --- | ---: |
| `keep_current` | 1 |

## Inspection Boundary

No test row ids, clinical text, raw model outputs, or row-level failures are stored in this report.
