# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.4400 | 0.4400 | 0.4400 | 0.4400 |
| macro | 0.5537 | 0.3987 | 0.4121 | 0.4400 |
| weighted | 0.5845 | 0.4400 | 0.4278 | 0.4400 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| missed_frequency_evidence | 242 |
| correct | 222 |
| scorer_correct_semantic_mismatch | 108 |
| wrong_frequency_bucket | 58 |
| missed_seizure_free_evidence | 56 |
| frequency_predicted_seizure_free | 34 |
| overpredicted_frequency | 30 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 424 |
| Rows with zero clinical candidates | 430 |
| Incorrect rows with zero clinical candidates | 296 |

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
| no_reference | 430 |
| frequency | 219 |
| seizure_free | 82 |
| unresolved_multiple | 10 |
| unknown | 9 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| header_fallback | 429 |
| clinical_evidence | 230 |
| other_text | 83 |
| medication_or_dose | 8 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| candidate_extraction | 298 |
| none | 222 |
| semantic_state_mapping | 108 |
| temporal_selection | 91 |
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
| ranges | 395 |
| medication_status | 371 |
| uncertainty | 256 |
| clusters | 245 |
| multiple_seizure_types | 229 |
| historical_current | 220 |
| negation | 210 |
| relative_dates | 185 |
| family_history | 70 |
| pnes_functional | 30 |
| lay_terminology | 25 |
| legacy_terminology | 4 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| seizure_freq_more1week_less1day | seizure_freq_unknown | 99 |
| currently_no_seizure | seizure_freq_unknown | 57 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 54 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_unknown | 45 |
| seizure_freq_1ormore_daily | seizure_freq_unknown | 21 |
| seizure_freq_1_per_mon | seizure_freq_unknown | 17 |
| seizure_freq_more1per6mon_less1mon | currently_no_seizure | 9 |
| seizure_freq_more1week_less1day | seizure_freq_1ormore_daily | 8 |
| seizure_freq_more1mon_less1week | currently_no_seizure | 8 |
| seizure_freq_unknown | currently_no_seizure | 7 |
| seizure_freq_1_per_week | seizure_freq_unknown | 6 |
| seizure_freq_more1mon_less1week | seizure_freq_1ormore_daily | 6 |

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
| 1694 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 1706 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 2023 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 2354 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 2366 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 2369 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 2425 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 2427 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_week | seizure_freq_unknown |
| 2513 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 2541 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
