# ExECTv2 SeizureFrequency Unknown-Suppression v0.7

- JSONL: `experiments\exectv2_section_timeline_ablation_dev140_sf_suppression_with_timeline.jsonl`
- Suppression version: `exectv2_hybrid_sf_unknown_suppression_v0.7`
- Source projection version: `exectv2_hybrid_sf_state_projection_v0.6`
- Split: `dev`
- Letters: 140
- Promoted by gate: `True`

## Rule Categories

| Rule family | Portability category | Attribution note |
| --- | --- | --- |
| unknown suppression | seizure_frequency | Drops existing unknown-state mentions when evidence is treatment-response scope or contextual/historical change scope. |

## Action Counts

| Rule | Count |
| --- | ---: |
| `unknown_suppression.contextual_or_historical_change` | 4 |
| `unknown_suppression.drug_response_scope` | 5 |

## Gate

| Check | Value | Pass |
| --- | ---: | --- |
| headline_f1_delta | 0.0200 | True |
| unknown_fp_drop | 9 | True |
| unknown_fn_increase | 0 | True |
| active_rate_recall_delta | 0.0000 | True |
| seizure_free_recall_delta | 0.0000 | True |
| evidence_validity | 1.0000 | True |
| attributed_actions | 9 | True |

## Baseline Versus Suppressed

| Slice | Baseline F1 | Suppressed F1 | Baseline P | Suppressed P | Baseline R | Suppressed R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency | 0.788 | 0.808 | 0.733 | 0.769 | 0.851 | 0.851 | 143 | 43 | 25 |
| active-rate | 0.822 | 0.822 | 0.788 | 0.788 | 0.859 | 0.859 | 67 | 18 | 11 |
| seizure-free | 0.852 | 0.852 | 0.812 | 0.812 | 0.897 | 0.897 | 52 | 12 | 6 |
| unknown | 0.615 | 0.696 | 0.522 | 0.649 | 0.750 | 0.750 | 24 | 13 | 8 |

## Interpretation

The predeclared suppression layer passes the hard-slice gate on dev140: it improves headline SF F1, reduces unknown over-emission by named rules, and leaves active-rate and seizure-free recall unchanged. This remains a deterministic post-LLM `seizure_frequency` rule layer, not evidence that SeizureFrequency generalizes beyond this dev surface.
