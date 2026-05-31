# Gan 2026 V1 Validation Deterministic Rule Ablation

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.
The frozen deterministic V1 test holdout remains 0.7600 Purist micro F1/accuracy and is included only as prior context.

Split manifest: `data/Gan (2026)/splits/gan2026_split_v1.json` (`gan2026_split_v1`)
Changed-row CSV: `experiments/gan2026_v1_validation_ablation_changed_rows_2026-05-31.csv`

## Experiment Unit

Hypothesis: disabling clinically portable and dataset-specific deterministic rule groups will expose which parts of V1 validation performance depend on each rule family.

Minimal change: run the frozen V1 extractor on validation with one `RuleGroup` disabled at a time. No deterministic recall rules, scorer policy, split policy, or test rows are changed.

Data surface: Gan 2026 `validation` split; `row_ok=False` rows included per project policy.

Scorer: Gan-compatible Purist micro F1 as the primary metric, Pragmatic micro F1 as a side-car. Evidence validity is exact selected-evidence substring validity.

## Ablation Table

| Condition | Disabled group | Changed rows | Correct | Evidence valid | Purist micro F1 | Pragmatic micro F1 | Unknown/no-reference predictions |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline_all_groups | none | 0 | 684 / 750 | 750 / 750 | 0.9120 | 0.9213 | 131 |
| disable_date_duration_utilities | date_duration_utilities | 0 | 684 / 750 | 750 / 750 | 0.9120 | 0.9213 | 131 |
| disable_portable_rate_expressions | portable_rate_expressions | 183 | 559 / 750 | 750 / 750 | 0.7453 | 0.7733 | 230 |
| disable_seizure_free_no_event_assertions | seizure_free_no_event_assertions | 131 | 595 / 750 | 750 / 750 | 0.7933 | 0.8027 | 243 |
| disable_cluster_arithmetic | cluster_arithmetic | 59 | 632 / 750 | 750 / 750 | 0.8427 | 0.8547 | 171 |
| disable_diary_log_aggregation | diary_log_aggregation | 48 | 638 / 750 | 750 / 750 | 0.8507 | 0.8653 | 168 |
| disable_temporal_selection | temporal_selection | 135 | 571 / 750 | 750 / 750 | 0.7613 | 0.7853 | 127 |
| disable_gan_shorthand | gan_shorthand | 21 | 664 / 750 | 750 / 750 | 0.8853 | 0.8973 | 145 |
| disable_benchmark_repair | benchmark_repair | 6 | 684 / 750 | 750 / 750 | 0.9120 | 0.9213 | 131 |

## Prediction State Distribution

| Condition | Frequency | Seizure-free | Unknown | No-reference | Unresolved multiple |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline_all_groups | 459 | 130 | 9 | 122 | 30 |
| disable_date_duration_utilities | 459 | 130 | 9 | 122 | 30 |
| disable_portable_rate_expressions | 354 | 142 | 9 | 221 | 24 |
| disable_seizure_free_no_event_assertions | 476 | 0 | 14 | 229 | 31 |
| disable_cluster_arithmetic | 413 | 136 | 10 | 161 | 30 |
| disable_diary_log_aggregation | 417 | 135 | 9 | 159 | 30 |
| disable_temporal_selection | 398 | 209 | 5 | 122 | 16 |
| disable_gan_shorthand | 442 | 133 | 9 | 136 | 30 |
| disable_benchmark_repair | 459 | 130 | 9 | 122 | 30 |

## Top Changed Rows

### disable_date_duration_utilities

Changed rows: 0

| Row | Baseline correct | Ablated correct | Gold category | Baseline prediction | Ablated prediction |
| ---: | --- | --- | --- | --- | --- |
| - | - | - | - | - | - |

### disable_portable_rate_expressions

Changed rows: 183

| Row | Baseline correct | Ablated correct | Gold category | Baseline prediction | Ablated prediction |
| ---: | --- | --- | --- | --- | --- |
| 5921 | False | True | seizure_freq_more1per6mon_less1mon | seizure_freq_1ormore_daily / 1 per day | seizure_freq_more1per6mon_less1mon / 1 per 6 to 8 week |
| 6209 | False | True | seizure_freq_unknown | seizure_freq_1ormore_daily / 1 per day | seizure_freq_unknown / no seizure frequency reference |
| 6321 | False | True | seizure_freq_unknown | seizure_freq_1ormore_daily / 1 per day | seizure_freq_unknown / no seizure frequency reference |
| 7168 | False | True | seizure_freq_unknown | seizure_freq_1_per_6mon / 2 per year | seizure_freq_unknown / no seizure frequency reference |
| 9496 | False | True | seizure_freq_more1per6mon_less1mon | seizure_freq_more1week_less1day / 2 per week | seizure_freq_more1per6mon_less1mon / 2 per 5 month |
| 10386 | False | True | seizure_freq_more1week_less1day | seizure_freq_1ormore_daily / 1 per day | seizure_freq_more1week_less1day / 1 cluster per week, 2 to 3 per cluster |
| 10 | True | False | seizure_freq_1ormore_daily | seizure_freq_1ormore_daily / 4 per day | seizure_freq_unknown / no seizure frequency reference |
| 40 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 4 per week | seizure_freq_unknown / no seizure frequency reference |
| 79 | True | False | seizure_freq_more1per6mon_less1mon | seizure_freq_more1per6mon_less1mon / 6 to 7 per year | seizure_freq_unknown / no seizure frequency reference |
| 103 | True | False | seizure_freq_more1per6mon_less1mon | seizure_freq_more1per6mon_less1mon / 2 to 4 per year | seizure_freq_unknown / no seizure frequency reference |
| 128 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 17 per month | seizure_freq_unknown / no seizure frequency reference |
| 409 | True | False | seizure_freq_1_per_mon | seizure_freq_1_per_mon / 1 per month | seizure_freq_more1week_less1day / 1 cluster per week, 3 per cluster |

### disable_seizure_free_no_event_assertions

Changed rows: 131

| Row | Baseline correct | Ablated correct | Gold category | Baseline prediction | Ablated prediction |
| ---: | --- | --- | --- | --- | --- |
| 3356 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 3528 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 4690 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 5534 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 5974 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 6077 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for 8 month | seizure_freq_unknown / no seizure frequency reference |
| 6131 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for 6 month | seizure_freq_unknown / no seizure frequency reference |
| 6244 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 6501 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 6571 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 6987 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |
| 9888 | False | True | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | seizure_freq_unknown / no seizure frequency reference |

### disable_cluster_arithmetic

Changed rows: 59

| Row | Baseline correct | Ablated correct | Gold category | Baseline prediction | Ablated prediction |
| ---: | --- | --- | --- | --- | --- |
| 1694 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 1 cluster per 2 week, 3 per cluster | seizure_freq_unknown / no seizure frequency reference |
| 1706 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / multiple cluster per month, multiple per cluster | seizure_freq_unknown / no seizure frequency reference |
| 3224 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 1 cluster per month, 6 to 7 per cluster | seizure_freq_unknown / no seizure frequency reference |
| 3261 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 2 cluster per month, 4 per cluster | seizure_freq_unknown / no seizure frequency reference |
| 5837 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 2 cluster per 3 week, multiple per cluster | seizure_freq_more1mon_less1week / 1 per 3 week |
| 7167 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 3 cluster per 6 week, 2 to 4 per cluster | seizure_freq_unknown / no seizure frequency reference |
| 7401 | True | False | seizure_freq_more1mon_less1week | seizure_freq_more1mon_less1week / 2 cluster per 6 week, 1 to 2 per cluster | seizure_freq_1_per_mon / 1 to 2 per 6 week |
| 10003 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 1 cluster per week, multiple per cluster | seizure_freq_unknown / no seizure frequency reference |
| 10047 | True | False | seizure_freq_more1mon_less1week | seizure_freq_more1mon_less1week / 2 cluster per 3 month, multiple per cluster | seizure_freq_unknown / no seizure frequency reference |
| 10063 | True | False | seizure_freq_more1mon_less1week | seizure_freq_more1mon_less1week / 3 cluster per 3 month, multiple per cluster | seizure_freq_unknown / no seizure frequency reference |
| 10097 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 3 cluster per month, multiple per cluster | seizure_freq_unknown / no seizure frequency reference |
| 10237 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 4 cluster per month, multiple per cluster | seizure_freq_unknown / unknown |

### disable_diary_log_aggregation

Changed rows: 48

| Row | Baseline correct | Ablated correct | Gold category | Baseline prediction | Ablated prediction |
| ---: | --- | --- | --- | --- | --- |
| 3281 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 8 per month | seizure_freq_1ormore_daily / 1 per day |
| 3297 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 6 per month | seizure_freq_unknown / no seizure frequency reference |
| 3325 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 3 per week | seizure_freq_unknown / no seizure frequency reference |
| 4337 | True | False | seizure_freq_1_per_mon | seizure_freq_1_per_mon / 3 per 3 month | currently_no_seizure / seizure free for multiple year |
| 4345 | True | False | seizure_freq_1_per_week | seizure_freq_1_per_week / 4 per month | currently_no_seizure / seizure free for multiple year |
| 4368 | True | False | seizure_freq_more1mon_less1week | seizure_freq_more1mon_less1week / 5 per 2 month | currently_no_seizure / seizure free for multiple year |
| 4402 | True | False | seizure_freq_1_per_mon | seizure_freq_1_per_mon / 7 per 7 month | seizure_freq_unknown / no seizure frequency reference |
| 5995 | True | False | seizure_freq_more1per6mon_less1mon | seizure_freq_more1per6mon_less1mon / 3 per 9 month | seizure_freq_unknown / no seizure frequency reference |
| 6065 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 5 per month | seizure_freq_unknown / no seizure frequency reference |
| 7275 | True | False | seizure_freq_1_per_mon | seizure_freq_1_per_mon / 3 per 3 month | seizure_freq_more1per6mon_less1mon / 2 per 12 week |
| 9449 | True | False | seizure_freq_more1per6mon_less1mon | seizure_freq_more1per6mon_less1mon / 4 per 6 month | seizure_freq_unknown / no seizure frequency reference |
| 9462 | True | False | seizure_freq_more1per6mon_less1mon | seizure_freq_more1per6mon_less1mon / 7 per 11 month | seizure_freq_unknown / no seizure frequency reference |

### disable_temporal_selection

Changed rows: 135

| Row | Baseline correct | Ablated correct | Gold category | Baseline prediction | Ablated prediction |
| ---: | --- | --- | --- | --- | --- |
| 5921 | False | True | seizure_freq_more1per6mon_less1mon | seizure_freq_1ormore_daily / 1 per day | seizure_freq_more1per6mon_less1mon / 1 per 6 to 8 week |
| 6889 | False | True | seizure_freq_unknown | seizure_freq_more1mon_less1week / 1 per 2 to 3 week | seizure_freq_unknown / multiple per week |
| 10386 | False | True | seizure_freq_more1week_less1day | seizure_freq_1ormore_daily / 1 per day | seizure_freq_more1week_less1day / 1 cluster per week, 2 to 3 per cluster |
| 13209 | False | True | seizure_freq_1_per_yr | seizure_freq_more1per6mon_less1mon / 1 per 4 to 5 week | seizure_freq_1_per_yr / 1 per 8 month |
| 15986 | False | True | seizure_freq_more1mon_less1week | seizure_freq_more1week_less1day / 1 per 5 to 7 day | seizure_freq_more1mon_less1week / 11 per 3 month |
| 278 | True | False | seizure_freq_unknown | seizure_freq_unknown / multiple per week | currently_no_seizure / seizure free for multiple year |
| 466 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 21 to 28 per month | currently_no_seizure / seizure free for multiple year |
| 744 | True | False | seizure_freq_unknown | seizure_freq_unknown / multiple per week | seizure_freq_more1per6mon_less1mon / 1 per 8 week |
| 891 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 1 per 2 day | currently_no_seizure / seizure free for multiple year |
| 899 | True | False | seizure_freq_more1mon_less1week | seizure_freq_more1mon_less1week / 1 per 2 week | currently_no_seizure / seizure free for multiple year |
| 1171 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 7 to 9 per 3 week | currently_no_seizure / seizure free for multiple year |
| 1363 | True | False | seizure_freq_1ormore_daily | seizure_freq_1ormore_daily / 3 per day | seizure_freq_more1week_less1day / 1 to 2 per week |

### disable_gan_shorthand

Changed rows: 21

| Row | Baseline correct | Ablated correct | Gold category | Baseline prediction | Ablated prediction |
| ---: | --- | --- | --- | --- | --- |
| 3681 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 9 per month | seizure_freq_unknown / no seizure frequency reference |
| 3682 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 6 per month | seizure_freq_unknown / no seizure frequency reference |
| 3710 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 5 per week | seizure_freq_unknown / no seizure frequency reference |
| 3791 | True | False | seizure_freq_more1per6mon_less1mon | seizure_freq_more1per6mon_less1mon / 10 per year | currently_no_seizure / seizure free for multiple year |
| 3801 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 9 per month | currently_no_seizure / seizure free for multiple year |
| 3806 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 6 per month | seizure_freq_unknown / no seizure frequency reference |
| 3827 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 7 per month | seizure_freq_more1mon_less1week / 1 cluster per 2 month, 3 per cluster |
| 3846 | True | False | seizure_freq_1ormore_daily | seizure_freq_1ormore_daily / 2 per day | seizure_freq_unknown / no seizure frequency reference |
| 3849 | True | False | seizure_freq_1ormore_daily | seizure_freq_1ormore_daily / 3 per day | seizure_freq_unknown / no seizure frequency reference |
| 3889 | True | False | seizure_freq_more1per6mon_less1mon | seizure_freq_more1per6mon_less1mon / 8 per year | seizure_freq_unknown / no seizure frequency reference |
| 3892 | True | False | seizure_freq_more1per6mon_less1mon | seizure_freq_more1per6mon_less1mon / 3 per year | seizure_freq_unknown / no seizure frequency reference |
| 3940 | True | False | seizure_freq_more1week_less1day | seizure_freq_more1week_less1day / 4 per week | seizure_freq_unknown / no seizure frequency reference |

### disable_benchmark_repair

Changed rows: 6

| Row | Baseline correct | Ablated correct | Gold category | Baseline prediction | Ablated prediction |
| ---: | --- | --- | --- | --- | --- |
| 6244 | False | False | seizure_freq_unknown | currently_no_seizure / seizure free for multiple year | currently_no_seizure / seizure free for multiple month |
| 3137 | True | True | currently_no_seizure | currently_no_seizure / seizure free for multiple year | currently_no_seizure / seizure free for multiple month |
| 5345 | True | True | currently_no_seizure | currently_no_seizure / seizure free for multiple year | currently_no_seizure / seizure free for multiple month |
| 5406 | True | True | currently_no_seizure | currently_no_seizure / seizure free for multiple year | currently_no_seizure / seizure free for multiple month |
| 8808 | True | True | currently_no_seizure | currently_no_seizure / seizure free for multiple year | currently_no_seizure / seizure free for multiple month |
| 9238 | True | True | currently_no_seizure | currently_no_seizure / seizure free for multiple year | currently_no_seizure / seizure free for multiple month |
