# Protocol: promote `last_event_well_since`

Date: 2026-08-29
Status: complete; living rungs and Table 1 refreshed
Owner: this file
Prior: [accept protocol](gan_last_event_well_since_protocol_2026-08-29.md)

## Primary question

After the dest750 accept and the `test450` aggregate confirmation,
does promoting the living select family require refreshing the
cited Gan cell-3 paper surfaces?

## Scope

- Candidate: living `llm_select_after_codebook` with
  `last_event_well_since` default on. No new model calls.
- Dataset: Gan `dev750` and aggregate-only `test450`.
- Models: the six-model roster. Gemini five-cell cell 3 uses the
  same replay. Cell 1 / cell 5 / standalone rules are unchanged.
- `test450` remains aggregate-only. No holdout row inspection.
- Cited Table 1 cell 3 moves from the curated 373 / living 374
  pair onto this replay. Do not keep a one-count gap.

## Stop rule

Write rung `comparison.json` (and dest750 `scored.jsonl`) for all
six models on both splits. Refresh Gemini class-report aggregates,
paired-test aggregates, living figures, and the results draft.
Holdout artifacts stay comparison-only.

## Measured

No-call replay of saved `gan_llm_extract` raws. Gemini cell 3
`test450` **387 / 396**. Cell 4 `llm_select_only` **382 / 391**.
Six-model holdout Purist select: Gemini 387, Grok 384, DeepSeek
369, Luna 355, Qwen 343, Gemma 326. `dev750` Gemini select 656.
Paired cell 3 vs rules 99 vs 37, *p* = 1.0×10⁻⁷; vs cell 5 40 vs
10, *p* = 2.4×10⁻⁵.

## Claim boundary

Promoted living cell-3 select. Still codebook find plus rule
encode plus rule select. Not a new architecture. ExECT unchanged.
