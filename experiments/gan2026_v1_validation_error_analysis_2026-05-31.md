# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.6293 | 0.6293 | 0.6293 | 0.6293 |
| macro | 0.6253 | 0.6066 | 0.5879 | 0.6293 |
| weighted | 0.6845 | 0.6293 | 0.6282 | 0.6293 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| correct | 377 |
| missed_frequency_evidence | 101 |
| scorer_correct_semantic_mismatch | 95 |
| wrong_frequency_bucket | 70 |
| missed_seizure_free_evidence | 53 |
| overpredicted_frequency | 43 |
| frequency_predicted_seizure_free | 11 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 807 |
| Rows with zero clinical candidates | 274 |
| Incorrect rows with zero clinical candidates | 154 |

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
| frequency | 397 |
| no_reference | 274 |
| seizure_free | 57 |
| unresolved_multiple | 15 |
| unknown | 7 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| clinical_evidence | 331 |
| header_fallback | 274 |
| other_text | 135 |
| medication_or_dose | 10 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| none | 377 |
| candidate_extraction | 154 |
| semantic_state_mapping | 95 |
| temporal_selection | 91 |
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
| ranges | 260 |
| medication_status | 242 |
| uncertainty | 176 |
| historical_current | 150 |
| negation | 144 |
| multiple_seizure_types | 141 |
| clusters | 135 |
| relative_dates | 105 |
| family_history | 52 |
| lay_terminology | 19 |
| pnes_functional | 18 |
| legacy_terminology | 3 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| currently_no_seizure | seizure_freq_unknown | 54 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 33 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_unknown | 29 |
| seizure_freq_more1week_less1day | seizure_freq_unknown | 23 |
| seizure_freq_more1week_less1day | seizure_freq_1ormore_daily | 9 |
| seizure_freq_1_per_mon | seizure_freq_unknown | 9 |
| seizure_freq_unknown | seizure_freq_more1per6mon_less1mon | 7 |
| seizure_freq_unknown | seizure_freq_more1mon_less1week | 6 |
| seizure_freq_more1mon_less1week | seizure_freq_1ormore_daily | 6 |
| seizure_freq_more1mon_less1week | currently_no_seizure | 6 |
| seizure_freq_more1mon_less1week | seizure_freq_more1week_less1day | 5 |
| seizure_freq_unknown | currently_no_seizure | 5 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
| 12218 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 12236 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 12314 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 12788 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 12810 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 12827 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_mon | seizure_freq_unknown |
| 12835 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_week | seizure_freq_unknown |
| 12877 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 12901 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 12949 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 12979 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 13008 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_week | seizure_freq_unknown |
| 13114 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_yr | seizure_freq_unknown |
| 13267 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 13290 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1per6mon_less1mon | seizure_freq_unknown |
| 13627 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 13711 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 13721 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 13732 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 14332 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
