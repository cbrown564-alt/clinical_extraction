# Compact ledger local cells

Living Compact (`exectv2_compact_ledger`) is the ExECT live default.
These files are the local-model remasure. Qwen 3.8 is still missing
(`dev140` was 8/140 on 2026-08-17; `test60` has not started).

Gemma 4 26B is complete on `dev140` and aggregate-only `test60`. Each
comparison records LLM-only (`raw_*`) and LLM-with-rules (`hybrid_*`).
Structured sidecars keep `letter_id`, `prompt_version`, and `raw_output`
so both surfaces can be replayed without gold or note text.

| Split | Compact hybrid | Compact raw | Full hybrid | Full raw |
| --- | ---: | ---: | ---: | ---: |
| `dev140` | 0.7674 | 0.4751 | 0.8038 | 0.7049 |
| `test60` | 0.6933 | 0.4662 | 0.7327 | 0.6740 |

`test60` is aggregate-only. Do not inspect those letters.
