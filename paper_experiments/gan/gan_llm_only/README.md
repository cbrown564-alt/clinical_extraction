# Gan LLM-only

Cited Gan LLM-only method (`gan_llm_only`). Living `dev750` cells
are the six-model frontend panel. Gemma 4 26B still has an older
tracked fill on both splits; that fill is not the living panel cell.

Each `rows.jsonl` keeps `source_row_index`, `prompt_version`, and
`raw_output`. `test450` is aggregate-only. Do not inspect those rows.

Gemma `dev750` has 8 empty `raw_output` rows from the 20 Jul live
cell. Those rows cannot be replayed.

| Model | Split | Rows | Empty raw |
| --- | --- | ---: | ---: |
| Grok 4.6 | `dev750` | 750 | 0 |
| GPT-5.6 Luna | `dev750` | 750 | 0 |
| Gemini 3.7 Flash | `dev750` | 750 | 0 |
| Gemma 4 26B (historical v0.8) | `dev750` | 750 | 8 |
| Gemma 4 26B (historical v0.8) | `test450` | 450 | 0 |
| DeepSeek / Qwen / living Gemma | `dev750` | — | pending |
