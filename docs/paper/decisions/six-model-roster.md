# Six-model roster

Date: 2026-08-17
Revised: 2026-08-21 (Gemini is the cited model)
Status: current
Owner: [paper methods](../methods.md)
Roster: [`paper_experiments/roster.json`](../../../paper_experiments/roster.json)
Cited-model decision: [Gemini is the cited model](gemini-is-the-cited-model.md)

## Decision

Every living comparison uses these six models, in this order:

1. Gemini 3.7 Flash (cited model)
2. Grok 4.6
3. GPT-5.6 Luna
4. DeepSeek V4 Flash 0731
5. Qwen 3.8 27B
6. Gemma 4 26B

Historical, not living: GPT-5.6 Sol, GPT-4.1-mini, DeepSeek
pre-0731, Qwen 3.6:35B, Compact dump.

Gemini 3.7 Flash is the cited model so the story stays on the method.
The other five are companion rows. Sol is historical and is not a
paper cell. Do not treat a missing cell as a score.

Later-stage LLM encode and LLM select calls are Gemini only. See
[Gemini is the cited model](gemini-is-the-cited-model.md).

## Why

One roster, every time. Mixing retired slots into a living table
makes the comparison unreadable. Citing one model keeps the story
on extract / encode / select, not on a model bake-off.

## Consequences

- New runs use these slugs and routes. Do not start new Sol live
  calls. Do not keep Sol fills as paper cells.
- Qwen 3.6 remains only as a Full-ledger historical local slot
  until Compact Qwen and cleaned Gan Qwen land.
- Gan LLM-only is a six-model table. Qwen 3.8 LLM-only is an
  allowed blank. It is not a later-stage encode / select call.
- DeepSeek V4 Flash is run with thinking on and thinking off.
  Living Compact is the thinking-on (provider-default) cell.
  Thinking-off is a rerun, not a replacement, until compared.
