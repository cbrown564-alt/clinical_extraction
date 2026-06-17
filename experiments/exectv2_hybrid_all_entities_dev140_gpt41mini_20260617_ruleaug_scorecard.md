# ExECTv2 GPT-First Reliability Scorecard (Phase E)

- Source: `experiments\exectv2_hybrid_all_entities_dev140_gpt41mini_20260617_ruleaug.jsonl`
- Split: `dev`  Letters: 140
- Candidate model: `openai/gpt-4.1-mini`  Rule augmentation: `True`

## Promotion gate

- Freeze targets: per-item 0.87 / per-letter 0.90 (benchmark, with-CUI).
- Benchmark per-item F1: 0.312  per-letter F1: 0.658
- **Gate met: False** — full-200 audit authorized: False.
- Dev evidence does NOT clear the freeze targets; the full-200 holdout audit is NOT authorized.

## Scorecard dimensions

| Dimension | Reading |
| --- | --- |
| Task correctness | semantic item F1 0.344 CI[0.324, 0.365]; benchmark item F1 0.312 CI[0.294, 0.333]; letter F1 0.658 |
| Candidate generation | source-near recall 0.680 |
| Faithfulness | evidence-routed 0 mentions |
| Schema reliability | scored 2083 / 2347 candidates |
| Benchmark format | semantic−benchmark item F1 +0.032; projection Δ -0.032 |
| Calibration/routing | routed 264 by reason {'duplicate_mention': 258, 'no_frequency_attributes': 4, 'bare_nonzero_count': 2} |
| Operational | candidates 2347, scored 2083, routed 264 |

## Robustness — per-entity benchmark item F1 vs published target

| Entity | Semantic F1 | Benchmark F1 | Published | Gap |
| --- | ---: | ---: | ---: | ---: |
| BirthHistory | 0.538 | 0.462 | 0.97 | -0.508 |
| Diagnosis | 0.347 | 0.284 | 0.85 | -0.566 |
| EpilepsyCause | 0.274 | 0.274 | 0.90 | -0.626 |
| Investigations | 0.444 | 0.399 | 0.95 | -0.551 |
| Onset | 0.142 | 0.124 | 0.96 | -0.836 |
| PatientHistory | 0.244 | 0.197 | 0.78 | -0.583 |
| Prescription | 0.307 | 0.307 | 0.87 | -0.563 |
| SeizureFrequency | 0.524 | 0.524 | 0.66 | -0.136 |
| WhenDiagnosed | 0.333 | 0.333 | 0.91 | -0.577 |
