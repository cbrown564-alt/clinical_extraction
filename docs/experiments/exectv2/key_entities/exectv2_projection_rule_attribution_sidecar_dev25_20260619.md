# ExECTv2 Projection Rule Attribution Sidecar

- Rows: `100`
- Sources: `experiments/exectv2_target_indicators_single_call_v039_live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl, experiments/exectv2_target_indicators_single_call_v040_reproject_v039live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl, experiments/exectv2_target_indicators_single_call_v041_reproject_v040live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl, experiments/exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`
- Attribution: Counts compare saved post-projection mentions with the same row's raw LLM output when available. They are warning-family attribution, not single-rule causal ablations, until switches are wired into the adapter.

## Fired Rules

| Rule | Entity | Portability | Default | Changed rows | Wrong-to-correct | Correct-to-wrong | Fidelity effect |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `dropped_inconsistent_zero_state_with_active_rate` | SeizureFrequency | `seizure_frequency` | True | 1 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `dropped_non_epilepsy_core` | Diagnosis | `clinical_epilepsy` | True | 13 | 9 | 0 | Diagnosis.concept_negation 0.6154->1.0000 |
| `dropped_unsupported_episode_frequency_anchor` | SeizureFrequency | `seizure_frequency` | True | 11 | 0 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.0000 |
| `normalized_diagnosis_text` | Diagnosis | `clinical_epilepsy` | True | 67 | 34 | 1 | Diagnosis.concept_negation 0.7223->0.9726 |
| `normalized_seizure_frequency_text` | SeizureFrequency | `seizure_frequency` | True | 8 | 5 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.8000 |
| `normalized_time_period` | SeizureFrequency | `general` | True | 48 | 29 | 0 | SeizureFrequency.active_rate_fidelity 0.1111->0.7647 |
| `projected_active_rate_seizure_type_to_diagnosis` | Diagnosis | `seizure_frequency` | True | 20 | 8 | 2 | Diagnosis.concept_negation 0.8705->0.9697 |
| `projected_christmas_point_to_month_date` | SeizureFrequency | `benchmark_format` | False | 1 | 0 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.0000 |
| `projected_controlled_context_to_infrequent_state` | SeizureFrequency | `clinical_epilepsy` | True | 2 | 2 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.0000 |
| `projected_controlled_drug_change_to_infrequent_state` | SeizureFrequency | `clinical_epilepsy` | True | 1 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.0000 |
| `projected_dated_diagnosis_context_to_sf` | SeizureFrequency | `clinical_epilepsy` | True | 4 | 2 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.4000 |
| `projected_diagnosis_context_to_controlled_sf_state` | SeizureFrequency | `clinical_epilepsy` | False | 1 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.0000 |
| `projected_diagnosis_context_to_frequent_myoclonic_jerks` | SeizureFrequency | `gan2026_specific` | False | 1 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_diagnosis_context_to_remote_last_seizures_state` | SeizureFrequency | `gan2026_specific` | False | 1 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.0000 |
| `projected_dropped_sf_to_diagnosis` | Diagnosis | `seizure_frequency` | True | 2 | 0 | 0 | Diagnosis.concept_negation 1.0000->1.0000 |
| `projected_eeg_context_to_mri_normal` | Investigations | `benchmark_format` | True | 4 | 0 | 0 | n/a |
| `projected_every_n_to_m_periods_to_one_event_rate` | SeizureFrequency | `benchmark_format` | True | 4 | 4 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_focal_diagnosis_context_to_sf_state` | SeizureFrequency | `clinical_epilepsy` | True | 1 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_four_since_last_clinic` | SeizureFrequency | `gan2026_specific` | False | 4 | 3 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_generic_yearly_rate_anchor` | SeizureFrequency | `gan2026_specific` | True | 4 | 4 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_header_parent_epilepsy` | Diagnosis | `clinical_epilepsy` | True | 8 | 4 | 0 | Diagnosis.concept_negation 0.8571->1.0000 |
| `projected_infrequent_context_state` | SeizureFrequency | `gan2026_specific` | False | 1 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_last_event_month_year_to_zero_since` | SeizureFrequency | `benchmark_format` | True | 4 | 4 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_march_range_count` | SeizureFrequency | `gan2026_specific` | True | 4 | 3 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_mri_context_to_eeg_result` | Investigations | `benchmark_format` | True | 4 | 0 | 0 | n/a |
| `projected_prescription_frequency_from_evidence` | Prescription | `general` | True | 2 | 0 | 0 | n/a |
| `projected_returned_context_to_increased_state` | SeizureFrequency | `clinical_epilepsy` | True | 2 | 2 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `projected_several_since_last_clinic` | SeizureFrequency | `gan2026_specific` | False | 4 | 2 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.6667 |
| `projected_sf_context_to_focal_diagnosis` | Diagnosis | `seizure_frequency` | True | 4 | 4 | 0 | Diagnosis.concept_negation 0.0000->1.0000 |
| `projected_typed_controlled_state_to_diagnosis` | Diagnosis | `seizure_frequency` | True | 2 | 2 | 0 | Diagnosis.concept_negation 0.5000->1.0000 |
| `projected_typed_seizure_frequency_to_diagnosis` | Diagnosis | `seizure_frequency` | True | 3 | 0 | 0 | Diagnosis.concept_negation 1.0000->1.0000 |
| `projected_vague_yearly_rate` | SeizureFrequency | `seizure_frequency` | True | 1 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `split_cluster_of_seizures_state` | SeizureFrequency | `seizure_frequency` | True | 4 | 4 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.6667 |
| `split_convulsive_zero_state` | SeizureFrequency | `seizure_frequency` | True | 4 | 1 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->1.0000 |
| `split_generalised_epilepsy_syndrome` | Diagnosis | `clinical_epilepsy` | True | 4 | 4 | 0 | Diagnosis.concept_negation 0.4444->1.0000 |
| `split_range_attribute` | SeizureFrequency | `general` | True | 12 | 9 | 0 | SeizureFrequency.active_rate_fidelity 0.0000->0.8333 |
| `split_secondary_gtc_to_tonic_clonic_diagnosis` | Diagnosis | `clinical_epilepsy` | True | 3 | 1 | 1 | Diagnosis.concept_negation 0.8000->1.0000 |
| `split_syndrome_to_tonic_clonic_diagnosis` | Diagnosis | `clinical_epilepsy` | True | 4 | 4 | 0 | Diagnosis.concept_negation 0.4444->1.0000 |
| `split_temporal_lobe_onset_to_focal_seizures` | Diagnosis | `clinical_epilepsy` | True | 3 | 2 | 0 | Diagnosis.concept_negation 0.8571->1.0000 |

## Unregistered Projection-Like Warnings

- `Diagnosis: dropped_unsupported_inferred_diagnosis: 'epilepsy'`
- `Diagnosis: dropped_unsupported_inferred_diagnosis: 'focal to bilateral tonic clonic seizure'`
- `Diagnosis: dropped_unsupported_inferred_diagnosis: 'reflex seizures'`
- `Diagnosis: dropped_unsupported_inferred_diagnosis: 'tonic clonic seizures'`
- `Investigations: dropped_empty_investigation_attrs: 'ECG'`
- `Investigations: dropped_illegal_attribute: 'ECTG_Performed'`
- `Investigations: dropped_illegal_attribute: 'ECTG_Results'`
- `Investigations: dropped_planned_investigation: 'EEG'`
- `Investigations: dropped_planned_investigation: 'MR brain and EEG'`
- `Investigations: dropped_planned_investigation: 'MR brain'`
- `Investigations: dropped_planned_investigation: 'MRI scan of the brain'`
- `Investigations: dropped_planned_investigation: 'MRI scan'`
- `Investigations: dropped_planned_investigation: 'MRI'`
- `Investigations: dropped_unsupported_eeg_confirmation: 'EEG recording'`
- `Investigations: dropped_unsupported_eeg_confirmation: 'EEG'`
- `Investigations: dropped_unsupported_investigation_evidence: 'MRI scan'`
- `Prescription: dropped_illegal_value: 'DoseUnit'='string copied or normalized from the letter' not in ['g', 'mg']`
- `Prescription: dropped_planned_prescription: 'Clobazam 10-20 mg as required'`
- `Prescription: dropped_planned_prescription: 'lamotrigine 75 mg twice a day'`
- `Prescription: dropped_planned_prescription: 'levetiracetam 250mg once-a-day'`
- `Prescription: dropped_planned_prescription: 'levetiracetam 750 mg twice daily'`
- `Prescription: normalized_attribute_value: 'DrugName'='Carbamazepine' -> 'carbamazepine'`
- `Prescription: normalized_attribute_value: 'DrugName'='Citalopram' -> 'citalopram'`
- `Prescription: normalized_attribute_value: 'DrugName'='Clobazam' -> 'clobazam'`
- `Prescription: normalized_attribute_value: 'DrugName'='Epilim' -> 'epilim'`
- `Prescription: normalized_attribute_value: 'DrugName'='Keppra' -> 'keppra'`
- `Prescription: normalized_attribute_value: 'DrugName'='Lamictal' -> 'lamictal'`
- `Prescription: normalized_attribute_value: 'DrugName'='Lamotrigine' -> 'lamotrigine'`
- `Prescription: normalized_attribute_value: 'DrugName'='Levetiracetam' -> 'levetiracetam'`
- `Prescription: normalized_attribute_value: 'DrugName'='Phenytoin' -> 'phenytoin'`
- `Prescription: normalized_attribute_value: 'DrugName'='Sodium Valproate' -> 'sodium valproate'`
- `Prescription: normalized_attribute_value: 'DrugName'='Tegretol' -> 'tegretol'`
- `Prescription: normalized_attribute_value: 'DrugName'='Topiramate' -> 'topiramate'`
- `Prescription: normalized_attribute_value: 'DrugName'='Zonisamide' -> 'zonisamide'`
- `Prescription: split_asymmetric_same_drug_dosing: 100/175 mg`
- `Prescription: split_asymmetric_same_drug_dosing: 300/600 mg`
- `Prescription: split_asymmetric_same_drug_dosing: 700/800 mg`
- `Prescription: split_asymmetric_same_drug_dosing: 750/500 mg`
- `SeizureFrequency: dropped_empty_sf_state_after_normalization: 'generalised tonic clonic seizures'`
- `SeizureFrequency: dropped_empty_sf_state_after_normalization: 'minor seizures'`
- `SeizureFrequency: dropped_generic_zero_state_for_typed_anchor: 'absence like seizures'`
- `SeizureFrequency: dropped_generic_zero_state_for_typed_anchor: 'focal seizures with altered awareness'`
- `SeizureFrequency: dropped_generic_zero_state_for_typed_anchor: 'generalised tonic clonic seizures'`
- `SeizureFrequency: dropped_illegal_attribute: 'MonthDateEnd'`
- `SeizureFrequency: dropped_illegal_value: 'PointInTime'='' not in ['Birthday', 'DrugChange', 'LastClinic', 'Last_Month', 'Last_Week', 'Last_Year', 'Surgery']`
- `SeizureFrequency: dropped_illegal_value: 'PointInTime'='August 2017' not in ['Birthday', 'DrugChange', 'LastClinic', 'Last_Month', 'Last_Week', 'Last_Year', 'Surgery']`
- `SeizureFrequency: dropped_illegal_value: 'PointInTime'='Christmas' not in ['Birthday', 'DrugChange', 'LastClinic', 'Last_Month', 'Last_Week', 'Last_Year', 'Surgery']`
- `SeizureFrequency: dropped_illegal_value: 'TimePeriod'='Unknown' not in ['Day', 'Month', 'Week', 'Year', 'days']`
- `SeizureFrequency: dropped_improvement_phrase_not_headline_state: 'focal seizures'`
- `SeizureFrequency: dropped_occasional_jerks_not_seizure_free: 'jerks with flashing lights'`
- `SeizureFrequency: dropped_previous_event_not_headline_frequency: 'Generalised tonic clonic seizure'`
- `SeizureFrequency: dropped_previous_event_not_headline_frequency: 'generalised tonic clonic seizure'`
- `SeizureFrequency: dropped_relative_prior_event_not_seizure_free: 'seizure'`
- `SeizureFrequency: dropped_relative_prior_event_not_seizure_free: 'seizures'`
- `SeizureFrequency: dropped_single_event_not_frequency_state: 'focal seizure'`
- `SeizureFrequency: dropped_single_event_not_frequency_state: 'single focal seizure'`
- `SeizureFrequency: dropped_unanchored_current_seizure_free_state: 'seizures'`
- `dropped_evidence_not_substring: text='Temporal lobe epilepsy'`
- `dropped_evidence_not_substring: text='epilepsy'`
- `dropped_evidence_not_substring: text='eslicarbazepine 800 mg once a day'`
- `dropped_evidence_not_substring: text='focal seizures'`
- `dropped_evidence_not_substring: text='generalised tonic clonic seizures'`
- `dropped_evidence_not_substring: text='minor seizures'`
- `dropped_evidence_not_substring: text='occipital lobe seizures'`
- `dropped_non_seizure_frequency_anchor: 'events'`
- `dropped_non_seizure_frequency_anchor: 'headaches'`
- `dropped_non_seizure_frequency_anchor: 'loss of consciousness'`
- `dropped_non_seizure_frequency_anchor: 'transient loss of consciousness'`
- `dropped_non_seizure_frequency_anchor: 'unusual thought'`
- `repaired_ellipsis_evidence: 'Clobazam 10-20 mg as required'`
- `repaired_evidence_case: 'blackouts'`
- `repaired_evidence_case: 'epilepsy'`
- `repaired_evidence_case: 'focal epilepsy'`
- `repaired_no_further_since_evidence: 'generalised tonic clonic seizures'`
- `repaired_prescription_frequency_synonym_evidence: 'carbamazepine 400 mg bd'`
- `repaired_whitespace_equivalent_evidence: 'Mild head injury'`
- `repaired_whitespace_equivalent_evidence: 'Temporal lobe epilepsy'`
- `repaired_whitespace_equivalent_evidence: 'bilateral convulsive seizures'`
- `repaired_whitespace_equivalent_evidence: 'eslicarbazepine 800 mg once a day'`
