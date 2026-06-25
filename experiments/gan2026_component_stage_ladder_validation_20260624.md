# Gan 2026 Component Stage-Ladder Replay

- Generated: `2026-06-26`
- JSON: `experiments/gan2026_component_stage_ladder_validation_20260624.json`
- Metric: Purist accuracy · split `validation`
- Claim boundary: validation replay-only aggregate component-impact ladder
- No model calls; deterministic stages re-run, structured-events + LLM-only stacks replayed from saved raw outputs.

| Architecture | Decision | Rows | Final | Stages (score) |
| --- | --- | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | control | 750 | 0.91 | Extract + normalize + select 0.91 → Benchmark repair 0.91 → Evidence trace check 0.91 |
| `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07` | diagnostic | 750 | 0.89 | LLM events + selection 0.61 → Normalize 0.64 → Evidence projection 0.79 → Clinical repair families 0.89 |
| `gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08` | diagnostic | 750 | 0.84 | LLM events + selection 0.62 → Normalize 0.64 → Evidence projection 0.77 → Clinical repair families 0.84 |
| `gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08` | diagnostic | 750 | 0.86 | LLM events + selection 0.57 → Normalize 0.62 → Evidence projection 0.79 → Clinical repair families 0.86 |
| `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07` | diagnostic | 750 | 0.78 | Model label 0.66 → Label repair 0.78 |
| `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08` | diagnostic | 750 | 0.76 | Model label 0.59 → Label repair 0.76 |
| `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08` | diagnostic | 750 | 0.74 | Model label 0.49 → Label repair 0.74 |
