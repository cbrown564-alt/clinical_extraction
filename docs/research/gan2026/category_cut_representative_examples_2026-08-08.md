# Gan 2026 category-cut representative examples

Paper-library role: detailed development examples; use the [row-evidence workbook](../artifacts/paper_source_row_evidence_2026-08-10.xlsx) for filtering.

Real development letters, with two examples for the dominant ordinary-rate bucket and one for each other gold-defined bucket. The examples explain the aggregate category cut; they do not estimate category performance on their own.

Split: `dev750` · LLM model: `GPT-5.6 Sol` · rules baseline: retained deterministic artifact.

## How to read the cases

The excerpt is the smallest source window covering the gold or method evidence. `correct` means Purist-correct for Gan; it is not a clinical-validation judgment.

## `ordinary_point_rate`

One countable rate; the main Gan mass.

### Example 1

**Development row:** `4026`  
**Gold:** `1 per month`

### Source excerpt

> …downward trend, with only a single brief spell in the most recent calendar month and none reported so far this month. The patient reports better sleep hygiene and consistent dosing times, which coincide with the reduction in events. Present Seizure Frequency: Now down to roughly one brief absence episode in a typical month, with some months entirely event-free. Plan of Action: - Continue lamotrigine 100 mg twice daily without change. - Keep clobazam as an intermittent option for clusters, although none have occurred recently. - Maintain daily seizure diary entries and reminder prompts, as this appears to be a key factor in the recent improvement. - Safety advice reiterated; patient understands driving restrictions and when to seek urgent help. - Arrange follow-up in four m…

### Three outputs

| Method | Answer | Evidence used | Purist |
| --- | --- | --- | --- |
| Rules | `1 per month` | “one brief absence episode in a typical month” | correct |
| LLM | `1 per month` | “Now down to roughly one brief absence episode in a typical month, with some months entirely event-free.” | correct |
| LLM with rules | `1 per month` | “Now down to roughly one brief absence episode in a typical month” | correct |

What this case makes visible: this is the easy, shared-competence case—all three methods recover the same ordinary rate from one explicit sentence.

### Example 2

**Development row:** `4402`  
**Gold:** `7 per 7 month`

### Source excerpt

> …as improved consistency, and his partner has visibility of adherence via the shared app. There have been no adverse effects reported from medication and no new neurological symptoms. Seizure record (patient-reported and cross-checked with his app timestamps): Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1. He notes typical events are brief with preserved awareness at onset, a déjà vu sensation, metallic taste, and occasional right-hand fumbling; duration under two minutes, followed by mild fatigue. No injuries, no emergency attendances. There is no clear photic sensitivity. Sleep disruption and missed doses were the most consistent antecedents before the alarm/NFC system was introduced. Medication: Levetiracetam 1 g t…

### Three outputs

| Method | Answer | Evidence used | Purist |
| --- | --- | --- | --- |
| Rules | `7 per 7 month` | “Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1” | correct |
| LLM | `3 per 3 month` | “May x1, Jun x1, Jul x1” | correct |
| LLM with rules | `7 per 7 month` | “Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1.” | correct |

Hybrid is a no-call calendar-log replay on the saved span. Older hybrid panels still store `14 per 14 month`.

What this case makes visible: the methods can read the same source text and still differ in selection, representation, or canonical rendering.

## `cluster_burden`

Cluster grammar must preserve both cluster frequency and seizures per cluster.

**Development row:** `15431`  
**Gold:** `1 cluster per 4 month, 5 per cluster`

### Source excerpt

> …cetam since March 2025 Levetiracetam 500 mg twice a day (patient-reported adherence, no missed doses in the last 8 weeks) Levetiracetam Blood Level: 20 September 2025: 14 µg/mL (laboratory therapeutic reference 12–46 µg/mL). Dose 500 mg twice a day. Seizures: She may remain seizure-free for up to 4 month, but then will experience clusters of 5 seizures in a single day. These clusters have reduced in intensity and recovery time over the last two episodes, with no injuries or prolonged post-ictal confusion reported. No clear auras or focal features described. I reviewed Amelia Hart today in follow-up. Since relocating at work from the hot cookline to a prep area with improved ventilation, she reports fewer heat and fume triggers, better sleep continuity, and reduced daytime fatigue.…

### Three outputs

| Method | Answer | Evidence used | Purist |
| --- | --- | --- | --- |
| Rules | `1 cluster per 4 month, 5 per cluster` | “seizure-free for up to 4 month, but then will experience clusters of 5 seizures in a single day” | correct |
| LLM | `unknown` | “She may remain seizure-free for up to 4 month, but then will experience clusters of 5 seizures in a single day.” | wrong |
| LLM with rules | `5 per 4 month` | “but then will experience clusters of 5 seizures in a single day” | correct |

What this case makes visible: the methods can read the same source text and still differ in selection, representation, or canonical rendering.

## `seizure_free`

The note supports a quiet interval rather than an active rate.

**Development row:** `2907`  
**Gold:** `seizure free for 6 month`

### Source excerpt

> …spital, Denmark Hill, London SE5 9RS Dear Dr Maya Patel, Alex Turner, DOB: 22-08-1991, Hospital No: A9135726 NHS No. 9432086157 Flat 12, 4 Beacon Yard, London, SE1 3AB Diagnosis: Recurrent seizures of undetermined classification; current control satisfactory. Seizure-free since 27 March 2024 as per patient and collateral reports. Aetiology: Unclear. No structural lesion identified on prior MRI (2022) and no clear precipitant identified beyond photic exposure at work. Other Medical Problems: Migraine without aura, intermittent; vitamin D insufficiency on replacement. Management Plan: Continue Levetiracetam 1,000 mg twice daily and Sodium Valproate 300 mg mane, 600 mg nocte; maintain single consistent brands. Check trough levels and U&E/LFTs at next review. Arrange repeat EEG with photic stimulation protocol given occupational exposure. Occupational health note provided to advise reasonable adjustments around strobe sequences and ensuring supervised environment if exposures are unavoidable. Driving advice reiterated as per DVLA guidance. Review in six months or sooner if breakthrough events or adverse effects. This stage lighting technician reports that colleagues may occasionally wi…

### Three outputs

| Method | Answer | Evidence used | Purist |
| --- | --- | --- | --- |
| Rules | `seizure free for 6 month` | “Seizure-free since 27 March 2024” | correct |
| LLM | `unknown` | “colleagues may occasionally witness events during intense strobe sequences” | wrong |
| LLM with rules | `seizure free for 6 month` | “however, he has been Seizure-free since 27 March 2024.” | correct |

Hybrid is a no-call elapsed-since-date replay on the saved Sol-style span. Older hybrid panels still store `seizure free for multiple year`.

What this case makes visible: the methods can read the same source text and still differ in selection, representation, or canonical rendering.

## `range_rate`

Both ends of a rate range matter.

**Development row:** `14187`  
**Gold:** `2 to 3 per month`

### Source excerpt

> …guidance and employer policy). Arrange follow-up in six months with trough Lamotrigine level and U&E/LFT monitoring. She reports a demanding role as a warehouse picker working between tall racking and narrow aisles, with variable lifting tasks and shift pace. She discontinued Valproate on 10 Jul. Shortly afterwards, she experienced 2 to 3 seizures, one triggered by missed medication. She has remained seizure-free since then. She attributes improvement to stricter adherence, better sleep on late shifts, and reduction in caffeine. There have been no injuries, no myoclonic jerks on waking in the last month, and no absence episodes witnessed by colleagues. We reviewed common precipitants, including missed doses and sleep deprivation, and she has implemented reminders and uses a pill organiser. She understands to avoid operating pallet stack…

### Three outputs

| Method | Answer | Evidence used | Purist |
| --- | --- | --- | --- |
| Rules | `2 to 3 per month` | “Shortly afterwards, she experienced 2 to 3 seizures” | correct |
| LLM | `unknown` | “Shortly afterwards, she experienced 2 to 3 seizures, one triggered by missed medication. She has remained seizure-free since then.” | wrong |
| LLM with rules | `2 to 3 per 1 month` | “She has remained seizure-free since then.” | correct |

What this case makes visible: the methods can read the same source text and still differ in selection, representation, or canonical rendering.

## `unknown_sentinel`

The gold answer withholds a rate.

**Development row:** `2166`  
**Gold:** `unknown`

### Source excerpt

> Epilepsy Centre Neurosciences Division From: Dr Priya Shah (KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST) Sent: 27 June 2019 11:20 To: epilepsy.clinic@nhs.net Cc: Dr Michael Turner (KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST); Dr Helen Brooks (KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST) Subject: Treatment review and guidance Hi Priya Epilepsy Diagnosis: Generalised epilepsy Present Medication: 1. Sodium Valproate 300 mg in the morning and 500 mg at night 2. Lamotrigine 50 mg twice daily Present Seizure Frequency: Patient reports frequent petit mal recently, particularly on waking and during periods of prolonged screen use at work. No generalised tonic–clonic seizures for over a year. Plan of Action: The patient describes increasing brief absence episodes over the past six weeks, with no clear illness, sleep deprivation, or missed doses identified. They feel work-related visual strain and stress may be contributory. Given the pattern in generalised epilepsy, I recommend a cautious optimisation of lamotrigine while maintaining sodium valproate.…

### Three outputs

| Method | Answer | Evidence used | Purist |
| --- | --- | --- | --- |
| Rules | `no seizure frequency reference` | “Epilepsy Centre Neurosciences Division From: Dr Priya Shah (KING'S COLLEGE HOSPITAL NHS FOUNDATION TRUST) Sent: 27 June 2019 11:20 To: epilepsy.clinic@nhs.net Cc: Dr Michael Turner (KING'S COLLEGE HOSPITAL NHS FOUNDATIO…” | correct |
| LLM | `unknown` | “Patient reports frequent petit mal recently, particularly on waking and during periods of prolonged screen use at work.” | correct |
| LLM with rules | `multiple per day` | “Patient reports frequent petit mal recently” | correct |

What this case makes visible: the methods can read the same source text and still differ in selection, representation, or canonical rendering.

## `no_reference_sentinel`

The note has no usable seizure-frequency reference.

**Development row:** `11409`  
**Gold:** `no seizure frequency reference`

### Source excerpt

> KINGS NEUROSCIENCES CENTRE Clinic Date: 04 August 2019 Dr Kate Health Centre Keele University, Keele, Newcastle Staffordshire ST5 5BG Dear Dr Kate Wendy Brown, DOB: 21-11-1982, Hospital No: K482715 NHS No. 6592841037 Flat 7 Brookside Avenue, Newcastle-under-Lyme, ST5 2QD Summary: Follow-up booking request to review symptom patterns associated with sleep loss and to align care with the patient’s personalised plan (documented elsewhere). Background: The patient reports occasional cluster patterns linked to sleep loss. A personalised plan is already in place and referenced in the record. Request: Please arrange a routine follow-up appointment in the neurology clinic within 8–10 weeks, sooner if the patient or primary care has concerns. At review, we will: - Reassess sleep hygiene and triggers - Check adherence and tolerability of current management - Confirm alignment with the personalised plan and update as needed Interim advice:…

### Three outputs

| Method | Answer | Evidence used | Purist |
| --- | --- | --- | --- |
| Rules | `no seizure frequency reference` | “KINGS NEUROSCIENCES CENTRE Clinic Date: 04 August 2019 Dr Kate Health Centre Keele University, Keele, Newcastle Staffordshire ST5 5BG Dear Dr Kate Wendy Brown, DOB: 21-11-1982, Hospital No: K482715 NHS No.” | correct |
| LLM | `unknown` | “The patient reports occasional cluster patterns linked to sleep loss.” | correct |
| LLM with rules | `unknown` | “The patient reports occasional cluster patterns linked to sleep loss.” | correct |

What this case makes visible: the methods can read the same source text and still differ in selection, representation, or canonical rendering.

## `unresolved_multiple`

The note says multiple, without a count that should be invented.

**Development row:** `14282`  
**Gold:** `multiple per month`

### Source excerpt

> …rearms following two unwitnessed collapses on stairs and when exiting public transport. He has not required emergency treatment, but these occurrences have increased his and his partner’s anxiety regarding safety and supervision. Medication and recent course: He came off Levetiracetam on 10 December. In the following week, he had several seizures, one associated with sleep deprivation. No further seizures have occurred since. He reports that sleep quality has been variable and that he occasionally misses meals when working late. No other anti-seizure medicines are currently prescribed, and there have been no recent intercurrent illnesses. He is using a smartphone seizure diary, which corroborates the timing of the early post-withdrawal events and the subsequent seizure-free interval. Examination today was unremarkable with normal cardior…

### Three outputs

| Method | Answer | Evidence used | Purist |
| --- | --- | --- | --- |
| Rules | `multiple per month` | “In the following week, he had several seizures” | correct |
| LLM | `multiple per week` | “In the following week, he had several seizures, one associated with sleep deprivation. No further seizures have occurred since.” | correct |
| LLM with rules | `multiple per 3 week` | “No further seizures have occurred since.” | correct |

What this case makes visible: the methods can read the same source text and still differ in selection, representation, or canonical rendering.

## Boundary

These are `dev750` examples only. The reports use real synthetic clinical letters and retained predictions, but they are explanatory slices, not holdout evidence or clinical validation. See the [category-cut performance report](../shared/six_model_category_cut_performance_2026-08-06.md) for aggregate results and the [protocol](../shared/category_cut_representative_examples_protocol_2026-08-08.md) for provenance.
