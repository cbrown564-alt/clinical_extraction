# ExECTv2 LLM-with-rules component audit

Date: 2026-07-14  
Status: corrected architecture implemented and replay-verified; final model rows not promoted

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
- Models: GPT-4.1-mini, a historical DeepSeek V4 Flash API run with incomplete
  runtime metadata, and Qwen 3.6 35B repair v02.
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

The durable decision-0040 configurations are in
`configs/exectv2/model_led_audit/`. The no-call check rehydrates their recorded
historical producer blobs in a temporary directory and reproduced all scores,
origin counts, and post-model SF action counts:

```powershell
.venv\Scripts\python.exe scripts/check_exectv2_model_led_audit.py
```

Its retained aggregate-only output is
`experiments/exectv2_model_led_architecture_replay_full200_20260715.json`.

## Corrected three-model results

These are the candidate results that match the intended method going forward.
They use the current `clinical_headline` scorer, unchanged gold, saved full200
model outputs, and no new calls.

| Model | Overall | Diagnosis | SF headline | SF `state_profile` | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.8171 | 0.8583 | 0.6501 | 0.7813 | 0.8700 | 0.8614 |
| DeepSeek V4 Flash API run (incomplete runtime metadata) | 0.8543 | 0.8789 | 0.7146 | 0.8085 | 0.9057 | 0.9091 |
| Qwen 3.6 35B, repair v02 | 0.8234 | 0.8520 | 0.6343 | 0.7812 | 0.9220 | 0.8548 |

Within these historical saved outputs, the best corrected Diagnosis score is
`0.8789` for DeepSeek. It is audit-only because its runtime metadata is
incomplete. The best corrected
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
| DeepSeek V4 Flash API run (incomplete runtime metadata) | 0.9043 | 0.9057 | 301 | 12 |
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
| DeepSeek V4 Flash API run (incomplete runtime metadata) | 0.7602 | 0.7146 | -0.0456 |
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

## Regression accounting

The durable replay compares each model-owned family output with the final
post-rule family output using per-letter clinical-headline key equality. These
are aggregate counts over full200; no test60 row was inspected.

| Model | Family | Changed rows | Wrong → correct | Correct → wrong |
| --- | --- | ---: | ---: | ---: |
| GPT-4.1-mini | Diagnosis | 75 | 25 | 8 |
| GPT-4.1-mini | Seizure Frequency | 27 | 0 | 1 |
| GPT-4.1-mini | Prescription | 39 | 16 | 11 |
| DeepSeek historical API run | Diagnosis | 68 | 26 | 6 |
| DeepSeek historical API run | Seizure Frequency | 23 | 0 | 1 |
| DeepSeek historical API run | Prescription | 43 | 19 | 16 |
| Qwen 3.6 35B repair v02 | Diagnosis | 77 | 30 | 4 |
| Qwen 3.6 35B repair v02 | Seizure Frequency | 23 | 0 | 0 |
| Qwen 3.6 35B repair v02 | Prescription | 33 | 13 | 13 |

Investigations has zero changed rows for all three models. The replay reports a
minimum exact-evidence rate of `1.0`; DeepSeek retains its one historical parse
or schema failure, and the other two conditions have zero. The nonzero
correct-to-wrong counts mean the component graph now has the right owners, but
the deterministic corrections are not yet safe enough to promote as final
model rows. Any rule change must be developed on dev140 without inspecting
test60 failures.

## Decision

- Adopt the family ownership boundary in
  [decision 0040](../../../decisions/0040-final-exect-llm-with-rules-family-ownership.md).
- Retain the corrected configurations and aggregate replay as architecture
  evidence, not as the final six-model comparison.
- Do not describe the old Prescription or Seizure Frequency columns as a
  model-to-model comparison.
- Use `0.8789` as the best corrected full200 Diagnosis aggregate for the
  intended architecture, not `0.9034`; the latter is a different dev140
  combined candidate.
- Keep the corrected results development-inclusive and aggregate-only.

## Next action

The permitted dev140 analysis is complete. Across 319 changed model/family
rows, the family-local view has 160 wrong-to-correct, 41 correct-to-wrong, and
118 changed-still-wrong outcomes; every changed row has exact evidence.
Seizure Frequency has 38 rescues and no component-local regression, while
Diagnosis has 18 regressions and Prescription has 23. Prescription residual
addition is net harmful and its four uniquely attributable rows are all
correct-to-wrong. See the
[dev140 regression analysis](exectv2_model_led_dev140_regression_analysis_2026-07-15.md).

Predeclare one bounded no-call candidate that keeps Seizure Frequency,
Investigations, Prescription normalization, and supported regimen splitting;
disables Prescription residual addition; and adds general model-preserving
guards for Diagnosis subsumption and Prescription current-versus-future
selection. The final six-model protocol must use decision-0040 family bindings
and rerun the same aggregate checks; it must not reuse the historical DeepSeek
result because its runtime metadata is incomplete.
