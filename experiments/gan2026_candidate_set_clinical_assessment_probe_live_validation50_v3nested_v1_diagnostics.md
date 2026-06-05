# Gan 2026 Clinical Assessment Diagnostics

Validation25 clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v1_diagnostics.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation50_v3nested_v1_diagnostics.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation50_gpt41mini_v3nested_v1.jsonl`

## Summary

- Rows: 50
- Clinical assessment rows: 50
- Missing assessment rows: 0
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 4

## Assessment Kinds

- `cluster_frequency`: 6
- `frequency_rate`: 42
- `unknown_frequency`: 2

## Aggregation Policies

- `cluster_axis`: 2
- `primary_with_context`: 11
- `single_fact`: 37

## Primary Candidate Counts

- `1`: 46
- `2`: 4

## Diagnostic Flags

- `cluster_context_leak_in_frequency_burden`: 1
- `historical_primary_candidate`: 1
- `multi_primary_nonadditive_policy`: 2
- `single_fact_multiple_primary_candidates`: 1

## Selector Comparisons

### Minimal Selector V2
- `assessment_primary_subset`: 2
- `assessment_primary_superset`: 1
- `different`: 3
- `overlap`: 1
- `same`: 43

### Rich Selector V0

- `assessment_primary_subset`: 4
- `assessment_primary_superset`: 3
- `different`: 3
- `same`: 39

## Inspection Examples

### Flagged Rows

- 678: kind `cluster_frequency`, policy `cluster_axis`, primary ['llm:678:1', 'llm:678:2'], supporting [], rejected [], flags ['historical_primary_candidate'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient currently experiences seizures twice every 4 months, with clusters of 3 to 6 seizures occurring in one day. This represents an improvement compared to prior patterns with more frequent clusters and shorter seizure-free intervals. Psychological support and sleep hygiene appear to contribute to better control. No injuries or hospitalizations reported.
- 731: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:731:1'], supporting ['llm:731:2'], rejected [], flags ['cluster_context_leak_in_frequency_burden'], minimal selector `same`, rich selector `same`. Summary: The patient experiences brief seizures daily, typically without postictal confusion or injury. A recent short cluster of three brief spells over 15 minutes was noted without escalation. Events are more frequent on nights with poor sleep. Monitoring continues with caregiver seizure diary and telemedicine follow-up planned.
- 744: kind `frequency_rate`, policy `primary_with_context`, primary ['det:744:2', 'det:744:1'], supporting ['llm:744:1', 'llm:744:2', 'det:744:3'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: Patient has frequent brief absence seizures occurring on most weekdays, often clustering in late afternoon with fatigue as a trigger, and one generalised tonic–clonic seizure in the last eight weeks. Current antiepileptic regimen is maintained with focus on managing fatigue and triggers. Monitoring and seizure diary planned to guide future adjustments.
- 1165: kind `cluster_frequency`, policy `single_fact`, primary ['det:1165:1', 'llm:1165:1'], supporting ['llm:1165:2'], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `overlap`, rich selector `different`. Summary: Patient experienced a cluster of 5 to 7 focal onset seizures over a recent 3-week period related to travel anxiety and sleep disruption, followed by a 6-week seizure-free interval. Current anti-seizure regimen maintained with no dose changes. Anxiety management and travel planning advised.

### Multi Primary Rows

- 338: kind `cluster_frequency`, policy `cluster_axis`, primary ['det:338:1', 'llm:338:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient experiences multiple generalized seizures clustered after eastbound flights and consecutive nights of restricted sleep (3-4 hours). The plan focuses on optimizing sleep hygiene and medication timing to reduce breakthrough seizures associated with travel-related circadian disruption.
- 678: kind `cluster_frequency`, policy `cluster_axis`, primary ['llm:678:1', 'llm:678:2'], supporting [], rejected [], flags ['historical_primary_candidate'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient currently experiences seizures twice every 4 months, with clusters of 3 to 6 seizures occurring in one day. This represents an improvement compared to prior patterns with more frequent clusters and shorter seizure-free intervals. Psychological support and sleep hygiene appear to contribute to better control. No injuries or hospitalizations reported.
- 744: kind `frequency_rate`, policy `primary_with_context`, primary ['det:744:2', 'det:744:1'], supporting ['llm:744:1', 'llm:744:2', 'det:744:3'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: Patient has frequent brief absence seizures occurring on most weekdays, often clustering in late afternoon with fatigue as a trigger, and one generalised tonic–clonic seizure in the last eight weeks. Current antiepileptic regimen is maintained with focus on managing fatigue and triggers. Monitoring and seizure diary planned to guide future adjustments.
- 1165: kind `cluster_frequency`, policy `single_fact`, primary ['det:1165:1', 'llm:1165:1'], supporting ['llm:1165:2'], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `overlap`, rich selector `different`. Summary: Patient experienced a cluster of 5 to 7 focal onset seizures over a recent 3-week period related to travel anxiety and sleep disruption, followed by a 6-week seizure-free interval. Current anti-seizure regimen maintained with no dose changes. Anxiety management and travel planning advised.

### Context Leak Rows

- 731: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:731:1'], supporting ['llm:731:2'], rejected [], flags ['cluster_context_leak_in_frequency_burden'], minimal selector `same`, rich selector `same`. Summary: The patient experiences brief seizures daily, typically without postictal confusion or injury. A recent short cluster of three brief spells over 15 minutes was noted without escalation. Events are more frequent on nights with poor sleep. Monitoring continues with caregiver seizure diary and telemedicine follow-up planned.

### Minimal Selector Differences

- 218: kind `frequency_rate`, policy `single_fact`, primary ['llm:218:2'], supporting ['llm:218:1'], rejected [], flags [], minimal selector `different`, rich selector `same`. Summary: The patient reports improved seizure control with seizures now occurring approximately every 3 weeks over the past three months, compared to prior frequency of once every 2-3 days. No injuries or emergency attendances noted. Current antiepileptic regimen is well tolerated.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, occurring both nocturnally and during wakefulness with variable clustering. This represents a clinical deterioration compared to prior months (June and August) when seizure frequency was lower. The patient is on stable polytherapy but reports worsening control and adverse effects impacting function. Further investigations and medication review are planned.
- 466: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:466:1'], supporting ['llm:466:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient experiences 21 to 28 focal impaired awareness seizures per month, typically brief and with post-ictal fatigue. Occasional seizure clusters occur around significant sleep disruption but are not additive to the total seizure count.
- 678: kind `cluster_frequency`, policy `cluster_axis`, primary ['llm:678:1', 'llm:678:2'], supporting [], rejected [], flags ['historical_primary_candidate'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient currently experiences seizures twice every 4 months, with clusters of 3 to 6 seizures occurring in one day. This represents an improvement compared to prior patterns with more frequent clusters and shorter seizure-free intervals. Psychological support and sleep hygiene appear to contribute to better control. No injuries or hospitalizations reported.
- 978: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:978:3'], supporting ['llm:978:1', 'llm:978:2'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences focal impaired-awareness seizures approximately every other month without clustering. Historically, seizures were more frequent and clustered with 6 to 8 events in one day. Improvement is attributed to better sleep hygiene and routine after retirement.
- 1046: kind `frequency_rate`, policy `primary_with_context`, primary ['det:1046:1'], supporting ['llm:1046:2', 'llm:1046:1'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient reports 3 to 5 seizures last month, including brief focal aware episodes and generalised seizures with loss of awareness. There is uncertainty in recall due to clustering. Recent increase in generalised events noted despite stable medication. Stress and missed meals may lower seizure threshold. Plan includes medication adjustment and further investigations.
- 1165: kind `cluster_frequency`, policy `single_fact`, primary ['det:1165:1', 'llm:1165:1'], supporting ['llm:1165:2'], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `overlap`, rich selector `different`. Summary: Patient experienced a cluster of 5 to 7 focal onset seizures over a recent 3-week period related to travel anxiety and sleep disruption, followed by a 6-week seizure-free interval. Current anti-seizure regimen maintained with no dose changes. Anxiety management and travel planning advised.

### Rich Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:2'], supporting ['llm:79:1'], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: Patient reports combined generalized and focal epilepsy with seizure frequency ≤ 6 to 7 per year, typically clustering around travel-related triggers such as jet lag and sleep loss. No injuries or hospital admissions. Current medications well tolerated. Adherence reinforced. Clobazam used PRN during travel. No immediate further investigations required. Follow-up planned in 4 months or earlier if increased events.
- 338: kind `cluster_frequency`, policy `cluster_axis`, primary ['det:338:1', 'llm:338:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient experiences multiple generalized seizures clustered after eastbound flights and consecutive nights of restricted sleep (3-4 hours). The plan focuses on optimizing sleep hygiene and medication timing to reduce breakthrough seizures associated with travel-related circadian disruption.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, occurring both nocturnally and during wakefulness with variable clustering. This represents a clinical deterioration compared to prior months (June and August) when seizure frequency was lower. The patient is on stable polytherapy but reports worsening control and adverse effects impacting function. Further investigations and medication review are planned.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:2'], supporting ['llm:598:1'], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: Patient reports a stable seizure frequency averaging 1 seizure every 8 months over the past 16 months, consistent with seizure diary. No secondary generalization or worsening noted. Current antiepileptic therapy is continued with good adherence and tolerability. Triggers such as sleep deprivation are recognized but do not increase frequency currently.
- 678: kind `cluster_frequency`, policy `cluster_axis`, primary ['llm:678:1', 'llm:678:2'], supporting [], rejected [], flags ['historical_primary_candidate'], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient currently experiences seizures twice every 4 months, with clusters of 3 to 6 seizures occurring in one day. This represents an improvement compared to prior patterns with more frequent clusters and shorter seizure-free intervals. Psychological support and sleep hygiene appear to contribute to better control. No injuries or hospitalizations reported.
- 744: kind `frequency_rate`, policy `primary_with_context`, primary ['det:744:2', 'det:744:1'], supporting ['llm:744:1', 'llm:744:2', 'det:744:3'], rejected [], flags ['multi_primary_nonadditive_policy'], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: Patient has frequent brief absence seizures occurring on most weekdays, often clustering in late afternoon with fatigue as a trigger, and one generalised tonic–clonic seizure in the last eight weeks. Current antiepileptic regimen is maintained with focus on managing fatigue and triggers. Monitoring and seizure diary planned to guide future adjustments.
- 816: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:816:1'], supporting ['llm:816:3'], rejected ['llm:816:2'], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: The patient currently experiences monthly seizures, which are brief focal-onset episodes with rapid recovery. There has been a marked reduction in seizure frequency since starting ketogenic diet therapy, with no prolonged events or injuries this year. The family reports improved sleep and fewer breakthrough events. Historical counts from 2017 are not included in the current burden assessment.
- 978: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:978:3'], supporting ['llm:978:1', 'llm:978:2'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences focal impaired-awareness seizures approximately every other month without clustering. Historically, seizures were more frequent and clustered with 6 to 8 events in one day. Improvement is attributed to better sleep hygiene and routine after retirement.
- 1094: kind `frequency_rate`, policy `single_fact`, primary ['llm:1094:1'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: Patient reports 3 to 5 seizures last week with increased frequency and duration compared to baseline, associated with circadian disruption and inconsistent medication timing during recent international travel. No emergency attendances or new neurological deficits noted. Strategies to re-establish regular sleep and medication timing discussed; follow-up planned in eight weeks.
- 1165: kind `cluster_frequency`, policy `single_fact`, primary ['det:1165:1', 'llm:1165:1'], supporting ['llm:1165:2'], rejected [], flags ['multi_primary_nonadditive_policy', 'single_fact_multiple_primary_candidates'], minimal selector `overlap`, rich selector `different`. Summary: Patient experienced a cluster of 5 to 7 focal onset seizures over a recent 3-week period related to travel anxiety and sleep disruption, followed by a 6-week seizure-free interval. Current anti-seizure regimen maintained with no dose changes. Anxiety management and travel planning advised.
