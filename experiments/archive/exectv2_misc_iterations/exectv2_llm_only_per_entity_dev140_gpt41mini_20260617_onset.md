# ExECTv2 LLM-Only Per-Entity — Onset

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_onset.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `Onset`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.96

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 95
- Mentions scored (evidence-valid): 91
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9579

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.148 | 0.088 | 0.471 | 0.219 | 8 | 83 | 9 |
| semantic | 0.148 | 0.088 | 0.471 | 0.219 | 8 | 83 | 9 |
| benchmark | 0.130 | 0.077 | 0.412 | 0.194 | 7 | 84 | 10 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.824 (TP=14 FN=3)
- Overlap F1: 0.259
- Over-emission (overlap FP): 77
- Attribute agreement on overlaps: 1.000 (14/14)
