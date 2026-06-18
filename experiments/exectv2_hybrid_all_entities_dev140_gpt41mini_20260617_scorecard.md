# ExECTv2 GPT-First Reliability Scorecard (Phase E)

- Source: `experiments\exectv2_hybrid_all_entities_dev140_gpt41mini_20260617.jsonl`
- Split: `dev`  Letters: 140
- Candidate model: `openai/gpt-4.1-mini`  Rule augmentation: `False`

## Promotion gate

- Freeze targets: per-item 0.87 / per-letter 0.90 (benchmark, with-CUI).
- Benchmark per-item F1: 0.181  per-letter F1: 0.420
- **Gate met: False** — full-200 audit authorized: False.
- Dev evidence does NOT clear the freeze targets; the full-200 holdout audit is NOT authorized.

## Scorecard dimensions

| Dimension | Reading |
| --- | --- |
| Task correctness | semantic item F1 0.220 CI[0.196, 0.241]; benchmark item F1 0.181 CI[0.160, 0.201]; letter F1 0.420 |
| Candidate generation | source-near recall 0.528 |
| Faithfulness | evidence-routed 0 mentions |
| Schema reliability | scored 1326 / 1337 candidates |
| Benchmark format | semantic−benchmark item F1 +0.038; projection Δ -0.038 |
| Calibration/routing | routed 11 by reason {'no_frequency_attributes': 4, 'bare_nonzero_count': 2, 'duplicate_mention': 5} |
| Operational | candidates 1337, scored 1326, routed 11 |

## Robustness — per-entity benchmark item F1 vs published target

| Entity | Semantic F1 | Benchmark F1 | Published | Gap |
| --- | ---: | ---: | ---: | ---: |
| BirthHistory | 0.281 | 0.246 | 0.97 | -0.724 |
| Diagnosis | 0.243 | 0.172 | 0.85 | -0.678 |
| EpilepsyCause | 0.175 | 0.175 | 0.90 | -0.725 |
| Investigations | 0.548 | 0.490 | 0.95 | -0.460 |
| Onset | 0.148 | 0.130 | 0.96 | -0.830 |
| PatientHistory | 0.161 | 0.106 | 0.78 | -0.674 |
| Prescription | 0.174 | 0.174 | 0.87 | -0.696 |
| SeizureFrequency | 0.131 | 0.131 | 0.66 | -0.529 |
| WhenDiagnosed | 0.073 | 0.073 | 0.91 | -0.837 |
