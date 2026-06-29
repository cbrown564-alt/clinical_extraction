# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_recall_lanes_deepseekchat_20260628

Date: 2026-06-28

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `deepseek/deepseek-chat` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 2400 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2400 tok (alpha 0.05)
- **final instruction length: 2344 tokens** (seed was 732 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.728** (P=0.678 R=0.786, Diagnosis=concept_negation)
  - Diagnosis=0.703  SeizureFrequency=0.581  Prescription=0.785  Investigations=0.921
- **Producer evidence-recall (source_near): 0.780** (GEPA per-family baseline 0.694, v08 hybrid 0.883) — Dx=0.642 SF=0.813 Rx=0.922 Inv=0.934
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.123
- Semantic (CUI-dropped) per-item F1: 0.133
- Letters: 140 (unscorable: 0); facts emitted 1610, scored 974

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
=== diagnosis ===
{
  "instruction": "You are a clinical information extractor. Given the text of a clinical letter, produce a JSON object with a single key \"clinical_facts\" containing an exhaustive list of facts. Each fact is a dict with fields: \"concept\" (short canonical name), \"evidence\" (exact substring from the letter), \"family\" (one of \"diagnosis\", \"seizure_frequency\", \"prescription\", \"investigation\"), and \"negation\" (always \"affirmed\"; do not extract negated facts).\n\nRules:\n\n### diagnosis\n- Extract **only** epilepsy-related diagnoses: epilepsy syndromes (e.g. \"juvenile absence epilepsy\", \"temporal lobe epilepsy\"), seizure types (e.g. \"focal seizures\", \"generalised tonic clonic seizure\", \"typical absences\", \"absence events\"), and the generic term \"epilepsy\". Do **not** include comorbid conditions (e.g. mild head injury, dissociative seizures, syncope) or non‑epileptic events, even if listed.\n- Use the **exact term** as it appears in the letter for the concept (e.g. \"absence events\", not \"absence seizures\"; \"typical absences\", not \"absences\"). Omit qualifiers like \"refractory\", \"nocturnal\", \"possible\", \"suspected\", \"secondary\" from the concept; keep them in the evidence.\n- Expand hyphenated or combined diagnoses into separate facts (e.g. \"focal epilepsy – probable temporal\" yields \"focal epilepsy\" and \"temporal lobe epilepsy\").\n- Do **not** extract negated diagnoses (e.g. \"no history of febrile seizures\" is ignored). Only extract affirmed diagnoses.\n- Negation: always \"affirmed\".\n- Evidence: copy the exact substring (including surrounding words) that supports the concept.\n\n### seizure_frequency\n- For each distinct seizure type mentioned (including generic \"seizures\"), emit a fact **only if** a frequency, change, or seizure-free state is stated. Do **not** emit for purely diagnostic mentions.\n- Concept: the exact seizure type string from the letter (e.g. \"absences\", \"absence events\", \"generalised tonic clonic seizure\", \"focal seizures\"). If the text says \"seizure free\" without specifying a type, concept is \"seizure-free\".\n- Evidence: the exact substring describing the frequency state. Choose the appropriate substring to capture:\n  - **Active rate**: a specific count, rate, or periodicity (e.g. \"seizures on a weekly basis\", \"4 to 5 times a year\", \"2-3 per day\", \"every month\").\n  - **Seizure-free**: a phrase indicating no seizures (e.g. \"has had no further seizures\", \"seizure free since before Christmas\", \"last seizure was two years ago\" – even if a last occurrence date is given, treat as seizure-free for that type).\n  - **Change in frequency**: a statement that seizures have increased, decreased, improved, worsened, or are continuing (e.g. \"increase in her seizures\", \"more of his typical absences\", \"absences continue fairly frequent\", \"things improved\", \"seizures have been worse in the last year\", \"Her seizure frequency has reduced from about once a year to 1 seizure every two to three years\"). For any explicit change, use the evidence that conveys the change.\n- If multiple distinct frequency statements exist for the same seizure type (e.g. both an active rate and a change), emit separate facts.\n- Negation: always \"affirmed\".\n\n### prescription\n- Extract **only current medications** that the patient is actively taking at the time of the letter. Do **not** extract historical medications or future planned changes (e.g. \"I would suggest increasing...\" is not extracted unless the letter states it as a current prescription).\n- Concept: the drug name (e.g. \"lamotrigine\", \"sodium valproate\", \"carbamazepine\", \"epilim\").\n- Evidence: the full medication string as it appears, including dose and frequency. If the same drug is listed with multiple distinct doses (e.g. \"100mg am, 200mg pm\"), **split** into separate facts, each with its own evidence substring (e.g. \"Carbamazepine 100mg am\" and \"Carbamazepine 200mg pm\"). If dose is not stated, use the drug name only.\n- Negation: always \"affirmed\".\n\n### investigation\n- Emit a fact for each of: MRI, CT, EEG, telemetry, ECG (including video EEG) that is mentioned **with a result** or **as pending**. Do **not** include physical examinations.\n- Concept: the modality (e.g. \"MRI\", \"EEG\").\n- Evidence: the exact sentence or substring that states the investigation and its result or pending status (e.g. \"MRI 2016 normal\", \"EEG 2015 frequent generalised spike and wave\", \"I will investigate further with an EEG and MRI scan of the brain\"). If the same modality appears multiple times with different results or different dates, emit separate facts.\n- Negation: always \"affirmed\".\n\n### General rules\n- Every \"evidence\" must be an exact contiguous substring from the letter. Preserve case and punctuation.\n- De‑duplicate identical facts (same concept, evidence, family, negation).\n- Do not invent concepts or facts not directly supported by the letter.\n- Output exactly one JSON object, no markdown, no extra text."
}

=== seizure_frequency ===
{
  "instruction": "You will read one clinical letter and extract its seizure-frequency facts exhaustively.\n\nEmit one fact per (seizure type × distinct frequency statement). If the same seizure type appears with multiple distinct statements (e.g., a current numeric rate and a separately reported change), list each as a separate fact.\n\nFor each fact provide:\n- \"evidence\": the exact substring copied verbatim from the letter. It must be a contiguous piece of text as it appears.\n- \"family\": always \"seizure_frequency\".\n- \"seizure_type\": the exact term used in the letter (e.g., \"generalised tonic clonic seizures\", \"focal motor seizures\", \"myoclonic jerks\", \"absences\", \"seizure\", \"seizures\"). Do not rephrase, pluralise, or shorten. Use the precise noun phrase from the letter.\n- \"state\": one of the following, chosen strictly:\n  - **\"active_rate\"**: an explicit count, rate, or cadence (e.g., \"2-3 per month\", \"weekly\", \"once per week\", \"six in total over two years\"). Do **not** use a single dated event (e.g., \"last event July 2016\") as an active_rate; such an event is instead captured under seizure_free if it indicates a current free period, otherwise ignored.\n  - **\"seizure_free\"**: seizures have stopped or there is a current seizure-free period (e.g., \"no seizures since March\", \"seizure-free for 6 months\", \"last occurred three years ago\", \"last event was 10 months ago\" when that implies current freedom). Only include the most recent/relevant seizure-free statement; ignore historical references that are no longer current (e.g., \"Previously she has been more than eight years seizure free\" is superseded by a more recent event).\n  - **\"changed\"**: a reported increase, decrease, improvement, or worsening **without a usable number** (e.g., \"seizures more frequent\", \"improved\", \"worse\", \"seizure frequency has improved\"). The change must be explicitly directional; do **not** treat vague statements (e.g., \"fluctuates\", \"not so good\") as changed unless they contain a clear comparative word.\n  - Do **not** emit a fact with state \"unknown\". If a seizure type is mentioned without any frequency, free period, or change, omit it entirely.\n\nGround each fact on an exact substring from the letter. Do not enumerate individual dated events as active_rate if they are merely past events without a current ongoing pattern. Only output facts from the \"seizure_frequency\" family; ignore diagnosis, investigations, medications, and other families.\n\nDe-duplicate identical facts (same evidence, same seizure_type, same state). Return exactly one JSON object matching the schema below, with no markdown or extra text.\n\n{\"clinical_facts\": [{\"evidence\": \"exact substring copied from the letter\", \"family\": \"seizure_frequency\", \"seizure_type\": \"named seizure type exactly as in the letter\", \"state\": \"active_rate | seizure_free | changed\"}]}"
}

=== prescription ===
You read one clinical letter and list its current prescription facts.

Emit each distinct current drug regimen once as drug + dose + dose_unit +
frequency (1/2/3/As_Required); omit past or planned-only medications. Ground
each by an exact substring of the letter as evidence. Return exactly one JSON
object matching output_schema with a 'clinical_facts' list, no markdown.

=== investigation ===
You will receive a clinical letter. Extract only the completed investigation facts for the modalities MRI, CT, EEG, or telemetry. A completed investigation is one that has been performed and whose result is explicitly reported in the letter (normal, abnormal, or unknown). Do not include investigations that are only planned, requested, or awaited. For each such investigation, output exactly one JSON object with the following keys:
- "evidence": an exact substring copied verbatim from the letter that confirms the modality and its result.
- "family": always "investigation".
- "modality": one of "MRI", "CT", "EEG", or "telemetry".
- "result": one of "normal", "abnormal", or "unknown" as stated in the letter.

Return exactly one JSON object matching the schema {"clinical_facts": [list of fact objects]}. Do not include any other text, markdown, or facts outside the four modalities.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.