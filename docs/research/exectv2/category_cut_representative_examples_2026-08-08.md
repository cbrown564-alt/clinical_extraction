# ExECTv2 within-family category examples

Paper-library role: detailed development examples; use the [row-evidence workbook](../artifacts/paper_source_row_evidence_2026-08-10.xlsx) for filtering.

Real development examples for every observed gold-defined subtype inside Diagnosis, SeizureFrequency, Prescription, and Investigations. Whole-letter composition buckets are not the category surface.

Split: `dev140` · LLM model: `GPT-5.6 Sol` · rules baseline: regenerated deterministic four-family artifact.

## How to read the cases

Each case shows only the named clinical family. `LLM` is the saved raw model lane; `LLM with rules` is the saved post-family-rules prediction. `match` means the complete family-level headline keys equal gold on that letter; it is not a clinical-validation judgment.

## Diagnosis

### `epilepsy`

**Letter:** `EA0173`

#### Source excerpt

> Rachel Johannes DoB 13-Jul-1990 Diagnosis – Unclassified Epilepsy Treatment – Unsure of exact medications I met with Rachel and her partner in clinic recently. Rachel said that her last seizure was on the 15th April in her home. Rachel showed me her seizure chart. We discssued safety issues and Rachel takes showers not baths. We also discussed contraception. Previously she has tried the pill but this seemed to make her seizures worse. The depo injection seems to cause wright gain. We agreed that Rachel will make an appointment with yourself to discussed contraception

#### Gold Diagnosis facts

`epilepsy (DiagCategory=Epilepsy)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | Epilepsy (DiagCategory=Epilepsy) | match |
| LLM | Unclassified Epilepsy (DiagCategory=Epilepsy) | match |
| LLM with rules | epilepsy (DiagCategory=Epilepsy) | match |

### `multiple_seizures`

**Letter:** `EA0008`

#### Source excerpt

> Dear Dr, Diagnosis: symptomatic structural focal epilepsy Previous meningioma resection 3rd January 2005 Seizure type and frequency: focal seizures with altered awareness every 3 weeks Current anti-epileptic medication: lamotrigine 75mg bd (to reduce and stop as detailed below) To start levetiracetam as detailed below I reviewed this 62 year old man together with his wife in clinic today. Unfortunately after the period of seizure freedom the seizures have returned. The seizures are very stereotyped and asked similar to the events he had before surgery. He will get a warning of an unusual burning taste and then lose awareness and contact for a few minutes. His wife said that he will stare and occasionally chew his lips during these events. He feels dizzy on the lamotrigine and is keen to change his medication. I therefore suggest that he starts levetiracetam at a dose of 250mg…

#### Gold Diagnosis facts

`symptomatic-structural-focal-epilepsy (DiagCategory=Epilepsy)`; `focal-seizures-with-altered-awareness (DiagCategory=MultipleSeizures)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | symptomatic structural focal epilepsy (DiagCategory=Epilepsy)<br>focal seizures with altered awareness (DiagCategory=Epilepsy) | match |
| LLM | symptomatic structural focal epilepsy (DiagCategory=Epilepsy)<br>focal seizures with altered awareness (DiagCategory=MultipleSeizures) | match |
| LLM with rules | symptomatic structural focal epilepsy (DiagCategory=Epilepsy)<br>focal seizures with altered awareness (DiagCategory=MultipleSeizures)<br>focal seizures (DiagCategory=MultipleSeizures) | differs |

### `single_seizure`

**Letter:** `EA0009`

#### Source excerpt

> Dear Dr , I reviewed this 42-year-old woman in the clinic this morning. As you know she has experienced seizures since around 4 weeks after her operation. This was a craniotomy for her frontal lobe brain tumour. During her seizures she typically has a left-handed stiffness which progresses to her shoulder. Around 50% of the time she will then lose consciousness before going in to a bilateral convulsive seizure. Her seizure frequency does vary. Currently she get around 2-4 seizures per month. Although she did have a cluster of seizures in August, 2017 where she had 6-9 seizures every week for 3 weeks. She was born normally but did have 2 febrile seizures at the age of 2 months and 34 months. She is currently taking levetiracetam 750 mg twice a day as well as lamotrigine 100 mg twice a day. Her last MRI in January, 2018 did show frontal lobe gliosis and signs of previous craniotomy which would be consistent with her previous surgery. Given that she is having ongoing seizures I would suggest increasing the lamotrigine in the 1st instance by 25 mg every fortnight until she is on a target dose of 150 mg twice a day

#### Gold Diagnosis facts

`bilateral-convulsive-seizure (DiagCategory=SingleSeizure)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | bilateral convulsive seizure (DiagCategory=Epilepsy) | match |
| LLM | bilateral convulsive seizure (DiagCategory=SingleSeizure)<br>febrile seizures (DiagCategory=MultipleSeizures) | differs |
| LLM with rules | bilateral convulsive seizure (DiagCategory=MultipleSeizures) | match |

## SeizureFrequency

### `seizure_free`

**Letter:** `EA0061`

#### Source excerpt

> Our Ref ABC/SW/T4888786 NHS No 4221549987 Clinic Date 19/9/2017 The Epilepsy service Dear Dr r.e. Mr Owen Owens 34, Terrible Road, Nicetown. SA2 4II Diagnosis: focal epilepsy, probable parietal onset Seizure type and frequency: focal seizures with altered awareness (unusual arm sensation), last event 3 years ago focal to bilateral seizures 2 events in total, last event 10 years ago. Current anti-epileptic medication: lamtorigine 250mg bd (to reduce as detailed below) Previous medication tried include topiramate. Investigations: MRI, right parietal focal cortical dysplasia I reviewed the 36 year old salesman today in clinic. I had not met him before. He was born in Scotland and has only lived in Wales for the last two years. His previous epilepsy investigations and care has been in Scotland. His epilepsy started when he was 10 years old. He had a febrile seizure at the age of 3. He has got episodic migraine for which he take sumitryptan. There is no family history of epilepsy. He has been back driving for the last year His seizures are quite stereotyped in that he gets a strange sensation in his left arm which rises towards his face. On the two occasions he has had bigger seizures t…

#### Gold SeizureFrequency facts

`focal-seizures-with-altered-awareness (NumberOfSeizures=0, NumberOfTimePeriods=3, TimePeriod=Year)`; `focal-to-bilateral-convulsive-seizure (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Year)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | focal seizures with altered awareness (NumberOfSeizures=0, NumberOfTimePeriods=3, TimePeriod=Year)<br>focal to bilateral seizures (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Year) | match |
| LLM | focal seizures with altered awareness (NumberOfSeizures=0, NumberOfTimePeriods=3, TimePeriod=Year, TimeSince_or_TimeOfEvent=Since)<br>focal to bilateral seizures (NumberOfSeizures=2)<br>focal to bilateral seizures (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Year, TimeSince_or_TimeOfEvent=Since) | differs |
| LLM with rules | focal seizures with altered awareness (NumberOfSeizures=0, NumberOfTimePeriods=3, TimePeriod=Year, TimeSince_or_TimeOfEvent=Since)<br>seizures (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Year)<br>focal to bilateral seizures (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Year, TimeSince_or_TimeOfEvent=Since) | differs |

### `numeric_cadence_rate`

**Letter:** `EA0025`

#### Source excerpt

> Ann Richards. D.O.B. 21/04/1974 Diagnosis: generalised tonic clonic seizures with myoclonic jerks, possible JME Anti-convulsant medication: epilim 500 mg BD Lamictal 100 mg in the morning, 175 mg in the afternoon I saw Ann who was accompanied with her daughter in my nurse led clinic today. She split up from her partner last year and so underwent a lot of stress. She had approximately 3–4 generalised tonic chronic seizures per week from May to August. She also had very frequent myoclonic jerks. She also has headaches and heartburn. She probably drinks too much alcohol, having around one bottle of wine per day. I have advised her around ifestyle issues and will review her in approximately four months time.

#### Gold SeizureFrequency facts

`generalised-tonic-clonic-seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week, TimeSince_or_TimeOfEvent=During)`; `myoclonic-jerks (FrequencyChange=Frequent)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week)<br>myoclonic jerks (FrequencyChange=Frequent)<br>generalised tonic clonic seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week, TimeSince_or_TimeOfEvent=During) | differs |
| LLM | seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week) | differs |
| LLM with rules | generalised tonic clonic seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week) | differs |

### `count_in_named_window`

**Letter:** `EA0186`

#### Source excerpt

> Clinic date 25/09/2018 Re Mr Owen Owens 30/06/1968 Dear doctor, Diagnosis: Symptomatic structural focal epilepsy Area of ischaemic damage left inferior frontal lobe Significant anxiety and depression I reviewed this 50 year old man, together with his wife, in clinic today. He was well from an epilepsy point of view until he had a seizure last month. His wife heard a bang from the next room and went in to see him unconsciouss on the floor. He was stiff, his eyes were open and he made unusual groaning noises before starting to shake. This lasted about 40 seconds before he went to a “deep sleep”. It took him several hours to recover fully. Mr Owens himself remembers his right leg twitching before he lost consciousness. I think therefore that this was a focal to bilateral convulsive seizures. As you recall Mr Owens has had focal motor seizures in the past where he has had jerking of his right leg. These were happening frequently before he started the medication. The last event was probably 10 months ago. He has had one previous focal to bilateral convulsive seizure at the time of diagnosis of his epilepsy in May 2017. As you will recall his MRI at the time was abnormal with an area of…

#### Gold SeizureFrequency facts

`focal-to-bilateral-convulsive-seizure (NumberOfSeizures=1, TimeSince_or_TimeOfEvent=During, YearDate=2017, MonthDate=5)`; `seizure (NumberOfSeizures=1, PointInTime=Last_Month, TimeSince_or_TimeOfEvent=During)`; `focal (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Month)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | seizure (NumberOfSeizures=1, PointInTime=Last_Month, TimeSince_or_TimeOfEvent=During)<br>focal to bilateral convulsive seizure (NumberOfSeizures=1, TimeSince_or_TimeOfEvent=During, YearDate=2017, MonthDate=5)<br>focal (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Month) | differs |
| LLM | seizure (NumberOfSeizures=1, PointInTime=Last_Month, TimeSince_or_TimeOfEvent=During)<br>focal motor seizures (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Month, TimeSince_or_TimeOfEvent=Since) | differs |
| LLM with rules | focal motor seizures (NumberOfSeizures=0, NumberOfTimePeriods=10, TimePeriod=Month, TimeSince_or_TimeOfEvent=Since) | differs |

### `qualitative_frequency_change`

**Letter:** `EA0025`

#### Source excerpt

> Ann Richards. D.O.B. 21/04/1974 Diagnosis: generalised tonic clonic seizures with myoclonic jerks, possible JME Anti-convulsant medication: epilim 500 mg BD Lamictal 100 mg in the morning, 175 mg in the afternoon I saw Ann who was accompanied with her daughter in my nurse led clinic today. She split up from her partner last year and so underwent a lot of stress. She had approximately 3–4 generalised tonic chronic seizures per week from May to August. She also had very frequent myoclonic jerks. She also has headaches and heartburn. She probably drinks too much alcohol, having around one bottle of wine per day. I have advised her around ifestyle issues and will review her in approximately four months time.

#### Gold SeizureFrequency facts

`generalised-tonic-clonic-seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week, TimeSince_or_TimeOfEvent=During)`; `myoclonic-jerks (FrequencyChange=Frequent)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week)<br>myoclonic jerks (FrequencyChange=Frequent)<br>generalised tonic clonic seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week, TimeSince_or_TimeOfEvent=During) | differs |
| LLM | seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week) | differs |
| LLM with rules | generalised tonic clonic seizures (LowerNumberOfSeizures=3, UpperNumberOfSeizures=4, NumberOfTimePeriods=1, TimePeriod=Week) | differs |

## Prescription

### `complete_regimen`

**Letter:** `EA0093`

#### Source excerpt

> Clinic date: 3rd April 2016 Typed: 5th April 2016 Dear Dr Pooled Re: Miss Lucy Williams D.O.B: 25/02/2007 NHS 123 123 5445 Diagnosis: Primary generalised epilepsy Medication: Levetiracetam ?dose Valproate as Episenta 500mg nocte to withdraw by 100mg increments every week starting next school holidays Follow up: 6 months I reviewed this young lady in the clinic today. She has been very well and has had no seizures since Christmas 2015. She is doing very well in Year 5 at School. She has no side effects from her current medication. Mother felt that as her medication was being withdrawn, she became very tearful but this has settled down. Lucy today, was wary of reducing her medication further but we have persuaded her to do this slowly over the summer holidays. I have asked out epilepsy nurse to clarify with you the actual dose of Levetiracetam that she is taking as mother was not entirely clear. Yours sincerely

#### Gold Prescription facts

`-Episenta-500mg (DrugName=SodiumValproate, DrugDose=500, DoseUnit=mg, Frequency=1)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | Episenta 500mg nocte to withdraw by (DrugName=sodium-valproate, DrugDose=500, DoseUnit=mg, Frequency=1) | match |
| LLM | Levetiracetam (DrugName=levetiracetam)<br>Valproate as Episenta 500mg nocte (DrugName=episenta, DrugDose=500, DoseUnit=mg, Frequency=1) | match |
| LLM with rules | Levetiracetam (DrugName=levetiracetam)<br>Valproate as Episenta 500mg nocte (DrugName=sodium-valproate, DrugDose=500, DoseUnit=mg, Frequency=1) | match |

### `rescue_as_required`

**Letter:** `EA0152`

#### Source excerpt

> Clinic date 19/4/2009 Re: Miss Rachel Stewart D.O.B: 22/04/1979 Diagnosis: Symptomatic structural epilepsy Focal cortical dysplasia right temporal lobe Seizure type and frequency: Complex partial seizures (deja-vu, automatism) 1-2 per month Secondary generalised seizures 3-4 per year anti-epileptic medication: Carbamazapine 400mg bd Clobazam 10-20mg bd for seizure clusters Previous medications tried: Lamotrigine (rash) Investigations: MRI 14/3/2006 right temporal lobe focal cortical dysplasia EEG sharp waves, right temporal lobe I reviewed this 40 year old woman in clinic today. As you know she was diagnosed with epilepsy at the age of 22 after having 2 secondary generalised seizures in 2 days. She gets a difficult to describe feeling of deja-vu before her bigger seizures. She gets the same feeling before her smaller complex partial seizures and sometimes she might smack her lips. She is considering having another baby and we went through risks and benefits of epilepsy medication in pregnancy. I explained that it is a balance between the risks of seizures and risks of medication to the unborn baby. Carbama…

#### Gold Prescription facts

`Carbmazapine- (DrugName=Carbamazepine, DrugDose=400, DoseUnit=mg, Frequency=2)`; `Clobazam- (DrugName=Clobazam, Frequency=As_Required)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | Carbamazapine 400mg bd (DrugName=carbamazepine, DrugDose=400, DoseUnit=mg, Frequency=2)<br>Clobazam (DrugName=clobazam, Frequency=As_Required) | match |
| LLM | Carbamazapine 400mg bd (DrugName=carbamazapine, DrugDose=400, DoseUnit=mg, Frequency=2)<br>Clobazam 10-20mg bd for seizure clusters (DrugName=clobazam, DrugDose=10-20, DoseUnit=mg, Frequency=2) | differs |
| LLM with rules | Carbamazapine 400mg bd (DrugName=carbamazepine, DrugDose=400, DoseUnit=mg, Frequency=2)<br>Clobazam 10-20mg bd for seizure clusters (DrugName=clobazam, DrugDose=10-20, DoseUnit=mg, Frequency=As_Required) | match |

## Investigations

### `eeg_normal`

**Letter:** `EA0119`

#### Source excerpt

> Dear Dr, Re: Ms Hannah Collins DOB 3/4/1972 Diagnosis: focal epilepsy Seizure type and frequency: 1 seizure per week to 1 seizure every month Focal seizures with altered awareness Current anti epileptic medication: Levetiracetam 1500 milligrammes BD Lamotrigine 75MG BD (to increase as detailed below) Other medication includes: olanzapine, diazepam and pregabalin. I reviewed this 48 year old woman in clinic today. I have previously spoken to her on the telephone. Adding the lamotrigine didn't really seem to helpful. She still seems to be getting fairly frequent seizures. She lives alone and so her seizures haven't been witnessed for some time. She thinks she has had this seizure when she in ”loses time”. She doesn't really get any warning before hand. She has had a normal MRI and a normal eeg since her last appointment. As she is still having fairly frequent seizures I think it would be reasonable to increase her lamotragine in steps of 25 milligrammes every two weeks until she is on a dose of 150 milligrammes twice a day. We will continue to follow her by phone consultation however it would be important for her to contact the epilepsy helpline on the number above should there be an…

#### Gold Investigations facts

`normal-MRI (MRI_Performed=Yes, MRI_Results=Normal)`; `normal-eeg (EEG_Performed=Yes, EEG_Results=Normal)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | MRI (MRI_Performed=Yes, MRI_Results=Normal)<br>EEG (EEG_Performed=Yes, EEG_Results=Normal) | match |
| LLM | MRI (MRI_Performed=Yes, MRI_Results=Normal)<br>eeg (EEG_Performed=Yes, EEG_Results=Normal) | match |
| LLM with rules | MRI (MRI_Performed=Yes, MRI_Results=Normal)<br>eeg (EEG_Performed=Yes, EEG_Results=Normal) | match |

### `eeg_abnormal`

**Letter:** `EA0131`

#### Source excerpt

> Clinic Date 2/09/2015 Dear Dr, Re: Ms Julie Johilst 31/07/1988 It was nice to meet this 27 year-old woman in clinic again. She has a primary generalised epilepsy with frequent EEG abnormalities. Previous MRI scans in June 2008 and Novemeber 2010 have been normal. Her epilepsy was not well controlled on carbamazepine monotherapy. However switching to sodium valproate at 400mg twice a day has made a big difference. Unfortunately seizures have been worse in the last year. She is having quite a number of generalised tonic clonic seizures which her partner described to me today. I think the only option here really is to increase the sodium valproate. We did discuss the risks of sodium valproate in pregnancy and in child development and Ms Johilst is well aware of the risks. Howevere this has to be balanced against the risks of frequent convulsive seizures which do carry the risk of serious injury and death.

#### Gold Investigations facts

`EEG-abnormalities (EEG_Performed=Yes, EEG_Results=Abnormal)`; `MRI- (MRI_Performed=Yes, MRI_Results=Normal)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | EEG (EEG_Performed=Yes, EEG_Results=Abnormal)<br>MRI (MRI_Performed=Yes, MRI_Results=Normal) | match |
| LLM | EEG (EEG_Performed=Yes, EEG_Results=Abnormal)<br>MRI scan (MRI_Performed=Yes, MRI_Results=Normal) | match |
| LLM with rules | EEG (EEG_Performed=Yes, EEG_Results=Abnormal)<br>MRI scan (MRI_Performed=Yes, MRI_Results=Normal) | match |

### `eeg_unknown_or_unstated`

**Letter:** `EA0179`

#### Source excerpt

> Diagnosis: Episodes of loss of consciousness ?syncope ? complex partial seizures Thanks for referring this gentleman to the epilepsy clinic. He has mild learning disabilities. As a child he had seizures and was on medication between the ages of 5 and 10. He had two febrile convulsions at the age of around 3. There is no relevant family history. He describes a typical episode of loss of consciousness where he will start feeling tired and had an unusual headache. He then will not be able to answer questions and will go pale and sweaty before loosing consciousness. He had an MRI scan around 5 years ago which was normal although I have not seen the report. I do not have the results of his recent EEG test. His neurological examination was normal today and he does not have any other medical problems. Comments: I dont have a definite conclusion as to the cause of his episodes of loss of consciousness. I thought today that the episodes sounded more like syncope however he does have learning disabilities and has previously had seizures and so epilepsy needs to be borne in mind. He has already been started on sodium valproate 300mg bd which has stopped the episodes. I will review cardiology…

#### Gold Investigations facts

`EEG- (EEG_Performed=Yes, EEG_Results=Unknown)`; `MRI (MRI_Performed=Yes, MRI_Results=Normal)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | MRI (MRI_Performed=Yes, MRI_Results=Unknown)<br>EEG (EEG_Performed=Yes, EEG_Results=Unknown)<br>EEG (EEG_Performed=Yes) | differs |
| LLM | MRI scan (MRI_Performed=Yes, MRI_Results=Normal)<br>EEG (EEG_Performed=Yes, EEG_Results=Unknown) | differs |
| LLM with rules | MRI scan (MRI_Performed=Yes, MRI_Results=Normal)<br>EEG (EEG_Performed=Yes, EEG_Results=Unknown) | differs |

### `mri_normal`

**Letter:** `EA0119`

#### Source excerpt

> Dear Dr, Re: Ms Hannah Collins DOB 3/4/1972 Diagnosis: focal epilepsy Seizure type and frequency: 1 seizure per week to 1 seizure every month Focal seizures with altered awareness Current anti epileptic medication: Levetiracetam 1500 milligrammes BD Lamotrigine 75MG BD (to increase as detailed below) Other medication includes: olanzapine, diazepam and pregabalin. I reviewed this 48 year old woman in clinic today. I have previously spoken to her on the telephone. Adding the lamotrigine didn't really seem to helpful. She still seems to be getting fairly frequent seizures. She lives alone and so her seizures haven't been witnessed for some time. She thinks she has had this seizure when she in ”loses time”. She doesn't really get any warning before hand. She has had a normal MRI and a normal eeg since her last appointment. As she is still having fairly frequent seizures I think it would be reasonable to increase her lamotragine in steps of 25 milligrammes every two weeks until she is on a dose of 150 milligrammes twice a day. We will continue to follow her by phone consultation however it would be important for her to contact the epilepsy helpline on the number above should there be an…

#### Gold Investigations facts

`normal-MRI (MRI_Performed=Yes, MRI_Results=Normal)`; `normal-eeg (EEG_Performed=Yes, EEG_Results=Normal)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | MRI (MRI_Performed=Yes, MRI_Results=Normal)<br>EEG (EEG_Performed=Yes, EEG_Results=Normal) | match |
| LLM | MRI (MRI_Performed=Yes, MRI_Results=Normal)<br>eeg (EEG_Performed=Yes, EEG_Results=Normal) | match |
| LLM with rules | MRI (MRI_Performed=Yes, MRI_Results=Normal)<br>eeg (EEG_Performed=Yes, EEG_Results=Normal) | match |

### `mri_abnormal`

**Letter:** `EA0126`

#### Source excerpt

> Dear Dr, Re: Mr James Joyce DOB 17/11/1979 Diagnosis: Focal epilepsy secondary to Tuberous sclerosis Medication: Sodium valproate 500mg bd Eslicarbazepine 800mg od Previous medications tried include levetiracetam and carbazmazepine I revealed Mr Joyce for the first time today. He came to clinic with his sister.As you know she he has a diagnosis of tuberous sclerosis stop his epilepsy was first diagnosed at the age of 6. He is reasonably stable from it too brisk rossis pov. His last MRI scan was around 10 years ago and was abnormal showing Sam tuber's in the frontal and temporal loops. Mr Joyce has different types of seizures. Focal frontal lobe seizures consist of stiffening with posturing of an arm lasting around a minute. These currently occur around 4-5 times a month. He also gets focal to bilateral convulsive seizures and these haven't happened for several years now. As a child he also had drop attacks but they haven't happened in adulthood. James has been on the current combination of medication for some time and he seems to be tolerating them well. In the past he's tried levetiracetam and carbamazepine and it sounds like the levetiracetam may have caused mood disturbances. I…

#### Gold Investigations facts

`MRI-scan (MRI_Performed=Yes, MRI_Results=Abnormal)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | MRI (MRI_Performed=Yes, MRI_Results=Abnormal) | match |
| LLM | MRI scan (MRI_Performed=Yes, MRI_Results=Abnormal) | match |
| LLM with rules | MRI scan (MRI_Performed=Yes, MRI_Results=Abnormal) | match |

### `ct_normal`

**Letter:** `EA0073`

#### Source excerpt

> The epilepsy serivce Our Ref: M768493 NHS No: 495 562 1252 Date: 18/10/2019 Clinic Date 12/10/2019 Dear Dr r.e. Georgina Jones D.O.B: 11/02/1945 Hafan, 38 Port Street, Bridestart, Llanelli SA43 9EB Mrs Jones was reviewed in the Neurology first fit clinic today via telephone consultation. She was referred from the A&E department in Morriston Hospital, following a recent episode of collapse. She is a 74-year-old female with a background of ischaemic heart disease, hypertension, and diabetes. Her current medication includes clopidogrel 75mg OD, Ramipril 2.5mg OD, and metformin 500mg BD. Mrs Jones lives alone and is normally very active. She continues to drive and is independent of activities of daily living. She is an ex-smoker and does not drink any alcohol. We discussed the collapse episode which occurred 6 weeks prior to this review. Whilst sitting in a chair at home, Mrs Jones suddenly felt her heart racing and had some mild central chest pain. She next recalls waking up on the floor with her daughter kneeling next to her. Whilst on the floor she was witnessed to have mild jerking of her limbs for a few seconds. On regaining consciousness, she was orientated to time and place, wit…

#### Gold Investigations facts

`CT (CT_Performed=Yes, CT_Results=Normal)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | CT (CT_Performed=Yes) | differs |
| LLM | CT (CT_Performed=Yes, CT_Results=Normal) | match |
| LLM with rules | CT (CT_Performed=Yes, CT_Results=Normal) | match |

### `ct_abnormal`

**Letter:** `EA0169`

#### Source excerpt

> Dear Dr Pooled Re: Ms Haana Habley D.O.B 30/01/1972 I reviewed this 41 year old lady with symptomatic epilepsy due to previous neurocysticercosis. She gets frequent focal dyscognitive seizures in clusters. Last week she had around 10-15 of these seizures over 2 days. There was no obvious provoking factor. As you know she had an abnormal CT scan in 2000 which showed calcifications consistent with her neurocysticercosis. A recent MRI in 2011 was normal. She has previously tried levetiracetam but it caused mood disturbance and is now taking lamotrigine 150mg bd. We discussed various treatment options. Mrs Habley does not want any further children and this will leave more options in terms of drug treatment. We decided to try and increase in the lamotrigine in the first instance. Please increase by 25mg every fortnight until she is taking 200mg bd. If this increase is not successful then I would suggest introducing zonisamide 25mg od increasing by 25mg every fortnight to a ta…

#### Gold Investigations facts

`CT (CT_Performed=Yes, CT_Results=Abnormal)`; `MRI (MRI_Performed=Yes, MRI_Results=Normal)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | CT (CT_Performed=Yes, CT_Results=Abnormal)<br>MRI (MRI_Performed=Yes, MRI_Results=Normal) | match |
| LLM | CT scan (CT_Performed=Yes, CT_Results=Abnormal)<br>MRI (MRI_Performed=Yes, MRI_Results=Normal) | match |
| LLM with rules | CT scan (CT_Performed=Yes, CT_Results=Abnormal)<br>MRI (MRI_Performed=Yes, MRI_Results=Normal) | match |

### `ct_unknown_or_unstated`

**Letter:** `EA0062`

#### Source excerpt

> Our Ref ABC/SW/T4888786 NHS No 4221549987 Clinic Date 2/4/2014 The Epilepsy service Dear Dr r.e. Ms Lydia Lavender Flat 2, Heol y Blodau, Treneis. SA12 8RH I reviewed the 28-year-old woman in clinic today, she came alone. She has had several episodes over the last two years, perhaps six in total. I phoned her sister who has witnessed several of these episodes, they have occured when she has been awake and when she has been asleep. Her eyes stay open and she will go stiff during them. Sometimes her muscles will ache for days afterwards. She has not had any episodes of myoclonus and photsensitivity doesnt seem to be an issue for her She used to live in London and may have had a few seizures when she was younger but cant remember much about this. She thinks that she was born normally and there is no history of meningitis or significant head injury. She has moderate asthma for which she takes inhalers. She works part time in a bar at the moment and lives with her sister. She had a CT head in 2013 and an ECG in clinic today shows a sinus rhythm of 72 bpm, a normal QT interval and normal QRS morphology. Impression. I think that the most likely diagnosis is epilepsy. Comments. I explained…

#### Gold Investigations facts

`CT (CT_Performed=Yes, CT_Results=Unknown)`

#### Three outputs

| Method | Family output | Family match |
| --- | --- | --- |
| Rules | CT (CT_Performed=Yes, CT_Results=Normal)<br>MRI (MRI_Performed=Yes) | differs |
| LLM | CT (CT_Performed=Yes, CT_Results=Unknown) | match |
| LLM with rules | CT (CT_Performed=Yes, CT_Results=Unknown) | match |

## Boundary

These are `dev140` examples only. The reports use real annotated letters and retained predictions, but they are explanatory slices, not holdout evidence or clinical validation. See the [category-cut performance report](../shared/six_model_category_cut_performance_2026-08-06.md) for aggregate results and the [protocol](../shared/category_cut_representative_examples_protocol_2026-08-08.md) for provenance.
