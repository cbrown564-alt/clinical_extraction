# ExECTv2 LLM-Only All Entities

- JSONL: `experiments\exectv2_llm_only_all_entities_dev25_gpt41mini_20260612.jsonl`
- Prompt version: `exectv2_llm_only_all_entities_v0.1`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 170
- Mentions scored (evidence-valid): 162
- Evidence-invalid dropped: 8
- Evidence validity rate: 0.9529

## Overall Scores

### semantic

- per-item: P=0.130 R=0.092 F1=0.108 (TP=21 FP=141 FN=207)
- per-letter: P=0.548 R=0.172 F1=0.262 (TP=17 FP=14 FN=82)

### benchmark

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=162 FN=228)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=14 FN=99)

### phrase_only

- per-item: P=0.228 R=0.162 F1=0.190 (TP=37 FP=125 FN=191)
- per-letter: P=0.682 R=0.303 F1=0.420 (TP=30 FP=14 FN=69)


## Per-Entity Semantic F1

| Entity | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: |
| BirthHistory | 0.97 | 0.000 | 0.000 |
| Diagnosis | 0.85 | 0.123 | 0.357 |
| EpilepsyCause | 0.90 | 0.000 | 0.000 |
| Investigations | 0.95 | 0.542 | 0.720 |
| Onset | 0.96 | 0.000 | 0.000 |
| PatientHistory | 0.78 | 0.000 | 0.000 |
| Prescription | 0.87 | 0.067 | 0.231 |
| SeizureFrequency | 0.66 | 0.000 | 0.000 |
| WhenDiagnosed | 0.91 | 0.000 | 0.000 |