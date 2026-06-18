# ExECTv2 Hybrid Merged Benchmark-Overall Scorecard

- Generated: `2026-06-18`
- Split: `dev`
- JSON: `experiments\exectv2_hybrid_benchmark_overall_bestof_dev_20260618.json`
- Pipeline family: `exectv2_hybrid_benchmark_overall`
- Row count: 140
- Key families (hybrid verifier): Investigations
- Deterministic fallback families: BirthHistory, Diagnosis, EpilepsyCause, Onset, PatientHistory, Prescription, SeizureFrequency, WhenDiagnosed

## Overall Scores (vs paper 0.87 item / 0.90 letter)

| Layer | Per-item F1 | Per-letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.4549 | 0.7541 | 555 | 405 | 925 |
| semantic | 0.4008 | 0.7037 | 489 | 471 | 991 |
| benchmark | 0.3877 | 0.6972 | 473 | 487 | 1007 |

- Benchmark overall vs paper: per-item -0.4823, per-letter -0.2028

## Per-Entity Benchmark F1 vs Paper

| Entity | Source | Item F1 | Paper item F1 | Δ vs paper | Letter F1 | TP | FP | FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BirthHistory | rules | 0.5574 | 0.97 | -0.4126 | 0.7317 | 17 | 13 | 14 |
| Diagnosis | rules | 0.3216 | 0.85 | -0.5284 | 0.7500 | 91 | 70 | 314 |
| EpilepsyCause | rules | 0.5333 | 0.90 | -0.3667 | 0.5806 | 12 | 12 | 9 |
| Investigations | hybrid | 0.4835 | 0.95 | -0.4665 | 0.7385 | 66 | 71 | 70 |
| Onset | rules | 0.2857 | 0.96 | -0.6743 | 0.4167 | 5 | 13 | 12 |
| PatientHistory | rules | 0.2371 | 0.78 | -0.5429 | 0.5475 | 76 | 99 | 390 |
| Prescription | rules | 0.3020 | 0.87 | -0.5680 | 0.5223 | 61 | 137 | 145 |
| SeizureFrequency | rules | 0.6921 | 0.66 | +0.0321 | 0.9247 | 136 | 70 | 51 |
| WhenDiagnosed | rules | 0.8182 | 0.91 | -0.0918 | 0.9000 | 9 | 2 | 2 |

## Mention Counts

| Entity | Merged predicted mentions |
| --- | ---: |
| BirthHistory | 30 |
| Diagnosis | 161 |
| EpilepsyCause | 24 |
| Investigations | 137 |
| Onset | 18 |
| PatientHistory | 175 |
| Prescription | 198 |
| SeizureFrequency | 206 |
| WhenDiagnosed | 11 |

## Provenance

- BirthHistory: deterministic all-9 substrate
- Diagnosis: deterministic all-9 substrate
- EpilepsyCause: deterministic all-9 substrate
- Investigations: hybrid verifier `experiments\exectv2_llm_investigations_verifier_v01_dev140_gpt41mini_20260618.jsonl`
- Onset: deterministic all-9 substrate
- PatientHistory: deterministic all-9 substrate
- Prescription: deterministic all-9 substrate
- SeizureFrequency: deterministic all-9 substrate
- WhenDiagnosed: deterministic all-9 substrate

## Reading

The benchmark layer is the only surface comparable to the published 0.87/0.90 headline (exact normalized phrase + all attributes + CUI). The phrase_only and semantic layers expose how much of the gap is phrase/attribute/CUI projection versus concept recall.
