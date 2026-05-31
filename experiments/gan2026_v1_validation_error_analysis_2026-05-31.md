# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.3893 | 0.3893 | 0.3893 | 0.3893 |
| macro | 0.4989 | 0.3441 | 0.3445 | 0.3893 |
| weighted | 0.5414 | 0.3893 | 0.3642 | 0.3893 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| missed_frequency_evidence | 267 |
| correct | 182 |
| scorer_correct_semantic_mismatch | 110 |
| missed_seizure_free_evidence | 80 |
| wrong_frequency_bucket | 56 |
| overpredicted_frequency | 30 |
| frequency_predicted_seizure_free | 25 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 346 |
| Rows with zero clinical candidates | 480 |
| Incorrect rows with zero clinical candidates | 344 |

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
| no_reference | 480 |
| frequency | 203 |
| seizure_free | 46 |
| unknown | 11 |
| unresolved_multiple | 10 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| header_fallback | 479 |
| clinical_evidence | 189 |
| other_text | 74 |
| medication_or_dose | 8 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| candidate_extraction | 347 |
| none | 182 |
| semantic_state_mapping | 110 |
| temporal_selection | 80 |
| assertion_classification | 19 |
| distractor_rejection | 8 |
| seizure_type_selection | 2 |
| cluster_normalization | 1 |
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
| ranges | 427 |
| medication_status | 402 |
| uncertainty | 278 |
| clusters | 254 |
| multiple_seizure_types | 247 |
| historical_current | 239 |
| negation | 238 |
| relative_dates | 208 |
| family_history | 71 |
| pnes_functional | 31 |
| lay_terminology | 30 |
| legacy_terminology | 8 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| seizure_freq_more1week_less1day | seizure_freq_unknown | 103 |
| currently_no_seizure | seizure_freq_unknown | 81 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 61 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_unknown | 45 |
| seizure_freq_1ormore_daily | seizure_freq_unknown | 30 |
| seizure_freq_1_per_mon | seizure_freq_unknown | 19 |
| seizure_freq_more1per6mon_less1mon | currently_no_seizure | 9 |
| seizure_freq_1_per_week | seizure_freq_unknown | 8 |
| seizure_freq_more1week_less1day | seizure_freq_1ormore_daily | 8 |
| seizure_freq_more1mon_less1week | currently_no_seizure | 8 |
| seizure_freq_more1mon_less1week | seizure_freq_1ormore_daily | 6 |
| seizure_freq_unknown | seizure_freq_more1per6mon_less1mon | 5 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
| 531 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 725 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 731 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 978 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 1165 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1171 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1207 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1223 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1249 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1357 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 1454 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 1486 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 1573 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 1591 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1596 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 1597 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1636 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1640 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1694 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1706 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
