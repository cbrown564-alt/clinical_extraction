# Gemini 3.7 Flash cell 3 at temperature 1

Date: 2026-08-28
Revised: 2026-08-28 (codebook cell-3 rescore)
Status: complete (not promoted)
Protocol: [temperature-1 both splits](gan_gemini37flash_temperature_1_protocol_2026-08-28.md)
Owner: this file
Cited comparator: living Gemini codebook rungs at temperature 0
([cell-3 codebook roster](gan_cell3_codebook_roster_replay_2026-08-28.md))

## Living default

Gemini temperature stays **0.0**. This file is the non-living
temperature-1 ablation. It is not promoted.

## Stack

Cell 3 is LLM find (`gan_llm_extract`), then `gan_rules_encode`,
then `llm_select_after_codebook`. The first write of this report
scored temperature-1 select with historical `llm_select` (363/450,
650/750). That is not cell 3. The table below is a no-call codebook
replay of the same temperature-1 raws.

Historical `llm_encode` / `llm_select` aggregates remain in
`comparison_historical_llm_encode.json` beside the living rung
files.

## Shift versus living Gemini cell 3 (temperature 0.0)

| Split | Stop | Temp. 0.0 (living) | Temp. 1.0 | Δ |
| --- | --- | ---: | ---: | ---: |
| `test450` | Find | 0.789 (355/450) | 0.778 (350/450) | **−5** |
| `test450` | Encode | 0.800 (360/450) | 0.793 (357/450) | **−3** |
| `test450` | Select | 0.831 (374/450) | 0.824 (371/450) | **−3** |
| `dev750` | Find | 0.781 (586/750) | 0.788 (591/750) | **+5** |
| `dev750` | Encode | 0.811 (608/750) | 0.809 (607/750) | **−1** |
| `dev750` | Select | 0.865 (649/750) | 0.867 (650/750) | **+1** |

Holdout select is **3** letters lower at temperature 1, not 11.
Development select is unchanged at one letter. Find deltas are
the same as the first write, because they do not depend on the later
rule stack.

New extracts had zero call and schema failures. Holdout rows were not
inspected. These cells are not promoted.

Work cells:
`experiments/paper/gan_llm_extract/gemini37flash/temperature_1/dev750/`
and
`scratch/holdout/paper/gan_llm_extract/gemini37flash/temperature_1/test450/`.

Codebook replay aggregates:
`experiments/paper/gan/rungs/gemini37flash/temperature_1/{split}/comparison.json`.

The joint Grok reading and the paper-facing bound are in
[Grok temperature 0](gan_grok46_temperature_0_2026-08-28.md) and
[three variables §2b](../paper/three_variables_rules_model_thinking_2026-08-23.md).
