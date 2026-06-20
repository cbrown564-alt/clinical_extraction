# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v015_live_dev25_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.15`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 138
- Mentions scored: 120
- Evidence-invalid dropped: 18

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev25`
- Rows: `25`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Headline Scoring Policy

| Indicator | Headline score used |
| --- | --- |
| Diagnosis | projected clinical-fact concept_only score after deterministic Diagnosis normalization/projection; one core fact per letter |
| SeizureFrequency | projected seizure-state clinical_headline score after deterministic frequency-state normalization/projection |
| Prescription | clinical_headline regimen score after deterministic medication normalization/projection |
| Investigations | clinical_headline modality/performed/result score after deterministic investigation normalization/projection |

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.8161 | no | Diagnosis, SeizureFrequency, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.7549 | 0.8438 | 0.6829 | 28 | 5 | 13 | 0.1451 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.7059 | 0.7200 | 0.6923 | 18 | 7 | 8 | 0.1941 |
| exectv2_target_indicators_single_call | Prescription | 0.9333 | 0.9459 | 0.9211 | 35 | 2 | 3 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.8500 | 0.8500 | 0.8500 | 17 | 3 | 3 | 0.0500 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 13 | 5 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 10 | 8 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 3 | 2 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 3 | 3 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.7549 | 0.1451 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.7059 | 0.1941 |
| Prescription | exectv2_target_indicators_single_call | 0.9333 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.8500 | 0.0500 |
