# Gan 2026 Clinical Assessment Diagnostics

Validation25 clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_v0_diagnostics.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation25_gpt41mini_v0.jsonl`

## Summary

- Rows: 25
- Clinical assessment rows: 25
- Missing assessment rows: 0
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 9

## Assessment Kinds

- `cluster_frequency`: 2
- `frequency_rate`: 21
- `unknown_frequency`: 2

## Aggregation Policies

- `primary_with_context`: 10
- `single_fact`: 15

## Primary Candidate Counts

- `1`: 17
- `2`: 6
- `3`: 1
- `4`: 1

## Diagnostic Flags

- `cluster_context_leak_in_frequency_burden`: 1
- `historical_context_phrase_in_burden`: 1
- `multi_primary_nonadditive_policy`: 8
- `seizure_free_context_leak_in_frequency_burden`: 1
- `single_fact_multiple_primary_candidates`: 5

## Selector Comparisons

### Minimal Selector V2
- `assessment_primary_subset`: 2
- `assessment_primary_superset`: 8
- `different`: 4
- `same`: 11

### Rich Selector V0

- `assessment_primary_subset`: 1
- `assessment_primary_superset`: 8
- `different`: 5
- `same`: 11

## Inspection Examples

### Flagged Rows

- 10: kind `frequency_rate`, policy `primary_with_context`, primary ['det:10:1', 'llm:10:2'], supporting ['llm:10:1'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient experiences up to four brief seizures daily with a fluctuating pattern; frequency based on accommodation logs and patient report.
- 79: kind `frequency_rate`, policy `single_fact`, primary ['det:79:1', 'llm:79:1', 'llm:79:2'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports seizure frequency of up to 6 to 7 seizures per year, consistent across multiple statements.
- 182: kind `frequency_rate`, policy `single_fact`, primary ['det:182:1', 'det:182:2', 'det:182:3', 'llm:182:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient experiences seizures approximately every 2 days as consistently reported by carer and seizure logs.
- 198: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:198:1'], supporting ['llm:198:2'], rejected ['det:198:1', 'det:198:2'], flags ['seizure_free_context_leak_in_frequency_burden'], minimal selector `same`, rich selector `same`. Summary: Patient continues to have seizures approximately every 4 weeks despite medication, with the last event 10 days ago without complications.
- 243: kind `frequency_rate`, policy `single_fact`, primary ['det:243:1', 'llm:243:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient has generalized seizures occurring approximately every four months with low seizure burden.
- 409: kind `frequency_rate`, policy `primary_with_context`, primary ['det:409:1', 'llm:409:2'], supporting ['llm:409:1'], rejected [], flags ['multi_primary_nonadditive_policy', 'cluster_context_leak_in_frequency_burden', 'historical_context_phrase_in_burden'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Seizure frequency has markedly improved to approximately once per month with brief focal impaired awareness episodes; previously occurred as weekly clusters of three events.
- 419: kind `frequency_rate`, policy `single_fact`, primary ['det:419:1', 'llm:419:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports a stable seizure frequency of approximately twice per year with no current antiseizure medication.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1', 'llm:446:3'], supporting ['llm:446:1', 'llm:446:2'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient currently experiences seizures up to twice per week, both nocturnally and during wakefulness, indicating clinical worsening compared to prior months with fewer events.
- 467: kind `frequency_rate`, policy `single_fact`, primary ['det:467:1', 'llm:467:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports a stable frequency of 9 focal seizures per month over the last eight weeks.

### Multi Primary Rows

- 10: kind `frequency_rate`, policy `primary_with_context`, primary ['det:10:1', 'llm:10:2'], supporting ['llm:10:1'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient experiences up to four brief seizures daily with a fluctuating pattern; frequency based on accommodation logs and patient report.
- 79: kind `frequency_rate`, policy `single_fact`, primary ['det:79:1', 'llm:79:1', 'llm:79:2'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports seizure frequency of up to 6 to 7 seizures per year, consistent across multiple statements.
- 182: kind `frequency_rate`, policy `single_fact`, primary ['det:182:1', 'det:182:2', 'det:182:3', 'llm:182:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient experiences seizures approximately every 2 days as consistently reported by carer and seizure logs.
- 243: kind `frequency_rate`, policy `single_fact`, primary ['det:243:1', 'llm:243:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient has generalized seizures occurring approximately every four months with low seizure burden.
- 409: kind `frequency_rate`, policy `primary_with_context`, primary ['det:409:1', 'llm:409:2'], supporting ['llm:409:1'], rejected [], flags ['multi_primary_nonadditive_policy', 'cluster_context_leak_in_frequency_burden', 'historical_context_phrase_in_burden'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Seizure frequency has markedly improved to approximately once per month with brief focal impaired awareness episodes; previously occurred as weekly clusters of three events.
- 419: kind `frequency_rate`, policy `single_fact`, primary ['det:419:1', 'llm:419:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports a stable seizure frequency of approximately twice per year with no current antiseizure medication.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1', 'llm:446:3'], supporting ['llm:446:1', 'llm:446:2'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient currently experiences seizures up to twice per week, both nocturnally and during wakefulness, indicating clinical worsening compared to prior months with fewer events.
- 467: kind `frequency_rate`, policy `single_fact`, primary ['det:467:1', 'llm:467:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports a stable frequency of 9 focal seizures per month over the last eight weeks.

### Context Leak Rows

- 198: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:198:1'], supporting ['llm:198:2'], rejected ['det:198:1', 'det:198:2'], flags ['seizure_free_context_leak_in_frequency_burden'], minimal selector `same`, rich selector `same`. Summary: Patient continues to have seizures approximately every 4 weeks despite medication, with the last event 10 days ago without complications.
- 409: kind `frequency_rate`, policy `primary_with_context`, primary ['det:409:1', 'llm:409:2'], supporting ['llm:409:1'], rejected [], flags ['multi_primary_nonadditive_policy', 'cluster_context_leak_in_frequency_burden', 'historical_context_phrase_in_burden'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Seizure frequency has markedly improved to approximately once per month with brief focal impaired awareness episodes; previously occurred as weekly clusters of three events.

### Minimal Selector Differences

- 10: kind `frequency_rate`, policy `primary_with_context`, primary ['det:10:1', 'llm:10:2'], supporting ['llm:10:1'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient experiences up to four brief seizures daily with a fluctuating pattern; frequency based on accommodation logs and patient report.
- 79: kind `frequency_rate`, policy `single_fact`, primary ['det:79:1', 'llm:79:1', 'llm:79:2'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports seizure frequency of up to 6 to 7 seizures per year, consistent across multiple statements.
- 103: kind `frequency_rate`, policy `primary_with_context`, primary ['det:103:1'], supporting ['llm:103:2'], rejected ['llm:103:1'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences two to four seizures per year, representing a marked improvement from prior seizures every 1 to 2 weeks.
- 128: kind `frequency_rate`, policy `primary_with_context`, primary ['det:128:1'], supporting ['llm:128:1'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: Patient experiences approximately 17 seizures per month, often clustering around sleep deprivation and stress periods.
- 182: kind `frequency_rate`, policy `single_fact`, primary ['det:182:1', 'det:182:2', 'det:182:3', 'llm:182:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient experiences seizures approximately every 2 days as consistently reported by carer and seizure logs.
- 243: kind `frequency_rate`, policy `single_fact`, primary ['det:243:1', 'llm:243:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient has generalized seizures occurring approximately every four months with low seizure burden.
- 338: kind `unknown_frequency`, policy `primary_with_context`, primary ['det:338:1'], supporting ['llm:338:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `different`. Summary: Patient has many convulsions in the past month, with events clustering after eastbound flights and sleep restriction; seizure frequency is high but exact counts are not specified.
- 409: kind `frequency_rate`, policy `primary_with_context`, primary ['det:409:1', 'llm:409:2'], supporting ['llm:409:1'], rejected [], flags ['multi_primary_nonadditive_policy', 'cluster_context_leak_in_frequency_burden', 'historical_context_phrase_in_burden'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Seizure frequency has markedly improved to approximately once per month with brief focal impaired awareness episodes; previously occurred as weekly clusters of three events.
- 419: kind `frequency_rate`, policy `single_fact`, primary ['det:419:1', 'llm:419:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports a stable seizure frequency of approximately twice per year with no current antiseizure medication.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1', 'llm:446:3'], supporting ['llm:446:1', 'llm:446:2'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient currently experiences seizures up to twice per week, both nocturnally and during wakefulness, indicating clinical worsening compared to prior months with fewer events.
- 466: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:466:1'], supporting ['llm:466:2'], rejected ['det:466:2'], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient experiences 21 to 28 focal impaired awareness seizures per month, with occasional clusters related to sleep disruption.
- 467: kind `frequency_rate`, policy `single_fact`, primary ['det:467:1', 'llm:467:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports a stable frequency of 9 focal seizures per month over the last eight weeks.

### Rich Selector Differences

- 10: kind `frequency_rate`, policy `primary_with_context`, primary ['det:10:1', 'llm:10:2'], supporting ['llm:10:1'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient experiences up to four brief seizures daily with a fluctuating pattern; frequency based on accommodation logs and patient report.
- 79: kind `frequency_rate`, policy `single_fact`, primary ['det:79:1', 'llm:79:1', 'llm:79:2'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports seizure frequency of up to 6 to 7 seizures per year, consistent across multiple statements.
- 103: kind `frequency_rate`, policy `primary_with_context`, primary ['det:103:1'], supporting ['llm:103:2'], rejected ['llm:103:1'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences two to four seizures per year, representing a marked improvement from prior seizures every 1 to 2 weeks.
- 128: kind `frequency_rate`, policy `primary_with_context`, primary ['det:128:1'], supporting ['llm:128:1'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: Patient experiences approximately 17 seizures per month, often clustering around sleep deprivation and stress periods.
- 182: kind `frequency_rate`, policy `single_fact`, primary ['det:182:1', 'det:182:2', 'det:182:3', 'llm:182:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient experiences seizures approximately every 2 days as consistently reported by carer and seizure logs.
- 218: kind `frequency_rate`, policy `primary_with_context`, primary ['det:218:1'], supporting ['llm:218:2'], rejected ['llm:218:1'], flags [], minimal selector `same`, rich selector `different`. Summary: Seizure frequency has improved to approximately one seizure every 3 weeks, stable over the past three months with good control and tolerability.
- 243: kind `frequency_rate`, policy `single_fact`, primary ['det:243:1', 'llm:243:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient has generalized seizures occurring approximately every four months with low seizure burden.
- 338: kind `unknown_frequency`, policy `primary_with_context`, primary ['det:338:1'], supporting ['llm:338:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `different`. Summary: Patient has many convulsions in the past month, with events clustering after eastbound flights and sleep restriction; seizure frequency is high but exact counts are not specified.
- 409: kind `frequency_rate`, policy `primary_with_context`, primary ['det:409:1', 'llm:409:2'], supporting ['llm:409:1'], rejected [], flags ['multi_primary_nonadditive_policy', 'cluster_context_leak_in_frequency_burden', 'historical_context_phrase_in_burden'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Seizure frequency has markedly improved to approximately once per month with brief focal impaired awareness episodes; previously occurred as weekly clusters of three events.
- 419: kind `frequency_rate`, policy `single_fact`, primary ['det:419:1', 'llm:419:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports a stable seizure frequency of approximately twice per year with no current antiseizure medication.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1', 'llm:446:3'], supporting ['llm:446:1', 'llm:446:2'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient currently experiences seizures up to twice per week, both nocturnally and during wakefulness, indicating clinical worsening compared to prior months with fewer events.
- 467: kind `frequency_rate`, policy `single_fact`, primary ['det:467:1', 'llm:467:1'], supporting [], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Patient reports a stable frequency of 9 focal seizures per month over the last eight weeks.
