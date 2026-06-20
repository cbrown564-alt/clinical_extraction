# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v09_live_dev25_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.9`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 131
- Mentions scored: 117
- Evidence-invalid dropped: 14

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev25`
- Rows: `25`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.7194 | no | Diagnosis, SeizureFrequency, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.5636 | 0.5806 | 0.5476 | 23 | 13 | 19 | 0.3364 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.6207 | 0.6667 | 0.5806 | 18 | 9 | 13 | 0.2793 |
| exectv2_target_indicators_single_call | Prescription | 0.9351 | 0.9231 | 0.9474 | 36 | 3 | 2 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.7317 | 0.7143 | 0.7500 | 15 | 6 | 5 | 0.1683 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 19 | 13 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 13 | 9 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 2 | 3 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 5 | 6 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.5636 | 0.3364 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.6207 | 0.2793 |
| Prescription | exectv2_target_indicators_single_call | 0.9351 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.7317 | 0.1683 |
