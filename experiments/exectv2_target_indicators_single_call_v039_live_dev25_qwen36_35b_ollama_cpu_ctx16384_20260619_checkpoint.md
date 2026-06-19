# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v039_live_dev25_qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.39`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 137
- Mentions scored: 130
- Evidence-invalid dropped: 4

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
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.8812 | no | Diagnosis, SeizureFrequency, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.8763 | 0.8718 | 0.8810 | 37 | 5 | 5 | 0.0237 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.7843 | 0.8000 | 0.7692 | 20 | 5 | 6 | 0.1157 |
| exectv2_target_indicators_single_call | Prescription | 0.9600 | 0.9730 | 0.9474 | 36 | 1 | 2 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.8696 | 0.7692 | 1.0000 | 20 | 6 | 0 | 0.0304 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 5 | 5 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 7 | 5 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 2 | 1 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 0 | 6 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.8763 | 0.0237 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.7843 | 0.1157 |
| Prescription | exectv2_target_indicators_single_call | 0.9600 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.8696 | 0.0304 |
