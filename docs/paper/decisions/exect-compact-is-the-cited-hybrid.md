# ExECT LLM with rules is the both-extract alias

Date: 2026-08-17
Revised: 2026-08-23 (cited extract is `exect_llm_extract`)
Status: current
Owner: [paper methods](../methods.md)
Related: [six-model roster](six-model-roster.md)

## Decision

The both-extract ExECT call is `exect_llm_pre_post`. The live alias
is `exect_llm_with_rules`: one structured call with candidates in
the prompt, then the same rule encode and rule select stack as cell 3.

This is not the cited paper ExECT method. The cited row is cell 3:
`exect_llm_extract` extract, then rule encode and rule select. See
[six-model roster](six-model-roster.md).

Compact and E5 are lineage labels for this alias. Do not cite them as
the headline hybrid. Do not relabel those cells as the paper method.

Full ledger (`exect_full_ledger`) is the only comparison/control
method when cited. It is not a headline paper method. Do not present
Full-ledger scores as peer columns. Grok has no Full ledger cell.

## Why

The both-extract call keeps letter wording and scores lower than
LLM extract alone; rule encode and rule select recover most of the
score. That trade is the ablation story, not the headline method.

The paper should cite the method we run for headline tables: LLM
extract, then fixed rules. Gemini five-cell grids carry the headline
totals.

## Consequences

- New writing cites Gemini cell-3 totals for headline tables and
  Gemini five-cell grids for the cited score. Do not wait on
  `exect_llm_with_rules` cells for the six-model table.
- Full ledger numbers stay as the named control when cited.
- Do not inspect `test60` rows.
- Do not invent Qwen numbers for either extract identity.
- Tracked replay files live under `paper_experiments/`.

## Claim boundary

A both-extract alias identity. Not the cited ExECT method. Not
clinical validation and not the published ExECT benchmark. Holdout
cells are aggregate-only.
