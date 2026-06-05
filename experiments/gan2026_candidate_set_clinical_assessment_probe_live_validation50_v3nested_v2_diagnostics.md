# Gan 2026 Clinical Assessment Diagnostics

Validation25 clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v2_diagnostics.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v2_diagnostics.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation50_gpt41mini_v3nested_v2.jsonl`

## Summary

- Rows: 50
- Clinical assessment rows: 50
- Missing assessment rows: 0
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 0

## Assessment Kinds

- `cluster_frequency`: 5
- `frequency_rate`: 43
- `unknown_frequency`: 2

## Aggregation Policies

- `cluster_axis`: 1
- `primary_with_context`: 9
- `single_fact`: 40

## Primary Candidate Counts

- `1`: 49
- `2`: 1

## Diagnostic Flags

- None.

## Selector Comparisons

### Minimal Selector V2
- `assessment_primary_subset`: 4
- `different`: 5
- `same`: 41

### Rich Selector V0

- `assessment_primary_subset`: 4
- `assessment_primary_superset`: 1
- `different`: 3
- `same`: 41

## Inspection Examples

### Flagged Rows

- None.

### Multi Primary Rows

- 338: kind `cluster_frequency`, policy `cluster_axis`, primary ['det:338:1', 'llm:338:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient has experienced many generalized convulsions in the past month, with events clustering after eastbound flights and consecutive nights of restricted sleep (3–4 hours). This pattern is consistent with breakthrough seizures triggered by disrupted sleep and rapid time-zone changes. The plan focuses on optimizing circadian alignment and medication timing to reduce seizure burden.

### Context Leak Rows

- None.

### Minimal Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:1'], supporting ['llm:79:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports combined generalized and focal epilepsy with seizure frequency ≤ 6 to 7 per year, typically clustering around jet lag and sleep loss related to frequent travel. No injuries or hospital admissions. Current medications include lamotrigine and brivaracetam with good tolerability. Clobazam used PRN during travel-related high-risk periods. Adherence reinforced. No immediate further investigations required.
- 218: kind `frequency_rate`, policy `single_fact`, primary ['llm:218:2'], supporting ['llm:218:1'], rejected [], flags [], minimal selector `different`, rich selector `same`. Summary: The patient reports improved seizure control with seizures occurring approximately every 3 weeks over the past three months, compared to prior frequency of once every 2-3 days. No injuries or emergency attendances noted. Current regimen and lifestyle adjustments are effective and well tolerated.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, occurring both nocturnally and during wakefulness, with variable clustering. This represents a clinical deterioration compared to prior months (June and August) when seizure frequency was lower. The patient is on stable polytherapy but reports worsening control and adverse effects. Further investigations and medication review are planned.
- 466: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:466:1'], supporting ['llm:466:2'], rejected ['det:466:1'], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient currently experiences 21 to 28 focal impaired awareness seizures per month, typically brief and lasting 30–90 seconds with post-ictal fatigue. Occasional seizure clusters occur around significant sleep disruption but are not additive to the overall frequency burden. No generalized tonic–clonic seizures reported in the past six months. No hypoglycaemic episodes reported. The ketogenic diet and medication regimen are ongoing with planned follow-up in three months.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:1'], supporting ['llm:598:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports stable focal epilepsy with impaired awareness, experiencing approximately one seizure every eight months over the past 16 months. Seizure diary corroborates this frequency. No secondary generalization or new neurological features. Current antiepileptic therapy is effective and well tolerated. Triggers include sleep deprivation. No changes to diabetes management. Follow-up planned in 12 months or sooner if frequency increases or new symptoms arise.
- 744: kind `frequency_rate`, policy `primary_with_context`, primary ['det:744:2'], supporting ['det:744:1', 'llm:744:2'], rejected ['det:744:3', 'llm:744:1'], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient experiences frequent brief absence seizures on most weekdays, often clustering in the late afternoon related to fatigue. There has been one generalised tonic–clonic seizure in the last eight weeks. Management focuses on addressing fatigue and triggers without medication changes currently.
- 978: kind `frequency_rate`, policy `single_fact`, primary ['llm:978:3'], supporting ['llm:978:1', 'llm:978:2'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences focal impaired-awareness seizures approximately every other month without clustering. Historically, seizures were more frequent and clustered with 6 to 8 events in one day. Improvement is attributed to better sleep hygiene and routine after retirement.
- 1046: kind `frequency_rate`, policy `primary_with_context`, primary ['det:1046:1'], supporting ['llm:1046:1', 'llm:1046:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient reports 3 to 5 seizures last month, including both focal aware and generalised events. There is uncertainty in recall due to clustering. Recent increase in generalised seizures noted despite stable medication levels. Stress and missed meals may contribute to lowered seizure threshold.
- 1165: kind `cluster_frequency`, policy `single_fact`, primary ['llm:1165:1'], supporting ['det:1165:1', 'llm:1165:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `different`. Summary: Patient experienced a cluster of 5 to 7 focal onset seizures over three weeks linked to travel-related anxiety and sleep disruption, followed by six seizure-free weeks. Current anti-seizure regimen maintained with no dose changes.

### Rich Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:1'], supporting ['llm:79:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports combined generalized and focal epilepsy with seizure frequency ≤ 6 to 7 per year, typically clustering around jet lag and sleep loss related to frequent travel. No injuries or hospital admissions. Current medications include lamotrigine and brivaracetam with good tolerability. Clobazam used PRN during travel-related high-risk periods. Adherence reinforced. No immediate further investigations required.
- 338: kind `cluster_frequency`, policy `cluster_axis`, primary ['det:338:1', 'llm:338:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient has experienced many generalized convulsions in the past month, with events clustering after eastbound flights and consecutive nights of restricted sleep (3–4 hours). This pattern is consistent with breakthrough seizures triggered by disrupted sleep and rapid time-zone changes. The plan focuses on optimizing circadian alignment and medication timing to reduce seizure burden.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, occurring both nocturnally and during wakefulness, with variable clustering. This represents a clinical deterioration compared to prior months (June and August) when seizure frequency was lower. The patient is on stable polytherapy but reports worsening control and adverse effects. Further investigations and medication review are planned.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:1'], supporting ['llm:598:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports stable focal epilepsy with impaired awareness, experiencing approximately one seizure every eight months over the past 16 months. Seizure diary corroborates this frequency. No secondary generalization or new neurological features. Current antiepileptic therapy is effective and well tolerated. Triggers include sleep deprivation. No changes to diabetes management. Follow-up planned in 12 months or sooner if frequency increases or new symptoms arise.
- 816: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:816:1'], supporting ['llm:816:3'], rejected ['llm:816:2'], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: The patient currently experiences occasional monthly seizures, typically brief focal-onset episodes with rapid recovery. There has been a marked improvement since starting ketogenic diet therapy, with fewer breakthrough events and better sleep reported by the family. Historical seizure counts from 2017 are not included in the current burden assessment.
- 978: kind `frequency_rate`, policy `single_fact`, primary ['llm:978:3'], supporting ['llm:978:1', 'llm:978:2'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences focal impaired-awareness seizures approximately every other month without clustering. Historically, seizures were more frequent and clustered with 6 to 8 events in one day. Improvement is attributed to better sleep hygiene and routine after retirement.
- 1094: kind `frequency_rate`, policy `single_fact`, primary ['llm:1094:1'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: Patient reports 3 to 5 seizures in the past week, with increased frequency and duration compared to baseline, likely related to circadian disruption and inconsistent medication timing during recent international travel.
- 1165: kind `cluster_frequency`, policy `single_fact`, primary ['llm:1165:1'], supporting ['det:1165:1', 'llm:1165:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `different`. Summary: Patient experienced a cluster of 5 to 7 focal onset seizures over three weeks linked to travel-related anxiety and sleep disruption, followed by six seizure-free weeks. Current anti-seizure regimen maintained with no dose changes.
