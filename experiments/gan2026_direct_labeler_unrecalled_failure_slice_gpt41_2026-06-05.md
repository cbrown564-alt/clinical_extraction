# Gan 2026 Direct Labeler Unrecalled Failure Slice

Validation-development hard-slice smoke over unrecalled and semantic-state assembly failures. This does not inspect locked test rows or authorize benchmark-comparable claims.

## Decision

promising_candidate_generator_needs_gating

## Artifacts

- Row JSONL: `experiments/gan2026_direct_labeler_unrecalled_failure_slice_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_direct_labeler_unrecalled_failure_slice_gpt41_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 31 |
| call ok rows | 31 |
| parse ok rows | 6 |
| exact evidence rows | 28 |
| direct correct rows | 21 |
| direct slice purist proxy | 0.6774 |
| slice w to c rows | 21 |
| slice c to w rows | 0 |
| base full correct rows | 708 |
| projected full correct rows if oracle switched slice | 729 |
| projected full purist proxy if oracle switched slice | 0.9720 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `W_to_C` | 21 |
| `W_to_W` | 10 |

## Recoverability Classes

| Class | Rows |
| --- | ---: |
| `no_recalled_candidate` | 14 |
| `semantic_state_only` | 17 |

## Rows

| Row | Class | Current | Direct | Gold | Transition | Evidence exact |
| ---: | --- | --- | --- | --- | --- | --- |
| 3528 | `no_recalled_candidate` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` | True |
| 5534 | `no_recalled_candidate` | `seizure free for multiple year` | `1 per multiple month` | `1 per multiple month` | `W_to_C` | True |
| 5974 | `no_recalled_candidate` | `` | `unknown` | `unknown` | `W_to_C` | True |
| 6094 | `semantic_state_only` | `` | `no seizure frequency reference` | `3 per month` | `W_to_W` | True |
| 6131 | `no_recalled_candidate` | `` | `unknown` | `unknown` | `W_to_C` | True |
| 6153 | `semantic_state_only` | `` | `9 per 4 week` | `9 per month` | `W_to_C` | True |
| 6209 | `no_recalled_candidate` | `1 per day` | `multiple per day` | `multiple per day` | `W_to_C` | True |
| 6368 | `no_recalled_candidate` | `` | `multiple per day` | `unknown` | `W_to_C` | True |
| 6501 | `no_recalled_candidate` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` | True |
| 6571 | `no_recalled_candidate` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | `W_to_W` | True |
| 7168 | `no_recalled_candidate` | `` | `2 per year` | `unknown` | `W_to_W` | True |
| 9888 | `no_recalled_candidate` | `seizure free for multiple year` | `no seizure frequency reference` | `unknown` | `W_to_C` | True |
| 9937 | `semantic_state_only` | `1 per multiple week` | `unknown` | `1 cluster per month, multiple per cluster` | `W_to_W` | True |
| 9943 | `semantic_state_only` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 cluster per 4 to 5 week, multiple per cluster` | `W_to_W` | True |
| 9955 | `semantic_state_only` | `1 per month` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `W_to_C` | True |
| 10677 | `semantic_state_only` | `1 per month` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `W_to_C` | True |
| 10996 | `semantic_state_only` | `1 to 2 cluster per month, multiple per cluster` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `W_to_C` | True |
| 12422 | `semantic_state_only` | `4 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12438 | `semantic_state_only` | `2 to 3 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12456 | `semantic_state_only` | `3 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12460 | `semantic_state_only` | `2 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12468 | `semantic_state_only` | `4 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 13843 | `no_recalled_candidate` | `no seizure frequency reference` | `` | `seizure free for multiple month` | `W_to_W` | False |
| 13858 | `no_recalled_candidate` | `no seizure frequency reference` | `unknown` | `seizure free for multiple month` | `W_to_W` | True |
| 13889 | `no_recalled_candidate` | `no seizure frequency reference` | `seizure free for multiple year` | `seizure free for multiple month` | `W_to_C` | True |
| 14025 | `no_recalled_candidate` | `seizure free for multiple year` | `no seizure frequency reference` | `unknown` | `W_to_C` | True |
| 14810 | `semantic_state_only` | `` | `seizure free for multiple year` | `1 per month` | `W_to_W` | True |
| 14821 | `semantic_state_only` | `` | `seizure free for multiple year` | `1 per month` | `W_to_W` | False |
| 15593 | `semantic_state_only` | `2 per 6 month` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `W_to_C` | True |
| 15672 | `semantic_state_only` | `2 per 6 week` | `1 per day` | `1 per day` | `W_to_C` | True |
| 15834 | `semantic_state_only` | `1 per multiple month` | `` | `5 per week` | `W_to_W` | False |

## Interpretation Boundary

This hard slice is intentionally enriched for current validation failures. Its slice accuracy is not a full-validation score; it only estimates whether a direct-label candidate source creates useful alternatives for rows that saved candidate discovery missed.
