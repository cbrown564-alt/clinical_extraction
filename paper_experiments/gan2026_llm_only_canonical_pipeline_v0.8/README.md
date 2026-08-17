# Gan LLM-only canonical pipeline v0.8

Selected Gan LLM-only program. This is a different prompt from hybrid
v0.5, not the unrepaired side of that run.

Gemma 4 26B is complete on both splits. Qwen 3.8 27B has not been run.

Each `rows.jsonl` keeps `source_row_index`, `prompt_version`, and
`raw_output`. `test450` is aggregate-only. Do not inspect those rows.

Gemma `dev750` has 8 empty `raw_output` rows from the 20 Jul live
cell (7 call errors, 1 blank). Those rows cannot be replayed.

| Model | Split | Rows | Empty raw | Live call |
| --- | --- | ---: | ---: | --- |
| Gemma 4 26B | `dev750` | 750 | 8 | 2026-07-20 |
| Gemma 4 26B | `test450` | 450 | 0 | 2026-08-01 |
| Qwen 3.8 27B | `dev750` | — | — | missing |
| Qwen 3.8 27B | `test450` | — | — | missing |
