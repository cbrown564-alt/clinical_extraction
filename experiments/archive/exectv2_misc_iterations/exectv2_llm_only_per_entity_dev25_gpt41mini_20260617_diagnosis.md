# ExECTv2 LLM-Only Per-Entity — Diagnosis

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_diagnosis.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `Diagnosis`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.85

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 30
- Mentions scored (evidence-valid): 30
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.372 | 0.533 | 0.286 | 0.737 | 16 | 14 | 40 |
| semantic | 0.256 | 0.367 | 0.196 | 0.545 | 11 | 19 | 45 |
| benchmark | 0.163 | 0.233 | 0.125 | 0.452 | 7 | 23 | 49 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.429 (TP=24 FN=32)
- Overlap F1: 0.558
- Over-emission (overlap FP): 6
- Attribute agreement on overlaps: 0.625 (15/24)
