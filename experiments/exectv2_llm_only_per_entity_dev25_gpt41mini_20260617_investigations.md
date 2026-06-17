# ExECTv2 LLM-Only Per-Entity — Investigations

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_investigations.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.3`
- Entity: `Investigations`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.95

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 27
- Mentions scored (evidence-valid): 27
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.553 | 0.481 | 0.650 | 0.640 | 13 | 14 | 7 |
| semantic | 0.511 | 0.444 | 0.600 | 0.640 | 12 | 15 | 8 |
| benchmark | 0.511 | 0.444 | 0.600 | 0.640 | 12 | 15 | 8 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.950 (TP=19 FN=1)
- Overlap F1: 0.808
- Over-emission (overlap FP): 8
- Attribute agreement on overlaps: 0.947 (18/19)
