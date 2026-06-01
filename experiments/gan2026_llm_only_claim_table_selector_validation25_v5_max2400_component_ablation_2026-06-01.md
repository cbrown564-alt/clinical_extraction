# Gan 2026 Claim-Table V5 Pre-Ladder Component Ablation

This is a pre-ladder development attribution artifact, not a held-out or benchmark claim.

- Prompt version: `gan2026_llm_only_claim_table_selector_v5`
- Source JSONL: `experiments/gan2026_llm_only_claim_table_selector_validation25_gpt41mini_v5_max2400_2026-06-01.jsonl`
- Rows: 25
- Validation ladder status: blocked until required ablations exist for `25`, `50`, and `250` validation rows.
- Required ablations: `raw_model_claim_table`, `strict_schema_repair`, `constrained_selector_state`, `clean_scorer_facing_policy`

## Condition Summary

| Condition | Role | Rows | Purist | Pragmatic | Scorable | Selector state | Issues |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model_claim_table | prediction-bearing model claim table and final query | 25 | 0.8800 | 0.8800 | 23 | 24 | 1 |
| strict_schema_repair | non-semantic shape and parser-format compatibility repair | 25 | 0.8800 | 0.8800 | 23 | 24 | 1 |
| constrained_selector_state | claim-table plus selector_decision, cluster_axis, and boundary_state | 25 | 0.8800 | 0.8800 | 23 | 24 | 1 |
| clean_scorer_facing_policy | frozen scorer-facing label cleanup after selector state is preserved | 25 | 0.9200 | 0.9200 | 24 | 24 | 1 |

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
