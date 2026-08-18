# ExECT paper cells

`exect_llm_with_rules` is Compact hybrid (cite hybrid F1 only).
`exect_llm_only` is the standalone Compact LLM-only request (cite
raw F1 only). Hybrid-call raw is not LLM-only. Full ledger lives
under `comparators/exect_full_ledger/`.

`test60` is aggregate-only. Do not inspect those letters.

| Model | Split | Compact hybrid | Compact LLM-only | Full hybrid | Full raw |
| --- | --- | ---: | ---: | ---: | ---: |
| Grok 4.6 | `dev140` | 0.8998 | — | — | — |
| Grok 4.6 | `test60` | 0.805 | — | — | — |
| GPT-5.6 Sol | `dev140` | 0.8934 | — | 0.9048 | 0.829 |
| GPT-5.6 Sol | `test60` | 0.8031 | — | 0.8202 | 0.7938 |
| GPT-5.6 Luna | `dev140` | 0.888 | 0.7912 | 0.8974 | 0.8306 |
| GPT-5.6 Luna | `test60` | 0.7827 | 0.7448 | 0.7974 | 0.7785 |
| Gemini 3.7 Flash | `dev140` | 0.889 | — | 0.902 | 0.8376 |
| Gemini 3.7 Flash | `test60` | 0.8121 | — | 0.831 | 0.8138 |
| DeepSeek V4 Flash 0731 | `dev140` | 0.88 | — | 0.9132 | 0.8448 |
| DeepSeek V4 Flash 0731 | `test60` | 0.8124 | — | 0.8144 | 0.792 |
| Gemma 4 26B | `dev140` | 0.7674 | — | 0.8038 | 0.7049 |
| Gemma 4 26B | `test60` | 0.6933 | — | 0.7327 | 0.6740 |

Still missing: Qwen 3.8 Compact hybrid on both splits. Standalone
Compact LLM-only for every living model except Luna. Grok Compact
has no Full-ledger control. Grok `dev140` is in the living frontend
panel (`exect/dev140_panel.json`). `test60` is aggregate-only.

Frontend pull: `GET /paper/exect/dev140` and
`GET /paper/exect/dev140/{slug}/scored`. Join letters on `letter_id`.
The July `/exectv2/runs` roster is historical (Sol + Qwen 3.6).
