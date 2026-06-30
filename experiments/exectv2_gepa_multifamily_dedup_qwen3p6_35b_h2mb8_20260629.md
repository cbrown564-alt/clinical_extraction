# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_multifamily_dedup_qwen3p6_35b_h2mb8_20260629

Date: 2026-06-29

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `ollama_chat/qwen3.6:35b` (temp 0.0, max_tokens 6000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 2000 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 2083 tokens** (seed was 417 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.654** (P=0.630 R=0.680, Diagnosis=concept_negation)
  - Diagnosis=0.553  SeizureFrequency=0.506  Prescription=0.730  Investigations=0.932
- **Producer evidence-recall (source_near): 0.615** (GEPA per-family baseline 0.694, v08 hybrid 0.883) — Dx=0.378 SF=0.663 Rx=0.835 Inv=0.919
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.132
- Semantic (CUI-dropped) per-item F1: 0.142
- Letters: 140 (unscorable: 0); facts emitted 1357, scored 796

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
=== diagnosis ===
You read one clinical letter and extract all distinct clinical facts. The facts belong to exactly four families: `diagnosis`, `seizure_frequency`, `prescription`, and `investigation`. For each fact you must output its short canonical concept, an exact substring evidence copied verbatim from the letter, the family name, and a negation field (`"affirmed"` or `"negated"`) – only diagnosis facts use negation; for other families always set `"negation": "affirmed"`.

**Rules for each family:**

- **diagnosis**: Only epilepsy and seizure type diagnoses (e.g., `focal epilepsy`, `generalised tonic clonic seizure`, `temporal lobe epilepsy`, `localisation-related epilepsy`). Do **not** emit non‑epileptic conditions (e.g., `non‑epileptic psychogenic seizures`), comorbid mental health conditions (e.g., `anxiety`, `depression`), or general medical problems (e.g., `hypertension`, `diabetes`). If a diagnosis is explicitly excluded (e.g., “no evidence of …”), set `"negation": "negated"`. Use a short, canonical term – not a long phrase. Example: `"concept": "focal seizures"` not `"infrequent focal seizures"`.

- **seizure_frequency**: For each seizure type mentioned in the letter, emit one fact with a precise state:
  - `"seizure-free"` if no seizures occurred (e.g., “has had no further seizures”).
  - `"active-rate (NumberOfSeizures=<number>, TimePeriod=<day|week|month|year>)"` when a specific count and period are given (e.g., “seizures every 1‑2 weeks” → `NumberOfSeizures=1, TimePeriod=Week`; “5 seizures in the last year” → `NumberOfSeizures=5, TimePeriod=Year`).
  - `"changed (infrequent|improved|worse|more|fewer)"` when frequency changes are reported but no exact rate (e.g., “seizures are less frequent now” → `"changed (fewer)"`).
  - Use the same seizure concept as in diagnosis (e.g., `focal seizures`, `generalised tonic clonic seizures`). If the letter refers to “seizures” in general, use `"seizures"`.

- **prescription**: Emit one fact per current medication with concept containing generic drug name, dose (in mg or units), and dosing frequency (e.g., `"Carbamazepine 400mg x2"`, `"Levetiracetam 1500mg bd"`, `"Insulin"` if no dose given). Only include medications that the patient is currently taking (not those stopped or not tolerated). Use the exact dose and frequency as written.

- **investigation**: Emit one fact per diagnostic test (EEG, MRI, CT, telemetry) with concept `"<modality> (<result>)"` where result is either `Normal`, `Abnormal`, or a specific finding (e.g., `"EEG (Normal)"`, `"MRI (negative)"`, `"EEG (focal abnormalities)"`). Do **not** emit modalities other than EEG, MRI, CT, or telemetry.

**General requirements:**
- Every `evidence` must be a **contiguous exact substring** copied from the letter (punctuation included). If multiple substrings support the same fact, use the most precise one.
- De‑duplicate identical concepts (same family and same canonical concept). If the same diagnosis appears multiple times, emit it only once.
- Output exactly one JSON object following this schema (no markdown):
```json
{"clinical_facts": [{"concept": "<short concept>", "evidence": "<exact substring>", "family": "diagnosis|seizure_frequency|prescription|investigation", "negation": "affirmed|negated"}]}
```
  The order of facts within the list does not matter.

- Do **not** emit facts for:
  - Non‑epileptic diagnoses (psychogenic, syncope, etc.)
  - Comorbid conditions (anxiety, depression, hypertension, diabetes, previous infections like herpes encephalitis)
  - Medications that are not current (e.g., “levetiracetam gave her mood disorder” – that is an adverse effect, not a prescription)
  - Observations that are not one of the four families (e.g., “seizures from sleep” is part of diagnosis, not a separate fact)

- Keep concepts concise and canonical. Use standard medical terminology without qualifiers like “new diagnosis”, “drug refractory”, “infrequent”, etc. The gold standard expects:
  - `"epilepsy"` or `"focal epilepsy"` (not `"refractory focal epilepsy"`)
  - `"focal seizures"` (not `"infrequent focal seizures"`)
  - `"generalised tonic clonic seizures"` (not `"generalised tonic clonic seizures from sleep"`)
  - `"SodiumValproate 200mg x2"` (not `"Eplim 200mg twice a day"` – use generic name, normalise dose to mg)

- For seizure frequency, never use `"active-rate"` when the patient is seizure‑free; use `"seizure-free"` instead. Never emit a seizure frequency fact with `"unknown"` or no state – it will be dropped.

- Read the entire letter before deciding what is a current diagnosis vs. historical condition. Only include diagnoses that are explicitly stated as present (or explicitly excluded) in the letter.

- The output must be a single JSON object with no surrounding text, markdown, or code fences.

=== seizure_frequency ===
You are given a clinical letter (letter_text) and must extract all seizure-frequency facts.  

- Return exactly one JSON object matching the output_schema: {"clinical_facts": [{"evidence": "exact substring from the letter", "family": "seizure_frequency", "seizure_type": "<seizure type>", "state": "<state>"}]}.  
- For each distinct seizure type mentioned (use the named type exactly as in the letter, e.g. "generalised tonic clonic seizures", "absences", "myoclonic jerks"; if no specific type is given, use "seizures"), output exactly one fact.  
- The "evidence" must be a verbatim substring from the letter that grounds the fact.  
- The "state" must be one of:  
  * "active_rate" – if a numeric rate or count is provided (e.g. "occurs 4 to 5 times a year", "1 since previous appointment")  
  * "seizure_free" – if the patient is explicitly said to have no seizures (e.g. "seizure free", "no further seizures")  
  * "changed" – if there is a reported change in frequency (improved/worsened/more/fewer) without a specific rate  
  * "unknown" – only if the frequency is mentioned but cannot be classified as the above (e.g. "occasional absences" without a rate or change)  
- Do **not** emit facts for negated statements (e.g. "no history of myoclonic jerks"), diagnoses, medications, investigations, or any other family.  
- Keep seizure_type concise: use the short canonical term from the letter (e.g. "generalised tonic clonic seizures", not the full diagnosis line).  
- De-duplicate: if the same seizure type appears with multiple pieces of evidence, choose the most specific state (prefer active_rate over changed, seizure_free over others) or combine if needed.

=== prescription ===
You read one clinical letter and list its current prescription facts.

Emit each distinct current drug regimen once as drug + dose + dose_unit +
frequency (1/2/3/As_Required); omit past or planned-only medications. Ground
each by an exact substring of the letter as evidence. Return exactly one JSON
object matching output_schema with a 'clinical_facts' list, no markdown.

=== investigation ===
Read the clinical letter. Extract only completed investigations (modality must be one of MRI, CT, EEG, or telemetry) that are explicitly mentioned as having been performed (past tense, e.g., "was done", "showed", "scan from 2017"). For each distinct modality, determine the result:  

- **normal** if the letter uses words like "normal", "unremarkable", "no abnormality".  
- **abnormal** if the letter describes a finding (e.g., "gliosis", "infarct", "sharp waves", "spikes", "evidence of epilepsy").  
- **unknown** only if the letter explicitly states the result is unknown or not available (e.g., "result not available").  

Do **not** infer unknown from absence of a result; if no result is stated, do not emit that modality.  
Do **not** include investigations that are only planned (e.g., "I will request an MRI").  
Do **not** include other modalities (ECG, blood tests, etc.) or any non‑investigation facts (diagnosis, seizure frequency, medications, examination findings, etc.).  

Ground each fact with an exact substring from the letter that confirms the modality and the result. Output exactly one JSON object matching the schema:  

```json
{"clinical_facts": [{"evidence": "exact substring", "family": "investigation", "modality": "MRI | CT | EEG | telemetry", "result": "normal | abnormal | unknown"}]}
```

Each distinct completed modality should appear at most once. Do not wrap in markdown.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.