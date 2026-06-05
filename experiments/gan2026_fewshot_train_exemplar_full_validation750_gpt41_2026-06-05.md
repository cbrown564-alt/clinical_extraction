# Gan 2026 Few-Shot Train-Exemplar Full Validation

Validation-development few-shot train-exemplar candidate generator over the combined switch-layer current label. No locked-test rows are inspected.

## Decision

freeze_candidate_for_aggregate_audit

## Artifacts

- Row JSONL: `experiments/gan2026_fewshot_train_exemplar_full_validation750_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_fewshot_train_exemplar_full_validation750_gpt41_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 750 |
| call ok rows | 743 |
| parse ok rows | 269 |
| exact evidence rows | 688 |
| current correct rows | 708 |
| raw proposed correct rows | 552 |
| contract projected correct rows | 726 |
| current purist proxy | 0.9440 |
| raw proposed purist proxy | 0.7360 |
| contract projected purist proxy | 0.9680 |
| contract selected rows | 23 |
| contract changed label precision | 1.0000 |

## Raw Proposed Transitions

| Value | Rows |
| --- | ---: |
| `C_to_C` | 525 |
| `C_to_W` | 183 |
| `W_to_C` | 27 |
| `W_to_W` | 15 |

## Contract Transitions

| Value | Rows |
| --- | ---: |
| `C_to_C` | 708 |
| `W_to_C` | 18 |
| `W_to_W` | 24 |

## Contract Families

| Value | Rows |
| --- | ---: |
| `cluster_per_cluster_completion` | 9 |
| `daily_upgrade_from_non_daily` | 5 |
| `explicit_rate_replacement` | 3 |
| `keep_current` | 727 |
| `multiple_daily_upgrade_from_single_daily` | 1 |
| `sf_current_to_unknown` | 5 |
