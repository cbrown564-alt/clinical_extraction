# 08 — GEPA negative comparison

Last updated: 2026-07-15

The selected ExECT LLM-only run is one GEPA-optimized GPT-4.1-mini program on
dev140.

| Measure | Result |
| --- | ---: |
| Clinical fact F1 (`clinical_headline`) | 0.7393 |
| Strict benchmark item F1 | 0.1356 |
| Historical LLM-with-rules control (`v08`) | 0.9202 (superseded value 0.9189, pre the disclosed Diagnosis subsumption-guard fix, commit 41165adc, 2026-08-11) |

This is a negative development comparison. It used an optimizer-only
development subset and is not a published-benchmark or production result. The
selected files retain the exact instruction, predictions, summary, entry point,
metric, adapter, scorer, and tests needed for replay.

Do not claim that LLM only matches the combined method or that this historical
search establishes a limit for all models.

The `v08` comparator is reproducible but uses a deterministic Prescription
producer and a Seizure Frequency extractor union. It does not satisfy the final
model-led family contract in
[decision 0040](../decisions/0040-final-exect-llm-with-rules-family-ownership.md).
