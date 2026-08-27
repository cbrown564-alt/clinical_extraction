# Six-model roster

Date: 2026-08-17
Revised: 2026-08-23 (ExECT cited score is 4-family micro F1)
Status: current
Owner: [paper methods](../methods.md)
Roster: [`paper_experiments/roster.json`](../../../paper_experiments/roster.json)
Cited-model decision: [Gemini is the cited model](gemini-is-the-cited-model.md)

## Decision

The six-model comparison is **cell 3 only** on both tasks: LLM
recognise, rules encode, rules select.

1. Gemini 3.7 Flash (cited model)
2. Grok 4.6
3. GPT-5.6 Luna
4. DeepSeek V4 Flash 0731
5. Qwen 3.8 27B
6. Gemma 4 26B

Gan recognise is `gan_llm_extract`. ExECT recognise is
`exect_llm_extract` (inventory prompt, 4-family micro F1). Encode and
select are the recorded rule stacks replayed on that raw.
`exect_llm_extract_filtered` is the Compact recognise ablation, Gemini
only.

Headline five-cell tables stay Gemini. On ExECT they score 4-family
micro F1 (`clinical_inventory_unit_keys`); Compact/headline F1 is
not the cited metric. Later-stage LLM encode and LLM select stay
Gemini only. Gemini thinking low / medium / high is a cell-3 recognise
ablation, not a roster table.

`gan_llm_extract_raw` and `gan_llm_only` are ablations or historical
cells. They are not the six-model comparison.

Historical, not living: GPT-5.6 Sol, GPT-4.1-mini, DeepSeek
pre-0731, Qwen 3.6:35B, Compact dump. Sol is not a paper cell.

## Why

Cell 3 is the same method on both tasks: one recognise call, then
fixed rules. That is the only row that can carry six models without
paying for later-stage encode or select on the roster. ExECT cell 4
stays Gemini-only. On 4-family micro F1, cell 3 is the Gemini peak
(0.8674 on `test60`). All six ExECT `exect_llm_extract` roster cells
are promoted on `dev140` and aggregate-only `test60`; cite those
inventory select stops in the six-model table, not Compact/headline
`exect_llm_only` replays.

## Consequences

- New roster runs are cell-3 recognises plus rule replay. Do not start
  six-model later-stage encode or select. Do not start new Sol calls.
- Do not treat `gan_llm_only` or source-near `gan_llm_extract_raw`
  as the six-model table.
- Cite ExECT roster totals from promoted
  `paper_experiments/exect/exect_llm_extract/{slug}/test60/`
  (4-family micro F1). Do not substitute Compact/headline
  `exect_llm_only` for that table.
- Living DeepSeek is thinking enabled at `reasoning_effort=low`,
  the same living effort as Gemini, Grok, and Luna. Thinking-off
  is a DeepSeek-only toggle, not the Gemini medium/high ablation.
