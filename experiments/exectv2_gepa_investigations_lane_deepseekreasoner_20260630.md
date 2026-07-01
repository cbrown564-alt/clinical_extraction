# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_investigations_lane_deepseekreasoner_20260630

Date: 2026-06-30

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `deepseek/deepseek-reasoner` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 2000 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 1904 tokens** (seed was 625 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.625** (P=0.538 R=0.746, Diagnosis=concept_negation)
  - Diagnosis=0.448  SeizureFrequency=0.449  Prescription=0.886  Investigations=0.925
- **Producer evidence-recall (source_near): 0.671** (GEPA per-family baseline 0.694, v08 hybrid 0.883) — Dx=0.412 SF=0.786 Rx=0.898 Inv=0.941
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.122
- Semantic (CUI-dropped) per-item F1: 0.131
- Letters: 140 (unscorable: 0); facts emitted 1377, scored 1054

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
=== diagnosis ===
You read one clinical letter and list its distinct diagnosis facts.

Emit every distinct diagnosis or syndrome concept once (epilepsy type and any
comorbid conditions), with negation=affirmed, or negated if the diagnosis is
explicitly excluded (a negated diagnosis is still a fact). Ground each by an
exact substring of the letter as evidence. Return exactly one JSON object
matching output_schema with a 'clinical_facts' list, no markdown.

=== seizure_frequency ===
You read one clinical letter and list its seizure-frequency facts.

Emit one fact per distinct seizure type (use the named type, or 'seizures' if
generic) with a coarse state: active_rate, seizure_free, changed, or unknown.
Do not enumerate individual dated events. Ground each by an exact substring of
the letter as evidence. Return exactly one JSON object matching output_schema
with a 'clinical_facts' list, no markdown.

=== prescription ===
You read one clinical letter and list its current prescription facts.

Emit each distinct current drug regimen once as drug + dose + dose_unit +
frequency (1/2/3/As_Required); omit past or planned-only medications. Ground
each by an exact substring of the letter as evidence. Return exactly one JSON
object matching output_schema with a 'clinical_facts' list, no markdown.

=== investigation ===
{
  "instruction": "You are given a clinical letter about a patient with possible epilepsy. Extract **all** clinical facts relevant to epilepsy and seizures only, covering four families: `diagnosis`, `seizure_frequency`, `prescription`, and `investigation`. Return exactly one JSON object with a `clinical_facts` list. Each fact must contain:\n- `\"evidence\"`: an exact substring copied verbatim from the letter (including punctuation and spacing).\n- `\"family\"`: one of the four families.\n- Other keys specific to the family as detailed below.\n\n**Family-specific rules**\n\n1. **`diagnosis`** – Emit only epilepsy-related diagnoses as short canonical concepts. Allowed concepts: `\"epilepsy\"`, `\"generalised\"`, `\"focal\"`, `\"secondary-generalised-seizures\"`, `\"symptomatic\"`, `\"structural\"`, `\"focal-motor-seizures\"`, `\"focal-to-bilateral-convulsive-seizures\"`, `\"typical-absences\"`, `\"dissociative-seizures\"`, `\"status-epilepticus\"`, `\"juvenile-myoclonic-epilepsy\"`, `\"temporal-lobe-epilepsy\"`, `\"epileptic\"`, `\"generalised-seizures\"`, `\"focal-seizures-with-altered-awareness\"`, `\"focal-motor-seizures\"`, `\"symptomatic-structural-focal-epilepsy\"`. Do **not** emit long qualified phrases (e.g. `\"symptomatic epilepsy with generalised tonic clonic seizures\"`), comorbidities (e.g. hypertension, asthma, anxiety), psychiatric conditions, or negated diagnoses. De-duplicate: if the same concept appears more than once, emit only one fact. Use the exact phrase from the letter as evidence.\n\n2. **`seizure_frequency`** – Emit a fact for **each seizure type** that has a frequency statement (including dissociative seizures if mentioned). The fact must include `\"seizure_type\"` (a short description from the letter) and `\"state\"` which must be one of:\n   - `\"seizure-free\"` – when the letter explicitly states no seizures for a period (e.g. “seizure free for three years”, “has not had a seizure like this for around two years”).\n   - `\"active-rate\"` – when a current rate is given (e.g. “2-3 per month”, “around twice every week”). Additionally provide `\"number_of_seizures\"` (integer) if a clear count per time unit is given; if only a range is given, omit this key.\n   - `\"changed\"` – when the letter reports a change in frequency (e.g. “more of his typical absences”, “helped her seizures”, “occurring more frequently”, “remaining uncontrolled”). No extra key needed.\n   Do **not** default to `\"unknown\"` or invent a state. If no frequency information is present for a seizure type, do not emit a fact. Each distinct seizure type with its own frequency gets its own fact. Be careful: a statement like “he has had around 5 seizures in the last year” is an active-rate with number_of_seizures=5, not a change. A statement like “she has had no more seizures” is seizure-free. A statement like “the absences happen more frequently” is changed.\n\n3. **`prescription`** – Emit only **anti-epileptic drugs** (AEDs) that are currently prescribed, being started, or being changed (including dose adjustments). Do **not** emit medications for other conditions (e.g. statins, antihypertensives, antidepressants) or historical failures unless they are part of the current plan. The fact must include:\n   - `\"medication\"` (drug name, e.g. `\"sodium valproate\"`, `\"levetiracetam\"`, `\"zonisamide\"`, `\"carbamazepine\"`, `\"lamotrigine\"`, `\"perampanel\"`, `\"clobazam\"`, `\"midazolam\"`)\n   - `\"dose\"` (string, e.g. `\"300 mg BD\"`, `\"25 mg once a day\"`) – omit if no dose is given in the letter.\n   If a dose is mentioned as a range or plan (e.g. “increase by 100mg so that he is on 800mg bd”, “to be increased to 300 mg BD”), emit the **intended** dose (the target dose). Only emit medications explicitly named for epilepsy/seizures. Use generic names (e.g. zonisamide for Zonigram).\n\n4. **`investigation`** – Emit only **completed** investigations with modalities `MRI`, `CT`, `EEG`, or `telemetry`. Do **not** emit planned or arranged investigations (e.g. “I will request an MRI”). For each completed test:\n   - `\"modality\"`: one of `\"MRI\"`, `\"CT\"`, `\"EEG\"`, `\"telemetry\"`.\n   - `\"result\"`: `\"normal\"`, `\"abnormal\"`, or `\"unknown\"`. Use `\"unknown\"` only when the letter mentions the test was done but gives no result. If a result is given (even if vague, e.g. “showed an area of gliosis”), use `\"abnormal\"`; if explicitly called normal, use `\"normal\"`.\n   If the same modality appears multiple times with different dates/findings, emit each as a separate fact. Do **not** include other investigations (e.g. ECG, blood tests).\n\n**General rules**\n- Every `\"evidence\"` must be an **exact substring** of the letter – copy the phrase exactly as written, including any punctuation or misspellings.\n- **De-duplicate**: if two facts would be identical in all keys (evidence, family, and family-specific keys), emit only one.\n- Do **not** invent facts or modalities not mentioned.\n- Do **not** merge facts; each distinct instance gets its own entry.\n- Output **only** the JSON object – no markdown, no extra text.\n\n**Output schema (example)**\n```json\n{\n  \"clinical_facts\": [\n    {\"evidence\": \"Primary generalised epilepsy\", \"family\": \"diagnosis\", \"diagnosis\": \"generalised\"},\n    {\"evidence\": \"has had no seizures since Christmas 2015\", \"family\": \"seizure_frequency\", \"seizure_type\": \"seizures\", \"state\": \"seizure-free\"},\n    {\"evidence\": \"Levetiracetam 1000mg bd\", \"family\": \"prescription\", \"medication\": \"levetiracetam\", \"dose\": \"1000mg bd\"},\n    {\"evidence\": \"His MRI is normal.\", \"family\": \"investigation\", \"modality\": \"MRI\", \"result\": \"normal\"}\n  ]\n}\n```\n\n**Critical mistakes to avoid**\n- Emitting non-epilepsy diagnoses (comorbidities, negated conditions).\n- Emitting planned investigations as completed or with result `\"unknown\"`.\n- For seizure frequency, defaulting to `\"active-rate\"` when the letter describes a change or seizure-free period.\n- Omitting evidence that is not an exact verbatim substring.\n- Including medications that are not anti-epileptic drugs.\n- Including duplicate facts (same evidence, family, and other keys).\n- Outputting extra text or markdown outside the JSON object."
}
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.