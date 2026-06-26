# ExECTv2 LLM-Only Per-Entity — Diagnosis

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_diagnosis.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `Diagnosis`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.85

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 163
- Mentions scored (evidence-valid): 154
- Evidence-invalid dropped: 9
- Evidence validity rate: 0.9448

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.315 | 0.571 | 0.217 | 0.762 | 88 | 66 | 317 |
| semantic | 0.243 | 0.442 | 0.168 | 0.647 | 68 | 86 | 337 |
| benchmark | 0.172 | 0.312 | 0.118 | 0.516 | 48 | 106 | 357 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.306 (TP=124 FN=281)
- Overlap F1: 0.444
- Over-emission (overlap FP): 30
- Attribute agreement on overlaps: 0.758 (94/124)
