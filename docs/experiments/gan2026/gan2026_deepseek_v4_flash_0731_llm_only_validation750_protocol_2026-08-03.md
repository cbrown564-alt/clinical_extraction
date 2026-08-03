# Gan DeepSeek V4-Flash-0731 llm_only validation750 protocol

Date: 2026-08-03  
Status: running  
Parent framing:
[0731 matched comparison protocol](../../research/deepseek_v4_flash_0731_matched_comparison_protocol_2026-08-03.md)  
Prior cell:
[six-model validation comparison](gan2026_six_model_validation_comparison_protocol_2026-07-18.md)
(`deepseek_v4_flash` / `llm_only`, 559/750 Purist)

## Primary question

Does the DeepSeek-V4-Flash-0731 API revision change Gan `llm_only`
(`gan2026_llm_only_canonical_pipeline_v0.8`) Purist accuracy on
`validation750` versus the pre-0731 six-model cell (559/750)?

## Data, split, and row policy

- Dataset: Gan 2026; manifest `gan2026_split_v1`; distribution `validation`;
  750 rows (`dev750` / `validation750`).
- Development split: row-level inspection is permitted on this distribution.
- No `test450` rows are opened or used for tuning.

## Frozen method (matched to prior)

| Field | Value |
| --- | --- |
| Pipeline | `llm` / `llm_only_canonical_pipeline` |
| Prompt | `gan2026_llm_only_canonical_pipeline_v0.8` |
| Model | `deepseek/deepseek-v4-flash` |
| Provider revision | DeepSeek-V4-Flash-0731 (current API surface) |
| Temperature | 0 |
| Max tokens | 32,000 |
| Cache | disabled (`--disable-dspy-cache`) |
| Scorer | Purist primary; Pragmatic side-car |

## Artifacts

| Role | Path |
| --- | --- |
| Output root | `scratch/validation/gan2026_validation750_deepseek_v4_flash_0731_20260803/llm_only/` |
| Rows | `.../rows.jsonl` |
| Aggregate | `.../aggregate.md` |
| Prior comparator | `scratch/validation/gan2026_six_model_comparison_20260718/deepseek_v4_flash/llm_only/validation750.report.md` (559/750) |
| Compare artifact (after completion) | `experiments/gan2026_deepseek_v4_flash_0731_llm_only_validation750_vs_20260718.json` |

## Stop rule and claim boundary

Run once to completion (resume allowed within this dated root only). Report
Purist/Pragmatic and delta versus the 2026-07-18 cell. This is
provider-update development evidence for Gan llm_only; it does not replace
the retained v0.5 llm_with_rules panel or automatically promote a new
six-model llm_only ranking.
