# Gan 2026 six-model LLM-only test450 panel

Date: 2026-08-01

Aggregate-only matched LLM-only (`gan2026_llm_only_canonical_pipeline_v0.8`) panel on locked `test450`. Does not replace the frozen hybrid v0.5 LLM-with-rules panel. Hosted versus local routes are disclosed. No row inspection.

| Rank | Model | Purist | Pragmatic | Call failures | Parse/schema | Route |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | `openai/gpt-5.6-sol` | 335/450 (0.7444) | 353/450 (0.7844) | 0 | 0 | hosted_openai |
| 2 | `deepseek/deepseek-v4-flash` | 332/450 (0.7378) | 350/450 (0.7778) | 0 | 0 | hosted_deepseek |
| 3 | `openai/gpt-4.1-mini` | 330/450 (0.7333) | 355/450 (0.7889) | 0 | 0 | hosted_openai |
| 4 | `openai/gpt-5.6-luna` | 319/450 (0.7089) | 334/450 (0.7422) | 0 | 2 | hosted_openai |
| 5 | `ollama_chat/qwen3.6:35b` | 316/450 (0.7022) | 332/450 (0.7378) | 0 | 4 | local |
| 6 | `ollama_chat/gemma4:26b` | 305/450 (0.6778) | 328/450 (0.7289) | 0 | 19 | local |

Protocol: `docs/experiments/gan2026/gan2026_six_model_llm_only_test450_protocol_2026-08-01.md`
Machine artifact: `experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json`
