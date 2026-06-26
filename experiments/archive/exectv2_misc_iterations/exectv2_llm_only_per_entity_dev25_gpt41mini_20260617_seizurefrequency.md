# ExECTv2 LLM-Only Per-Entity — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_seizurefrequency.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `SeizureFrequency`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.66

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
| phrase_only | 0.552 | 0.593 | 0.516 | 0.750 | 16 | 11 | 15 |
| semantic | 0.172 | 0.185 | 0.161 | 0.400 | 5 | 22 | 26 |
| benchmark | 0.172 | 0.185 | 0.161 | 0.400 | 5 | 22 | 26 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.581 (TP=18 FN=13)
- Overlap F1: 0.621
- Over-emission (overlap FP): 9
- Attribute agreement on overlaps: 0.278 (5/18)
