# Grok 4.6 cell 3 at temperature 0

Date: 2026-08-28
Status: complete (not promoted)
Protocol: [temperature-0 `test450`](gan_grok46_temperature_0_test450_protocol_2026-08-28.md)
Owner: this file
Cited comparator: [three variables](../paper/three_variables_rules_model_thinking_2026-08-23.md)
§3 (Grok `gan_llm_extract` + codebook rule select)

## Living default

Grok temperature is now **0.0**, the same living setting as Gemini,
DeepSeek, Qwen, and Gemma. Luna stays at **1.0** because that provider
rejects `0`.

## Shift versus cited Grok cell 3 (temperature 1.0)

Cell 3 is LLM recognise (`gan_llm_extract`) then codebook rule encode
and rule select. The cited Grok row is recognise / select from the
three-variables table. Temperature-0 select is a no-call replay of
the new raws (`llm_select`), not a new model call.

| Split | Stop | Temp. 1.0 (cited) | Temp. 0.0 (new) | Δ |
| --- | --- | ---: | ---: | ---: |
| `test450` | Recognise | 0.784 (353/450) | 0.789 (355/450) | **+2** |
| `test450` | Select | 0.842 (379/450) | 0.816 (367/450) | **−12** |
| `dev750` | Recognise | 0.784 (588/750) | 0.780 (585/750) | **−3** |
| `dev750` | Select | 0.867 (650/750) | 0.884 (663/750) | **+13** |

Holdout: recognise is essentially unchanged; select is **0.026** lower.
Development: recognise is essentially unchanged; select is **0.017**
higher.

New extracts had zero call and schema failures. Holdout rows were not
inspected. Grok cell 3 is now promoted at temperature 0:
`paper_experiments/gan/gan_llm_extract/grok46/` and
`paper_experiments/gan/rungs/grok46/`.

## Joint reading with Gemini temperature 1

The matched Gemini ablation (living 0 versus temperature 1) is
[gan_gemini37flash_temperature_1_2026-08-28.md](gan_gemini37flash_temperature_1_2026-08-28.md).
The paper synthesis is
[three variables §2b](../paper/three_variables_rules_model_thinking_2026-08-23.md).

| Model | Split | Stop | Temp. 0 | Temp. 1 | Δ (1 − 0) |
| --- | --- | ---: | ---: | ---: | ---: |
| Gemini | `test450` | Select | 0.831 (374) | 0.807 (363) | −11 |
| Gemini | `dev750` | Select | 0.865 (649) | 0.867 (650) | +1 |
| Grok | `test450` | Select | 0.816 (367) | 0.842 (379) | +12 |
| Grok | `dev750` | Select | 0.884 (663) | 0.867 (650) | −13 |

Effects are mixed. Temperature 0 is the appropriate living default
for every model that accepts it. Luna was not run at 0; these signs
do not predict that Luna would rise or fall if the provider allowed
the same setting. Temperature is relatively inconsequential next to
thinking effort. Stage ownership on the three-stage pipeline moves
the Gemini holdout select far more (0.71 rules versus 0.83 cell 3).
