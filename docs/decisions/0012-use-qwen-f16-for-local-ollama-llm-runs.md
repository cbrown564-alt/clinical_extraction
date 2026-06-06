# 0012: Use Qwen F16 For Local Ollama LLM Runs

Date: 2026-06-06

## Status

Accepted.

## Decision

Use Qwen 3.6 35B via local Ollama with f16 KV cache as the default local LLM
route for Gan 2026 LLM-backed validation-development runs.

The current default local configuration is:

- model: `ollama_chat/qwen3.6:35b`;
- Ollama server environment: `OLLAMA_KV_CACHE_TYPE=f16`;
- Ollama server environment: `OLLAMA_FLASH_ATTENTION=1`;
- model context: keep the current Qwen/Ollama context configuration unless a
  specific experiment predeclares a narrower context.

Gemma 4 12B remains an exploratory comparison model only. It should not replace
Qwen as the routine local model for candidate-set extraction, clinical
assessment, or related Gan 2026 LLM validation-development artifacts without a
new decision record.

## Context

The project compared Qwen 3.6 35B against Gemma 4 12B after changing Ollama
runtime settings to q8 KV cache plus flash attention. It then reran Qwen with
f16 KV cache on the same slice. The relevant quick checks used the first 25
rows of the Gan 2026 validation split with the
`llm_extracted_candidate_schema_probe` pipeline.

On the same validation25 slice, Qwen's fresh q8 run recovered the earlier
structural failures seen in the first 25 rows of the validation250 Qwen
artifact:

| Run | Candidate sets | Failures | Rows with no candidates | Total candidates |
|---|---:|---:|---:|---:|
| Earlier Qwen validation250 first 25 rows | 20/25 | 5 | 5 | 44 |
| Fresh Qwen q8 validation25 | 25/25 | 0 | 0 | 54 |
| Fresh Qwen f16 validation25 | 25/25 | 0 | 0 | 54 |

The previously failing rows were `40`, `180`, `212`, `466`, and `659`; all
completed cleanly in the fresh q8 and f16 validation25 runs.

The f16 Qwen run preserved the same structural output as q8 while improving
wall-clock speed:

| Qwen KV cache | Total time | Seconds per row |
|---|---:|---:|
| `q8_0` | 814.7s | 32.6 |
| `f16` | 653.8s | 26.2 |

Because f16 was faster on the same validation25 slice with identical schema-fit
behavior, f16 is the preferred local default.

Gemma 4 12B was faster on the same slice but had weaker structural behavior:
23/25 candidate sets, 2 call/parse failures, 3 rows with no candidates, and
truncation warnings. Ollama also continued to report partial CPU/GPU residency
for Gemma under the tested settings, so the comparison did not justify a model
switch.

## Consequences

- New local Gan 2026 LLM extraction and assessment experiments should use Qwen
  f16 unless the experiment explicitly documents a different model or KV cache.
- Reports should record the model route and Ollama runtime settings when they
  are relevant to interpreting speed or schema-fit behavior.
- Gemma comparison artifacts should be treated as exploratory and not used as
  the baseline for architecture decisions.
- Future changes to model, KV cache type, or context strategy should be made
  through a new decision note or an explicit superseding update.

## Related Artifacts

- `experiments/gan2026_validation250_llm_candidate_set_qwen36_35b_v6_2026-06-06.jsonl`
- `experiments/gan2026_validation25_llm_candidate_set_qwen36_35b_v6_kvq8_flash_2026-06-06.jsonl`
- `experiments/gan2026_validation25_llm_candidate_set_qwen36_35b_v6_kvq8_flash_2026-06-06.md`
- `experiments/gan2026_validation25_llm_candidate_set_qwen36_35b_v6_kvf16_flash_2026-06-06.jsonl`
- `experiments/gan2026_validation25_llm_candidate_set_qwen36_35b_v6_kvf16_flash_2026-06-06.md`
- `experiments/gan2026_validation25_llm_candidate_set_gemma4_12b_v6_kvq8_flash_2026-06-06.jsonl`
- `experiments/gan2026_validation25_llm_candidate_set_gemma4_12b_v6_kvq8_flash_2026-06-06.md`
