# Gan 2026 LLM-Reasoning Stage 0 V0 Comparators

Date: 2026-06-13

This is a validation-development no-call artifact. It builds family hard-slice manifests and scores saved pure structured-event V0 artifacts before any new agentic reasoning runs. It does not inspect locked `test450` row-level data.

## Experiment Unit

- Work class: Stage 0 data/scoring parity and reporting.
- Hypothesis: saved pure structured-event artifacts can define reproducible validation hard slices and V0 baselines before V1/V2 agent calls.
- Data surface: validation split only, `gan2026_split_v1`.
- Scorer: saved Gan-compatible Purist and Pragmatic comparisons from each structured-event artifact.
- Stop rule: do not run agents until the V0 rows, slices, and source-index files are reproducible.

## Generated Slice Manifests

| Slice | Rows | Primary trigger |
| --- | ---: | --- |
| `unknown_no_reference_validation50` | 50 | Boundary-state rows where validation gold or V0 selection involves unknown or no-reference, prioritizing V0 boundary disagreements. |
| `seizure_free_last_event_validation50` | 50 | Rows with seizure-free or last-event-only gold, note text, or V0 events. |
| `frequency_denominator_validation50` | 50 | Rows with frequency denominators, ranges, vague multiple terms, or frequency_rate events. |
| `cluster_axis_validation50` | 50 | Rows where gold labels, note text, V0 final labels, or V0 events mention clusters. |
| `multi_semiology_burden_validation50` | 50 | Rows with multiple semiology terms or V0 events applying to multiple seizure types. |

## V0 Comparator Scores

| Surface | Artifact | Purist | Pragmatic | Evidence exact | Missing |
| --- | --- | ---: | ---: | ---: | ---: |
| `validation25_prefix` | `gpt41mini_hybrid_structured_events_v0_5` | 25/25 (1.0000) | 25/25 (1.0000) | 24/25 | 0 |
| `validation25_prefix` | `qwen3635b_hybrid_structured_events_v0_6` | 25/25 (1.0000) | 25/25 (1.0000) | 21/25 | 0 |
| `validation25_prefix` | `deepseek_hybrid_structured_events_v0_6` | 25/25 (1.0000) | 25/25 (1.0000) | 25/25 | 0 |
| `fixed_agentic_hard50` | `gpt41mini_hybrid_structured_events_v0_5` | 39/50 (0.7800) | 40/50 (0.8000) | 46/50 | 0 |
| `fixed_agentic_hard50` | `qwen3635b_hybrid_structured_events_v0_6` | 37/50 (0.7400) | 37/50 (0.7400) | 40/50 | 0 |
| `fixed_agentic_hard50` | `deepseek_hybrid_structured_events_v0_6` | 38/50 (0.7600) | 38/50 (0.7600) | 48/50 | 0 |
| `unknown_no_reference_validation50` | `gpt41mini_hybrid_structured_events_v0_5` | 34/50 (0.6800) | 34/50 (0.6800) | 44/50 | 0 |
| `unknown_no_reference_validation50` | `qwen3635b_hybrid_structured_events_v0_6` | 24/50 (0.4800) | 24/50 (0.4800) | 31/50 | 0 |
| `unknown_no_reference_validation50` | `deepseek_hybrid_structured_events_v0_6` | 18/50 (0.3600) | 18/50 (0.3600) | 43/50 | 0 |
| `seizure_free_last_event_validation50` | `gpt41mini_hybrid_structured_events_v0_5` | 15/50 (0.3000) | 20/50 (0.4000) | 45/50 | 0 |
| `seizure_free_last_event_validation50` | `qwen3635b_hybrid_structured_events_v0_6` | 10/50 (0.2000) | 15/50 (0.3000) | 36/50 | 0 |
| `seizure_free_last_event_validation50` | `deepseek_hybrid_structured_events_v0_6` | 5/50 (0.1000) | 11/50 (0.2200) | 48/50 | 0 |
| `frequency_denominator_validation50` | `gpt41mini_hybrid_structured_events_v0_5` | 7/50 (0.1400) | 15/50 (0.3000) | 46/50 | 0 |
| `frequency_denominator_validation50` | `qwen3635b_hybrid_structured_events_v0_6` | 3/50 (0.0600) | 9/50 (0.1800) | 42/50 | 0 |
| `frequency_denominator_validation50` | `deepseek_hybrid_structured_events_v0_6` | 2/50 (0.0400) | 9/50 (0.1800) | 48/50 | 0 |
| `cluster_axis_validation50` | `gpt41mini_hybrid_structured_events_v0_5` | 7/50 (0.1400) | 17/50 (0.3400) | 46/50 | 0 |
| `cluster_axis_validation50` | `qwen3635b_hybrid_structured_events_v0_6` | 9/50 (0.1800) | 15/50 (0.3000) | 40/50 | 0 |
| `cluster_axis_validation50` | `deepseek_hybrid_structured_events_v0_6` | 8/50 (0.1600) | 16/50 (0.3200) | 46/50 | 0 |
| `multi_semiology_burden_validation50` | `gpt41mini_hybrid_structured_events_v0_5` | 7/50 (0.1400) | 14/50 (0.2800) | 46/50 | 0 |
| `multi_semiology_burden_validation50` | `qwen3635b_hybrid_structured_events_v0_6` | 4/50 (0.0800) | 9/50 (0.1800) | 42/50 | 0 |
| `multi_semiology_burden_validation50` | `deepseek_hybrid_structured_events_v0_6` | 2/50 (0.0400) | 8/50 (0.1600) | 48/50 | 0 |
| `validation250_prefix` | `gpt41mini_hybrid_structured_events_v0_5` | 236/250 (0.9440) | 238/250 (0.9520) | 239/250 | 0 |
| `validation250_prefix` | `qwen3635b_hybrid_structured_events_v0_6` | 235/250 (0.9400) | 236/250 (0.9440) | 194/250 | 0 |
| `validation250_prefix` | `deepseek_hybrid_structured_events_v0_6` | 237/250 (0.9480) | 237/250 (0.9480) | 246/250 | 0 |

## Artifacts

- Combined JSON: `experiments\gan2026_llm_reasoning_stage0_v0_comparators_2026-06-13.json`
- Runner-facing source-row files: `experiments/gan2026_llm_reasoning_*_validation50_manifest_2026-06-13.txt`

## Interpretation

This artifact creates the Stage 0 substrate for the test-0.85 plan. The next implementation step is a V1/V2 reasoner runner that consumes these source-row files and reports changed-label precision against the best V0 pure structured-event comparator on each slice.
