# Descriptive clinical-inventory feasibility on Gan `dev750`

Date: 2026-08-28
Status: completed; development descriptive evidence only
Protocol: [gan inventory feasibility protocol](gan_inventory_feasibility_dev750_n100_protocol_2026-08-28.md)
Decision: [Gan is the dissertation paper](../../paper/decisions/gan-is-the-dissertation-paper.md)
Artifact: `experiments/gan_inventory_feasibility_dev750_n100_20260828/`

## Question

Can the frozen ExECT-style four-family inventory program produce
structured descriptions of diagnoses, medicines, investigations, and
seizure-frequency statements from Gan synthetic letters?

## Protocol

- Dataset: Gan 2026 synthetic letters.
- Split: paper `dev750` / machine `validation`. `test450` was not loaded.
- Sample: `gan_inventory_feasibility_dev750_n100_v1`;
  `random.Random(20260828).sample` of 100 indices from the sorted
  validation pool. Processing order was the selected indices sorted
  ascending.
- Program: `run_letter` →
  `run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)`. No LLM. No
  scorer. Counts use select-stop four-family mentions only.
- Tree: commit `baf4aed4`, dirty working tree at run time.

## Answer

Yes, as a descriptive output. On this 100-letter sample the frozen
program emitted at least one four-family fact in **97** letters
(**483** facts; median **5** per letter, range **0–11**). Medicines and
diagnoses were the most often filled families. Investigations and
seizure-frequency statements appeared in half or fewer of the letters.

This is output volume and structure. It is not accuracy.

## Family summaries

| Family | Letters with ≥1 fact | Total facts | Median (range) per letter | Common subtypes |
| --- | ---: | ---: | --- | --- |
| Diagnosis | 76 | 130 | 1 (0–4) | Epilepsy (130) |
| Prescription | 81 | 204 | 2 (0–9) | levetiracetam (72), lamotrigine (63), sodium-valproate (23), clobazam (13), topiramate (10) |
| Investigations | 40 | 68 | 0 (0–3) | MRI:Normal (32), EEG:Abnormal (19), EEG:Normal (14), MRI:Abnormal (3) |
| SeizureFrequency | 50 | 81 | 0.5 (0–4) | seizures (14), seizure (11), Increased (8), Infrequent (6), Frequent (5) |
| Any family | 97 | 483 | 5 (0–11) | — |

Diagnosis subtypes collapse to `DiagCategory`, which is almost always
`Epilepsy` on this program. That is the protocol’s declared label, not
a claim that every diagnosis mention is the same clinical concept.
Prescription subtypes are drug names. Investigation subtypes are
modality-plus-result. Seizure-frequency subtypes often fall back to
generic `CUIPhrase` anchors (`seizure` / `seizures`) when
`FrequencyChange` is absent.

## Illustration letters

Chosen by the predeclared rule (most families, then fact count, then
lowest `source_row_index`): **2748**, **5551**, **2759**. Synthetic
development letters only. Inventories are extracted output, not gold.

**2748.** Neurology clinic letter: focal epilepsy with impaired-awareness
seizures, unremarkable MRI, left-temporal EEG sharp waves, levetiracetam
and lacosamide.

- Diagnosis: Focal epilepsy; focal seizure (both `DiagCategory=Epilepsy`)
- Prescription: levetiracetam; lacosamide (each repeated from later
  mention of the same regimen)
- Investigations: MRI:Normal; EEG:Abnormal
- SeizureFrequency: Decreased; focal seizure (1 / month); Increased

**5551.** Combined generalised and focal epilepsy; levetiracetam and
clobazam rescue; normal MRI; EEG with generalised and focal discharges.

- Diagnosis: Epilepsy; Focal Epilepsy; focal seizures; generalised
  seizures
- Prescription: levetiracetam; clobazam (each repeated)
- Investigations: MRI:Normal; EEG:Abnormal
- SeizureFrequency: Infrequent (`clonic seizures`)

**2759.** Recurrent seizures of uncertain classification; historical
normal imaging/EEG; lamotrigine split dosing.

- Diagnosis: secondary generalisation
- Prescription: lamotrigine (four mentions from one split-dose sentence)
- Investigations: EEG:Normal; MRI:Normal; EEG:Normal
- SeizureFrequency: simple partial seizure (1 / month); seizures
  (1 / day)

The illustrations show multi-fact inventories and also repeated or
coarse mentions. That is part of the descriptive result.

## Attribution

All counts come from the frozen rules-only three-stage program on
wrapped Gan notes. No model call. No inventory gold. No comparison to
Gan Purist labels.

## Claim boundary

Development descriptive evidence only.

The study may say that the frozen inventory schema produced the table
above on 100 Gan `dev750` synthetic letters.

It may not say those facts are precise, complete, or clinically valid.
It may not cite ExECT `test60` scores. It may not treat this sample as
a Gan classification result.

## Decision and next

Stop. Do not retune from these letters. Do not redraw the sample.
The compact table and three illustrations are now in
[paper results §G](../../paper/sections/results.md).
