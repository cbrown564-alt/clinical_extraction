# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.5733 | 0.5733 | 0.5733 | 0.5733 |
| macro | 0.5941 | 0.5415 | 0.5357 | 0.5733 |
| weighted | 0.6488 | 0.5733 | 0.5744 | 0.5733 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| correct | 334 |
| missed_frequency_evidence | 137 |
| scorer_correct_semantic_mismatch | 96 |
| wrong_frequency_bucket | 71 |
| missed_seizure_free_evidence | 53 |
| overpredicted_frequency | 37 |
| frequency_predicted_seizure_free | 22 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 710 |
| Rows with zero clinical candidates | 309 |
| Incorrect rows with zero clinical candidates | 188 |

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
| frequency | 344 |
| no_reference | 309 |
| seizure_free | 73 |
| unresolved_multiple | 15 |
| unknown | 9 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| header_fallback | 308 |
| clinical_evidence | 305 |
| other_text | 129 |
| medication_or_dose | 8 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| none | 334 |
| candidate_extraction | 190 |
| temporal_selection | 97 |
| semantic_state_mapping | 96 |
| assertion_classification | 22 |
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
| ranges | 303 |
| medication_status | 281 |
| uncertainty | 204 |
| historical_current | 175 |
| clusters | 170 |
| negation | 167 |
| multiple_seizure_types | 165 |
| relative_dates | 136 |
| family_history | 56 |
| pnes_functional | 20 |
| lay_terminology | 19 |
| legacy_terminology | 3 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| currently_no_seizure | seizure_freq_unknown | 54 |
| seizure_freq_more1week_less1day | seizure_freq_unknown | 52 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 36 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_unknown | 30 |
| seizure_freq_1_per_mon | seizure_freq_unknown | 9 |
| seizure_freq_more1per6mon_less1mon | currently_no_seizure | 9 |
| seizure_freq_more1week_less1day | seizure_freq_1ormore_daily | 8 |
| seizure_freq_unknown | currently_no_seizure | 8 |
| seizure_freq_more1mon_less1week | currently_no_seizure | 8 |
| seizure_freq_more1mon_less1week | seizure_freq_1ormore_daily | 6 |
| seizure_freq_unknown | seizure_freq_more1per6mon_less1mon | 6 |
| seizure_freq_1ormore_daily | seizure_freq_unknown | 6 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
| 6509 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 6701 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 6952 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 7167 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 7196 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 7275 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_mon | seizure_freq_unknown |
| 7401 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 9002 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 9287 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 9299 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 9300 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10003 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10047 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 10063 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 10097 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10237 | missed_frequency_evidence | frequency | unknown | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10245 | missed_frequency_evidence | frequency | unknown | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10383 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10434 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10481 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
