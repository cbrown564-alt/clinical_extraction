# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.9280 | 0.9280 | 0.9280 | 0.9280 |
| macro | 0.9152 | 0.9337 | 0.9189 | 0.9280 |
| weighted | 0.9326 | 0.9280 | 0.9280 | 0.9280 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| correct | 616 |
| scorer_correct_semantic_mismatch | 80 |
| wrong_frequency_bucket | 44 |
| overpredicted_frequency | 7 |
| missed_seizure_free_evidence | 3 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 1098 |
| Rows with zero clinical candidates | 108 |
| Incorrect rows with zero clinical candidates | 3 |

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
| frequency | 473 |
| seizure_free | 130 |
| no_reference | 108 |
| unresolved_multiple | 30 |
| unknown | 9 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| clinical_evidence | 497 |
| other_text | 143 |
| header_fallback | 108 |
| medication_or_dose | 2 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| none | 616 |
| semantic_state_mapping | 81 |
| temporal_selection | 39 |
| assertion_classification | 9 |
| candidate_extraction | 3 |
| cluster_normalization | 1 |
| seizure_type_selection | 1 |

## Clinical Error Mode Flags

These flags are heuristic row slices, not mutually exclusive causal labels.

| Mode | Count |
| --- | ---: |
| ranges | 693 |
| medication_status | 648 |
| uncertainty | 441 |
| clusters | 407 |
| multiple_seizure_types | 401 |
| historical_current | 394 |
| negation | 364 |
| relative_dates | 332 |
| family_history | 111 |
| pnes_functional | 56 |
| lay_terminology | 42 |
| legacy_terminology | 17 |
| none | 1 |

## Incorrect Clinical Error Mode Flags

These counts are restricted to incorrect rows.

| Mode | Count |
| --- | ---: |
| medication_status | 51 |
| ranges | 48 |
| uncertainty | 39 |
| historical_current | 34 |
| clusters | 33 |
| multiple_seizure_types | 29 |
| relative_dates | 26 |
| negation | 20 |
| family_history | 7 |
| pnes_functional | 4 |
| lay_terminology | 3 |
| legacy_terminology | 1 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| seizure_freq_unknown | currently_no_seizure | 21 |
| seizure_freq_1ormore_daily | seizure_freq_more1per6mon_less1mon | 4 |
| currently_no_seizure | seizure_freq_unknown | 3 |
| seizure_freq_more1mon_less1week | seizure_freq_more1week_less1day | 2 |
| seizure_freq_more1week_less1day | seizure_freq_more1mon_less1week | 2 |
| seizure_freq_unknown | seizure_freq_1ormore_daily | 2 |
| seizure_freq_unknown | seizure_freq_more1mon_less1week | 2 |
| seizure_freq_more1mon_less1week | seizure_freq_1_per_mon | 2 |
| seizure_freq_1_per_mon | seizure_freq_more1week_less1day | 2 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_1ormore_daily | 1 |
| seizure_freq_unknown | seizure_freq_1_per_6mon | 1 |
| seizure_freq_unknown | seizure_freq_1_per_mon | 1 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
| 13843 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 13858 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 13889 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 3356 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 3528 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 4690 | wrong_frequency_bucket | unresolved_multiple | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 5534 | wrong_frequency_bucket | unresolved_multiple | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 5921 | wrong_frequency_bucket | frequency | frequency | seizure_freq_more1per6mon_less1mon | seizure_freq_1ormore_daily |
| 5974 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 6077 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 6094 | wrong_frequency_bucket | frequency | frequency | seizure_freq_more1mon_less1week | seizure_freq_more1week_less1day |
| 6131 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 6153 | wrong_frequency_bucket | frequency | frequency | seizure_freq_more1week_less1day | seizure_freq_more1mon_less1week |
| 6244 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 6501 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 6571 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 6987 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
| 7615 | wrong_frequency_bucket | frequency | frequency | seizure_freq_more1week_less1day | seizure_freq_1_per_6mon |
| 9496 | wrong_frequency_bucket | frequency | frequency | seizure_freq_more1per6mon_less1mon | seizure_freq_more1week_less1day |
| 9888 | wrong_frequency_bucket | unknown | seizure_free | seizure_freq_unknown | currently_no_seizure |
