# ExECTv2 Per-Entity Candidate-Source Probe — Combined

- Generated: `2026-06-17`
- JSON: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_combined.json`
- Split: `dev`  Letters: 25
- Model: `openai/gpt-4.1-mini`  Mode: `live`
- Prompt version: `exectv2_llm_only_per_entity_v0.3`
- Verdict rule: source-near overlap recall beats the all-9 baseline by >= 0.05

Source-near overlap recall is the format-blind candidate read. Semantic F1 is the CUI-dropped headline. The all-9 baseline is the documented negative comparator (attention-diluted single pass).

## Per-Entity Table

| Entity | Regime | Pub item F1 | Base sem item | Probe sem item | Probe sem letter | Base SN recall | Probe SN recall | Δ SN recall | Over-emit (probe/base) | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Prescription | representation_bound | 0.870 | 0.222 | 0.279 | 0.600 | 0.872 | 0.949 | +0.077 | 3/17 | GPT candidate source |
| Investigations | recall_bound | 0.950 | 0.542 | 0.511 | 0.640 | 0.950 | 0.950 | +0.000 | 8/9 | no recall lift -> deterministic+projection |
| Diagnosis | recall_bound | 0.850 | 0.123 | 0.256 | 0.545 | 0.339 | 0.429 | +0.089 | 6/6 | GPT candidate source |
| SeizureFrequency | mixed | 0.660 | 0.000 | 0.172 | 0.400 | 0.516 | 0.581 | +0.065 | 9/8 | GPT candidate source |

## Reading

GPT recall can only help recall-bound (and partly mixed) entities. A positive Δ source-near recall on a recall-bound entity confirms it as a Phase C GPT candidate source; flat/negative Δ on a representation-bound entity confirms it stays deterministic-candidate + projection. Read the over-emission columns for the first hybrid target.
