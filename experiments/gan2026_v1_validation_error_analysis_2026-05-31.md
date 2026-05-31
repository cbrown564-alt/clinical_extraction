# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.4920 | 0.4920 | 0.4920 | 0.4920 |
| macro | 0.5540 | 0.4494 | 0.4534 | 0.4920 |
| weighted | 0.5999 | 0.4920 | 0.4852 | 0.4920 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| correct | 270 |
| missed_frequency_evidence | 199 |
| scorer_correct_semantic_mismatch | 99 |
| wrong_frequency_bucket | 66 |
| missed_seizure_free_evidence | 56 |
| overpredicted_frequency | 33 |
| frequency_predicted_seizure_free | 27 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 513 |
| Rows with zero clinical candidates | 378 |
| Incorrect rows with zero clinical candidates | 253 |

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
| no_reference | 378 |
| frequency | 273 |
| seizure_free | 76 |
| unresolved_multiple | 14 |
| unknown | 9 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| header_fallback | 377 |
| clinical_evidence | 275 |
| other_text | 90 |
| medication_or_dose | 8 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| none | 270 |
| candidate_extraction | 255 |
| semantic_state_mapping | 99 |
| temporal_selection | 95 |
| assertion_classification | 20 |
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
| ranges | 360 |
| medication_status | 337 |
| uncertainty | 238 |
| clusters | 217 |
| historical_current | 204 |
| multiple_seizure_types | 201 |
| negation | 189 |
| relative_dates | 160 |
| family_history | 65 |
| pnes_functional | 25 |
| lay_terminology | 19 |
| legacy_terminology | 4 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| seizure_freq_more1week_less1day | seizure_freq_unknown | 76 |
| currently_no_seizure | seizure_freq_unknown | 57 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 48 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_unknown | 41 |
| seizure_freq_1_per_mon | seizure_freq_unknown | 16 |
| seizure_freq_1ormore_daily | seizure_freq_unknown | 12 |
| seizure_freq_more1mon_less1week | currently_no_seizure | 9 |
| seizure_freq_more1per6mon_less1mon | currently_no_seizure | 9 |
| seizure_freq_more1week_less1day | seizure_freq_1ormore_daily | 8 |
| seizure_freq_unknown | currently_no_seizure | 8 |
| seizure_freq_1_per_week | seizure_freq_unknown | 6 |
| seizure_freq_more1mon_less1week | seizure_freq_1ormore_daily | 6 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
| 2425 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 2427 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_week | seizure_freq_unknown |
| 2678 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 2762 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_mon | seizure_freq_unknown |
| 3224 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3297 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3325 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3623 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 3681 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3682 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3710 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3791 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 3801 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3806 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3846 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 3849 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 3889 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 3892 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 3940 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 3949 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
