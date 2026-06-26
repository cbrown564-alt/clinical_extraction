# ExECTv2 LLM-Only All Entities

- JSONL: `experiments\exectv2_llm_only_all_entities_dev140_gpt41mini_20260612.jsonl`
- Prompt version: `exectv2_llm_only_all_entities_v0.1`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 1049
- Mentions scored (evidence-valid): 988
- Evidence-invalid dropped: 61
- Evidence validity rate: 0.9418

## Overall Scores

### semantic

- per-item: P=0.108 R=0.072 F1=0.087 (TP=107 FP=881 FN=1373)
- per-letter: P=0.516 R=0.153 F1=0.236 (TP=94 FP=88 FN=520)

### benchmark

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=988 FN=1480)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=88 FN=614)

### phrase_only

- per-item: P=0.179 R=0.120 F1=0.143 (TP=177 FP=811 FN=1303)
- per-letter: P=0.625 R=0.239 F1=0.346 (TP=147 FP=88 FN=467)


## Per-Entity Semantic F1

| Entity | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: |
| BirthHistory | 0.97 | 0.000 | 0.000 |
| Diagnosis | 0.85 | 0.176 | 0.533 |
| EpilepsyCause | 0.90 | 0.000 | 0.000 |
| Investigations | 0.95 | 0.328 | 0.548 |
| Onset | 0.96 | 0.000 | 0.000 |
| PatientHistory | 0.78 | 0.006 | 0.030 |
| Prescription | 0.87 | 0.026 | 0.087 |
| SeizureFrequency | 0.66 | 0.000 | 0.000 |
| WhenDiagnosed | 0.91 | 0.000 | 0.000 |