# Gan codebook-extract holdout protocol

Date: 2026-08-22
Status: completed 2026-08-22
Result: [five-cell grid](gan_five_cell_grid_2026-08-22.md)
Owner: this file

## Question

What are the locked `test450` aggregates for the formalized Gemini
LLM row (extract = encode, select from extract) and for Rules then
LLM with `label_forms`?

## Why it matters

Development already chose the codebook extract and dropped a
separate LLM encode call. Holdout is required before those cells
can replace the published Gemini grid.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Split | `test450` aggregate only |
| Row policy | Do not inspect rows. Do not dump failure ids. |
| Model | Gemini 3.7 Flash |
| Scorer | Purist; secondary Pragmatic and scorable count |
| Prompts | Frozen. Do not retune `label_forms`. |

## Candidate arms

1. **LLM extract / encode** — `gan_llm_extract` at
   extract stop. Same score in both columns. Reuse the existing
   frozen scratch cell if it is complete; do not pay for a second
   extract draw.
2. **LLM select** — `gan_llm_select_from_extract` on that extract
   ledger. Fresh call. No encode work cell. No hybrid post-stack.
3. **Cell 4** — no-call `llm_select_only` on the frozen extract
   raw. Aggregate only.
4. **Rules then LLM** — fresh `gan_llm_and_rules_extract`, then
   no-call rule encode/select on that raw (`note_text` on).
   Aggregate only.

## Fixed comparators

- Source-near ablation grid on `gan_llm_extract_raw` (not the cited
  five-cell table). No-forms `gan_llm_pre_post` is retired.
- Do not overwrite those ablation cells
- Do not run later-stage `gan_llm_encode` or encode-then-select

## Stop rule

Stop after the three aggregates and the pre-post rule-stop
aggregates are written. Do not promote `claims.md` in this cut.
Do not inspect holdout rows.

## Claim boundary

Frozen-prompt holdout aggregates. Not a paper column until
promoted.
