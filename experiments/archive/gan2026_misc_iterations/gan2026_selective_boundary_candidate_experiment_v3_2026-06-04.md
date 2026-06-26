# Gan 2026 Selective Boundary-Candidate Experiment

This controlled validation-development run uses the predeclared 22-row boundary-candidate rescue slice. The model proposes candidate facts only; candidate outputs are gated and deterministically normalized for component accounting, not used as final labels.

## Outcome

The live proposer produced parseable outputs for 22/22 rows and retained at least one gated candidate for 22/22 rows. Exact-label candidate recall was 16/22; Purist-category candidate recall was 21/22.

## Claim Boundary

Validation-development controlled component experiment only. Outputs are candidate proposals, not final labels; no locked-test inspection, whole-pipeline promotion, or benchmark-comparable claim is authorized.

## Artifacts

- JSONL: `experiments/gan2026_selective_boundary_candidate_experiment_v3_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_boundary_candidate_experiment_v3_2026-06-04.json`
- Predeclaration: `experiments/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| call ok rows | 22 |
| call error rows | 0 |
| parse ok rows | 22 |
| parse error rows | 0 |
| rows with retained candidate | 22 |
| rows with gold exact label recall | 16 |
| rows with gold purist recall | 21 |
| rows with saved rescue evidence overlap | 21 |
| rows all retained evidence exact | 22 |
| total retained candidates | 75 |
| median retained candidates | 4.000 |
| p90 retained candidates | 4.000 |
| total rejected candidates | 7 |

## Gate Failures

| Failure | Count |
| --- | ---: |
| `missing_seizure_free_duration` | 2 |
| `non_exact_evidence` | 3 |
| `unrenderable_candidate` | 3 |

## V1/V2 Comparison

| Metric | V1 | V2 | V3 | Direction |
| --- | ---: | ---: | ---: | --- |
| parse ok rows | 20/22 | 21/22 | 22/22 | improved |
| exact-label candidate recall | 15/22 | 16/22 | 16/22 | unchanged from v2 |
| Purist candidate recall | 17/22 | 20/22 | 21/22 | improved |
| saved rescue evidence overlap | 20/22 | 21/22 | 21/22 | unchanged from v2 |
| total retained candidates | 66 | 71 | 75 | higher burden |
| median retained candidates | 3 | 4 | 4 | unchanged from v2 |
| total rejected candidates | 13 | 10 | 7 | improved |
| unrenderable candidate failures | 9 | 6 | 3 | improved |
| non-exact evidence failures | 3 | 3 | 3 | unchanged |

V3 fixed parse stability and recovered exact cluster labels for rows 9943 and
10996 plus the missing-reason parse failure on row 12456. It did not fix row
15593: the proposer still encodes "five days without seizures followed by a day
of clustering" as `1 cluster per day, 2 to 4 per cluster` instead of the gold
`1 cluster per 5 day, 2 to 4 per cluster`.

## Row Outcomes

| Row | Gold | Exact recall | Purist recall | Retained | Rejected | Notes |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 338 | `multiple per month` | no | yes | 4 | 0 |  |
| 1707 | `multiple per week` | no | yes | 4 | 0 |  |
| 3356 | `unknown` | yes | yes | 3 | 0 |  |
| 5974 | `unknown` | yes | yes | 2 | 1 |  |
| 6077 | `unknown` | yes | yes | 3 | 1 |  |
| 6131 | `unknown` | yes | yes | 4 | 0 |  |
| 6244 | `unknown` | yes | yes | 3 | 1 |  |
| 6321 | `unknown` | yes | yes | 4 | 0 |  |
| 6501 | `unknown` | no | yes | 4 | 0 |  |
| 6571 | `unknown` | no | yes | 2 | 2 |  |
| 6987 | `unknown` | yes | yes | 3 | 0 |  |
| 9888 | `unknown` | yes | yes | 4 | 0 |  |
| 9943 | `1 cluster per 4 to 5 week, multiple per cluster` | yes | yes | 4 | 0 |  |
| 9955 | `1 cluster per month, multiple per cluster` | yes | yes | 4 | 0 |  |
| 10266 | `unknown` | yes | yes | 3 | 1 |  |
| 10618 | `unknown, 4 to 6 per cluster` | no | yes | 4 | 0 |  |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | yes | yes | 1 | 0 |  |
| 12456 | `1 per day` | yes | yes | 4 | 0 |  |
| 14025 | `unknown` | yes | yes | 4 | 0 |  |
| 14076 | `unknown` | yes | yes | 4 | 0 |  |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | no | no | 3 | 1 |  |
| 15834 | `5 per week` | yes | yes | 4 | 0 |  |

## Interpretation

- Revise before selected-state replay if exact cluster labels are required. V3
  is the best parse/Purist run so far, but it leaves the seizure-free-interval
  cluster cadence pattern unresolved on row 15593.
- Do not treat this as final-label performance. Any downstream label effect must
  be measured by a separate selected-state replay over the gated union.
