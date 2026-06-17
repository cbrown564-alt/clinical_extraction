# ExECTv2 LLM-Only Per-Entity — Investigations

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_investigations.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.3`
- Entity: `Investigations`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.95

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 184
- Mentions scored (evidence-valid): 179
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9728

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.578 | 0.508 | 0.669 | 0.770 | 91 | 88 | 45 |
| semantic | 0.546 | 0.480 | 0.632 | 0.755 | 86 | 93 | 50 |
| benchmark | 0.489 | 0.430 | 0.566 | 0.723 | 77 | 102 | 59 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.890 (TP=121 FN=15)
- Overlap F1: 0.768
- Over-emission (overlap FP): 58
- Attribute agreement on overlaps: 0.942 (114/121)
