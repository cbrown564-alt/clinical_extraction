# ExECTv2 LLM-Only Per-Entity — SeizureFrequency

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_seizurefrequency.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.3`
- Entity: `SeizureFrequency`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.66

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 173
- Mentions scored (evidence-valid): 171
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9884

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.469 | 0.491 | 0.449 | 0.703 | 84 | 87 | 103 |
| semantic | 0.134 | 0.140 | 0.128 | 0.298 | 24 | 147 | 163 |
| benchmark | 0.134 | 0.140 | 0.128 | 0.298 | 24 | 147 | 163 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.642 (TP=120 FN=67)
- Overlap F1: 0.670
- Over-emission (overlap FP): 51
- Attribute agreement on overlaps: 0.225 (27/120)
