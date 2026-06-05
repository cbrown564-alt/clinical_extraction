# Gan 2026 Clinical Assessment Diagnostics

5-row clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_v3nested_v3_diagnostics.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_v3nested_v3_diagnostics.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_flagged5_gpt41mini_v3nested_v3.jsonl`

## Summary

- Rows: 5
- Clinical assessment rows: 5
- Missing assessment rows: 0
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 0

## Assessment Kinds

- `cluster_frequency`: 2
- `frequency_rate`: 1
- `unknown_frequency`: 2

## Aggregation Policies

- `primary_with_context`: 4
- `unknown_due_to_absence`: 1

## Primary Candidate Counts

- `0`: 1
- `1`: 4

## Diagnostic Flags

- None.

## Selector Comparisons

### Minimal Selector V2
- `assessment_primary_subset`: 1
- `different`: 2
- `same`: 1

### Rich Selector V0

- `different`: 1
- `same`: 3

## Inspection Examples

### Flagged Rows

- None.

### Multi Primary Rows

- None.

### Context Leak Rows

- None.

### Minimal Selector Differences

- 744: kind `unknown_frequency`, policy `primary_with_context`, primary ['llm:744:1'], supporting ['llm:744:2', 'det:744:1', 'det:744:2', 'det:744:3'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient experiences frequent brief absence seizures on most weekdays, often clustering in the late afternoon due to fatigue, with one generalised tonic–clonic seizure in the last eight weeks. Current antiepileptic regimen is maintained with focus on managing fatigue and triggers. Monitoring and seizure diary recommended.
- 3469: kind `cluster_frequency`, policy `primary_with_context`, primary ['llm:3469:1'], supporting ['llm:3469:2', 'det:3469:3'], rejected ['det:3469:2'], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: Seizures occur exclusively during the perimenstrual window (days -3 to +3) with no events reported outside this window over the last six months. Events are brief behavioral arrests with loss of awareness and no consistent aura. Triggers include sleep disruption and premenstrual symptoms. Patient maintains a seizure ID card and peer observations supplement history. Repeat EEG and blood tests planned.
- 5567: kind `frequency_rate`, policy `primary_with_context`, primary ['det:5567:1'], supporting ['det:5567:2', 'llm:5567:3', 'llm:5567:4'], rejected ['llm:5567:1', 'llm:5567:2'], flags [], minimal selector `different`, rich selector `same`. Summary: The patient experiences several absence seizures per week, typically clustering in the late afternoon, with two generalised tonic–clonic seizures over the past six months, the last one three weeks ago after sleep deprivation. Generalised tonic–clonic seizures have not recurred since valproate dose increase six weeks ago. The absence seizures remain frequent and are the dominant current burden.

### Rich Selector Differences

- 744: kind `unknown_frequency`, policy `primary_with_context`, primary ['llm:744:1'], supporting ['llm:744:2', 'det:744:1', 'det:744:2', 'det:744:3'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient experiences frequent brief absence seizures on most weekdays, often clustering in the late afternoon due to fatigue, with one generalised tonic–clonic seizure in the last eight weeks. Current antiepileptic regimen is maintained with focus on managing fatigue and triggers. Monitoring and seizure diary recommended.
