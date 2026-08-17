# Gan LLM-only

Cited Gan LLM-only method (`gan_llm_only`). Gemma 4 26B is complete
on both splits. Qwen 3.8 27B has not been run.

Each `rows.jsonl` keeps `source_row_index`, `prompt_version`, and
`raw_output`. `test450` is aggregate-only. Do not inspect those rows.

Gemma `dev750` has 8 empty `raw_output` rows from the 20 Jul live
cell. Those rows cannot be replayed.

| Model | Split | Rows | Empty raw |
| --- | --- | ---: | ---: |
| Gemma 4 26B | `dev750` | 750 | 8 |
| Gemma 4 26B | `test450` | 450 | 0 |
| Qwen 3.8 27B | both | — | missing |
