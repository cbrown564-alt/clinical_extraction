# Gemini 3.7 Flash cell 3 at temperature 1

Date: 2026-08-28
Status: complete (not promoted)
Protocol: [temperature-1 both splits](gan_gemini37flash_temperature_1_protocol_2026-08-28.md)
Owner: this file
Cited comparator: [three variables](../paper/three_variables_rules_model_thinking_2026-08-23.md)
§2–3 (Gemini `gan_llm_extract` + codebook rule select at temperature 0)

## Living default

Gemini temperature stays **0.0**. This file is the non-living
temperature-1 ablation. It is not promoted.

## Shift versus cited Gemini cell 3 (temperature 0.0)

Cell 3 is LLM recognise (`gan_llm_extract`) then codebook rule encode
and rule select. Temperature-1 select is a no-call replay of the new
raws (`llm_select`), not a new model call.

| Split | Stop | Temp. 0.0 (cited) | Temp. 1.0 (new) | Δ |
| --- | --- | ---: | ---: | ---: |
| `test450` | Recognise | 0.789 (355/450) | 0.778 (350/450) | **−5** |
| `test450` | Select | 0.831 (374/450) | 0.807 (363/450) | **−11** |
| `dev750` | Recognise | 0.781 (586/750) | 0.788 (591/750) | **+5** |
| `dev750` | Select | 0.865 (649/750) | 0.867 (650/750) | **+1** |

Holdout: recognise is **5** letters lower; select is **0.024** lower
(**−11**). Development: recognise is **5** letters higher; select is
essentially unchanged.

New extracts had zero call and schema failures. Holdout rows were not
inspected. These cells are not promoted.

Work cells:
`experiments/paper/gan_llm_extract/gemini37flash/temperature_1/dev750/`
and
`scratch/holdout/paper/gan_llm_extract/gemini37flash/temperature_1/test450/`.

Replay aggregates:
`experiments/paper/gan/rungs/gemini37flash/temperature_1/{split}/comparison.json`.

The joint Grok reading and the paper-facing bound are in
[Grok temperature 0](gan_grok46_temperature_0_2026-08-28.md) and
[three variables §2b](../paper/three_variables_rules_model_thinking_2026-08-23.md).
