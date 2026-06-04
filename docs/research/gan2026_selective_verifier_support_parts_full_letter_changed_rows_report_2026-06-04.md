# Selective Verifier Full-Letter Changed Row Mechanics

This report expands every row whose decision changed in the `support_parts_full_letter` live run. It includes the reconstructed full model input, raw model output, parsed output, scoring delta, and an interpretation. This is validation-development analysis only; it does not authorize prediction-bearing use, locked-test inspection, or benchmark-comparable claims.

## Source Artifacts

- Run report: `docs/research/gan2026_selective_verifier_support_parts_full_letter_live_gpt41mini_2026-06-04.md`
- Row JSONL: `experiments/gan2026_selective_verifier_support_parts_full_letter_live_gpt41mini_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_verifier_support_parts_full_letter_live_gpt41mini_2026-06-04.json`
- Predeclaration JSONL: `experiments/gan2026_selective_verifier_predeclaration_2026-06-04.jsonl`
- Source notes: `data/Gan (2026)/synthetic_data_subset_1500.json`

## Summary

| Metric | Value |
| --- | ---: |
| row count | 42 |
| call ok rows | 41 |
| parse ok rows | 41 |
| parse error rows | 1 |
| decision changed rows | 24 |
| changed scorable rows | 13 |
| changed decision precision | 0.615 |
| w to c vs routing rows | 5 |
| c to w vs routing rows | 1 |
| c to review vs routing rows | 4 |
| w to review vs routing rows | 6 |
| unchanged rows | 18 |

Changed rows: 190, 338, 744, 869, 959, 1363, 1694, 4368, 5921, 6153, 6209, 6321, 6889, 7168, 7615, 10677, 10996, 11259, 12438, 12460, 13209, 15193, 15593, 15672.

## Row Index

| Row | Action | Label | Delta | Interpretation |
| ---: | --- | --- | --- | --- |
| 190 | `use_proposed_answer` | `1 per 4 week` | `W_to_C` | Good recovery. The full letter gives a recurring cluster cadence every four weeks; approving the proposed label corrects routing unknown, though the row should still be reviewed for cluster wording portability. |
| 338 | `use_proposed_answer` | `multiple per month` | `C_to_C_changed` | Benign changed render. The model approved a label that stays correct, so this is not a regression, but it does not add net value beyond preserving a correct row. |
| 744 | `parse_error` | `None` | `W_to_W_changed` | No clinical conclusion: the API call failed, so the changed accounting is an artifact of missing output. This row should be rerun before interpreting the design. |
| 869 | `use_unknown` | `unknown` | `W_to_W_changed` | Conservative but still wrong relative to gold. The model chose unknown, matching the uncertainty posture but not recovering the missed frequency. |
| 959 | `needs_review` | `None` | `W_to_review` | Over-conservative. The model sent the row to review rather than making a scorable correction; this increases review load without a prediction-bearing win. |
| 1363 | `needs_review` | `None` | `W_to_review` | Over-conservative. The model identified uncertainty and chose review, which may be safe clinically but does not improve the routing label. |
| 1694 | `needs_review` | `None` | `W_to_review` | Over-conservative. The model avoided rendering a questionable proposed answer, but the result remains non-scorable and should count as review burden. |
| 4368 | `use_unknown` | `unknown` | `W_to_W_changed` | Conservative wrong-to-wrong. The model chose unknown, preserving the safe posture but not recovering the gold state. |
| 5921 | `needs_review` | `None` | `W_to_review` | Over-conservative. The model refused a complex cluster proposal; safe, but not a prediction-bearing improvement. |
| 6153 | `use_proposed_answer` | `9 per 4 week` | `W_to_C` | Strong recovery. The full letter clearly supports 3 nocturnal convulsions plus 6 focal aware events in four weeks, so approving 9 per 4 week is well grounded. |
| 6209 | `needs_review` | `None` | `C_to_review` | Good safety behavior. The model rejected 2 to 3 per day because the text separates daily brief events from 2 to 3 longer monthly episodes. |
| 6321 | `needs_review` | `None` | `C_to_review` | Safe review. The model avoided rendering a row that routing had correct as unknown/review; this is not prediction-bearing but avoids a wrong label. |
| 6889 | `use_proposed_answer` | `3 per 6 month` | `C_to_W` | Safety failure. The model approved the tonic-clonic count and incorrectly called it current highest frequency despite myoclonic jerks several times per week. This is the full-letter variant's C->W regression. |
| 7168 | `needs_review` | `None` | `C_to_review` | Good safety behavior. The model saw that two tonic-clonic seizures over a year does not justify cluster syntax and kept the row out of prediction-bearing use. |
| 7615 | `use_proposed_answer` | `1 cluster per month, 3 to 6 per cluster` | `W_to_C` | Good recovery. Full context supports perimenstrual clusters with 3 to 6 episodes per cycle, and the competing tonic-clonic events are less frequent. |
| 10677 | `use_proposed_answer` | `1 per month` | `W_to_W_changed` | Wrong-to-wrong render. The model approved a plausible monthly answer, but the row remains incorrect under the scorer; this is not useful evidence for promotion. |
| 10996 | `use_proposed_answer` | `1 to 2 cluster per month, 4 per cluster` | `W_to_C` | Strong recovery. The text directly states one to two morning clusters per month and about four events per cluster. |
| 11259 | `use_proposed_answer` | `unknown` | `W_to_W_changed` | Wrong-to-wrong oddity. The model selected the proposed answer even though the proposed answer is unknown; it remains non-improving and should be treated as noisy. |
| 12438 | `needs_review` | `None` | `W_to_review` | Over-conservative. The model chose review rather than committing to the proposed low-frequency answer, increasing review burden. |
| 12460 | `needs_review` | `None` | `W_to_review` | Over-conservative. The model sent a low-frequency row to review; safe, but not a scorable gain. |
| 13209 | `use_unknown` | `unknown` | `W_to_W_changed` | Conservative wrong-to-wrong. The model chose unknown, which is safe but does not recover the correct answer. |
| 15193 | `needs_review` | `None` | `C_to_review` | Good safety behavior with full context. The model saw ongoing absence seizures and rejected the zero-generalized-seizure answer as not applying to all seizure types. |
| 15593 | `use_proposed_answer` | `1 cluster per 5 day, 2 to 4 per cluster` | `W_to_C` | Good recovery. The text supports clusters every five days with 2 to 4 events per cluster, so approving the proposed cluster answer is grounded. |
| 15672 | `use_proposed_answer` | `multiple per day` | `W_to_W_changed` | Wrong-to-wrong render. The model approved a broad multiple-per-day answer but did not fix the row under the scoring policy. |

## Changed Row Details

### Row 190

Interpretation: Good recovery. The full letter gives a recurring cluster cadence every four weeks; approving the proposed label corrects routing unknown, though the row should still be reviewed for cluster wording portability.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_C",
  "design_action": "use_proposed_answer",
  "gold_label": "1 per 4 week",
  "parse_errors": [],
  "proposed_answer": "1 per 4 week",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 190,
  "verifier_label": "1 per 4 week"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 02 October 2025 \n\nDr Wang\nSaffron Park Hospital\n\nSaffron Park, London, E14 7JL\nDear Dr Wang\nAlex Carter, DOB: 14-05-2006, Hospital No: P903772 NHS No. 7712390045\nFlat 3, 12 Kingsbridge Lane, London, E14 6PA \n\nI reviewed the above patient in the Adult Neurology Clinic today following transition from paediatric services. A parent attended and contributed helpful collateral history. He has a confirmed diagnosis of generalised epilepsy.\n\nThis is our first adult clinic review post-transition. From the joint handover summary and today’s history, his typical episodes comprise brief staring spells with eyelid flutter and occasional myoclonic jerks shortly after waking. Generalised tonic–clonic seizures have been infrequent. At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress. His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since.\n\nHe is taking Sodium Valproate 500 mg b.d. and Levetiracetam (Keppra) 1 g b.d. with good adherence. He describes mild morning lethargy and intermittent low mood around examination periods, which he and his parent feel are manageable. No rashes, visual disturbance, or focal neurological symptoms were reported. There is no history of focal onset phenomena. He is not driving.\n\nOn examination today he was alert and oriented with normal speech and language. Cranial nerves were intact, tone and power were normal in all limbs, reflexes were symmetric, and coordination and gait were normal. There were no neurocutaneous stigmata.\n\nPaediatric EEGs have shown generalised spike–wave discharges, most recently in 2024. MRI brain (2023) was normal. We will arrange an updated EEG to reassess background and interictal activity in the adult service and to support ongoing management planning. Given his current pattern of absence clusters every 4 weeks without recent convulsions, I have not altered medication today. We discussed adherence, regular sleep, and stress management as practical measures that may help reduce breakthrough events. He and his parent were given information on our transition nurse specialist and epilepsy advisor should they wish to discuss education or lifestyle issues further.\n\nI have asked him to keep a simple seizure diary, noting any absence clusters and possible triggers, particularly sleep loss. We will review him in 6 months, or sooner if events increase in frequency, if he experiences any adverse effects, or if a generalised tonic–clonic seizure recurs.\n\nYours sincerely",
  "competing_possibilities": [
    "Generalised tonic–clonic seizures are infrequent, last in May 2025"
  ],
  "evidence_snippet": "At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "1 per 4 week",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress."
  ],
  "reason": "The clinical text clearly states the patient currently experiences clusters of brief absence episodes every 4 weeks, which provides the seizure/event type (brief absence episodes), the count (clusters), and the timeframe (every 4 weeks). This supports the proposed answer of '1 per 4 week' as the current highest seizure frequency.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress."
  ],
  "reason": "The clinical text clearly states the patient currently experiences clusters of brief absence episodes every 4 weeks, which provides the seizure/event type (brief absence episodes), the count (clusters), and the timeframe (every 4 weeks). This supports the proposed answer of '1 per 4 week' as the current highest seizure frequency.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 338

Interpretation: Benign changed render. The model approved a label that stays correct, so this is not a regression, but it does not add net value beyond preserving a correct row.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "C_to_C_changed",
  "design_action": "use_proposed_answer",
  "gold_label": "multiple per month",
  "parse_errors": [],
  "proposed_answer": "multiple per month",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 338,
  "verifier_label": "multiple per month"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Department of Neurology \n\nClinic Date: 02 October 2025 \n\nDr Green  \nSt Thomas' Hospital  \nDepartment of Neurology, Westminster Bridge Road, London SE1 7EH  \n\nDear Dr Green,  \n\nMichael Turner, DOB: 22-03-1981, Hospital No: H947520 NHS No. 9057314628  \nFlat 12, 5 Riverside Walk, London, SE1 9PP \n\nDiagnoses: \n\nGeneralised epilepsy with prior EEG demonstrating generalised spike-and-wave activity (2017) \n\nCurrent Medication: \n\nLevetiracetam 1 g bd  \nClobazam 10 mg nocte (prn for travel-related sleep disruption) \n\nPlan: \n\n- Optimise sleep hygiene around long-haul travel; structured jet‑lag plan provided  \n- Adjust Levetiracetam timing to destination time zone within 24–48 hours of arrival  \n- Continue current regimen; consider sodium valproate only if inadequate control persists after optimisation and discussion of risks  \n- Arrange ambulatory EEG if further breakthrough events occur despite adherence  \n- Provide fit note guidance and safety advice regarding driving, swimming, heights, and machinery  \n- Telephone follow‑up in 6 weeks, video review in 3 months  \n\nI reviewed Michael Turner via scheduled telephone appointment today, consistent with his frequent business travel pattern across multiple time zones. He reports irregular sleep, prolonged flights, and variable meal schedules, often with overnight work calls. Over the last four weeks he has experienced many convulsions in past month, described as sudden loss of awareness followed by generalised tonic–clonic activity lasting 1–2 minutes with tongue‑bite on one occasion and post‑ictal confusion for up to an hour. These events clustered after eastbound flights and consecutive nights of restricted sleep (3–4 hours). There is no reported alcohol excess; adherence to medication is generally good, though he occasionally takes the evening dose late when transiting. He denies focal auras, focal neurological deficit, or head injury. \n\nThe clinical picture remains in keeping with generalised epilepsy. He previously had an EEG in 2017 showing generalised spike‑and‑wave discharges, and a normal MRI brain. Bloods last month (U&E, LFT, FBC, B12, folate, TSH) were unremarkable. There are no intercurrent infections. \n\nWe discussed practical measures tailored to his travel: bringing a medication schedule card aligned to destination time, setting dual‑time alarms, avoiding red‑eye flights where feasible, and prioritising the first two nights of consolidated sleep. I advised he keeps a rescue plan; clobazam has been helpful around long‑haul trips and can be used cautiously for anticipated sleep deprivation. I also provided written seizure first‑aid for colleagues. \n\nDriving: he is aware of DVLA guidance; given recent generalised seizures, he should refrain from driving and will seek advice per Group 1 licensing regulations. Safety counsel provided regarding showers (prefer baths avoided or with supervision), working at heights, and operating heavy machinery. \n\nI have not arranged routine blood monitoring for Levetiracetam. If further convulsions occur despite the above strategies and confirmed adherence, we will discuss alternative agents (notably sodium valproate, acknowledging teratogenicity is not a consideration for him) or adjuncts. Ambulatory EEG may help quantify interictal burden during travel weeks. \n\nIn summary, breakthrough seizures have coincided with disrupted sleep and rapid time‑zone changes; there have been many convulsions in past month. The plan focuses on optimising circadian alignment and dosing timing, with close follow‑up by phone. \n\nYours sincerely, \n\nÃ‚Â· Dr ï¿½A. Patel  \nConsultant Neurologist â€‚  \nDepartment of Neurology, St Thomas' Hospital \n\nWith best wishes,",
  "competing_possibilities": [],
  "evidence_snippet": "Over the last four weeks he has experienced many convulsions in past month, described as sudden loss of awareness followed by generalised tonic–clonic activity lasting 1–2 minutes with tongue‑bite on one occasion and post‑ictal confusion for up to an hour.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "multiple per month",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": "true",
  "count_supported": "true",
  "current_highest_frequency_supported": "true",
  "missing_or_conflicting_parts": [],
  "quotes": [
    "Over the last four weeks he has experienced many convulsions in past month, described as sudden loss of awareness followed by generalised tonic–clonic activity lasting 1–2 minutes with tongue‑bite on one occasion and post‑ictal confusion for up to an hour."
  ],
  "reason": "The clinical text explicitly states that over the last four weeks (past month) the patient has experienced many convulsions, which supports the count ('multiple') and timeframe ('per month') for generalised tonic–clonic seizures. The seizure type, count, and timeframe are all clearly documented, supporting the proposed answer.",
  "recommended_action": ["use_proposed_answer"],
  "seizure_or_event_type_supported": "true",
  "timeframe_supported": "true"
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "Over the last four weeks he has experienced many convulsions in past month, described as sudden loss of awareness followed by generalised tonic–clonic activity lasting 1–2 minutes with tongue‑bite on one occasion and post‑ictal confusion for up to an hour."
  ],
  "reason": "The clinical text explicitly states that over the last four weeks (past month) the patient has experienced many convulsions, which supports the count ('multiple') and timeframe ('per month') for generalised tonic–clonic seizures. The seizure type, count, and timeframe are all clearly documented, supporting the proposed answer.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 744

Interpretation: No clinical conclusion: the API call failed, so the changed accounting is an artifact of missing output. This row should be rerun before interpreting the design.

Row summary:

```json
{
  "call_errors": [
    "RuntimeError: OpenAI HTTP 503: upstream connect error or disconnect/reset before headers. retried and the latest reset reason: connection timeout"
  ],
  "call_status": "error",
  "delta": "W_to_W_changed",
  "design_action": "parse_error",
  "gold_label": "multiple per week",
  "parse_errors": [
    "call_error_no_output"
  ],
  "proposed_answer": "multiple per week",
  "quotes_exact": false,
  "routing_policy_action": "route_review",
  "routing_policy_label": null,
  "source_row_index": 744,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "St Mary's Hospital \n\nInstitute of Neurology \n\nClinic Date: 02 October 2025 \n\nDr Ahmed  \nSt Mary's Hospital  \nInstitute of Neurology, St Mary's Hospital, London W2 1NY  \n\nDear Dr Ahmed,  \n\nSophie Williams, DOB: 23-04-1991, Hospital No: H583920 NHS No. 9842157306  \n12 Briar Close, London, W10 5QP \n\nMedication: \n\nValproate (Epilim) 500 mg morning / 1000 mg evening. Levetiracetam (Keppra) 750 mg twice daily. \n\nI reviewed Sophie Williams in clinic today. She has generalised epilepsy with typical absence episodes and occasional generalised tonic–clonic seizures. Over the past two months she reports brief absences occurring on most weekdays, often clustering around late afternoon when she is more tired. There has been one generalised tonic–clonic seizure in the last eight weeks, witnessed at home. \n\nHer primary carer accompanied her and notes that increased fatigue has been noticeable since the levetiracetam dose was optimised three months ago. The carer also reports that the patient’s caregiving responsibilities at home (supporting an elderly relative with mobility needs) have led to shortened sleep and irregular mealtimes, which may be lowering her threshold for breakthrough events. The patient describes the tiredness as \"heavy\" by early evening and finds concentration dips during routine tasks. No new focal features, no injuries, and recovery is prompt after the briefer events. \n\nOn current therapy, tolerability is otherwise acceptable: no mood instability beyond mild irritability late in the day, no gastrointestinal upset, and weight stable. She is using a pill organiser and has not missed doses to her knowledge. There is no reported alcohol use and caffeine is modest. Menses are regular and not clearly linked to a change in seizure pattern. \n\nGiven the frequency pattern—most weekdays for brief absences with infrequent generalised convulsions—we discussed strategies to address fatigue and reduce triggers in the caregiving context. The patient and carer prefer to maintain the present antiepileptic regimen for now and focus on sleep regularity and planned respite support. I have not changed medication today. We agreed the following: \n\n- Carer to coordinate short daily rest periods for the patient, aiming for a consistent sleep window and a brief early afternoon break.  \n- Hydration and regular meals to reduce late-day dips that appear to precede absences.  \n- Seizure diary to log timing in relation to sleep debt and caregiving tasks, to guide any future dose adjustments.  \n\nSafety and driving were reviewed in accordance with DVLA guidance for generalised epilepsy. The patient is aware of the need to avoid bath bathing unsupervised and to take extra care with cooking when overtired. We also discussed community support options; the carer will contact the local carers’ centre regarding respite. \n\nIf the weekday absences persist at the current rate or increase, we would consider a modest evening uptitration of levetiracetam to 1000 mg while monitoring mood and fatigue, or alternatively rationalising valproate to a more even split dosing. For now, plan is conservative monitoring given the patient’s preference. \n\nWe will review in three months, or sooner if she experiences more than two generalised tonic–clonic seizures in any four-week period, new injury, or concerning mood change. \n\nYours sincerely",
  "competing_possibilities": [
    "One generalised tonic–clonic seizure in last eight weeks noted, but less frequent than absences"
  ],
  "evidence_snippet": "Over the past two months she reports brief absences occurring on most weekdays, often clustering around late afternoon when she is more tired.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "multiple per week",
  "review_reasons": [
    "The count and timeframe may not belong together."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json

```

</details>

<details>
<summary>Parsed model output</summary>

```json
null
```

</details>

### Row 869

Interpretation: Conservative but still wrong relative to gold. The model chose unknown, matching the uncertainty posture but not recovering the missed frequency.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_W_changed",
  "design_action": "use_unknown",
  "gold_label": "multiple per month",
  "parse_errors": [],
  "proposed_answer": "unknown",
  "quotes_exact": true,
  "routing_policy_action": "route_review",
  "routing_policy_label": null,
  "source_row_index": 869,
  "verifier_label": "unknown"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 09 April 2019\n\nDr A. Patel\nRiverside Medical Practice\n\n12 Riverbank Way\nLondon SE1 5AB\nDear Dr A. Patel\nMichael Turner, DOB: 14-03-1955, Hospital No: H937521 NHS No. 8421905630\nFlat 3, 28 Willow Street, London, SE1 3JT \n\nDiagnoses/summary: History of recurrent unprovoked seizures of uncertain character and cause. Multiple routine EEGs previously nondiagnostic. No clear structural lesion identified on prior brain imaging per patient report.\n\nPrior medication trials (per patient and records): Sodium valproate (sedation and tremor), carbamazepine (skin rash), levetiracetam (irritability), lamotrigine (insufficient benefit), clobazam PRN (helpful for clusters but daytime drowsiness). No history of topiramate, zonisamide, lacosamide, perampanel, or brivaracetam use.\n\nComorbidities: Mild hypertension (on amlodipine). No known cardiac murmur. No history of head injury or CNS infection. No family history of epilepsy recalled.\n\nI reviewed Michael Turner in clinic today. He is a newly retired secondary-school teacher living alone. He reports a predictable daily routine with early mornings, scheduled walks, and reduced social interaction since retirement. He keeps a seizure diary on paper and on his phone. He describes episodes that remain variably stereotyped. He notes that over the course of most calendar cycles he will have several events, sometimes in loose clusters, with longer quiet spells in between. He associates poorer sleep and missed meals with increased likelihood of events. He denies tongue biting or prolonged post-event confusion in every instance, though on occasion he experiences notable fatigue afterwards. There is no clear photic trigger, and he does not drive.\n\nCurrent medication:\n- Amlodipine 5 mg once daily\n- Clobazam 10 mg at night PRN for clusters (used sparingly)\n- Vitamin D 1000 IU once daily\n\nExamination today was unremarkable. Weight stable. No focal neurological deficits. Blood pressure 138/82. He brought recent home BP readings which are broadly similar. Diary review suggests several events spread across most months, typically brief, with occasional back-to-back occurrences on successive days. No injuries reported.\n\nInvestigations and plans:\n- Bloods today: FBC, U&E, LFT, bone profile, vitamin D level, thyroid function.\n- Arrange MRI brain (epilepsy protocol) to update prior imaging from several years ago, as records provided were incomplete.\n- Discussed treatment options, including introducing a different anti-seizure medicine. He wishes to consider this after reviewing the MRI and bloods. We also discussed safety at home given that he lives alone: kettle use seated, avoiding high ladders, and considering a wearable alert device. He has already placed pans on back hobs and keeps the bathroom door unlocked.\n- Agreed to continue clobazam PRN for short clusters only and to maintain a detailed seizure diary noting sleep, meals, and stressors.\n- Provided information on local peer support groups; he will explore options that fit his routine to mitigate social isolation.\n\nFollow-up:\n- Telephone review by epilepsy nurse in 6–8 weeks to check diary, adherence, and side effects if any changes occur.\n- Face-to-face clinic review in 3–4 months or sooner if events increase in intensity, duration, or lead to injury.\n- Emergency plan discussed: seek urgent help if an event lasts longer than 5 minutes or if there are repeated events without full recovery.\n\nThank you for your continued care and support with blood pressure monitoring and general health maintenance. Please let me know if there are any concerns in the interim.\n\nYours sincerely",
  "competing_possibilities": [],
  "evidence_snippet": "Diary review suggests several events spread across most months, typically brief, with occasional back-to-back occurrences on successive days.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "unknown",
  "review_reasons": [
    "The text lists dates or diary entries without a clear observation timeframe.",
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "timeframe",
    "current_highest_frequency",
    "seizure_or_event_type"
  ],
  "quotes": [
    "Diary review suggests several events spread across most months, typically brief, with occasional back-to-back occurrences on successive days."
  ],
  "reason": "The clinical text mentions 'several events spread across most months' and 'occasional back-to-back occurrences on successive days' but does not specify an exact count, a clear timeframe for frequency calculation, or a defined seizure/event type. There is no explicit statement about the current highest seizure frequency. Therefore, the proposed answer 'unknown' is appropriate as the text lacks sufficient detail to support a specific seizure frequency.",
  "recommended_action": [
    "use_unknown"
  ],
  "seizure_or_event_type_supported": false,
  "timeframe_supported": false
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "timeframe",
    "current_highest_frequency",
    "seizure_or_event_type"
  ],
  "quotes": [
    "Diary review suggests several events spread across most months, typically brief, with occasional back-to-back occurrences on successive days."
  ],
  "reason": "The clinical text mentions 'several events spread across most months' and 'occasional back-to-back occurrences on successive days' but does not specify an exact count, a clear timeframe for frequency calculation, or a defined seizure/event type. There is no explicit statement about the current highest seizure frequency. Therefore, the proposed answer 'unknown' is appropriate as the text lacks sufficient detail to support a specific seizure frequency.",
  "recommended_action": "use_unknown",
  "seizure_or_event_type_supported": false,
  "timeframe_supported": false
}
```

</details>

### Row 959

Interpretation: Over-conservative. The model sent the row to review rather than making a scorable correction; this increases review load without a prediction-bearing win.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_review",
  "design_action": "needs_review",
  "gold_label": "1 per 2 month",
  "parse_errors": [],
  "proposed_answer": "unknown, 2 per cluster",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 959,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "KINGS NEUROSCIENCES CENTRE\n\nClinic Date: 02 October 2025\n\nDr Patel\nRiverside Health Centre\n\n12 Riverside Way, London SE1 2AB\nDear Dr Patel\nWendy Brown, DOB: 21-11-1982, Hospital No: K482715 NHS No. 6592841037\nFlat 7, Brookside Avenue, Newcastle-under-Lyme, ST5 2QD\n\nDiagnoses/summary: Recurrent seizures of undetermined classification; prior routine EEGs non-diagnostic; MRI brain previously non-lesional.\n\nPrevious medication: Lamotrigine (fatigue, no clear benefit), Levetiracetam (irritability), Carbamazepine (dizziness), Sodium valproate (weight gain), Lacosamide (nausea), Clobazam PRN (sedation), Phenytoin (gum changes). Not tried: Topiramate, Zonisamide, Pregabalin, Perampanel, Rufinamide, Tiagabine.\n\nComorbidity: History of migraine without aura; vitamin D insufficiency treated in 2023.\n\nI reviewed Wendy Brown in clinic today, accompanied by her partner. She reports ongoing events that she describes as sudden pauses with loss of awareness followed by brief confusion; at times these are preceded by a sensation of pressure in the chest, but there is no consistent warning. She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession. She keeps a diary corroborated by her partner. There have been no tongue bites or significant injuries, and no clear triggers identified. Sleep is fragmented due to shift work; caffeine intake is moderate; alcohol minimal.\n\nSince her last review, she tapered off Lacosamide under GP supervision because of persistent nausea. She is currently off regular antiseizure medication and prefers to avoid benzodiazepines unless absolutely necessary. She is interested in non-pharmacological strategies and asked about wearable alert devices; we discussed their role and limitations.\n\nExamination today was unremarkable. Blood pressure 118/72, pulse 72 regular. Neurological exam normal. Review of prior investigations: MRI brain (2017) reported structurally normal; routine EEGs in 2016 and 2021 without interictal epileptiform activity. No prolonged monitoring to date. We discussed the uncertainty around the nature of her events and the value of capturing typical events on ambulatory/sleep-deprived EEG or inpatient video-EEG if needed.\n\nPlan:\n- Arrange ambulatory EEG (48–72 hours) aiming to capture typical events that occur bimonthly; if nondiagnostic and events persist, consider inpatient video-EEG monitoring.\n- Blood tests: FBC, U&E, LFT, calcium, magnesium, vitamin D, B12, TSH to rule out contributors to reduced threshold for events.\n- Safety advice provided (first aid around seizures, bathing precautions, cooking with care, and general injury prevention). Driving discussed as per DVLA guidance for episodes of altered awareness; she reports she is currently not driving.\n- Lifestyle: optimise sleep hygiene; limit caffeine to mornings; maintain hydration; continue migraine management with simple analgesia early in the attack and consider GP review for prophylaxis if frequency increases.\n- Medication options explained in neutral terms, including Topiramate and Zonisamide; patient prefers to defer starting treatment until after ambulatory EEG unless event frequency increases. She will contact us urgently if there is any escalation or injury.\n- Provide information on seizure first aid to partner and signpost to patient support resources.\n\nFollow-up: Nurse-led telephone check-in in 6–8 weeks to review ambulatory EEG scheduling and interim events; clinic review in 4 months, earlier if required.\n\nYours sincerely",
  "competing_possibilities": [
    "No competing seizure frequency states described"
  ],
  "evidence_snippet": "She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "unknown, 2 per cluster",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe.",
    "The text may describe seizures in groups without a clear group frequency."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [
    "seizure_or_event_type",
    "timeframe"
  ],
  "quotes": [
    "She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession."
  ],
  "reason": "The clinical text states the events occur bimonthly on average and describes clusters of two events in quick succession some months, but does not specify a clear seizure or event type, nor does it define a precise timeframe for the '2 per cluster' count. The proposed answer 'unknown, 2 per cluster' lacks a defined seizure/event type and a clear timeframe, so these parts are unsupported. The overall highest frequency of bimonthly events is supported.",
  "recommended_action": [
    "needs_review"
  ],
  "seizure_or_event_type_supported": false,
  "timeframe_supported": false
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [
    "seizure_or_event_type",
    "timeframe"
  ],
  "quotes": [
    "She notes the events are occurring bimonthly on average, though some months she has none and then two in quick succession."
  ],
  "reason": "The clinical text states the events occur bimonthly on average and describes clusters of two events in quick succession some months, but does not specify a clear seizure or event type, nor does it define a precise timeframe for the '2 per cluster' count. The proposed answer 'unknown, 2 per cluster' lacks a defined seizure/event type and a clear timeframe, so these parts are unsupported. The overall highest frequency of bimonthly events is supported.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": false,
  "timeframe_supported": false
}
```

</details>

### Row 1363

Interpretation: Over-conservative. The model identified uncertainty and chose review, which may be safe clinically but does not improve the routing label.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_review",
  "design_action": "needs_review",
  "gold_label": "3 per day",
  "parse_errors": [],
  "proposed_answer": "unknown, 3 per cluster",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 1363,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "King's College Hospital \n\nDepartment of Neurosciences \n\nClinic Date: 02 October 2025 \n\nDr A. Patel\nConsultant Neurologist  \nKing's College Hospital  \nDepartment of Neurosciences, King's College Hospital, London SE5 9RS  \n\nDear Dr A. Patel\nConsultant Neurologist,  \n\nSamuel Green, DOB: 14-03-1986, Hospital No: KCH723518 NHS No. 9983214576  \n12 Brookfield Road, London, SE15 3QH\n\nThank you for asking me to review this patient in our epilepsy clinic. He has a remote history of mild traumatic brain injury in his twenties without documented loss of consciousness beyond a few minutes and no neurosurgical intervention at that time. He reports that his first seizures occurred several years later and that, over time, his events have evolved with a clear focal onset. Yesterday he experienced three tonic-clonic seizures yesterday, each preceded by a stereotyped warning of a rising epigastric sensation, brief déjà vu, and impaired awareness with right-hand automatisms lasting around 30–60 seconds before secondary generalisation. His partner confirms post-ictal confusion for 20–30 minutes after each event.\n\nOn current history and semiology, this is most consistent with focal epilepsy. He describes interictal brief auras occurring approximately once or twice per week without progression, and nocturnal events are rare. Known triggers include sleep deprivation and missed meals; he denies alcohol excess. There is no family history of epilepsy. He has noted occasional word-finding difficulty for several hours after larger seizures but no persistent focal deficits.\n\nMedication history: He is taking lamotrigine 150 mg twice daily and levetiracetam 1 g twice daily with good adherence by report; no significant adverse effects beyond mild irritability on levetiracetam which he feels is manageable. He has not previously tried lacosamide or brivaracetam. No known drug allergies.\n\nExamination today between events was unremarkable with normal cranial nerves, no lateralising motor signs, intact coordination, and normal gait. Cardiovascular and general examination were also normal.\n\nPrior investigations: A routine EEG from 2023 was reported as showing intermittent left temporal sharp waves. Brain MRI (epilepsy protocol) from the same year described subtle left mesial temporal T2/FLAIR signal without volume loss; no acute lesions. Basic bloods (FBC, U&Es, LFTs) in June 2025 were within normal limits.\n\nPlan discussed with the patient: Given the focal semiology with secondary generalisation and the recent clustering of three tonic-clonic seizures yesterday, I have recommended an urgent ambulatory EEG with sleep to capture interictal activity and to reassess localisation, along with repeat MRI using an updated temporal lobe protocol. We will also check lamotrigine and levetiracetam trough levels and standard bloods. He is keen to continue current treatment for now; we discussed potential adjustment to introduce lacosamide as add-on if further generalised seizures occur pending results. He will maintain a detailed seizure diary including auras, precipitating factors, and recovery times. Safety advice regarding driving, bathing, and machinery has been reiterated in accordance with current DVLA guidance.\n\nI will review him in six weeks or sooner if there is any escalation. Please let me know if there are any concerns in the interim.\n\nYours sincerely",
  "competing_possibilities": [
    "Interictal auras once or twice per week and rare nocturnal events noted, but recent tonic-clonic seizures dominate frequency assessment."
  ],
  "evidence_snippet": "Yesterday he experienced three tonic-clonic seizures yesterday, each preceded by a stereotyped warning of a rising epigastric sensation, brief déjà vu, and impaired awareness with right-hand automatisms lasting around 30–60 seconds before secondary generalisation.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "unknown, 3 per cluster",
  "review_reasons": [
    "The text may describe seizures in groups without a clear group frequency."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [
    "timeframe"
  ],
  "quotes": [
    "Yesterday he experienced three tonic-clonic seizures yesterday, each preceded by a stereotyped warning of a rising epigastric sensation, brief déjà vu, and impaired awareness with right-hand automatisms lasting around 30–60 seconds before secondary generalisation."
  ],
  "reason": "The clinical text confirms three tonic-clonic seizures occurred yesterday, supporting the count and event type, and indicating these are the current highest frequency seizures. However, the proposed answer 'unknown, 3 per cluster' lacks a clear timeframe for the seizure frequency beyond the single day, so the timeframe is not fully supported.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": false
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [
    "timeframe"
  ],
  "quotes": [
    "Yesterday he experienced three tonic-clonic seizures yesterday, each preceded by a stereotyped warning of a rising epigastric sensation, brief déjà vu, and impaired awareness with right-hand automatisms lasting around 30–60 seconds before secondary generalisation."
  ],
  "reason": "The clinical text confirms three tonic-clonic seizures occurred yesterday, supporting the count and event type, and indicating these are the current highest frequency seizures. However, the proposed answer 'unknown, 3 per cluster' lacks a clear timeframe for the seizure frequency beyond the single day, so the timeframe is not fully supported.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": false
}
```

</details>

### Row 1694

Interpretation: Over-conservative. The model avoided rendering a questionable proposed answer, but the result remains non-scorable and should count as review burden.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_review",
  "design_action": "needs_review",
  "gold_label": "1 cluster per 2 week, 3 per cluster",
  "parse_errors": [],
  "proposed_answer": "1 cluster per 2 week, 3 per cluster",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 1694,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "St Mary's Hospital \n\nInstitute of Neurology \n\nClinic Date: 02 October 2025 \n\nDr Ahmed  \nSt Mary's Hospital  \nInstitute of Neurology, St Mary's Hospital, London W2 1NY  \n\nDear Dr Ahmed,  \n\nSophie Turner, DOB: 12-05-1991, Hospital No: H938421 NHS No. 5839201746  \n24 Elm Grove, London, W8 6PA \n\nMedication: \n\nLevetiracetam 1 g twice daily; Sodium valproate 300 mg morning and 600 mg evening. No adverse effects reported beyond mild daytime tiredness.\n\nThank you for reviewing this patient in primary care for her type 2 diabetes, which remains under your management. She attended my neurology clinic today for review of her epilepsy. She has generalised epilepsy. Over the past fortnight she describes a run of brief generalised events, with three short episodes occurring on separate days, each with abrupt loss of awareness and limb jerks, followed by quick recovery and a mild postictal headache. There were no injuries. She links these to disrupted sleep and a missed evening dose of levetiracetam on one occasion. Alcohol intake is minimal and there has been no recent intercurrent illness.\n\nOn discussion, she has been generally stable for several months prior to this cluster. Neurological examination today is normal. She remains fit to continue current activities, avoiding known precipitants such as sleep deprivation. We reviewed adherence strategies; she has set phone reminders and will use a weekly pill organiser.\n\nPlan: \n- Continue levetiracetam 1 g twice daily and sodium valproate 300 mg morning, 600 mg evening. \n- If further breakthrough events occur despite full adherence and adequate sleep hygiene, we will consider a modest increase of levetiracetam at next review. \n- She understands standard seizure first-aid advice and safety precautions. She does not drive and is aware of DVLA regulations regarding seizure recurrence. \n- From a diabetes perspective, she reports good adherence to metformin prescribed by you, with no hypoglycaemia. No medication interactions of concern identified today.\n\nWe will review her again in four months, sooner if she experiences additional generalised seizures or any change in pattern.\n\nYours sincerely",
  "competing_possibilities": [
    "Patient was stable for several months prior to this cluster"
  ],
  "evidence_snippet": "Over the past fortnight she describes a run of brief generalised events, with three short episodes occurring on separate days, each with abrupt loss of awareness and limb jerks, followed by quick recovery and a mild postictal headache.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "1 cluster per 2 week, 3 per cluster",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe.",
    "The text may describe seizures in groups without a clear group frequency."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": "false",
  "count_supported": "true",
  "current_highest_frequency_supported": "false",
  "missing_or_conflicting_parts": [
    "timeframe",
    "current_highest_frequency"
  ],
  "quotes": [
    "Over the past fortnight she describes a run of brief generalised events, with three short episodes occurring on separate days, each with abrupt loss of awareness and limb jerks, followed by quick recovery and a mild postictal headache."
  ],
  "reason": "The clinical text supports that there were three brief generalized seizure episodes over the past fortnight (two weeks), which supports the count and timeframe. However, the text does not clearly define the frequency as '1 cluster per 2 weeks' or specify that this is the current highest seizure frequency. It only mentions a recent cluster after several months of stability, so the proposed answer's grouping into clusters and frequency per cluster is not explicitly supported.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": "true",
  "timeframe_supported": "true"
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": true,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "timeframe",
    "current_highest_frequency"
  ],
  "quotes": [
    "Over the past fortnight she describes a run of brief generalised events, with three short episodes occurring on separate days, each with abrupt loss of awareness and limb jerks, followed by quick recovery and a mild postictal headache."
  ],
  "reason": "The clinical text supports that there were three brief generalized seizure episodes over the past fortnight (two weeks), which supports the count and timeframe. However, the text does not clearly define the frequency as '1 cluster per 2 weeks' or specify that this is the current highest seizure frequency. It only mentions a recent cluster after several months of stability, so the proposed answer's grouping into clusters and frequency per cluster is not explicitly supported.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 4368

Interpretation: Conservative wrong-to-wrong. The model chose unknown, preserving the safe posture but not recovering the gold state.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_W_changed",
  "design_action": "use_unknown",
  "gold_label": "5 per 2 month",
  "parse_errors": [],
  "proposed_answer": "unknown",
  "quotes_exact": true,
  "routing_policy_action": "route_review",
  "routing_policy_label": null,
  "source_row_index": 4368,
  "verifier_label": "unknown"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Department of Neurology \n\nClinic Date: 29 May 2023 \n\nDr Amelia Patel  \nSt George’s University Hospitals NHS Foundation Trust  \nDepartment of Neurology, Blackshaw Road, London SW17 0QT  \n\nDear Dr Amelia Patel,  \n\nAlex Carter, DOB: 14-02-1991, Hospital No: H392845 NHS No. 9038451172  \n12 Oakfield Close, Mitcham, CR4 1TP \n\nDiagnoses: \n\nRemote history of mild traumatic brain injury. Recurrent seizure episodes under investigation. \n\nCurrent Medication: \n\nLevetiracetam 500 mg twice daily \nClobazam 10 mg at night (as rescue for clusters) \n\nPlan: \n\n- Continue levetiracetam 500 mg twice daily.  \n- Provide midazolam oromucosal 5 mg for prolonged events (>5 minutes) or clusters; patient and carer trained in use.  \n- MRI brain (epilepsy protocol) to be arranged.  \n- EEG to be scheduled; will review results and adjust treatment accordingly.  \n- Seizure diary to continue; please record potential triggers, sleep patterns, and medication adherence.  \n- Safety advice discussed including driving regulations, water safety, heights, and operating machinery.  \n- Follow-up in 3 months or sooner if further events occur.  \n\nI reviewed Alex Carter in the neurology clinic today. They describe intermittent episodes characterised by sudden loss of awareness with brief stiffening and bilateral shaking in some events, and in others a brief blank spell with confusion afterwards. Remote history of mild traumatic brain injury (no neurosurgical intervention, recovered without persistent focal deficits) is noted. There is no family history of seizures reported. Sleep disruption and intercurrent illness appear to precede several events. Alcohol intake is minimal and there is no recreational drug use reported.\n\nRegarding recent frequency, the seizure diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24. Two of these were associated with missed evening doses; one followed a febrile upper respiratory infection. No tongue lacerations were reported; one event involved a minor fall without head strike. No persistent focal neurological deficits have been noted between episodes.\n\nOn examination today, general and neurological examinations were unremarkable. Observations stable. Prior routine blood tests (U&Es, LFTs, calcium, glucose, FBC) last month were within normal limits. No prior neuroimaging is available for comparison. We discussed that the pattern remains under investigation and further characterisation with EEG and MRI is required. In the interim, we will continue current antiseizure therapy and emphasised adherence and sleep hygiene.\n\nWe reviewed safety and first-aid measures. The patient has been issued with an updated seizure action plan. They will not drive and understand the requirement to notify the DVLA; I have advised to follow national guidance and to remain off driving until medically cleared. A letter summarising this advice has been provided to the patient.\n\nPlease do not hesitate to contact me if there are any concerns or if further events occur. I will write again once the investigation results are available or sooner if there is a change in clinical status.\n\nWith best wishes, ",
  "competing_possibilities": [
    "No competing seizure frequency states described"
  ],
  "evidence_snippet": "Regarding recent frequency, the seizure diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "unknown",
  "review_reasons": [
    "The text lists dates or diary entries without a clear observation timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "timeframe",
    "current_highest_frequency"
  ],
  "quotes": [
    "Regarding recent frequency, the seizure diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24."
  ],
  "reason": "The clinical text provides specific seizure event dates but does not specify a clear timeframe over which these events occurred (e.g., number of seizures per month or per week). There is no explicit statement about the current highest seizure frequency or a defined count within a set period. Therefore, the count, timeframe, and current highest frequency parts of the answer are not supported.",
  "recommended_action": [
    "use_unknown"
  ],
  "seizure_or_event_type_supported": false,
  "timeframe_supported": false
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "timeframe",
    "current_highest_frequency"
  ],
  "quotes": [
    "Regarding recent frequency, the seizure diary documents: Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24."
  ],
  "reason": "The clinical text provides specific seizure event dates but does not specify a clear timeframe over which these events occurred (e.g., number of seizures per month or per week). There is no explicit statement about the current highest seizure frequency or a defined count within a set period. Therefore, the count, timeframe, and current highest frequency parts of the answer are not supported.",
  "recommended_action": "use_unknown",
  "seizure_or_event_type_supported": false,
  "timeframe_supported": false
}
```

</details>

### Row 5921

Interpretation: Over-conservative. The model refused a complex cluster proposal; safe, but not a prediction-bearing improvement.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_review",
  "design_action": "needs_review",
  "gold_label": "1 per 6 to 8 week",
  "parse_errors": [],
  "proposed_answer": "1 cluster per 6 to 8 week, multiple per cluster",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 5921,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Centre for Epilepsy\n\nNeurosciences Division \n\nClinic Date: 02 October 2025 \n\nDr Martin Hale  \nRiverside Health Centre  \n22 Millbank, London SW1P 4QP  \n\nDear Dr Martin Hale,                                                                                                         \n\nJames Carter, DOB: 09-11-1992, Hospital No: H732019 NHS No. 9843175620  \nFlat 3B, 47 King Street, Hammersmith, London W6 0QF  \n\nEpilepsy \n\nMedication: Continuing Levetiracetam since March 2025  \n\nLevetiracetam 750mg twice daily (as confirmed with the patient by phone)  \n\nLevetiracetam Blood Level:  \n\n15 September 2025: 14 µg/mL (reference 12–46 µg/mL). Dose 750mg twice daily  \n\nSeizures: Patient reports intermittent events tending to cluster towards the later part of the night, typically occurring in the early hours before dawn, approximately once every 6–8 weeks. No clear warning symptoms; partner occasionally notes brief limb stiffening and a short period of confusion on waking. \n\nI spoke with the patient today during a scheduled telephone review. They describe improved daytime alertness since switching dosing times to 08:00 and 20:00. Sleep has been irregular due to shift work, which may be contributing to the pre-dawn episodes. No tongue biting, injuries, or incontinence reported. Recovery is usually complete within an hour, with mild headache only. They have been adherent to the stated dose, and there have been no missed doses in the last month. \n\nWe discussed practical measures around sleep hygiene and maintaining consistent dosing given variable work patterns. The patient prefers to avoid dose escalation currently while monitoring for any pattern change. I will re-check levels if frequency increases or if further events occur outside the usual early-morning window. Safety advice (driving and bathing) was reiterated; no new triggers identified. \n\nI will arrange a follow-up in three months via telephone, or sooner if the early-morning events increase in frequency or severity. \n\nYours sincerely",
  "competing_possibilities": [
    "No competing seizure frequency states described"
  ],
  "evidence_snippet": "Patient reports intermittent events tending to cluster towards the later part of the night, typically occurring in the early hours before dawn, approximately once every 6–8 weeks.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "1 cluster per 6 to 8 week, multiple per cluster",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": "false",
  "count_supported": "false",
  "current_highest_frequency_supported": "true",
  "missing_or_conflicting_parts": [
    "count"
  ],
  "quotes": [
    "Patient reports intermittent events tending to cluster towards the later part of the night, typically occurring in the early hours before dawn, approximately once every 6–8 weeks."
  ],
  "reason": "The clinical text supports a seizure frequency of approximately once every 6-8 weeks and describes the events as clustering, but does not specify the number of seizures per cluster, so the count part of the proposed answer is not supported. The timeframe and event type (intermittent events clustering at night) are supported, and this is the current highest frequency described.",
  "recommended_action": [
    "needs_review"
  ],
  "seizure_or_event_type_supported": "true",
  "timeframe_supported": "true"
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [
    "count"
  ],
  "quotes": [
    "Patient reports intermittent events tending to cluster towards the later part of the night, typically occurring in the early hours before dawn, approximately once every 6–8 weeks."
  ],
  "reason": "The clinical text supports a seizure frequency of approximately once every 6-8 weeks and describes the events as clustering, but does not specify the number of seizures per cluster, so the count part of the proposed answer is not supported. The timeframe and event type (intermittent events clustering at night) are supported, and this is the current highest frequency described.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 6153

Interpretation: Strong recovery. The full letter clearly supports 3 nocturnal convulsions plus 6 focal aware events in four weeks, so approving 9 per 4 week is well grounded.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_C",
  "design_action": "use_proposed_answer",
  "gold_label": "9 per month",
  "parse_errors": [],
  "proposed_answer": "9 per 4 week",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 6153,
  "verifier_label": "9 per 4 week"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "King's College Hospital \n\nDepartment of Neurosciences \n\nClinic Date: 16 February 2016 \n\nDr Eleanor Patel\nConsultant Neurologist  \nKing's College Hospital  \nDepartment of Neurosciences, King's College Hospital, London SE5 9RS  \n\nDear Dr Eleanor Patel\nConsultant Neurologist,  \n\nSophie Bennett, DOB: 14-03-1993, Hospital No: KCH728519 NHS No. 9076143258  \n12 Celandine Court, Dulwich, London SE21 8JT\n\nThank you for your referral and for the accompanying details. I reviewed Sophie Bennett in clinic today following recent postpartum changes. She reports a clear deterioration over the past two months, with increasing fatigue, low mood, and a subjective sense that her seizures are clustering more often. She is breastfeeding and sleeping in fragmented blocks, which she feels has amplified both her tiredness and seizure burden. Her partner corroborates a noticeable decline in resilience and longer post-event recovery times.\n\nShe has a known diagnosis of combined generalised and focal epilepsy. On history, there are two distinct event types:  \n- Generalised episodes: abrupt loss of awareness with bilateral tonic-clonic activity, preceded at times by a brief “whole-head pressure” sensation. Post-ictal confusion typically lasts 30–60 minutes.  \n- Focal episodes: focal aware onset with a rising epigastric sensation, right-hand clenching, and brief speech arrest lasting 30–90 seconds, occasionally progressing to impaired awareness.\n\nShe additionally describes light-triggered attacks: in busy retail settings and when scrolling rapidly through high-contrast digital content, she experiences brief shimmering in the visual field, eyelid flutter, and then an escalation to her usual generalised convulsions if exposure continues. These light-provoked events have increased from approximately once monthly before delivery to occurring every one to two weeks postpartum. In the past four weeks she reports three nocturnal convulsions and six focal aware events, which is a significant increase from her late antenatal baseline.\n\nMedication history: currently on lamotrigine 200 mg twice daily and levetiracetam 1 g twice daily. She was stable antenatally on the same regimen but had better sleep and fewer triggers. No recent missed doses reported; however, she notes occasional delays with evening doses due to infant care demands. No new intercurrent illness, alcohol intake minimal, and no recreational drugs. She has not resumed driving and remains compliant with DVLA advice.\n\nExamination today was unremarkable neurologically. Mental state suggested low mood and tearfulness, without psychotic features. There were no focal deficits on examination. Bloods available from the GP last month showed normal U&Es and LFTs; antiseizure medication levels were not checked.\n\nImpression: combined generalised and focal epilepsy with postpartum deterioration in seizure control, plausibly exacerbated by sleep deprivation, physiological postpartum changes, and possible heightened photosensitivity manifesting as light-provoked attacks. Her overall condition is deteriorating compared with the pre-delivery baseline, with increased frequency of both focal and generalised events and longer recovery.\n\nPlan:  \n1. Arrange urgent serum lamotrigine and levetiracetam trough levels to guide dose optimisation.  \n2. Bring forward EEG with photic stimulation and sleep deprivation protocol to characterise the light-provoked component and interictal burden.  \n3. Expedite MRI brain (epilepsy protocol) if not updated within the last two years.  \n4. Sleep hygiene and practical postpartum adjustments discussed; she will trial scheduled rest periods supported by her partner for consistent medication timing.  \n5. Provide written guidance on reducing light-trigger exposure (screen brightness adjustments, flicker-reduction settings, and protective eyewear in high-contrast environments).  \n6. Safety counselling reiterated regarding bathing, infant handling when drowsy or post-ictal, and seizure first aid.  \n7. Liaise with perinatal mental health for assessment of postpartum low mood, as this may be contributing to perceived worsening and coping.  \n8. Review in six weeks, sooner if further clusters or injuries occur. She was given the urgent advice line and instructed to seek emergency assessment for prolonged seizures or repeated events without recovery.\n\nThank you for your continued care. I will update you following investigations and once serum levels are available.\n\nYours sincerely",
  "competing_possibilities": [
    "No competing seizure frequency states explicitly described"
  ],
  "evidence_snippet": "These light-provoked events have increased from approximately once monthly before delivery to occurring every one to two weeks postpartum. In the past four weeks she reports three nocturnal convulsions and six focal aware events, which is a significant increase from her late antenatal baseline.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "9 per 4 week",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": "true",
  "count_supported": "true",
  "current_highest_frequency_supported": "true",
  "missing_or_conflicting_parts": [],
  "quotes": [
    "In the past four weeks she reports three nocturnal convulsions and six focal aware events, which is a significant increase from her late antenatal baseline."
  ],
  "reason": "The clinical text explicitly states that in the past four weeks the patient has had three nocturnal convulsions and six focal aware events, totaling nine events in four weeks, which supports the proposed seizure frequency of 9 per 4 weeks. The seizure types, count, and timeframe are clearly described and pertain to the current highest seizure frequency.",
  "recommended_action": ["use_proposed_answer"],
  "seizure_or_event_type_supported": "true",
  "timeframe_supported": "true"
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "In the past four weeks she reports three nocturnal convulsions and six focal aware events, which is a significant increase from her late antenatal baseline."
  ],
  "reason": "The clinical text explicitly states that in the past four weeks the patient has had three nocturnal convulsions and six focal aware events, totaling nine events in four weeks, which supports the proposed seizure frequency of 9 per 4 weeks. The seizure types, count, and timeframe are clearly described and pertain to the current highest seizure frequency.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 6209

Interpretation: Good safety behavior. The model rejected 2 to 3 per day because the text separates daily brief events from 2 to 3 longer monthly episodes.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "C_to_review",
  "design_action": "needs_review",
  "gold_label": "multiple per day",
  "parse_errors": [],
  "proposed_answer": "2 to 3 per day",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 6209,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 02 October 2025\n\nDr A Patel\nRiverside Health Centre\n\n12 Brook Lane\n\nSouthwark\nLondon SE1 0AB\nDear Dr A Patel\nJordan Ellis, DOB: 14-03-1991, Hospital No: H739205 NHS No. 8421906753\nFlat 3, 28 Willow Court, London, SE15 4JG \n\nDiagnoses/summary: Recurrent seizures with uncertain classification; prior EEGs non-diagnostic and one ambulatory study reported sporadic non-specific changes. No clearly identified precipitant other than sudden environmental sounds reported by the patient and family. \n\nMRI brain 2019 reported structurally unremarkable appearances; no focal lesion detected.\n\nPrevious medication: Levetiracetam (behavioural irritability, seizures persisted), Sodium valproate (weight gain and tremor), Carbamazepine (dizziness, hyponatraemia), Lamotrigine (partial benefit but ongoing events), Clobazam PRN (some reduction in clusters), Lacosamide (no clear benefit), Topiramate (word-finding difficulty), Zonisamide (appetite suppression and insomnia).\n\nNot taken: Perampanel, Brivaracetam, Rufinamide, Oxcarbazepine, Cenobamate, Pregabalin, Tiagabine.\n\nComorbidities: Migraine without aura; mild asthma. No known cardiac disease; echocardiogram 2021 normal. \n\nI reviewed Jordan Ellis in clinic today, accompanied by their partner. They described daily brief events and approximately 2–3 longer episodes per month. Of note, they and their partner have observed that abrupt, unexpected noises (for example, a dropped plate or sudden door slam) often precede the shorter events; these are described as a rapid startle followed by a freeze and loss of awareness for up to 30–60 seconds with occasional right-hand fumbling, then a short period of confusion. There is no consistent nocturnal pattern. They report no sustained aura. Injuries have been limited to minor bruises.\n\nThey continue to work part-time in an office role and are not driving. Mood has been variable but there is no current self-harm risk. Sleep is reported as fragmented. Alcohol intake minimal; no recreational drugs. Family history non-contributory.\n\nCurrent medication:\n- Lamotrigine 150 mg twice daily\n- Clobazam 10 mg at night (with 5 mg as needed for clusters, used approximately once weekly)\n- Salbutamol inhaler PRN\n- Magnesium supplement (patient-initiated)\n\nPlan:\n- We discussed options including a cautious switch from lamotrigine to brivaracetam, or trial of perampanel, acknowledging prior behavioural effects on levetiracetam. The patient wishes to consider brivaracetam first; I provided written information and asked them to contact the epilepsy nurse specialist (ENS) within 2 weeks to confirm preference.\n- Safety advice reinforced, particularly around baths vs showers, kitchen hazards, and using a soft alarm tone where feasible given the tendency of abrupt noise to precede brief events.\n- Seizure diary to continue, with particular note of context, sound environment, and time-of-day. Partner will attempt to capture a safe video of typical episodes on their phone for review.\n- Request repeat routine EEG with additional sound-related activation procedures if tolerated, and consider ambulatory EEG if routine study remains uninformative.\n- Bloods: U&E, LFT, FBC, vitamin D, lamotrigine level for reference.\n- Referral to ENS for telephone follow-up in 4–6 weeks to review frequency, tolerability, and to finalise medication strategy.\n- Driving: patient not driving; current guidance reiterated.\n\nI will review Jordan Ellis in clinic in approximately 4 months, sooner if there is any deterioration or if they elect to commence a new antiseizure medication requiring closer titration.\n\nYours sincerely",
  "competing_possibilities": [],
  "evidence_snippet": "They described daily brief events and approximately 2–3 longer episodes per month.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "2 to 3 per day",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": ["count", "timeframe"],
  "quotes": ["They described daily brief events and approximately 2–3 longer episodes per month."],
  "reason": "The clinical text states 'daily brief events' and 'approximately 2–3 longer episodes per month,' but the proposed answer '2 to 3 per day' does not match either the count or the timeframe for the longer episodes. The text does not specify a count of 2 to 3 events per day; it only mentions daily brief events without quantifying them and 2–3 longer episodes per month.",
  "recommended_action": ["needs_review"],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": false
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "timeframe"
  ],
  "quotes": [
    "They described daily brief events and approximately 2–3 longer episodes per month."
  ],
  "reason": "The clinical text states 'daily brief events' and 'approximately 2–3 longer episodes per month,' but the proposed answer '2 to 3 per day' does not match either the count or the timeframe for the longer episodes. The text does not specify a count of 2 to 3 events per day; it only mentions daily brief events without quantifying them and 2–3 longer episodes per month.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": false
}
```

</details>

### Row 6321

Interpretation: Safe review. The model avoided rendering a row that routing had correct as unknown/review; this is not prediction-bearing but avoids a wrong label.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "C_to_review",
  "design_action": "needs_review",
  "gold_label": "unknown",
  "parse_errors": [],
  "proposed_answer": "unknown",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 6321,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Centre for Epilepsy\n\nNeurosciences Division \n\nClinic Date: 02 October 2025 \n\nDr Priya Nair  \nRiverside Health Centre  \n3 Mill Lane, Bridgeford, BD12 4QT  \n\nDear Dr Priya Nair,                                                                                                         \n\nThomas Green, DOB: 22-11-1989, Hospital No: H738201 NHS No. 9842756310  \nLow Meadow Farm Cottage, Hilltop Road, Bridgeford, BD12 7PX  \n\nEpilepsy \n\nMedication: Continuing Levetiracetam since March 2024  \n\nLevetiracetam 750 mg twice daily (patient-reported adherence good) \n\nLevetiracetam Blood Level:  \n\n09 September 2025: 18 µg/mL (local reference 12–46 µg/mL). Dose 750 mg twice daily  \n\nSeizures: The patient reports that spells are uncommon when meals are regular; when they go long hours without food, brief collapses with confusion have occurred on two recent occasions (July and September 2025). No injuries. No reported auras or prolonged events. \n\nI conducted a video follow-up today as the patient resides in a rural area with limited public transport, making in-person appointments difficult. They described two short episodes this summer coinciding with irregular eating on busy farm workdays. Otherwise, daytime alertness is stable and there is no new neurological symptomatology. Sleep has improved since August after adjusting work shifts. No missed doses reported in the last three months. \n\nWe discussed practical measures around maintaining regular meals and hydration during long outdoor work periods, and they have arranged to keep snacks available while working. They will continue to track events in a diary and will contact the service if frequency increases or if there is any evolution in features such as injuries, prolonged confusion, or clustering. A community phlebotomy appointment can be arranged through the district service should repeat levels be needed. \n\nPlan:  \n- Continue current Levetiracetam 750 mg twice daily.  \n- Safety advice reinforced regarding work at heights and operating machinery on days when unwell.  \n- Arrange remote review in 4 months by telephone, with earlier contact if further episodes occur. \n\nYours sincerely",
  "competing_possibilities": [
    "No competing seizure frequency states reported"
  ],
  "evidence_snippet": "when they go long hours without food, brief collapses with confusion have occurred on two recent occasions (July and September 2025)",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "unknown",
  "review_reasons": [
    "The frequency may apply only under a condition or trigger."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "current_highest_frequency"
  ],
  "quotes": [
    "brief collapses with confusion have occurred on two recent occasions (July and September 2025)",
    "The patient reports that spells are uncommon when meals are regular",
    "They described two short episodes this summer coinciding with irregular eating on busy farm workdays"
  ],
  "reason": "The clinical text indicates that the two brief collapse events occurred only under the specific condition of irregular eating, and spells are otherwise uncommon when meals are regular. There is no clear statement that these two events represent the current highest seizure frequency overall, nor is there a general seizure frequency count or timeframe that applies unconditionally. Therefore, the proposed answer 'unknown' is not fully supported because the frequency is conditional and not clearly established as the highest frequency.",
  "recommended_action": [
    "needs_review"
  ],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "current_highest_frequency"
  ],
  "quotes": [
    "brief collapses with confusion have occurred on two recent occasions (July and September 2025)",
    "The patient reports that spells are uncommon when meals are regular",
    "They described two short episodes this summer coinciding with irregular eating on busy farm workdays"
  ],
  "reason": "The clinical text indicates that the two brief collapse events occurred only under the specific condition of irregular eating, and spells are otherwise uncommon when meals are regular. There is no clear statement that these two events represent the current highest seizure frequency overall, nor is there a general seizure frequency count or timeframe that applies unconditionally. Therefore, the proposed answer 'unknown' is not fully supported because the frequency is conditional and not clearly established as the highest frequency.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 6889

Interpretation: Safety failure. The model approved the tonic-clonic count and incorrectly called it current highest frequency despite myoclonic jerks several times per week. This is the full-letter variant's C->W regression.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "C_to_W",
  "design_action": "use_proposed_answer",
  "gold_label": "multiple per week",
  "parse_errors": [],
  "proposed_answer": "3 per 6 month",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 6889,
  "verifier_label": "3 per 6 month"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 02 October 2025\n\nDr James Patel\nRiverside Medical Practice\n\n12 Millbank, London SW1P 3GE\nDear Dr James Patel\nAlex Morgan, DOB: 14-03-1990, Hospital No: H927461 NHS No. 7485209163\nFlat 3, 21 Kingfisher Close, London, SE10 8AB \n\nDiagnoses/summary: Combined generalised and focal epilepsy (patient has both generalised and focal epilepsy), longstanding; learning points from prior work-up include mixed semiologies consistent with dual network involvement\n\nMRI brain (2019) reported normal; no structural focus identified\n\nEEG history: background normal; frequent interictal epileptiform activity recorded without captured clinical events; most recent EEG (Aug 2025) noted sporadic generalised spike–wave and independent left temporal sharp waves with no recorded clinical counterpart\n\nPrevious medication: sodium valproate (weight gain, tremor), carbamazepine (rash), lamotrigine (partial benefit), levetiracetam (irritability), topiramate (cognitive slowing), zonisamide (reduced appetite), clobazam (sedation), perampanel (mood change)\n\nNot taken: lacosamide, brivaracetam, cannabidiol (Epidyolex), cenobamate, rufinamide, tiagabine, pregabalin\n\nComorbidities: mild asthma; vitamin D insufficiency; no known cardiac history\n\nI reviewed Alex in clinic today, accompanied by his partner. He reports two distinct seizure patterns:\n- Generalised: brief morning myoclonic jerks several times per week, and three generalised tonic–clonic seizures in the past six months, typically on sleep deprivation.\n- Focal: episodes of rising epigastric sensation followed by behavioural arrest and lip smacking lasting 60–90 seconds, occurring roughly once every 2–3 weeks, with post-event confusion for 10–15 minutes.\n\nHe keeps a diary and notes that alcohol and irregular sleep are common precipitants. He is currently driving-ineligible and understands DVLA guidance. He denies recent injuries. Mood is stable; no active safety concerns. He is interested in future family planning and asks about medication options compatible with this.\n\nCurrent medication:\n- Lamotrigine 150 mg twice daily\n- Levetiracetam 1 g twice daily\n- Vitamin D3 1000 IU daily\n- Salbutamol inhaler PRN\n\nExamination today was unremarkable; no focal neurological deficits. Weight stable. Bloods from July 2025: FBC, U&E, LFTs within reference limits; vitamin D marginally low (repletion initiated). ECG normal.\n\nEEG context and frequency statement: His most recent EEG demonstrated interictal epileptiform abnormalities without any recorded seizure during the study, aligning with his report of intermittent events outside the recording window and supporting the clinical impression of combined generalised and focal epilepsy.\n\nPlan:\n- Optimise antiseizure therapy: discuss transition from levetiracetam to brivaracetam to address irritability risk; commence cross-taper if agreed after patient information provided and consent obtained. If suboptimal control persists, consider add-on lacosamide targeting focal-onset events. We will avoid sodium valproate given prior adverse effects and his wish to minimise metabolic side effects.\n- Lifestyle: reinforce sleep regularity, alcohol minimisation, and hydration; continue seizure diary with differentiation of generalised vs focal events.\n- Safety: DVLA regulations reinforced; SUDEP and general safety measures discussed (supervised bathing, avoid heights/open water when alone).\n- Investigations: arrange repeat MRI epilepsy protocol with 3T if feasible; consider ambulatory EEG if diary suggests clustering to better phenotype events temporally.\n- Follow-up: nurse-led telephone review at 4 weeks to assess tolerability and frequency; clinic review in 3 months or sooner if deterioration or adverse effects.\n\nThank you for your ongoing care and prescriptions support. Please do not hesitate to contact me if queries arise or if earlier review is needed.\n\nYours sincerely",
  "competing_possibilities": [
    "Also reports focal seizures approximately every 2–3 weeks"
  ],
  "evidence_snippet": "He reports two distinct seizure patterns:\n- Generalised: brief morning myoclonic jerks several times per week, and three generalised tonic–clonic seizures in the past six months, typically on sleep deprivation.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "3 per 6 month",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "three generalised tonic–clonic seizures in the past six months",
    "He reports two distinct seizure patterns:\n- Generalised: brief morning myoclonic jerks several times per week, and three generalised tonic–clonic seizures in the past six months, typically on sleep deprivation."
  ],
  "reason": "The clinical text explicitly states the patient had three generalised tonic–clonic seizures in the past six months, providing a clear count and timeframe for the highest seizure frequency. The seizure type is specified as generalised tonic–clonic seizures, and the timeframe is recent and relevant, supporting the proposed answer.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "three generalised tonic–clonic seizures in the past six months",
    "He reports two distinct seizure patterns:\n- Generalised: brief morning myoclonic jerks several times per week, and three generalised tonic–clonic seizures in the past six months, typically on sleep deprivation."
  ],
  "reason": "The clinical text explicitly states the patient had three generalised tonic–clonic seizures in the past six months, providing a clear count and timeframe for the highest seizure frequency. The seizure type is specified as generalised tonic–clonic seizures, and the timeframe is recent and relevant, supporting the proposed answer.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 7168

Interpretation: Good safety behavior. The model saw that two tonic-clonic seizures over a year does not justify cluster syntax and kept the row out of prediction-bearing use.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "C_to_review",
  "design_action": "needs_review",
  "gold_label": "unknown",
  "parse_errors": [],
  "proposed_answer": "1 cluster per year, 2 per cluster",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 7168,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Department of Neurology \n\nClinic Date: 02 October 2025 \n\nDr Aisha Rahman  \nSt Mary’s Hospital  \nDepartment of Neurology, Praed Street, London W2 1NY  \n\nDear Dr Aisha Rahman,  \n\nMarta Nowak, DOB: 14-02-1992, Hospital No: H3928476 NHS No. 9012457783  \nFlat 3, 28 Harrow Road, London, W9 3RJ \n\nDiagnoses: \n\nPrimary generalised epilepsy with occasional catamenial clustering \nEEG (June 2025): Generalised spike-and-wave discharges consistent with generalised epilepsy \n\nCurrent Medication: \n\nSodium valproate 300 mg in the morning and 600 mg at night  \nFolic acid 5 mg once daily \n\nPlan: \n\n- Continue sodium valproate at current dose; check trough level and LFTs in 3 months  \n- Provide written seizure first-aid and SUDEP advice in preferred language  \n- Refer to epilepsy specialist nurse for care planning and NHS pathway orientation; interpreter to be arranged as needed  \n- Consider perimenstrual dose optimisation or alternative catamenial strategy if breakthrough events persist; to be reviewed after seizure diary review in 4 months  \n- Safety advice: avoid sleep deprivation, limit alcohol, and maintain adherence; no driving in accordance with DVLA guidance until seizure-free for the required period  \n\nI reviewed Marta Nowak in clinic today with telephone interpreter support. They are a recent migrant to the UK and are still becoming familiar with NHS services and how to obtain repeat prescriptions. We discussed the role of the GP, community pharmacy, and how to contact the neurology team or the epilepsy specialist nurse for advice between appointments. \n\nThey report a history of generalised seizures beginning in adolescence. Over the past year there have been two brief generalised tonic–clonic seizures, both occurring shortly before menstruation, with preserved recovery and no injuries. Day-to-day, there are intermittent morning myoclonic jerks, especially after poor sleep. A seizure diary kept over the last three months shows a recurring pattern of seizure susceptibility in the late premenstrual window; in their words, \"the few days before periods are when things bunch up.\" There have been no status epilepticus episodes. No red flags for infection or new neurological deficit. \n\nMedication adherence is good; no notable adverse effects aside from mild tremor. We discussed risks and benefits of valproate comprehensively, including teratogenicity and the need for highly effective contraception and a Pregnancy Prevention Programme; patient confirms not planning pregnancy and using reliable contraception. Folic acid is continued. Lifestyle measures (sleep regularity and caffeine moderation) have been reinforced. \n\nGiven the pattern of premenstrual worsening, I have advised continuation of current therapy while we gather more data from the seizure diary to guide any targeted adjustment around the perimenstrual period. If clustering persists, we will consider a limited perimenstrual dose increment or an alternative agent better suited to catamenial exacerbations, balancing efficacy and safety. \n\nI will review in 4 months with interpreter support. Blood tests (valproate level, FBC, LFTs) will be arranged via the GP in 2–3 weeks. Information leaflets and an emergency plan have been provided in translated format. \n\nWith best wishes, ",
  "competing_possibilities": [
    "Intermittent myoclonic jerks occur day-to-day but are not counted as seizures here"
  ],
  "evidence_snippet": "Over the past year there have been two brief generalised tonic–clonic seizures, both occurring shortly before menstruation, with preserved recovery and no injuries.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "1 cluster per year, 2 per cluster",
  "review_reasons": [
    "The text may describe seizures in groups without a clear group frequency."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": ["count", "timeframe"],
  "quotes": [
    "Over the past year there have been two brief generalised tonic–clonic seizures, both occurring shortly before menstruation, with preserved recovery and no injuries.",
    "A seizure diary kept over the last three months shows a recurring pattern of seizure susceptibility in the late premenstrual window; in their words, \"the few days before periods are when things bunch up.\""
  ],
  "reason": "The clinical text states there have been two generalised tonic–clonic seizures over the past year, both shortly before menstruation, but does not explicitly describe these as occurring in a single cluster or multiple clusters. The seizure diary notes a pattern of susceptibility in the late premenstrual window but does not quantify the number of seizures per cluster or confirm the presence of discrete clusters. Therefore, the proposed answer of '1 cluster per year, 2 per cluster' is not fully supported as the cluster count and cluster frequency are not clearly documented.",
  "recommended_action": ["needs_review"],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "timeframe"
  ],
  "quotes": [
    "Over the past year there have been two brief generalised tonic–clonic seizures, both occurring shortly before menstruation, with preserved recovery and no injuries.",
    "A seizure diary kept over the last three months shows a recurring pattern of seizure susceptibility in the late premenstrual window; in their words, \"the few days before periods are when things bunch up.\""
  ],
  "reason": "The clinical text states there have been two generalised tonic–clonic seizures over the past year, both shortly before menstruation, but does not explicitly describe these as occurring in a single cluster or multiple clusters. The seizure diary notes a pattern of susceptibility in the late premenstrual window but does not quantify the number of seizures per cluster or confirm the presence of discrete clusters. Therefore, the proposed answer of '1 cluster per year, 2 per cluster' is not fully supported as the cluster count and cluster frequency are not clearly documented.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 7615

Interpretation: Good recovery. Full context supports perimenstrual clusters with 3 to 6 episodes per cycle, and the competing tonic-clonic events are less frequent.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_C",
  "design_action": "use_proposed_answer",
  "gold_label": "3 to 7 per month",
  "parse_errors": [],
  "proposed_answer": "1 cluster per month, 3 to 6 per cluster",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 7615,
  "verifier_label": "1 cluster per month, 3 to 6 per cluster"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "University College Hospital \n\nNational Hospital for Neurology and Neurosurgery \n\nClinic Date: 02 October 2025 \n\nDr Susan  \nUniversity College Hospital  \nNational Hospital for Neurology and Neurosurgery, London WC1N 3BG  \n\nDear Dr Susan,  \n\nEmily Carter, DOB: 22-07-1992, Hospital No: U914527 NHS No. 1045928376  \nFlat 3, 28 Northway Court, London, NW1 6QP \n\nSummary/ Diagnoses: Generalised epilepsy with suspected catamenial pattern/primary generalised tonic-clonic seizures and brief focal features reported by witness/iron deficiency anaemia under GP review/migraine without aura. \n\nMedication: Sodium valproate modified-release 500 mg twice daily.  \nClobazam 10 mg nocte (intermittent perimenstrual use as rescue per prior plan).  \nFerrous fumarate 210 mg once daily.  \nSumatriptan 50 mg as required for migraine.  \n\nI reviewed her in clinic today unaccompanied. She remains independent with daily activities and continues part-time work in retail. She has been using a menstrual tracking application consistently for the past 9 months and allowed me to review the app entries on her phone during the consultation. Energy levels fluctuate around menstruation; otherwise mood and sleep are stable. No recent intercurrent illness. \n\nSeizures: She describes short spells characterised by a sudden pause with fixed gaze and small chewing-like mouth movements, followed by quick recovery without confusion. These “brief pause-and-stare episodes with subtle mouth movements” occur predominantly in clusters within the 3 days prior to menses and the first 2 days of flow. The app logs correlate: over the last 6 cycles she recorded 3–6 of these brief episodes per cycle within that 5-day perimenstrual window, and none or at most one isolated episode outside it. In addition, there have been two generalised tonic-clonic seizures this year (February and July), each on day −1 to day +1 relative to menses onset, both occurring in the early morning. No injuries, tongue bite once, transient post-ictal myalgia, no incontinence. No known triggers aside from the cyclical pattern; she avoids alcohol and has been adherent to medication. Witness accounts are consistent with generalised onset; there is no history of focal neurological deficits preceding events. \n\nGiven the history, examination, past EEG reports (previous routine EEG with generalised spike–wave discharges) and seizure semiology, this fits with generalised epilepsy, with catamenial exacerbation supported by contemporaneous app records. \n\nPlan:  \n- Continue sodium valproate MR 500 mg twice daily; adherence reinforced.  \n- Perimenstrual clobazam as previously advised: 10 mg nightly from day −3 to day +2 relative to menses; she has found this reduces clustering without daytime sedation.  \n- Continue menstrual tracking app and bring screenshots to next review; patient will tag any seizure-day with “C1–C5” to denote cycle day for clearer correlation.  \n- Safety advice reiterated including bathing and height precautions; no driving as per DVLA regulations until seizure-free by required period; she understands.  \n- Bloods via GP: FBC, LFTs, and valproate level (trough) in the next 2 weeks; continue iron therapy and recheck ferritin in 3 months.  \n- Consider addition of lamotrigine as adjunct if catamenial pattern persists despite current perimenstrual clobazam; to be discussed at next visit.  \n- Review in neurology clinic in 4 months, sooner if breakthrough generalised tonic-clonic seizures occur.  \n\nYours sincerely",
  "competing_possibilities": [
    "Two generalised tonic-clonic seizures this year also noted, but less frequent and outside cluster count"
  ],
  "evidence_snippet": "These “brief pause-and-stare episodes with subtle mouth movements” occur predominantly in clusters within the 3 days prior to menses and the first 2 days of flow. The app logs correlate: over the last 6 cycles she recorded 3–6 of these brief episodes per cycle within that 5-day perimenstrual window, and none or at most one isolated episode outside it.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "1 cluster per month, 3 to 6 per cluster",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe.",
    "The text may describe seizures in groups without a clear group frequency."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": "true",
  "count_supported": "true",
  "current_highest_frequency_supported": "true",
  "missing_or_conflicting_parts": [],
  "quotes": [
    "These “brief pause-and-stare episodes with subtle mouth movements” occur predominantly in clusters within the 3 days prior to menses and the first 2 days of flow.",
    "The app logs correlate: over the last 6 cycles she recorded 3–6 of these brief episodes per cycle within that 5-day perimenstrual window"
  ],
  "reason": "The clinical text clearly states that over the last 6 menstrual cycles, the patient recorded 3 to 6 brief pause-and-stare episodes per cycle within a defined 5-day perimenstrual window, supporting the count and timeframe. The frequency of one cluster per month (one menstrual cycle) is implied by the 6 cycles over 6 months, making this the current highest seizure frequency described.",
  "recommended_action": ["use_proposed_answer"],
  "seizure_or_event_type_supported": "true",
  "timeframe_supported": "true"
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "These “brief pause-and-stare episodes with subtle mouth movements” occur predominantly in clusters within the 3 days prior to menses and the first 2 days of flow.",
    "The app logs correlate: over the last 6 cycles she recorded 3–6 of these brief episodes per cycle within that 5-day perimenstrual window"
  ],
  "reason": "The clinical text clearly states that over the last 6 menstrual cycles, the patient recorded 3 to 6 brief pause-and-stare episodes per cycle within a defined 5-day perimenstrual window, supporting the count and timeframe. The frequency of one cluster per month (one menstrual cycle) is implied by the 6 cycles over 6 months, making this the current highest seizure frequency described.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 10677

Interpretation: Wrong-to-wrong render. The model approved a plausible monthly answer, but the row remains incorrect under the scorer; this is not useful evidence for promotion.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_W_changed",
  "design_action": "use_proposed_answer",
  "gold_label": "1 cluster per month, multiple per cluster",
  "parse_errors": [],
  "proposed_answer": "1 per month",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 10677,
  "verifier_label": "1 per month"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Centre for Epilepsy\n\nNeurosciences Division \n\nClinic Date: 02 October 2025 \n\nDr Priya Shah \nConsultant Neurologist  \nCentre for Epilepsy  \nKing’s College Hospital, Denmark Hill, London SE5 9RS  \n\nDear Dr Priya Shah, \n\nMr Alan Peters, DOB: 22-08-1986, Hospital No: K8475201 NHS No. 9431127086  \nFlat 4, 12 Mariners Close, Aberdeen, AB11 5QJ  \n\nDiagnosis: \n\nRecurrent unprovoked seizures; current pattern reported as brief bursts occurring roughly once a month, typically soon after waking \n\nAetiology: \n\nUnclear despite prior routine EEG and MRI brain reported as within normal limits \n\nOther Medical Problems: \n\nMild gastro-oesophageal reflux disease managed with intermittent omeprazole; seasonal allergic rhinitis \n\nManagement Plan: \n\n- Continue current Levetiracetam at 1 g twice daily. Patient reports good tolerability without mood disturbance.\n- Rescue plan discussed for early-morning episodes; midazolam buccal 5 mg prescribed for clusters lasting over 10 minutes or repeated spells within one hour; partner trained and written guidance provided.\n- Safety advice reiterated regarding offshore duties: avoid lone work at height or in confined spaces for 24 hours following an event; ensure colleagues aware of rescue plan; maintain regular sleep schedule on rotation.\n- Bloods today: FBC, U&E, LFTs; arrange trough Levetiracetam level prior to next onshore review as a baseline only.\n- Seizure triggers diary to continue, with emphasis on sleep pattern and shift changes.\n- DVLA guidance reviewed; patient confirms no driving at present and understands to notify if any change.\n- Follow-up: telephone review scheduled to coincide with next onshore week in eight weeks; earlier contact via epilepsy nurse specialist if event frequency escalates or new features arise (e.g. prolonged confusion, injury, or events during wakeful daytime activity).\n\nThis patient works offshore on a two-weeks-on, three-weeks-off rotation. He reports a consistent pattern over the last three months of short runs of events approximately monthly, most often noted within the first hour after awakening on rest days following a change in shift while offshore. He describes brief loss of awareness with automatisms lasting under one minute, with rapid recovery and no injuries. No episodes at depth or during active lifting tasks. Sleep disruption and early starts preceding events were noted. He has had no emergency department attendances and no status episodes. Adherence to medication is good, with alarms set on his phone and dosing supervised when on the rig.\n\nWe agreed to continue current therapy, emphasising sleep hygiene and structured handovers to minimise abrupt shift transitions offshore. He will provide rig occupational health with the rescue protocol and contact details for our team. No immediate changes to medication are proposed, pending the seizure diary review and baseline levels at the next onshore appointment.\n\nYours sincerely",
  "competing_possibilities": [],
  "evidence_snippet": "current pattern reported as brief bursts occurring roughly once a month",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "1 per month",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": "true",
  "count_supported": "true",
  "current_highest_frequency_supported": "true",
  "missing_or_conflicting_parts": [],
  "quotes": [
    "current pattern reported as brief bursts occurring roughly once a month",
    "He reports a consistent pattern over the last three months of short runs of events approximately monthly"
  ],
  "reason": "The clinical text clearly states the seizure frequency as brief bursts occurring roughly once a month, with a consistent pattern over the last three months, providing count, timeframe, and context for the current highest seizure frequency.",
  "recommended_action": ["use_proposed_answer"],
  "seizure_or_event_type_supported": "true",
  "timeframe_supported": "true"
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "current pattern reported as brief bursts occurring roughly once a month",
    "He reports a consistent pattern over the last three months of short runs of events approximately monthly"
  ],
  "reason": "The clinical text clearly states the seizure frequency as brief bursts occurring roughly once a month, with a consistent pattern over the last three months, providing count, timeframe, and context for the current highest seizure frequency.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 10996

Interpretation: Strong recovery. The text directly states one to two morning clusters per month and about four events per cluster.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_C",
  "design_action": "use_proposed_answer",
  "gold_label": "1 to 2 cluster per month, 4 per cluster",
  "parse_errors": [],
  "proposed_answer": "1 to 2 cluster per month, 4 per cluster",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 10996,
  "verifier_label": "1 to 2 cluster per month, 4 per cluster"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Epilepsy Centre\n\nNeurosciences Division\n\nFrom: Dr Priya Shah (KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST)\nSent: 20 July 2018 10:12\nTo: neuro.clinic@kch.nhs.uk\nCc: Dr Michael O’Connor (KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST); Dr Hannah Lewis (KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST)\nSubject: Treatment review and titration plan\n\nDear Dr Patel,\n\nEpilepsy Diagnosis:\n\nCombined generalised and focal epilepsy (patient reports both generalised and focal epilepsy).\n\nBackground and context:\n\nHe cycles to work most days and reports that his routine is relatively consistent; this has been recorded for context. No recent intercurrent illness or sleep deprivation was volunteered.\n\nCurrent Medication:\n\n1. Lamotrigine 150 mg twice daily\n2. Brivaracetam 50 mg twice daily\n\nPrevious Anti-Seizure Medications (patient-reported):\n\n- Topiramate (stopped due to cognitive slowing)\n- Sodium valproate (stopped when planning family; weight gain reported)\n\nPresent Seizure Frequency:\n\nMorning clusters one - two×/month; ~four events over 90 min. He describes these as brief focal aware episodes with rising epigastric sensation and speech hesitation, occasionally progressing to generalised convulsions if the cluster is prolonged. There have been no injuries reported during recent events.\n\nAssessment and Plan of Action:\n\nThe pattern suggests persistent focal onset seizures with secondary generalisation within the context of combined generalised and focal epilepsy. Given partial response to lamotrigine and brivaracetam, I propose introducing lacosamide as adjunctive therapy and then reassessing. If tolerated, we will consider rationalising the regimen at follow-up.\n\nLacosamide titration schedule:\n- Week 1: 50 mg at night\n- Week 2: 50 mg twice daily\n- Week 3: 50 mg in the morning and 100 mg at night\n- Week 4: 100 mg twice daily (continue at this dose thereafter pending review)\n\nI have arranged a follow-up appointment in four months. At that visit, if stability is maintained and lacosamide is well tolerated, we will consider gradual reduction of brivaracetam while maintaining lamotrigine.\n\nWith best wishes,",
  "competing_possibilities": [
    "None"
  ],
  "evidence_snippet": "Morning clusters one - two×/month; ~four events over 90 min. He describes these as brief focal aware episodes with rising epigastric sensation and speech hesitation, occasionally progressing to generalised convulsions if the cluster is prolonged.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "1 to 2 cluster per month, 4 per cluster",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "Morning clusters one - two×/month; ~four events over 90 min.",
    "He describes these as brief focal aware episodes with rising epigastric sensation and speech hesitation, occasionally progressing to generalised convulsions if the cluster is prolonged."
  ],
  "reason": "The clinical text explicitly states the seizure frequency as morning clusters occurring one to two times per month, with approximately four events per cluster over 90 minutes. The seizure type is described as brief focal aware episodes with possible progression to generalised convulsions, matching the proposed answer. The timeframe (per month and per cluster duration) is clearly given, supporting the current highest seizure frequency.",
  "recommended_action": [
    "use_proposed_answer"
  ],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "Morning clusters one - two×/month; ~four events over 90 min.",
    "He describes these as brief focal aware episodes with rising epigastric sensation and speech hesitation, occasionally progressing to generalised convulsions if the cluster is prolonged."
  ],
  "reason": "The clinical text explicitly states the seizure frequency as morning clusters occurring one to two times per month, with approximately four events per cluster over 90 minutes. The seizure type is described as brief focal aware episodes with possible progression to generalised convulsions, matching the proposed answer. The timeframe (per month and per cluster duration) is clearly given, supporting the current highest seizure frequency.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 11259

Interpretation: Wrong-to-wrong oddity. The model selected the proposed answer even though the proposed answer is unknown; it remains non-improving and should be treated as noisy.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_W_changed",
  "design_action": "use_proposed_answer",
  "gold_label": "unknown",
  "parse_errors": [],
  "proposed_answer": "unknown",
  "quotes_exact": true,
  "routing_policy_action": "route_review",
  "routing_policy_label": null,
  "source_row_index": 11259,
  "verifier_label": "unknown"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 28 August 2018\n\nDr Amrita Patel\nRiverside Health Centre\n\n12 Millbank Close\nSouthwark\nLondon SE1 7TG\nDear Dr Amrita Patel\nHannah Cooper, DOB: 03-02-1987, Hospital No: H937462 NHS No. 7482916503\nFlat 12, 5A Warwick Street, London W1B 5NE\n\nDiagnoses/summary: Ongoing seizure disorder under review; implanted VNS in situ; no VNS parameter changes at today’s review. Prior investigations and semiology remain non-specific.\n\nNeuroimaging/EEG: Previous studies not clearly localising; no new imaging requested today.\n\nMedication history: Trials previously include levetiracetam and sodium valproate (both discontinued due to side effects). Currently taking lamotrigine 100 mg twice daily. Uses PRN buccal midazolam issued by community team (not used recently). No known drug allergies.\n\nCardiorespiratory: Reports occasional palpitations; baseline ECG earlier this year normal. VNS pocket site well healed; lead pathway non-tender.\n\nSocial/functional: Lives with partner; works part-time in retail. Sleep variable; trying to keep regular routine. Avoids alcohol; stays hydrated. Driving not undertaken and DVLA position understood. Mood described as stable though fatigued after poor sleep. ï¿½\n\nReview today: She attended alone and brought her diary. She feels overall stability since the VNS was implanted, with fewer post-event headaches. Last seizure on 27 May as per diary entry; there have been no clearly documented events since then, and overall frequency is uncertain as some spells may represent panic or presyncopal episodes rather than definite seizures. She uses the VNS magnet at prodromal sensations with mixed effect. No adverse effects from VNS beyond mild throat pulling at higher stimulation bursts, which is tolerable. Appetite and weight stable. No new neurological complaints. Ã‚Â·\n\nVNS: Device interrogated; battery status satisfactory; impedances within expected range. No parameter changes at this review. We rehearsed magnet use and safety. â€\n\nPlan:\n- Continue lamotrigine 100 mg twice daily; no dose change today.\n- Maintain seizure and symptom diary; we discussed distinguishing features of panic/presyncope vs probable epileptic events as patient-reported markers.\n- No VNS adjustments today; will reconsider at next visit if diary suggests recurrent events or increased clusters.\n- Routine bloods via GP: FBC, U&E, LFTs within the next 2–3 months for general monitoring (patient agreeable).\n- Safety advice reinforced (bathing/showering, heights, cooking). Provided written information leaflet.\n- Follow-up in clinic in 6 months or sooner if events recur; patient may contact epilepsy specialist nurse for interim support. \n\nThank you for your ongoing care. Please let me know if there are any concerns. \n\nYours sincerely",
  "competing_possibilities": [
    "Some spells may represent panic or presyncopal episodes rather than definite seizures"
  ],
  "evidence_snippet": "Last seizure on 27 May as per diary entry; there have been no clearly documented events since then",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "unknown",
  "review_reasons": [
    "The text lists dates or diary entries without a clear observation timeframe.",
    "The text may describe seizure freedom for one seizure type while another type remains active."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "Last seizure on 27 May as per diary entry; there have been no clearly documented events since then",
    "some spells may represent panic or presyncopal episodes rather than definite seizures"
  ],
  "reason": "The clinical text clearly states the last seizure was on 27 May with no clearly documented events since then, indicating a low or unknown seizure frequency. It also notes some spells may not be seizures, supporting uncertainty about seizure frequency. The seizure type (seizure), count (last seizure date), and timeframe (since 27 May to 28 August review) are all present and relevant to the current highest frequency.",
  "recommended_action": [
    "use_proposed_answer"
  ],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "Last seizure on 27 May as per diary entry; there have been no clearly documented events since then",
    "some spells may represent panic or presyncopal episodes rather than definite seizures"
  ],
  "reason": "The clinical text clearly states the last seizure was on 27 May with no clearly documented events since then, indicating a low or unknown seizure frequency. It also notes some spells may not be seizures, supporting uncertainty about seizure frequency. The seizure type (seizure), count (last seizure date), and timeframe (since 27 May to 28 August review) are all present and relevant to the current highest frequency.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 12438

Interpretation: Over-conservative. The model chose review rather than committing to the proposed low-frequency answer, increasing review burden.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_review",
  "design_action": "needs_review",
  "gold_label": "1 per day",
  "parse_errors": [],
  "proposed_answer": "2 to 3 per year",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 12438,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Department of Neurology\n\nClinic Date: 04 November 2015\n\nDr A. Patel\nEastborough Neurology Centre\nNeurology Outpatients, 12 Millbank Way, Eastborough EB2 4HT\n\nDear Dr A. Patel,\n\nEmily Carter, DOB: 14-03-1991, Hospital No: E927451 NHS No. 6045812379\nFlat 2, 16 Rowan Close, Eastborough EB3 1QP\n\nDiagnoses:\n\nAdult-onset seizure disorder; history of childhood febrile seizures noted.\n\nCurrent Medication:\n\n- Levetiracetam 1 g bd\n- Clobazam 10 mg nocte (intermittent use for clusters)\n\nPlan:\n\n- Continue current antiseizure regimen without changes today while we complete further evaluation.\n- Arrange prolonged ambulatory EEG and MRI brain with epilepsy protocol to clarify seizure onset and aid risk stratification.\n- Provide seizure first-aid and nocturnal supervision advice; reinforce SUDEP risk discussion given ongoing nocturnal events.\n- Safety counselling: bathing supervision, avoid heights/open water; driving not permitted and DVLA guidance reviewed.\n- Follow-up in 3 months, sooner if escalation occurs; consider medication optimisation or addition depending on results and tolerability.\n\nI reviewed Emily Carter in clinic today with her partner present. She reports a long-standing history of childhood febrile seizures, with no clear events through adolescence. In adulthood she developed recurrent seizures. Seizure control is inconsistent and while the caregiver perceives stability, she continues to have nightly generalised tonic-clonic seizures and intermittent tonic seizures 2 - 3 times per year, this has been her enduring seizure profile for many years. She describes the nocturnal events as occurring during sleep with a bitten tongue on several occasions and morning headache and myalgia. Daytime events are rare. There are no clear catamenial patterns. She identifies sleep deprivation and intercurrent illness as potential precipitants.\n\nShe is adherent with her current medication. Previous trials of lamotrigine were discontinued due to rash; topiramate caused cognitive side effects. No recent injuries, but there have been two prior bed falls without major harm. There is no family history of adult seizures. Neurological examination today is unremarkable. Routine blood tests earlier this month were within reference limits.\n\nWe discussed lifestyle measures, nocturnal safeguards (monitoring device, side-lying positioning), and the importance of regular sleep. An updated seizure diary was provided. I will review her after investigations to consider adjustments such as clobazam regularisation at night or alternative adjuncts depending on tolerability and findings.\n\nWith best wishes,\n\nYours sincerely",
  "competing_possibilities": [
    "No competing seizure frequency states reported"
  ],
  "evidence_snippet": "she continues to have nightly generalised tonic-clonic seizures and intermittent tonic seizures 2 - 3 times per year, this has been her enduring seizure profile for many years",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "2 to 3 per year",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": true,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "current_highest_frequency",
    "timeframe"
  ],
  "quotes": [
    "she continues to have nightly generalised tonic-clonic seizures and intermittent tonic seizures 2 - 3 times per year, this has been her enduring seizure profile for many years"
  ],
  "reason": "The clinical text states that the patient has nightly generalised tonic-clonic seizures and intermittent tonic seizures 2-3 times per year. The proposed answer '2 to 3 per year' only reflects the less frequent tonic seizures and omits the nightly generalised tonic-clonic seizures, which represent a higher seizure frequency. Therefore, the proposed answer does not represent the current highest seizure frequency. The count '2 to 3' and the timeframe 'per year' are supported for the tonic seizures, but the overall highest frequency (nightly seizures) is not supported by the proposed answer.",
  "recommended_action": [
    "needs_review"
  ],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": false
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": true,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "current_highest_frequency",
    "timeframe"
  ],
  "quotes": [
    "she continues to have nightly generalised tonic-clonic seizures and intermittent tonic seizures 2 - 3 times per year, this has been her enduring seizure profile for many years"
  ],
  "reason": "The clinical text states that the patient has nightly generalised tonic-clonic seizures and intermittent tonic seizures 2-3 times per year. The proposed answer '2 to 3 per year' only reflects the less frequent tonic seizures and omits the nightly generalised tonic-clonic seizures, which represent a higher seizure frequency. Therefore, the proposed answer does not represent the current highest seizure frequency. The count '2 to 3' and the timeframe 'per year' are supported for the tonic seizures, but the overall highest frequency (nightly seizures) is not supported by the proposed answer.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 12460

Interpretation: Over-conservative. The model sent a low-frequency row to review; safe, but not a scorable gain.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_review",
  "design_action": "needs_review",
  "gold_label": "1 per day",
  "parse_errors": [],
  "proposed_answer": "2 per year",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 12460,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "KINGS NEUROSCIENCES CENTRE\n\nClinic Date: 17 February 2015\n\nDr Wang\nSaffron Park Hospital\n\nSaffron Park, London, E14 7JL\nDear Dr Wang\nJohn Doe, DOB: 21-11-1982, Hospital No: P546484 NHS No. 5484656746\nFlat 15 Roundwood Road, London, E14 7JL\n\nI reviewed the above patient in the Neurology Clinic today. Since her last contact with our service, she reports ongoing difficulties with fatigue and variable alertness across the day. She has been actively reducing social alcohol use over recent months, noting fewer late evenings and better morning energy; this has coincided with a small improvement in daytime concentration, though she still experiences patchy attention in the afternoons. She denies recreational drug use. Sleep is generally 6–7 hours, often fragmented. There is no new history of head injury, illness, or intercurrent infection.\n\nIn discussing recent events with the patient and her caregiver, Seizure control is inconsistent and while the caregiver perceives stability, she continues to have nightly generalised convulsions seizures and intermittent tonic seizures two times per year, this has been her enduring seizure profile for many years. The caregiver keeps a diary and feels patterns are steady, whereas the patient highlights disrupted sleep and morning myalgia consistent with nocturnal convulsive activity. No clear precipitant was identified aside from occasional missed evening meals and prior higher alcohol intake, which she is now reducing. She has had no emergency department presentations in the past six months and there have been no reported injuries or tongue bites lately.\n\nCurrent medicines (as reported and reconciled today): Carbamazepine 400 mg b.d.; Levetiracetam (Keppra) 1250 mg b.d.; Topiramate 125 mg b.d.; Sodium Valproate 500 mg b.d.; Clobazam 10 mg b.d. She reports tolerating the regimen without rash or visual disturbance. Main adverse effects are tiredness and mild word-finding difficulty later in the day. Weight stable. Liver function tests from her GP three months ago were within reference ranges (per patient portal screenshot ï¿½ unable to verify today). She mentioned occasional leg itchiness in the evenings with scratch marks noted previously; there are no current breaks in the skin on examination today. Ã‚Â·\n\nWe discussed safety: supervision around baths/showers, awareness of nocturnal events, and ensuring a charged phone nearby overnight. She and her caregiver have an action plan for prolonged events and are comfortable with its use. She is keen to continue reducing alcohol intake socially and will aim to maintain more regular sleep. The caregiver confirms adherence with medication using a weekly pill organiser. \n\nGiven the long-standing pattern and her report of fewer late nights since reducing social alcohol, we agreed to maintain current therapy for now while we gather further objective information. I have arranged a short ambulatory EEG with overnight recording to characterise nocturnal events and a basic blood panel (U&Es, LFTs, FBC) via her GP. We will also provide access to our epilepsy nurse specialist for practical support and to review her seizure diary structure. I did not make any dose changes today â€ pending review of the recordings and bloods. If there is evidence of persistent nocturnal convulsive activity on monitoring, we will consider rationalising her polytherapy at the next visit.\n\nFollow-up: 3 months in clinic, sooner if her caregiver notes escalation or if she has any daytime convulsions. She has the contact number for our nurse line for interim queries.\n\nYours sincerely",
  "competing_possibilities": [
    "Caregiver perceives stability but patient reports ongoing seizures"
  ],
  "evidence_snippet": "she continues to have nightly generalised convulsions seizures and intermittent tonic seizures two times per year, this has been her enduring seizure profile for many years",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "2 per year",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": true,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "timeframe",
    "current_highest_frequency"
  ],
  "quotes": [
    "she continues to have nightly generalised convulsions seizures and intermittent tonic seizures two times per year, this has been her enduring seizure profile for many years"
  ],
  "reason": "The clinical text supports a count of 'two times per year' for intermittent tonic seizures but also states she has 'nightly generalised convulsions seizures,' which is a higher frequency. The proposed answer '2 per year' does not reflect the highest seizure frequency because the nightly seizures are more frequent. The timeframe for the '2 per year' count is supported, but the overall highest seizure frequency is not supported by the proposed answer.",
  "recommended_action": [
    "needs_review"
  ],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true,
  "count_supported": true
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": true,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "timeframe",
    "current_highest_frequency"
  ],
  "quotes": [
    "she continues to have nightly generalised convulsions seizures and intermittent tonic seizures two times per year, this has been her enduring seizure profile for many years"
  ],
  "reason": "The clinical text supports a count of 'two times per year' for intermittent tonic seizures but also states she has 'nightly generalised convulsions seizures,' which is a higher frequency. The proposed answer '2 per year' does not reflect the highest seizure frequency because the nightly seizures are more frequent. The timeframe for the '2 per year' count is supported, but the overall highest seizure frequency is not supported by the proposed answer.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 13209

Interpretation: Conservative wrong-to-wrong. The model chose unknown, which is safe but does not recover the correct answer.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_W_changed",
  "design_action": "use_unknown",
  "gold_label": "1 per 8 month",
  "parse_errors": [],
  "proposed_answer": "unknown",
  "quotes_exact": true,
  "routing_policy_action": "route_review",
  "routing_policy_label": null,
  "source_row_index": 13209,
  "verifier_label": "unknown"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 02 October 2025\n\nDr Kate\nHealth Centre\n\nKeele University, Keele, Newcastle\n\nStaffordshire ST5 5BG\nDear Dr Kate\nJamie Turner, DOB: 14-03-1990, Hospital No: K593217 NHS No. 7482601935\n12 Maple Crescent, Newcastle-under-Lyme, ST5 8QH \n\nDiagnoses/summary: Recurrent seizures of uncertain classification; catamenial pattern suspected based on symptom diary and menstrual tracking app entries; prior routine EEG non-diagnostic; MRI brain (2021) structurally unremarkable\n\nPrevious medication: Levetiracetam (mood lability), Lamotrigine (rash), Topiramate (cognitive slowing), Clobazam PRN (sedation)\n\nNot taken: Zonisamide, Lacosamide, Perampanel, Brivaracetam, Pregabalin, Valproate\n\nCardiac history unremarkable; no known syncope. Thyroid function normal (2024). No known drug allergies.\n\nI reviewed Jamie Turner in clinic today. He attended alone and brought printouts from his menstrual tracking app, which he uses to cross-reference his partner’s cycle and his own recorded symptoms; he also keeps a personal health diary where he logs sleep and stress. He reports improved overall stability since simplifying to one antiseizure medicine earlier this year. On Carbamazepine monotherapy he was seizure-free for 8 months, until a focal impaired-awareness seizure occurred 2 Thursdays ago. He describes a brief warning of queasiness and a metallic taste, followed by a blank spell lasting approximately 60–90 seconds, with subsequent fatigue for several hours. There was no witnessed convulsion, tongue-bite, or incontinence. He denies missed doses and reports good adherence. He notes increased stress at work that week and shorter sleep.\n\nA possible catamenial relationship is suspected because his diary shows clusters of auras and brief blanks roughly every 4–5 weeks; he has correlated these with his partner’s menstrual cycle timing using the app. He understands this may reflect cyclical factors in the household routine rather than a direct biological link, but he finds the patterning helpful for anticipating higher-risk days.\n\nCurrent medication:\n- Carbamazepine modified-release 400 mg twice daily\n- Folic acid 5 mg daily (self-initiated)\n- Vitamin D3 1000 IU daily\n\nExamination today was unremarkable with normal speech, eye movements, power, coordination and gait. No rash. Weight stable. Bloods (July 2025): normal FBC/U&E/LFT; Carbamazepine level mid-therapeutic.\n\nPlan:\n- Continue current Carbamazepine dose for now; he prefers no change after a single breakthrough event.\n- Arrange repeat serum Carbamazepine level and LFT/U&E in 6–8 weeks, or sooner if further events occur.\n- Request ambulatory EEG to capture interictal activity during a predicted higher-risk window based on his tracking app; he will share dates via the patient portal.\n- Provide seizure safety advice reviewed today (showers over baths, avoid heights/operating machinery on days with auras, ensure bystanders know first aid).\n- Ask him to continue detailed diary entries including sleep, stress, illness, and the app-referenced cycle notes. He agrees to upload monthly PDFs.\n- If additional events occur, options discussed (patient-informed, non-committal today): adjust Carbamazepine dose; consider add-on Brivaracetam or Zonisamide; or review for device/advanced therapies if events recur despite optimisation.\n- DVLA guidance reiterated: he is currently driving and remains eligible, but must cease and inform DVLA if further impaired-awareness events occur; he understands and agrees.\n\nI will review him in 4 months, or sooner if there is another event or any concern. Please let me know if there are issues with monitoring bloods locally.\n\nYours sincerely",
  "competing_possibilities": [
    "No competing seizure frequency states clearly described"
  ],
  "evidence_snippet": "On Carbamazepine monotherapy he was seizure-free for 8 months, until a focal impaired-awareness seizure occurred 2 Thursdays ago.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "unknown",
  "review_reasons": [
    "The text lists dates or diary entries without a clear observation timeframe.",
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": ["count", "timeframe", "current_highest_frequency"],
  "quotes": [
    "On Carbamazepine monotherapy he was seizure-free for 8 months, until a focal impaired-awareness seizure occurred 2 Thursdays ago."
  ],
  "reason": "The clinical text provides a single recent seizure event occurring 2 weeks ago after an 8-month seizure-free period, but does not specify a seizure count over a defined timeframe or a current highest seizure frequency. The mention of clusters of auras every 4-5 weeks is suggestive but not quantified as seizures, and no clear seizure frequency count or timeframe is given to support a seizure frequency answer.",
  "recommended_action": ["use_unknown"],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": false
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": false,
  "missing_or_conflicting_parts": [
    "count",
    "timeframe",
    "current_highest_frequency"
  ],
  "quotes": [
    "On Carbamazepine monotherapy he was seizure-free for 8 months, until a focal impaired-awareness seizure occurred 2 Thursdays ago."
  ],
  "reason": "The clinical text provides a single recent seizure event occurring 2 weeks ago after an 8-month seizure-free period, but does not specify a seizure count over a defined timeframe or a current highest seizure frequency. The mention of clusters of auras every 4-5 weeks is suggestive but not quantified as seizures, and no clear seizure frequency count or timeframe is given to support a seizure frequency answer.",
  "recommended_action": "use_unknown",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": false
}
```

</details>

### Row 15193

Interpretation: Good safety behavior with full context. The model saw ongoing absence seizures and rejected the zero-generalized-seizure answer as not applying to all seizure types.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "C_to_review",
  "design_action": "needs_review",
  "gold_label": "multiple per 13 month",
  "parse_errors": [],
  "proposed_answer": "0 per 9 to 10 month",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 15193,
  "verifier_label": null
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "King's College Hospital\n\nDepartment of Neurosciences\n\nClinic Date: 09 October 2023\n\nDr Sarah Ahmed\nConsultant Neurologist\nKing's College Hospital\nDepartment of Neurosciences, King's College Hospital, London SE5 9RS\n\nDear Dr Sarah Ahmed\nConsultant Neurologist,\n\nDaniel Roberts, DOB: 14-03-1988, Hospital No: KCH1029384 NHS No. 9876543210\n12 Brookfield Road, London, SE15 3AB\n\nThank you for asking me to review your patient. He has a background history of migraine, noted over many years, but the current clinical focus is epilepsy. He reports a clear improvement in his seizure control over the past year. He has had no generalised seizures since 9 - 2022, though continues to experience brief absence from time to time. These brief episodes are described as sudden lapses in awareness lasting a few seconds, with immediate recovery and no confusion. His partner has occasionally noticed a brief pause in conversation and a vacant stare during these events, without automatisms or falls.\n\nFrom the clinical history and prior EEG documentation available in the notes, the features are most consistent with generalised epilepsy. There is no reliable history of focal onset, auras, or lateralising postures, and previous routine EEG reportedly showed generalised spike-and-wave discharges. He is currently maintained on levetiracetam with good tolerability; he denies behavioural change, mood disturbance, or cognitive adverse effects. He has also trialled topiramate in the past for migraine prophylaxis but discontinued due to paraesthesia and word-finding difficulties. Migraines now occur infrequently and are managed with simple analgesia and trigger avoidance; there is no current use of triptans.\n\nThere is no recent history of nocturnal events, tongue biting, or injuries. He does not drive and understands DVLA regulations. Sleep deprivation is a recognised trigger for his absences, and he is actively working on regular sleep and hydration. Alcohol intake is minimal and there is no recreational drug use. No intercurrent systemic illness has been reported.\n\nOn examination today he was well, alert and oriented, with normal speech and language. Neurological examination was unremarkable. Bloods from his GP last month, including U&E, LFT, and full blood count, were normal per the records provided. We discussed ongoing management of his generalised epilepsy, the good seizure control to date, and the importance of adherence. Given the sustained absence of generalised seizures since September 2022 and only brief intermittent absences, I propose no immediate change to therapy. He is agreeable to continue current medication and lifestyle measures. We reviewed red flags for escalation, including any recurrence of generalised tonic–clonic seizures, increasing frequency of absences impacting function, or emergence of new neurological symptoms.\n\nPlan:\n- Generalised epilepsy with good current control: continue levetiracetam at the present dose.\n- Encourage sleep hygiene and avoidance of known triggers; maintain seizure diary documenting absences.\n- Safety counselling reinforced; patient aware of DVLA guidance and to notify us if events change.\n- Arrange follow-up in 6 months, sooner if there is any breakthrough generalised seizure activity or significant increase in absence frequency.\n\nPlease let me know if there are any concerns or if further information becomes available from prior EEGs or imaging that would alter management.\n\nYours sincerely",
  "competing_possibilities": [
    "Brief absence seizures continue intermittently, so not fully seizure-free for all seizure types"
  ],
  "evidence_snippet": "He has had no generalised seizures since 9 - 2022, though continues to experience brief absence from time to time.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "0 per 9 to 10 month",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": ["count", "timeframe"],
  "quotes": [
    "He has had no generalised seizures since 9 - 2022, though continues to experience brief absence from time to time."
  ],
  "reason": "The clinical text confirms no generalised seizures since September 2022 and ongoing brief absence seizures intermittently, but does not specify an exact count or precise timeframe frequency for the absences. The proposed answer '0 per 9 to 10 month' implies a count of zero seizures over a 9-10 month period, which is only supported for generalised seizures, not for absences. The absences continue intermittently, so the count of zero is not supported for all seizure types. The timeframe is implied but not explicitly detailed for absences.",
  "recommended_action": ["needs_review"],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": false
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": false,
  "count_supported": false,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [
    "count",
    "timeframe"
  ],
  "quotes": [
    "He has had no generalised seizures since 9 - 2022, though continues to experience brief absence from time to time."
  ],
  "reason": "The clinical text confirms no generalised seizures since September 2022 and ongoing brief absence seizures intermittently, but does not specify an exact count or precise timeframe frequency for the absences. The proposed answer '0 per 9 to 10 month' implies a count of zero seizures over a 9-10 month period, which is only supported for generalised seizures, not for absences. The absences continue intermittently, so the count of zero is not supported for all seizure types. The timeframe is implied but not explicitly detailed for absences.",
  "recommended_action": "needs_review",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": false
}
```

</details>

### Row 15593

Interpretation: Good recovery. The text supports clusters every five days with 2 to 4 events per cluster, so approving the proposed cluster answer is grounded.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_C",
  "design_action": "use_proposed_answer",
  "gold_label": "1 cluster per 5 day, 2 to 4 per cluster",
  "parse_errors": [],
  "proposed_answer": "1 cluster per 5 day, 2 to 4 per cluster",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 15593,
  "verifier_label": "1 cluster per 5 day, 2 to 4 per cluster"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "King's College Hospital \n\nDepartment of Neurosciences \n\nClinic Date: 23 March 2015 \n\nDr Aisha Rahman\nConsultant Neurologist  \nKing's College Hospital  \nDepartment of Neurosciences, King's College Hospital, London SE5 9RS  \n\nDear Dr Aisha Rahman\nConsultant Neurologist,  \n\nSarah Whitfield, DOB: 14-03-1986, Hospital No: KCH-872114 NHS No. 9427753106  \n12 Brookside Close, London, SE15 3HT\n\nThank you for asking me to review your patient. I met her in clinic accompanied by her partner, and we also had a brief telephone contribution from a facilitator of her local peer support group. The patient has kept a contemporaneous diary and invited two group peers to observe two community episodes; their notes broadly align with the partner’s account.\n\nShe reports a long-standing history of episodic events characterised by a brief prodrome of light-headedness and a sense of internal \"pressure,\" followed by loss of awareness with stiffening and low-amplitude shaking, sometimes with a short cry at onset. Post-event, she is fatigued and disoriented for 20–40 minutes, occasionally longer. There is no consistent injury pattern, but she has had tongue biting twice this year and one minor shoulder strain; no incontinence was reported. Triggers are not clearly defined, though she suspects sleep disruption and high-stress days may lower her threshold. Night-time events are rare by her account; the partner has witnessed two nocturnal episodes over the past six months, each with brief confusion on waking.\n\nRegarding frequency, the current pattern is variable but with a recognisable cadence. She can occasionally manage five days without seizures, though this is usually followed by a day of clustering, with two to four events. This pattern is corroborated by diary entries and partner observation and is consistent with peer notes taken during two observed days earlier this summer. Rescue measures have not been required to date, and there have been no emergency attendances in the last twelve months.\n\nMedication history includes levetiracetam previously (discontinued due to mood irritability), lamotrigine (partial benefit but dose-limited by rash), and currently lacosamide at a moderate dose, which she tolerates. She has not tried brivaracetam or perampanel. She does not drive. Menses are regular; she does not note a cyclic pattern. Alcohol intake is minimal, and she denies recreational drug use. Past medical history includes mild asthma; no known cardiac disease. Family history is non-contributory for seizures.\n\nNeurological examination in clinic today was non-focal. Cognitive screening was unremarkable. Routine bloods earlier this month were within reference ranges, and a prior MRI (reported last year) noted no structural abnormality. A prior routine EEG was non-diagnostic.\n\nGiven the persisting events with clustering and the present uncertainties regarding semiology and physiology, I discussed further characterisation. The patient is open to structured observation and welcomes the idea of integrating collateral information from her peer support group. I will therefore arrange ambulatory video-EEG monitoring with event-marking and encourage continued use of her detailed seizure diary, including peer-observer notes when available. Depending on those results, we can consider inpatient telemetry if necessary. No immediate medication change was made today; she prefers to await monitoring data before contemplating adjustments. We also discussed general measures: consistent sleep routine, hydration, and pacing on high-demand days; she will continue these self-management strategies.\n\nI will update you once monitoring is complete and we have a clearer synthesis. Please let me know if there are interim concerns or if new information arises from your records.\n\nYours sincerely",
  "competing_possibilities": [
    "None noted"
  ],
  "evidence_snippet": "Regarding frequency, the current pattern is variable but with a recognisable cadence. She can occasionally manage five days without seizures, though this is usually followed by a day of clustering, with two to four events. This pattern is corroborated by diary entries and partner observation and is consistent with peer notes taken during two observed days earlier this summer.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "1 cluster per 5 day, 2 to 4 per cluster",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe.",
    "The text may describe seizures in groups without a clear group frequency."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": "true",
  "count_supported": "true",
  "current_highest_frequency_supported": "true",
  "missing_or_conflicting_parts": [],
  "quotes": [
    "She can occasionally manage five days without seizures, though this is usually followed by a day of clustering, with two to four events.",
    "This pattern is corroborated by diary entries and partner observation and is consistent with peer notes taken during two observed days earlier this summer."
  ],
  "reason": "The clinical text clearly states a seizure frequency pattern with a timeframe (five days without seizures followed by a day of clustering), a count (two to four events per cluster), and corroborating context from diary and partner observations, supporting the proposed answer.",
  "recommended_action": ["use_proposed_answer"],
  "seizure_or_event_type_supported": "true",
  "timeframe_supported": "true"
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "She can occasionally manage five days without seizures, though this is usually followed by a day of clustering, with two to four events.",
    "This pattern is corroborated by diary entries and partner observation and is consistent with peer notes taken during two observed days earlier this summer."
  ],
  "reason": "The clinical text clearly states a seizure frequency pattern with a timeframe (five days without seizures followed by a day of clustering), a count (two to four events per cluster), and corroborating context from diary and partner observations, supporting the proposed answer.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

### Row 15672

Interpretation: Wrong-to-wrong render. The model approved a broad multiple-per-day answer but did not fix the row under the scoring policy.

Row summary:

```json
{
  "call_errors": [],
  "call_status": "ok",
  "delta": "W_to_W_changed",
  "design_action": "use_proposed_answer",
  "gold_label": "1 per day",
  "parse_errors": [],
  "proposed_answer": "multiple per day",
  "quotes_exact": true,
  "routing_policy_action": "route_unknown",
  "routing_policy_label": "unknown",
  "source_row_index": 15672,
  "verifier_label": "multiple per day"
}
```

<details>
<summary>Full model input</summary>

```json
{
  "clinical_text": "Epilepsy Centre \n\nNeurosciences Division \n\nClinic Date: 02 October 2025 \n\nDr Patel  \nSt Thomas' Hospital  \nNeurosciences Department, Westminster Bridge Road, London SE1 7EH  \n\nDear Dr Patel,  \n\nEmily Dawson, DOB: 14-11-1990, Hospital No: R928417 NHS No. 7401563928  \n58 Alder Grove, London, SW8 1JP  \n\nDiagnoses: \n\nSymptomatic generalised epilepsy. \n\nI reviewed Emily Dawson in clinic today. She attends alone and reports a notable deterioration in her seizure control over the past 4–5 months. Historically, she has generalised epilepsy and she has a past history of atonic seizures, drop attacks and generalised tonic–clonic seizures one to two times per year, but seizure control has been excellent, and she has now been seizure free for several years. However, since increasing work pressures and longer hours, she has experienced clusters of jumps almost daily, particularly on workdays, consistent with her report that high workload has been a precipitating factor. She describes these as brief, sudden axial and upper limb jerks with occasional object dropping; she also notes intermittent disequilibrium and near‑falls. There have been two definite drop events in the last six weeks. No generalised tonic–clonic seizures have been witnessed, but her partner reports brief staring and word‑finding pauses on two occasions. \n\nShe links the worsening to work‑related stress and poor sleep. Events tend to cluster on workdays per patient report, with relative improvement on weekends. There is no recent intercurrent illness, alcohol excess, or new medications. She denies missed anti‑seizure medication, though acknowledges variable timing on late shifts. Menses regular; no pregnancy. \n\nCurrent treatment: lamotrigine 150 mg twice daily; levetiracetam 1,000 mg twice daily. She has tolerated these without rash or mood lability; mild irritability attributed to work fatigue. She is not using rescue medication currently. No vagus nerve stimulator in situ. \n\nExamination today was unremarkable: alert, oriented, speech fluent; cranial nerves intact; no focal motor deficit; gait steady in clinic though she describes occasional morning unsteadiness. Blood pressure 118/72, pulse 72 regular. \n\nGiven the deterioration and daily clustering of myoclonic‑type events, I have discussed seizure safety at work (avoidance of ladders, hot surfaces; shower rather than bath; supervision with heavy machinery) and driving regulations. She does not currently drive. We agreed to obtain updated bloods (U&Es, LFTs, FBC, vitamin D) and anti‑seizure medication levels where available, and to arrange an EEG, including activation procedures, to look for generalised spike‑wave or polyspike‑wave activity. A brain MRI from 2018 was normal; we will repeat MRI if clinically indicated after EEG review. \n\nShe will start a structured sleep routine and stress‑reduction plan (patient‑led), and keep a seizure diary noting triggers, timing, and any clusters. We also discussed the option of dose optimisation if events persist; plan to consider a cautious lamotrigine uptitration or adjunctive valproate discussion if appropriate and acceptable in future. She understands this is an interim plan while we complete investigations. \n\nIn summary, despite several years of excellent control, there is clear worsening temporally associated with occupational stress: she has experienced clusters of jumps almost daily, with occasional drops and brief absences suggested. This represents a deterioration from her prior baseline of rare events. I have asked her to contact the service urgently if she has any generalised tonic–clonic seizures, injuries, or any prolonged clusters. \n\nFollow‑up in 6–8 weeks after EEG, or sooner if needed. \n\nYours sincerely",
  "competing_possibilities": [
    "Patient historically seizure free for several years but now deteriorated with daily clusters"
  ],
  "evidence_snippet": "she has experienced clusters of jumps almost daily, particularly on workdays, consistent with her report that high workload has been a precipitating factor.",
  "output_schema": {
    "all_answer_parts_supported": "true or false.",
    "count_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "missing_or_conflicting_parts": [
      "Short names of any unsupported or conflicting parts."
    ],
    "quotes": [
      "Exact copied phrases from clinical_text."
    ],
    "reason": "Brief explanation using only the provided clinical text.",
    "recommended_action": [
      "use_proposed_answer",
      "use_unknown",
      "needs_review"
    ],
    "seizure_or_event_type_supported": "true or false.",
    "timeframe_supported": "true or false."
  },
  "proposed_answer": "multiple per day",
  "review_reasons": [
    "The text may not give enough information for both count and timeframe."
  ],
  "system_prompt": "Check whether the proposed seizure-frequency answer is supported by the clinical text. A supported answer has a seizure or event type, a count, a timeframe, and enough context to show it applies to the current highest seizure frequency. The evidence snippet is the passage that originally suggested the answer, but use the full clinical text when dates, currentness, seizure types, or other context matters. Do not fill in missing parts from assumptions. Return only JSON matching the requested fields.",
  "task_design": "support_parts_full_letter"
}
```

</details>

<details>
<summary>Raw model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "she has experienced clusters of jumps almost daily, particularly on workdays",
    "clusters of jumps almost daily",
    "This represents a deterioration from her prior baseline of rare events"
  ],
  "reason": "The clinical text clearly states that the patient, previously seizure free for several years, now experiences clusters of jumps almost daily, indicating multiple events per day. The timeframe of 'almost daily' is explicitly mentioned, and the event type (clusters of jumps, myoclonic-type events) is described in detail, supporting the proposed answer of 'multiple per day' as the current highest seizure frequency.",
  "recommended_action": ["use_proposed_answer"],
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>

<details>
<summary>Parsed model output</summary>

```json
{
  "all_answer_parts_supported": true,
  "count_supported": true,
  "current_highest_frequency_supported": true,
  "missing_or_conflicting_parts": [],
  "quotes": [
    "she has experienced clusters of jumps almost daily, particularly on workdays",
    "clusters of jumps almost daily",
    "This represents a deterioration from her prior baseline of rare events"
  ],
  "reason": "The clinical text clearly states that the patient, previously seizure free for several years, now experiences clusters of jumps almost daily, indicating multiple events per day. The timeframe of 'almost daily' is explicitly mentioned, and the event type (clusters of jumps, myoclonic-type events) is described in detail, supporting the proposed answer of 'multiple per day' as the current highest seizure frequency.",
  "recommended_action": "use_proposed_answer",
  "seizure_or_event_type_supported": true,
  "timeframe_supported": true
}
```

</details>
