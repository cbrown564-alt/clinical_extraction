# ExECTv2 Per-Entity Candidate-Source Probe — Combined

- Generated: `2026-06-17`
- JSON: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_combined.json`
- Split: `dev`  Letters: 25
- Model: `openai/gpt-4.1-mini`  Mode: `live`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Verdict rule: focused frame lifts LLM candidate recall when source-near overlap recall beats the all-9 baseline by >= 0.05

The LLM is the candidate source for every entity. Source-near overlap recall is the format-blind candidate read; semantic F1 is the CUI-dropped headline; the all-9 baseline is the documented negative comparator (attention-diluted single pass). The regime column sizes the deterministic projection that must follow the LLM candidate — it does not route an entity away from GPT candidate generation.

## Per-Entity Table

| Entity | Regime | Pub item F1 | Base sem item | Probe sem item | Probe sem letter | Base SN recall | Probe SN recall | Δ SN recall | Over-emit (probe/base) | Verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| BirthHistory | representation_bound | 0.970 | 0.000 | 0.200 | 0.400 | 0.500 | 0.500 | +0.000 | 1/0 | recall on par with all-9 |
| Diagnosis | recall_bound | 0.850 | 0.123 | 0.256 | 0.545 | 0.339 | 0.429 | +0.089 | 6/6 | focused frame lifts LLM recall |
| EpilepsyCause | representation_bound | 0.900 | 0.000 | 0.222 | 0.250 | 0.500 | 1.000 | +0.500 | 5/0 | focused frame lifts LLM recall |
| Investigations | recall_bound | 0.950 | 0.542 | 0.511 | 0.640 | 0.950 | 0.950 | +0.000 | 8/9 | recall on par with all-9 |
| Onset | mixed | 0.960 | 0.000 | 0.100 | 0.154 | 1.000 | 1.000 | +0.000 | 18/5 | recall on par with all-9 |
| PatientHistory | recall_bound | 0.780 | 0.000 | 0.153 | 0.387 | 0.192 | 0.370 | +0.178 | 31/10 | focused frame lifts LLM recall |
| Prescription | representation_bound | 0.870 | 0.222 | 0.279 | 0.600 | 0.872 | 0.949 | +0.077 | 3/17 | focused frame lifts LLM recall |
| SeizureFrequency | mixed | 0.660 | 0.000 | 0.172 | 0.400 | 0.516 | 0.581 | +0.065 | 9/8 | focused frame lifts LLM recall |
| WhenDiagnosed | representation_bound | 0.910 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | +0.000 | 6/0 | recall on par with all-9 |

## Reading

The LLM generates candidates for every entity. A positive Δ source-near recall means the focused frame recovers more real candidates than the attention-diluted all-9 pass; flat/negative Δ means the focused frame did not help recall there. High LLM source-near recall on a representation-bound entity (e.g. Prescription) is expected — its low semantic F1 is a projection gap, not a recall gap, and is closed by deterministic projection (Phase D), not by routing candidate generation away from the LLM. Read the over-emission columns for the first hybrid target.
