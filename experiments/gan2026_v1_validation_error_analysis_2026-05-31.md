# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.5813 | 0.5813 | 0.5813 | 0.5813 |
| macro | 0.5888 | 0.5491 | 0.5395 | 0.5813 |
| weighted | 0.6470 | 0.5813 | 0.5829 | 0.5813 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| correct | 343 |
| missed_frequency_evidence | 126 |
| scorer_correct_semantic_mismatch | 93 |
| wrong_frequency_bucket | 74 |
| missed_seizure_free_evidence | 51 |
| overpredicted_frequency | 41 |
| frequency_predicted_seizure_free | 22 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 769 |
| Rows with zero clinical candidates | 293 |
| Incorrect rows with zero clinical candidates | 175 |

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
| frequency | 359 |
| no_reference | 293 |
| seizure_free | 74 |
| unresolved_multiple | 15 |
| unknown | 9 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| clinical_evidence | 320 |
| header_fallback | 292 |
| other_text | 130 |
| medication_or_dose | 8 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| none | 343 |
| candidate_extraction | 177 |
| temporal_selection | 104 |
| semantic_state_mapping | 93 |
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
| ranges | 297 |
| medication_status | 277 |
| uncertainty | 202 |
| historical_current | 172 |
| clusters | 169 |
| multiple_seizure_types | 165 |
| negation | 163 |
| relative_dates | 132 |
| family_history | 57 |
| lay_terminology | 19 |
| pnes_functional | 18 |
| legacy_terminology | 3 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| currently_no_seizure | seizure_freq_unknown | 52 |
| seizure_freq_more1week_less1day | seizure_freq_unknown | 45 |
| seizure_freq_more1mon_less1week | seizure_freq_unknown | 35 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_unknown | 29 |
| seizure_freq_more1week_less1day | seizure_freq_1ormore_daily | 9 |
| seizure_freq_more1per6mon_less1mon | currently_no_seizure | 9 |
| seizure_freq_1_per_mon | seizure_freq_unknown | 8 |
| seizure_freq_more1mon_less1week | currently_no_seizure | 8 |
| seizure_freq_unknown | seizure_freq_more1per6mon_less1mon | 7 |
| seizure_freq_unknown | currently_no_seizure | 7 |
| seizure_freq_unknown | seizure_freq_more1mon_less1week | 6 |
| seizure_freq_more1mon_less1week | seizure_freq_1ormore_daily | 6 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
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
| 10487 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10517 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1ormore_daily | seizure_freq_unknown |
| 10630 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10673 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1mon_less1week | seizure_freq_unknown |
| 10807 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_week | seizure_freq_unknown |
| 10829 | missed_frequency_evidence | frequency | no_reference | seizure_freq_1_per_week | seizure_freq_unknown |
| 10862 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10865 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
| 10873 | missed_frequency_evidence | frequency | no_reference | seizure_freq_more1week_less1day | seizure_freq_unknown |
