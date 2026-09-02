# Gan cell-3 codebook roster replay protocol

Date: 2026-08-28
Status: completed 2026-08-28
Owner: this file
Result: [cell-3 codebook roster replay](gan_cell3_codebook_roster_replay_2026-08-28.md)

## Question

When every living roster model is replayed on the same cell-3 stack
as the Gemini five-cell headline — `gan_llm_extract`, then
`gan_rules_encode`, then `llm_select_after_codebook` — what are the
locked `test450` find / encode / select Purist aggregates?

## Why it matters

The six-model comparison is defined as cell 3 only. The Gemini
five-cell select stop for that cell is codebook encode then rule
select (**0.83**, 373/450). The living rung artifacts still replay
historical selected-evidence encode (`llm_encode`) then historical
select (`llm_select`). For Gemini that select is **0.804** (362/450).
Those are not the same method. The roster table cannot cite cell 3
until the rungs use the codebook stack.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Splits | `dev750` (review permitted) and `test450` (aggregate only) |
| Row policy | No new model calls. Replay saved `gan_llm_extract` raw. |
| Holdout | Do not inspect rows. Do not dump failure ids or letter text. |
| Models | Gemini 3.7 Flash, Grok 4.6, GPT-5.6 Luna, DeepSeek V4 Flash, Qwen 3.8 27B, Gemma 4 26B |
| Scorer | Purist micro-F1 (primary); Pragmatic companion |

Do not retune prompts, rules, or temperature from holdout aggregates.

## Candidate

Living Gan rungs:

- find: `raw_model`
- encode: `gan_rules_encode`
- select: `llm_select_after_codebook`

Historical `llm_encode` / `llm_select` remain the five-cell
`historical_encode_ablation` and are not the roster.

## Comparator

The current `paper_experiments/gan/rungs/{slug}/{split}/comparison.json`
selected-evidence rungs. Gemini five-cell cell 3 is the Gemini
alignment check: encode should match codebook encode, select should
match codebook-then-select.

## Stop rule

Answer when all six models have codebook rungs on both splits and
Gemini `test450` select matches the cited cell-3 codebook select
(373/450, or the living no-call replay of that same stack). Negative
if a model lacks saved extract raw. Do not start new calls in this
study.

## Claim boundary

Holdout evidence is aggregate-only. This is a no-call replay of a
frozen stack, not a new architecture result. ExECT rungs are
unchanged.
