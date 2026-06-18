# ExECTv2 Hybrid Merged Benchmark-Overall Scorecard

- Generated: `2026-06-18`
- Split: `dev`
- JSON: `experiments\exectv2_hybrid_benchmark_overall_dev_20260618.json`
- Pipeline family: `exectv2_hybrid_benchmark_overall`
- Row count: 140
- Key families (hybrid verifier): Diagnosis, Investigations, Prescription, SeizureFrequency
- Deterministic fallback families: BirthHistory, EpilepsyCause, Onset, PatientHistory, WhenDiagnosed

## Overall Scores (vs paper 0.87 item / 0.90 letter)

| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.4984 | 0.7740 | 688 | 593 | 792 |
| semantic | 0.3890 | 0.6833 | 537 | 744 | 943 |
| benchmark | 0.3100 | 0.6454 | 428 | 853 | 1052 |

- Benchmark overall vs paper: per-item -0.5600, per-letter -0.2546

## Per-Entity Benchmark F1 vs Paper

| Entity | Source | Item F1 | Paper item F1 | Δ vs paper | Letter F1 | TP | FP | FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | rules | 0.5574 | 0.97 | -0.4126 | 0.7317 | 17 | 13 | 14 |
| Diagnosis | hybrid | 0.2834 | 0.85 | -0.5666 | 0.8000 | 121 | 328 | 284 |
| EpilepsyCause | rules | 0.5333 | 0.90 | -0.3667 | 0.5806 | 12 | 12 | 9 |
| Investigations | hybrid | 0.4835 | 0.95 | -0.4665 | 0.7385 | 66 | 71 | 70 |
| Onset | rules | 0.2857 | 0.96 | -0.6743 | 0.4167 | 5 | 13 | 12 |
| PatientHistory | rules | 0.2371 | 0.78 | -0.5429 | 0.5475 | 76 | 99 | 390 |
| Prescription | hybrid | 0.2477 | 0.87 | -0.6223 | 0.4671 | 55 | 183 | 151 |
| SeizureFrequency | hybrid | 0.3472 | 0.66 | -0.3128 | 0.6460 | 67 | 132 | 120 |
| WhenDiagnosed | rules | 0.8182 | 0.91 | -0.0918 | 0.9000 | 9 | 2 | 2 |

## Mention Counts

| Entity | Merged predicted mentions |
| --- | ---: |
| BirthHistory | 30 |
| Diagnosis | 449 |
| EpilepsyCause | 24 |
| Investigations | 137 |
| Onset | 18 |
| PatientHistory | 175 |
| Prescription | 238 |
| SeizureFrequency | 199 |
| WhenDiagnosed | 11 |

## Provenance

- BirthHistory: deterministic all-9 substrate
- Diagnosis: hybrid verifier `experiments\exectv2_hybrid_diagnosis_reconciler_v02_dev140_gpt41mini_20260618.jsonl`
- EpilepsyCause: deterministic all-9 substrate
- Investigations: hybrid verifier `experiments\exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.jsonl`
- Onset: deterministic all-9 substrate
- PatientHistory: deterministic all-9 substrate
- Prescription: hybrid verifier `experiments\exectv2_llm_med_inv_verifier_v01_dev140_gpt41mini_20260618.jsonl`
- SeizureFrequency: hybrid verifier `experiments\exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`
- WhenDiagnosed: deterministic all-9 substrate

## Reading

The benchmark layer is the only surface comparable to the published 0.87/0.90 headline (exact normalized phrase + all attributes + CUI). The phrase_only and semantic layers expose how much of the gap is phrase/attribute/CUI projection versus concept recall.
