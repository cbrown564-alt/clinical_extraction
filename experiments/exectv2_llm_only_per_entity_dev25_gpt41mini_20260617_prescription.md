# ExECTv2 LLM-Only Per-Entity — Prescription

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_prescription.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.3`
- Entity: `Prescription`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.87

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 41
- Mentions scored (evidence-valid): 40
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9756

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.354 | 0.350 | 0.359 | 0.727 | 14 | 26 | 25 |
| semantic | 0.279 | 0.275 | 0.282 | 0.600 | 11 | 29 | 28 |
| benchmark | 0.279 | 0.275 | 0.282 | 0.600 | 11 | 29 | 28 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.949 (TP=37 FN=2)
- Overlap F1: 0.937
- Over-emission (overlap FP): 3
- Attribute agreement on overlaps: 0.865 (32/37)
