# Evidence support-quality companion audit (dev140) — closes FM1's "Partial" guardrail

Run: `exectv2_holistic_finding_assembly_v08_full200_currentcode_gpt41mini_20260624` (v08 hybrid, full-200 production system, filtered to dev140).
Model: `openai/gpt-4.1-mini`. Support-judge sample: 5 grounded mentions per family (seed 20260630).

Distinct from `evidence_validity_audit.py`'s **groundedness** rate (is the evidence string locatable in the note text). This measures **support**: does the evidence text justify the *specific* claimed value/attributes, not merely sit nearby. Per FM1 (the predecessor h005 null result), these must never be conflated.

## Groundedness baseline (zero-LLM, full dev140, all mentions)

| family | n_mentions | n_grounded | groundedness_rate |
| --- | ---: | ---: | ---: |
| Diagnosis | 409 | 409 | 1.0 |
| SeizureFrequency | 276 | 276 | 1.0 |
| Prescription | 201 | 201 | 1.0 |
| Investigations | 129 | 129 | 1.0 |

## Support-quality sample (LLM-judge, grounded mentions only)

| family | n_sampled | SUPPORTS | PARTIALLY | NONE | strict rate | lenient rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 5 | 4 | 1 | 0 | 0.8 | 1.0 |
| SeizureFrequency | 5 | 3 | 1 | 1 | 0.6 | 0.8 |
| Prescription | 5 | 5 | 0 | 0 | 1.0 | 1.0 |
| Investigations | 5 | 5 | 0 | 0 | 1.0 | 1.0 |

## Sample detail

### Diagnosis
- `EA0108` claimed=`tonic clonic seizures` evidence=`There is usually a warning in the form of twitching in his left hand and then the episode progresses to a tonic clonic convulsion.` -> **SUPPORTS** — The evidence explicitly states that the seizure episode progresses to a tonic clonic convulsion, directly supporting the claim of tonic clonic seizures.
- `EA0124` claimed=`tonic clonic seizures` evidence=`generalised tonic clonic seizures` -> **SUPPORTS** — The evidence explicitly states "generalised tonic clonic seizures," which directly supports the claimed text "tonic clonic seizures" with affirmed certainty.
- `EA0113` claimed=`juvenile myoclonic epilepsy` evidence=`Diagnosis: Juvenile myoclonic epilepsy` -> **SUPPORTS** — The evidence explicitly states "Diagnosis: Juvenile myoclonic epilepsy," directly affirming the claimed diagnosis with certainty.
- `EA0109` claimed=`temporal lobe seizures` evidence=`Diagnosis:  Focal Seizures, probably temporal lobe.` -> **PARTIALLY_SUPPORTS** — The evidence states "Focal Seizures, probably temporal lobe," indicating a probable but not definitive diagnosis, which partially supports the claim of "temporal lobe seizures" with affirmed certainty.
- `EA0009` claimed=`epilepsy` evidence=`she has experienced seizures since around 4 weeks after her operation` -> **SUPPORTS** — The evidence that the patient has experienced seizures since around 4 weeks after her operation supports the diagnosis of epilepsy, as seizures are a defining feature of epilepsy.

### SeizureFrequency
- `EA0119` claimed=`seizures` evidence=`Seizure type and frequency: 1 seizure per week to 1 seizure every month` -> **PARTIALLY_SUPPORTS** — The evidence states the seizure frequency ranges from 1 seizure per week to 1 seizure every month, but the claimed attributes specify a range of 1 to 4 seizures per week, which is not fully supported by the evidence.
- `EA0019` claimed=`generalised tonic clonic seizure` evidence=`generalised tonic clonic seizure` -> **SUPPORTS** — The evidence phrase "generalised tonic clonic seizure" directly matches the claimed text and confirms the occurrence of one such seizure last week.
- `EA0050` claimed=`seizure clusters` evidence=`He can have 10 to 20 mg at night for up to 5 days for seizure clusters.` -> **DOES_NOT_SUPPORT** — The evidence mentions treatment for seizure clusters lasting up to 5 days but does not specify the number of seizures as 1 within that time period.
- `EA0011` claimed=`focal to bilateral convulsive seizures` evidence=`focal to bilateral convulsive seizures` -> **SUPPORTS** — The evidence text explicitly states "focal to bilateral convulsive seizures," directly supporting the claimed seizure type.
- `EA0131` claimed=`seizures` evidence=`Unfortunately seizures have been worse in the last year.` -> **SUPPORTS** — The evidence explicitly states that seizures have been worse in the last year, directly supporting the claim of increased seizure frequency during that time.

### Prescription
- `EA0102` claimed=`Eplim 200mg twice a day` evidence=`Eplim 200mg twice a day` -> **SUPPORTS** — The evidence text explicitly states "Eplim 200mg twice a day," which directly matches the claimed prescription details.
- `EA0049` claimed=`Sodium valproate 700 mg BD` evidence=`Sodium valproate 700 mg BD` -> **SUPPORTS** — The evidence text explicitly states "Sodium valproate 700 mg BD," which matches the claimed drug name, dose, and frequency exactly.
- `EA0172` claimed=`Lamotrigine 200mg bd` evidence=`Lamotrigine 200mg bd` -> **SUPPORTS** — The evidence text explicitly states "Lamotrigine 200mg bd," which directly matches the claimed drug name, dose, and frequency.
- `EA0044` claimed=`lamotrigine 75mg twice a day` evidence=`lamotrigine 75mg twice a day` -> **SUPPORTS** — The evidence text explicitly states the prescription as "lamotrigine 75mg twice a day," which exactly matches the claimed text and attributes.
- `EA0007` claimed=`levetiracetam 750mg mane` evidence=`levetiracetam 750mg mane, 500 mg nocte` -> **SUPPORTS** — The evidence explicitly states "levetiracetam 750mg mane," which matches the claimed drug name, dose, and frequency.

### Investigations
- `EA0076` claimed=`EEG` evidence=`and his EEG was normal although it didn't capture any events.` -> **SUPPORTS** — The evidence explicitly states that an EEG was performed and the result was normal, directly supporting the claimed attributes.
- `EA0146` claimed=`EEG` evidence=`A recent MRI and EEG in 2018 have been normal.` -> **SUPPORTS** — The evidence explicitly states that an EEG was performed in 2018 and the results were normal, directly supporting the claimed attributes.
- `EA0186` claimed=`MRI` evidence=`As you will recall his MRI at the time was abnormal with an area of ischaemic damage in the left inferior frontal lobe.` -> **SUPPORTS** — The evidence explicitly states that the MRI was performed and was abnormal, showing an area of ischaemic damage in the left inferior frontal lobe, directly supporting the claimed attributes.
- `EA0021` claimed=`EEG` evidence=`His EEG in 2010 was abnormal, with sharp wave activity in the left anterior region.` -> **SUPPORTS** — The evidence explicitly states that the EEG was performed in 2010 and was abnormal, matching the claimed attributes.
- `EA0142` claimed=`An EEG from November last year did show bilateral temporal spike (right more than left).` evidence=`An EEG from November last year did show bilateral temporal spike (right more than left).` -> **SUPPORTS** — The evidence explicitly states that the EEG from November showed bilateral temporal spikes, confirming the EEG was performed and abnormal as claimed.

## Caveats

- Sample size is small (5/family, 20 total) — a bounded spot-check per the predeclared contract, not a precise rate; read as a signal, not a decimal.
- Sampled only from mentions already flagged `evidence_valid` by the production pipeline (groundedness is a precondition for support; ungrounded evidence cannot support anything by construction).
- The judge model (gpt-4.1-mini) is the same family as the production extractor; an independent judge model would be a stronger design for a future, larger-scale version of this audit.