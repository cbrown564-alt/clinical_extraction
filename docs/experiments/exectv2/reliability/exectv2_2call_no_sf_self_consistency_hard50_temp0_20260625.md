# ExECTv2 2-Call GPT-4.1-Mini Self-Consistency

- Generated: `2026-06-25`
- Panel: `hard50_temp0`
- Candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`
- Model: `openai/gpt-4.1-mini`
- Temperatures: `0.0, 0.0, 0.0, 0.0`
- Repeats: `4`
- Rows: `50`
- Family cells: `200`
- Row inspection policy: `aggregate_only_no_failure_ledger`
- Claim boundary: Selected GPT-4.1-mini lean-candidate self-consistency panel. Final readout is aggregate-only; saved JSONL artifacts preserve provenance but are not a full-200 row-level failure-analysis ledger.

> **Temperature caveat.** All repeats use temperature `0`, so this panel measures reproducibility/decision stability under repeated live calls, not varying-temperature semantic self-consistency. The varying-temperature entropy panel is the direct ExECTv2 analogue of Gan P2.1.

## Agreement And Entropy

| Metric | Value |
| --- | ---: |
| Pairwise comparisons | 6 |
| Exact family-cell agreement | 0.9217 |
| Mean pairwise Jaccard | 0.9485 |
| Mean semantic entropy | 0.1261 |
| Non-zero entropy cells | 28 |

## Per-Family Stability

| Family | Exact agreement | Mean Jaccard | Mean entropy | Non-zero entropy cells |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0.8767 | 0.9475 | 0.1985 | 12 |
| SeizureFrequency | 0.8667 | 0.8914 | 0.2174 | 11 |
| Prescription | 1.0000 | 1.0000 | 0.0000 | 0 |
| Investigations | 0.9433 | 0.9550 | 0.0887 | 5 |

## Majority Agreement Correctness

| Majority top/k | Cells | Exact-correct majority | Accuracy |
| --- | ---: | ---: | ---: |
| 4/4 | 172 | 142 | 0.8256 |
| 3/4 | 20 | 10 | 0.5000 |
| 2/4 | 8 | 1 | 0.1250 |

## Run Health

| Artifact | Rows | Call failures | Parse/schema failures | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r1_temp0p0_20260625_assembly.jsonl` | 50 | 0 | 0 | 1.0000 |
| `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r2_temp0p0_20260625_assembly.jsonl` | 50 | 0 | 0 | 1.0000 |
| `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_assembly.jsonl` | 50 | 0 | 0 | 1.0000 |
| `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r4_temp0p0_20260625_assembly.jsonl` | 50 | 0 | 0 | 1.0000 |

## Producer Raw-Output Variation

| Producer | Rows compared | Mean unique raw outputs / row | Rows with variation |
| --- | ---: | ---: | ---: |
| diagnosis_decomposer | 50 | 3.0600 | 42 |
| structured_key_family_event_ledger | 50 | 3.6000 | 47 |

## Interpretation

Exact family-cell agreement is 0.9217 with mean semantic entropy 0.1261. The strongest agreement bucket is 4/4 with correctness 0.8256. Raw producer outputs vary across repeats, so stable clinical-headline cells should be read as decision stability rather than cache reuse. Interpret high agreement as reliability only where the majority-correctness curve also stays high; unanimous-but-wrong cells are the ExECTv2 analogue of Gan's confident residual.

## Artifacts

- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r1_temp0p0_20260625_assembly.jsonl`
- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r2_temp0p0_20260625_assembly.jsonl`
- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_assembly.jsonl`
- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r4_temp0p0_20260625_assembly.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r1_temp0p0_20260625_diagnosis_decomposer.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r2_temp0p0_20260625_diagnosis_decomposer.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_diagnosis_decomposer.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r4_temp0p0_20260625_diagnosis_decomposer.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r1_temp0p0_20260625_structured.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r2_temp0p0_20260625_structured.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_structured.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_hard50_temp0_r4_temp0p0_20260625_structured.jsonl`
