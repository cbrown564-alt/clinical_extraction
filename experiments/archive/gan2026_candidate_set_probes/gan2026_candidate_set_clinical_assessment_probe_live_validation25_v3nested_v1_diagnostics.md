# Gan 2026 Clinical Assessment Diagnostics

Validation25 clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v1_diagnostics.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v1_diagnostics.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v3nested_v1.jsonl`

## Summary

- Rows: 25
- Clinical assessment rows: 25
- Missing assessment rows: 0
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 0

## Assessment Kinds

- `cluster_frequency`: 2
- `frequency_rate`: 23

## Aggregation Policies

- `cluster_axis`: 1
- `primary_with_context`: 6
- `single_fact`: 18

## Primary Candidate Counts

- `1`: 25

## Diagnostic Flags

- None.

## Selector Comparisons

### Minimal Selector V2
- `assessment_primary_subset`: 2
- `different`: 4
- `same`: 19

### Rich Selector V0

- `assessment_primary_subset`: 2
- `different`: 2
- `same`: 21

## Inspection Examples

### Flagged Rows

- None.

### Multi Primary Rows

- None.

### Context Leak Rows

- None.

### Minimal Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:1'], supporting ['llm:79:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports combined generalized and focal epilepsy with seizure frequency ≤ 6 to 7 per year, typically clustering around travel-related sleep loss and jet lag. No injuries or hospital admissions. Current medications well tolerated. Clobazam used PRN during travel. Adherence reinforced. No immediate further investigations required.
- 218: kind `frequency_rate`, policy `single_fact`, primary ['llm:218:2'], supporting ['llm:218:1'], rejected [], flags [], minimal selector `different`, rich selector `same`. Summary: The patient reports improved seizure control with seizures now occurring approximately every 3 weeks, compared to prior frequency of once every 2 to 3 days. No injuries or emergency attendances noted. Current regimen and lifestyle adjustments are effective and well tolerated.
- 338: kind `frequency_rate`, policy `primary_with_context`, primary ['det:338:1'], supporting ['llm:338:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `different`. Summary: The patient has experienced many convulsions in the past month, with events clustering after eastbound flights and consecutive nights of restricted sleep. The plan focuses on optimizing sleep hygiene and medication timing to reduce breakthrough seizures.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, both nocturnally and during wakefulness, with variable clustering. This represents a clinical deterioration compared to prior months (June and August) when seizure frequency was lower. The patient is on stable polytherapy but reports worsening control and adverse effects impacting function.
- 466: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:466:1'], supporting ['llm:466:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient experiences 21 to 28 focal impaired awareness seizures per month, typically brief and with post-ictal fatigue. Occasional seizure clusters occur around significant sleep disruption but are not quantified separately in frequency burden. No generalized tonic-clonic seizures reported in past six months.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:1'], supporting ['llm:598:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports stable focal epilepsy with impaired awareness seizures occurring approximately once every eight months over the past 16 months, consistent with seizure diary. No secondary generalization or worsening noted. Triggers include sleep deprivation. Current antiepileptic therapy is effective and well tolerated.

### Rich Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:1'], supporting ['llm:79:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports combined generalized and focal epilepsy with seizure frequency ≤ 6 to 7 per year, typically clustering around travel-related sleep loss and jet lag. No injuries or hospital admissions. Current medications well tolerated. Clobazam used PRN during travel. Adherence reinforced. No immediate further investigations required.
- 338: kind `frequency_rate`, policy `primary_with_context`, primary ['det:338:1'], supporting ['llm:338:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `different`. Summary: The patient has experienced many convulsions in the past month, with events clustering after eastbound flights and consecutive nights of restricted sleep. The plan focuses on optimizing sleep hygiene and medication timing to reduce breakthrough seizures.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, both nocturnally and during wakefulness, with variable clustering. This represents a clinical deterioration compared to prior months (June and August) when seizure frequency was lower. The patient is on stable polytherapy but reports worsening control and adverse effects impacting function.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:1'], supporting ['llm:598:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports stable focal epilepsy with impaired awareness seizures occurring approximately once every eight months over the past 16 months, consistent with seizure diary. No secondary generalization or worsening noted. Triggers include sleep deprivation. Current antiepileptic therapy is effective and well tolerated.
