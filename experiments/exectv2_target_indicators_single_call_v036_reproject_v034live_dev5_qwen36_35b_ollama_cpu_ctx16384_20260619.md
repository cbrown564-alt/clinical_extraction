# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v036_reproject_v034live_dev5_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.36`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `reproject_v034_live_raw`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 35
- Mentions scored: 36
- Evidence-invalid dropped: 2

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev5`
- Rows: `5`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Headline Scoring Policy

| Indicator | Headline score used |
| --- | --- |
| Diagnosis | projected clinical-fact concept_only score after deterministic Diagnosis normalization/projection; scored as projected core facts per letter |
| SeizureFrequency | projected seizure-state clinical_headline score after deterministic frequency-state normalization/projection |
| Prescription | clinical_headline regimen score after deterministic medication normalization/projection |
| Investigations | clinical_headline modality/performed/result score after deterministic investigation normalization/projection |

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.9275 | no | Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.9524 | 1.0000 | 0.9091 | 10 | 0 | 1 | 0.0000 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.9333 | 1.0000 | 0.8750 | 7 | 0 | 1 | 0.0000 |
| exectv2_target_indicators_single_call | Prescription | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.8000 | 0.8571 | 0.7500 | 6 | 1 | 2 | 0.1000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 1 | 0 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 2 | 1 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 0 | 0 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 2 | 1 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.9524 | 0.0000 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.9333 | 0.0000 |
| Prescription | exectv2_target_indicators_single_call | 1.0000 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.8000 | 0.1000 |
