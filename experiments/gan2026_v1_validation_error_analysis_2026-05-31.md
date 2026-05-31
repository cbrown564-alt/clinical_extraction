# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.4667 | 0.4667 | 0.4667 | 0.4667 |
| macro | 0.5624 | 0.4180 | 0.4363 | 0.4667 |
| weighted | 0.5931 | 0.4667 | 0.4597 | 0.4667 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| correct | 249 |
| missed_frequency_evidence | 218 |
| scorer_correct_semantic_mismatch | 101 |
| wrong_frequency_bucket | 60 |
| missed_seizure_free_evidence | 56 |
| frequency_predicted_seizure_free | 35 |
| overpredicted_frequency | 31 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 473 |
| Rows with zero clinical candidates | 399 |
| Incorrect rows with zero clinical candidates | 272 |

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
| no_reference | 399 |
| frequency | 244 |
| seizure_free | 84 |
| unresolved_multiple | 14 |
| unknown | 9 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| header_fallback | 398 |
| clinical_evidence | 255 |
| other_text | 89 |
| medication_or_dose | 8 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| candidate_extraction | 274 |
| none | 249 |
| semantic_state_mapping | 101 |
| temporal_selection | 96 |
| assertion_classification | 19 |
| distractor_rejection | 8 |
| cluster_normalization | 1 |
| seizure_type_selection | 1 |
| range_normalization | 1 |

## Clinical Error Mode Flags

These flags are heuristic row slices, not mutually exclusive causal labels.

| Mode | Count |
| --- | ---: |
| ranges | 693 |
| medication_status | 648 |
| uncertainty | 441 |
| clusters | 407 |
| multiple_seizure_types | 400 |
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
| ranges | 378 |
| medication_status | 353 |
| uncertainty | 248 |
| clusters | 234 |
| multiple_seizure_types | 216 |
| historical_current | 211 |
| negation | 201 |
| relative_dates | 174 |
| family_history | 65 |
| pnes_functional | 29 |
| lay_terminology | 21 |
| legacy_terminology | 4 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| seizure_freq_more1week_less1day | seizure_freq_unknown | 85 |
| currently_no_seizure | seizure_freq_unknown | 57 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 51 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_unknown | 42 |
| seizure_freq_1ormore_daily | seizure_freq_unknown | 17 |
| seizure_freq_1_per_mon | seizure_freq_unknown | 16 |
| seizure_freq_more1mon_less1week | currently_no_seizure | 9 |
| seizure_freq_more1per6mon_less1mon | currently_no_seizure | 9 |
| seizure_freq_more1week_less1day | seizure_freq_1ormore_daily | 8 |
| seizure_freq_unknown | currently_no_seizure | 8 |
| seizure_freq_1_per_week | seizure_freq_unknown | 6 |
| seizure_freq_more1mon_less1week | seizure_freq_1ormore_daily | 6 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
| 978 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 1223 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1694 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1706 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 2369 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 2425 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 2427 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_week | seizure_freq_unknown |
| 2622 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 2628 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 2678 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 2762 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_mon | seizure_freq_unknown |
| 2822 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 2824 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 3224 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3242 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3261 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3262 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3297 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3325 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3623 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
