# ExECTv2 LLM-with-rules component audit

Date: 2026-07-14  
Status: completed architecture audit; corrected results not yet promoted

## Question

Do the three full200 model rows represent the intended LLM-with-rules method:
each named model extracts the clinical facts, followed by the same attributable
deterministic corrections?

This audit also calculates corrected full200 aggregate Diagnosis and
Prescription scores after applying the retained model outputs and the approved
post-extraction corrections. It does not make new model calls.

## Intended method

For each entity family and model:

1. The named model extracts or selects the clinical fact and its evidence.
2. Deterministic code may validate exact evidence, normalize a representation,
   repair an output attribute, remove a duplicate or unsupported fact, or apply
   a narrow recorded post-extraction correction.
3. Deterministic code must not replace the model output with a rules-only
   extraction or independently supply most of the clinical facts.
4. Another model must not select the named model's final facts.

A rule that independently adds, removes, or chooses a clinical concept remains
deterministic clinical selection. The resulting row is hybrid, but the fact is
not credited to the LLM.

## Protocol

- Dataset and split: ExECTv2 full200, comprising dev140 and test60.
- Row policy: aggregate-only. Do not inspect, quote, classify, or tune from
  test60 rows or full200 row-level differences.
- Models: GPT-4.1-mini, a historical DeepSeek V4 Flash API run whose thinking
  state was not recorded, and Qwen 3.6 35B repair v02.
- Replay: saved historical outputs only; no new model calls.
- Comparator: the recorded full200 scores in the three-model table.
- Primary component metrics: Diagnosis and Prescription clinical-fact F1.
- Secondary evidence: final fact-origin counts and deterministic additions,
  removals, rewrites, fallbacks, and clinical-selection ownership by family.
- Scorer: the existing `clinical_headline` family scorer used by the full200
  model comparison; gold and scorer remain unchanged.
- Diagnosis correction: apply the opt-in Diagnosis resolution candidate added
  in commit `14bce056` to each model's own saved Diagnosis output.
- Prescription correction: start from each model's own saved Prescription
  extraction. Apply only shared post-extraction normalization and regimen
  repair; do not substitute the deterministic Prescription extractor.
- Required comparison: before and after aggregate scores for each model and
  family, plus an ownership audit of Diagnosis, SeizureFrequency, Prescription,
  and Investigations.
- Stop rule: retain a corrected row only if its source model and every
  prediction-changing deterministic step are attributable. Mark the family
  unresolved if the saved artifact does not preserve the required model output.

## Claim boundary

This is a development-inclusive, aggregate-only replay. It may correct the
description and aggregate scores of the three saved model conditions. It does
not establish an independent holdout result, authorize test60 row inspection,
validate clinical correctness, or prove transfer to another dataset.

The three saved model conditions audited here are partial historical evidence,
not the final comparison roster. Decision 0039 fixes the final six as
GPT-4.1-mini, GPT-5.6 Luna, GPT-5.6 Sol, hosted DeepSeek V4 Flash, local Qwen
3.6:35B, and local Gemma 4 26B. Decision 0040 fixes the family ownership rules
for the final comparison.

## Answer

The recorded three-model table is not a consistent LLM-with-rules comparison.
Diagnosis is model-led but uses material deterministic rescue. Investigations
is model-led. Prescription is deterministic-only. Seizure Frequency merges the
model result with an independent deterministic extractor.

An aggregate-only replay of the intended method is possible from the saved
outputs. It uses each named model's Diagnosis, Seizure Frequency, Prescription,
and Investigations facts; retains attributable post-model corrections; removes
the deterministic Prescription substitute; and removes the deterministic
Seizure Frequency extractor union.

Machine-readable result:
`experiments/exectv2_llm_with_rules_component_audit_full200_20260714.json`.

## Corrected three-model results

These are the candidate results that match the intended method going forward.
They use the current `clinical_headline` scorer, unchanged gold, saved full200
model outputs, and no new calls.

| Model | Overall | Diagnosis | Seizure frequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.8171 | 0.8583 | 0.6501 | 0.8700 | 0.8614 |
| DeepSeek V4 Flash API run (thinking state unrecorded) | 0.8543 | 0.8789 | 0.7146 | 0.9057 | 0.9091 |
| Qwen 3.6 35B, repair v02 | 0.8234 | 0.8520 | 0.6343 | 0.9220 | 0.8548 |

Within these historical saved outputs, the best corrected Diagnosis score is
`0.8789` for DeepSeek. It is audit-only and will not be the paper's DeepSeek
result unless thinking-enabled execution can be proved. The best corrected
Prescription score is `0.9220` for Qwen.

The changes from the manuscript table are not all gains from the Diagnosis
fixes. They also remove two architecture substitutions: deterministic-only
Prescription and the deterministic Seizure Frequency extractor union. The
corrected overall score therefore falls for GPT and DeepSeek even though their
Diagnosis scores rise.

## Prescription correction

The old `0.8926` Prescription score was identical for every model because all
three rows used `deterministic_prescription_repair_v03` as the producer. It did
not measure the named model's Prescription extraction.

| Model | Model output only | Model plus shared corrections | Final model-origin facts | Rule-added facts |
| --- | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.8595 | 0.8700 | 395 | 10 |
| DeepSeek V4 Flash API run (thinking state unrecorded) | 0.9043 | 0.9057 | 301 | 12 |
| Qwen 3.6 35B, repair v02 | 0.9213 | 0.9220 | 294 | 12 |

The corrected Prescription path is model-led. Shared rules normalize drug and
dose representations, split supported daily regimens, remove unsupported
mentions, and add a small number of bounded residual facts. Rule-added facts
remain separately attributable.

## Component ownership audit

| Family | Recorded three-model path | Finding | Intended path |
| --- | --- | --- | --- |
| Diagnosis | Named model decomposer plus dictionary and heading/residual recovery | Model-led, but 50–68 final facts per model are deterministic rescue | Retain with explicit model/rule attribution |
| Seizure Frequency | Named model output plus projection, suppression, and union with a rules-only extractor | Does not meet the agreed definition | Named model output plus projection and suppression; no deterministic extractor union |
| Prescription | Deterministic all-entity extractor and regimen repair | Does not meet the agreed definition; the model is not the producer | Named model output plus shared Prescription corrections |
| Investigations | Named model structured output through a thin adapter | Meets the agreed definition | Retain |

For the corrected Seizure Frequency path, all final facts retain model origin.
Deterministic code performed 24–29 projection actions and 2–4 suppression
actions per model over full200. Those actions can change clinical meaning, so
the path is hybrid and must not credit those decisions to the model.

### Seizure Frequency score ladder

The historical assembled score includes the deterministic extractor union.
The corrected candidate starts from the named model's pre-union output and
retains attributable projection and suppression only.

| Model | Historical assembled `clinical_headline` F1 | Corrected model-led F1 | Change |
| --- | ---: | ---: | ---: |
| GPT-4.1-mini | 0.7525 | 0.6501 | -0.1024 |
| DeepSeek V4 Flash API run (thinking state unrecorded) | 0.7602 | 0.7146 | -0.0456 |
| Qwen 3.6 35B, repair v02 | 0.7020 | 0.6343 | -0.0677 |

The lower corrected values are not regressions caused by removing a useful
post-model repair. They expose how much the rejected independent extractor
union contributed to the old column. These are compatibility scores under
`clinical_headline`; promotion also requires the `state_profile` result from
decision 0037.

## Important scoring dependency

The per-family `clinical_headline` values are not pure component scores. Recall
is entity-agnostic, so a concept emitted in another family can satisfy a gold
fact. In the audit, DeepSeek's serialized Diagnosis predictions were identical
with and without the deterministic Seizure Frequency union, but Diagnosis F1
changed from `0.8801` to `0.8789`.

The table remains a valid score of the final assembled output under the current
scorer. It should not be used alone to claim that a named family extractor made
the credited decision. Component claims require the origin counts and
prediction-changing rule accounting above.

## Decision

- Adopt the family ownership boundary in
  [decision 0040](../../../decisions/0040-final-exect-llm-with-rules-family-ownership.md).
- Replace the manuscript's three-model table only after the intended model-led
  configurations and aggregate artifact are retained in the active evidence
  set.
- Do not describe the old Prescription or Seizure Frequency columns as a
  model-to-model comparison.
- Use `0.8789` as the best corrected full200 Diagnosis aggregate for the
  intended architecture, not `0.9034`; the latter is a different dev140
  combined candidate.
- Keep the corrected results development-inclusive and aggregate-only.

## Next implementation action

Create durable model-swap configurations that select each model's structured
Prescription lane and pre-union Seizure Frequency lane, then reproduce this
aggregate artifact through the normal runbook and retained-evidence checks.
Add Seizure Frequency `state_profile`, exact-evidence accounting,
schema/parse failures, fact-origin counts, and deterministic-correct regression
counts before promotion.
