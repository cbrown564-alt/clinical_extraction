# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.3240 | 0.3240 | 0.3240 | 0.3240 |
| macro | 0.4573 | 0.2108 | 0.2152 | 0.3240 |
| weighted | 0.5171 | 0.3240 | 0.2678 | 0.3240 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| missed_frequency_evidence | 356 |
| correct | 125 |
| scorer_correct_semantic_mismatch | 118 |
| missed_seizure_free_evidence | 85 |
| frequency_predicted_seizure_free | 26 |
| wrong_frequency_bucket | 25 |
| overpredicted_frequency | 15 |

## Gold Kinds

| Gold kind | Count |
| --- | ---: |
| frequency | 468 |
| seizure_free | 112 |
| unknown | 100 |
| unresolved_multiple | 43 |
| no_reference | 27 |

## Prediction Kinds

| Prediction kind | Count |
| --- | ---: |
| no_reference | 582 |
| frequency | 99 |
| seizure_free | 48 |
| unknown | 11 |
| unresolved_multiple | 10 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| seizure_freq_more1week_less1day | seizure_freq_unknown | 134 |
| currently_no_seizure | seizure_freq_unknown | 85 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 81 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_unknown | 58 |
| seizure_freq_1ormore_daily | seizure_freq_unknown | 37 |
| seizure_freq_1_per_mon | seizure_freq_unknown | 31 |
| seizure_freq_1_per_week | seizure_freq_unknown | 10 |
| seizure_freq_more1per6mon_less1mon | currently_no_seizure | 9 |
| seizure_freq_more1mon_less1week | currently_no_seizure | 9 |
| seizure_freq_1_per_6mon | seizure_freq_unknown | 4 |
| seizure_freq_unknown | currently_no_seizure | 4 |
| seizure_freq_unknown | seizure_freq_more1per6mon_less1mon | 4 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
| 156 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 180 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 182 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 187 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 190 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_mon | seizure_freq_unknown |
| 198 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_mon | seizure_freq_unknown |
| 212 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 218 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 243 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 409 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_mon | seizure_freq_unknown |
| 531 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 694 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 704 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 725 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 731 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 763 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 790 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 816 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_mon | seizure_freq_unknown |
| 849 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_yr | seizure_freq_unknown |
| 854 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_yr | seizure_freq_unknown |
