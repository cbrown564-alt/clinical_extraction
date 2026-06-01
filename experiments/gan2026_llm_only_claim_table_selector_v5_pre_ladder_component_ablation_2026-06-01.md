# Gan 2026 Claim-Table V5 Pre-Ladder Component Ablation

This is a pre-ladder development attribution artifact, not a held-out or benchmark claim.

- Prompt version: `gan2026_llm_only_claim_table_selector_v5`
- Source JSONL: `none; design gate only`
- Rows: 0
- Validation ladder status: blocked until required ablations exist for `25`, `50`, and `250` validation rows.
- Required ablations: `raw_model_claim_table`, `strict_schema_repair`, `constrained_selector_state`, `clean_scorer_facing_policy`

## Condition Summary

| Condition | Role | Rows | Purist | Pragmatic | Scorable | Selector state | Issues |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model_claim_table | prediction-bearing model claim table and final query | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| strict_schema_repair | non-semantic shape and parser-format compatibility repair | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| constrained_selector_state | claim-table plus selector_decision, cluster_axis, and boundary_state | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 |
| clean_scorer_facing_policy | frozen scorer-facing label cleanup after selector state is preserved | 0 | 0.0000 | 0.0000 | 0 | 0 | 0 |

## Component Map

### raw_model_claim_table

- Score layer: `raw`
- Enabled: LLM claim extraction, LLM final query
- Disabled: strict schema repair, constrained selector state audit, clean scorer-facing policy

### strict_schema_repair

- Score layer: `strict_format`
- Enabled: LLM claim extraction, LLM final query, strict schema repair
- Disabled: clean scorer-facing policy

### constrained_selector_state

- Score layer: `strict_format`
- Enabled: LLM claim extraction, LLM constrained selector, cluster-axis state, boundary-state field, strict schema repair
- Disabled: clean scorer-facing policy

### clean_scorer_facing_policy

- Score layer: `clean_scorer_facing`
- Enabled: LLM claim extraction, LLM constrained selector, cluster-axis state, boundary-state field, strict schema repair, clean scorer-facing policy
- Disabled: none
