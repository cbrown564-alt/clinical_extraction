# ExECTv2 SeizureFrequency Unknown-Suppression v0.7

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_deepseek_dev140_20260625_sf_unknown_suppression.jsonl`
- Suppression version: `exectv2_hybrid_sf_unknown_suppression_v0.7`
- Source projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Split: `dev140`
- Letters: 140
- Promoted by gate: `False`

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| unknown suppression | seizure_frequency | Drops existing unknown-state mentions when evidence is treatment-response scope or contextual/historical change scope. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `unknown_suppression.contextual_or_historical_change` | 1 |

## Gate

| Check | Value | Pass |
| --- | ---: | --- |
| headline_f1_delta | 0.0020 | False |
| unknown_fp_drop | 1 | False |
| unknown_fn_increase | 0 | True |
| active_rate_recall_delta | 0.0000 | True |
| seizure_free_recall_delta | 0.0000 | True |
| evidence_validity | 1.0000 | True |
| attributed_actions | 1 | True |

## Baseline Versus Suppressed

| Slice | Baseline F1 | Suppressed F1 | Baseline P | Suppressed P | Baseline R | Suppressed R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.695 | 0.697 | 0.670 | 0.674 | 0.721 | 0.721 | 124 | 60 | 48 |
| active-rate | 0.755 | 0.755 | 0.698 | 0.698 | 0.822 | 0.822 | 60 | 26 | 13 |
| seizure-free | 0.701 | 0.701 | 0.644 | 0.644 | 0.770 | 0.770 | 47 | 26 | 14 |
| unknown | 0.531 | 0.540 | 0.654 | 0.680 | 0.447 | 0.447 | 17 | 8 | 21 |

## Interpretation

The predeclared suppression layer passes the hard-slice gate on dev140: it improves headline SF F1, reduces unknown over-emission by named rules, and leaves active-rate and seizure-free recall unchanged. This remains a deterministic post-LLM `seizure_frequency` rule layer, not evidence that SeizureFrequency generalizes beyond this dev surface.
