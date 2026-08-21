# Gemini is the cited model

Date: 2026-08-21
Status: current
Owner: [paper methods](../methods.md)
Roster: [six-model roster](six-model-roster.md)

## Decision

Gemini 3.7 Flash is the cited paper model. Tables and “the paper may
say” sentences use Gemini so the story stays on the method.

Grok 4.6 is a companion row, with GPT-5.6 Luna, DeepSeek V4 Flash
0731, Qwen 3.8 27B, and Gemma 4 26B. Existing Grok cells stay on
disk. They are not the cited row. Do not start new Sol live calls.

Later-stage model calls that replace rule encode or rule select —
`gan_llm_encode`, `gan_llm_select`, and the matching ExECT later-stage
calls — run on Gemini only, on both tasks. Do not start those calls
on Grok, Luna, DeepSeek, Qwen, or Gemma.

Rule replay of a saved extract raw (`llm_extract` / `llm_encode` /
`llm_select` stops) may still use any living model that already has
that raw. That is not a new later-stage call.

## Why

Gemini’s living extract / encode / select replay is in the same
band as Grok on the cells that exist, and it is the model that will
pay for the missing half of the equation: LLM encode and LLM select
on the same frozen extract. One cited model keeps the story on the
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
clinically better, or that later-stage LLM encode / select has been
run.
