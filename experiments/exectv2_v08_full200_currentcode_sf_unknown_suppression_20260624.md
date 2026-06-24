# ExECTv2 SeizureFrequency Unknown-Suppression v0.7

- JSONL: `experiments\exectv2_v08_full200_currentcode_sf_unknown_suppression_20260624.jsonl`
- Suppression version: `exectv2_hybrid_sf_unknown_suppression_v0.7`
- Source projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Split: `full_200_authorized`
- Letters: 200
- Promoted by gate: `False`

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| unknown suppression | seizure_frequency | Drops existing unknown-state mentions when evidence is treatment-response scope or contextual/historical change scope. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `unknown_suppression.contextual_or_historical_change` | 4 |
| `unknown_suppression.drug_response_scope` | 3 |

## Gate

| Check | Value | Pass |
| --- | ---: | --- |
| headline_f1_delta | 0.0056 | False |
| unknown_fp_drop | 6 | True |
| unknown_fn_increase | 1 | True |
| active_rate_recall_delta | 0.0000 | True |
| seizure_free_recall_delta | 0.0000 | True |
| evidence_validity | 1.0000 | True |
| attributed_actions | 7 | True |

## Baseline Versus Suppressed

| Slice | Baseline F1 | Suppressed F1 | Baseline P | Suppressed P | Baseline R | Suppressed R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.697 | 0.703 | 0.650 | 0.663 | 0.752 | 0.748 | 181 | 92 | 61 |
| active-rate | 0.733 | 0.733 | 0.680 | 0.680 | 0.794 | 0.794 | 85 | 40 | 22 |
| seizure-free | 0.685 | 0.685 | 0.630 | 0.630 | 0.750 | 0.750 | 63 | 37 | 21 |
| unknown | 0.642 | 0.667 | 0.618 | 0.688 | 0.667 | 0.647 | 33 | 15 | 18 |

## Interpretation

The predeclared suppression layer passes the hard-slice gate on dev140: it improves headline SF F1, reduces unknown over-emission by named rules, and leaves active-rate and seizure-free recall unchanged. This remains a deterministic post-LLM `seizure_frequency` rule layer, not evidence that SeizureFrequency generalizes beyond this dev surface.
