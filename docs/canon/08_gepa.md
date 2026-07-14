# 08 — GEPA negative comparison

Last updated: 2026-07-14

The selected ExECT LLM-only run is one GEPA-optimized GPT-4.1-mini program on
dev140.

| Measure | Result |
| --- | ---: |
| Clinical fact F1 (`clinical_headline`) | 0.7393 |
| Strict benchmark item F1 | 0.1356 |
| Current LLM-with-rules result (`v08`) | 0.9189 |

This is a negative development comparison. It used an optimizer-only
development subset and is not a published-benchmark or production result. The
selected files retain the exact instruction, predictions, summary, entry point,
metric, adapter, scorer, and tests needed for replay.

Do not claim that LLM only matches the combined method or that this historical
search establishes a limit for all models.
