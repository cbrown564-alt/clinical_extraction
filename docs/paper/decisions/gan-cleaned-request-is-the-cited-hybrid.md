# Gan cleaned request is the cited hybrid

Date: 2026-08-17
Status: current
Owner: [paper methods](../methods.md)

## Decision

The paper Gan LLM-with-rules method is the cleaned structured-events
request (`gan_llm_with_rules`): the same thirteen clinical
instructions as the earlier enveloped request, without the dataset
name, version string, or row index in the model-facing JSON. The
repair stack is unchanged.

The enveloped request is not this method. Do not relabel those
cells. Do not cite Sol 381/450, or the rest of that panel, as the
paper hybrid.

Grok, Luna, and Gemini `dev750` on the cleaned request are on disk.
Grok cleaned `test450` is on disk (0.83). DeepSeek, Qwen, and
living Gemma on `dev750`, and the other five models on
aggregate-only `test450`, remain allowed blanks.

## Why

The three dropped fields do not instruct extraction. A paper method
should not carry lab identity in the request. A rename of the
enveloped cells would describe the wrong call.

## Consequences

- New writing cites the Gemini cleaned-request cells where they
  exist. Grok cleaned `test450` (0.83) remains a companion
  locked total. Wait for the remaining models before a six-model
  holdout table.
- Existing enveloped hybrid fills stay historical.
- Do not inspect `test450` rows.
- Do not invent the remaining cleaned-request holdout numbers.

## Claim boundary

A paper-identity choice that requires new matched cells. Not
clinical validation. Holdout cells are aggregate-only.
