# ExECTv2 Key-Entity Structured Prompt v0.5 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_only_key_entities_structured`  
Model: `openai/gpt-4.1-mini`

## Decision

v0.5 is the best single-prompt structured-event dev25 candidate so far, but it
is still revise-only. The diagnosis-focused prompt pass substantially improved
Diagnosis clinical-recovery headline F1 from `0.460` to `0.569` while preserving
Prescription/medication above target (`0.897`), Investigations above target
(`0.837`), and SeizureFrequency near its v0.4 recovery level (`0.633`).

This is enough to justify a next architectural comparison: a specialist
Diagnosis prompt against the same dev25 surface. More broad single-prompt rules
are likely to add cognitive load faster than they add Diagnosis recall.

## v0.4 -> v0.5 Comparison

| Layer | v0.4 item F1 | v0.5 item F1 | Delta |
| --- | ---: | ---: | ---: |
| source-near | 0.728 | 0.729 | +0.001 |
| phrase-only | 0.446 | 0.508 | +0.062 |
| semantic | 0.295 | 0.368 | +0.073 |
| benchmark | 0.256 | 0.274 | +0.018 |

| Entity | v0.4 clinical F1 | v0.5 clinical F1 | Read |
| --- | ---: | ---: | --- |
| Prescription | 0.900 | 0.897 | Above target; stable. |
| Diagnosis | 0.460 | 0.569 | Large gain, still below target. |
| SeizureFrequency | 0.644 | 0.633 | Slight slip, still much better than v0.3. |
| Investigations | 0.837 | 0.837 | Above target; stable. |

## Error-Analysis Read

The v0.5 prompt targeted core Diagnosis span rendering: strip hedging words from
mention text into `Certainty`, keep abbreviations such as `JME` as the source
span, avoid symptom-only mentions, and preserve tonic-clonic wording. The strong
semantic and phrase-only gains show that these were the right error families.

Diagnosis remains below target because the single prompt is now carrying many
competing policies: event decomposition, medication regimen rendering,
seizure-frequency temporal logic, investigation precision, and diagnosis concept
projection. This is exactly the point the original architecture question asked
us to test.

## Next Iteration

Run a focused specialist Diagnosis prompt on the same dev25 surface before
spending dev140. Compare:

1. v0.5 single-prompt structured Diagnosis headline F1 (`0.569`);
2. an entity-family specialist Diagnosis prompt with the same evidence/neutral
   projection gates;
3. optionally, a hybrid assembly that keeps v0.5 for medication/SF/investigation
   and uses the specialist Diagnosis output only if it improves the headline
   without harming evidence validity.
