# ExECT LLM with rules is the both-recognise alias

Date: 2026-08-17
Revised: 2026-08-23 (cited recognise is `exect_llm_extract`; cited score is 4-family micro F1)
Status: current
Owner: [paper methods](../methods.md)
Related: [six-model roster](six-model-roster.md)

## Decision

The both-recognise ExECT call is `exect_llm_pre_post` (cell 2): living
`exect_llm_extract` plus suggested candidates in the prompt, then the
same rule encode and rule select stack as cell 3. The live alias is
`exect_llm_with_rules`.

This is not the cited paper ExECT method. The cited row is cell 3:
`exect_llm_extract` recognise, then rule encode and rule select. The
cited score is **4-family micro F1** (`clinical_inventory_unit_keys`).
See [six-model roster](six-model-roster.md).

Compact and E5 are lineage labels for this alias and for the old
hybrid recognise path. The Compact recognise ablation runner is
`exect_llm_extract_filtered`. Do not cite Compact, E5, Compact/
headline F1, `clinical_headline_unit_keys`, or hybrid F1 as the
current cited recognise or score. The retired Compact cell 2–5 select
stops (0.8031 / 0.8161 / 0.8173 / 0.7954) are lineage only. Do not
relabel those cells as the paper method.

Full ledger (`exect_full_ledger`) is the only comparison/control
method when cited. It is not a headline paper method. Do not present
Full-ledger scores as peer columns. Grok has no Full ledger cell.

## Why

The both-recognise call keeps letter wording and scores lower than
LLM recognise alone; rule encode and rule select recover most of the
score. That trade is the ablation story, not the headline method.

Compact was the earlier cited hybrid recognise path. The living cited
recognise is inventory `exect_llm_extract` and the cited score is
4-family micro F1. Compact/headline F1 remains historical lineage,
not the current headline metric.

The paper should cite the method we run for headline tables: LLM
recognise (`exect_llm_extract`), then fixed rules, scored on 4-family
micro F1. Gemini five-cell grids carry the headline totals (peak
cell 3 = 0.8674 on `test60`; five select stops 0.77 / 0.86 / 0.87 /
0.86 / 0.85 at two decimals).

## Consequences

- New writing cites Gemini cell-3 totals on 4-family micro F1 for
  headline tables and Gemini five-cell grids for the cited score. Do
  not wait on `exect_llm_with_rules` cells for the six-model table.
- Do not compare 4-family micro F1 to Compact/headline F1 as if they
  shared a denominator.
- Full ledger numbers stay as the named control when cited.
- Do not inspect `test60` rows.
- Do not invent Qwen numbers for either recognise identity.
- Tracked replay files live under `paper_experiments/`.

## Claim boundary

A both-recognise alias identity. Not the cited ExECT method. Not
clinical validation and not the published ExECT benchmark. Holdout
cells are aggregate-only.
