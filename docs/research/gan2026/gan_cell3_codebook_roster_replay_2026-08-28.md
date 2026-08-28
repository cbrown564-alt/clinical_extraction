# Gan cell-3 codebook roster replay

Date: 2026-08-28
Status: completed
Protocol: [cell-3 codebook roster replay protocol](gan_cell3_codebook_roster_replay_protocol_2026-08-28.md)
Decision: [six-model roster](../../paper/decisions/six-model-roster.md)
Artifact: `paper_experiments/gan/rungs/{slug}/{split}/comparison.json`

## Question

When every living roster model is replayed on the same cell-3 stack
as the Gemini five-cell headline, what are the locked `test450`
recognise / encode / select Purist aggregates?

## Protocol

- Dataset: Gan 2026. Splits: `dev750` and aggregate-only `test450`.
- Saved extract: promoted `gan_llm_extract` raw. No new model calls.
- Living rungs: `raw_model` → `gan_rules_encode` →
  `llm_select_after_codebook`.
- Models: Gemini 3.7 Flash, Grok 4.6, GPT-5.6 Luna, DeepSeek V4
  Flash, Qwen 3.8 27B, Gemma 4 26B.
- Holdout rows were not inspected.

## Answer

The six-model table is now the same cell-3 stack as the Gemini
headline. Grok still leads on locked select. Gemini’s living select
is 374/450, the same no-call codebook replay already recorded beside
Table 1’s curated 373/450.

| Model | Recognise | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 355 (0.789) | 360 (0.800) | 374 (0.831) |
| Grok 4.6 | 355 (0.789) | 365 (0.811) | **377 (0.838)** |
| DeepSeek V4 Flash | 334 (0.742) | 341 (0.758) | 358 (0.796) |
| GPT-5.6 Luna | 312 (0.693) | 332 (0.738) | 350 (0.778) |
| Qwen 3.8 27B | 315 (0.700) | 329 (0.731) | 339 (0.753) |
| Gemma 4 26B | 299 (0.664) | 307 (0.682) | 323 (0.718) |

Rules still raise every model over recognise. Luna still gains the
most letters (+38). Local models remain last. Historical
selected-evidence encode (Gemini 346 / 362) is the five-cell
ablation, not this roster.

## Claim boundary

Holdout aggregate-only. No-call replay of a frozen stack. Not a new
architecture result. Do not retune from the Gemini 373 versus 374
gap. ExECT rungs were not changed.
