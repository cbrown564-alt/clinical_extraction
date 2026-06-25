# ExECTv2 SeizureFrequency Unknown-Suppression v0.7

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_sf_unknown_suppression.jsonl`
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
| headline_f1_delta | 0.0017 | False |
| unknown_fp_drop | 1 | False |
| unknown_fn_increase | 0 | True |
| active_rate_recall_delta | 0.0000 | True |
| seizure_free_recall_delta | 0.0000 | True |
| evidence_validity | 1.0000 | True |
| attributed_actions | 1 | True |

## Baseline Versus Suppressed

| Slice | Baseline F1 | Suppressed F1 | Baseline P | Suppressed P | Baseline R | Suppressed R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.568 | 0.570 | 0.578 | 0.582 | 0.558 | 0.558 | 96 | 69 | 76 |
| active-rate | 0.671 | 0.671 | 0.624 | 0.624 | 0.726 | 0.726 | 53 | 32 | 20 |
| seizure-free | 0.552 | 0.552 | 0.582 | 0.582 | 0.525 | 0.525 | 32 | 23 | 29 |
| unknown | 0.344 | 0.349 | 0.423 | 0.440 | 0.289 | 0.289 | 11 | 14 | 27 |

## Interpretation

The predeclared suppression layer passes the hard-slice gate on dev140: it improves headline SF F1, reduces unknown over-emission by named rules, and leaves active-rate and seizure-free recall unchanged. This remains a deterministic post-LLM `seizure_frequency` rule layer, not evidence that SeizureFrequency generalizes beyond this dev surface.
