> **Superseded for navigation —** canonical summary: [`SELF_CONSISTENCY_RELIABILITY_CANON.md`](../../../canon/workstreams/SELF_CONSISTENCY_RELIABILITY_CANON.md). Full detail retained below.

# ExECTv2 2-Call GPT-4.1-Mini Self-Consistency

- Generated: `2026-06-25`
- Panel: `entropy_dev140_temps`
- Candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`
- Model: `openai/gpt-4.1-mini`
- Temperatures: `0.3, 0.5, 0.7, 1.0`
- Repeats: `4`
- Rows: `140`
- Family cells: `560`
- Row inspection policy: `aggregate_only_no_failure_ledger`
- Claim boundary: Selected GPT-4.1-mini lean-candidate self-consistency panel. Final readout is aggregate-only; saved JSONL artifacts preserve provenance but are not a full-200 row-level failure-analysis ledger.

> **Temperature panel.** Repeats use varying temperatures, so entropy and agreement measure semantic stability under sampled live calls rather than temp-0 reproducibility.

## Agreement And Entropy

| Metric | Value |
| --- | ---: |
| Pairwise comparisons | 6 |
| Exact family-cell agreement | 0.8857 |
| Mean pairwise Jaccard | 0.9284 |
| Mean semantic entropy | 0.1905 |
| Non-zero entropy cells | 107 |

## Per-Family Stability

| Family | Exact agreement | Mean Jaccard | Mean entropy | Non-zero entropy cells |
| --- | ---: | ---: | ---: | ---: |
| Diagnosis | 0.8155 | 0.9107 | 0.3069 | 42 |
| SeizureFrequency | 0.8333 | 0.8911 | 0.2792 | 39 |
| Prescription | 1.0000 | 1.0000 | 0.0000 | 0 |
| Investigations | 0.8940 | 0.9119 | 0.1757 | 26 |

## Majority Agreement Correctness

| Majority top/k | Cells | Exact-correct majority | Accuracy |
| --- | ---: | ---: | ---: |
| 4/4 | 453 | 359 | 0.7925 |
| 3/4 | 68 | 24 | 0.3529 |
| 2/4 | 36 | 16 | 0.4444 |
| 1/4 | 3 | 1 | 0.3333 |

## Run Health

| Artifact | Rows | Call failures | Parse/schema failures | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_assembly.jsonl` | 140 | 0 | 0 | 1.0000 |
| `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_assembly.jsonl` | 140 | 0 | 0 | 1.0000 |
| `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r3_temp0p7_20260625_assembly.jsonl` | 140 | 0 | 0 | 1.0000 |
| `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r4_temp1p0_20260625_assembly.jsonl` | 140 | 0 | 0 | 1.0000 |

## Producer Raw-Output Variation

| Producer | Rows compared | Mean unique raw outputs / row | Rows with variation |
| --- | ---: | ---: | ---: |
| structured_key_family_event_ledger | 140 | 3.9500 | 139 |
| diagnosis_decomposer | 140 | 3.7500 | 130 |

## Interpretation

Exact family-cell agreement is 0.8857 with mean semantic entropy 0.1905. The strongest agreement bucket is 4/4 with correctness 0.7925. Raw producer outputs vary across repeats, so stable clinical-headline cells should be read as decision stability rather than cache reuse. Interpret high agreement as reliability only where the majority-correctness curve also stays high; unanimous-but-wrong cells are the ExECTv2 analogue of Gan's confident residual.

## Artifacts

- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_assembly.jsonl`
- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_assembly.jsonl`
- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r3_temp0p7_20260625_assembly.jsonl`
- Assembly JSONL: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r4_temp1p0_20260625_assembly.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_structured.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_structured.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r3_temp0p7_20260625_structured.jsonl`
- structured_key_family_event_ledger: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r4_temp1p0_20260625_structured.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_diagnosis_decomposer.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_diagnosis_decomposer.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r3_temp0p7_20260625_diagnosis_decomposer.jsonl`
- diagnosis_decomposer: `experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r4_temp1p0_20260625_diagnosis_decomposer.jsonl`
