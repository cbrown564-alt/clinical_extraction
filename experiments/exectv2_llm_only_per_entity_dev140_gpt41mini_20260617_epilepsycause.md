# ExECTv2 LLM-Only Per-Entity — EpilepsyCause

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_epilepsycause.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `EpilepsyCause`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.90

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 60
- Mentions scored (evidence-valid): 59
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9833

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.200 | 0.136 | 0.381 | 0.267 | 8 | 51 | 13 |
| semantic | 0.175 | 0.119 | 0.333 | 0.237 | 7 | 52 | 14 |
| benchmark | 0.175 | 0.119 | 0.333 | 0.237 | 7 | 52 | 14 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.809 (TP=17 FN=4)
- Overlap F1: 0.425
- Over-emission (overlap FP): 42
- Attribute agreement on overlaps: 0.824 (14/17)
