# Gan 2026 Clinical Assessment Diagnostics

250-row clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_diagnostics_2026-06-06.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_diagnostics_2026-06-06.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_qwen36_35b_v3nested_v3_lenientdraft_repaired_recovered_2026-06-06.jsonl`

## Summary

- Rows: 250
- Clinical assessment rows: 250
- Missing assessment rows: 0
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 0

## Assessment Kinds

- `cluster_frequency`: 8
- `frequency_rate`: 158
- `seizure_free`: 43
- `unknown_frequency`: 41

## Aggregation Policies

- `additive_same_window`: 7
- `cluster_axis`: 1
- `primary_with_context`: 56
- `seizure_free_state`: 27
- `single_fact`: 126
- `unknown_due_to_absence`: 14
- `unknown_due_to_ambiguity`: 19

## Primary Candidate Counts

- `0`: 8
- `1`: 228
- `2`: 11
- `3`: 2
- `4`: 1

## Diagnostic Flags

- None.

## Selector Comparisons

### Minimal Selector V2

### Rich Selector V0


## Inspection Examples

### Flagged Rows

- None.

### Multi Primary Rows

- 849: kind `unknown_frequency`, policy `unknown_due_to_ambiguity`, primary ['llm:849:1', 'llm:849:3'], supporting ['det:849:1', 'llm:849:2'], rejected [], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: The patient describes a current pattern of yearly seizures, with variability in frequency (some years having one event, others none). A specific collapse occurred last winter.
- 854: kind `seizure_free`, policy `seizure_free_state`, primary ['llm:854:3', 'llm:854:4'], supporting ['llm:854:1'], rejected [], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: The patient is currently seizure-free regarding daytime episodes and witnessed prolonged events or clusters. Historically, seizures occurred roughly yearly, with the last episode in late January.
- 1413: kind `frequency_rate`, policy `additive_same_window`, primary ['det:1413:1', 'det:1413:2'], supporting [], rejected [], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: The patient reports a total of nine seizures (four focal sensory and five focal non-motor) in the last month.
- 1694: kind `cluster_frequency`, policy `cluster_axis`, primary ['llm:1694:2', 'llm:1694:3'], supporting ['llm:1694:1'], rejected [], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: The patient experienced a recent cluster of 3 short generalized seizures over three separate days within the past fortnight. She had been generally stable for several months prior to this event.
- 1914: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:1914:1', 'llm:1914:2'], supporting [], rejected [], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: The patient has experienced a total of seven seizures (two drop attacks and five tonic-clonic) over the past three months.
- 2622: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:2622:2', 'llm:2622:3'], supporting [], rejected ['llm:2622:1'], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: Current burden is characterized by nightly seizures, with three specific instances of secondary generalization noted this month. Historical context of previous clustering is noted but not part of the current primary burden assessment.
- 2822: kind `frequency_rate`, policy `additive_same_window`, primary ['det:2822:1', 'llm:2822:2'], supporting ['llm:2822:3', 'llm:2822:4'], rejected ['llm:2822:1'], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: The patient experiences a myoclonic jerk daily. These events occasionally cluster in the morning and very rarely occur later in the day, particularly during periods of sleep deprivation or stress.
- 3846: kind `frequency_rate`, policy `additive_same_window`, primary ['det:3846:1', 'llm:3846:3'], supporting ['llm:3846:2'], rejected [], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: Current burden is 2 seizures per month, with two occasions escalating to generalized tonic-clonic activity. Events typically cluster near the end of the dinner rush.
- 3988: kind `unknown_frequency`, policy `unknown_due_to_ambiguity`, primary ['det:3988:1', 'det:3988:2'], supporting ['llm:3988:1', 'llm:3988:2', 'llm:3988:4'], rejected ['llm:3988:3'], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 3995: kind `frequency_rate`, policy `additive_same_window`, primary ['det:3995:1', 'det:3995:2'], supporting ['llm:3995:1'], rejected [], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: Patient has 3 seizures per day. Additionally, absence seizures occur monthly.
- 4116: kind `frequency_rate`, policy `additive_same_window`, primary ['det:4116:1', 'llm:4116:2'], supporting ['det:4116:2', 'llm:4116:3'], rejected ['llm:4116:1'], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 4839: kind `seizure_free`, policy `seizure_free_state`, primary ['llm:4839:2', 'det:4839:2', 'llm:4839:5'], supporting ['llm:4839:3'], rejected ['llm:4839:1'], flags [], minimal selector `not_available`, rich selector `not_available`. Summary: 

### Context Leak Rows

- None.

### Minimal Selector Differences

- None.

### Rich Selector Differences

- None.
