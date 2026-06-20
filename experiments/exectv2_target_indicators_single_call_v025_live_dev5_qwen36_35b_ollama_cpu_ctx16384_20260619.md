# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v025_live_dev5_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.25`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Mentions raw: 29
- Mentions scored: 34
- Evidence-invalid dropped: 1

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
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.8657 | no | Diagnosis, SeizureFrequency, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.8000 | 0.8889 | 0.7273 | 8 | 1 | 3 | 0.1000 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.8750 | 0.8750 | 0.8750 | 7 | 1 | 1 | 0.0250 |
| exectv2_target_indicators_single_call | Prescription | 0.9412 | 1.0000 | 0.8889 | 8 | 0 | 1 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.8571 | 1.0000 | 0.7500 | 6 | 0 | 2 | 0.0429 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 3 | 1 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 1 | 1 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 1 | 0 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 2 | 0 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.8000 | 0.1000 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.8750 | 0.0250 |
| Prescription | exectv2_target_indicators_single_call | 0.9412 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.8571 | 0.0429 |
