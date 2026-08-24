# Living comparison contract

Date: 2026-08-24
Status: current
Owner: [paper methods](../methods.md)
Code: [`src/clinical_extraction/paper/comparison_contract.py`](../../../src/clinical_extraction/paper/comparison_contract.py)

## Decision

Every new living paper cell writes one envelope. The cited number is
the **select** stop. Extract and encode are prior-stage scores on the
same raw. Gan uses Purist. ExECT uses 4-family micro F1
(`clinical_inventory_unit_keys`).

Required identity: `task`, `method`, `cell`, `model_slug`, `split`,
`row_policy`, `scorer`, `prompt_version`, `replay_mode`,
`headline` (`select`). Required stages: `extract`, `encode`,
`select`. Each stage carries the cited metric and counts.

Living ExECT cells must not use `hybrid_headline_f1` or
`four_family_headline_f1` as the primary field. Those names remain
readable on historical Compact files through an adapter.

`gan_llm_only`, `gan_llm_extract_raw`, and
`exect_llm_extract_filtered` stay callable as ablations
(`cell: ablation`). They are not five-cell or six-model columns.

Holdout stays aggregate-only. Do not rewrite cited Compact,
source-near, or provider-default comparisons. Read them with the
adapter.

## Why

Live runners still emit one hybrid Purist or a `headline_f1` field
while the scorer is inventory. Replay-rungs still start from Compact
or source-near raws. The paper table cannot be assembled from those
shapes without renaming.

## Consequences

- `python -m clinical_extraction.paper run` attaches the envelope.
- `replay-rungs` defaults to `gan_llm_extract` / `exect_llm_extract`.
- `write-five-cell` builds the Gemini headline grid from living cells.
- Development panels read stage stops, not Compact `clinical_fact_f1`
  as the living primary.
