# Gan 2026 Selective Boundary-Candidate Experiment

This controlled validation-development run uses the predeclared 22-row boundary-candidate rescue slice. The model proposes candidate facts only; candidate outputs are gated and deterministically normalized for component accounting, not used as final labels.

## Outcome

The live proposer produced parseable outputs for 20/22 rows and retained at least one gated candidate for 20/22 rows. Exact-label candidate recall was 15/22; Purist-category candidate recall was 17/22.

## Claim Boundary

Validation-development controlled component experiment only. Outputs are candidate proposals, not final labels; no locked-test inspection, whole-pipeline promotion, or benchmark-comparable claim is authorized.

## Artifacts

- JSONL: `experiments/gan2026_selective_boundary_candidate_experiment_v1_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_boundary_candidate_experiment_v1_2026-06-04.json`
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
| rows with gold purist recall | 17 |
| rows with saved rescue evidence overlap | 20 |
| rows all retained evidence exact | 20 |
| total retained candidates | 66 |
| median retained candidates | 3.000 |
| p90 retained candidates | 4.000 |
| total rejected candidates | 13 |

## Gate Failures

| Failure | Count |
| --- | ---: |
| `missing_seizure_free_duration` | 1 |
| `non_exact_evidence` | 3 |
| `unrenderable_candidate` | 9 |

## V0 Comparison

| Metric | V0 | V1 | Direction |
| --- | ---: | ---: | --- |
| parse ok rows | 20/22 | 20/22 | unchanged |
| exact-label candidate recall | 15/22 | 15/22 | unchanged |
| Purist candidate recall | 16/22 | 17/22 | improved |
| saved rescue evidence overlap | 15/22 | 20/22 | improved |
| total retained candidates | 55 | 66 | higher burden |
| total rejected candidates | 24 | 13 | improved |
| unrenderable candidate failures | 15 | 9 | improved |
| non-exact evidence failures | 9 | 3 | improved |

V1 improved evidence overlap and reduced gate rejections, but it did not improve
parse stability or exact-label candidate recall. The remaining parse failures
are scalar enum mistakes: rows 6571 and 10996 put `no_reference` in
`assertion_status`. Cluster-specific rows still miss exact labels for 9943,
9955, 10996, and 15593, so this run is a revise signal rather than a selected
state replay input.

## Row Outcomes

| Row | Gold | Exact recall | Purist recall | Retained | Rejected | Notes |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 338 | `multiple per month` | yes | yes | 2 | 2 |  |
| 1707 | `multiple per week` | no | yes | 4 | 0 |  |
| 3356 | `unknown` | yes | yes | 2 | 1 |  |
| 5974 | `unknown` | yes | yes | 4 | 0 |  |
| 6077 | `unknown` | yes | yes | 3 | 1 |  |
| 6131 | `unknown` | yes | yes | 4 | 0 |  |
| 6244 | `unknown` | yes | yes | 3 | 1 |  |
| 6321 | `unknown` | yes | yes | 4 | 0 |  |
| 6501 | `unknown` | yes | yes | 2 | 2 |  |
| 6571 | `unknown` | no | no | 0 | 0 | ValidationError: 1 validation error for BoundaryCandidateOutput
candidates.2.assertion_status
  Input should be 'asserted', 'negated', 'uncertain' or 'conditional' [type=literal_error, input_value='no_reference', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/literal_error |
| 6987 | `unknown` | yes | yes | 4 | 0 |  |
| 9888 | `unknown` | yes | yes | 3 | 1 |  |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | no | no | 3 | 1 |  |
| 9955 | `1 cluster per month, multiple per cluster` | no | no | 4 | 0 |  |
| 10266 | `unknown` | yes | yes | 4 | 0 |  |
| 10618 | `unknown, 4 to 6 per cluster` | no | yes | 3 | 1 |  |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | no | no | 0 | 0 | ValidationError: 1 validation error for BoundaryCandidateOutput
candidates.3.assertion_status
  Input should be 'asserted', 'negated', 'uncertain' or 'conditional' [type=literal_error, input_value='no_reference', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/literal_error |
| 12456 | `1 per day` | yes | yes | 3 | 1 |  |
| 14025 | `unknown` | yes | yes | 4 | 0 |  |
| 14076 | `unknown` | yes | yes | 3 | 1 |  |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | no | no | 4 | 0 |  |
| 15834 | `5 per week` | yes | yes | 3 | 1 |  |

## Interpretation

- Revise before selected-state replay. The v1 prompt/schema reduced rejection
  burden and improved saved-rescue evidence overlap, but parse stability and
  cluster exact-label recall remain insufficient.
- Do not treat this as final-label performance. Any downstream label effect must be measured by a separate selected-state replay over the gated union.
