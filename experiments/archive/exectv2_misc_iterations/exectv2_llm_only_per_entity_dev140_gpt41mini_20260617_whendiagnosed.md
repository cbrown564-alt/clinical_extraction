# ExECTv2 LLM-Only Per-Entity — WhenDiagnosed

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_whendiagnosed.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `WhenDiagnosed`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.91

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 44
- Mentions scored (evidence-valid): 44
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.073 | 0.045 | 0.182 | 0.087 | 2 | 42 | 9 |
| semantic | 0.073 | 0.045 | 0.182 | 0.087 | 2 | 42 | 9 |
| benchmark | 0.073 | 0.045 | 0.182 | 0.087 | 2 | 42 | 9 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 1.000 (TP=11 FN=0)
- Overlap F1: 0.400
- Over-emission (overlap FP): 33
- Attribute agreement on overlaps: 0.909 (10/11)
