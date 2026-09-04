# Protocol: Local same-model policy-example select on Gan `dev750`

Date: 2026-09-03
Status: complete
Report: [result](gan_llm_select_policy_examples_local_dev750_2026-09-04.md)
Owner: this file
Guardrail: `gan2026-scoring-guardrail`;
[later-stage select](../../paper/decisions/gan-later-stage-encode-select-prompts.md)
Related holdout: [test450 transfer](gan_llm_select_policy_examples_local_test450_2026-09-03.md)

## Primary question

Why does living policy-example select lower Purist versus each local
model's own codebook find?

On sealed `test450` the drop was −21 for both Qwen 3.8 27B (315 → 294)
and Gemma 4 26B (299 → 278). This protocol repeats the same second
call on inspectable `dev750` so changed rows can be read.

## Why this matters

Cited Gemini cell 5 uses this select prompt. If local select harms
the find pick, the living prompt or the local models' extract
ledgers are the mechanism — not a holdout-only accident. Development
review can separate: overwrite of a correct find pick, a written
label that is wrong, parse/projection loss, or a rare rescue.

## Frozen candidate

- Find ledger: saved `gan_llm_extract` rows for the same slug
- Select: living `build_llm_select_prompt_input`
  (`gan_llm_select_policy_examples`)
- Method: `gan_llm_select_from_extract`
- No later-stage encode; no letter reread; no hybrid post-stack
- Models: `qwen38_27b` then `gemma4_26b` (one resident model)
- Work cells:
  `experiments/paper/gan_llm_select_from_extract/<slug>/gan_llm_extract/dev750`
- Call transport: local sync

## Fixed comparators

| Cell | Purist |
| --- | ---: |
| Qwen codebook find `dev750` | **505**/750 |
| Gemma codebook find `dev750` | **501**/750 |
| Same-model select `test450` (Qwen / Gemma) | 294 / 278 of 450 |

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `dev750` (machine `validation`) |
| Row policy | `development_review_permitted` |
| Scorer | Purist primary; Pragmatic secondary |
| Holdout | Do not open `test450` rows |

## Required analysis

After both work cells finish:

1. Aggregate Purist / Pragmatic / scorable versus each find stop.
2. Changed-row counts: select rescues a find miss; select harms a
   find hit; both wrong; both right with a different label.
3. On a small permitted sample of harm and rescue rows, attribute
   the first component that changed the answer: pick overwrite,
   written label, parse/projection, or extract-ledger quality.
4. Do not retune the living select prompt from these rows in this
   protocol. Stop at a mechanism reading.

## Stop rule

Answer if the same −direction appears and the changed-row sample
names one dominant mechanism. Negative if select is flat or up.
Revise if instrumentation cannot pair find and select on the same
`source_row_index`. Do not promote. Do not touch `test450`.

## Claim boundary

Development mechanism reading. Not Table 1. Not cited cell 5. Not
holdout evidence.
