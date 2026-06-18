# ExECTv2 LLM-Only Per-Entity — WhenDiagnosed

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_whendiagnosed.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `WhenDiagnosed`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.91

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 6
- Mentions scored (evidence-valid): 6
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 6 | 0 |
| semantic | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 6 | 0 |
| benchmark | 0.000 | 0.000 | 0.000 | 0.000 | 0 | 6 | 0 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.000 (TP=0 FN=0)
- Overlap F1: 0.000
- Over-emission (overlap FP): 6
- Attribute agreement on overlaps: 0.000 (0/0)
