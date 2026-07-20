# Gan 2026 six-model validation comparison

Generated: 2026-07-20T08:37:41.487142+00:00

Development evidence on `validation750`; not holdout evidence or clinical validation.

## Conditions

| Model | Method | State | Rows | Purist | Pragmatic | Evidence | Repairs |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| gpt41mini | `llm_with_rules` | complete | 750 | 653/750 | 674/750 | 693 | 545 |
| gpt41mini | `llm_only` | complete | 750 | 577/750 | 607/750 | 702 | 359 |
| gpt56luna | `llm_with_rules` | complete | 750 | 646/750 | 669/750 | 739 | 490 |
| gpt56luna | `llm_only` | complete | 750 | 558/750 | 580/750 | 710 | 258 |
| gpt56sol | `llm_with_rules` | complete | 750 | 655/750 | 672/750 | 750 | 597 |
| gpt56sol | `llm_only` | complete | 750 | 590/750 | 620/750 | 740 | 374 |
| deepseek_v4_flash | `llm_with_rules` | complete | 750 | 643/750 | 664/750 | 738 | 444 |
| deepseek_v4_flash | `llm_only` | complete | 750 | 559/750 | 591/750 | 674 | 247 |
| qwen36_35b | `llm_with_rules` | complete | 750 | 667/750 | 683/750 | 582 | 537 |
| qwen36_35b | `llm_only` | complete | 750 | 565/750 | 594/750 | 567 | 267 |
| gemma4_26b | `llm_with_rules` | complete | 750 | 646/750 | 674/750 | 718 | 466 |
| gemma4_26b | `llm_only` | complete | 750 | 512/750 | 545/750 | 675 | 352 |

## Matched method transitions

| Model | Changed | LLM-only wrong → rules correct | LLM-only correct → rules wrong | Both evidence-valid |
| --- | ---: | ---: | ---: | ---: |
| gpt41mini | 282 | 110 | 34 | 244 |
| gpt56luna | 280 | 120 | 32 | 257 |
| gpt56sol | 227 | 96 | 31 | 226 |
| deepseek_v4_flash | 267 | 115 | 31 | 231 |
| qwen36_35b | 305 | 125 | 23 | 155 |
| gemma4_26b | 325 | 168 | 34 | 249 |
