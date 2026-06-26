# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_promptonly_dev3_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.1`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `prompt-only`
- Letters: 3

## Gate Summary

- Call failures: 0
- Parse/schema failures: 3
- Mentions raw: 0
- Mentions scored: 0
- Evidence-invalid dropped: 0

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev3`
- Rows: `3`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.0000 | no | Diagnosis, SeizureFrequency, Prescription, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 12 | 0.9000 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 6 | 0.9000 |
| exectv2_target_indicators_single_call | Prescription | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 5 | 0.9000 |
| exectv2_target_indicators_single_call | Investigations | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 5 | 0.9000 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 12 | 0 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 6 | 0 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 5 | 0 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 5 | 0 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.0000 | 0.9000 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.0000 | 0.9000 |
| Prescription | exectv2_target_indicators_single_call | 0.0000 | 0.9000 |
| Investigations | exectv2_target_indicators_single_call | 0.0000 | 0.9000 |
