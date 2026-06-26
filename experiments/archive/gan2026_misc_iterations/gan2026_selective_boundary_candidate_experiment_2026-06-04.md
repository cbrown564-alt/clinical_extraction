# Gan 2026 Selective Boundary-Candidate Experiment

This controlled validation-development run uses the predeclared 22-row boundary-candidate rescue slice. The model proposes candidate facts only; candidate outputs are gated and deterministically normalized for component accounting, not used as final labels.

## Outcome

The live proposer produced parseable outputs for 20/22 rows and retained at least one gated candidate for 20/22 rows. Exact-label candidate recall was 15/22; Purist-category candidate recall was 16/22.

## Claim Boundary

Validation-development controlled component experiment only. Outputs are candidate proposals, not final labels; no locked-test inspection, whole-pipeline promotion, or benchmark-comparable claim is authorized.

## Artifacts

- JSONL: `experiments/gan2026_selective_boundary_candidate_experiment_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_boundary_candidate_experiment_2026-06-04.json`
- Predeclaration: `experiments/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| call ok rows | 22 |
| call error rows | 0 |
| parse ok rows | 20 |
| parse error rows | 2 |
| rows with retained candidate | 20 |
| rows with gold exact label recall | 15 |
| rows with gold purist recall | 16 |
| rows with saved rescue evidence overlap | 15 |
| rows all retained evidence exact | 20 |
| total retained candidates | 55 |
| median retained candidates | 3.000 |
| p90 retained candidates | 4.000 |
| total rejected candidates | 24 |

## Gate Failures

| Failure | Count |
| --- | ---: |
| `missing_seizure_free_duration` | 4 |
| `non_exact_evidence` | 9 |
| `unrenderable_candidate` | 15 |

## Row Outcomes

| Row | Gold | Exact recall | Purist recall | Retained | Rejected | Notes |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 338 | `multiple per month` | yes | yes | 3 | 1 |  |
| 1707 | `multiple per week` | yes | yes | 4 | 0 |  |
| 3356 | `unknown` | yes | yes | 4 | 0 |  |
| 5974 | `unknown` | yes | yes | 4 | 0 |  |
| 6077 | `unknown` | no | no | 1 | 3 |  |
| 6131 | `unknown` | yes | yes | 3 | 1 |  |
| 6244 | `unknown` | yes | yes | 1 | 3 |  |
| 6321 | `unknown` | yes | yes | 2 | 2 |  |
| 6501 | `unknown` | yes | yes | 2 | 2 |  |
| 6571 | `unknown` | no | no | 0 | 0 | ValidationError: 1 validation error for BoundaryCandidateOutput
candidates.1.candidate_kind
  Input should be 'frequency_rate', 'cluster_frequency', 'seizure_free', 'unknown_frequency', 'no_reference' or 'conditional_frequency' [type=literal_error, input_value=['cluster_frequency', 'seizure_free'], input_type=list]
    For further information visit https://errors.pydantic.dev/2.12/v/literal_error |
| 6987 | `unknown` | yes | yes | 3 | 1 |  |
| 9888 | `unknown` | yes | yes | 2 | 1 |  |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | no | no | 2 | 2 |  |
| 9955 | `1 cluster per month, multiple per cluster` | no | no | 3 | 1 |  |
| 10266 | `unknown` | no | no | 0 | 0 | ValidationError: 1 validation error for BoundaryCandidateOutput
candidates.0.candidate_kind
  Input should be 'frequency_rate', 'cluster_frequency', 'seizure_free', 'unknown_frequency', 'no_reference' or 'conditional_frequency' [type=literal_error, input_value=['cluster_frequency', 'unknown_frequency'], input_type=list]
    For further information visit https://errors.pydantic.dev/2.12/v/literal_error |
| 10618 | `unknown, 4 to 6 per cluster` | no | yes | 2 | 2 |  |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | no | no | 4 | 0 |  |
| 12456 | `1 per day` | yes | yes | 3 | 1 |  |
| 14025 | `unknown` | yes | yes | 4 | 0 |  |
| 14076 | `unknown` | yes | yes | 2 | 2 |  |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | yes | yes | 3 | 1 |  |
| 15834 | `5 per week` | yes | yes | 3 | 1 |  |

## Interpretation

- Promote only as a candidate-proposal component if exact evidence remains high and retained candidates cover the missed gold states without excess burden.
- Do not treat this as final-label performance. Any downstream label effect must be measured by a separate selected-state replay over the gated union.
