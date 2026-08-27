# Gemini is the cited model

Date: 2026-08-21
Revised: 2026-08-22 (six-model row is cell 3)
Status: current
Owner: [paper methods](../methods.md)
Roster: [six-model roster](six-model-roster.md)

## Decision

Gemini 3.7 Flash is the cited paper model. Tables and “the paper may
say” sentences use Gemini so the story stays on the method.

The six-model comparison is cell 3 (LLM recognise, rules encode, rules
select). Companion rows exist only for that row. Existing Grok and
other leftover recognise raws stay on disk as ablations or history. They
are not the cited row. Do not start new Sol live calls.

Later-stage model calls that replace rule encode or rule select —
`gan_llm_encode`, `gan_llm_select`, and the matching ExECT later-stage
calls — run on Gemini only, on both tasks. Do not start those calls
on Grok, Luna, DeepSeek, Qwen, or Gemma.

Rule replay of a saved recognise raw (`llm_extract` / `llm_encode` /
`llm_select` stops) may still use any living model that already has
that raw. That is not a new later-stage call.

## Why

Gemini’s living recognise / encode / select replay is in the same
band as Grok on the cells that exist, and it is the model that will
pay for the missing half of the equation: LLM encode and LLM select
on the same frozen recognise raw. One cited model keeps the story on the
method. Restricting those new calls to Gemini keeps cost and
attribution on the cited row.

## Consequences

- Roster order starts with Gemini. `method_identity` is Gemini.
- New writing cites Gemini locked totals where they exist. Companion
  rows may appear beside them. Do not invent missing Gemini cells.
- A protocol for later-stage LLM encode / select names Gemini, Gan
  and ExECT, and no other living model.
- Luna remains the Gan pre-post development iterator. That does not
  make Luna the cited model, and it does not authorise Luna
  later-stage encode / select calls.

## Claim boundary

A paper-identity and allowed-run choice. Not a claim that Gemini is
clinically better. Gan and ExECT later-stage encode and select have
been run and promoted for Gemini.
