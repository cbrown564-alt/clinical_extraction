# Gan 2026 Component Stage-Ladder Replay

- Generated: `2026-06-24`
- JSON: `experiments/gan2026_component_stage_ladder_validation_20260624.json`
- Metric: Purist accuracy · split `validation`
- Claim boundary: validation replay-only aggregate component-impact ladder
- No model calls; deterministic stages re-run, structured-events + LLM-only stacks replayed from saved raw outputs.

| Architecture | Decision | Rows | Final | Stages (score) |
| --- | --- | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | control | 750 | 0.91 | Extract + normalize + select 0.91 → Benchmark repair 0.91 → Evidence trace check 0.91 |
| `hybrid_structured_events` | diagnostic | 750 | 0.89 | LLM events + selection 0.61 → Normalize 0.64 → Evidence projection 0.79 → Clinical repair families 0.89 |
| `llm_only_canonical_pipeline` | diagnostic | 750 | 0.78 | Model label 0.66 → Label repair 0.78 |
