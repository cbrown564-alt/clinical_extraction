# Gan 2026 Clinical Assessment Diagnostics

Validation25 clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v0_diagnostics.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_v3nested_v0_diagnostics.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v3nested_v0.jsonl`

## Summary

- Rows: 25
- Clinical assessment rows: 25
- Missing assessment rows: 0
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 1

## Assessment Kinds

- `cluster_frequency`: 3
- `frequency_rate`: 22

## Aggregation Policies

- `cluster_axis`: 1
- `primary_with_context`: 4
- `single_fact`: 20

## Primary Candidate Counts

- `1`: 24
- `2`: 1

## Diagnostic Flags

- `cluster_context_leak_in_frequency_burden`: 1
- `historical_context_phrase_in_burden`: 1

## Selector Comparisons

### Minimal Selector V2
- `assessment_primary_subset`: 1
- `different`: 4
- `same`: 20

### Rich Selector V0

- `assessment_primary_subset`: 2
- `assessment_primary_superset`: 1
- `different`: 1
- `same`: 21

## Inspection Examples

### Flagged Rows

- 409: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:409:2'], supporting ['llm:409:1'], rejected [], flags ['cluster_context_leak_in_frequency_burden', 'historical_context_phrase_in_burden'], minimal selector `same`, rich selector `same`. Summary: Seizure frequency has markedly improved to ≤ once per month with brief focal impaired awareness episodes; previously experienced weekly clusters of three events.

### Multi Primary Rows

- 338: kind `cluster_frequency`, policy `cluster_axis`, primary ['det:338:1', 'llm:338:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: Patient experiences many convulsions in the past month, with seizures clustering after eastbound flights and nights of restricted sleep.

### Context Leak Rows

- 409: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:409:2'], supporting ['llm:409:1'], rejected [], flags ['cluster_context_leak_in_frequency_burden', 'historical_context_phrase_in_burden'], minimal selector `same`, rich selector `same`. Summary: Seizure frequency has markedly improved to ≤ once per month with brief focal impaired awareness episodes; previously experienced weekly clusters of three events.

### Minimal Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:1'], supporting ['llm:79:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports a current seizure frequency of up to 6 to 7 seizures per year, consistent across note references, with no recent hospital admissions or injuries.
- 218: kind `frequency_rate`, policy `single_fact`, primary ['llm:218:2'], supporting ['llm:218:1'], rejected [], flags [], minimal selector `different`, rich selector `same`. Summary: Seizure frequency has improved to approximately one seizure every 3 weeks over the past three months, indicating better control with current treatment and lifestyle adjustments.
- 446: kind `frequency_rate`, policy `single_fact`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, indicating a clinical worsening compared to prior months despite medication adherence.
- 466: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:466:1'], supporting ['llm:466:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: Patient experiences 21 to 28 focal impaired awareness seizures per month, with occasional clusters triggered by sleep disruption.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:1'], supporting ['llm:598:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports stable seizure frequency averaging one seizure every eight months, consistent with clinical history and seizure diary.

### Rich Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:1'], supporting ['llm:79:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports a current seizure frequency of up to 6 to 7 seizures per year, consistent across note references, with no recent hospital admissions or injuries.
- 338: kind `cluster_frequency`, policy `cluster_axis`, primary ['det:338:1', 'llm:338:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: Patient experiences many convulsions in the past month, with seizures clustering after eastbound flights and nights of restricted sleep.
- 446: kind `frequency_rate`, policy `single_fact`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, indicating a clinical worsening compared to prior months despite medication adherence.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:1'], supporting ['llm:598:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports stable seizure frequency averaging one seizure every eight months, consistent with clinical history and seizure diary.
