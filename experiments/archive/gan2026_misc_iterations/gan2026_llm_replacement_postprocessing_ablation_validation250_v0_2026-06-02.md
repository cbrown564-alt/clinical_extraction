# Gan 2026 LLM-Replacement Post-Processing Ablation

Diagnostic saved-output replay only: no hosted calls, prompt changes, scorer changes, projection-policy promotion, or holdout behavior changes.

- Source JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.jsonl`
- Split: `validation`
- Split manifest: `gan2026_split_v1`
- Rows: 250
- Condition rows: 1000
- JSONL artifact: `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.jsonl`
- Summary JSON: `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.json`

## Condition Summary

| Condition | Target | Rows | Scorable | Purist | Pragmatic | Changed | Raw wrong -> correct | Raw correct -> wrong | Evidence exact | Trace mismatches |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `raw_model_selected_label` | `strict_format` | 250 | 213 | 188 (0.7520) | 195 (0.7800) | 0 | 0 | 0 | 230 | 9 |
| `format_only_repair` | `strict_format` | 250 | 213 | 188 (0.7520) | 195 (0.7800) | 7 | 0 | 0 | 230 | 9 |
| `selected_evidence_arithmetic_only` | `selected_evidence_arithmetic` | 250 | 237 | 219 (0.8760) | 225 (0.9000) | 57 | 32 | 1 | 230 | 9 |
| `benchmark_aligned_adapter` | `benchmark_aligned` | 250 | 237 | 204 (0.8160) | 213 (0.8520) | 28 | 16 | 0 | 230 | 9 |

## Replay Variance

- Reused raw-output rows: 50
- Non-reused raw-output rows: 200
- Provider-call-change rows: 0

## Hard-Slice Breakdown

| Slice | Rows | Parse/schema failures | Trace mismatches |
| --- | ---: | ---: | ---: |
| `cluster` | 12 | 1 | 3 |
| `schema_parse_failure` | 12 | 12 | 0 |
| `seizure_free_duration` | 40 | 2 | 1 |
| `selected_event_trace_mismatch` | 9 | 0 | 9 |
| `unclassified_validation` | 170 | 0 | 0 |
| `unknown_no_reference_boundary` | 25 | 5 | 3 |
