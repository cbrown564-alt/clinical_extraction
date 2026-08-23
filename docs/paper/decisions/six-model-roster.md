# Six-model roster

Date: 2026-08-17
Revised: 2026-08-22 (cell 3 only)
Status: current
Owner: [paper methods](../methods.md)
Roster: [`paper_experiments/roster.json`](../../../paper_experiments/roster.json)
Cited-model decision: [Gemini is the cited model](gemini-is-the-cited-model.md)

## Decision

The six-model comparison is **cell 3 only** on both tasks: LLM
extract, rules encode, rules select.

1. Gemini 3.7 Flash (cited model)
2. Grok 4.6
3. GPT-5.6 Luna
4. DeepSeek V4 Flash 0731
5. Qwen 3.8 27B
6. Gemma 4 26B

Gan extract is `gan_llm_extract`. ExECT extract is
`exect_llm_extract` (inventory prompt, 4-family micro F1). Encode and
select are the recorded rule stacks replayed on that raw.
`exect_llm_extract_filtered` is the Compact extract ablation, Gemini
only.

Headline five-cell tables stay Gemini. Later-stage LLM encode and
LLM select stay Gemini only. Gemini thinking low / medium / high
is a cell-3 extract ablation, not a roster table.

`gan_llm_extract_raw` and `gan_llm_only` are ablations or historical
cells. They are not the six-model comparison.

Historical, not living: GPT-5.6 Sol, GPT-4.1-mini, DeepSeek
pre-0731, Qwen 3.6:35B, Compact dump. Sol is not a paper cell.

## Why

Cell 3 is the same method on both tasks: one extract call, then
fixed rules. That is the only row that can carry six models without
paying for later-stage encode or select on the roster. ExECT cell 4
stays Gemini-only. On the inventory extract, cell 3 is also the
Gemini peak.

## Consequences

- New roster runs are cell-3 extracts plus rule replay. Do not start
  six-model later-stage encode or select. Do not start new Sol calls.
- Do not treat `gan_llm_only` or source-near `gan_llm_extract_raw`
  as the six-model table.
- Living DeepSeek is thinking enabled at `reasoning_effort=low`,
  the same living effort as Gemini, Grok, and Luna. Thinking-off
  is a DeepSeek-only toggle, not the Gemini medium/high ablation.
