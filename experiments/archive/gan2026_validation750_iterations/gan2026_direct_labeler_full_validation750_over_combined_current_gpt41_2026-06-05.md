# Gan 2026 Direct Labeler Unrecalled Failure Slice

Validation-development hard-slice smoke over unrecalled and semantic-state assembly failures. This does not inspect locked test rows or authorize benchmark-comparable claims.

## Decision

reject_as_broad_switch_source

## Artifacts

- Row JSONL: `experiments/gan2026_direct_labeler_full_validation750_over_combined_current_gpt41_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_direct_labeler_full_validation750_over_combined_current_gpt41_2026-06-05.json`

## Metrics

| Metric | Value |
| --- | ---: |
| row count | 750 |
| call ok rows | 750 |
| parse ok rows | 221 |
| exact evidence rows | 485 |
| direct correct rows | 405 |
| direct slice purist proxy | 0.5400 |
| slice w to c rows | 26 |
| slice c to w rows | 329 |
| base full correct rows | 708 |
| projected full correct rows if oracle switched slice | 405 |
| projected full purist proxy if oracle switched slice | 0.5400 |

## Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 379 |
| `C_to_W` | 329 |
| `W_to_C` | 26 |
| `W_to_W` | 16 |

## Recoverability Classes

| Class | Rows |
| --- | ---: |
| `full_validation_candidate_surface` | 750 |

## Rows

| Row | Class | Current | Direct | Gold | Transition | Evidence exact |
| ---: | --- | --- | --- | --- | --- | --- |
| 10 | `full_validation_candidate_surface` | `4 per day` | `4 per day` | `4 per day` | `C_to_C` | True |
| 40 | `full_validation_candidate_surface` | `4 per week` | `` | `4 per week` | `C_to_W` | False |
| 79 | `full_validation_candidate_surface` | `6 to 7 per year` | `` | `6 to 7 per year` | `C_to_W` | False |
| 103 | `full_validation_candidate_surface` | `2 to 4 per year` | `2 to 4 per year` | `2 to 4 per year` | `C_to_C` | True |
| 128 | `full_validation_candidate_surface` | `17 per month` | `` | `17 per month` | `C_to_W` | False |
| 156 | `full_validation_candidate_surface` | `1 per 6 day` | `1 per 6 day` | `1 per 6 day` | `C_to_C` | True |
| 180 | `full_validation_candidate_surface` | `1 per 7 day` | `1 per 7 day` | `1 per 7 day` | `C_to_C` | True |
| 182 | `full_validation_candidate_surface` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `C_to_C` | True |
| 187 | `full_validation_candidate_surface` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `C_to_C` | True |
| 190 | `full_validation_candidate_surface` | `1 per 4 week` | `` | `1 per 4 week` | `C_to_W` | False |
| 198 | `full_validation_candidate_surface` | `1 per 4 week` | `1 per 4 week` | `1 per 4 week` | `C_to_C` | True |
| 212 | `full_validation_candidate_surface` | `1 per 3 to 4 week` | `1 per 3 to 4 week` | `1 per 3 to 4 week` | `C_to_C` | True |
| 218 | `full_validation_candidate_surface` | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `C_to_C` | True |
| 243 | `full_validation_candidate_surface` | `1 per 4 month` | `` | `1 per 4 month` | `C_to_W` | False |
| 278 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 280 | `full_validation_candidate_surface` | `multiple per day` | `multiple per day` | `multiple per day` | `C_to_C` | True |
| 338 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per month` | `multiple per month` | `C_to_C` | True |
| 409 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 419 | `full_validation_candidate_surface` | `2 per year` | `2 per year` | `2 per year` | `C_to_C` | True |
| 446 | `full_validation_candidate_surface` | `2 per week` | `2 per week` | `2 per week` | `C_to_C` | True |
| 466 | `full_validation_candidate_surface` | `21 to 28 per month` | `21 to 28 per month` | `21 to 28 per month` | `C_to_C` | True |
| 467 | `full_validation_candidate_surface` | `9 per month` | `9 per month` | `9 per month` | `C_to_C` | True |
| 531 | `full_validation_candidate_surface` | `12 to 30 per 3 month` | `` | `12 to 30 per 3 month` | `C_to_W` | False |
| 598 | `full_validation_candidate_surface` | `1 per 8 month` | `` | `1 per 8 month` | `C_to_W` | False |
| 659 | `full_validation_candidate_surface` | `2 per 4 day` | `` | `2 per 4 day` | `C_to_W` | False |
| 665 | `full_validation_candidate_surface` | `2 per 2 week` | `2 per 2 week` | `2 per 2 week` | `C_to_C` | True |
| 678 | `full_validation_candidate_surface` | `2 per 4 month` | `2 per 4 month` | `2 per 4 month` | `C_to_C` | True |
| 694 | `full_validation_candidate_surface` | `1 per week` | `1 per week` | `1 per week` | `C_to_C` | True |
| 704 | `full_validation_candidate_surface` | `2 per month` | `2 per month` | `2 per month` | `C_to_C` | True |
| 725 | `full_validation_candidate_surface` | `1 per day` | `multiple per day` | `1 per day` | `C_to_W` | True |
| 731 | `full_validation_candidate_surface` | `1 per day` | `multiple per day` | `1 per day` | `C_to_W` | False |
| 743 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per day` | `multiple per week` | `C_to_C` | True |
| 744 | `full_validation_candidate_surface` | `multiple per week` | `` | `multiple per week` | `C_to_W` | False |
| 763 | `full_validation_candidate_surface` | `1 per week` | `1 per week` | `1 per week` | `C_to_C` | True |
| 790 | `full_validation_candidate_surface` | `1 per 7 to 10 day` | `1 per 7 to 10 day` | `1 per 7 to 10 day` | `C_to_C` | True |
| 816 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 849 | `full_validation_candidate_surface` | `1 per year` | `1 per year` | `1 per year` | `C_to_C` | True |
| 854 | `full_validation_candidate_surface` | `1 per year` | `1 per year` | `1 per year` | `C_to_C` | True |
| 869 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per month` | `multiple per month` | `C_to_C` | True |
| 891 | `full_validation_candidate_surface` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `C_to_C` | True |
| 899 | `full_validation_candidate_surface` | `1 per 2 week` | `1 per 2 week` | `1 per 2 week` | `C_to_C` | True |
| 959 | `full_validation_candidate_surface` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `C_to_C` | True |
| 960 | `full_validation_candidate_surface` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `C_to_C` | True |
| 978 | `full_validation_candidate_surface` | `1 per 2 month` | `` | `1 per 2 month` | `C_to_W` | False |
| 987 | `full_validation_candidate_surface` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `C_to_C` | True |
| 1030 | `full_validation_candidate_surface` | `1 to 3 per month` | `` | `1 to 3 per month` | `C_to_W` | False |
| 1046 | `full_validation_candidate_surface` | `3 to 5 per month` | `` | `3 to 5 per month` | `C_to_W` | False |
| 1070 | `full_validation_candidate_surface` | `3 to 4 per week` | `3 to 4 per week` | `3 to 4 per week` | `C_to_C` | True |
| 1094 | `full_validation_candidate_surface` | `3 to 5 per week` | `3 to 5 per week` | `3 to 5 per week` | `C_to_C` | True |
| 1165 | `full_validation_candidate_surface` | `5 to 7 per 3 week` | `seizure free for multiple year` | `5 to 7 per 3 week` | `C_to_W` | True |
| 1171 | `full_validation_candidate_surface` | `7 to 9 per 3 week` | `7 to 9 per 3 week` | `7 to 9 per 3 week` | `C_to_C` | False |
| 1207 | `full_validation_candidate_surface` | `21 to 28 per 3 month` | `7 to 9 per month` | `21 to 28 per 3 month` | `C_to_C` | True |
| 1223 | `full_validation_candidate_surface` | `3 to 4 per week` | `` | `3 to 4 per week` | `C_to_W` | False |
| 1249 | `full_validation_candidate_surface` | `2 to 4 per week` | `2 to 4 per week` | `2 to 4 per week` | `C_to_C` | True |
| 1281 | `full_validation_candidate_surface` | `5 to 7 per year` | `` | `5 to 7 per year` | `C_to_W` | False |
| 1317 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown, multiple per cluster` | `C_to_C` | False |
| 1357 | `full_validation_candidate_surface` | `1 per day` | `no seizure frequency reference` | `1 per day` | `C_to_W` | True |
| 1363 | `full_validation_candidate_surface` | `3 per day` | `` | `3 per day` | `C_to_W` | False |
| 1413 | `full_validation_candidate_surface` | `9 per month` | `9 per month` | `9 per month` | `C_to_C` | True |
| 1454 | `full_validation_candidate_surface` | `7 per week` | `` | `7 per week` | `C_to_W` | False |
| 1486 | `full_validation_candidate_surface` | `3 per month` | `` | `3 per month` | `C_to_W` | False |
| 1573 | `full_validation_candidate_surface` | `11 per week` | `` | `11 per week` | `C_to_W` | False |
| 1591 | `full_validation_candidate_surface` | `11 per month` | `` | `11 per month` | `C_to_W` | False |
| 1596 | `full_validation_candidate_surface` | `12 per week` | `12 per week` | `12 per week` | `C_to_C` | True |
| 1597 | `full_validation_candidate_surface` | `12 per month` | `` | `12 per month` | `C_to_W` | False |
| 1636 | `full_validation_candidate_surface` | `5 per month` | `` | `5 per month` | `C_to_W` | False |
| 1640 | `full_validation_candidate_surface` | `2-5 per week` | `` | `5 per week` | `C_to_W` | False |
| 1687 | `full_validation_candidate_surface` | `multiple per week` | `multiple per day` | `multiple per week` | `C_to_C` | True |
| 1694 | `full_validation_candidate_surface` | `1 cluster per 2 week, 3 per cluster` | `3 per 2 week` | `1 cluster per 2 week, 3 per cluster` | `C_to_C` | True |
| 1695 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `multiple per month` | `C_to_C` | True |
| 1706 | `full_validation_candidate_surface` | `multiple cluster per month, multiple per cluster` | `multiple cluster per month, multiple per cluster` | `multiple cluster per month, multiple per cluster` | `C_to_C` | True |
| 1707 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per day` | `multiple per week` | `C_to_C` | True |
| 1772 | `full_validation_candidate_surface` | `11 per 6 month` | `11 per 6 month` | `11 per 6 month` | `C_to_C` | True |
| 1773 | `full_validation_candidate_surface` | `11 per 3 month` | `11 per 3 month` | `11 per 3 month` | `C_to_C` | True |
| 1790 | `full_validation_candidate_surface` | `8 per 4 month` | `8 per 4 month` | `8 per 4 month` | `C_to_C` | True |
| 1794 | `full_validation_candidate_surface` | `8 per 2 month` | `8 per 2 month` | `8 per 2 month` | `C_to_C` | True |
| 1866 | `full_validation_candidate_surface` | `8 per 2 month` | `8 per 2 month` | `8 per 2 month` | `C_to_C` | True |
| 1880 | `full_validation_candidate_surface` | `8 per 2 month` | `multiple per week` | `8 per 2 month` | `C_to_W` | True |
| 1887 | `full_validation_candidate_surface` | `4 per 3 month` | `4 per 3 month` | `4 per 3 month` | `C_to_C` | True |
| 1914 | `full_validation_candidate_surface` | `7 per 3 month` | `7 per 3 month` | `7 per 3 month` | `C_to_C` | True |
| 1922 | `full_validation_candidate_surface` | `7 per 3 month` | `7 per 3 month` | `7 per 3 month` | `C_to_C` | True |
| 1923 | `full_validation_candidate_surface` | `7 per 6 month` | `7 per 6 month` | `7 per 6 month` | `C_to_C` | True |
| 1979 | `full_validation_candidate_surface` | `6 per 2 month` | `3 per 2 month` | `6 per 2 month` | `C_to_C` | True |
| 1980 | `full_validation_candidate_surface` | `6 per 3 month` | `6 per 3 month` | `6 per 3 month` | `C_to_C` | True |
| 2023 | `full_validation_candidate_surface` | `5 per month` | `` | `5 per month` | `C_to_W` | False |
| 2080 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per day` | `multiple per month` | `C_to_C` | True |
| 2094 | `full_validation_candidate_surface` | `multiple per month` | `multiple per day` | `multiple per month` | `C_to_C` | True |
| 2114 | `full_validation_candidate_surface` | `multiple per month` | `multiple per month` | `multiple per month` | `C_to_C` | True |
| 2149 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 2166 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per day` | `unknown` | `C_to_C` | True |
| 2228 | `full_validation_candidate_surface` | `3 to 5 per 2 week` | `3 to 5 per 2 week` | `3 to 5 per 2 week` | `C_to_C` | True |
| 2233 | `full_validation_candidate_surface` | `6 to 7 per 2 month` | `` | `6 to 7 per 2 month` | `C_to_W` | False |
| 2245 | `full_validation_candidate_surface` | `7 to 8 per 3 week` | `7 to 8 per 3 week` | `7 to 8 per 3 week` | `C_to_C` | True |
| 2259 | `full_validation_candidate_surface` | `6 to 8 per 3 month` | `6 to 8 per 3 month` | `6 to 8 per 3 month` | `C_to_C` | True |
| 2354 | `full_validation_candidate_surface` | `6 to 7 per week` | `6 to 7 per week` | `6 to 7 per week` | `C_to_C` | True |
| 2366 | `full_validation_candidate_surface` | `2 to 4 per year` | `` | `2 to 4 per year` | `C_to_W` | False |
| 2369 | `full_validation_candidate_surface` | `3 to 4 per month` | `3 to 4 per month` | `3 to 4 per month` | `C_to_C` | True |
| 2374 | `full_validation_candidate_surface` | `7 to 9 per month` | `` | `7 to 9 per month` | `C_to_W` | False |
| 2425 | `full_validation_candidate_surface` | `6 to 8 per month` | `` | `6 to 8 per month` | `C_to_W` | False |
| 2427 | `full_validation_candidate_surface` | `3 to 5 per month` | `` | `3 to 5 per month` | `C_to_W` | False |
| 2435 | `full_validation_candidate_surface` | `5 to 7 per 2 week` | `5 to 7 per 2 week` | `5 to 7 per 2 week` | `C_to_C` | True |
| 2437 | `full_validation_candidate_surface` | `2 to 3 per 2 month` | `2 to 3 per 2 month` | `2 to 3 per 2 month` | `C_to_C` | True |
| 2440 | `full_validation_candidate_surface` | `5 to 7 per 2 month` | `5 to 7 per 2 month` | `5 to 7 per 2 month` | `C_to_C` | True |
| 2456 | `full_validation_candidate_surface` | `6 to 7 per 2 week` | `6 to 7 per 2 week` | `6 to 7 per 2 week` | `C_to_C` | True |
| 2459 | `full_validation_candidate_surface` | `7 to 9 per 2 week` | `7 to 9 per 2 week` | `7 to 9 per 2 week` | `C_to_C` | True |
| 2487 | `full_validation_candidate_surface` | `2 to 3 per 3 month` | `2 to 3 per 3 month` | `2 to 3 per 3 month` | `C_to_C` | True |
| 2513 | `full_validation_candidate_surface` | `2 to 3 per 2 week` | `` | `2 to 3 per 2 week` | `C_to_W` | False |
| 2541 | `full_validation_candidate_surface` | `8 to 9 per 2 week` | `8 to 9 per 2 week` | `8 to 9 per 2 week` | `C_to_C` | True |
| 2548 | `full_validation_candidate_surface` | `5 to 6 per 2 month` | `5 to 6 per 2 month` | `5 to 6 per 2 month` | `C_to_C` | True |
| 2554 | `full_validation_candidate_surface` | `1 to 10 per 2 month` | `1 to 10 per 2 month` | `1 to 10 per 2 month` | `C_to_C` | True |
| 2558 | `full_validation_candidate_surface` | `3 to 4 per 2 month` | `3 to 4 per 2 month` | `3 to 4 per 2 month` | `C_to_C` | True |
| 2609 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 2622 | `full_validation_candidate_surface` | `1 per day` | `` | `1 per day` | `C_to_W` | False |
| 2628 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 2678 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 2681 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 2698 | `full_validation_candidate_surface` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `C_to_C` | True |
| 2731 | `full_validation_candidate_surface` | `1 per 2 week` | `1 per 2 week` | `1 per 2 week` | `C_to_C` | True |
| 2740 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 2748 | `full_validation_candidate_surface` | `1 per month` | `` | `1 per month` | `C_to_W` | False |
| 2759 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | False |
| 2762 | `full_validation_candidate_surface` | `1 per month` | `` | `1 per month` | `C_to_W` | False |
| 2765 | `full_validation_candidate_surface` | `1 per month` | `` | `1 per month` | `C_to_W` | False |
| 2776 | `full_validation_candidate_surface` | `1 per week` | `1 per week` | `1 per week` | `C_to_C` | True |
| 2789 | `full_validation_candidate_surface` | `1 per week` | `1 per week` | `1 per week` | `C_to_C` | True |
| 2812 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 2822 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 2824 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 2877 | `full_validation_candidate_surface` | `2 per year` | `2 per year` | `2 per year` | `C_to_C` | True |
| 2887 | `full_validation_candidate_surface` | `2 per week` | `2 per week` | `2 per week` | `C_to_C` | True |
| 2907 | `full_validation_candidate_surface` | `seizure free for 6 month` | `seizure free for 6 month` | `seizure free for 6 month` | `C_to_C` | True |
| 2932 | `full_validation_candidate_surface` | `seizure free for 9 month` | `` | `seizure free for 9 month` | `C_to_W` | False |
| 2938 | `full_validation_candidate_surface` | `seizure free for 8 month` | `seizure free for 8 month` | `seizure free for 8 month` | `C_to_C` | True |
| 2965 | `full_validation_candidate_surface` | `seizure free for 16 month` | `` | `seizure free for 16 month` | `C_to_W` | False |
| 2992 | `full_validation_candidate_surface` | `seizure free for 7 month` | `seizure free for 7 month` | `seizure free for 7 month` | `C_to_C` | False |
| 3015 | `full_validation_candidate_surface` | `seizure free for 12 month` | `` | `seizure free for 12 month` | `C_to_W` | False |
| 3048 | `full_validation_candidate_surface` | `seizure free for 16 month` | `` | `seizure free for 16 month` | `C_to_W` | False |
| 3058 | `full_validation_candidate_surface` | `seizure free for 12 month` | `seizure free for 12 month` | `seizure free for 12 month` | `C_to_C` | True |
| 3082 | `full_validation_candidate_surface` | `seizure free for 10 month` | `seizure free for 10 month` | `seizure free for 10 month` | `C_to_C` | True |
| 3095 | `full_validation_candidate_surface` | `seizure free for 12 month` | `seizure free for 12 month` | `seizure free for 12 month` | `C_to_C` | True |
| 3113 | `full_validation_candidate_surface` | `seizure free for 14 month` | `` | `seizure free for 14 month` | `C_to_W` | False |
| 3118 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 12 month` | `seizure free for multiple month` | `C_to_C` | True |
| 3137 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 3224 | `full_validation_candidate_surface` | `1 cluster per month, 6 to 7 per cluster` | `1 cluster per month, 6 to 7 per cluster` | `1 cluster per month, 6 to 7 per cluster` | `C_to_C` | True |
| 3242 | `full_validation_candidate_surface` | `2 cluster per month, 5 per cluster` | `2 cluster per month, 5 per cluster` | `2 cluster per month, 5 per cluster` | `C_to_C` | True |
| 3261 | `full_validation_candidate_surface` | `2 cluster per month, 4 per cluster` | `2 cluster per month, 4 per cluster` | `2 cluster per month, 4 per cluster` | `C_to_C` | True |
| 3262 | `full_validation_candidate_surface` | `5 per 4 week` | `` | `2 cluster per month, 5 per cluster` | `C_to_W` | False |
| 3281 | `full_validation_candidate_surface` | `8 per month` | `` | `8 per month` | `C_to_W` | False |
| 3297 | `full_validation_candidate_surface` | `6 per month` | `` | `6 per month` | `C_to_W` | False |
| 3325 | `full_validation_candidate_surface` | `3 per week` | `` | `3 per week` | `C_to_W` | False |
| 3356 | `full_validation_candidate_surface` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` | True |
| 3371 | `full_validation_candidate_surface` | `unknown` | `` | `unknown` | `C_to_W` | False |
| 3436 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 3468 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `unknown` | `C_to_C` | True |
| 3469 | `full_validation_candidate_surface` | `unknown` | `` | `unknown` | `C_to_W` | False |
| 3482 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 3493 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 3507 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 3512 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 3528 | `full_validation_candidate_surface` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` | True |
| 3532 | `full_validation_candidate_surface` | `no seizure frequency reference` | `1 per day` | `unknown` | `C_to_W` | True |
| 3534 | `full_validation_candidate_surface` | `unknown` | `seizure free for 7 month` | `unknown` | `C_to_W` | True |
| 3600 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 3623 | `full_validation_candidate_surface` | `7 per week` | `7 per week` | `7 per week` | `C_to_C` | True |
| 3643 | `full_validation_candidate_surface` | `7 per week` | `` | `7 per week` | `C_to_W` | False |
| 3681 | `full_validation_candidate_surface` | `9 per month` | `` | `9 per month` | `C_to_W` | False |
| 3682 | `full_validation_candidate_surface` | `6 per month` | `` | `6 per month` | `C_to_W` | False |
| 3710 | `full_validation_candidate_surface` | `5 per week` | `5 per week` | `5 per week` | `C_to_C` | True |
| 3753 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 3766 | `full_validation_candidate_surface` | `8 per year` | `` | `8 per year` | `C_to_W` | False |
| 3774 | `full_validation_candidate_surface` | `9 per year` | `2 per 3 month` | `9 per year` | `C_to_C` | True |
| 3791 | `full_validation_candidate_surface` | `10 per year` | `` | `10 per year` | `C_to_W` | False |
| 3801 | `full_validation_candidate_surface` | `9 per month` | `9 per month` | `9 per month` | `C_to_C` | True |
| 3806 | `full_validation_candidate_surface` | `6 per month` | `6 per month` | `6 per month` | `C_to_C` | True |
| 3827 | `full_validation_candidate_surface` | `7 per month` | `7 per month` | `7 per month` | `C_to_C` | True |
| 3846 | `full_validation_candidate_surface` | `2 per day` | `` | `2 per day` | `C_to_W` | False |
| 3849 | `full_validation_candidate_surface` | `3 per day` | `` | `3 per day` | `C_to_W` | False |
| 3889 | `full_validation_candidate_surface` | `8 per year` | `` | `8 per year` | `C_to_W` | False |
| 3892 | `full_validation_candidate_surface` | `3 per year` | `3 per year` | `3 per year` | `C_to_C` | True |
| 3940 | `full_validation_candidate_surface` | `4 per week` | `4 per week` | `4 per week` | `C_to_C` | True |
| 3949 | `full_validation_candidate_surface` | `4 per week` | `4 per week` | `4 per week` | `C_to_C` | True |
| 3988 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 3995 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 3999 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 4022 | `full_validation_candidate_surface` | `8 per month` | `8 per month` | `8 per month` | `C_to_C` | True |
| 4026 | `full_validation_candidate_surface` | `1 per month` | `` | `1 per month` | `C_to_W` | False |
| 4092 | `full_validation_candidate_surface` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `C_to_C` | True |
| 4100 | `full_validation_candidate_surface` | `1 per 2 to 3 week` | `` | `1 per 2 to 3 week` | `C_to_W` | False |
| 4110 | `full_validation_candidate_surface` | `1 per 1 to 2 day` | `1 per 1 to 2 day` | `1 per 1 to 2 day` | `C_to_C` | True |
| 4116 | `full_validation_candidate_surface` | `1 per 1 to 2 day` | `1 per 1 to 2 day` | `1 per 1 to 2 day` | `C_to_C` | True |
| 4173 | `full_validation_candidate_surface` | `1 per 2 week` | `2 per month` | `1 per 2 week` | `C_to_C` | True |
| 4243 | `full_validation_candidate_surface` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `C_to_C` | True |
| 4258 | `full_validation_candidate_surface` | `4 per week` | `4 per week` | `4 per week` | `C_to_C` | False |
| 4337 | `full_validation_candidate_surface` | `3 per 3 month` | `3 per 4 month` | `3 per 3 month` | `C_to_W` | True |
| 4345 | `full_validation_candidate_surface` | `4 per month` | `` | `4 per month` | `C_to_W` | False |
| 4368 | `full_validation_candidate_surface` | `5 per 2 month` | `` | `5 per 2 month` | `C_to_W` | False |
| 4402 | `full_validation_candidate_surface` | `7 per 7 month` | `` | `7 per 7 month` | `C_to_W` | False |
| 4410 | `full_validation_candidate_surface` | `4 per 7 month` | `` | `4 per 7 month` | `C_to_W` | False |
| 4478 | `full_validation_candidate_surface` | `19 per week` | `` | `19 per week` | `C_to_W` | False |
| 4480 | `full_validation_candidate_surface` | `3 to 5 per week` | `` | `3 to 5 per week` | `C_to_W` | False |
| 4496 | `full_validation_candidate_surface` | `7 to 8 per 3 month` | `7 to 8 per 3 month` | `7 to 8 per 3 month` | `C_to_C` | True |
| 4562 | `full_validation_candidate_surface` | `1 per 6 week` | `1 per 6 week` | `1 per 6 week` | `C_to_C` | True |
| 4563 | `full_validation_candidate_surface` | `1 per 4 month` | `1 per 4 month` | `1 per 4 month` | `C_to_C` | True |
| 4574 | `full_validation_candidate_surface` | `1 per 4 week` | `` | `1 per 4 week` | `C_to_W` | False |
| 4592 | `full_validation_candidate_surface` | `1 per 2 month` | `1 per 2 month` | `1 per 2 month` | `C_to_C` | True |
| 4597 | `full_validation_candidate_surface` | `1 per 3 week` | `1 per 3 week` | `1 per 3 week` | `C_to_C` | True |
| 4624 | `full_validation_candidate_surface` | `1 per 3 to 4 day` | `multiple per week` | `1 per 3 to 4 day` | `C_to_W` | True |
| 4631 | `full_validation_candidate_surface` | `1 per 14 to 21 day` | `1 per 2 to 3 week` | `1 per 14 to 21 day` | `C_to_C` | True |
| 4690 | `full_validation_candidate_surface` | `unknown` | `` | `multiple per day` | `C_to_W` | False |
| 4694 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `multiple per day` | `C_to_C` | True |
| 4700 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `multiple per day` | `C_to_C` | True |
| 4709 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `multiple per day` | `C_to_W` | False |
| 4731 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 4732 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 4771 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per month` | `unknown` | `C_to_C` | True |
| 4839 | `full_validation_candidate_surface` | `seizure free for 4 month` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 4842 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 4910 | `full_validation_candidate_surface` | `seizure free for 2 year` | `` | `seizure free for 2 year` | `C_to_W` | False |
| 4919 | `full_validation_candidate_surface` | `seizure free for 2 year` | `` | `seizure free for 2 year` | `C_to_W` | False |
| 4926 | `full_validation_candidate_surface` | `seizure free for 1 year` | `` | `seizure free for 1 year` | `C_to_W` | False |
| 4951 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple month` | `C_to_W` | False |
| 4956 | `full_validation_candidate_surface` | `seizure free for 7 month` | `seizure free for 7 month` | `seizure free for 7 month` | `C_to_C` | True |
| 4992 | `full_validation_candidate_surface` | `seizure free for 11 month` | `seizure free for 11 month` | `seizure free for 11 month` | `C_to_C` | True |
| 4994 | `full_validation_candidate_surface` | `seizure free for 6 month` | `seizure free for 6 month` | `seizure free for 6 month` | `C_to_C` | True |
| 5040 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 6 month` | `seizure free for 6 months` | `C_to_C` | True |
| 5082 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | False |
| 5092 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 5110 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for multiple month` | `C_to_C` | True |
| 5121 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 5136 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for multiple month` | `C_to_C` | True |
| 5141 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 5197 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 5210 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 5221 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 5248 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `C_to_C` | True |
| 5331 | `full_validation_candidate_surface` | `seizure free for 12 month` | `` | `seizure free for 12 month` | `C_to_W` | False |
| 5345 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 5351 | `full_validation_candidate_surface` | `seizure free for 18 month` | `seizure free for multiple year` | `seizure free for 18 month` | `C_to_C` | True |
| 5379 | `full_validation_candidate_surface` | `seizure free for 6 month` | `seizure free for 6 month` | `seizure free for multiple month` | `C_to_C` | True |
| 5406 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 2 month` | `seizure free for multiple month` | `C_to_C` | True |
| 5476 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `unknown` | `C_to_C` | True |
| 5490 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | False |
| 5491 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 5504 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 5507 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 5528 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 5534 | `full_validation_candidate_surface` | `seizure free for multiple year` | `1 per multiple month` | `1 per multiple month` | `W_to_C` | True |
| 5551 | `full_validation_candidate_surface` | `multiple per day` | `multiple per day` | `multiple per day` | `C_to_C` | True |
| 5567 | `full_validation_candidate_surface` | `multiple per week` | `` | `multiple per week` | `C_to_W` | False |
| 5584 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 5624 | `full_validation_candidate_surface` | `1 per 10 day` | `1 per 10 day` | `1 per 10 day` | `C_to_C` | True |
| 5652 | `full_validation_candidate_surface` | `1 per 8 day` | `1 per 8 day` | `1 per 8 day` | `C_to_C` | True |
| 5682 | `full_validation_candidate_surface` | `2 to 4 per month` | `` | `2 to 4 per month` | `C_to_W` | False |
| 5696 | `full_validation_candidate_surface` | `3 per 4 month` | `no seizure frequency reference` | `3 per 4 month` | `C_to_W` | True |
| 5763 | `full_validation_candidate_surface` | `6 per 3 month` | `2 per 3 month` | `2 per month` | `C_to_W` | True |
| 5767 | `full_validation_candidate_surface` | `1 per 1 to 2 week` | `2 per month` | `1 per 1 to 2 week` | `C_to_C` | True |
| 5791 | `full_validation_candidate_surface` | `3 per 3 month` | `no seizure frequency reference` | `1 per month` | `C_to_W` | True |
| 5827 | `full_validation_candidate_surface` | `multiple per week` | `multiple per day` | `multiple per week` | `C_to_C` | True |
| 5837 | `full_validation_candidate_surface` | `2 cluster per 3 week, multiple per cluster` | `multiple per week` | `2 cluster per 3 week, multiple per cluster` | `C_to_W` | True |
| 5866 | `full_validation_candidate_surface` | `4 per 6 week` | `no seizure frequency reference` | `4 per 6 week` | `C_to_W` | True |
| 5873 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 5921 | `full_validation_candidate_surface` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `C_to_C` | True |
| 5954 | `full_validation_candidate_surface` | `2 per week` | `` | `2 per week` | `C_to_W` | False |
| 5961 | `full_validation_candidate_surface` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `C_to_C` | True |
| 5974 | `full_validation_candidate_surface` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` | True |
| 5977 | `full_validation_candidate_surface` | `multiple per 6 week` | `multiple per 6 week` | `unknown` | `C_to_C` | True |
| 5995 | `full_validation_candidate_surface` | `3 per 9 month` | `1 per month` | `1 per 3 months` | `C_to_W` | True |
| 5996 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 6026 | `full_validation_candidate_surface` | `3 per 2 month` | `3 per 2 month` | `3 per 2 month` | `C_to_C` | True |
| 6029 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 6034 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 6065 | `full_validation_candidate_surface` | `5 per month` | `3 to 5 per month` | `5 per month` | `C_to_W` | True |
| 6077 | `full_validation_candidate_surface` | `seizure free for 8 month` | `no seizure frequency reference` | `unknown` | `W_to_C` | False |
| 6087 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per day` | `unknown` | `C_to_C` | True |
| 6094 | `full_validation_candidate_surface` | `3 per week` | `no seizure frequency reference` | `3 per month` | `W_to_W` | True |
| 6112 | `full_validation_candidate_surface` | `3 to 5 per month` | `3 to 5 per month` | `3 to 5 per month` | `C_to_C` | True |
| 6131 | `full_validation_candidate_surface` | `seizure free for 6 month` | `unknown` | `unknown` | `W_to_C` | True |
| 6137 | `full_validation_candidate_surface` | `1 per 2 to 3 week` | `` | `1 per 2 week` | `C_to_W` | False |
| 6153 | `full_validation_candidate_surface` | `1 per 1 to 2 week` | `9 per 4 week` | `9 per month` | `W_to_C` | True |
| 6180 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 6192 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 6204 | `full_validation_candidate_surface` | `1 per 3 to 4 week` | `1 per 3 to 4 week` | `2 per month` | `C_to_C` | True |
| 6209 | `full_validation_candidate_surface` | `1 per day` | `multiple per day` | `multiple per day` | `W_to_C` | True |
| 6244 | `full_validation_candidate_surface` | `unknown` | `2 per week` | `unknown` | `C_to_W` | True |
| 6251 | `full_validation_candidate_surface` | `1 per 1 to 2 month` | `1 per 3 month` | `1 per 1 to 2 month` | `C_to_C` | False |
| 6273 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 6319 | `full_validation_candidate_surface` | `1 per week` | `1 per week` | `1 per week` | `C_to_C` | True |
| 6321 | `full_validation_candidate_surface` | `unknown` | `no seizure frequency reference` | `unknown` | `C_to_C` | True |
| 6331 | `full_validation_candidate_surface` | `2 per 6 week` | `2 per 6 week` | `2 per 6 weeks` | `C_to_C` | True |
| 6358 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 4 month` | `seizure free for 15 to 16 months` | `C_to_C` | True |
| 6368 | `full_validation_candidate_surface` | `1 per 1 to 2 week` | `multiple per day` | `unknown` | `W_to_C` | True |
| 6395 | `full_validation_candidate_surface` | `1 to 2 per month` | `1 to 2 per month` | `1 to 2 per month` | `C_to_C` | True |
| 6501 | `full_validation_candidate_surface` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` | True |
| 6509 | `full_validation_candidate_surface` | `2 per 2 week` | `multiple per day` | `1 per week` | `C_to_W` | True |
| 6571 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | `W_to_W` | True |
| 6607 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 6684 | `full_validation_candidate_surface` | `3 per 4 month` | `3 per 4 month` | `3 per 4 month` | `C_to_C` | True |
| 6701 | `full_validation_candidate_surface` | `4 per 3 week` | `no seizure frequency reference` | `4 per 3 week` | `C_to_W` | True |
| 6738 | `full_validation_candidate_surface` | `1 per 6 to 8 week` | `` | `1 per 6 to 8 week` | `C_to_W` | False |
| 6852 | `full_validation_candidate_surface` | `4 to 6 per month` | `` | `4 to 6 per month` | `C_to_W` | False |
| 6889 | `full_validation_candidate_surface` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `multiple per week` | `W_to_W` | True |
| 6952 | `full_validation_candidate_surface` | `2 per week` | `2 per week` | `2 per week` | `C_to_C` | True |
| 6967 | `full_validation_candidate_surface` | `unknown` | `` | `unknown` | `C_to_W` | False |
| 6987 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 7093 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 7126 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 7141 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 7167 | `full_validation_candidate_surface` | `3 cluster per 6 week, 2 to 4 per cluster` | `unknown` | `1 cluster per 2 weeks, 2 to 4 per cluster` | `C_to_W` | True |
| 7168 | `full_validation_candidate_surface` | `2 per year` | `2 per year` | `unknown` | `W_to_W` | True |
| 7192 | `full_validation_candidate_surface` | `multiple per week` | `unknown` | `multiple per week` | `C_to_C` | True |
| 7195 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 7196 | `full_validation_candidate_surface` | `6 per 6 week` | `no seizure frequency reference` | `1 per week` | `C_to_W` | True |
| 7198 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 7275 | `full_validation_candidate_surface` | `3 per 3 month` | `` | `1 per month` | `C_to_W` | False |
| 7290 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 7316 | `full_validation_candidate_surface` | `1 to 2 per month` | `1 to 2 per month` | `1 to 2 per month` | `C_to_C` | True |
| 7389 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 7392 | `full_validation_candidate_surface` | `2 to 4 per week` | `2 to 4 per week` | `2 to 4 per week` | `C_to_C` | True |
| 7401 | `full_validation_candidate_surface` | `2 cluster per 6 week, 1 to 2 per cluster` | `2 cluster per 6 week, 1 to 2 per cluster` | `2 cluster per 6 week, 1 to 2 per cluster` | `C_to_C` | True |
| 7409 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per week` | `unknown` | `C_to_C` | True |
| 7455 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per day` | `unknown` | `C_to_C` | True |
| 7475 | `full_validation_candidate_surface` | `2 per 6 month` | `2 per 2 month` | `2 per 6 month` | `C_to_W` | True |
| 7491 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | False |
| 7506 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 7573 | `full_validation_candidate_surface` | `1 per 2 week` | `2 per month` | `1 per 2 week` | `C_to_C` | True |
| 7581 | `full_validation_candidate_surface` | `2 to 3 per week` | `2 to 3 per week` | `2 to 3 per week` | `C_to_C` | True |
| 7615 | `full_validation_candidate_surface` | `2 per year` | `` | `3 to 7 per month` | `W_to_W` | False |
| 7650 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 7738 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 6 month` | `seizure free for multiple month` | `C_to_C` | True |
| 7785 | `full_validation_candidate_surface` | `seizure free for 12 month` | `` | `seizure free for 12 month` | `C_to_W` | False |
| 7818 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for 2 years` | `C_to_C` | True |
| 7834 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | False |
| 7859 | `full_validation_candidate_surface` | `no seizure frequency reference` | `seizure free for multiple year` | `unknown` | `C_to_W` | True |
| 7872 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 7911 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 7961 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple year` | `C_to_W` | False |
| 8002 | `full_validation_candidate_surface` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | `C_to_C` | True |
| 8006 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 6 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8079 | `full_validation_candidate_surface` | `seizure free for 18 month` | `` | `seizure free for 18 month` | `C_to_W` | False |
| 8089 | `full_validation_candidate_surface` | `seizure free for 16 month` | `seizure free for multiple year` | `seizure free for 16 month` | `C_to_C` | True |
| 8124 | `full_validation_candidate_surface` | `seizure free for 13 month` | `seizure free for 13 month` | `seizure free for 13 month` | `C_to_C` | True |
| 8144 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple month` | `C_to_W` | False |
| 8145 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 6 month` | `C_to_W` | False |
| 8160 | `full_validation_candidate_surface` | `seizure free for multiple year` | `1 per multiple week` | `seizure free for multiple month` | `C_to_W` | True |
| 8180 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 6 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8188 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 8203 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 8224 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8235 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 8264 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 4 month` | `seizure free for 4 month` | `C_to_C` | False |
| 8265 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 6 month` | `C_to_W` | False |
| 8354 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8355 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `C_to_C` | True |
| 8400 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 8419 | `full_validation_candidate_surface` | `2 per week` | `multiple per week` | `1 to 2 per week` | `C_to_W` | True |
| 8474 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 8512 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8564 | `full_validation_candidate_surface` | `seizure free for 6 month` | `` | `seizure free for 6 month` | `C_to_W` | False |
| 8577 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple month` | `C_to_W` | False |
| 8581 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple month` | `C_to_W` | False |
| 8593 | `full_validation_candidate_surface` | `seizure free for 14 month` | `seizure free for 14 month` | `seizure free for 14 month` | `C_to_C` | True |
| 8596 | `full_validation_candidate_surface` | `seizure free for 11 month` | `` | `seizure free for 11 month` | `C_to_W` | False |
| 8674 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 8724 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8730 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 6 month` | `seizure free for 6 month` | `C_to_C` | True |
| 8794 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 6 month` | `C_to_W` | False |
| 8802 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 12 month` | `C_to_W` | False |
| 8805 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 6 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8808 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 10 month` | `C_to_W` | False |
| 8820 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 7 month` | `C_to_W` | False |
| 8835 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 10 month` | `C_to_W` | False |
| 8854 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple month` | `C_to_W` | False |
| 8893 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 4 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8922 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8924 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 5 month` | `seizure free for multiple month` | `C_to_C` | True |
| 8938 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for 10 month` | `C_to_C` | True |
| 8949 | `full_validation_candidate_surface` | `seizure free for 6 month` | `seizure free for 6 month` | `seizure free for 6 month` | `C_to_C` | True |
| 8969 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 9002 | `full_validation_candidate_surface` | `7 per year` | `` | `7 per year` | `C_to_W` | False |
| 9063 | `full_validation_candidate_surface` | `seizure free for 8 month` | `seizure free for 8 month` | `seizure free for 8 month` | `C_to_C` | True |
| 9103 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per day` | `unknown` | `C_to_C` | True |
| 9163 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | False |
| 9190 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 9215 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 9238 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple month` | `C_to_C` | True |
| 9250 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 9 month` | `seizure free for multiple month` | `C_to_C` | True |
| 9259 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 1 year` | `seizure free for 1 year` | `C_to_C` | True |
| 9287 | `full_validation_candidate_surface` | `3 to 5 per week` | `` | `3 to 5 per week` | `C_to_W` | False |
| 9299 | `full_validation_candidate_surface` | `5 per week` | `` | `5 per week` | `C_to_W` | False |
| 9300 | `full_validation_candidate_surface` | `2 to 4 per week` | `2 to 4 per week` | `2 to 4 per week` | `C_to_C` | True |
| 9344 | `full_validation_candidate_surface` | `multiple per day` | `multiple per day` | `multiple per day` | `C_to_C` | True |
| 9365 | `full_validation_candidate_surface` | `1 per 2 day` | `` | `1 per 2 day` | `C_to_W` | False |
| 9368 | `full_validation_candidate_surface` | `1 per 2 day` | `` | `1 per 2 day` | `C_to_W` | False |
| 9391 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 9397 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 9449 | `full_validation_candidate_surface` | `4 per 6 month` | `` | `4 per 6 month` | `C_to_W` | False |
| 9462 | `full_validation_candidate_surface` | `7 per 11 month` | `7 per 11 month` | `7 per 11 month` | `C_to_C` | True |
| 9496 | `full_validation_candidate_surface` | `2 per week` | `4 per 7 month` | `6 per 12 month` | `W_to_C` | True |
| 9547 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 9588 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 7 to 8 month` | `seizure free for multiple month` | `C_to_C` | True |
| 9704 | `full_validation_candidate_surface` | `unknown` | `` | `unknown` | `C_to_W` | False |
| 9815 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `multiple per day` | `C_to_C` | True |
| 9877 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 9879 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 9888 | `full_validation_candidate_surface` | `seizure free for multiple year` | `no seizure frequency reference` | `unknown` | `W_to_C` | True |
| 9912 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `unknown` | `C_to_C` | True |
| 9937 | `full_validation_candidate_surface` | `1 per multiple week` | `unknown` | `1 cluster per month, multiple per cluster` | `W_to_W` | True |
| 9943 | `full_validation_candidate_surface` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `1 cluster per 4 to 5 week, multiple per cluster` | `W_to_W` | True |
| 9955 | `full_validation_candidate_surface` | `1 per month` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `W_to_C` | True |
| 10003 | `full_validation_candidate_surface` | `1 cluster per week, multiple per cluster` | `1 cluster per week, multiple per cluster` | `1 cluster per week, multiple per cluster` | `C_to_C` | True |
| 10047 | `full_validation_candidate_surface` | `2 cluster per 3 month, multiple per cluster` | `2 cluster per 3 month, multiple per cluster` | `2 cluster per 3 month, multiple per cluster` | `C_to_C` | True |
| 10063 | `full_validation_candidate_surface` | `3 cluster per 3 month, multiple per cluster` | `` | `3 cluster per 3 month, multiple per cluster` | `C_to_W` | False |
| 10097 | `full_validation_candidate_surface` | `3 cluster per month, multiple per cluster` | `` | `3 cluster per month, multiple per cluster` | `C_to_W` | False |
| 10147 | `full_validation_candidate_surface` | `unknown` | `no seizure frequency reference` | `unknown` | `C_to_C` | True |
| 10183 | `full_validation_candidate_surface` | `unknown` | `` | `unknown` | `C_to_W` | False |
| 10189 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown, 3 to 4 per cluster` | `C_to_C` | True |
| 10200 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown, 2 to 4 per cluster` | `C_to_C` | True |
| 10237 | `full_validation_candidate_surface` | `4 cluster per month, multiple per cluster` | `unknown` | `4 cluster per month, multiple per cluster` | `C_to_W` | True |
| 10245 | `full_validation_candidate_surface` | `3 cluster per month, multiple per cluster` | `unknown` | `3 cluster per month, multiple per cluster` | `C_to_W` | True |
| 10260 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 10264 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 10266 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 10268 | `full_validation_candidate_surface` | `unknown` | `` | `unknown` | `C_to_W` | False |
| 10371 | `full_validation_candidate_surface` | `seizure free for 25 month` | `seizure free for multiple year` | `seizure free for multiple year` | `C_to_C` | True |
| 10383 | `full_validation_candidate_surface` | `1 cluster per week, 5 per cluster` | `1 cluster per week, 5 per cluster` | `1 cluster per week, 5 per cluster` | `C_to_C` | True |
| 10386 | `full_validation_candidate_surface` | `1 cluster per week, 2 to 3 per cluster` | `` | `1 cluster per week, 2 to 3 per cluster` | `C_to_W` | False |
| 10434 | `full_validation_candidate_surface` | `multiple cluster per week, 2 to 3 per cluster` | `2 to 3 per day` | `multiple cluster per week, 2 to 3 per cluster` | `C_to_W` | False |
| 10481 | `full_validation_candidate_surface` | `4 cluster per month, multiple per cluster` | `4 cluster per month, multiple per cluster` | `4 cluster per month, multiple per cluster` | `C_to_C` | True |
| 10487 | `full_validation_candidate_surface` | `4 cluster per month, multiple per cluster` | `4 cluster per month, multiple per cluster` | `4 cluster per month, multiple per cluster` | `C_to_C` | True |
| 10509 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 10517 | `full_validation_candidate_surface` | `3 to 4 cluster per week, multiple per cluster` | `3 to 4 cluster per week, multiple per cluster` | `3 to 4 cluster per week, multiple per cluster` | `C_to_C` | True |
| 10542 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown, 2 to 4 per cluster` | `C_to_C` | True |
| 10578 | `full_validation_candidate_surface` | `unknown, 3 to 4 per cluster` | `` | `unknown, 3 to 4 per cluster` | `C_to_W` | False |
| 10583 | `full_validation_candidate_surface` | `unknown, 2 to 3 per cluster` | `unknown` | `unknown, 2 to 3 per cluster` | `C_to_C` | True |
| 10594 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown, 2 per cluster` | `C_to_C` | True |
| 10618 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown, 4 to 6 per cluster` | `C_to_C` | True |
| 10629 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 10630 | `full_validation_candidate_surface` | `multiple cluster per 2 week, 5 per cluster` | `multiple per week` | `multiple cluster per 2 week, 5 per cluster` | `C_to_W` | True |
| 10673 | `full_validation_candidate_surface` | `1 cluster per month, multiple per cluster` | `no seizure frequency reference` | `1 cluster per month, multiple per cluster` | `C_to_W` | False |
| 10677 | `full_validation_candidate_surface` | `1 per month` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | `W_to_C` | True |
| 10753 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 10807 | `full_validation_candidate_surface` | `2 cluster per month, multiple per cluster` | `2 cluster per month, multiple per cluster` | `2 cluster per month, multiple per cluster` | `C_to_C` | True |
| 10829 | `full_validation_candidate_surface` | `2 cluster per month, multiple per cluster` | `2 cluster per month, multiple per cluster` | `2 cluster per month, multiple per cluster` | `C_to_C` | True |
| 10862 | `full_validation_candidate_surface` | `1 cluster per week, multiple per cluster` | `1 cluster per week, multiple per cluster` | `1 cluster per week, multiple per cluster` | `C_to_C` | True |
| 10865 | `full_validation_candidate_surface` | `1 cluster per week, multiple per cluster` | `` | `1 cluster per week, multiple per cluster` | `C_to_W` | False |
| 10873 | `full_validation_candidate_surface` | `1 cluster per week, 6 per cluster` | `1 cluster per week, 6 per cluster` | `1 cluster per week, 6 per cluster` | `C_to_C` | True |
| 10894 | `full_validation_candidate_surface` | `1 cluster per week, 4 per cluster` | `1 cluster per week, 4 per cluster` | `1 cluster per week, 4 per cluster` | `C_to_C` | True |
| 10896 | `full_validation_candidate_surface` | `1 cluster per week, 3 to 4 per cluster` | `` | `1 cluster per week, 3 to 4 per cluster` | `C_to_W` | False |
| 10902 | `full_validation_candidate_surface` | `1 cluster per week, 4 per cluster` | `1 cluster per week, 4 per cluster` | `1 cluster per week, 4 per cluster` | `C_to_C` | True |
| 10933 | `full_validation_candidate_surface` | `2 to 3 cluster per month, multiple per cluster` | `2 to 3 cluster per month, 5 per cluster` | `2 to 3 cluster per month, 5 per cluster` | `C_to_C` | True |
| 10942 | `full_validation_candidate_surface` | `5 per month` | `2 cluster per month, 5 per cluster` | `2 cluster per month, 5 per cluster` | `C_to_C` | True |
| 10965 | `full_validation_candidate_surface` | `2 cluster per month, 4 to 5 per cluster` | `2 cluster per month, 4 to 5 per cluster` | `2 cluster per month, 4 to 5 per cluster` | `C_to_C` | True |
| 10967 | `full_validation_candidate_surface` | `3 cluster per month, 4 to 5 per cluster` | `3 cluster per month, 4 to 5 per cluster` | `3 cluster per month, 4 to 5 per cluster` | `C_to_C` | True |
| 10984 | `full_validation_candidate_surface` | `3 cluster per month, multiple per cluster` | `` | `3 cluster per month, 3 to 4 per cluster` | `C_to_W` | False |
| 10996 | `full_validation_candidate_surface` | `1 to 2 cluster per month, multiple per cluster` | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, 4 per cluster` | `W_to_C` | True |
| 11002 | `full_validation_candidate_surface` | `2 to 4 cluster per month, multiple per cluster` | `2 to 4 cluster per month, 5 per cluster` | `2 to 4 cluster per month, 5 per cluster` | `C_to_C` | True |
| 11035 | `full_validation_candidate_surface` | `1 per 3 month` | `1 cluster per 3 month, 1 per cluster` | `1 cluster per 3 month, 1 per cluster` | `C_to_C` | True |
| 11109 | `full_validation_candidate_surface` | `2 cluster per month, 5 per cluster` | `` | `2 cluster per month, 5 per cluster` | `C_to_W` | False |
| 11118 | `full_validation_candidate_surface` | `2 cluster per month, 6 per cluster` | `2 cluster per month, 6 per cluster` | `2 cluster per month, 6 per cluster` | `C_to_C` | True |
| 11131 | `full_validation_candidate_surface` | `2 cluster per month, 3 to 4 per cluster` | `` | `2 cluster per month, 3 to 4 per cluster` | `C_to_W` | False |
| 11197 | `full_validation_candidate_surface` | `1 cluster per month, 4 to 6 per cluster` | `1 cluster per month, 4 to 6 per cluster` | `1 cluster per month, 4 to 6 per cluster` | `C_to_C` | True |
| 11216 | `full_validation_candidate_surface` | `seizure free for 4 month` | `seizure free for 4 month` | `unknown` | `W_to_W` | False |
| 11254 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `unknown` | `W_to_W` | False |
| 11259 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `unknown` | `W_to_W` | True |
| 11262 | `full_validation_candidate_surface` | `unknown` | `multiple per day` | `unknown` | `C_to_C` | True |
| 11272 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for 3 month` | `unknown` | `W_to_W` | False |
| 11282 | `full_validation_candidate_surface` | `unknown` | `seizure free for 3 month` | `unknown` | `C_to_W` | True |
| 11337 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 11350 | `full_validation_candidate_surface` | `multiple per week` | `multiple per day` | `unknown` | `C_to_C` | True |
| 11380 | `full_validation_candidate_surface` | `no seizure frequency reference` | `multiple per day` | `unknown` | `C_to_C` | True |
| 11389 | `full_validation_candidate_surface` | `no seizure frequency reference` | `1 per 2 month` | `unknown` | `C_to_W` | True |
| 11400 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `no seizure frequency reference` | `C_to_W` | False |
| 11405 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11408 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11409 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `no seizure frequency reference` | `C_to_C` | True |
| 11411 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11434 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11463 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11562 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11585 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11606 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11614 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11632 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | True |
| 11640 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11658 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11681 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11706 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11711 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11728 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11734 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11737 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11752 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11756 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11763 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11804 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11824 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11841 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | False |
| 11852 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `no seizure frequency reference` | `C_to_C` | True |
| 12036 | `full_validation_candidate_surface` | `multiple per day` | `multiple per day` | `multiple per day` | `C_to_C` | True |
| 12041 | `full_validation_candidate_surface` | `multiple per day` | `multiple per day` | `multiple per day` | `C_to_C` | True |
| 12046 | `full_validation_candidate_surface` | `multiple per day` | `multiple per day` | `multiple per day` | `C_to_C` | True |
| 12051 | `full_validation_candidate_surface` | `multiple per day` | `multiple per day` | `multiple per day` | `C_to_C` | True |
| 12111 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 12127 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 12130 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 12139 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 12145 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 12192 | `full_validation_candidate_surface` | `1 per day` | `multiple per day` | `1 per day` | `C_to_W` | True |
| 12218 | `full_validation_candidate_surface` | `1 per day` | `multiple per day` | `1 per day` | `C_to_W` | True |
| 12236 | `full_validation_candidate_surface` | `1 per day` | `multiple per day` | `1 per day` | `C_to_W` | True |
| 12246 | `full_validation_candidate_surface` | `1 to 2 per day` | `1 to 2 per day` | `1 to 2 per day` | `C_to_C` | True |
| 12314 | `full_validation_candidate_surface` | `3 per week` | `3 per week` | `3 per week` | `C_to_C` | True |
| 12366 | `full_validation_candidate_surface` | `4 per day` | `` | `4 per day` | `C_to_W` | False |
| 12378 | `full_validation_candidate_surface` | `4 per day` | `` | `4 per day` | `C_to_W` | False |
| 12383 | `full_validation_candidate_surface` | `4 per day` | `` | `4 per day` | `C_to_W` | False |
| 12403 | `full_validation_candidate_surface` | `2 to 3 per day` | `2 to 3 per day` | `2 to 3 per day` | `C_to_C` | True |
| 12412 | `full_validation_candidate_surface` | `2 per day` | `` | `2 per day` | `C_to_W` | False |
| 12422 | `full_validation_candidate_surface` | `4 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12438 | `full_validation_candidate_surface` | `2 to 3 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12456 | `full_validation_candidate_surface` | `3 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12460 | `full_validation_candidate_surface` | `2 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12468 | `full_validation_candidate_surface` | `4 per year` | `1 per day` | `1 per day` | `W_to_C` | True |
| 12484 | `full_validation_candidate_surface` | `3 to 4 per day` | `3 to 4 per day` | `3 to 4 per day` | `C_to_C` | False |
| 12502 | `full_validation_candidate_surface` | `4 per day` | `1 cluster per month, multiple per cluster` | `4 per day` | `C_to_W` | True |
| 12506 | `full_validation_candidate_surface` | `4 per day` | `` | `4 per day` | `C_to_W` | False |
| 12537 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 12548 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 12551 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 12556 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 12562 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 12573 | `full_validation_candidate_surface` | `1 per day` | `` | `1 per day` | `C_to_W` | False |
| 12584 | `full_validation_candidate_surface` | `1 per week` | `1 per 3 month` | `1 per week` | `C_to_W` | True |
| 12641 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 12665 | `full_validation_candidate_surface` | `5 per day` | `` | `1 per day` | `C_to_W` | False |
| 12667 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 12676 | `full_validation_candidate_surface` | `1 per day` | `` | `1 per day` | `C_to_W` | False |
| 12679 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 12749 | `full_validation_candidate_surface` | `3 to 4 per day` | `3 to 4 per day` | `3 to 4 per day` | `C_to_C` | True |
| 12751 | `full_validation_candidate_surface` | `4 per day` | `` | `4 per day` | `C_to_W` | False |
| 12788 | `full_validation_candidate_surface` | `6 per 4 month` | `` | `6 per 4 month` | `C_to_W` | False |
| 12810 | `full_validation_candidate_surface` | `5 per 2 month` | `5 per year` | `5 per 2 month` | `C_to_W` | True |
| 12823 | `full_validation_candidate_surface` | `9 per month` | `9 per year` | `9 per month` | `C_to_W` | True |
| 12827 | `full_validation_candidate_surface` | `5 per 5 month` | `` | `5 per 5 month` | `C_to_W` | False |
| 12835 | `full_validation_candidate_surface` | `4 per month` | `4 per year` | `4 per month` | `C_to_W` | True |
| 12877 | `full_validation_candidate_surface` | `10 per 4 month` | `10 per year` | `10 per 4 month` | `C_to_W` | True |
| 12882 | `full_validation_candidate_surface` | `7 per 4 month` | `` | `7 per 4 month` | `C_to_W` | False |
| 12901 | `full_validation_candidate_surface` | `8 per 5 month` | `` | `8 per 5 month` | `C_to_W` | False |
| 12949 | `full_validation_candidate_surface` | `9 per 6 month` | `` | `9 per 6 month` | `C_to_W` | False |
| 12950 | `full_validation_candidate_surface` | `7 per 3 month` | `7 per year` | `7 per 3 month` | `C_to_W` | True |
| 12963 | `full_validation_candidate_surface` | `no seizure frequency reference` | `2 to 3 per 3 month` | `unknown` | `C_to_W` | True |
| 12979 | `full_validation_candidate_surface` | `3 per 4 month` | `` | `3 per 4 month` | `C_to_W` | False |
| 13008 | `full_validation_candidate_surface` | `4 per month` | `4 per year` | `4 per month` | `C_to_W` | True |
| 13011 | `full_validation_candidate_surface` | `3 per 4 month` | `` | `3 per 4 month` | `C_to_W` | False |
| 13051 | `full_validation_candidate_surface` | `2 per 8 month` | `unknown` | `2 per 8 month` | `C_to_W` | False |
| 13058 | `full_validation_candidate_surface` | `2 per 7 month` | `` | `2 per 7 month` | `C_to_W` | False |
| 13114 | `full_validation_candidate_surface` | `1 per year` | `1 per 2 week` | `1 per year` | `C_to_W` | True |
| 13122 | `full_validation_candidate_surface` | `3 per year` | `no seizure frequency reference` | `3 per year` | `C_to_W` | True |
| 13149 | `full_validation_candidate_surface` | `3 per year` | `seizure free for multiple year` | `3 per year` | `C_to_W` | False |
| 13178 | `full_validation_candidate_surface` | `1 per 6 month` | `no seizure frequency reference` | `1 per 6 month` | `C_to_W` | True |
| 13190 | `full_validation_candidate_surface` | `1 per 5 month` | `seizure free for 5 month` | `1 per 5 month` | `C_to_W` | True |
| 13209 | `full_validation_candidate_surface` | `1 per 8 month` | `no seizure frequency reference` | `1 per 8 month` | `C_to_W` | True |
| 13267 | `full_validation_candidate_surface` | `2 per 5 month` | `no seizure frequency reference` | `2 per 5 month` | `C_to_W` | True |
| 13290 | `full_validation_candidate_surface` | `4 per 6 month` | `` | `4 per 6 month` | `C_to_W` | False |
| 13327 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple year` | `C_to_W` | False |
| 13336 | `full_validation_candidate_surface` | `seizure free for 1.5 year` | `seizure free for multiple year` | `seizure free for 1.5 year` | `C_to_C` | True |
| 13349 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple year` | `C_to_W` | False |
| 13385 | `full_validation_candidate_surface` | `seizure free for 1.5 year` | `` | `seizure free for 1.5 year` | `C_to_W` | False |
| 13450 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for 1 year` | `C_to_C` | True |
| 13471 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 5 year` | `C_to_W` | False |
| 13478 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for 1 year` | `C_to_W` | False |
| 13485 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple year` | `C_to_W` | False |
| 13487 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `C_to_C` | True |
| 13513 | `full_validation_candidate_surface` | `seizure free for 1.5 year` | `seizure free for multiple year` | `seizure free for 1.5 year` | `C_to_C` | True |
| 13574 | `full_validation_candidate_surface` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free for multiple year` | `C_to_C` | True |
| 13595 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple year` | `C_to_W` | False |
| 13598 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple year` | `C_to_W` | False |
| 13608 | `full_validation_candidate_surface` | `seizure free for multiple year` | `` | `seizure free for multiple year` | `C_to_W` | False |
| 13627 | `full_validation_candidate_surface` | `64 per 12 month` | `` | `64 per 12 month` | `C_to_W` | False |
| 13635 | `full_validation_candidate_surface` | `47 per 7 month` | `` | `47 per 7 month` | `C_to_W` | False |
| 13711 | `full_validation_candidate_surface` | `76 per 12 month` | `` | `76 per 12 month` | `C_to_W` | False |
| 13721 | `full_validation_candidate_surface` | `77 per 12 month` | `` | `77 per 12 month` | `C_to_W` | False |
| 13732 | `full_validation_candidate_surface` | `52 per 8 month` | `52 per 8 month` | `52 per 8 month` | `C_to_C` | True |
| 13843 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `seizure free for multiple month` | `W_to_W` | False |
| 13858 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `seizure free for multiple month` | `W_to_W` | True |
| 13889 | `full_validation_candidate_surface` | `no seizure frequency reference` | `seizure free for multiple year` | `seizure free for multiple month` | `W_to_C` | True |
| 13893 | `full_validation_candidate_surface` | `2 per year` | `` | `2 per year` | `C_to_W` | False |
| 13922 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `unknown` | `C_to_C` | True |
| 14002 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 14025 | `full_validation_candidate_surface` | `2 per 6 weeks` | `no seizure frequency reference` | `unknown` | `W_to_C` | True |
| 14029 | `full_validation_candidate_surface` | `no seizure frequency reference` | `unknown` | `unknown` | `C_to_C` | True |
| 14040 | `full_validation_candidate_surface` | `unknown` | `unknown` | `unknown` | `C_to_C` | True |
| 14076 | `full_validation_candidate_surface` | `seizure free for multiple year` | `unknown` | `unknown` | `W_to_C` | True |
| 14092 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `unknown` | `C_to_C` | True |
| 14096 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 14137 | `full_validation_candidate_surface` | `no seizure frequency reference` | `no seizure frequency reference` | `unknown` | `C_to_C` | True |
| 14146 | `full_validation_candidate_surface` | `no seizure frequency reference` | `` | `unknown` | `C_to_W` | False |
| 14187 | `full_validation_candidate_surface` | `2 to 3 per month` | `seizure free for 1 month` | `2 to 3 per month` | `C_to_W` | False |
| 14214 | `full_validation_candidate_surface` | `2 to 4 per month` | `seizure free for multiple year` | `2 to 4 per month` | `C_to_W` | True |
| 14250 | `full_validation_candidate_surface` | `2 per month` | `seizure free for multiple year` | `2 per month` | `C_to_W` | True |
| 14282 | `full_validation_candidate_surface` | `multiple per 6 week` | `seizure free for 1 month` | `multiple per month` | `C_to_W` | True |
| 14284 | `full_validation_candidate_surface` | `2 to 3 per month` | `seizure free for 1 month` | `2 to 3 per month` | `C_to_W` | True |
| 14317 | `full_validation_candidate_surface` | `4 per 2 month` | `seizure free for 2 month` | `4 per 2 month` | `C_to_W` | True |
| 14332 | `full_validation_candidate_surface` | `5 per 2 month` | `seizure free for 2 month` | `5 per 2 month` | `C_to_W` | True |
| 14335 | `full_validation_candidate_surface` | `3 to 4 per 2 month` | `seizure free for multiple year` | `3 to 4 per 2 month` | `C_to_W` | True |
| 14383 | `full_validation_candidate_surface` | `3 to 4 per 3 month` | `seizure free for 3 month` | `3 to 4 per 3 month` | `C_to_W` | True |
| 14454 | `full_validation_candidate_surface` | `2 per 2 month` | `seizure free for 2 month` | `2 per 2 month` | `C_to_W` | True |
| 14524 | `full_validation_candidate_surface` | `2 per 6 month` | `unknown` | `2 per 6 month` | `C_to_W` | True |
| 14530 | `full_validation_candidate_surface` | `2 per 2 month` | `seizure free for multiple year` | `2 per 2 month` | `C_to_W` | False |
| 14540 | `full_validation_candidate_surface` | `2 per 8 month` | `seizure free for multiple year` | `2 per 8 month` | `C_to_W` | False |
| 14562 | `full_validation_candidate_surface` | `3 per 6 month` | `seizure free for multiple year` | `3 per 6 month` | `C_to_W` | True |
| 14567 | `full_validation_candidate_surface` | `3 per 3 month` | `` | `3 per 3 month` | `C_to_W` | False |
| 14581 | `full_validation_candidate_surface` | `2 per 3 month` | `seizure free for multiple year` | `2 per 3 month` | `C_to_W` | True |
| 14587 | `full_validation_candidate_surface` | `2 per 3 month` | `no seizure frequency reference` | `2 per 3 month` | `C_to_W` | True |
| 14592 | `full_validation_candidate_surface` | `3 per 5 month` | `2 per month` | `3 per 5 month` | `C_to_W` | True |
| 14611 | `full_validation_candidate_surface` | `2 per 4 month` | `seizure free for multiple year` | `2 per 4 month` | `C_to_W` | True |
| 14628 | `full_validation_candidate_surface` | `2 per 2 month` | `` | `2 per 2 month` | `C_to_W` | False |
| 14635 | `full_validation_candidate_surface` | `5 per 4 month` | `seizure free for multiple year` | `5 per 4 month` | `C_to_W` | True |
| 14645 | `full_validation_candidate_surface` | `2 per 6 month` | `seizure free for multiple year` | `2 per 6 month` | `C_to_W` | True |
| 14662 | `full_validation_candidate_surface` | `3 per 4 month` | `` | `3 per 4 month` | `C_to_W` | False |
| 14672 | `full_validation_candidate_surface` | `3 per 8 month` | `seizure free for multiple year` | `3 per 8 month` | `C_to_W` | True |
| 14706 | `full_validation_candidate_surface` | `2 per 5 month` | `no seizure frequency reference` | `2 per 5 month` | `C_to_W` | True |
| 14765 | `full_validation_candidate_surface` | `1 per month` | `seizure free for 1 month` | `1 per month` | `C_to_W` | True |
| 14806 | `full_validation_candidate_surface` | `1 per 2 month` | `seizure free for 1 month` | `1 per 2 month` | `C_to_W` | True |
| 14810 | `full_validation_candidate_surface` | `12 per month` | `seizure free for multiple year` | `1 per month` | `W_to_W` | True |
| 14821 | `full_validation_candidate_surface` | `17 per month` | `seizure free for multiple year` | `1 per month` | `W_to_W` | False |
| 14872 | `full_validation_candidate_surface` | `1 per month` | `seizure free for multiple year` | `1 per month` | `C_to_W` | True |
| 14943 | `full_validation_candidate_surface` | `1 per 3 month` | `seizure free for multiple year` | `1 per 3 month` | `C_to_W` | True |
| 14949 | `full_validation_candidate_surface` | `1 per month` | `` | `1 per month` | `C_to_W` | False |
| 14965 | `full_validation_candidate_surface` | `1 per 3 month` | `seizure free for multiple year` | `1 per 3 month` | `C_to_W` | True |
| 14973 | `full_validation_candidate_surface` | `1 per month` | `seizure free for multiple year` | `1 per month` | `C_to_W` | False |
| 15004 | `full_validation_candidate_surface` | `1 per 3 month` | `seizure free for multiple year` | `1 per 3 month` | `C_to_W` | True |
| 15012 | `full_validation_candidate_surface` | `1 per 2 month` | `seizure free for multiple year` | `1 per 2 month` | `C_to_W` | True |
| 15021 | `full_validation_candidate_surface` | `1 per 3 month` | `` | `1 per 3 month` | `C_to_W` | False |
| 15029 | `full_validation_candidate_surface` | `1 per 3 month` | `seizure free for multiple year` | `1 per 3 month` | `C_to_W` | True |
| 15094 | `full_validation_candidate_surface` | `4 per 13 month` | `` | `4 per 13 month` | `C_to_W` | False |
| 15108 | `full_validation_candidate_surface` | `3 to 4 per 15 month` | `2 to 3 per month` | `3 to 4 per 15 month` | `C_to_W` | True |
| 15127 | `full_validation_candidate_surface` | `5 per 13 month` | `` | `5 per 13 month` | `C_to_W` | False |
| 15129 | `full_validation_candidate_surface` | `4 per 15 month` | `` | `4 per 15 month` | `C_to_W` | False |
| 15141 | `full_validation_candidate_surface` | `4 to 5 per 15 month` | `` | `4 to 5 per 15 month` | `C_to_W` | False |
| 15168 | `full_validation_candidate_surface` | `seizure free for multiple year` | `unknown` | `multiple per 15 month` | `W_to_C` | True |
| 15193 | `full_validation_candidate_surface` | `unknown` | `` | `multiple per 13 month` | `C_to_W` | False |
| 15242 | `full_validation_candidate_surface` | `multiple cluster per 15 month, multiple per cluster` | `unknown` | `multiple cluster per 15 month, multiple per cluster` | `C_to_W` | True |
| 15262 | `full_validation_candidate_surface` | `multiple cluster per 13 month, multiple per cluster` | `` | `multiple cluster per 13 month, multiple per cluster` | `C_to_W` | False |
| 15267 | `full_validation_candidate_surface` | `3 per 14 month` | `seizure free for 14 month` | `3 per 14 month` | `C_to_W` | True |
| 15306 | `full_validation_candidate_surface` | `2 to 3 per 15 month` | `2 to 3 per month` | `2 to 3 per 15 month` | `C_to_W` | True |
| 15317 | `full_validation_candidate_surface` | `2 to 3 per 15 month` | `2 to 3 per month` | `2 to 3 per 15 month` | `C_to_W` | True |
| 15376 | `full_validation_candidate_surface` | `1 cluster per 2 week, 4 to 6 per cluster` | `` | `1 cluster per 2 week, 4 to 6 per cluster` | `C_to_W` | False |
| 15404 | `full_validation_candidate_surface` | `1 cluster per 4 month, 3 to 4 per cluster` | `unknown` | `1 cluster per 4 month, 3 to 4 per cluster` | `C_to_W` | True |
| 15429 | `full_validation_candidate_surface` | `1 cluster per 2 month, 4 per cluster` | `unknown` | `1 cluster per 2 month, 4 per cluster` | `C_to_W` | True |
| 15431 | `full_validation_candidate_surface` | `1 cluster per 4 month, 5 per cluster` | `unknown` | `1 cluster per 4 month, 5 per cluster` | `C_to_W` | True |
| 15442 | `full_validation_candidate_surface` | `1 cluster per 4 day, 2 per cluster` | `` | `1 cluster per 4 day, 2 per cluster` | `C_to_W` | False |
| 15470 | `full_validation_candidate_surface` | `1 cluster per 5 day, multiple per cluster` | `1 cluster per 5 day, 2 per cluster` | `1 cluster per 5 day, multiple per cluster` | `C_to_C` | False |
| 15479 | `full_validation_candidate_surface` | `1 cluster per 4 to 5 day, 2 per cluster` | `1 cluster per 4 to 5 day, 2 per cluster` | `1 cluster per 4 to 5 day, 2 per cluster` | `C_to_C` | True |
| 15497 | `full_validation_candidate_surface` | `1 cluster per 4 to 5 day, 5 per cluster` | `1 cluster per 5 day, 5 per cluster` | `1 cluster per 4 to 5 day, 5 per cluster` | `C_to_C` | True |
| 15503 | `full_validation_candidate_surface` | `1 cluster per 5 day, 3 to 4 per cluster` | `1 cluster per 5 day, 3 to 4 per cluster` | `1 cluster per 5 day, 3 to 4 per cluster` | `C_to_C` | True |
| 15513 | `full_validation_candidate_surface` | `1 cluster per 4 to 5 day, 2 to 3 per cluster` | `1 cluster per 5 day, 2 to 3 per cluster` | `1 cluster per 4 to 5 day, 2 to 3 per cluster` | `C_to_C` | True |
| 15519 | `full_validation_candidate_surface` | `1 cluster per 4 day, 3 per cluster` | `unknown` | `1 cluster per 4 day, 3 per cluster` | `C_to_W` | False |
| 15529 | `full_validation_candidate_surface` | `1 cluster per 3 day, 4 per cluster` | `unknown` | `1 cluster per 3 day, 4 per cluster` | `C_to_W` | True |
| 15593 | `full_validation_candidate_surface` | `2 per 6 month` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | `W_to_C` | True |
| 15614 | `full_validation_candidate_surface` | `3 per week` | `3 per week` | `3 per week` | `C_to_C` | True |
| 15628 | `full_validation_candidate_surface` | `multiple per week` | `multiple per week` | `multiple per week` | `C_to_C` | True |
| 15639 | `full_validation_candidate_surface` | `2 per week` | `` | `2 per week` | `C_to_W` | False |
| 15642 | `full_validation_candidate_surface` | `2 to 4 per week` | `2 to 4 per week` | `2 to 4 per week` | `C_to_C` | True |
| 15650 | `full_validation_candidate_surface` | `3 to 4 per day` | `3 to 4 per day` | `3 to 4 per day` | `C_to_C` | True |
| 15672 | `full_validation_candidate_surface` | `2 per 6 week` | `1 per day` | `1 per day` | `W_to_C` | True |
| 15697 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 15715 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | True |
| 15745 | `full_validation_candidate_surface` | `2 to 3 per week` | `2 to 3 per week` | `2 to 3 per week` | `C_to_C` | True |
| 15766 | `full_validation_candidate_surface` | `4 per week` | `4 per week` | `4 per week` | `C_to_C` | True |
| 15768 | `full_validation_candidate_surface` | `2 to 3 per week` | `2 to 3 per week` | `2 to 3 per week` | `C_to_C` | True |
| 15771 | `full_validation_candidate_surface` | `3 per week` | `multiple per week` | `3 per week` | `C_to_W` | True |
| 15772 | `full_validation_candidate_surface` | `2 per week` | `` | `2 per week` | `C_to_W` | False |
| 15774 | `full_validation_candidate_surface` | `2 per week` | `` | `2 per week` | `C_to_W` | False |
| 15783 | `full_validation_candidate_surface` | `2 to 3 per week` | `` | `2 to 3 per week` | `C_to_W` | False |
| 15802 | `full_validation_candidate_surface` | `7 per week` | `` | `7 per week` | `C_to_W` | False |
| 15831 | `full_validation_candidate_surface` | `2 to 4 per day` | `2 to 4 per day` | `2 to 4 per day` | `C_to_C` | True |
| 15834 | `full_validation_candidate_surface` | `1 per multiple month` | `` | `5 per week` | `W_to_W` | False |
| 15964 | `full_validation_candidate_surface` | `11 per 3 month` | `11 per 2 month` | `11 per 3 month` | `C_to_W` | True |
| 15965 | `full_validation_candidate_surface` | `13 per 2 month` | `13 per 2 month` | `13 per 2 month` | `C_to_C` | True |
| 15966 | `full_validation_candidate_surface` | `5 per 3 month` | `5 per 2 month` | `5 per 3 month` | `C_to_C` | True |
| 15982 | `full_validation_candidate_surface` | `9 per 2 month` | `` | `9 per 2 month` | `C_to_W` | False |
| 15986 | `full_validation_candidate_surface` | `11 per 3 month` | `1 per month` | `11 per 3 month` | `C_to_W` | True |
| 15992 | `full_validation_candidate_surface` | `7 per 2 month` | `` | `7 per 2 month` | `C_to_W` | False |
| 15997 | `full_validation_candidate_surface` | `10 per 3 month` | `10 per 2 month` | `10 per 3 month` | `C_to_W` | True |
| 16021 | `full_validation_candidate_surface` | `9 per 3 month` | `9 per 2 month` | `9 per 3 month` | `C_to_W` | True |
| 16041 | `full_validation_candidate_surface` | `9 per 3 month` | `9 per 2 month` | `9 per 3 month` | `C_to_W` | True |
| 16084 | `full_validation_candidate_surface` | `8 per 4 month` | `8 per 4 month` | `8 per 4 month` | `C_to_C` | True |
| 16091 | `full_validation_candidate_surface` | `3 per 3 month` | `` | `3 per 3 month` | `C_to_W` | False |
| 16097 | `full_validation_candidate_surface` | `6 per month` | `17 per 4 month` | `17 per 4 month` | `C_to_C` | True |
| 16107 | `full_validation_candidate_surface` | `8 per 3 month` | `8 per 3 month` | `8 per 3 month` | `C_to_C` | True |
| 16108 | `full_validation_candidate_surface` | `12 per 4 month` | `` | `12 per 4 month` | `C_to_W` | False |
| 16132 | `full_validation_candidate_surface` | `15 per 3 month` | `13 per 2 month` | `15 per 3 month` | `C_to_C` | True |
| 16133 | `full_validation_candidate_surface` | `6 per month` | `` | `18 per 4 month` | `C_to_W` | False |
| 16161 | `full_validation_candidate_surface` | `18 per 3 month` | `` | `18 per 3 month` | `C_to_W` | False |
| 16162 | `full_validation_candidate_surface` | `11 per 3 month` | `` | `11 per 3 month` | `C_to_W` | False |
| 16181 | `full_validation_candidate_surface` | `15 per 4 month` | `` | `15 per 4 month` | `C_to_W` | False |
| 16195 | `full_validation_candidate_surface` | `16 per 4 month` | `` | `16 per 4 month` | `C_to_W` | False |
| 16203 | `full_validation_candidate_surface` | `9 per 3 month` | `8 per 2 month` | `9 per 3 month` | `C_to_W` | True |
| 16204 | `full_validation_candidate_surface` | `5 per 3 month` | `5 per 3 month` | `5 per 3 month` | `C_to_C` | True |
| 16220 | `full_validation_candidate_surface` | `11 per 4 month` | `11 per 4 month` | `11 per 4 month` | `C_to_C` | True |
| 16324 | `full_validation_candidate_surface` | `10 per 3 month` | `` | `10 per 3 month` | `C_to_W` | False |
| 16335 | `full_validation_candidate_surface` | `6 per 2 month` | `` | `7 per 3 month` | `C_to_W` | False |
| 16356 | `full_validation_candidate_surface` | `1 per 4 day` | `1 per 4 day` | `1 per 4 day` | `C_to_C` | True |
| 16394 | `full_validation_candidate_surface` | `1 per 2 to 4 day` | `1 per 2 to 4 day` | `1 per 2 to 4 day` | `C_to_C` | True |
| 16408 | `full_validation_candidate_surface` | `1 per 3 day` | `` | `1 per 3 day` | `C_to_W` | False |
| 16429 | `full_validation_candidate_surface` | `1 per 2 to 3 day` | `` | `1 per 2 to 3 day` | `C_to_W` | False |
| 16432 | `full_validation_candidate_surface` | `1 per 2 day` | `1 per day` | `1 per 2 day` | `C_to_W` | True |
| 16450 | `full_validation_candidate_surface` | `1 per multiple day` | `1 per day` | `1 per multiple day` | `C_to_W` | True |
| 16529 | `full_validation_candidate_surface` | `1 per 5 day` | `1 per 5 day` | `1 per 5 day` | `C_to_C` | True |
| 16557 | `full_validation_candidate_surface` | `1 per 2 to 3 day` | `1 per 2 to 3 day` | `1 per 2 to 3 day` | `C_to_C` | True |
| 16574 | `full_validation_candidate_surface` | `1 per 4 day` | `unknown` | `1 per 4 day` | `C_to_W` | True |
| 16590 | `full_validation_candidate_surface` | `1 per 4 to 5 day` | `unknown` | `1 per 4 to 5 day` | `C_to_W` | True |
| 16618 | `full_validation_candidate_surface` | `1 per 5 day` | `` | `1 per 5 day` | `C_to_W` | False |
| 16645 | `full_validation_candidate_surface` | `5 per 7 month` | `` | `5 per 7 month` | `C_to_W` | False |
| 16674 | `full_validation_candidate_surface` | `7 per 6 month` | `` | `7 per 6 month` | `C_to_W` | False |
| 16685 | `full_validation_candidate_surface` | `10 per 3 month` | `6 per month` | `10 per 3 month` | `C_to_W` | True |
| 16697 | `full_validation_candidate_surface` | `3 per 6 month` | `1 per 3 month` | `3 per 6 month` | `C_to_C` | True |
| 16704 | `full_validation_candidate_surface` | `9 per 6 month` | `7 per month` | `9 per 6 month` | `C_to_W` | True |
| 16714 | `full_validation_candidate_surface` | `5 per 6 month` | `1 per month` | `5 per 6 month` | `C_to_W` | True |
| 16717 | `full_validation_candidate_surface` | `5 per 6 month` | `no seizure frequency reference` | `5 per 6 month` | `C_to_W` | True |
| 16719 | `full_validation_candidate_surface` | `7 per 6 month` | `1 per week` | `7 per 6 month` | `C_to_W` | True |
| 16728 | `full_validation_candidate_surface` | `4 per 6 month` | `1 to 2 per month` | `4 per 6 month` | `C_to_W` | True |
| 16750 | `full_validation_candidate_surface` | `6 per 7 month` | `seizure free for multiple year` | `6 per 7 month` | `C_to_W` | True |
| 16757 | `full_validation_candidate_surface` | `13 per 6 month` | `` | `13 per 6 month` | `C_to_W` | False |
| 16758 | `full_validation_candidate_surface` | `9 per 5 month` | `` | `9 per 5 month` | `C_to_W` | False |
| 16772 | `full_validation_candidate_surface` | `9 per 5 month` | `` | `9 per 5 month` | `C_to_W` | False |
| 16774 | `full_validation_candidate_surface` | `19 per 7 month` | `` | `19 per 7 month` | `C_to_W` | False |
| 16780 | `full_validation_candidate_surface` | `3 per 7 month` | `unknown` | `3 per 7 month` | `C_to_W` | True |
| 16824 | `full_validation_candidate_surface` | `11 per 5 month` | `7 per month` | `11 per 5 month` | `C_to_W` | True |
| 16833 | `full_validation_candidate_surface` | `8 per 6 month` | `` | `8 per 6 month` | `C_to_W` | False |
| 16839 | `full_validation_candidate_surface` | `9 per 4 month` | `` | `9 per 4 month` | `C_to_W` | False |
| 16867 | `full_validation_candidate_surface` | `6 per 7 month` | `` | `6 per 7 month` | `C_to_W` | False |
| 16907 | `full_validation_candidate_surface` | `9 per 6 month` | `` | `9 per 6 month` | `C_to_W` | False |
| 16938 | `full_validation_candidate_surface` | `2 per week` | `1 per 2 month` | `2 per week` | `C_to_W` | True |
| 16947 | `full_validation_candidate_surface` | `2 per week` | `1 per 2 month` | `2 per week` | `C_to_W` | True |
| 16961 | `full_validation_candidate_surface` | `2 per week` | `1 per 3 month` | `2 per week` | `C_to_W` | True |
| 16983 | `full_validation_candidate_surface` | `2 to 3 per week` | `2 to 3 per week` | `2 to 3 per week` | `C_to_C` | True |
| 16990 | `full_validation_candidate_surface` | `4 to 5 per week` | `4 to 5 per week` | `4 to 5 per week` | `C_to_C` | True |
| 17001 | `full_validation_candidate_surface` | `5 per week` | `` | `5 per week` | `C_to_W` | False |
| 17003 | `full_validation_candidate_surface` | `3 to 4 per month` | `3 to 4 per month` | `3 to 4 per month` | `C_to_C` | False |
| 17110 | `full_validation_candidate_surface` | `4 to 5 cluster per week, multiple per cluster` | `unknown` | `4 to 5 cluster per week, multiple per cluster` | `C_to_W` | True |
| 17135 | `full_validation_candidate_surface` | `5 cluster per month, multiple per cluster` | `` | `5 cluster per month, multiple per cluster` | `C_to_W` | False |
| 17146 | `full_validation_candidate_surface` | `1 per day` | `1 per day` | `1 per day` | `C_to_C` | False |
| 17167 | `full_validation_candidate_surface` | `1 per week` | `1 per 6 month` | `1 per week` | `C_to_W` | True |
| 17189 | `full_validation_candidate_surface` | `1 per month` | `` | `1 per month` | `C_to_W` | False |
| 17200 | `full_validation_candidate_surface` | `1 per month` | `1 per month` | `1 per month` | `C_to_C` | True |
| 17201 | `full_validation_candidate_surface` | `4 per month` | `` | `4 per month` | `C_to_W` | False |
| 17273 | `full_validation_candidate_surface` | `1 per 2 day` | `1 per day` | `1 per 2 day` | `C_to_W` | True |
| 17279 | `full_validation_candidate_surface` | `1 per 4 to 5 week` | `1 per day` | `1 per 4 to 5 week` | `C_to_W` | True |
| 17287 | `full_validation_candidate_surface` | `1 per 1 to 2 day` | `1 per day` | `1 per 1 to 2 day` | `C_to_W` | True |

## Interpretation Boundary

This hard slice is intentionally enriched for current validation failures. Its slice accuracy is not a full-validation score; it only estimates whether a direct-label candidate source creates useful alternatives for rows that saved candidate discovery missed.
