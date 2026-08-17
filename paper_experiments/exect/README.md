# ExECT paper cells

`exect_llm_with_rules` is Compact hybrid. `exect_llm_only` is Compact
raw from the same call. Full ledger lives under
`comparators/exect_full_ledger/`.

`test60` is aggregate-only. Do not inspect those letters.

| Model | Split | Compact hybrid | Compact raw | Full hybrid | Full raw |
| --- | --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol | `dev140` | 0.8934 | 0.8047 | 0.9048 | 0.829 |
| GPT-5.6 Sol | `test60` | 0.8031 | 0.7697 | 0.8202 | 0.7938 |
| GPT-5.6 Luna | `dev140` | 0.8818 | 0.7929 | 0.8974 | 0.8306 |
| GPT-5.6 Luna | `test60` | 0.7868 | 0.7426 | 0.7974 | 0.7785 |
| Gemini 3.7 Flash | `dev140` | 0.889 | 0.83 | 0.902 | 0.8376 |
| Gemini 3.7 Flash | `test60` | 0.8121 | 0.8 | 0.831 | 0.8138 |
| DeepSeek V4 Flash 0731 | `dev140` | 0.88 | 0.601 | 0.9132 | 0.8448 |
| DeepSeek V4 Flash 0731 | `test60` | 0.8124 | 0.5927 | 0.8144 | 0.792 |
| Gemma 4 26B | `dev140` | 0.7674 | 0.4751 | 0.8038 | 0.7049 |
| Gemma 4 26B | `test60` | 0.6933 | 0.4662 | 0.7327 | 0.6740 |

Still missing: Qwen 3.8 Compact on both splits.
