# Gan 2026 Clinical Assessment Diagnostics

250-row clinical-assessment diagnostics only. This inspects role usage, context separation, and comparisons to selector artifacts; it does not score, project, or render answers.

## Artifacts

- Diagnostic JSONL: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_v3nested_v2_diagnostics.jsonl`
- Summary JSON: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_v3nested_v2_diagnostics.json`
- Assessment source: `experiments\gan2026_candidate_set_clinical_assessment_probe_live_validation250_gpt41mini_v3nested_v2.jsonl`

## Summary

- Rows: 250
- Clinical assessment rows: 247
- Missing assessment rows: 3
- Invalid reference rows: 0
- Role overlap rows: 0
- Rows with diagnostic flags: 5

## Assessment Kinds

- `cluster_frequency`: 22
- `frequency_rate`: 167
- `seizure_free`: 41
- `unknown_frequency`: 17

## Aggregation Policies

- `additive_same_window`: 3
- `cluster_axis`: 2
- `no_reference_boundary`: 1
- `primary_with_context`: 41
- `seizure_free_state`: 14
- `single_fact`: 185
- `unknown_due_to_absence`: 1

## Primary Candidate Counts

- `0`: 2
- `1`: 239
- `2`: 6

## Diagnostic Flags

- `additive_policy_non_frequency_primary`: 1
- `assessment_missing`: 3
- `seizure_free_context_leak_in_cluster_burden`: 1

## Selector Comparisons

### Minimal Selector V2
- `assessment_primary_subset`: 13
- `assessment_primary_superset`: 1
- `different`: 26
- `same`: 205

### Rich Selector V0

- `assessment_primary_subset`: 23
- `assessment_primary_superset`: 4
- `different`: 24
- `same`: 187

## Inspection Examples

### Flagged Rows

- 744: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:744:1', 'llm:744:2'], supporting [], rejected ['det:744:1', 'det:744:2', 'det:744:3'], flags ['additive_policy_non_frequency_primary'], minimal selector `different`, rich selector `different`. Summary: The patient experiences frequent brief absence seizures on most weekdays, often clustering in the late afternoon, alongside one generalised tonic–clonic seizure in the last eight weeks. Fatigue and caregiving responsibilities are noted as potential triggers. Current antiepileptic regimen is maintained with plans for conservative monitoring and supportive measures to address fatigue and seizure triggers.
- 1363: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 3469: kind `cluster_frequency`, policy `single_fact`, primary ['llm:3469:1'], supporting ['llm:3469:2', 'det:3469:3'], rejected ['det:3469:2'], flags ['seizure_free_context_leak_in_cluster_burden'], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: Seizures occur exclusively during a perimenstrual window of approximately 7 days every cycle, with no events reported outside this window for the past six months. Events are brief behavioral arrests with loss of awareness. No consistent aura reported. The perimenstrual clustering is the primary burden; seizure freedom outside this window is noted as context. No exact seizure counts are provided, so frequency is described as cluster frequency with a defined cluster period. The aura candidate is rejected as it does not describe frequency or burden.
- 3532: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 
- 5567: kind `missing`, policy `missing`, primary [], supporting [], rejected [], flags ['assessment_missing'], minimal selector `not_available`, rich selector `not_available`. Summary: 

### Multi Primary Rows

- 338: kind `cluster_frequency`, policy `cluster_axis`, primary ['det:338:1', 'llm:338:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient has experienced many generalized convulsions in the past month, with events clustering after eastbound flights and consecutive nights of restricted sleep (3-4 hours). This pattern is consistent with breakthrough seizures triggered by disrupted sleep and rapid time-zone changes. The plan focuses on optimizing circadian alignment and medication timing to reduce seizure burden.
- 744: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:744:1', 'llm:744:2'], supporting [], rejected ['det:744:1', 'det:744:2', 'det:744:3'], flags ['additive_policy_non_frequency_primary'], minimal selector `different`, rich selector `different`. Summary: The patient experiences frequent brief absence seizures on most weekdays, often clustering in the late afternoon, alongside one generalised tonic–clonic seizure in the last eight weeks. Fatigue and caregiving responsibilities are noted as potential triggers. Current antiepileptic regimen is maintained with plans for conservative monitoring and supportive measures to address fatigue and seizure triggers.
- 1573: kind `cluster_frequency`, policy `cluster_axis`, primary ['llm:1573:1', 'llm:1573:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient experienced 11 focal seizures (five focal cognitive and six focal non-motor) over the last week, with several clustered over two consecutive mornings. There is clinical deterioration with escalating fatigue and irritability attributed to polytherapy. No witnessed generalized convulsions were noted. The patient is adherent to medication but seizure control remains suboptimal. Prolonged post-event disorientation was noted on one occasion. Further video-EEG monitoring is planned to clarify electroclinical pattern and guide treatment rationalization.
- 1591: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:1591:1', 'llm:1591:2'], supporting ['det:1591:1', 'det:1591:2'], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient reports a total of 11 focal seizures in the last month, including 5 focal onset seizures with impaired awareness and 6 focal non-motor seizures. No generalized tonic-clonic seizures were reported. Seizures are often triggered by flicker or bright light exposure. The patient is on stable levetiracetam therapy with good adherence and therapeutic blood levels. No auras or other seizure types noted. Safety measures and seizure diary are in place.
- 1923: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:1923:1', 'llm:1923:2'], supporting [], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient reports a total of seven seizures in the past six months, comprising two drop attacks and five epileptic spasms. These events are brief, with no focal onset symptoms or prolonged confusion. No emergency medication or hospital admissions in the past year. Ongoing monitoring and EEG planned.
- 3534: kind `seizure_free`, policy `seizure_free_state`, primary ['llm:3534:2', 'llm:3534:1'], supporting ['det:3534:2', 'llm:3534:5'], rejected ['det:3534:1', 'llm:3534:3', 'llm:3534:4'], flags [], minimal selector `assessment_primary_superset`, rich selector `assessment_primary_superset`. Summary: The patient reports no seizures requiring rescue medication and no injuries or admissions for the past seven months, indicating improved seizure control and sustained seizure freedom during this period. Historical possible auras and anxiety episodes earlier this year are not considered current seizures. The patient maintains good medication adherence and sleep hygiene, with ongoing monitoring and safety advice.

### Context Leak Rows

- 3469: kind `cluster_frequency`, policy `single_fact`, primary ['llm:3469:1'], supporting ['llm:3469:2', 'det:3469:3'], rejected ['det:3469:2'], flags ['seizure_free_context_leak_in_cluster_burden'], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: Seizures occur exclusively during a perimenstrual window of approximately 7 days every cycle, with no events reported outside this window for the past six months. Events are brief behavioral arrests with loss of awareness. No consistent aura reported. The perimenstrual clustering is the primary burden; seizure freedom outside this window is noted as context. No exact seizure counts are provided, so frequency is described as cluster frequency with a defined cluster period. The aura candidate is rejected as it does not describe frequency or burden.

### Minimal Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:1'], supporting ['llm:79:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports combined generalized and focal epilepsy with seizure frequency ≤ 6 to 7 per year, typically clustering around jet lag and sleep loss related to frequent travel. No injuries or hospital admissions. Current medications include lamotrigine and brivaracetam with good tolerability. Clobazam used PRN during travel-related high-risk periods. Adherence strategies reinforced. No immediate further imaging required; follow-up planned in 4 months or earlier if seizures increase.
- 218: kind `frequency_rate`, policy `single_fact`, primary ['llm:218:2'], supporting ['llm:218:1'], rejected [], flags [], minimal selector `different`, rich selector `same`. Summary: The patient reports improved seizure control with seizures now occurring approximately every 3 weeks over the past three months, compared to prior frequency of once every 2 to 3 days before workload reduction. No injuries or emergency attendances reported; treatment is well tolerated.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, both nocturnally and during wakefulness, with variable clustering. This represents a clinical deterioration compared to historical frequencies in June and August. Adverse effects from polytherapy are significant, impacting function and quality of life. Further diagnostic evaluation and medication review are planned.
- 466: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:466:1'], supporting ['llm:466:2'], rejected ['det:466:1'], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient experiences 21 to 28 focal impaired awareness seizures per month, typically brief and with post-ictal fatigue. Occasional seizure clusters occur around significant sleep disruption but are not additive to the overall frequency burden. No generalized tonic-clonic seizures reported in the past six months. No hypoglycaemic episodes are noted.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:1'], supporting ['llm:598:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports stable focal epilepsy with impaired awareness, experiencing approximately one seizure every eight months over the past 16 months. No secondary generalization or recent increase in frequency. Seizure diary corroborates this pattern. Triggers include sleep deprivation. Current antiepileptic therapy is effective and well tolerated.
- 744: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:744:1', 'llm:744:2'], supporting [], rejected ['det:744:1', 'det:744:2', 'det:744:3'], flags ['additive_policy_non_frequency_primary'], minimal selector `different`, rich selector `different`. Summary: The patient experiences frequent brief absence seizures on most weekdays, often clustering in the late afternoon, alongside one generalised tonic–clonic seizure in the last eight weeks. Fatigue and caregiving responsibilities are noted as potential triggers. Current antiepileptic regimen is maintained with plans for conservative monitoring and supportive measures to address fatigue and seizure triggers.
- 978: kind `frequency_rate`, policy `single_fact`, primary ['llm:978:3'], supporting ['llm:978:1', 'llm:978:2'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences focal impaired-awareness seizures approximately every other month without clustering, representing a significant improvement from prior frequent clustered seizures occurring several times per day. Improved sleep hygiene and routine likely contributed to this better control.
- 1046: kind `frequency_rate`, policy `primary_with_context`, primary ['det:1046:1'], supporting ['llm:1046:1', 'llm:1046:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `same`. Summary: The patient reports 3 to 5 seizures last month, including both focal aware and generalised seizures. There is uncertainty in recall due to clustering. Recent increase in generalised events noted despite stable medication. Stress and missed meals may contribute to lowered seizure threshold.
- 1165: kind `cluster_frequency`, policy `primary_with_context`, primary ['llm:1165:1'], supporting ['det:1165:1', 'llm:1165:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `different`. Summary: Patient experienced a cluster of 5 to 7 focal onset seizures over three weeks related to travel anxiety and sleep disruption, followed by six seizure-free weeks. Current anti-seizure regimen maintained with no dose changes.
- 1687: kind `unknown_frequency`, policy `single_fact`, primary ['llm:1687:1'], supporting ['det:1687:2'], rejected ['det:1687:1'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient reports several focal seizures last week, indicating recent seizure activity with unclear exact frequency. The phrase 'every 2 weeks' was rejected due to unclear temporality and less specific timing. The current burden is best summarized as multiple focal seizures in the past week.
- 1790: kind `frequency_rate`, policy `single_fact`, primary ['llm:1790:1'], supporting [], rejected [], flags [], minimal selector `different`, rich selector `same`. Summary: Patient reports 6 drop attacks and 2 epileptic spasms over the past 4 months, with events clustering around menstrual cycle phases. No prolonged convulsions or injuries. Current medication unchanged; ongoing monitoring and documentation planned.
- 1880: kind `frequency_rate`, policy `primary_with_context`, primary ['det:1880:3'], supporting ['det:1880:2', 'llm:1880:4', 'llm:1880:5', 'llm:1880:2', 'llm:1880:1'], rejected ['det:1880:5'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences approximately eight seizures over the past two months, including one drop attack and seven convulsions. He also reports focal onset events occurring several times per week and absence seizures clustered in threes monthly. The cluster absences and focal seizures are considered contextual and non-additive to the primary convulsion count. The burden has increased recently with injuries and drop attacks, prompting further evaluation.

### Rich Selector Differences

- 79: kind `frequency_rate`, policy `single_fact`, primary ['llm:79:1'], supporting ['llm:79:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports combined generalized and focal epilepsy with seizure frequency ≤ 6 to 7 per year, typically clustering around jet lag and sleep loss related to frequent travel. No injuries or hospital admissions. Current medications include lamotrigine and brivaracetam with good tolerability. Clobazam used PRN during travel-related high-risk periods. Adherence strategies reinforced. No immediate further imaging required; follow-up planned in 4 months or earlier if seizures increase.
- 338: kind `cluster_frequency`, policy `cluster_axis`, primary ['det:338:1', 'llm:338:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient has experienced many generalized convulsions in the past month, with events clustering after eastbound flights and consecutive nights of restricted sleep (3-4 hours). This pattern is consistent with breakthrough seizures triggered by disrupted sleep and rapid time-zone changes. The plan focuses on optimizing circadian alignment and medication timing to reduce seizure burden.
- 446: kind `frequency_rate`, policy `primary_with_context`, primary ['det:446:1'], supporting ['llm:446:3'], rejected ['llm:446:1', 'llm:446:2'], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences seizures up to twice per week, both nocturnally and during wakefulness, with variable clustering. This represents a clinical deterioration compared to historical frequencies in June and August. Adverse effects from polytherapy are significant, impacting function and quality of life. Further diagnostic evaluation and medication review are planned.
- 598: kind `frequency_rate`, policy `single_fact`, primary ['llm:598:1'], supporting ['llm:598:2'], rejected [], flags [], minimal selector `different`, rich selector `assessment_primary_subset`. Summary: Patient reports stable focal epilepsy with impaired awareness, experiencing approximately one seizure every eight months over the past 16 months. No secondary generalization or recent increase in frequency. Seizure diary corroborates this pattern. Triggers include sleep deprivation. Current antiepileptic therapy is effective and well tolerated.
- 744: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:744:1', 'llm:744:2'], supporting [], rejected ['det:744:1', 'det:744:2', 'det:744:3'], flags ['additive_policy_non_frequency_primary'], minimal selector `different`, rich selector `different`. Summary: The patient experiences frequent brief absence seizures on most weekdays, often clustering in the late afternoon, alongside one generalised tonic–clonic seizure in the last eight weeks. Fatigue and caregiving responsibilities are noted as potential triggers. Current antiepileptic regimen is maintained with plans for conservative monitoring and supportive measures to address fatigue and seizure triggers.
- 816: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:816:1'], supporting ['llm:816:3'], rejected ['llm:816:2'], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: The patient currently experiences occasional monthly seizures, typically brief focal-onset episodes with rapid recovery. There has been a marked improvement since starting ketogenic diet therapy, with fewer breakthrough events and better sleep reported by the family.
- 978: kind `frequency_rate`, policy `single_fact`, primary ['llm:978:3'], supporting ['llm:978:1', 'llm:978:2'], rejected [], flags [], minimal selector `different`, rich selector `different`. Summary: The patient currently experiences focal impaired-awareness seizures approximately every other month without clustering, representing a significant improvement from prior frequent clustered seizures occurring several times per day. Improved sleep hygiene and routine likely contributed to this better control.
- 1094: kind `frequency_rate`, policy `single_fact`, primary ['llm:1094:1'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_subset`. Summary: Patient reports 3 to 5 seizures last week, increased frequency compared to prior baseline associated with circadian disruption and inconsistent medication timing during recent international travel. No clusters or seizure-free intervals currently reported.
- 1165: kind `cluster_frequency`, policy `primary_with_context`, primary ['llm:1165:1'], supporting ['det:1165:1', 'llm:1165:2'], rejected [], flags [], minimal selector `assessment_primary_subset`, rich selector `different`. Summary: Patient experienced a cluster of 5 to 7 focal onset seizures over three weeks related to travel anxiety and sleep disruption, followed by six seizure-free weeks. Current anti-seizure regimen maintained with no dose changes.
- 1357: kind `frequency_rate`, policy `primary_with_context`, primary ['llm:1357:1'], supporting ['det:1357:1', 'llm:1357:2'], rejected [], flags [], minimal selector `same`, rich selector `different`. Summary: The patient experienced a single tonic-clonic seizure yesterday after missing two doses of sodium valproate and poor sleep. He had been largely stable for the past 18 months on sodium valproate prior to this breakthrough event. Adherence and sleep hygiene are emphasized to prevent further seizures.
- 1573: kind `cluster_frequency`, policy `cluster_axis`, primary ['llm:1573:1', 'llm:1573:2'], supporting [], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient experienced 11 focal seizures (five focal cognitive and six focal non-motor) over the last week, with several clustered over two consecutive mornings. There is clinical deterioration with escalating fatigue and irritability attributed to polytherapy. No witnessed generalized convulsions were noted. The patient is adherent to medication but seizure control remains suboptimal. Prolonged post-event disorientation was noted on one occasion. Further video-EEG monitoring is planned to clarify electroclinical pattern and guide treatment rationalization.
- 1591: kind `frequency_rate`, policy `additive_same_window`, primary ['llm:1591:1', 'llm:1591:2'], supporting ['det:1591:1', 'det:1591:2'], rejected [], flags [], minimal selector `same`, rich selector `assessment_primary_superset`. Summary: The patient reports a total of 11 focal seizures in the last month, including 5 focal onset seizures with impaired awareness and 6 focal non-motor seizures. No generalized tonic-clonic seizures were reported. Seizures are often triggered by flicker or bright light exposure. The patient is on stable levetiracetam therapy with good adherence and therapeutic blood levels. No auras or other seizure types noted. Safety measures and seizure diary are in place.
