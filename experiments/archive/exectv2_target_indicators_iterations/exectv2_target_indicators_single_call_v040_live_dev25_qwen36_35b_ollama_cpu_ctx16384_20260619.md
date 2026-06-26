# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v040_live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.40`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Mentions raw: 136
- Mentions scored: 130
- Evidence-invalid dropped: 2

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev25`
- Rows: `25`
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
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.8840 | no | Diagnosis, SeizureFrequency, Prescription |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.8792 | 0.8571 | 0.9024 | 37 | 6 | 4 | 0.0208 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.8235 | 0.8400 | 0.8077 | 21 | 4 | 5 | 0.0765 |
| exectv2_target_indicators_single_call | Prescription | 0.8800 | 0.8919 | 0.8684 | 33 | 4 | 5 | 0.0200 |
| exectv2_target_indicators_single_call | Investigations | 0.9756 | 0.9524 | 1.0000 | 20 | 1 | 0 | 0.0000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 4 | 6 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 6 | 4 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 5 | 4 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 0 | 1 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.8792 | 0.0208 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.8235 | 0.0765 |
| Prescription | exectv2_target_indicators_single_call | 0.8800 | 0.0200 |
| Investigations | exectv2_target_indicators_single_call | 0.9756 | 0.0000 |
