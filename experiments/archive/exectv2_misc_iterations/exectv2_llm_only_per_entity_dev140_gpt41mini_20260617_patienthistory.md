# ExECTv2 LLM-Only Per-Entity — PatientHistory

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_patienthistory.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `PatientHistory`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.78

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 431
- Mentions scored (evidence-valid): 381
- Evidence-invalid dropped: 50
- Evidence validity rate: 0.8840

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.246 | 0.273 | 0.223 | 0.685 | 104 | 277 | 362 |
| semantic | 0.163 | 0.181 | 0.148 | 0.526 | 69 | 312 | 397 |
| benchmark | 0.109 | 0.121 | 0.099 | 0.418 | 46 | 335 | 420 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.363 (TP=169 FN=297)
- Overlap F1: 0.399
- Over-emission (overlap FP): 212
- Attribute agreement on overlaps: 0.621 (105/169)
