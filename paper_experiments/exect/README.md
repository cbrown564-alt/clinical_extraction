# ExECT paper cells

Living paper methods:

- `exect_llm_with_rules/` — ExECT LLM with rules (cite hybrid F1 only).
- `exect_llm_only/` — ExECT LLM only (cite raw F1 only).

The unrepaired output of ExECT LLM with rules is not ExECT LLM
only. Full ledger is a named comparator control only; raws live
under `comparators/exect_full_ledger/`.

`test60` is aggregate-only. Do not inspect those letters.

| Model | Split | ExECT LLM with rules | ExECT LLM only |
| --- | --- | ---: | ---: |
| Grok 4.6 | `dev140` | 0.8998 | 0.8212 |
| Grok 4.6 | `test60` | 0.805 | 0.7726 |
| GPT-5.6 Luna | `dev140` | 0.888 | 0.7912 |
| GPT-5.6 Luna | `test60` | 0.7827 | 0.7448 |
| Gemini 3.7 Flash | `dev140` | 0.8946 | 0.8037 |
| Gemini 3.7 Flash | `test60` | 0.8129 | 0.7826 |
| DeepSeek V4 Flash 0731 | `dev140` | 0.88 | — |
| DeepSeek V4 Flash 0731 | `test60` | 0.8124 | — |
| Gemma 4 26B | `dev140` | 0.7674 | — |
| Gemma 4 26B | `test60` | 0.6933 | — |

Still missing: Qwen 3.8 both methods on both splits. ExECT LLM only
for DeepSeek, Gemma, and Qwen. `dev140` is in the living frontend
panel (`exect/dev140_panel.json`). `test60` is aggregate-only.

Frontend pull: `GET /paper/exect/dev140` and
`GET /paper/exect/dev140/{exect_llm_only|exect_llm_with_rules}/{slug}/scored`.
Join letters on `letter_id`.
The July `/exectv2/runs` roster is historical (Sol + Qwen 3.6).
