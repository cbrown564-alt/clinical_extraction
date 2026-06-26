# ExECTv2 LLM-Only Per-Entity — BirthHistory

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_birthhistory.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `BirthHistory`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.97

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 4
- Mentions scored (evidence-valid): 4
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.600 | 0.750 | 0.500 | 0.857 | 3 | 1 | 3 |
| semantic | 0.200 | 0.250 | 0.167 | 0.400 | 1 | 3 | 5 |
| benchmark | 0.200 | 0.250 | 0.167 | 0.400 | 1 | 3 | 5 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.500 (TP=3 FN=3)
- Overlap F1: 0.600
- Over-emission (overlap FP): 1
- Attribute agreement on overlaps: 0.333 (1/3)
