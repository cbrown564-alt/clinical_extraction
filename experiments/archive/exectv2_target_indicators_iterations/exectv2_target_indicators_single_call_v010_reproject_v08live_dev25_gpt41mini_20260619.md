# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v010_reproject_v08live_dev25_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.10`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `no-call-reproject`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 128
- Mentions scored: 109
- Evidence-invalid dropped: 19

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev25`
- Rows: `25`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.8215 | no | Diagnosis, SeizureFrequency, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.7690 | 0.8800 | 0.6829 | 28 | 3 | 13 | 0.1310 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.6897 | 0.7407 | 0.6452 | 20 | 7 | 11 | 0.2103 |
| exectv2_target_indicators_single_call | Prescription | 0.9474 | 0.9474 | 0.9474 | 36 | 2 | 2 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.8718 | 0.8947 | 0.8500 | 17 | 2 | 3 | 0.0282 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 13 | 3 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 12 | 8 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 2 | 2 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 3 | 2 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.7690 | 0.1310 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.6897 | 0.2103 |
| Prescription | exectv2_target_indicators_single_call | 0.9474 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.8718 | 0.0282 |
