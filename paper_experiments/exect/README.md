# ExECT paper cells

Headline table: Gemini five-cell grid on locked `test60`. The cited
score is the select stop. Cell 3 (LLM / rules / rules) is the
six-model roster row; extract is `exect_llm_only`. Cell 4 (LLM / LLM /
rules) is the Gemini-only peak after later-stage encode.

| Extract | Encode | Select | F1 (Gemini `test60`) |
| --- | --- | --- | ---: |
| rules | rules | rules | 0.79 |
| both | rules | rules | 0.80 |
| LLM | rules | rules | 0.82 |
| LLM | LLM | rules | 0.82 |
| LLM | LLM | LLM | 0.80 |

Cell-3 roster fills use `exect_llm_only/` plus rule encode and
select. Cell-4 encode uses `exect_llm_encode/` (Gemini only).
Extract and encode columns above are stage ablations, not separate
headline methods.

Historical on disk (not headline):

- `exect_llm_pre_post/` — two-method hybrid from before the five-cell
  pin. `exect_llm_with_rules` is a live runner alias only.
- Producer raw F1 from `exect_llm_only` without rule stops is an
  ablation view, not the cited score.

`test60` is aggregate-only. Do not inspect those letters.

## Development reference (not headline)

Scores below are from historical two-method cells on `dev140` /
`test60`. They support roster debugging, not the cited five-cell
table.

| Model | Split | ExECT pre-post | ExECT LLM only |
| --- | --- | ---: | ---: |
| Grok 4.6 | `dev140` | 0.8998 | 0.8212 |
| Grok 4.6 | `test60` | 0.805 | 0.7726 |
| GPT-5.6 Luna | `dev140` | 0.888 | 0.7912 |
| GPT-5.6 Luna | `test60` | 0.7827 | 0.7448 |
| Gemini 3.7 Flash | `dev140` | 0.8946 | 0.8037 |
| Gemini 3.7 Flash | `test60` | 0.8129 | 0.7826 |
| DeepSeek V4 Flash 0731 | `dev140` | 0.88 | 0.8137 |
| DeepSeek V4 Flash 0731 | `test60` | 0.8124 | present |
| Gemma 4 26B | `dev140` | 0.7674 | — |
| Gemma 4 26B | `test60` | 0.6933 | — |

Still missing: Qwen 3.8 cell-3 fills on both splits. ExECT LLM
only for Gemma and Qwen. `dev140` cell-3 rungs are in the frontend
panel (`exect/dev140_panel.json`). `exect_llm_pre_post` is not a
panel column. `test60` is aggregate-only.

Frontend pull: `GET /paper/exect/dev140` and
`GET /paper/exect/dev140/{method}/{slug}/scored`.
Join letters on `letter_id`.
The July `/exectv2/runs` roster is historical (Sol + Qwen 3.6).
