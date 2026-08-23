# Gan cleaned request is the source-near ablation

Date: 2026-08-17
Revised: 2026-08-22 (codebook extract is the cited Gan row)
Status: current
Owner: [paper methods](../methods.md)
Related: [six-model roster](six-model-roster.md)

## Decision

The source-near Gan ablation is the cleaned structured-events
request (`gan_llm_extract_raw`): the same thirteen clinical
instructions as the earlier enveloped request, without the dataset
name, version string, or row index in the model-facing JSON. The
repair stack is unchanged.

This is not the cited paper Gan method. The cited row is cell 3:
`gan_llm_extract` extract, then rule encode and rule
select. See [six-model roster](six-model-roster.md).

The enveloped request is not this ablation either. Do not relabel those
cells. Do not cite Sol 381/450, or the rest of that panel, as the
paper hybrid.

Grok, Luna, and Gemini `dev750` on the cleaned request are on disk.
Grok cleaned `test450` is on disk (0.83). DeepSeek, Qwen, and
living Gemma on `dev750`, and the other five models on
aggregate-only `test450`, remain allowed blanks for this ablation
only.

## Why

The three dropped fields do not instruct extraction. A paper method
should not carry lab identity in the request. A rename of the
enveloped cells would describe the wrong call.

The codebook extract (`gan_llm_extract`) is the cited
Gan row because extract already writes the designed form. The
cleaned hybrid request keeps letter wording and scores lower; rule
encode and rule select recover most of the score. That trade is the
ablation story, not the headline method.

## Consequences

- New writing cites Gemini codebook cell-3 totals for headline tables.
  Grok cleaned `test450` (0.83) remains a companion locked total for
  the source-near ablation only. Do not wait on remaining
  `gan_llm_extract_raw` cells for the six-model table.
- Existing enveloped hybrid fills stay historical.
- Do not inspect `test450` rows.
- Do not invent the remaining cleaned-request holdout numbers.

## Claim boundary

A source-near ablation identity. Not the cited Gan method. Not
clinical validation. Holdout cells are aggregate-only.
