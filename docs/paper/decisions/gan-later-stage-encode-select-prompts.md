# Gan later-stage encode and select prompts

Date: 2026-08-21
Revised: 2026-09-02 (local same-model select-from-extract is transfer-only)
Status: current
Owner: [paper methods](../methods.md)
Related: [Gemini is the cited model](gemini-is-the-cited-model.md)

## Decision

On the codebook find (`gan_llm_extract`), the Gemini
**LLM** row has no separate encode call. Find already writes the
designed form. Encode is that same cell. Select is
`gan_llm_select_from_extract`: it reads find events, their quotes,
and the find pick, not a later-stage encode ledger and not the letter.

`gan_llm_encode` and encode-then-`gan_llm_select` remain runnable
ablations. They are not the LLM row. They do not re-read the letter.

Select from find uses the same select prompt as encode-then-select.
It may write a new label only when no single event is the answer.
The living prompt may use event quotes under the same current-state
policies as living rule select: usual spacing, usual rate versus a
year total, recent count after a quiet spell, not epileptic (write
`seizure free for multiple year`), month list with the diary
keep-guards, dated sequence without a day or week overwrite, burst
after a change, and a short quiet spell after a last event (under
6 months; 5 weeks or less becomes per month). It still has no
letter, so it cannot apply the dated-sequence clinic-date gate.
After the call, only join and projection run.
Cited cell 5 is this living prompt
(`gan_llm_select_policy_examples`) on both splits: `test450`
383/450 and `dev750` 640/750.

## Why

Later-stage encode never sees find `final_label`. It rewrites from
`raw_value` without the letter and drops the codebook answer
(0.78 → 0.69 on `dev750`). Select from find is 0.79 versus 0.79 after
that encode. A separate encode stage is not worth a column.

The source-near `gan_llm_extract_raw` ledger still needs a form-writing
step if that ablation is cited. Rules after find still encode.

## Claim boundary

A prompt and ownership contract. Later-stage LLM encode and
encode-then-select stay Gemini only. Same-model
`gan_llm_select_from_extract` may run on living local slugs
(`qwen38_27b`, `gemma4_26b`) as transfer evidence; that run is not
cited cell 5. Headline tables cite the codebook find row and Gemini
select. The source-near `gan_llm_extract_raw` ledger may still cite
form-writing encode for that ablation only. This select is not
hybrid select.
