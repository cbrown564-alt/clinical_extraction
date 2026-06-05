# Gan 2026 Structured Projection Expansion Source Audit v0

Validation-development expansion-source audit only. It compares saved validation artifacts, writes no note text, uses no locked-test row-level artifacts, and does not authorize holdout-facing use.

## Decision

direct_labeler_source_rejected_for_broadening

## Summary

| Metric | Value |
| --- | ---: |
| current W->C rows | 23 |
| candidate clean prediction-bearing rows | 187 |
| candidate clean W->C rows | 6 |
| candidate clean C->W rows | 40 |
| novel clean W->C rows | 1 |
| safe to broaden from candidate source | False |
| holdout authorized | False |

## Clean Candidate Transitions

| Transition | Rows |
| --- | ---: |
| `C_to_C` | 137 |
| `C_to_W` | 40 |
| `W_to_C` | 6 |
| `W_to_W` | 4 |

## Next Step

Do not broaden by importing the broad direct-labeler source. Build a new validation hard-opportunity panel from explicit projection-owner mechanisms and matched controls, then rerun the extractor smoke.

## Artifacts

- Audit JSONL: `experiments/gan2026_structured_projection_expansion_source_audit_v0_2026-06-05.jsonl`
- Summary JSON: `experiments/gan2026_structured_projection_expansion_source_audit_v0_2026-06-05.json`
- Source current extractor JSONL: `experiments/gan2026_structured_validation_projection_extractor_v0_2026-06-05.jsonl`
- Source candidate JSONL: `experiments/gan2026_structured_candidate_event_contract_v0_direct_labeler_validation750_panel_2026-06-05.jsonl`
