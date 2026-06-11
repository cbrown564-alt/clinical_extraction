# ExECTv2 Three-Way Architecture Comparison — SeizureFrequency (openai/gpt-4.1-mini, dev)

- Generated: `2026-06-11`
- Model: `openai/gpt-4.1-mini` (rules family is model-independent)
- Split: `dev`
- Entity: SeizureFrequency (the benchmark's hardest cell; Table 1, Fonferko-Shadrach 2024)
- Match axes: `phrase_only` (phrase recall), `sf_semantic` (guideline-aligned attributes), `sf_benchmark` (keeps CUI)

## Scores (F1)

| Family | Config | Letters | phrase per-item | phrase per-letter | semantic per-item | semantic per-letter | benchmark per-item | benchmark per-letter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rules | `deterministic_sf` | 140 | 0.485 | 0.684 | 0.362 | 0.575 | 0.362 | 0.575 |
| llm_only | `per_entity` | 140 | 0.486 | 0.698 | 0.135 | 0.264 | 0.000 | 0.000 |
| llm_only | `single_pass` | 140 | 0.466 | 0.701 | 0.094 | 0.197 | 0.000 | 0.000 |
| hybrid | `candidate_assessment` | 140 | 0.585 | 0.781 | 0.327 | 0.578 | 0.327 | 0.578 |
| **benchmark target** | published SF | 200 | — | — | — | — | **0.660** | **0.680** |

## Provenance

- The **rules** row is computed live from the deterministic pipeline in the tree (sub-second dev pass, no per-record cost; deliberately unregistered per satellite 05 §5a).
- The **llm_only** and **hybrid** rows are the registered live runs for this model and split.
  - `per_entity` ← `exectv2_llm_only_per_entity_dev140_gpt41mini_20260610`
  - `single_pass` ← `exectv2_llm_only_single_pass_dev140_gpt41mini_20260610`
  - `candidate_assessment` ← `exectv2_hybrid_dev140_gpt41mini_20260611`
