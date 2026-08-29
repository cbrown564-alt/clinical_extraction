# Gan cell-3 codebook roster replay

Date: 2026-08-28
Revised: 2026-08-29 (`last_event_well_since` promoted)
Status: completed
Protocol: [cell-3 codebook roster replay protocol](gan_cell3_codebook_roster_replay_protocol_2026-08-28.md)
Decision: [six-model roster](../../paper/decisions/six-model-roster.md)
Artifact: `paper_experiments/gan/rungs/{slug}/{split}/comparison.json`

## Question

When every living roster model is replayed on the same cell-3 stack
as the Gemini five-cell headline, what are the locked `test450`
find / encode / select Purist aggregates?

## Protocol

- Dataset: Gan 2026. Splits: `dev750` and aggregate-only `test450`.
- Saved extract: promoted `gan_llm_extract` raw. No new model calls.
- Living rungs: `raw_model` → `gan_rules_encode` →
  `llm_select_after_codebook` (includes `last_event_well_since`).
- Models: Gemini 3.7 Flash, Grok 4.6, GPT-5.6 Luna, DeepSeek V4
  Flash, Qwen 3.8 27B, Gemma 4 26B.
- Holdout rows were not inspected.

## Answer

The six-model table is the same cell-3 stack as the Gemini
headline. Gemini leads locked select after the well-since family.
Find and encode stops are unchanged from the prior codebook replay.

| Model | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 355 (0.789) | 360 (0.800) | **387 (0.860)** |
| Grok 4.6 | 355 (0.789) | 365 (0.811) | 384 (0.853) |
| DeepSeek V4 Flash | 334 (0.742) | 341 (0.758) | 369 (0.820) |
| GPT-5.6 Luna | 312 (0.693) | 332 (0.738) | 355 (0.789) |
| Qwen 3.8 27B | 315 (0.700) | 329 (0.731) | 343 (0.762) |
| Gemma 4 26B | 299 (0.664) | 307 (0.682) | 326 (0.724) |

Rules still raise every model over find. Luna still gains the
most letters (+43). Local models remain last. Historical
selected-evidence encode (Gemini 346 / 362) is the five-cell
ablation, not this roster.

`dev750` select: Grok **666**, Gemini **656**, DeepSeek **623**,
Luna **619**, Qwen **577**, Gemma **567**.

## Claim boundary

Holdout aggregate-only. No-call replay of a frozen stack. Not a new
architecture result. ExECT rungs were not changed.
