# Gan 2026 Validation 53 Purist Misses Component Stress Analysis

This is a detailed triage and component-stress diagnostic report analyzing the 53 remaining Purist misses on the validation750 set for the `hybrid_parallel_state_candidate_reasoner` development candidate.

- Date: 2026-06-03
- Split: `validation` / `gan2026_split_v1` (750 rows)
- Total Purist Misses Analyzed: 53 / 750 (accuracy: 92.93%)
- Replay JSONL Source: `experiments/gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_deterministic_safety_floor_v2_replay_2026-06-03.jsonl`

## Executive Summary

The 53 Purist misses are classified into four key clinical failure mode families:

1. **Unknown Gold vs. Seizure-Free Predictions** (16 rows): The gold label is mapped to `unknown` (often because of ambiguous/non-epileptic events or distal historical references), but the deterministic safety floor and LLM adjudicator select a `seizure-free` interval. This is the largest single class of classification discrepancy.
2. **Wrong Frequency Bucket Mismatches** (17 rows): Discrepancies between monthly frequencies (e.g. monthly vs weekly, or specific bucket boundaries) where both gold and prediction agree that seizures are active, but the exact frequency rate or its parsing disagrees.
3. **Unresolved Multiple Mismatches** (16 rows): Notes where multiple active seizure types exist or there are vague multi-episode statements (such as `multiple per day` vs `seizure free for multiple year` or `1 per day`).
4. **Other Misses** (4 rows): Edge cases involving `unknown` gold labels mapped to specific rates due to context distractors.

## Failure Families Breakdown

### Unknown Gold vs. Seizure-Free Predictions (Count: 16)

| Row | Gold Label | Predicted (Adjudicated) | Deterministic Top | LLM Raw | Safety Floor Fired? |
|---|---|---|---|---|---|
| 3356 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | Yes |
| 3528 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `increased_frequency` | Yes |
| 5974 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `cluster_frequency` | No |
| 6077 | `unknown` | `seizure free for 8 month` | `seizure free for 8 month` | `seizure_free` | No |
| 6131 | `unknown` | `seizure free for 6 month` | `seizure free for 6 month` | `infrequent` | Yes |
| 6244 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | No |
| 6501 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `cluster_frequency` | Yes |
| 6571 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure_free` | No |
| 6987 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `infrequent` | No |
| 9888 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `sporadic` | No |
| 11216 | `unknown` | `seizure free for 4 month` | `seizure free for 4 month` | `seizure_free` | No |
| 11254 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure free` | No |
| 11259 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | No |
| 11272 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure_last_event` | No |
| 14025 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `2 per 6 weeks` | Yes |
| 14076 | `unknown` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | No |

#### Row-level Case Details

- **Row 3356**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Epilepsy Centre | To: kch.epilepsyclinic@nhs.net | Epilepsy Diagnosis: | Primary generalised epilepsy*
- **Row 3528**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Primary generalised epilepsy with prior generalised tonic–clonic seizures (first in 2006, relapse August 2018). EEG (October 2018) demonstrated generalised spike-and-wave activity consistent with generalised epilepsy. | Safety counselling, driving advice reiterated, and close monitoring with seizure diary. Bloods (FBC/U&E/LFTs) and repeat drug level planned. Review in 3 months or sooner if further...*
- **Row 5974**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected explicit seizure-free statements from deterministic and graph sources indicating no convulsive events reported in the past year.
  - **Clinical Context**: *This patient has focal epilepsy, with semiology of a rising epigastric sensation followed by behavioural arrest and impaired awareness lasting 1–2 minutes, occasionally progressing to right arm posturing. Remote history of mild traumatic brain injury in late adolescence is noted without lasting neurological deficit. Interval reports describe “Seizures with missed ASM doses,” typically occurring wi...*
- **Row 6077**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for 8 month`
  - **Adjudicator Rationale**: Consistent explicit seizure-free statement supported by deterministic candidate, state graph node, and LLM candidate.
  - **Clinical Context**: *Centre for Epilepsy | Centre for Epilepsy | - Fit note not required; employer letter offered regarding flexible scheduling around long-haul travel. | Since their last review, the patient reports one breakthrough episode on 12/09/2025 while on a late-evening flight from London to Lisbon (ï¿½row 18C). Witness description consistent with brief generalised stiffening followed by rhythmic movements las...*
- **Row 6131**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for 6 month`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Centre for Epilepsy | Diagnosis: Generalised epilepsy (patient has generalised epilepsy) | Not routinely monitored; no recent serum level requested as seizure control has been stable. | - Risks and benefits of continuing levetiracetam in pregnancy. She understands levetiracetam is generally considered compatible with pregnancy, and seizure control remains the priority.*
- **Row 6244**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Explicit negation of daytime convulsions supports seizure-free daytime status; nocturnal episodes frequency uncertain and not quantified, so seizure-free label applies to daytime convulsions only.
  - **Clinical Context**: *Thank you for reviewing this patient who has a diagnosis of generalised epilepsy. Since our last appointment, she describes episodes that her partner mainly witnesses during the night; however, he was not present at today’s review, so collateral details are second-hand. She reports feeling unrefreshed on waking on approximately two mornings per week and occasional tongue soreness, with bedclothes ...*
- **Row 6501**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Centre for Epilepsy | Centre for Epilepsy | Seizures: Patient reports "Periods of clustering followed by quiescence" in the context of work-related stress and dehydration in a commercial kitchen line setting. Clusters are described as brief episodes occurring over 2–3 days, often during consecutive evening shifts near the grill station, followed by several weeks without events. No consistent auras...*
- **Row 6571**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Consistent explicit seizure-free statements from deterministic candidate, state graph node, and LLM candidate with recent no events reported since mid-June 2025.
  - **Clinical Context**: *Centre for Epilepsy | Centre for Epilepsy | Seizures: Typical seizure event duration twenty seconds. Patient describes brief behavioural arrest with preserved awareness per family report, occurring in clusters during periods of missed or delayed doses in the past. No post‑ictal confusion reported. Last cluster was in early June 2025 during a documented delay in dispensing (ï¿½ two days without eve...*
- **Row 6987**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected the explicit seizure-free statement supported by deterministic and graph evidence.
  - **Clinical Context**: *Centre for Epilepsy | Centre for Epilepsy | Focal epilepsy with focal impaired awareness seizures; improved stability on current regimen | - Provide accessible seizure action plan and pictorial diary; carer to continue assisting with communication and event logging.*
- **Row 9888**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected explicit seizure-free statement supported by deterministic and graph evidence; no recent generalised tonic-clonic seizures since late last year.
  - **Clinical Context**: *Generalised epilepsy (primary generalised epilepsy) | - Seizure diary to continue; reinforce adherence to regular sleep and avoidance of alcohol excess | I reviewed Alex Turner in clinic today. They have a history of generalised epilepsy, supported by prior EEG demonstrating generalised spike-and-wave discharges, consistent with a primary generalised epilepsy syndrome. They have an implanted VNS, ...*
- **Row 11216**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for 4 month`
  - **Adjudicator Rationale**: Selected explicit date of last seizure on 25 December 2023 with no subsequent events reported, indicating current seizure freedom.
  - **Clinical Context**: *Epilepsy Centre | Subject: Review following workplace exposure and seizure control | Epilepsy Diagnosis: | Generalised epilepsy (primary generalised epilepsy phenotype).*
- **Row 11254**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected explicit seizure-free statements from deterministic and graph sources, corroborated by LLM evidence indicating no further events since last seizure.
  - **Clinical Context**: *Epilepsy history and current status: | This patient has focal epilepsy. Seizures have historically begun with a rising epigastric sensation and brief speech arrest, progressing on occasion to impaired awareness with right-hand automatisms; there have been no generalised tonic–clonic seizures reported in the past year. Last seizure on 31-May, described as a brief focal aware event lasting approxima...*
- **Row 11259**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected explicit seizure-free statement from deterministic and graph sources, supported by note text 'no clearly documented events since'.
  - **Clinical Context**: *Review today: She attended alone and brought her diary. She feels overall stability since the VNS was implanted, with fewer post-event headaches. Last seizure on 27 May as per diary entry; there have been no clearly documented events since then, and overall frequency is uncertain as some spells may represent panic or presyncopal episodes rather than definite seizures. She uses the VNS magnet at pr...*
- **Row 11272**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Explicit note states last seizure on 20/Dec with no seizures since then, supported by deterministic and graph evidence.
  - **Clinical Context**: *Epilepsy Centre | - Generalised epilepsy. | Thank you for reviewing Sophie Williams in our epilepsy clinic. She attended today with her mother. She reports that her migraine symptoms have been stable over the past year without requiring specific prophylaxis; however, our current focus remains her epilepsy management. She confirms that her last seizure on 20/Dec occurred in the early morning with a...*
- **Row 14025**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Summary/Diagnoses: Generalised epilepsy; history of traumatic brain injury (remote); persistent cognitive deficits; osteoporosis; former alcohol dependence with alcoholic hepatitis (in remission); currently in supported accommodation; smoker. Past variability in pharmacy supply documented; historical adherence impacted at times. | Epilepsy details: He has generalised epilepsy with prior history of...*
- **Row 14076**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected the explicit seizure-free statement supported by deterministic and graph evidence; no generalised tonic–clonic seizures reported.
  - **Clinical Context**: *Epilepsy Centre | To: neuro.epilepsyclinic@nhs.net | Epilepsy Diagnosis: | Primary generalised epilepsy. The patient has a history consistent with generalised epilepsy and reports recent worsening of events in the context of environmental triggers.*

### Wrong Frequency Bucket Mismatches (Count: 17)

| Row | Gold Label | Predicted (Adjudicated) | Deterministic Top | LLM Raw | Safety Floor Fired? |
|---|---|---|---|---|---|
| 5921 | `1 per 6 to 8 week` | `1 per day` | `1 per day` | `cluster_frequency` | Yes |
| 6094 | `3 per month` | `3 per week` | `3 per week` | `increased_frequency` | No |
| 6153 | `9 per month` | `1 per 1 to 2 week` | `1 per 1 to 2 week` | `increased frequency` | Yes |
| 7615 | `3 to 7 per month` | `2 per year` | `2 per year` | `cluster_frequency` | No |
| 9496 | `6 per 12 month` | `2 per week` | `2 per week` | `low frequency` | No |
| 10386 | `1 cluster per week, 2 to 3 per cluster` | `1 per day` | `1 per day` | `weekly clustering` | Yes |
| 12422 | `1 per day` | `4 per year` | `4 per year` | `nightly generalized convulsions` | Yes |
| 12438 | `1 per day` | `2 to 3 per year` | `2 to 3 per year` | `nightly` | Yes |
| 12456 | `1 per day` | `3 per year` | `3 per year` | `nightly generalised tonic-clonic seizures and intermittent tonic seizures three times per year` | No |
| 12460 | `1 per day` | `2 per year` | `2 per year` | `nightly generalised convulsions` | No |
| 12468 | `1 per day` | `4 per year` | `4 per year` | `nightly` | Yes |
| 13209 | `1 per 8 month` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `focal impaired-awareness seizure` | No |
| 14810 | `1 per month` | `12 per month` | `12 per month` | `seizure_free` | Yes |
| 14821 | `1 per month` | `17 per month` | `17 per month` | `seizure_free` | Yes |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `2 per 6 month` | `2 per 6 month` | `cluster_frequency` | No |
| 15672 | `1 per day` | `2 per 6 week` | `2 per 6 week` | `daily clusters` | Yes |
| 15986 | `11 per 3 month` | `1 per 5 to 7 day` | `1 per 5 to 7 day` | `1 per month` | No |

#### Row-level Case Details

- **Row 5921**:
  - **Gold**: `1 per 6 to 8 week` (purist category: `1 per 6 to 8 week`)
  - **Predicted**: `1 per day`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Centre for Epilepsy | Seizures: Patient reports intermittent events tending to cluster towards the later part of the night, typically occurring in the early hours before dawn, approximately once every 6–8 weeks. No clear warning symptoms; partner occasionally notes brief limb stiffening and a short period of confusion on waking. | We discussed practical measures around sleep hygiene and maintainin...*
- **Row 6094**:
  - **Gold**: `3 per month` (purist category: `3 per month`)
  - **Predicted**: `3 per week`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate from deterministic and graph sources, reflecting the current seizure frequency.
  - **Clinical Context**: *Thank you for asking me to review Sophie Martin, whom I last saw in clinic nine months ago. She describes a clear deterioration in her seizure control over the past six to eight weeks. She reports clusters of brief nocturnal warning sensations followed by loss of awareness on three occasions in September and two further events in early October. This worsening appears to coincide with a change to r...*
- **Row 6153**:
  - **Gold**: `9 per month` (purist category: `9 per month`)
  - **Predicted**: `1 per 1 to 2 week`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Thank you for your referral and for the accompanying details. I reviewed Sophie Bennett in clinic today following recent postpartum changes. She reports a clear deterioration over the past two months, with increasing fatigue, low mood, and a subjective sense that her seizures are clustering more often. She is breastfeeding and sleeping in fragmented blocks, which she feels has amplified both her t...*
- **Row 7615**:
  - **Gold**: `3 to 7 per month` (purist category: `3 to 7 per month`)
  - **Predicted**: `2 per year`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate supported by deterministic and graph sources; LLM cluster frequency is less precise for Gan scoring.
  - **Clinical Context**: *Summary/ Diagnoses: Generalised epilepsy with suspected catamenial pattern/primary generalised tonic-clonic seizures and brief focal features reported by witness/iron deficiency anaemia under GP review/migraine without aura. | Seizures: She describes short spells characterised by a sudden pause with fixed gaze and small chewing-like mouth movements, followed by quick recovery without confusion. Th...*
- **Row 9496**:
  - **Gold**: `6 per 12 month` (purist category: `6 per 12 month`)
  - **Predicted**: `2 per week`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate from deterministic and graph sources, consistent with note text 'two per week'.
  - **Clinical Context**: *Epilepsy Centre | To: kch.neuro-epilepsy@nhs.net | Epilepsy Diagnosis: | Primary generalised epilepsy (patient has generalised epilepsy) â€ with intermittent focal-aware events reported since late 2019.*
- **Row 10386**:
  - **Gold**: `1 cluster per week, 2 to 3 per cluster` (purist category: `1 cluster per week, 2 to 3 per cluster`)
  - **Predicted**: `1 per day`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Epilepsy Centre | To: kch.epilepsyclinic@nhs.net | Subject: Review – generalised epilepsy with weekly clustering | Re: Adult epilepsy review – history of childhood febrile seizures*
- **Row 12422**:
  - **Gold**: `1 per day` (purist category: `1 per day`)
  - **Predicted**: `4 per year`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Seizure control is inconsistent and while the caregiver perceives stability, she continues to have nightly generalised convulsions seizures and intermittent tonic seizures four times per year, this has been her enduring seizure profile for many years. The family keeps a calendar record which corroborates this pattern over the last 12 months. There are no identified new triggers; menses and intercu...*
- **Row 12438**:
  - **Gold**: `1 per day` (purist category: `1 per day`)
  - **Predicted**: `2 to 3 per year`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *- Clobazam 10 mg nocte (intermittent use for clusters) | - Arrange prolonged ambulatory EEG and MRI brain with epilepsy protocol to clarify seizure onset and aid risk stratification. | I reviewed Emily Carter in clinic today with her partner present. She reports a long-standing history of childhood febrile seizures, with no clear events through adolescence. In adulthood she developed recurrent sei...*
- **Row 12456**:
  - **Gold**: `1 per day` (purist category: `1 per day`)
  - **Predicted**: `3 per year`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate supported by deterministic and graph evidence; LLM adds context but does not change frequency count.
  - **Clinical Context**: *Epilepsy Centre | To: neuro.epilepsyclinic@nhs.net | Epilepsy Diagnosis: | Present Seizure Frequency:*
- **Row 12460**:
  - **Gold**: `1 per day` (purist category: `1 per day`)
  - **Predicted**: `2 per year`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate from deterministic and graph sources; nightly seizures mentioned by LLM are not quantified as frequency rate.
  - **Clinical Context**: *In discussing recent events with the patient and her caregiver, Seizure control is inconsistent and while the caregiver perceives stability, she continues to have nightly generalised convulsions seizures and intermittent tonic seizures two times per year, this has been her enduring seizure profile for many years. The caregiver keeps a diary and feels patterns are steady, whereas the patient highli...*
- **Row 12468**:
  - **Gold**: `1 per day` (purist category: `1 per day`)
  - **Predicted**: `4 per year`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Generalised epilepsy with longstanding nocturnal generalised tonic-clonic seizures and intermittent tonic seizures. EEG (previous studies) demonstrated generalised spike-and-wave discharges consistent with primary generalised epilepsy. | Clobazam 10 mg nocte (intermittent rescue dosing for clusters as per prior plan) | - Routine follow-up in 6 months, sooner if escalation in frequency or injury. |...*
- **Row 13209**:
  - **Gold**: `1 per 8 month` (purist category: `1 per 8 month`)
  - **Predicted**: `1 per 4 to 5 week`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate supported by deterministic and graph sources; aligns with diary clusters every 4-5 weeks indicating current seizure frequency.
  - **Clinical Context**: *Diagnoses/summary: Recurrent seizures of uncertain classification; catamenial pattern suspected based on symptom diary and menstrual tracking app entries; prior routine EEG non-diagnostic; MRI brain (2021) structurally unremarkable | I reviewed Jamie Turner in clinic today. He attended alone and brought printouts from his menstrual tracking app, which he uses to cross-reference his partner’s cycle...*
- **Row 14810**:
  - **Gold**: `1 per month` (purist category: `1 per month`)
  - **Predicted**: `12 per month`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Since her last routine contact with our service she has resumed a consistent dosing schedule and is keeping a seizure and symptom diary. She reports good adherence and no missed evening doses in the past month. She had recurrent headaches following her seizures earlier this month, but these have now settled. On 12 May the absence episodes reduced significantly after she restarted Lamotrigine. Her ...*
- **Row 14821**:
  - **Gold**: `1 per month` (purist category: `1 per month`)
  - **Predicted**: `17 per month`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Centre for Epilepsy | Centre for Epilepsy | Diagnosis: Focal epilepsy | Monitoring: No recent bloods available; she prefers to attend a local phlebotomy service when transport is convenient. She will contact us if headaches recur, if she experiences new focal aware auras (e.g., déjà vu, rising epigastric sensations), or if there is any breakthrough impairment of awareness. She keeps a seizure diar...*
- **Row 15593**:
  - **Gold**: `1 cluster per 5 day, 2 to 4 per cluster` (purist category: `1 cluster per 5 day, 2 to 4 per cluster`)
  - **Predicted**: `2 per 6 month`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate from deterministic and graph sources, which is supported by explicit note text and aligns with observed nocturnal episodes.
  - **Clinical Context**: *Thank you for asking me to review your patient. I met her in clinic accompanied by her partner, and we also had a brief telephone contribution from a facilitator of her local peer support group. The patient has kept a contemporaneous diary and invited two group peers to observe two community episodes; their notes broadly align with the partner’s account. | Regarding frequency, the current pattern ...*
- **Row 15672**:
  - **Gold**: `1 per day` (purist category: `1 per day`)
  - **Predicted**: `2 per 6 week`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Epilepsy Centre | Symptomatic generalised epilepsy. | I reviewed Emily Dawson in clinic today. She attends alone and reports a notable deterioration in her seizure control over the past 4–5 months. Historically, she has generalised epilepsy and she has a past history of atonic seizures, drop attacks and generalised tonic–clonic seizures one to two times per year, but seizure control has been excel...*
- **Row 15986**:
  - **Gold**: `11 per 3 month` (purist category: `11 per 3 month`)
  - **Predicted**: `1 per 5 to 7 day`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate from deterministic and graph sources, supported by consistent evidence 'every 5–7 days'.
  - **Clinical Context**: *Epilepsy Centre | To: kch-epilepsy@nhs.net | Epilepsy Diagnosis: | Focal epilepsy, probable temporal lobe onset, with secondary generalisation reported on two occasions historically. Patient has focal epilepsy.*

### Unresolved Multiple Mismatches (Count: 16)

| Row | Gold Label | Predicted (Adjudicated) | Deterministic Top | LLM Raw | Safety Floor Fired? |
|---|---|---|---|---|---|
| 4690 | `multiple per day` | `seizure free for multiple year` | `seizure free for multiple year` | `frequent` | No |
| 5534 | `1 per multiple month` | `seizure free for multiple year` | `seizure free for multiple year` | `infrequent` | No |
| 6209 | `multiple per day` | `1 per day` | `1 per day` | `daily and monthly seizures` | Yes |
| 6889 | `multiple per week` | `1 per 2 to 3 week` | `1 per 2 to 3 week` | `3 per 6 months` | No |
| 9937 | `1 cluster per month, multiple per cluster` | `1 per multiple week` | `1 per multiple week` | `periodic_bursts` | Yes |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | `1 per 4 to 5 week` | `1 per 4 to 5 week` | `clustered` | No |
| 9955 | `1 cluster per month, multiple per cluster` | `1 per month` | `1 per month` | `cluster_frequency` | No |
| 10618 | `unknown, 4 to 6 per cluster` | `seizure free for multiple year` | `seizure free for multiple year` | `cluster_frequency` | No |
| 10677 | `1 cluster per month, multiple per cluster` | `1 per month` | `1 per month` | `monthly clusters` | No |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `1 to 2 cluster per month, multiple per cluster` | `1 to 2 cluster per month, multiple per cluster` | `1-2 clusters per month` | No |
| 13843 | `seizure free for multiple month` | `no seizure frequency reference` | `no seizure frequency reference` | `rare` | No |
| 13858 | `seizure free for multiple month` | `no seizure frequency reference` | `no seizure frequency reference` | `unknown` | Yes |
| 13889 | `seizure free for multiple month` | `no seizure frequency reference` | `no seizure frequency reference` | `reduced frequency` | No |
| 15168 | `multiple per 15 month` | `seizure free for multiple year` | `seizure free for multiple year` | `seizure_free` | No |
| 15193 | `multiple per 13 month` | `seizure free for multiple year` | `seizure free for multiple year` | `unknown` | No |
| 15834 | `5 per week` | `1 per multiple month` | `1 per multiple month` | `5 times weekly` | Yes |

#### Row-level Case Details

- **Row 4690**:
  - **Gold**: `multiple per day` (purist category: `multiple per day`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected explicit clinical statement of no witnessed convulsions since last contact, supported by deterministic and graph evidence; EEG frequent electrographic seizures are not clinically correlated events.
  - **Clinical Context**: *Given the constraints of his offshore work and the proximity of his next onshore window, we agreed to maintain his current regimen until an in‑person review can be arranged to reconcile EEG activity with symptom diaries and undertake bloods for therapeutic levels and safety monitoring. He will keep a detailed log of alertness, any brief lapses, and potential triggers (sleep loss, dehydration, work...*
- **Row 5534**:
  - **Gold**: `1 per multiple month` (purist category: `1 per multiple month`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected explicit seizure-free statement from deterministic and graph sources despite LLM noting a recent infrequent event; the recent event is described as brief and isolated, not a generalised tonic–clonic seizure.
  - **Clinical Context**: *Mrs Emily Carter is known to have generalised epilepsy. She reports a very infrequent, short event a fortnight ago, described as a sudden pause with eyelid fluttering and brief unresponsiveness lasting under 10 seconds, with immediate recovery and no injury. This is the first such occurrence in several months and represents an isolated, fleeting episode on an otherwise stable background. | Plan: I...*
- **Row 6209**:
  - **Gold**: `multiple per day` (purist category: `multiple per day`)
  - **Predicted**: `1 per day`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Previous medication: Levetiracetam (behavioural irritability, seizures persisted), Sodium valproate (weight gain and tremor), Carbamazepine (dizziness, hyponatraemia), Lamotrigine (partial benefit but ongoing events), Clobazam PRN (some reduction in clusters), Lacosamide (no clear benefit), Topiramate (word-finding difficulty), Zonisamide (appetite suppression and insomnia). | - Clobazam 10 mg at ...*
- **Row 6889**:
  - **Gold**: `multiple per week` (purist category: `multiple per week`)
  - **Predicted**: `1 per 2 to 3 week`
  - **Adjudicator Rationale**: Selected the highest current seizure frequency for focal seizures, supported by deterministic and graph evidence, reflecting the most frequent clinically relevant seizure pattern.
  - **Clinical Context**: *Diagnoses/summary: Combined generalised and focal epilepsy (patient has both generalised and focal epilepsy), longstanding; learning points from prior work-up include mixed semiologies consistent with dual network involvement | Previous medication: sodium valproate (weight gain, tremor), carbamazepine (rash), lamotrigine (partial benefit), levetiracetam (irritability), topiramate (cognitive slowin...*
- **Row 9937**:
  - **Gold**: `1 cluster per month, multiple per cluster` (purist category: `1 cluster per month, multiple per cluster`)
  - **Predicted**: `1 per multiple week`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Centre for Epilepsy | Centre for Epilepsy | - Seizure diary to continue; please note pattern description below for ongoing monitoring. | - Review in six months; bring updated diary and any witness accounts if available.*
- **Row 9943**:
  - **Gold**: `1 cluster per 4 to 5 week, multiple per cluster` (purist category: `1 cluster per 4 to 5 week, multiple per cluster`)
  - **Predicted**: `1 per 4 to 5 week`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate from deterministic and graph sources, supported by LLM evidence describing clustering every 4-5 weeks.
  - **Clinical Context**: *Thank you for referring this patient for neurological review. I met him today in clinic accompanied by his partner. He described longstanding episodes that he and his family have termed “spells,” beginning in his late teens. The events are stereotyped: he experiences a brief warning of a rising internal tension and a sense of detachment, followed by behavioural arrest with fixed gaze and lip chewi...*
- **Row 9955**:
  - **Gold**: `1 cluster per month, multiple per cluster` (purist category: `1 cluster per month, multiple per cluster`)
  - **Predicted**: `1 per month`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate supported by deterministic and graph evidence; LLM describes clustering but does not contradict the monthly frequency rate.
  - **Clinical Context**: **
- **Row 10618**:
  - **Gold**: `unknown, 4 to 6 per cluster` (purist category: `unknown, 4 to 6 per cluster`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected the explicit seizure-free statement supported by deterministic and graph evidence; LLM cluster frequency reflects prior events but current state is seizure free.
  - **Clinical Context**: *- MRI brain with epilepsy protocol already requested; await appointment | - Provide seizure diary to track timing, duration, potential triggers, and post-event features | - Follow-up neurology clinic in 4 months, earlier if clusters escalate or medication intolerance occurs | Regarding frequency, the patient reports that episodes tend to come in small runs: typically around four to six short spell...*
- **Row 10677**:
  - **Gold**: `1 cluster per month, multiple per cluster` (purist category: `1 cluster per month, multiple per cluster`)
  - **Predicted**: `1 per month`
  - **Adjudicator Rationale**: LLM candidate provides the most clinically relevant and detailed recent seizure frequency pattern over the last three months, describing clusters monthly, which aligns with the note's detailed description beyond the simple 'once a month' frequency from deterministic and graph sources.
  - **Clinical Context**: *Centre for Epilepsy | Centre for Epilepsy | - Rescue plan discussed for early-morning episodes; midazolam buccal 5 mg prescribed for clusters lasting over 10 minutes or repeated spells within one hour; partner trained and written guidance provided. | - Seizure triggers diary to continue, with emphasis on sleep pattern and shift changes.*
- **Row 10996**:
  - **Gold**: `1 to 2 cluster per month, 4 per cluster` (purist category: `1 to 2 cluster per month, 4 per cluster`)
  - **Predicted**: `1 to 2 cluster per month, multiple per cluster`
  - **Adjudicator Rationale**: Consistent evidence across deterministic, graph, and LLM sources all indicate morning clusters one to two times per month.
  - **Clinical Context**: *Epilepsy Centre | Epilepsy Diagnosis: | Combined generalised and focal epilepsy (patient reports both generalised and focal epilepsy). | Present Seizure Frequency:*
- **Row 13843**:
  - **Gold**: `seizure free for multiple month` (purist category: `seizure free for multiple month`)
  - **Predicted**: `no seizure frequency reference`
  - **Adjudicator Rationale**: Patient and partner diary shows fewer episodes over the past six weeks indicating reduced frequency
  - **Clinical Context**: *Thank you for asking me to review your patient, whom I saw in clinic today with his partner. He described a long history of intermittent episodes that have varied over the years. The current concerns relate to brief spells of behavioural arrest with a sense of pressure in the chest and a tendency to pace or fidget, usually lasting a few minutes, without clear loss of awareness, and without tongue ...*
- **Row 13858**:
  - **Gold**: `seizure free for multiple month` (purist category: `seizure free for multiple month`)
  - **Predicted**: `no seizure frequency reference`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *None for seizure control at present. Uses over-the-counter vitamin D and a multivitamin. | - Neurology review in 9–12 months, sooner if episodes change in character, increase in frequency, or if there is any injury, loss of awareness without clear precipitant, or witnessed convulsive activity.*
- **Row 13889**:
  - **Gold**: `seizure free for multiple month` (purist category: `seizure free for multiple month`)
  - **Predicted**: `no seizure frequency reference`
  - **Adjudicator Rationale**: LLM candidate provides current clinical state with explicit evidence of less intrusive events after sleep hygiene and jet-lag plan, which is more informative than no seizure frequency reference.
  - **Clinical Context**: *Medication history: Previously tried levetiracetam (fatigue, irritability), carbamazepine (dizziness), lamotrigine (no clear benefit), and lacosamide (nausea). Not previously tried: topiramate, zonisamide, pregabalin, clobazam, perampanel. | Today’s review: I conducted a scheduled telephone review as she is currently abroad on business. She reports that since adopting stricter sleep hygiene during...*
- **Row 15168**:
  - **Gold**: `multiple per 15 month` (purist category: `multiple per 15 month`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected explicit seizure-free statement 'no generalised seizures since' supported by deterministic and graph evidence, consistent with LLM evidence specifying no generalised seizures since 9 - 2018.
  - **Clinical Context**: *Combined generalised and focal epilepsy – patient has both generalised and focal epilepsy.*
- **Row 15193**:
  - **Gold**: `multiple per 13 month` (purist category: `multiple per 13 month`)
  - **Predicted**: `seizure free for multiple year`
  - **Adjudicator Rationale**: Selected explicit seizure-free statement for generalised seizures; brief absence seizures noted but do not negate seizure-free status for generalised seizures.
  - **Clinical Context**: *Thank you for asking me to review your patient. He has a background history of migraine, noted over many years, but the current clinical focus is epilepsy. He reports a clear improvement in his seizure control over the past year. He has had no generalised seizures since 9 - 2022, though continues to experience brief absence from time to time. These brief episodes are described as sudden lapses in ...*
- **Row 15834**:
  - **Gold**: `5 per week` (purist category: `5 per week`)
  - **Predicted**: `1 per multiple month`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *- Continue levetiracetam 1 g twice daily for now. We discussed potential adjustments, but agreed to collate additional event data first, given the recent change in frequency and the need to clarify semiology and triggers. | - Provide a seizure diary template; the patient will log timing, context, sleep, stress, and menses. Occupational health will submit monthly summaries directly to clinic with p...*

### Other Misses (Count: 4)

| Row | Gold Label | Predicted (Adjudicated) | Deterministic Top | LLM Raw | Safety Floor Fired? |
|---|---|---|---|---|---|
| 6321 | `unknown` | `1 per day` | `1 per day` | `unknown` | Yes |
| 6368 | `unknown` | `1 per 1 to 2 week` | `1 per 1 to 2 week` | `3 seizures per 6 weeks` | No |
| 7168 | `unknown` | `2 per year` | `2 per year` | `occasional catamenial clustering` | No |
| 10266 | `unknown` | `1 per 5 day` | `1 per 5 day` | `unknown` | Yes |

#### Row-level Case Details

- **Row 6321**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `1 per day`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Centre for Epilepsy | Seizures: The patient reports that spells are uncommon when meals are regular; when they go long hours without food, brief collapses with confusion have occurred on two recent occasions (July and September 2025). No injuries. No reported auras or prolonged events. | We discussed practical measures around maintaining regular meals and hydration during long outdoor work periods...*
- **Row 6368**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `1 per 1 to 2 week`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate from deterministic and graph sources, consistent with note text 'once every one to two weeks'.
  - **Clinical Context**: *I reviewed Michael Turner in clinic today following a period of clinical decline. Since undertaking recent long-haul travel across several time zones, he reports marked circadian disruption with difficulty initiating and maintaining sleep. Over the past six weeks he describes three witnessed convulsive episodes and several brief staring events with loss of awareness. Of note, he identifies a patte...*
- **Row 7168**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `2 per year`
  - **Adjudicator Rationale**: Selected the highest normalized current frequency candidate from deterministic and graph sources; LLM catamenial clustering is a pattern descriptor, not a frequency label.
  - **Clinical Context**: *Primary generalised epilepsy with occasional catamenial clustering | EEG (June 2025): Generalised spike-and-wave discharges consistent with generalised epilepsy | - Refer to epilepsy specialist nurse for care planning and NHS pathway orientation; interpreter to be arranged as needed | - Consider perimenstrual dose optimisation or alternative catamenial strategy if breakthrough events persist; to b...*
- **Row 10266**:
  - **Gold**: `unknown` (purist category: `unknown`)
  - **Predicted**: `1 per 5 day`
  - **Adjudicator Rationale**: Deterministic safety-floor fallback: the adjudicator's repaired answer disagreed with the deterministic top candidate, so the transparent deterministic prediction remains prediction-bearing.
  - **Clinical Context**: *Epilepsy Centre | To: neuro.epilepsy@nhs.net | Epilepsy Diagnosis: | Present Seizure Frequency:*
