# Gan 2026 Clinical Assessment Diagnostics

250-row clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_diagnostics_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_diagnostics_2026-06-06.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_2026-06-06.jsonl`

## Summary

- Rows: 250
- Clinical assessment rows: 26
- Missing assessment rows: 224
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 225

## Assessment Kinds

- `frequency_rate`: 7
- `seizure_free`: 4
- `unknown_frequency`: 15

## Aggregation Policies

- `additive_same_window`: 1
- `primary_with_context`: 2
- `single_fact`: 10
- `unknown_due_to_absence`: 9
- `unknown_due_to_ambiguity`: 4

## Primary Candidate Counts

- `0`: 7
- `1`: 16
- `2`: 3

## Diagnostic Flags

- `assessment_missing`: 224
- `multi_primary_nonadditive_policy`: 1

## Selector Comparisons

### Minimal Selector V2
- `assessment_primary_subset`: 5
- `assessment_primary_superset`: 2
- `different`: 6
- `same`: 10

### Rich Selector V0

- `assessment_primary_subset`: 7
- `assessment_primary_superset`: 2
- `different`: 4
- `same`: 8

## Inspection Examples

### Flagged Rows

- 10: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 40: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 79: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 103: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 128: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 156: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 180: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 182: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 187: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 190: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 198: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 212: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 

### Multi Primary Rows

- 2166: kind `unknown_frequency`, policy `unknown_due_to_ambiguity`, primary ['llm:2166:1', 'llm:2166:3'], supporting [], rejected ['llm:2166:2'], flags [], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient has frequent petit mal seizures and increasing brief absence episodes recently. There is no history of generalized tonic-clonic seizures for over a year.
- 2622: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:2622:2', 'llm:2622:3'], supporting [], rejected ['llm:2622:1'], flags [], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Current burden is characterized by nightly seizures, with three specific instances of secondary generalization noted this month. Historical context of previous clustering is noted but not part of the current primary burden assessment.
- 4771: kind `unknown_frequency`, policy `primary_with_context`, primary ['llm:4771:1', 'llm:4771:2'], supporting ['llm:4771:3', 'llm:4771:4', 'llm:4771:5'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `different`, rich selector `different`. Summary: The patient reports increased seizure activity occurring in several stretches across the month, characterized by brief focal aware episodes (lip-smacking, word-finding pauses) that sometimes progress to focal impaired awareness events. Supporting context includes two instances of secondary generalization in the last six weeks, short runs of events following disrupted sleep/travel, and a history of a generalized seizure in August. The exact frequency is unknown due to the vague description of 'spells' and 'stretches'.

### Context Leak Rows

- None.

### Minimal Selector Differences

- 1094: kind `frequency_rate`, policy `single_fact`, primary ['det:1094:1'], supporting ['llm:1094:1'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: The patient reports a frequency of 3 to 5 seizures over the past week. The LLM-extracted candidate corroborates this recent event count.
- 2166: kind `unknown_frequency`, policy `unknown_due_to_ambiguity`, primary ['llm:2166:1', 'llm:2166:3'], supporting [], rejected ['llm:2166:2'], flags [], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient has frequent petit mal seizures and increasing brief absence episodes recently. There is no history of generalized tonic-clonic seizures for over a year.
- 2456: kind `frequency_rate`, policy `single_fact`, primary ['llm:2456:2'], supporting ['det:2456:1'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient reports six to seven seizures over the last two weeks according to their diary. The deterministic candidate is corroborated by the LLM-extracted candidate.
- 2622: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:2622:2', 'llm:2622:3'], supporting [], rejected ['llm:2622:1'], flags [], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Current burden is characterized by nightly seizures, with three specific instances of secondary generalization noted this month. Historical context of previous clustering is noted but not part of the current primary burden assessment.
- 3512: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary [], supporting ['llm:3512:1', 'llm:3512:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `assessment_primary_subset`. Summary: The patient's seizure frequency has increased by approximately 20% following a dose increase. The events are characterized as brief (seconds to under a minute) with preserved awareness in some instances, but no specific frequency rate or count is provided to quantify the current burden.
- 3534: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary [], supporting ['det:3534:1', 'det:3534:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `assessment_primary_subset`. Summary: The note mentions possible auras and one episode this year, but lacks a specific frequency rate. Improvement is noted over the past seven months.
- 3623: kind `unknown_frequency`, policy `unknown_due_to_ambiguity`, primary ['llm:3623:1'], supporting ['llm:3623:2'], rejected ['det:3623:1'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient experiences clusters of seizure-like events with variable frequency. While 'up to seven in bad weeks' was noted, the overall pattern is characterized by variable frequency rather than a precise rate. Multiple events are reported within these clusters.
- 3892: kind `frequency_rate`, policy `single_fact`, primary ['det:3892:1'], supporting [], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: Current seizure frequency is 3 per year. Triggers include poor sleep and intercurrent illness. Management is stable.
- 4694: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary [], supporting [], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `assessment_primary_subset`. Summary: The note describes frequent electrographic seizures (~9/h) on recent video-EEG, but the provided candidate set is empty due to a validation error. Consequently, no structured burden assessment can be derived from the candidates. Clinically, the patient has frequent subclinical seizures with rare clinical correlates.
- 4709: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary [], supporting [], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `assessment_primary_subset`. Summary: The clinical note indicates persistent focal features and frequent electrographic seizures, but the provided candidate set is empty. Therefore, a specific current seizure frequency burden cannot be quantified from the candidates. The note mentions a plan to revisit medication changes and requests a repeat MRI, implying ongoing active disease management.
- 4771: kind `unknown_frequency`, policy `primary_with_context`, primary ['llm:4771:1', 'llm:4771:2'], supporting ['llm:4771:3', 'llm:4771:4', 'llm:4771:5'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `different`, rich selector `different`. Summary: The patient reports increased seizure activity occurring in several stretches across the month, characterized by brief focal aware episodes (lip-smacking, word-finding pauses) that sometimes progress to focal impaired awareness events. Supporting context includes two instances of secondary generalization in the last six weeks, short runs of events following disrupted sleep/travel, and a history of a generalized seizure in August. The exact frequency is unknown due to the vague description of 'spells' and 'stretches'.
- 5490: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary ['llm:5490:1'], supporting ['llm:5490:2', 'llm:5490:3', 'llm:5490:4'], rejected [], flags [], minimal selector `different`, rich selector `not_available`. Summary: The patient experiences sporadic drop attacks this year, but the overall seizure frequency remains unclear as the clinician could not provide a reliable count over recent months.

### Rich Selector Differences

- 1094: kind `frequency_rate`, policy `single_fact`, primary ['det:1094:1'], supporting ['llm:1094:1'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: The patient reports a frequency of 3 to 5 seizures over the past week. The LLM-extracted candidate corroborates this recent event count.
- 2166: kind `unknown_frequency`, policy `unknown_due_to_ambiguity`, primary ['llm:2166:1', 'llm:2166:3'], supporting [], rejected ['llm:2166:2'], flags [], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient has frequent petit mal seizures and increasing brief absence episodes recently. There is no history of generalized tonic-clonic seizures for over a year.
- 2456: kind `frequency_rate`, policy `single_fact`, primary ['llm:2456:2'], supporting ['det:2456:1'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient reports six to seven seizures over the last two weeks according to their diary. The deterministic candidate is corroborated by the LLM-extracted candidate.
- 2622: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:2622:2', 'llm:2622:3'], supporting [], rejected ['llm:2622:1'], flags [], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: Current burden is characterized by nightly seizures, with three specific instances of secondary generalization noted this month. Historical context of previous clustering is noted but not part of the current primary burden assessment.
- 3512: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary [], supporting ['llm:3512:1', 'llm:3512:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `assessment_primary_subset`. Summary: The patient's seizure frequency has increased by approximately 20% following a dose increase. The events are characterized as brief (seconds to under a minute) with preserved awareness in some instances, but no specific frequency rate or count is provided to quantify the current burden.
- 3534: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary [], supporting ['det:3534:1', 'det:3534:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `assessment_primary_subset`. Summary: The note mentions possible auras and one episode this year, but lacks a specific frequency rate. Improvement is noted over the past seven months.
- 3623: kind `unknown_frequency`, policy `unknown_due_to_ambiguity`, primary ['llm:3623:1'], supporting ['llm:3623:2'], rejected ['det:3623:1'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient experiences clusters of seizure-like events with variable frequency. While 'up to seven in bad weeks' was noted, the overall pattern is characterized by variable frequency rather than a precise rate. Multiple events are reported within these clusters.
- 3892: kind `frequency_rate`, policy `single_fact`, primary ['det:3892:1'], supporting [], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: Current seizure frequency is 3 per year. Triggers include poor sleep and intercurrent illness. Management is stable.
- 4694: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary [], supporting [], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `assessment_primary_subset`. Summary: The note describes frequent electrographic seizures (~9/h) on recent video-EEG, but the provided candidate set is empty due to a validation error. Consequently, no structured burden assessment can be derived from the candidates. Clinically, the patient has frequent subclinical seizures with rare clinical correlates.
- 4709: kind `unknown_frequency`, policy `unknown_due_to_absence`, primary [], supporting [], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `assessment_primary_subset`. Summary: The clinical note indicates persistent focal features and frequent electrographic seizures, but the provided candidate set is empty. Therefore, a specific current seizure frequency burden cannot be quantified from the candidates. The note mentions a plan to revisit medication changes and requests a repeat MRI, implying ongoing active disease management.
- 4771: kind `unknown_frequency`, policy `primary_with_context`, primary ['llm:4771:1', 'llm:4771:2'], supporting ['llm:4771:3', 'llm:4771:4', 'llm:4771:5'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `different`, rich selector `different`. Summary: The patient reports increased seizure activity occurring in several stretches across the month, characterized by brief focal aware episodes (lip-smacking, word-finding pauses) that sometimes progress to focal impaired awareness events. Supporting context includes two instances of secondary generalization in the last six weeks, short runs of events following disrupted sleep/travel, and a history of a generalized seizure in August. The exact frequency is unknown due to the vague description of 'spells' and 'stretches'.
- 4910: kind `seizure_free`, policy `single_fact`, primary ['llm:4910:1'], supporting ['llm:4910:2'], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: Patient reports being free of seizures for 2 years with no further blackouts, convulsions, or focal neurological events. Prior investigations (EEG, MRI) were normal. No antiepileptic drugs are currently prescribed.
