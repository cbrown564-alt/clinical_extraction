# ExECTv2 LLM-Only Per-Entity — Diagnosis

- JSONL: `experiments\exectv2_llm_only_per_entity_diagnosis_dev25_gpt41mini_20260618_diagnosis.jsonl`
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
- Mentions raw: 29
- Mentions scored (evidence-valid): 29
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.400 | 0.586 | 0.304 | 0.769 | 17 | 12 | 39 |
| semantic | 0.259 | 0.379 | 0.196 | 0.545 | 11 | 18 | 45 |
| benchmark | 0.141 | 0.207 | 0.107 | 0.400 | 6 | 23 | 50 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.429 (TP=24 FN=32)
- Overlap F1: 0.565
- Over-emission (overlap FP): 5
- Attribute agreement on overlaps: 0.583 (14/24)
