# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v08_live_dev25_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.8`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 128
- Mentions scored: 116
- Evidence-invalid dropped: 12

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev25`
- Rows: `25`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.7303 | no | Diagnosis, SeizureFrequency, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.5879 | 0.5806 | 0.5952 | 25 | 13 | 17 | 0.3121 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.6552 | 0.7037 | 0.6129 | 19 | 8 | 12 | 0.2448 |
| exectv2_target_indicators_single_call | Prescription | 0.9474 | 0.9474 | 0.9474 | 36 | 2 | 2 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.6829 | 0.6667 | 0.7000 | 14 | 7 | 6 | 0.2171 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 17 | 13 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 12 | 8 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 2 | 2 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 6 | 7 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.5879 | 0.3121 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.6552 | 0.2448 |
| Prescription | exectv2_target_indicators_single_call | 0.9474 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.6829 | 0.2171 |
