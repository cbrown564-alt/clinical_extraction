# Compact ledger paper cells

Living Compact (`exectv2_compact_ledger`) is the paper-cited ExECT
hybrid ([Decision 0058](../../docs/decisions/0058-compact-ledger-is-the-paper-cited-exect-hybrid.md)).
Full ledger in the same folders is the matched control.

Each comparison records LLM-only (`raw_*`) and LLM-with-rules
(`hybrid_*`). Replay files keep `letter_id`, `prompt_version`, and
`raw_output` so both surfaces can be replayed without gold or note
text. `test60` is aggregate-only. Do not inspect those letters.

| Model | Split | Compact hybrid | Compact raw | Full hybrid | Full raw |
| --- | --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Sol | `dev140` | 0.8934 | 0.8047 | 0.9048 | 0.829 |
| GPT-5.6 Sol | `test60` | 0.8031 | 0.7697 | 0.8202 | 0.7938 |
| GPT-5.6 Luna | `dev140` | 0.8818 | 0.7929 | 0.8974 | 0.8306 |
| Gemini 3.7 Flash | `dev140` | 0.889 | 0.83 | 0.902 | 0.8376 |
| Gemini 3.7 Flash | `test60` | 0.8121 | 0.8 | 0.831 | 0.8138 |
| DeepSeek V4 Flash 0731 | `dev140` | 0.88 | 0.601 | 0.9132 | 0.8448 |
| DeepSeek V4 Flash 0731 | `test60` | 0.8124 | 0.5927 | 0.8144 | 0.792 |
| Gemma 4 26B | `dev140` | 0.7674 | 0.4751 | 0.8038 | 0.7049 |
| Gemma 4 26B | `test60` | 0.6933 | 0.4662 | 0.7327 | 0.6740 |

Still missing: Qwen 3.8 Compact on both splits, and Luna Compact
`test60`.
