# ExECTv2 LLM-Only All Entities

- JSONL: `experiments\exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl`
- Prompt version: `exectv2_llm_only_all_entities_v0.1`
- Split: `full200_overall_audit`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 1492
- Mentions scored (evidence-valid): 1391
- Evidence-invalid dropped: 101
- Evidence validity rate: 0.9323

## Overall Scores

### semantic

- per-item: P=0.144 R=0.096 F1=0.115 (TP=201 FP=1190 FN=1891)
- per-letter: P=0.605 R=0.199 F1=0.299 (TP=176 FP=115 FN=709)

### benchmark

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=1391 FN=2092)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=115 FN=885)

### phrase_only

- per-item: P=0.184 R=0.122 F1=0.147 (TP=256 FP=1135 FN=1836)
- per-letter: P=0.658 R=0.250 F1=0.362 (TP=221 FP=115 FN=664)


## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.502 | 874 | 517 | 1218 | 0.569 (497/874) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| BirthHistory | 0.718 | 28 | 0.071 (2/28) |
| Diagnosis | 0.440 | 177 | 0.605 (107/177) |
| EpilepsyCause | 0.516 | 16 | 0.375 (6/16) |
| Investigations | 0.800 | 158 | 0.930 (147/158) |
| Onset | 0.301 | 11 | 0.636 (7/11) |
| PatientHistory | 0.264 | 122 | 0.328 (40/122) |
| Prescription | 0.710 | 230 | 0.687 (158/230) |
| SeizureFrequency | 0.523 | 123 | 0.187 (23/123) |
| WhenDiagnosed | 0.621 | 9 | 0.778 (7/9) |

## Per-Entity Semantic F1

| Entity | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: |
| BirthHistory | 0.97 | 0.000 | 0.000 |
| Diagnosis | 0.85 | 0.169 | 0.513 |
| EpilepsyCause | 0.90 | 0.032 | 0.056 |
| Investigations | 0.95 | 0.324 | 0.544 |
| Onset | 0.96 | 0.000 | 0.000 |
| PatientHistory | 0.78 | 0.011 | 0.053 |
| Prescription | 0.87 | 0.191 | 0.440 |
| SeizureFrequency | 0.66 | 0.004 | 0.012 |
| WhenDiagnosed | 0.91 | 0.000 | 0.000 |