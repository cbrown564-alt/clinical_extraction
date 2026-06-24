# ExECTv2 Phase 5 Prescription Projection Pilot

- Source artifact: `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v05_dev140_gpt41mini_20260623.jsonl`
- Rows: `140`
- Attribution: LLM-only projection keeps the model-selected Prescription inventory fixed. Hybrid rescue and verifier-filtered actions are counted as separate candidate score lines and are not applied here.

## Projection Taxonomy

| Rule | Score line | Portability | LLM-only allowed |
| --- | --- | --- | --- |
| `prescription_drugname_cui_projection` | `llm_only_meaning_preserving_projection` | `benchmark_format` | True |
| `prescription_brand_generic_equivalence` | `llm_only_meaning_preserving_projection` | `benchmark_format` | True |
| `prescription_frequency_abbreviation_rendering` | `llm_only_meaning_preserving_projection` | `general` | True |
| `prescription_dose_unit_normalization` | `llm_only_meaning_preserving_projection` | `general` | True |
| `prescription_prn_frequency_rendering` | `llm_only_meaning_preserving_projection` | `clinical_epilepsy` | True |
| `prescription_missing_medication_rescue` | `hybrid_rescue` | `clinical_epilepsy` | False |
| `prescription_missing_dose_or_frequency_completion` | `hybrid_rescue` | `clinical_epilepsy` | False |
| `prescription_duplicate_regimen_collapse` | `verifier_filtered` | `benchmark_format` | False |
| `prescription_unsupported_medication_rejection` | `verifier_filtered` | `clinical_epilepsy` | False |

## Score Lines

| Score line | Status | Clinical headline F1 | Benchmark+CUI F1 | Drug+CUI F1 | Delta benchmark+CUI |
| --- | --- | ---: | ---: | ---: | ---: |
| `raw_model` | measured | 0.812 | 0.000 | 0.000 | 0.000 |
| `llm_only_meaning_preserving_projection` | measured | 0.814 | 0.180 | 0.907 | 0.180 |
| `hybrid_rescue` | not_applied | 0.000 | 0.000 | 0.000 | 0.000 |
| `verifier_filtered` | not_applied | 0.000 | 0.000 | 0.000 | 0.000 |

## Rule Counts

### Accepted LLM-only projection rules

| Rule | Count |
| --- | ---: |
| `prescription_brand_generic_equivalence` | 0 |
| `prescription_dose_unit_normalization` | 219 |
| `prescription_drugname_cui_projection` | 213 |
| `prescription_duplicate_regimen_collapse` | 0 |
| `prescription_frequency_abbreviation_rendering` | 190 |
| `prescription_missing_dose_or_frequency_completion` | 0 |
| `prescription_missing_medication_rescue` | 0 |
| `prescription_prn_frequency_rendering` | 1 |
| `prescription_unsupported_medication_rejection` | 0 |

## Boundary Counts

### Separated hybrid/verifier boundary rules

| Rule | Count |
| --- | ---: |
| `prescription_brand_generic_equivalence` | 0 |
| `prescription_dose_unit_normalization` | 0 |
| `prescription_drugname_cui_projection` | 0 |
| `prescription_duplicate_regimen_collapse` | 20 |
| `prescription_frequency_abbreviation_rendering` | 0 |
| `prescription_missing_dose_or_frequency_completion` | 8 |
| `prescription_missing_medication_rescue` | 21 |
| `prescription_prn_frequency_rendering` | 0 |
| `prescription_unsupported_medication_rejection` | 35 |

## Accepted Projection Examples

- `EA0002` `prescription_drugname_cui_projection`: {'letter_id': 'EA0002', 'rule_id': 'prescription_drugname_cui_projection', 'mention_text': 'carbamazepine', 'attributes': {'CUI': 'C0006949', 'CUIPhrase': 'carbamazepine', 'DoseUnit': 'mg', 'DrugDose': '400', 'DrugName': 'carbamazepine', 'Frequency': '2'}}
- `EA0002` `prescription_frequency_abbreviation_rendering`: {'letter_id': 'EA0002', 'rule_id': 'prescription_frequency_abbreviation_rendering', 'mention_text': 'carbamazepine', 'attributes': {'CUI': 'C0006949', 'CUIPhrase': 'carbamazepine', 'DoseUnit': 'mg', 'DrugDose': '400', 'DrugName': 'carbamazepine', 'Frequency': '2'}}
- `EA0002` `prescription_dose_unit_normalization`: {'letter_id': 'EA0002', 'rule_id': 'prescription_dose_unit_normalization', 'mention_text': 'carbamazepine', 'attributes': {'CUI': 'C0006949', 'CUIPhrase': 'carbamazepine', 'DoseUnit': 'mg', 'DrugDose': '400', 'DrugName': 'carbamazepine', 'Frequency': '2'}}
- `EA0002` `prescription_drugname_cui_projection`: {'letter_id': 'EA0002', 'rule_id': 'prescription_drugname_cui_projection', 'mention_text': 'Topiramate', 'attributes': {'CUI': 'C0076829', 'CUIPhrase': 'topiramate', 'DoseUnit': 'mg', 'DrugDose': '100', 'DrugName': 'topiramate', 'Frequency': '2'}}
- `EA0002` `prescription_frequency_abbreviation_rendering`: {'letter_id': 'EA0002', 'rule_id': 'prescription_frequency_abbreviation_rendering', 'mention_text': 'Topiramate', 'attributes': {'CUI': 'C0076829', 'CUIPhrase': 'topiramate', 'DoseUnit': 'mg', 'DrugDose': '100', 'DrugName': 'topiramate', 'Frequency': '2'}}
- `EA0002` `prescription_dose_unit_normalization`: {'letter_id': 'EA0002', 'rule_id': 'prescription_dose_unit_normalization', 'mention_text': 'Topiramate', 'attributes': {'CUI': 'C0076829', 'CUIPhrase': 'topiramate', 'DoseUnit': 'mg', 'DrugDose': '100', 'DrugName': 'topiramate', 'Frequency': '2'}}
- `EA0004` `prescription_drugname_cui_projection`: {'letter_id': 'EA0004', 'rule_id': 'prescription_drugname_cui_projection', 'mention_text': 'Lamotrigine', 'attributes': {'CUI': 'C0064636', 'CUIPhrase': 'lamotrigine', 'DoseUnit': 'mg', 'DrugDose': '125', 'DrugName': 'lamotrigine', 'Frequency': '2'}}
- `EA0004` `prescription_frequency_abbreviation_rendering`: {'letter_id': 'EA0004', 'rule_id': 'prescription_frequency_abbreviation_rendering', 'mention_text': 'Lamotrigine', 'attributes': {'CUI': 'C0064636', 'CUIPhrase': 'lamotrigine', 'DoseUnit': 'mg', 'DrugDose': '125', 'DrugName': 'lamotrigine', 'Frequency': '2'}}
- `EA0004` `prescription_dose_unit_normalization`: {'letter_id': 'EA0004', 'rule_id': 'prescription_dose_unit_normalization', 'mention_text': 'Lamotrigine', 'attributes': {'CUI': 'C0064636', 'CUIPhrase': 'lamotrigine', 'DoseUnit': 'mg', 'DrugDose': '125', 'DrugName': 'lamotrigine', 'Frequency': '2'}}
- `EA0005` `prescription_drugname_cui_projection`: {'letter_id': 'EA0005', 'rule_id': 'prescription_drugname_cui_projection', 'mention_text': 'sodium valproate', 'attributes': {'CUI': 'C0037567', 'CUIPhrase': 'sodium-valproate', 'DoseUnit': 'mg', 'DrugDose': '500', 'DrugName': 'sodium valproate', 'Frequency': '2'}}

## Boundary Violation Examples

- `EA0007` `prescription_duplicate_regimen_collapse`: {'letter_id': 'EA0007', 'rule_id': 'prescription_duplicate_regimen_collapse', 'detail': 'levetiracetam'}
- `EA0016` `prescription_unsupported_medication_rejection`: {'letter_id': 'EA0016', 'rule_id': 'prescription_unsupported_medication_rejection', 'detail': {'drug': 'levetiracetam', 'text': 'Levetiracetam'}}
- `EA0019` `prescription_missing_medication_rescue`: {'letter_id': 'EA0019', 'rule_id': 'prescription_missing_medication_rescue', 'detail': ('ordinary', 'sodium-valproate', '600', 'mg', '1')}
- `EA0019` `prescription_duplicate_regimen_collapse`: {'letter_id': 'EA0019', 'rule_id': 'prescription_duplicate_regimen_collapse', 'detail': 'sodium-valproate'}
- `EA0021` `prescription_duplicate_regimen_collapse`: {'letter_id': 'EA0021', 'rule_id': 'prescription_duplicate_regimen_collapse', 'detail': 'sodium-valproate'}
- `EA0024` `prescription_missing_dose_or_frequency_completion`: {'letter_id': 'EA0024', 'rule_id': 'prescription_missing_dose_or_frequency_completion', 'detail': {'drug': 'citalopram', 'text': 'Citalopram'}}
- `EA0024` `prescription_unsupported_medication_rejection`: {'letter_id': 'EA0024', 'rule_id': 'prescription_unsupported_medication_rejection', 'detail': {'drug': 'citalopram', 'text': 'Citalopram'}}
- `EA0024` `prescription_missing_dose_or_frequency_completion`: {'letter_id': 'EA0024', 'rule_id': 'prescription_missing_dose_or_frequency_completion', 'detail': {'drug': 'co-codamol', 'text': 'co-codamol'}}
- `EA0024` `prescription_unsupported_medication_rejection`: {'letter_id': 'EA0024', 'rule_id': 'prescription_unsupported_medication_rejection', 'detail': {'drug': 'co-codamol', 'text': 'co-codamol'}}
- `EA0024` `prescription_missing_dose_or_frequency_completion`: {'letter_id': 'EA0024', 'rule_id': 'prescription_missing_dose_or_frequency_completion', 'detail': {'drug': 'lansoprazole', 'text': 'lansoprazole'}}
