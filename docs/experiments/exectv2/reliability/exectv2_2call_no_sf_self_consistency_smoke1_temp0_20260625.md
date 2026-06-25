# ExECTv2 2-Call GPT-4.1-Mini Self-Consistency

- Generated: `2026-06-25`
- Panel: `smoke1_temp0`
- Candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`
- Model: `openai/gpt-4.1-mini`
- Temperatures: `0.0, 0.0`
- Repeats: `2`
- Rows: `1`
- Family cells: `4`
- Row inspection policy: `aggregate_only_no_failure_ledger`
- Claim boundary: Selected GPT-4.1-mini lean-candidate self-consistency panel. Final readout is aggregate-only; saved JSONL artifacts preserve provenance but are not a full-200 row-level failure-analysis ledger.

## Agreement And Entropy

| Metric | Value |
| --- | ---: |
| Pairwise comparisons | 1 |
| Exact family-cell agreement | 0.7500 |
| Mean pairwise Jaccard | 0.7500 |
| Mean semantic entropy | 0.2500 |
| Non-zero entropy cells | 1 |

## Per-Family Stability

| Family | Exact agreement | Mean Jaccard | Mean entropy | Non-zero entropy cells |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 1.0000 | 1.0000 | 0.0000 | 0 |
| SeizureFrequency | 1.0000 | 1.0000 | 0.0000 | 0 |
| Prescription | 1.0000 | 1.0000 | 0.0000 | 0 |
| Investigations | 0.0000 | 0.0000 | 1.0000 | 1 |

## Majority Agreement Correctness

| Majority top/k | Cells | Exact-correct majority | Accuracy |
| --- | ---: | ---: | ---: |
| 2/2 | 3 | 1 | 0.3333 |
| 1/2 | 1 | 1 | 1.0000 |

## Run Health

| Artifact | Rows | Call failures | Parse/schema failures | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| `experiments/exectv2_2call_no_sf_self_consistency_smoke1_temp0_r1_temp0p0_20260625_assembly.jsonl` | 1 | 0 | 0 | 1.0000 |
| `experiments/exectv2_2call_no_sf_self_consistency_smoke1_temp0_r2_temp0p0_20260625_assembly.jsonl` | 1 | 0 | 0 | 1.0000 |

## Producer Raw-Output Variation

| Producer | Rows compared | Mean unique raw outputs / row | Rows with variation |
| --- | ---: | ---: | ---: |
| structured_key_family_event_ledger | 1 | 2.0000 | 1 |
| diagnosis_decomposer | 1 | 2.0000 | 1 |

## Interpretation

Exact family-cell agreement is 0.7500 with mean semantic entropy 0.2500. The strongest agreement bucket is 2/2 with correctness 0.3333. Raw producer outputs vary across repeats, so stable clinical-headline cells should be read as decision stability rather than cache reuse. Interpret high agreement as reliability only where the majority-correctness curve also stays high; unanimous-but-wrong cells are the ExECTv2 analogue of Gan's confident residual.

## Artifacts

- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_smoke1_temp0_r1_temp0p0_20260625_assembly.jsonl`
- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_smoke1_temp0_r2_temp0p0_20260625_assembly.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_smoke1_temp0_r1_temp0p0_20260625_structured.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_smoke1_temp0_r2_temp0p0_20260625_structured.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_smoke1_temp0_r1_temp0p0_20260625_diagnosis_decomposer.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_smoke1_temp0_r2_temp0p0_20260625_diagnosis_decomposer.jsonl`
