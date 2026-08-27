# Inexact-span family-rewrite block

Date: 2026-08-15
Status: landed; living Qwen Gan test450 fill promoted to 361/450
Protocol: recovered from git history; this report is the answer.
Parent: [Qwen rescue overfiring audit](qwen_rescue_overfiring_2026-08-15.md)
Artifact: [`experiments/gan2026_inexact_span_family_rewrite_test450_20260815.json`](../../experiments/gan2026_inexact_span_family_rewrite_test450_20260815.json)
Rebuild: removed in the 2026-08-16 scripts prune; recover from git history (`scripts/check_gan2026_inexact_span_family_rewrite_test450.py`)

## Plain answer

Evidence reconcile now splits two jobs. Format / same-family render may
still use a paraphrased quote. Changing a parsed clinical family
(unknown ↔ frequency ↔ seizure-free, and other parsed-kind changes)
requires an exact source span.

On matched v0.5 locked `test450` (aggregate-only, no row inspection):
Sol, Gemini, Luna, DeepSeek 0731, and Gemma are unchanged. Qwen moves
**364 → 361 Purist (−3)** and 384 → 380 Pragmatic. Pooled six-model
delta is −3. Living fills now carry Qwen **361/450**. Decision 0050
policy is unchanged.

Matched v0.5 `dev750` raws for Qwen / Sol / Luna / DeepSeek / Gemma are
not on this checkout (`scratch/validation/gan2026_matched_v05_dev750_20260727/`
is absent). Gemini and the June 07 mini v0.5 cells are the available
development remasure sources. July 18 v0.7 is no longer an audit source
(Decision 0043).

## What changed

`blocks_inexact_span_family_rewrite` in
`selected_evidence_derivation.py`, applied from
`repair_prediction_label_with_evidence` after
`should_prefer_selected_evidence_label` would accept the derived label.

No model-specific branch. Unparsed source-near labels still render.

## Holdout (aggregate only)

Same v0.5 sidecars as the current-stack fills. Zero new calls.

| Model | Published Purist | HEAD Purist | Δ |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 374 | 374 | 0 |
| GPT-5.6 Luna | 366 | 366 | 0 |
| GPT-5.6 Sol | 381 | 381 | 0 |
| DeepSeek V4 Flash 0731 | 366 | 366 | 0 |
| Qwen 3.6:35B | 364 | 361 | −3 |
| Gemma 4 26B | 360 | 360 | 0 |

## Claim boundary

Model-agnostic semantic gate on evidence reconcile. Holdout is
aggregate-only. Not a paper performance rewrite. Not authorization to
inspect the three Qwen holdout cells. Restoring the missing v0.5
`dev750` tree is required before a same-prompt six-model development
remasure.
