# Gan 2026 V1 Validation Error Analysis

Date: 2026-05-31

This is a validation-split development artifact, not a held-out benchmark result.

CSV: `experiments/gan2026_v1_validation_error_rows_2026-05-31.csv`

## Metrics

Rows: 750

| Average | Precision | Recall | F1 | Accuracy |
| --- | ---: | ---: | ---: | ---: |
| micro | 0.8013 | 0.8013 | 0.8013 | 0.8013 |
| macro | 0.7604 | 0.8320 | 0.7715 | 0.8013 |
| weighted | 0.8163 | 0.8013 | 0.7890 | 0.8013 |

Evidence validity: 750 / 750

## Error Types

| Error type | Count |
| --- | ---: |
| correct | 507 |
| scorer_correct_semantic_mismatch | 94 |
| missed_seizure_free_evidence | 53 |
| wrong_frequency_bucket | 51 |
| overpredicted_frequency | 45 |

## Candidate Recall Diagnostics

| Measure | Count |
| --- | ---: |
| Clinical candidates extracted | 944 |
| Rows with zero clinical candidates | 172 |
| Incorrect rows with zero clinical candidates | 53 |

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
| frequency | 511 |
| no_reference | 172 |
| seizure_free | 45 |
| unresolved_multiple | 15 |
| unknown | 7 |

## Selected Evidence Types

| Evidence type | Count |
| --- | ---: |
| clinical_evidence | 428 |
| header_fallback | 172 |
| other_text | 140 |
| medication_or_dose | 10 |

## Likely Failed Operations

| Operation | Count |
| --- | ---: |
| none | 507 |
| semantic_state_mapping | 94 |
| temporal_selection | 72 |
| candidate_extraction | 53 |
| assertion_classification | 13 |
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
| ranges | 137 |
| medication_status | 127 |
| uncertainty | 95 |
| historical_current | 90 |
| negation | 78 |
| multiple_seizure_types | 66 |
| relative_dates | 65 |
| clusters | 62 |
| lay_terminology | 16 |
| family_history | 14 |
| pnes_functional | 13 |
| legacy_terminology | 3 |

## Top Incorrect Category Pairs

| Gold category | Prediction category | Count |
| --- | --- | ---: |
| currently_no_seizure | seizure_freq_unknown | 54 |
| seizure_freq_unknown | seizure_freq_more1per6mon_less1mon | 7 |
| seizure_freq_unknown | seizure_freq_more1mon_less1week | 6 |
| seizure_freq_more1mon_less1week | seizure_freq_1ormore_daily | 5 |
| seizure_freq_unknown | currently_no_seizure | 5 |
| seizure_freq_unknown | seizure_freq_1ormore_daily | 5 |
| seizure_freq_more1mon_less1week | seizure_freq_more1week_less1day | 4 |
| seizure_freq_1_per_mon | seizure_freq_more1week_less1day | 4 |
| seizure_freq_more1per6mon_less1mon | seizure_freq_1ormore_daily | 4 |
| currently_no_seizure | seizure_freq_more1week_less1day | 4 |
| currently_no_seizure | seizure_freq_more1per6mon_less1mon | 4 |
| seizure_freq_1ormore_daily | seizure_freq_more1per6mon_less1mon | 4 |

## First High-Priority Rows

| Row | Error type | Gold kind | Pred kind | Gold category | Pred category |
| ---: | --- | --- | --- | --- | --- |
| 2932 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 3137 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 4839 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 4842 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 4994 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5040 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5082 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5092 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5110 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5136 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5210 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5221 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5248 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 5406 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 7738 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 7785 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 7818 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 7872 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 8006 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
| 8144 | missed_seizure_free_evidence | seizure_free | no_reference | currently_no_seizure | seizure_freq_unknown |
