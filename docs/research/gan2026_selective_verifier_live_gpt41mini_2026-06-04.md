# Gan 2026 Selective Verifier Live Run

Validation-development selective verifier over the frozen predeclared suspicious selected-state surface. This does not authorize locked-test inspection, whole-pipeline promotion, or benchmark-comparable claims.

## Decision

Do not promote the verifier to prediction-bearing use: it introduced 5 C->W regression(s) versus the routing policy.

## Artifacts

- Row JSONL: `experiments/gan2026_selective_verifier_live_gpt41mini_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_selective_verifier_live_gpt41mini_2026-06-04.json`
- Source predeclaration: `experiments/gan2026_selective_verifier_predeclaration_2026-06-04.jsonl`

## Metrics

| Metric | Value |
| --- | ---: |
| abstain review rows | 0 |
| all evidence quotes exact rows | 38 |
| c to review vs routing rows | 0 |
| c to w vs routing rows | 5 |
| call ok rows | 42 |
| changed decision precision | 0.522 |
| changed scorable rows | 23 |
| decision changed rows | 30 |
| parse error rows | 0 |
| parse ok rows | 42 |
| unchanged rows | 12 |
| w to c vs routing rows | 6 |
| w to review vs routing rows | 0 |

## Recommendations

| Recommendation | Rows |
| --- | ---: |
| `choose_listed_competing_hypothesis` | 10 |
| `render_as_selected_state` | 20 |
| `render_as_unknown` | 12 |

## Deltas Versus Routing

| Delta | Rows |
| --- | ---: |
| `C_to_C_changed` | 1 |
| `C_to_W` | 5 |
| `W_to_C` | 6 |
| `W_to_W_changed` | 18 |
| `unchanged` | 12 |

## Changed Rows

| Row | Routing | Verifier recommendation | Label | Delta | Quotes exact |
| ---: | --- | --- | --- | --- | --- |
| 190 | route_unknown | render_as_selected_state | 1 per 4 week | W_to_C | True |
| 338 | route_unknown | render_as_selected_state | multiple per month | C_to_C_changed | True |
| 743 | route_review | choose_listed_competing_hypothesis | multiple per day | W_to_W_changed | True |
| 744 | route_review | render_as_selected_state | multiple per week | W_to_W_changed | True |
| 869 | route_review | render_as_unknown | unknown | W_to_W_changed | True |
| 1694 | route_unknown | choose_listed_competing_hypothesis | None | W_to_W_changed | True |
| 2080 | route_unknown | render_as_selected_state | 1 cluster per month, 2 per cluster | C_to_W | True |
| 4368 | route_review | render_as_unknown | unknown | W_to_W_changed | True |
| 5534 | route_unknown | render_as_selected_state | 1 per 2 week | C_to_W | True |
| 5921 | route_unknown | render_as_selected_state | 1 cluster per 6 to 8 week, multiple per cluster | W_to_W_changed | True |
| 6131 | route_unknown | render_as_selected_state | None | W_to_W_changed | True |
| 6153 | route_unknown | render_as_selected_state | 9 per 4 week | W_to_C | True |
| 6209 | route_unknown | render_as_selected_state | 2 to 3 per day | C_to_W | True |
| 6571 | route_unknown | render_as_selected_state | None | W_to_W_changed | True |
| 6889 | route_unknown | choose_listed_competing_hypothesis | None | W_to_W_changed | True |
| 6987 | route_unknown | choose_listed_competing_hypothesis | None | W_to_W_changed | True |
| 7168 | route_unknown | render_as_selected_state | 1 cluster per year, 2 per cluster | C_to_W | True |
| 7615 | route_unknown | render_as_selected_state | 1 cluster per month, 3 to 6 per cluster | W_to_C | True |
| 9943 | route_unknown | render_as_selected_state | 1 cluster per 4 to 5 week, multiple per cluster | W_to_C | True |
| 10618 | route_review | render_as_unknown | unknown | W_to_W_changed | True |
| 10677 | route_unknown | render_as_selected_state | 1 per month | W_to_W_changed | True |
| 10996 | route_unknown | render_as_selected_state | 1 to 2 cluster per month, 4 per cluster | W_to_C | True |
| 11259 | route_review | choose_listed_competing_hypothesis | unknown | W_to_W_changed | False |
| 12438 | route_unknown | render_as_selected_state | 2 to 3 per year | W_to_W_changed | True |
| 12460 | route_unknown | render_as_selected_state | 2 per year | W_to_W_changed | True |
| 13209 | route_review | render_as_selected_state | None | W_to_W_changed | False |
| 14810 | route_unknown | render_as_selected_state | None | W_to_W_changed | True |
| 15193 | route_unknown | choose_listed_competing_hypothesis | 0 per 9 to 10 month | C_to_W | False |
| 15593 | route_unknown | render_as_selected_state | 1 cluster per 5 day, 2 to 4 per cluster | W_to_C | True |
| 15672 | route_unknown | choose_listed_competing_hypothesis | multiple per day | W_to_W_changed | True |

## Promotion Boundary

The verifier is not promoted to prediction-bearing use unless C->W rows are zero or explicitly adjudicated under a separate protocol. Abstentions and review recommendations remain routing actions, not correct final labels.
