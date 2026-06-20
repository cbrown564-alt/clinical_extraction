# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v014_live_dev25_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.14`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 146
- Mentions scored: 121
- Evidence-invalid dropped: 25

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev25`
- Rows: `25`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.8349 | no | Diagnosis, SeizureFrequency |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.7729 | 0.8519 | 0.7073 | 29 | 4 | 12 | 0.1271 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.7059 | 0.7200 | 0.6923 | 18 | 7 | 8 | 0.1941 |
| exectv2_target_indicators_single_call | Prescription | 0.9211 | 0.9211 | 0.9211 | 35 | 3 | 3 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.9500 | 0.9500 | 0.9500 | 19 | 1 | 1 | 0.0000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 12 | 4 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 10 | 8 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 3 | 3 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 1 | 1 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.7729 | 0.1271 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.7059 | 0.1941 |
| Prescription | exectv2_target_indicators_single_call | 0.9211 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.9500 | 0.0000 |
