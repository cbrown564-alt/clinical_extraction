# ExECTv2 six-model Seizure Frequency over-inference result

Date: 2026-07-18  
Status: completed no-call dev140 study

Protocol: [exectv2_six_model_sf_overinference_protocol_2026-07-18.md](exectv2_six_model_sf_overinference_protocol_2026-07-18.md)  
Machine-readable result: `experiments/exectv2_six_model_sf_overinference_dev140_20260718.json`

## Answer

The primary gold unknown-only denominator contains **0 letters**, so the result is classified as **diagnostic**.

| Model | Comparator over-read | Final over-read | Comparator state F1 | Final state F1 | W→C | C→W |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0/0 (n/a) | 0/0 (n/a) | 0.7340 | 0.7845 | 13 | 0 |
| GPT-5.6 Luna | 0/0 (n/a) | 0/0 (n/a) | 0.8357 | 0.8551 | 4 | 0 |
| GPT-5.6 Sol | 0/0 (n/a) | 0/0 (n/a) | 0.8509 | 0.8603 | 3 | 1 |
| DeepSeek V4 Flash | 0/0 (n/a) | 0/0 (n/a) | 0.8104 | 0.8429 | 9 | 0 |
| Qwen 3.6:35B | 0/0 (n/a) | 0/0 (n/a) | 0.7517 | 0.7986 | 13 | 0 |
| Gemma 4 26B | 0/0 (n/a) | 0/0 (n/a) | 0.6894 | 0.7386 | 12 | 0 |

The comparator is the model's structured output after schema and evidence validation.
The final stage adds the named deterministic Seizure Frequency projection and suppression path.

## Component evidence

| Model | Over-reads rescued | Introduced | Persistent | Changed-still-wrong | Exact final evidence | SF parse/schema failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0 | 0 | 0 | 3 | 1.0000 | 0 |
| GPT-5.6 Luna | 0 | 0 | 0 | 1 | 1.0000 | 0 |
| GPT-5.6 Sol | 0 | 0 | 0 | 0 | 1.0000 | 0 |
| DeepSeek V4 Flash | 0 | 0 | 0 | 1 | 1.0000 | 0 |
| Qwen 3.6:35B | 0 | 0 | 0 | 2 | 1.0000 | 0 |
| Gemma 4 26B | 0 | 0 | 0 | 5 | 1.0000 | 0 |

Every state-changing row is attributed to `deterministic_sf_projection_or_suppression`;
unchanged rows remain model-selected facts passing through the final adapter. 
Exact evidence means source-text presence, not independent clinical confirmation.

## Gold-band diagnostics

Empty-gold rows remain separate because missing annotation is not proof that a supported prediction is false.
The following counts are diagnostics, not factuality prevalence estimates.

| Model | Empty-gold active-rate | Seizure-free-band active-rate | Changed-only active-rate |
| --- | ---: | ---: | ---: |
| GPT-4.1-mini | 11/41 | 5/34 | 0/2 |
| GPT-5.6 Luna | 10/41 | 4/34 | 0/2 |
| GPT-5.6 Sol | 7/41 | 4/34 | 0/2 |
| DeepSeek V4 Flash | 8/41 | 2/34 | 0/2 |
| Qwen 3.6:35B | 13/41 | 5/34 | 0/2 |
| Gemma 4 26B | 12/41 | 10/34 | 1/2 |

## Permitted development examples

No primary-band over-read example exists because the gold unknown-only denominator is empty. Component-transition examples remain available:
- `EA0052` / GPT-4.1-mini: `wrong_to_correct`; gold `[]`, comparator `['active-rate']`, final `[]`; evidence: “Sine the last appointment Mr Richards has had 4 more attacks.”
- `EA0062` / GPT-4.1-mini: `wrong_to_correct`; gold `[]`, comparator `['active-rate']`, final `[]`; evidence: “She used to live in London and may have had a few seizures when she was younger but cant remember much about this.”
- `EA0063` / GPT-4.1-mini: `wrong_to_correct`; gold `['seizure-free']`, comparator `['changed', 'seizure-free']`, final `['seizure-free']`; evidence: “I was glad to hear that her seizures have stopped since reaching her current dose of lamotrigine. Her last seizure now was 5 months ago”
- `EA0078` / GPT-4.1-mini: `wrong_to_correct`; gold `[]`, comparator `['changed']`, final `[]`; evidence: “Her seizures are reasonably controlled by her low mood as well as some agitation is causing her some distress.”
- `EA0085` / GPT-4.1-mini: `wrong_to_correct`; gold `['active-rate']`, comparator `['active-rate', 'seizure-free']`, final `['active-rate']`; evidence: “He is a 21-year-old gentleman who had his first seizure at the age of 12 and was investigated by paediatrics.”
- `EA0113` / GPT-4.1-mini: `wrong_to_correct`; gold `['active-rate']`, comparator `['active-rate', 'seizure-free']`, final `['active-rate']`; evidence: “He has had on average one seizure a year since the age of 16 but a total of 3 in 2018.”

## Interpretation and claim boundary

This study measures an ExECT-specific analogue of unknown-versus-rate behavior. It does not prove that the Gan mechanism transfers, because Gan uses one exhaustive label per note while ExECT permits multiple mentions and has documented annotation omissions and conventions.

ExECTv2 dev140 development evidence for the named six model conditions and fixed state transform; not Gan-to-ExECT transfer validation, test60 evidence, clinical validation, or an empty-gold factuality estimate.
