# Gan 2026 Selective Boundary-Candidate Experiment

This controlled validation-development run uses the predeclared 22-row boundary-candidate rescue slice. The model proposes candidate facts only; candidate outputs are gated and deterministically normalized for component accounting, not used as final labels.

## Outcome

The live proposer produced parseable outputs for 21/22 rows and retained at least one gated candidate for 21/22 rows. Exact-label candidate recall was 16/22; Purist-category candidate recall was 20/22.

## Claim Boundary

Validation-development controlled component experiment only. Outputs are candidate proposals, not final labels; no locked-test inspection, whole-pipeline promotion, or benchmark-comparable claim is authorized.

## Artifacts

- JSONL: `experiments/gan2026_selective_boundary_candidate_experiment_v2_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_boundary_candidate_experiment_v2_2026-06-04.json`
- Predeclaration: `experiments/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| call ok rows | 22 |
| call error rows | 0 |
| parse ok rows | 21 |
| parse error rows | 1 |
| rows with retained candidate | 21 |
| rows with gold exact label recall | 16 |
| rows with gold purist recall | 20 |
| rows with saved rescue evidence overlap | 21 |
| rows all retained evidence exact | 21 |
| total retained candidates | 71 |
| median retained candidates | 4.000 |
| p90 retained candidates | 4.000 |
| total rejected candidates | 10 |

## Gate Failures

| Failure | Count |
| --- | ---: |
| `missing_seizure_free_duration` | 1 |
| `non_exact_evidence` | 3 |
| `unrenderable_candidate` | 6 |

## V1 Comparison

| Metric | V1 | V2 | Direction |
| --- | ---: | ---: | --- |
| parse ok rows | 20/22 | 21/22 | improved |
| exact-label candidate recall | 15/22 | 16/22 | improved |
| Purist candidate recall | 17/22 | 20/22 | improved |
| saved rescue evidence overlap | 20/22 | 21/22 | improved |
| total retained candidates | 66 | 71 | higher burden |
| median retained candidates | 3 | 4 | higher burden |
| total rejected candidates | 13 | 10 | improved |
| unrenderable candidate failures | 9 | 6 | improved |
| non-exact evidence failures | 3 | 3 | unchanged |

V2 fixed the known `assertion_status=no_reference` parse failure pattern and
improved candidate recall on the controlled validation rescue slice. It is still
a revise signal before selected-state replay: row 12456 failed parse because two
candidates omitted required `reason`, and cluster exact-label rows 9943, 10996,
and 15593 remain unresolved.

## Row Outcomes

| Row | Gold | Exact recall | Purist recall | Retained | Rejected | Notes |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 338 | `multiple per month` | yes | yes | 3 | 1 |  |
| 1707 | `multiple per week` | no | yes | 4 | 0 |  |
| 3356 | `unknown` | yes | yes | 4 | 0 |  |
| 5974 | `unknown` | yes | yes | 4 | 0 |  |
| 6077 | `unknown` | yes | yes | 3 | 1 |  |
| 6131 | `unknown` | yes | yes | 2 | 2 |  |
| 6244 | `unknown` | yes | yes | 4 | 0 |  |
| 6321 | `unknown` | yes | yes | 4 | 0 |  |
| 6501 | `unknown` | yes | yes | 2 | 2 |  |
| 6571 | `unknown` | no | yes | 3 | 1 |  |
| 6987 | `unknown` | yes | yes | 3 | 1 |  |
| 9888 | `unknown` | yes | yes | 4 | 0 |  |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | no | yes | 4 | 0 |  |
| 9955 | `1 cluster per month, multiple per cluster` | yes | yes | 4 | 0 |  |
| 10266 | `unknown` | yes | yes | 3 | 1 |  |
| 10618 | `unknown, 4 to 6 per cluster` | yes | yes | 4 | 0 |  |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | no | yes | 1 | 0 |  |
| 12456 | `1 per day` | no | no | 0 | 0 | ValidationError: 2 validation errors for BoundaryCandidateOutput
candidates.0.reason
  Field required [type=missing, input_value={'evidence_quote': 'she c... {}, 'seizure_free': {}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
candidates.1.reason
  Field required [type=missing, input_value={'evidence_quote': 'she c... {}, 'seizure_free': {}}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing |
| 14025 | `unknown` | yes | yes | 4 | 0 |  |
| 14076 | `unknown` | yes | yes | 3 | 1 |  |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | no | no | 4 | 0 |  |
| 15834 | `5 per week` | yes | yes | 4 | 0 |  |

## Interpretation

- Revise before selected-state replay. V2 is directionally better than v1, but
  parse stability is still not complete and the remaining cluster exact-label
  misses are exactly the slice this revision was meant to stabilize.
- Do not treat this as final-label performance. Any downstream label effect must
  be measured by a separate selected-state replay over the gated union.
