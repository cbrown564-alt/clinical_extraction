# Gan later-stage encode and select prompts

Date: 2026-08-21
Revised: 2026-08-22 (codebook extract absorbs encode)
Status: current
Owner: [paper methods](../methods.md)
Related: [Gemini is the cited model](gemini-is-the-cited-model.md)

## Decision

On the codebook extract (`gan_llm_extract_label_forms`), the Gemini
**LLM** row has no separate encode call. Extract already writes the
designed form. Encode is that same cell. Select is
`gan_llm_select_from_extract`: it reads extract events and the
extract pick, not a later-stage encode ledger.

`gan_llm_encode` and encode-then-`gan_llm_select` remain runnable
ablations. They are not the LLM row. They do not re-read the letter.

Select from extract uses the same select prompt as encode-then-select.
It may write a new label only when no single event is the answer.
It cannot do the note-derived hybrid families. After the call, only
join and projection run.

## Why

Later-stage encode never sees extract `final_label`. It rewrites from
`raw_value` without the letter and drops the codebook answer
(0.78 → 0.69 on `dev750`). Select from extract is 0.79 versus 0.79 after
that encode. A separate encode stage is not worth a column.

The source-near `gan_llm_with_rules` ledger still needs a form-writing
step if that ablation is cited. Rules after extract still encode.

## Claim boundary

A prompt and ownership contract. The published Gemini grid still cites
the `gan_llm_with_rules` later-stage cells until the codebook row is
promoted. This select is not hybrid select.
