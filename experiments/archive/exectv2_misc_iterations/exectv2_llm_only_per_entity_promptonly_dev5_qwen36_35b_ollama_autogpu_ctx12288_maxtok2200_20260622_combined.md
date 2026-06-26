# ExECTv2 Per-Entity Candidate-Source Probe — Combined

- Generated: `2026-06-22`
- JSON: `experiments\exectv2_llm_only_per_entity_promptonly_dev5_qwen36_35b_ollama_autogpu_ctx12288_maxtok2200_20260622_combined.json`
- Split: `dev`  Letters: 5
- Model: `ollama_chat/qwen3.6:35b`  Mode: `prompt-only`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Verdict rule: focused frame lifts LLM candidate recall when source-near overlap recall beats the all-9 baseline by >= 0.05

The LLM is the candidate source for every entity. Source-near overlap recall is the format-blind candidate read; semantic F1 is the CUI-dropped headline; the all-9 baseline is the documented negative comparator (attention-diluted single pass). The regime column sizes the deterministic projection that must follow the LLM candidate — it does not route an entity away from GPT candidate generation.

## Per-Entity Table

| Entity | Regime | Pub item F1 | Base sem item | Probe sem item | Probe sem letter | Base SN recall | Probe SN recall | Δ SN recall | Over-emit (probe/base) | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Diagnosis | recall_bound | 0.850 | 0.000 | 0.000 | 0.000 | 0.263 | 0.000 | -0.263 | 0/2 | focused frame regresses vs all-9 |
| SeizureFrequency | mixed | 0.660 | 0.000 | 0.000 | 0.000 | 0.727 | 0.000 | -0.727 | 0/0 | focused frame regresses vs all-9 |
| Prescription | representation_bound | 0.870 | 0.174 | 0.000 | 0.000 | 0.889 | 0.000 | -0.889 | 0/6 | focused frame regresses vs all-9 |
| Investigations | recall_bound | 0.950 | 0.778 | 0.000 | 0.000 | 1.000 | 0.000 | -1.000 | 0/2 | focused frame regresses vs all-9 |

## Reading

The LLM generates candidates for every entity. A positive Δ source-near recall means the focused frame recovers more real candidates than the attention-diluted all-9 pass; flat/negative Δ means the focused frame did not help recall there. High LLM source-near recall on a representation-bound entity (e.g. Prescription) is expected — its low semantic F1 is a projection gap, not a recall gap, and is closed by deterministic projection (Phase D), not by routing candidate generation away from the LLM. Read the over-emission columns for the first hybrid target.
