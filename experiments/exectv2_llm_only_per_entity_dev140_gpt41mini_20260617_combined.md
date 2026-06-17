# ExECTv2 Per-Entity Candidate-Source Probe — Combined

- Generated: `2026-06-17`
- JSON: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_combined.json`
- Split: `dev`  Letters: 140
- Model: `openai/gpt-4.1-mini`  Mode: `live`
- Prompt version: `exectv2_llm_only_per_entity_v0.3`
- Verdict rule: focused frame lifts LLM candidate recall when source-near overlap recall beats the all-9 baseline by >= 0.05

The LLM is the candidate source for every entity. Source-near overlap recall is the format-blind candidate read; semantic F1 is the CUI-dropped headline; the all-9 baseline is the documented negative comparator (attention-diluted single pass). The regime column sizes the deterministic projection that must follow the LLM candidate — it does not route an entity away from GPT candidate generation.

## Per-Entity Table

| Entity | Regime | Pub item F1 | Base sem item | Probe sem item | Probe sem letter | Base SN recall | Probe SN recall | Δ SN recall | Over-emit (probe/base) | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Prescription | representation_bound | 0.870 | 0.179 | 0.173 | 0.385 | 0.820 | 0.903 | +0.083 | 46/83 | focused frame lifts LLM recall |
| Investigations | recall_bound | 0.950 | 0.328 | 0.546 | 0.755 | 0.868 | 0.890 | +0.022 | 58/45 | recall on par with all-9 |
| Diagnosis | recall_bound | 0.850 | 0.176 | 0.243 | 0.647 | 0.301 | 0.306 | +0.005 | 30/42 | recall on par with all-9 |
| SeizureFrequency | mixed | 0.660 | 0.000 | 0.134 | 0.298 | 0.497 | 0.642 | +0.144 | 51/59 | focused frame lifts LLM recall |

## Reading

The LLM generates candidates for every entity. A positive Δ source-near recall means the focused frame recovers more real candidates than the attention-diluted all-9 pass; flat/negative Δ means the focused frame did not help recall there. High LLM source-near recall on a representation-bound entity (e.g. Prescription) is expected — its low semantic F1 is a projection gap, not a recall gap, and is closed by deterministic projection (Phase D), not by routing candidate generation away from the LLM. Read the over-emission columns for the first hybrid target.
