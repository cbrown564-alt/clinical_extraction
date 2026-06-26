# ExECTv2 LLM-Only Per-Entity — PatientHistory

- JSONL: `experiments\exectv2_llm_only_per_entity_dev25_gpt41mini_20260617_patienthistory.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `PatientHistory`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Published per-item F1 target: 0.78

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 62
- Mentions scored (evidence-valid): 58
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9355

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.290 | 0.328 | 0.260 | 0.649 | 19 | 39 | 54 |
| semantic | 0.153 | 0.172 | 0.137 | 0.387 | 10 | 48 | 63 |
| benchmark | 0.092 | 0.103 | 0.082 | 0.333 | 6 | 52 | 67 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.370 (TP=27 FN=46)
- Overlap F1: 0.412
- Over-emission (overlap FP): 31
- Attribute agreement on overlaps: 0.370 (10/27)
