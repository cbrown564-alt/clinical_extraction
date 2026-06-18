# ExECTv2 Target Indicators Single-Call Run

- JSONL: `experiments\exectv2_target_indicators_single_call_v03_live_dev10_gpt41mini_20260619.jsonl`
- Prompt version: `exectv2_target_indicators_single_call_v0.3`
- Pipeline family: `exectv2_target_indicators_single_call`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 10

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 60
- Mentions scored: 58
- Evidence-invalid dropped: 2

# ExECTv2 ADR 0030 Target Indicator Report

- Source: `exectv2_target_indicators_single_call`
- Split/stage: `dev` / `dev10`
- Rows: `10`
- Target F1: `>0.900` for each indicator
- ADR: `docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md`

## Candidate Readout

| Candidate | Ownership | Overall target F1 | Clears all four? | Blocking indicators |
| --- | --- | ---: | --- | --- |
| exectv2_target_indicators_single_call | `llm_first_with_deterministic_normalization_projection` | 0.6377 | no | Diagnosis, SeizureFrequency, Investigations |

## Indicator Scores

| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 0.3810 | 0.5714 | 0.2857 | 8 | 6 | 20 | 0.5190 |
| exectv2_target_indicators_single_call | SeizureFrequency | 0.5405 | 0.6667 | 0.4545 | 10 | 5 | 12 | 0.3595 |
| exectv2_target_indicators_single_call | Prescription | 0.9143 | 0.8889 | 0.9412 | 16 | 2 | 1 | 0.0000 |
| exectv2_target_indicators_single_call | Investigations | 0.8333 | 0.8333 | 0.8333 | 10 | 2 | 2 | 0.0667 |

## Error Analysis

| Candidate | Indicator | candidate_miss | wrong_detail_selection | projection_gap | evidence_failure |
| --- | --- | ---: | ---: | ---: | ---: |
| exectv2_target_indicators_single_call | Diagnosis | 20 | 6 | 0 | 0 |
| exectv2_target_indicators_single_call | SeizureFrequency | 12 | 5 | 0 | 0 |
| exectv2_target_indicators_single_call | Prescription | 1 | 2 | 0 | 0 |
| exectv2_target_indicators_single_call | Investigations | 2 | 2 | 0 | 0 |

## Best Current Indicator Scores

| Indicator | Best candidate | F1 | Shortfall |
| --- | --- | ---: | ---: |
| Diagnosis | exectv2_target_indicators_single_call | 0.3810 | 0.5190 |
| SeizureFrequency | exectv2_target_indicators_single_call | 0.5405 | 0.3595 |
| Prescription | exectv2_target_indicators_single_call | 0.9143 | 0.0000 |
| Investigations | exectv2_target_indicators_single_call | 0.8333 | 0.0667 |
