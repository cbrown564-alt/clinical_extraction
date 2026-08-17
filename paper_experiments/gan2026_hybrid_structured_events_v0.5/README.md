# Gan hybrid structured events v0.5

Selected Gan hybrid prompt (Decision 0043). These files are the latest
live raws for Gemma 4 26B and Qwen 3.8 27B.

Each `rows.jsonl` keeps `source_row_index`, `prompt_version`, and
`raw_output` so a later no-call replay can run the same raws through
one ruleset. `test450` is aggregate-only. Do not inspect those rows.

| Model | Split | Rows | Empty raw | Live call |
| --- | --- | ---: | ---: | --- |
| Gemma 4 26B | `dev750` | 750 | 0 | 2026-07-28 |
| Gemma 4 26B | `test450` | 450 | 0 | 2026-07-19 |
| Qwen 3.8 27B | `dev750` | 750 | 0 | 2026-08-15 |
| Qwen 3.8 27B | `test450` | 450 | 0 | 2026-08-15 |
