# Gan 2026 six-model LLM-only test450 protocol

Date: 2026-08-01  
Status: complete; all six aggregate-only conditions finished  
Readout: aggregate-only  
Panel artifact:
`experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json`  
Parent method contract:
[six-model validation comparison](gan2026_six_model_validation_comparison_protocol_2026-07-18.md)
(`llm_only` arm)  
Row policy parent:
[matched v0.5 test450](gan2026_matched_v05_test450_protocol_2026-07-16.md)

## Primary question

How do the fixed six models compare on locked Gan `test450` under the matched
product-arm LLM-only pipeline (`llm` /
`llm_only_canonical_pipeline`, prompt
`gan2026_llm_only_canonical_pipeline_v0.8`)?

This is a matched aggregate panel for the named routes and frozen scorer. It is
not a model-neutral capability ranking, clinical validation, or a rewrite of
the frozen hybrid v0.5 LLM-with-rules `test450` panel.

## Data, split, and row policy

- Dataset: Gan 2026; manifest `gan2026_split_v1`; distribution `test`; 450 rows.
- Aggregate-only: no test-row identifier, note, prediction, evidence, label,
  model-specific failure, or row slice may be printed, copied, or analyzed.
- Sealed JSONL checkpoints remain under ignored `scratch/holdout/` roots.
- Markdown reports must be holdout aggregates (no `## Rows` tables).

## Frozen method

- Pipeline: `llm` / retained ID `llm_only_canonical_pipeline`
- Prompt: `gan2026_llm_only_canonical_pipeline_v0.8` (no prompt edit)
- Cache: disabled for every fresh live call
- Scorer: Gan Purist primary; Pragmatic side-car
- Deterministic code limited to label repair, evidence text-containment, and
  scoring (same as the retained `dev750` LLM-only arm)

## Fixed model conditions

| Slug | Model | Route | Temperature | Max tokens |
| --- | --- | --- | ---: | ---: |
| `gpt41mini` | `openai/gpt-4.1-mini` | hosted chat | 0 | 10,000 |
| `gpt56luna` | `openai/gpt-5.6-luna` | hosted chat | 1 | 10,000 |
| `gpt56sol` | `openai/gpt-5.6-sol` | hosted Responses | omitted by adapter | 10,000 |
| `deepseek_v4_flash` | `deepseek/deepseek-v4-flash` | official hosted | 0 | 32,000 |
| `qwen36_35b` | `ollama_chat/qwen3.6:35b` | native Ollama, `think=false` | 0 | 16,000 |
| `gemma4_26b` | `ollama_chat/gemma4:26b` | native Ollama, `think=false` | 0 | 16,000 |

Hosted OpenAI conditions run sequentially. DeepSeek may run independently.
Local Qwen then Gemma share Ollama and run sequentially after or beside hosted
work without overlapping each other.

## Artifact roots

Panel root:
`scratch/holdout/gan2026_six_model_llm_only_test450_20260801/{slug}/`

DeepSeek cell: the completed 2026-07-31 live no-cache `test450` LLM-only run
under
`scratch/holdout/gan2026_test450_deepseek_v4_flash_0731_20260731/llm/`
is the authorized DeepSeek panel cell (current DeepSeek-V4-Flash API surface).
Its aggregate Markdown is regenerated aggregate-only; sealed JSONL is not
rewritten. Panel tooling may hardlink or reference that path.

Configuration owner:
`configs/gan2026/six_model_llm_only_test450_20260801.json`.

## Stop rule and claim boundary

Run each remaining condition once to completion (resume allowed only within its
own dated root). Report aggregate metrics only. Hosted versus local route
differences remain disclosed. This panel does not replace the frozen hybrid
v0.5 `test450` LLM-with-rules panel and does not authorize row-level holdout
inspection or tuning.
