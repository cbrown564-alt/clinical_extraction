# ExECTv2 SeizureFrequency Unknown-Suppression v0.7

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_sf_unknown_suppression.jsonl`
- Suppression version: `exectv2_hybrid_sf_unknown_suppression_v0.7`
- Source projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Split: `entropy_dev140_temps`
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
| `unknown_suppression.drug_response_scope` | 1 |

## Gate

| Check | Value | Pass |
| --- | ---: | --- |
| headline_f1_delta | 0.0037 | False |
| unknown_fp_drop | 2 | False |
| unknown_fn_increase | 0 | True |
| active_rate_recall_delta | 0.0000 | True |
| seizure_free_recall_delta | 0.0000 | True |
| evidence_validity | 1.0000 | True |
| attributed_actions | 2 | True |

## Baseline Versus Suppressed

| Slice | Baseline F1 | Suppressed F1 | Baseline P | Suppressed P | Baseline R | Suppressed R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.628 | 0.632 | 0.628 | 0.635 | 0.628 | 0.628 | 108 | 62 | 64 |
| active-rate | 0.667 | 0.667 | 0.649 | 0.649 | 0.685 | 0.685 | 50 | 27 | 23 |
| seizure-free | 0.688 | 0.688 | 0.657 | 0.657 | 0.721 | 0.721 | 44 | 23 | 17 |
| unknown | 0.424 | 0.438 | 0.500 | 0.538 | 0.368 | 0.368 | 14 | 12 | 24 |

## Interpretation

The predeclared suppression layer passes the hard-slice gate on dev140: it improves headline SF F1, reduces unknown over-emission by named rules, and leaves active-rate and seizure-free recall unchanged. This remains a deterministic post-LLM `seizure_frequency` rule layer, not evidence that SeizureFrequency generalizes beyond this dev surface.
