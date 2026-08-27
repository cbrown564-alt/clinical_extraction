# 0051: Gemini 3.7 Flash succeeds GPT-4.1-mini in the next six-model roster

Date: 2026-08-13
Status: accepted for new six-model calls; not a score promotion
Amends: the live roster named by
[decision 0039](0039-final-exect-six-model-roster.md)
Does not change: [decision 0050](0050-current-stack-hybrid-primary-fills.md)
fills, Decision 0046 method identity, Decision 0043 v0.5 prompt identity,
or any retained GPT-4.1-mini artifact

## Decision

New six-model comparison calls use this closed-weight lineup:

| Slot | Model condition | Route |
| --- | --- | --- |
| Small closed | GPT-5.6 Luna | Hosted OpenAI |
| Medium closed | **Gemini 3.7 Flash** | Hosted Gemini (`gemini/gemini-3.7-flash`) |
| Large closed | GPT-5.6 Sol | Hosted OpenAI |

The three open-weight conditions stay DeepSeek V4 Flash (hosted), Qwen 3.6:35B
(local), and Gemma 4 26B (local). Qwen 3.8 27B is reserved as a later
open-weight successor and is not available to this roster.

GPT-4.1-mini remains the completed Decision 0039 / Decision 0050 closed-weight
small/medium overlap cell. It is historical evidence, not a live successor
condition. Do not rewrite its scores as Gemini scores.

## Why

Decision 0039 placed two small closed models (GPT-4.1-mini and Luna) beside
Sol. Gemini 3.7 Flash is a current hosted Flash model and fills a single
medium closed slot, so the closed line is Luna / Gemini / Sol.

## Runtime identity

- Identifier: `gemini/gemini-3.7-flash`
- Transport: Google's OpenAI-compatible Gemini endpoint
  (`https://generativelanguage.googleapis.com/v1beta/openai/`)
- Credential: `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- Thinking: declared `reasoning_effort=low`. A 10-letter ExECT `dev140`
  raw-lane check found `medium` slightly higher F1 from Diagnosis precision
  and worse recall (inventory drops). `low` is the selected live condition
  because it matches the existing model-led inventory style. `minimal` is
  rejected by the model. Thinking cannot be turned off.
- Temperature: `0`
- Output cap: 16,000 tokens unless a later protocol amends it
- Cache: disabled on live comparison calls

Adapters may repair transport or output shape only. A semantic prompt,
clinical repair, scorer, split, or component-graph change is a new condition.

## Claim boundary

This decision authorizes wiring and new development calls under a
predeclared protocol. It does not create Gemini benchmark scores, does not
inspect locked holdout rows, and does not let a successor cell inherit
GPT-4.1-mini numbers. Promotion to selected six-model fills requires a later
measurement decision after the protocol completes.

## Owners

- Protocol:
  [six-model Gemini successor](../research/shared/six_model_gemini37flash_successor_protocol_2026-08-13.md)
- Machine roster: `src/clinical_extraction/core/six_model_roster.py`
- ExECT config: `configs/exectv2/six_model_comparison/gemini37flash_dev140.json`
- Gan config: `configs/gan2026/six_model_successor_gemini37flash_20260813.json`
- Gan LLM-only cells:
  [protocol](../research/gan2026/gemini37flash_llm_only_dev750_test450_protocol_2026-08-13.md),
  [report](../research/gan2026/gemini37flash_llm_only_dev750_test450_2026-08-13.md)
