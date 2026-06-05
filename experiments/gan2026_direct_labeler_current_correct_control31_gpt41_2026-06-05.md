# Gan 2026 Direct Labeler Unrecalled Failure Slice

Validation-development hard-slice smoke over unrecalled and semantic-state assembly failures. This does not inspect locked test rows or authorize benchmark-comparable claims.

## Decision

reject_as_broad_switch_source

## Artifacts

- Row JSONL: `experiments/gan2026_direct_labeler_current_correct_control31_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_direct_labeler_current_correct_control31_gpt41_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 31 |
| call ok rows | 31 |
| parse ok rows | 13 |
| exact evidence rows | 22 |
| direct correct rows | 21 |
| direct slice purist proxy | 0.6774 |
| slice w to c rows | 0 |
| slice c to w rows | 10 |
| base full correct rows | 708 |
| projected full correct rows if oracle switched slice | 698 |
| projected full purist proxy if oracle switched slice | 0.9307 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 21 |
| `C_to_W` | 10 |

## Recoverability Classes

| Class | Rows |
| --- | ---: |
| `current_correct_control` | 31 |

## Rows

| Row | Class | Current | Direct | Gold | Transition | Evidence exact |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | `current_correct_control` | `4 per day` | `4 per day` | `4 per day` | `C_to_C` | True |
| 40 | `current_correct_control` | `4 per week` | `` | `4 per week` | `C_to_W` | False |
| 79 | `current_correct_control` | `6 to 7 per year` | `` | `6 to 7 per year` | `C_to_W` | False |
| 103 | `current_correct_control` | `2 to 4 per year` | `2 to 4 per year` | `2 to 4 per year` | `C_to_C` | True |
| 128 | `current_correct_control` | `17 per month` | `` | `17 per month` | `C_to_W` | False |
| 156 | `current_correct_control` | `1 per 6 day` | `1 per 6 day` | `1 per 6 day` | `C_to_C` | True |
| 180 | `current_correct_control` | `1 per 7 day` | `1 per 7 day` | `1 per 7 day` | `C_to_C` | True |
| 182 | `current_correct_control` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `C_to_C` | True |
| 187 | `current_correct_control` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `C_to_C` | True |
| 190 | `current_correct_control` | `1 per 4 week` | `` | `1 per 4 week` | `C_to_W` | False |
| 198 | `current_correct_control` | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `C_to_C` | True |
| 212 | `current_correct_control` | `1 per 3 to 4 week` | `1 per 3 to 4 week` | `1 per 3 to 4 week` | `C_to_C` | True |
| 218 | `current_correct_control` | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `C_to_C` | True |
| 243 | `current_correct_control` | `1 per 4 month` | `` | `1 per 4 month` | `C_to_W` | False |
| 278 | `current_correct_control` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 280 | `current_correct_control` | `multiple per day` | `multiple per day` | `multiple per day` | `C_to_C` | True |
| 338 | `current_correct_control` | `no seizure frequency reference` | `multiple per month` | `multiple per month` | `C_to_C` | True |
| 409 | `current_correct_control` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 419 | `current_correct_control` | `2 per year` | `2 per year` | `2 per year` | `C_to_C` | True |
| 446 | `current_correct_control` | `2 per week` | `2 per week` | `2 per week` | `C_to_C` | True |
| 466 | `current_correct_control` | `21 to 28 per month` | `21 to 28 per month` | `21 to 28 per month` | `C_to_C` | True |
| 467 | `current_correct_control` | `9 per month` | `9 per month` | `9 per month` | `C_to_C` | True |
| 531 | `current_correct_control` | `12 to 30 per 3 month` | `` | `12 to 30 per 3 month` | `C_to_W` | False |
| 598 | `current_correct_control` | `1 per 8 month` | `` | `1 per 8 month` | `C_to_W` | False |
| 659 | `current_correct_control` | `2 per 4 day` | `` | `2 per 4 day` | `C_to_W` | False |
| 665 | `current_correct_control` | `2 per 2 week` | `2 per 2 week` | `2 per 2 week` | `C_to_C` | True |
| 678 | `current_correct_control` | `2 per 4 month` | `2 per 4 month` | `2 per 4 month` | `C_to_C` | True |
| 694 | `current_correct_control` | `1 per week` | `1 per week` | `1 per week` | `C_to_C` | True |
| 704 | `current_correct_control` | `2 per month` | `2 per month` | `2 per month` | `C_to_C` | True |
| 725 | `current_correct_control` | `1 per day` | `multiple per day` | `1 per day` | `C_to_W` | True |
| 731 | `current_correct_control` | `1 per day` | `multiple per day` | `1 per day` | `C_to_W` | False |

## Interpretation Boundary

This hard slice is intentionally enriched for current validation failures. Its slice accuracy is not a full-validation score; it only estimates whether a direct-label candidate source creates useful alternatives for rows that saved candidate discovery missed.
