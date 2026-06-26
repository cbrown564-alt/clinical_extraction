# ExECTv2 Per-Entity Candidate-Source Probe — Combined

- Generated: `2026-06-18`
- JSON: `experiments\exectv2_llm_only_per_entity_diagnosis_dev25_gpt41mini_20260618_combined.json`
- Split: `dev`  Letters: 25
- Model: `openai/gpt-4.1-mini`  Mode: `live`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Verdict rule: focused frame lifts LLM candidate recall when source-near overlap recall beats the all-9 baseline by >= 0.05

The LLM is the candidate source for every entity. Source-near overlap recall is the format-blind candidate read; semantic F1 is the CUI-dropped headline; the all-9 baseline is the documented negative comparator (attention-diluted single pass). The regime column sizes the deterministic projection that must follow the LLM candidate — it does not route an entity away from GPT candidate generation.

## Per-Entity Table

| Entity | Regime | Pub item F1 | Base sem item | Probe sem item | Probe sem letter | Base SN recall | Probe SN recall | Δ SN recall | Over-emit (probe/base) | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Diagnosis | recall_bound | 0.850 | 0.123 | 0.259 | 0.545 | 0.339 | 0.429 | +0.089 | 5/6 | focused frame lifts LLM recall |

## Reading

The LLM generates candidates for every entity. A positive Δ source-near recall means the focused frame recovers more real candidates than the attention-diluted all-9 pass; flat/negative Δ means the focused frame did not help recall there. High LLM source-near recall on a representation-bound entity (e.g. Prescription) is expected — its low semantic F1 is a projection gap, not a recall gap, and is closed by deterministic projection (Phase D), not by routing candidate generation away from the LLM. Read the over-emission columns for the first hybrid target.
