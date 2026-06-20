# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v016_reproject_v014live_dev25_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.16`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `no-call-reproject`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 146
- Mentions scored: 132
- Evidence-invalid dropped: 14

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
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.9017 | no | Diagnosis, SeizureFrequency |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.8971 | 0.8919 | 0.9024 | 37 | 4 | 4 | 0.0029 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.8400 | 0.8750 | 0.8077 | 21 | 3 | 5 | 0.0600 |
| exectv2_target_indicators_single_call | Prescription | 0.9211 | 0.9211 | 0.9211 | 35 | 3 | 3 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.9500 | 0.9500 | 0.9500 | 19 | 1 | 1 | 0.0000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 4 | 4 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 7 | 4 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 3 | 3 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 1 | 1 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.8971 | 0.0029 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.8400 | 0.0600 |
| Prescription | exectv2_target_indicators_single_call | 0.9211 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.9500 | 0.0000 |
